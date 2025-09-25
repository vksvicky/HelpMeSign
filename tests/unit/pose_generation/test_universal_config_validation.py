"""
Test suite for validating universal_config.json pose data consistency.

This module tests the pose data in universal_config.json for logical consistency
without requiring visual inspection. It validates:
- Joint relationships and constraints
- Expected joint counts for different actions
- HPR value ranges and logical consistency
- Finger joint relationships
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from helpmesign.modes.learn.instruction_to_pose_generator import (
    UniversalInstructionToPoseGenerator,
)


class UniversalConfigValidator:
    """Validates pose data consistency in universal_config.json"""

    def __init__(self):
        self.config_path = (
            Path(__file__).parent.parent.parent.parent
            / "resources"
            / "data"
            / "pose_generation"
            / "universal_config.json"
        )
        self.generator = UniversalInstructionToPoseGenerator()
        self.config_data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load the universal config file"""
        with open(self.config_path, "r") as f:
            return json.load(f)

    def validate_all_actions(self) -> Dict[str, List[str]]:
        """Validate all actions in the config"""
        results = {}
        keywords = self.config_data.get("keywords", {})
        actions = keywords.get("actions", {})

        for action_name, action_data in actions.items():
            if "pose_data" in action_data:
                results[action_name] = self._validate_action_pose_data(
                    action_name, action_data["pose_data"]
                )
            else:
                results[action_name] = [
                    f"⚠️ No pose_data defined for action '{action_name}'"
                ]

        return results

    def validate_all_handshapes(self) -> Dict[str, List[str]]:
        """Validate all handshapes in the config"""
        results = {}
        keywords = self.config_data.get("keywords", {})
        handshapes = keywords.get("hand_shapes", {})

        for handshape_name, handshape_data in handshapes.items():
            if "pose_data" in handshape_data:
                results[handshape_name] = self._validate_handshape_pose_data(
                    handshape_name, handshape_data["pose_data"]
                )
            else:
                results[handshape_name] = [
                    f"⚠️ No pose_data defined for handshape '{handshape_name}'"
                ]

        return results

    def _validate_action_pose_data(
        self, action_name: str, pose_data: Dict[str, List[float]]
    ) -> List[str]:
        """Validate pose data for a specific action"""
        issues = []

        # Check for expected joint types based on action
        expected_joints = self._get_expected_joints_for_action(action_name)
        actual_joints = set(pose_data.keys())

        # Check if we have the expected joints (more flexible matching)
        for expected_joint_type in expected_joints:
            if not any(expected_joint_type in joint for joint in actual_joints):
                # Only warn if we have no joints at all, or if it's a critical joint
                if len(actual_joints) == 0:
                    issues.append(f"❌ No joints defined for action '{action_name}'")
                elif expected_joint_type in ["Arm", "Shoulder"]:  # Critical joints
                    issues.append(
                        f"⚠️ Missing expected joint type '{expected_joint_type}' for action '{action_name}'"
                    )

        # Validate HPR values
        for joint_name, hpr_values in pose_data.items():
            issues.extend(
                self._validate_hpr_values(joint_name, hpr_values, action_name)
            )

        # Check joint relationships
        issues.extend(self._validate_joint_relationships(pose_data, action_name))

        if not issues:
            issues.append("✅ All validations passed")

        return issues

    def _validate_handshape_pose_data(
        self, handshape_name: str, pose_data: Dict[str, List[float]]
    ) -> List[str]:
        """Validate pose data for a specific handshape"""
        issues = []

        # Check for expected finger joints
        finger_joints = [
            k
            for k in pose_data.keys()
            if any(
                finger in k for finger in ["Index", "Middle", "Ring", "Pinky", "Thumb"]
            )
        ]

        # Validate that we have all 3 joints per finger if any finger joints exist
        if finger_joints:
            issues.extend(
                self._validate_finger_joint_completeness(finger_joints, handshape_name)
            )

        # Validate HPR values
        for joint_name, hpr_values in pose_data.items():
            issues.extend(
                self._validate_hpr_values(
                    joint_name, hpr_values, f"handshape_{handshape_name}"
                )
            )

        # Check handshape-specific constraints
        issues.extend(self._validate_handshape_constraints(handshape_name, pose_data))

        if not issues:
            issues.append("✅ All validations passed")

        return issues

    def _get_expected_joints_for_action(self, action_name: str) -> List[str]:
        """Get expected joint types for a specific action"""
        action_expectations = {
            "raise": ["Arm", "Shoulder"],
            "lower": ["Arm"],
            "hold": ["Arm", "Hand"],
            "point": ["Hand", "Index"],
            "curve": ["Hand", "Index", "Middle", "Ring", "Pinky"],
            "curl": ["Hand", "Index", "Middle", "Ring", "Pinky"],
            "touch": ["Hand"],
            "natural": [
                "Hips",
                "Spine",
                "Head",
                "Neck",
                "Shoulder",
                "Arm",
                "ForeArm",
                "Hand",
            ],
            "make": ["Hand", "Index", "Middle", "Ring", "Pinky", "Thumb"],
            "move": ["Arm"],
            "bend": ["Arm", "Hand"],
            "extend": ["Arm", "Hand"],
        }
        return action_expectations.get(action_name, [])

    def _validate_hpr_values(
        self, joint_name: str, hpr_values: List[float], context: str
    ) -> List[str]:
        """Validate HPR values for logical consistency"""
        issues = []

        if len(hpr_values) != 3:
            issues.append(
                f"❌ {joint_name} in {context}: HPR should have 3 values, got {len(hpr_values)}"
            )
            return issues

        h, p, r = hpr_values

        # Check for reasonable ranges (degrees)
        if not (-180 <= h <= 180):
            issues.append(
                f"⚠️ {joint_name} in {context}: Heading {h}° outside normal range [-180, 180]"
            )
        if not (-180 <= p <= 180):
            issues.append(
                f"⚠️ {joint_name} in {context}: Pitch {p}° outside normal range [-180, 180]"
            )
        if not (-180 <= r <= 180):
            issues.append(
                f"⚠️ {joint_name} in {context}: Roll {r}° outside normal range [-180, 180]"
            )

        # Check for extreme values that might indicate errors
        if abs(h) > 90 or abs(p) > 90 or abs(r) > 90:
            issues.append(
                f"⚠️ {joint_name} in {context}: Large rotation values H:{h}° P:{p}° R:{r}° - verify correctness"
            )

        return issues

    def _validate_joint_relationships(
        self, pose_data: Dict[str, List[float]], action_name: str
    ) -> List[str]:
        """Validate relationships between joints"""
        issues = []

        # Check arm-shoulder relationship
        if "RightArm" in pose_data and "RightShoulder" in pose_data:
            arm_pitch = pose_data["RightArm"][1]
            shoulder_pitch = pose_data["RightShoulder"][1]

            # Shoulder should generally move less than arm
            if abs(shoulder_pitch) > abs(arm_pitch):
                issues.append(
                    f"⚠️ {action_name}: Shoulder pitch {shoulder_pitch}° > Arm pitch {arm_pitch}° - verify relationship"
                )

        return issues

    def _validate_finger_joint_completeness(
        self, finger_joints: List[str], handshape_name: str
    ) -> List[str]:
        """Validate that we have all 3 joints per finger"""
        issues = []

        # Group joints by finger and hand
        finger_groups = {}
        for joint in finger_joints:
            for finger in ["Index", "Middle", "Ring", "Pinky", "Thumb"]:
                if finger in joint:
                    # Create a key that includes both hand and finger
                    hand = "Right" if "Right" in joint else "Left"
                    key = f"{hand}_{finger}"
                    if key not in finger_groups:
                        finger_groups[key] = []
                    finger_groups[key].append(joint)
                    break

        # Check each finger has all 3 joints
        for finger_key, joints in finger_groups.items():
            if len(joints) != 3:
                issues.append(
                    f"❌ {handshape_name}: {finger_key} finger has {len(joints)} joints, expected 3"
                )

        return issues

    def _validate_handshape_constraints(
        self, handshape_name: str, pose_data: Dict[str, List[float]]
    ) -> List[str]:
        """Validate handshape-specific constraints"""
        issues = []

        if handshape_name == "fist":
            # Fist should have curled fingers
            for joint_name, hpr_values in pose_data.items():
                if (
                    "Index" in joint_name
                    or "Middle" in joint_name
                    or "Ring" in joint_name
                    or "Pinky" in joint_name
                ):
                    pitch = hpr_values[1]
                    if pitch > -30:  # Fingers should be curled (negative pitch)
                        issues.append(
                            f"⚠️ {handshape_name}: {joint_name} pitch {pitch}° - fist fingers should be curled"
                        )

        elif handshape_name == "flat":
            # Flat hand should have extended fingers
            for joint_name, hpr_values in pose_data.items():
                if (
                    "Index" in joint_name
                    or "Middle" in joint_name
                    or "Ring" in joint_name
                    or "Pinky" in joint_name
                ):
                    pitch = hpr_values[1]
                    if pitch < -30:  # Fingers should be extended (less negative pitch)
                        issues.append(
                            f"⚠️ {handshape_name}: {joint_name} pitch {pitch}° - flat hand fingers should be extended"
                        )

        return issues

    def test_pose_generation(self) -> Dict[str, List[str]]:
        """Test actual pose generation for key actions"""
        results = {}

        test_cases = [
            ("raise", "Raise your right arm"),
            ("fist", "Make a fist with your right hand"),
            ("point", "Point with your right index finger"),
            ("flat", "Hold your right hand flat"),
        ]

        for test_name, instruction in test_cases:
            try:
                pose_data = self.generator.generate_universal_pose(
                    instruction, hand="right"
                )
                results[test_name] = [
                    f"✅ Generated {len(pose_data)} joints successfully"
                ]

                # Check for reasonable joint count
                if len(pose_data) == 0:
                    results[test_name].append("❌ No joints generated")
                elif len(pose_data) < 2:
                    results[test_name].append(
                        "⚠️ Very few joints generated - verify completeness"
                    )

            except Exception as e:
                results[test_name] = [f"❌ Generation failed: {e}"]

        return results


def test_universal_config_validation():
    """Main test function"""
    validator = UniversalConfigValidator()

    # Test actions
    action_results = validator.validate_all_actions()

    # Test handshapes
    handshape_results = validator.validate_all_handshapes()

    # Test pose generation
    generation_results = validator.test_pose_generation()

    # Assert that all validations passed
    all_results = {
        "actions": action_results,
        "handshapes": handshape_results,
        "generation": generation_results,
    }

    for category, results in all_results.items():
        for item, issues in results.items():
            # Check that we don't have any critical errors (❌)
            critical_errors = [issue for issue in issues if issue.startswith("❌")]
            assert (
                len(critical_errors) == 0
            ), f"Critical errors found in {category}.{item}: {critical_errors}"

    # If we get here, all validations passed
    assert True


def test_universal_config_validation_detailed():
    """Detailed test function that prints results"""
    print("🧪 Testing Universal Config Validation")
    print("=" * 50)

    validator = UniversalConfigValidator()

    # Test actions
    print("\n📋 Testing Actions:")
    action_results = validator.validate_all_actions()
    for action, issues in action_results.items():
        print(f"\n  {action.upper()}:")
        for issue in issues:
            print(f"    {issue}")

    # Test handshapes
    print("\n✋ Testing Handshapes:")
    handshape_results = validator.validate_all_handshapes()
    for handshape, issues in handshape_results.items():
        print(f"\n  {handshape.upper()}:")
        for issue in issues:
            print(f"    {issue}")

    # Test pose generation
    print("\n🎯 Testing Pose Generation:")
    generation_results = validator.test_pose_generation()
    for test_name, issues in generation_results.items():
        print(f"\n  {test_name.upper()}:")
        for issue in issues:
            print(f"    {issue}")

    # Summary
    total_issues = (
        sum(len(issues) for issues in action_results.values())
        + sum(len(issues) for issues in handshape_results.values())
        + sum(len(issues) for issues in generation_results.values())
    )

    print(f"\n📊 Summary: {total_issues} validation checks completed")


if __name__ == "__main__":
    test_universal_config_validation_detailed()
