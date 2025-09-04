#!/usr/bin/env python3
"""
TDD Tests for ASL Pose Validation
Test-driven development for validating sign language poses before implementation
"""

import json
import os
from typing import Dict, List, Tuple
from unittest.mock import Mock, patch

import pytest

from src.helpmesign.utils.joint_constraints import (
    JointConstraintValidator,
    joint_validator,
)


class TestASLPoseValidation:
    """Test-driven validation of ASL poses for realistic human movement"""

    def setup_method(self):
        """Set up test fixtures"""
        self.validator = JointConstraintValidator()
        self.asl_data_path = "resources/data/signs/asl/asl_right_hand.json"

    def test_asl_a_pose_validation(self):
        """Test that ASL 'A' pose is anatomically valid and realistic"""
        # Load current ASL A pose from the data file
        asl_a_pose = self._load_asl_pose("A")

        # Validate the pose against human anatomical constraints
        constrained_pose = self.validator.validate_and_constrain_pose(asl_a_pose)

        # Test that the constrained pose is valid (no violations)
        assert self.validator.is_pose_valid(
            constrained_pose
        ), "ASL A pose should be anatomically valid after constraint application"

        # Test specific joint constraints for ASL A (fist)
        self._validate_fist_formation(asl_a_pose, "ASL A")

        # Test that arm position is realistic for signing
        self._validate_arm_position_for_signing(asl_a_pose, "ASL A")

    def test_asl_a_pose_chest_height_positioning(self):
        """Test that ASL 'A' pose positions hand at chest height for optimal visibility"""
        # Test different arm positions to find optimal chest height positioning
        test_positions = [
            # (shoulder_h, shoulder_p, arm_h, arm_p, description)
            (0, 0, 0, 0, "neutral_arms_down"),
            (0, 15, 0, 30, "slight_shoulder_raise_arm_forward"),
            (0, 30, 0, 45, "moderate_shoulder_raise_arm_forward"),
            (0, 45, 0, 60, "higher_shoulder_raise_arm_forward"),
            (0, -15, 0, 15, "shoulder_lowered_arm_slightly_forward"),
        ]

        for shoulder_h, shoulder_p, arm_h, arm_p, description in test_positions:
            test_pose = {
                "mixamorig:RightShoulder": [shoulder_h, shoulder_p, 0],
                "mixamorig:RightArm": [arm_h, arm_p, 0],
                "mixamorig:RightForeArm": [0, 0, 0],
                "mixamorig:RightHand": [0, 0, 0],
                # Fist formation
                "mixamorig:RightHandIndex1": [0, 80, 0],
                "mixamorig:RightHandIndex2": [0, 100, 0],
                "mixamorig:RightHandIndex3": [0, 80, 0],
                "mixamorig:RightHandMiddle1": [0, 80, 0],
                "mixamorig:RightHandMiddle2": [0, 100, 0],
                "mixamorig:RightHandMiddle3": [0, 80, 0],
                "mixamorig:RightHandRing1": [0, 80, 0],
                "mixamorig:RightHandRing2": [0, 100, 0],
                "mixamorig:RightHandRing3": [0, 80, 0],
                "mixamorig:RightHandPinky1": [0, 80, 0],
                "mixamorig:RightHandPinky2": [0, 100, 0],
                "mixamorig:RightHandPinky3": [0, 80, 0],
                "mixamorig:RightHandThumb1": [0, 0, 0],
                "mixamorig:RightHandThumb2": [0, 0, 0],
                "mixamorig:RightHandThumb3": [0, 0, 0],
            }

            # Validate the test pose
            constrained_pose = self.validator.validate_and_constrain_pose(test_pose)

            # Test that the pose is anatomically valid
            assert self.validator.is_pose_valid(
                constrained_pose
            ), f"ASL A test pose '{description}' should be valid"

            # Test that the pose maintains fist formation
            self._validate_fist_formation(
                constrained_pose, f"ASL A test pose '{description}'"
            )

            # Log the constrained values for analysis
            print(f"\nASL A Test Position: {description}")
            print(
                f"  Shoulder: {constrained_pose.get('mixamorig:RightShoulder', 'N/A')}"
            )
            print(f"  Arm: {constrained_pose.get('mixamorig:RightArm', 'N/A')}")
            print(f"  ForeArm: {constrained_pose.get('mixamorig:RightForeArm', 'N/A')}")

    def test_asl_a_pose_optimal_positioning(self):
        """Test to find the optimal positioning for ASL 'A' at chest height"""
        # Based on the constraint analysis, test the optimal position
        # RightShoulder: min_p=-60, max_p=180 (pitch controls forward/backward)
        # RightArm: min_p=0, max_p=150 (pitch controls arm flexion)

        # Test optimal chest height positioning
        optimal_pose = {
            "mixamorig:RightShoulder": [0, 20, 0],  # Slight forward shoulder
            "mixamorig:RightArm": [0, 45, 0],  # Arm forward at chest height
            "mixamorig:RightForeArm": [0, 0, 0],  # Forearm neutral
            "mixamorig:RightHand": [0, 0, 0],  # Hand neutral
            # Fist formation
            "mixamorig:RightHandIndex1": [0, 80, 0],
            "mixamorig:RightHandIndex2": [0, 100, 0],
            "mixamorig:RightHandIndex3": [0, 80, 0],
            "mixamorig:RightHandMiddle1": [0, 80, 0],
            "mixamorig:RightHandMiddle2": [0, 100, 0],
            "mixamorig:RightHandMiddle3": [0, 80, 0],
            "mixamorig:RightHandRing1": [0, 80, 0],
            "mixamorig:RightHandRing2": [0, 100, 0],
            "mixamorig:RightHandRing3": [0, 80, 0],
            "mixamorig:RightHandPinky1": [0, 80, 0],
            "mixamorig:RightHandPinky2": [0, 100, 0],
            "mixamorig:RightHandPinky3": [0, 80, 0],
            "mixamorig:RightHandThumb1": [0, 0, 0],
            "mixamorig:RightHandThumb2": [0, 0, 0],
            "mixamorig:RightHandThumb3": [0, 0, 0],
        }

        # Validate the optimal pose
        constrained_pose = self.validator.validate_and_constrain_pose(optimal_pose)

        # Test that the pose is valid
        assert self.validator.is_pose_valid(
            constrained_pose
        ), "Optimal ASL A pose should be valid"

        # Test that the pose maintains fist formation
        self._validate_fist_formation(constrained_pose, "Optimal ASL A")

        # Test that the arm is positioned for optimal visibility
        arm_pose = constrained_pose.get("mixamorig:RightArm", [0, 0, 0])
        shoulder_pose = constrained_pose.get("mixamorig:RightShoulder", [0, 0, 0])

        # Arm should be forward (positive pitch) for chest height visibility
        assert (
            arm_pose[1] > 0
        ), "Arm should be positioned forward for chest height visibility"
        assert (
            arm_pose[1] <= 90
        ), "Arm should not be raised too high (above chest level)"

        # Shoulder should be slightly forward to support arm position
        assert shoulder_pose[1] >= 0, "Shoulder should be neutral or slightly forward"
        assert shoulder_pose[1] <= 45, "Shoulder should not be raised too high"

        print(f"\nOptimal ASL A Pose Validation:")
        print(f"  Shoulder: {shoulder_pose}")
        print(f"  Arm: {arm_pose}")
        print(f"  ForeArm: {constrained_pose.get('mixamorig:RightForeArm', 'N/A')}")
        print(f"  Hand: {constrained_pose.get('mixamorig:RightHand', 'N/A')}")

    def test_asl_b_pose_validation(self):
        """Test that ASL 'B' pose (flat hand) is anatomically valid"""
        # ASL B is a flat hand with all fingers extended
        asl_b_pose = {
            "mixamorig:RightShoulder": [0, 20, 0],
            "mixamorig:RightArm": [0, 45, 0],
            "mixamorig:RightForeArm": [0, 0, 0],
            "mixamorig:RightHand": [0, 0, 0],
            # Flat hand formation (all fingers extended)
            "mixamorig:RightHandIndex1": [0, 0, 0],
            "mixamorig:RightHandIndex2": [0, 0, 0],
            "mixamorig:RightHandIndex3": [0, 0, 0],
            "mixamorig:RightHandMiddle1": [0, 0, 0],
            "mixamorig:RightHandMiddle2": [0, 0, 0],
            "mixamorig:RightHandMiddle3": [0, 0, 0],
            "mixamorig:RightHandRing1": [0, 0, 0],
            "mixamorig:RightHandRing2": [0, 0, 0],
            "mixamorig:RightHandRing3": [0, 0, 0],
            "mixamorig:RightHandPinky1": [0, 0, 0],
            "mixamorig:RightHandPinky2": [0, 0, 0],
            "mixamorig:RightHandPinky3": [0, 0, 0],
            "mixamorig:RightHandThumb1": [0, 0, 0],
            "mixamorig:RightHandThumb2": [0, 0, 0],
            "mixamorig:RightHandThumb3": [0, 0, 0],
        }

        # Validate the pose
        constrained_pose = self.validator.validate_and_constrain_pose(asl_b_pose)

        # Test that the pose is valid
        assert self.validator.is_pose_valid(
            constrained_pose
        ), "ASL B pose should be anatomically valid"

        # Test that the pose maintains flat hand formation
        self._validate_flat_hand_formation(constrained_pose, "ASL B")

    def test_asl_c_pose_validation(self):
        """Test that ASL 'C' pose (C-shape) is anatomically valid"""
        # ASL C is a C-shape with fingers curved
        asl_c_pose = {
            "mixamorig:RightShoulder": [0, 20, 0],
            "mixamorig:RightArm": [0, 45, 0],
            "mixamorig:RightForeArm": [0, 0, 0],
            "mixamorig:RightHand": [0, 0, 0],
            # C-shape formation (fingers curved)
            "mixamorig:RightHandIndex1": [0, 45, 0],
            "mixamorig:RightHandIndex2": [0, 60, 0],
            "mixamorig:RightHandIndex3": [0, 45, 0],
            "mixamorig:RightHandMiddle1": [0, 45, 0],
            "mixamorig:RightHandMiddle2": [0, 60, 0],
            "mixamorig:RightHandMiddle3": [0, 45, 0],
            "mixamorig:RightHandRing1": [0, 45, 0],
            "mixamorig:RightHandRing2": [0, 60, 0],
            "mixamorig:RightHandRing3": [0, 45, 0],
            "mixamorig:RightHandPinky1": [0, 45, 0],
            "mixamorig:RightHandPinky2": [0, 60, 0],
            "mixamorig:RightHandPinky3": [0, 45, 0],
            "mixamorig:RightHandThumb1": [0, 0, 0],
            "mixamorig:RightHandThumb2": [0, 0, 0],
            "mixamorig:RightHandThumb3": [0, 0, 0],
        }

        # Validate the pose
        constrained_pose = self.validator.validate_and_constrain_pose(asl_c_pose)

        # Test that the pose is valid
        assert self.validator.is_pose_valid(
            constrained_pose
        ), "ASL C pose should be anatomically valid"

        # Test that the pose maintains C-shape formation
        self._validate_c_shape_formation(constrained_pose, "ASL C")

    def test_pose_visibility_from_front_view(self):
        """Test that poses are visible and clear from front view"""
        # Test poses that should be visible from front
        front_view_poses = [
            {
                "name": "chest_height_fist",
                "pose": {
                    "mixamorig:RightShoulder": [0, 20, 0],
                    "mixamorig:RightArm": [0, 45, 0],
                    "mixamorig:RightForeArm": [0, 0, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                },
            },
            {
                "name": "shoulder_height_fist",
                "pose": {
                    "mixamorig:RightShoulder": [0, 45, 0],
                    "mixamorig:RightArm": [0, 60, 0],
                    "mixamorig:RightForeArm": [0, 0, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                },
            },
            {
                "name": "face_height_fist",
                "pose": {
                    "mixamorig:RightShoulder": [0, 60, 0],
                    "mixamorig:RightArm": [0, 75, 0],
                    "mixamorig:RightForeArm": [0, 0, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                },
            },
        ]

        for test_case in front_view_poses:
            pose_name = test_case["name"]
            pose = test_case["pose"]

            # Validate the pose
            constrained_pose = self.validator.validate_and_constrain_pose(pose)

            # Test that the pose is valid
            assert self.validator.is_pose_valid(
                constrained_pose
            ), f"Front view pose '{pose_name}' should be valid"

            # Test that the pose is positioned for front view visibility
            arm_pose = constrained_pose.get("mixamorig:RightArm", [0, 0, 0])
            shoulder_pose = constrained_pose.get("mixamorig:RightShoulder", [0, 0, 0])

            # Arm should be forward (positive pitch) for front view visibility
            assert (
                arm_pose[1] > 0
            ), f"Arm should be positioned forward for front view visibility in '{pose_name}'"
            assert (
                arm_pose[1] <= 120
            ), f"Arm should not be raised too high in '{pose_name}'"

            print(f"\nFront View Pose '{pose_name}':")
            print(f"  Shoulder: {shoulder_pose}")
            print(f"  Arm: {arm_pose}")

    def test_pose_transition_smoothness(self):
        """Test that pose transitions are smooth and realistic"""
        # Test smooth transition from neutral to ASL A
        transition_poses = [
            {
                "name": "neutral",
                "pose": {
                    "mixamorig:RightShoulder": [0, 0, 0],
                    "mixamorig:RightArm": [0, 0, 0],
                    "mixamorig:RightForeArm": [0, 0, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                },
            },
            {
                "name": "transition_1",
                "pose": {
                    "mixamorig:RightShoulder": [0, 10, 0],
                    "mixamorig:RightArm": [0, 20, 0],
                    "mixamorig:RightForeArm": [0, 0, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                },
            },
            {
                "name": "transition_2",
                "pose": {
                    "mixamorig:RightShoulder": [0, 15, 0],
                    "mixamorig:RightArm": [0, 35, 0],
                    "mixamorig:RightForeArm": [0, 0, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                },
            },
            {
                "name": "final_asl_a",
                "pose": {
                    "mixamorig:RightShoulder": [0, 20, 0],
                    "mixamorig:RightArm": [0, 45, 0],
                    "mixamorig:RightForeArm": [0, 0, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                },
            },
        ]

        for test_case in transition_poses:
            pose_name = test_case["name"]
            pose = test_case["pose"]

            # Validate the pose
            constrained_pose = self.validator.validate_and_constrain_pose(pose)

            # Test that the pose is valid
            assert self.validator.is_pose_valid(
                constrained_pose
            ), f"Transition pose '{pose_name}' should be valid"

            print(f"\nTransition Pose '{pose_name}':")
            print(
                f"  Shoulder: {constrained_pose.get('mixamorig:RightShoulder', 'N/A')}"
            )
            print(f"  Arm: {constrained_pose.get('mixamorig:RightArm', 'N/A')}")

    def _load_asl_pose(self, letter: str) -> Dict[str, List[float]]:
        """Load ASL pose data from the JSON file"""
        try:
            if os.path.exists(self.asl_data_path):
                with open(self.asl_data_path, "r") as f:
                    data = json.load(f)
                    if "alphabet" in data and letter in data["alphabet"]:
                        return data["alphabet"][letter].get("pose", {})
        except Exception as e:
            print(f"Error loading ASL pose for '{letter}': {e}")

        # Return empty pose if loading fails
        return {}

    def _validate_fist_formation(self, pose: Dict[str, List[float]], pose_name: str):
        """Validate that the pose maintains proper fist formation"""
        # Check that all fingers are curled (positive pitch values)
        finger_joints = [
            "mixamorig:RightHandIndex1",
            "mixamorig:RightHandIndex2",
            "mixamorig:RightHandIndex3",
            "mixamorig:RightHandMiddle1",
            "mixamorig:RightHandMiddle2",
            "mixamorig:RightHandMiddle3",
            "mixamorig:RightHandRing1",
            "mixamorig:RightHandRing2",
            "mixamorig:RightHandRing3",
            "mixamorig:RightHandPinky1",
            "mixamorig:RightHandPinky2",
            "mixamorig:RightHandPinky3",
        ]

        for joint_name in finger_joints:
            if joint_name in pose:
                h, p, r = pose[joint_name]
                # Fingers should be curled (positive pitch values)
                assert (
                    p > 0
                ), f"{pose_name} {joint_name} should be curled (pitch > 0), got {p}"
                assert (
                    p <= 120
                ), f"{pose_name} {joint_name} should not be over-curled (pitch <= 120), got {p}"

        # Check that thumb is positioned for ASL signs (extended to side for visibility)
        thumb_joints = [
            "mixamorig:RightHandThumb1",
            "mixamorig:RightHandThumb2",
            "mixamorig:RightHandThumb3",
        ]

        for joint_name in thumb_joints:
            if joint_name in pose:
                h, p, r = pose[joint_name]
                # Thumb should be positioned for ASL signs
                assert (
                    abs(h) <= 45
                ), f"{pose_name} {joint_name} heading should be neutral, got {h}"
                assert (
                    abs(p) <= 20
                ), f"{pose_name} {joint_name} pitch should be neutral, got {p}"
                # Thumb roll should be neutral for ASL 'A' (fist with thumb to side)
                assert (
                    abs(r) <= 45
                ), f"{pose_name} {joint_name} roll should be neutral for ASL A, got {r}"

    def _validate_flat_hand_formation(
        self, pose: Dict[str, List[float]], pose_name: str
    ):
        """Validate that the pose maintains proper flat hand formation"""
        # Check that all fingers are extended (neutral pitch values)
        finger_joints = [
            "mixamorig:RightHandIndex1",
            "mixamorig:RightHandIndex2",
            "mixamorig:RightHandIndex3",
            "mixamorig:RightHandMiddle1",
            "mixamorig:RightHandMiddle2",
            "mixamorig:RightHandMiddle3",
            "mixamorig:RightHandRing1",
            "mixamorig:RightHandRing2",
            "mixamorig:RightHandRing3",
            "mixamorig:RightHandPinky1",
            "mixamorig:RightHandPinky2",
            "mixamorig:RightHandPinky3",
        ]

        for joint_name in finger_joints:
            if joint_name in pose:
                h, p, r = pose[joint_name]
                # Fingers should be extended (neutral pitch values)
                assert (
                    abs(p) <= 10
                ), f"{pose_name} {joint_name} should be extended (pitch ≈ 0), got {p}"

    def _validate_c_shape_formation(self, pose: Dict[str, List[float]], pose_name: str):
        """Validate that the pose maintains proper C-shape formation"""
        # Check that all fingers are curved (moderate positive pitch values)
        finger_joints = [
            "mixamorig:RightHandIndex1",
            "mixamorig:RightHandIndex2",
            "mixamorig:RightHandIndex3",
            "mixamorig:RightHandMiddle1",
            "mixamorig:RightHandMiddle2",
            "mixamorig:RightHandMiddle3",
            "mixamorig:RightHandRing1",
            "mixamorig:RightHandRing2",
            "mixamorig:RightHandRing3",
            "mixamorig:RightHandPinky1",
            "mixamorig:RightHandPinky2",
            "mixamorig:RightHandPinky3",
        ]

        for joint_name in finger_joints:
            if joint_name in pose:
                h, p, r = pose[joint_name]
                # Fingers should be curved (moderate positive pitch values)
                assert (
                    30 <= p <= 90
                ), f"{pose_name} {joint_name} should be curved (pitch 30-90), got {p}"

    def _validate_arm_position_for_signing(
        self, pose: Dict[str, List[float]], pose_name: str
    ):
        """Validate that the arm is positioned appropriately for signing"""
        # Check that the arm is positioned for optimal signing visibility
        arm_pose = pose.get("mixamorig:RightArm", [0, 0, 0])
        shoulder_pose = pose.get("mixamorig:RightShoulder", [0, 0, 0])

        # Arm should be forward (positive pitch) for signing visibility
        assert (
            arm_pose[1] >= 0
        ), f"{pose_name} arm should be positioned forward for signing, got {arm_pose[1]}"
        assert (
            arm_pose[1] <= 120
        ), f"{pose_name} arm should not be raised too high, got {arm_pose[1]}"

        # Shoulder should support the arm position (allow negative values for natural poses)
        assert (
            shoulder_pose[1] >= -60
        ), f"{pose_name} shoulder should be within reasonable range, got {shoulder_pose[1]}"
        assert (
            shoulder_pose[1] <= 60
        ), f"{pose_name} shoulder should not be raised too high, got {shoulder_pose[1]}"


class TestASLPoseOptimization:
    """Test optimization of ASL poses for best visibility and realism"""

    def setup_method(self):
        """Set up test fixtures"""
        self.validator = JointConstraintValidator()

    def test_optimal_chest_height_positioning(self):
        """Test to find the optimal chest height positioning for ASL signs"""
        # Test various combinations to find the best chest height positioning
        test_combinations = [
            # (shoulder_pitch, arm_pitch, description)
            (0, 30, "neutral_shoulder_moderate_arm"),
            (10, 35, "slight_shoulder_moderate_arm"),
            (20, 40, "moderate_shoulder_moderate_arm"),
            (15, 45, "slight_shoulder_forward_arm"),
            (25, 50, "moderate_shoulder_forward_arm"),
            (30, 55, "higher_shoulder_forward_arm"),
        ]

        optimal_poses = []

        for shoulder_p, arm_p, description in test_combinations:
            test_pose = {
                "mixamorig:RightShoulder": [0, shoulder_p, 0],
                "mixamorig:RightArm": [0, arm_p, 0],
                "mixamorig:RightForeArm": [0, 0, 0],
                "mixamorig:RightHand": [0, 0, 0],
            }

            # Validate the pose
            constrained_pose = self.validator.validate_and_constrain_pose(test_pose)

            # Test that the pose is valid
            assert self.validator.is_pose_valid(
                constrained_pose
            ), f"Chest height test '{description}' should be valid"

            # Check if this is a good chest height position
            arm_pose = constrained_pose.get("mixamorig:RightArm", [0, 0, 0])
            shoulder_pose = constrained_pose.get("mixamorig:RightShoulder", [0, 0, 0])

            # Good chest height: arm pitch between 30-60 degrees
            if 30 <= arm_pose[1] <= 60:
                optimal_poses.append(
                    {
                        "description": description,
                        "shoulder": shoulder_pose,
                        "arm": arm_pose,
                        "score": self._calculate_visibility_score(
                            shoulder_pose, arm_pose
                        ),
                    }
                )

            print(f"\nChest Height Test '{description}':")
            print(f"  Shoulder: {shoulder_pose}")
            print(f"  Arm: {arm_pose}")
            print(f"  Valid: {self.validator.is_pose_valid(constrained_pose)}")

        # Find the best pose based on visibility score
        if optimal_poses:
            best_pose = max(optimal_poses, key=lambda x: x["score"])
            print(f"\nBest Chest Height Position: {best_pose['description']}")
            print(f"  Shoulder: {best_pose['shoulder']}")
            print(f"  Arm: {best_pose['arm']}")
            print(f"  Score: {best_pose['score']}")

            # Test that the best pose is valid
            assert (
                best_pose["score"] > 0
            ), "Best pose should have positive visibility score"

    def _calculate_visibility_score(
        self, shoulder_pose: List[float], arm_pose: List[float]
    ) -> float:
        """Calculate a visibility score for the pose"""
        # Higher score = better visibility
        # Factors: arm forward position, shoulder support, not too high/low

        arm_pitch = arm_pose[1]
        shoulder_pitch = shoulder_pose[1]

        # Base score from arm position (30-60 degrees is optimal)
        if 30 <= arm_pitch <= 60:
            arm_score = 100 - abs(arm_pitch - 45) * 2  # Peak at 45 degrees
        else:
            arm_score = max(
                0, 100 - abs(arm_pitch - 45) * 3
            )  # Penalty for being outside optimal range

        # Shoulder support score (should support arm position)
        if 0 <= shoulder_pitch <= 30:
            shoulder_score = 100 - abs(shoulder_pitch - 15) * 2  # Peak at 15 degrees
        else:
            shoulder_score = max(0, 100 - abs(shoulder_pitch - 15) * 3)

        # Combined score
        return (arm_score + shoulder_score) / 2


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
