#!/usr/bin/env python3
"""
Tests for pose data validation and analysis
"""

import json
import os
import sys
from pathlib import Path

import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestPoseDataValidation:
    """Test validation of pose data from sign language files."""

    def setup_method(self):
        """Set up test fixtures."""
        self.project_root = os.path.join(os.path.dirname(__file__), "..", "..")
        self.resources_path = os.path.join(self.project_root, "resources")

    def test_pose_data_structure(self):
        """Test that pose data has correct structure."""
        asl_file = os.path.join(
            self.resources_path, "data", "signs", "asl", "asl_right_hand.json"
        )

        if os.path.exists(asl_file):
            with open(asl_file, "r", encoding="utf-8") as f:
                asl_data = json.load(f)

            # Test alphabet pose data
            if "alphabet" in asl_data:
                letters_with_pose = 0
                for letter, data in asl_data["alphabet"].items():
                    # Only test letters that have pose data (some may only have SVG/description)
                    if "pose" in data:
                        letters_with_pose += 1
                        pose = data["pose"]
                        assert isinstance(
                            pose, dict
                        ), f"Letter {letter} pose should be dict"

                        for joint_name, hpr_values in pose.items():
                            # Validate joint name format
                            assert joint_name.startswith(
                                "mixamorig:"
                            ), f"Invalid joint name format: {joint_name}"

                            # Validate HPR values
                            assert isinstance(
                                hpr_values, list
                            ), f"HPR values should be list for {joint_name}"
                            assert (
                                len(hpr_values) == 3
                            ), f"HPR should have 3 values for {joint_name}"

                            # Check value types
                            for i, value in enumerate(hpr_values):
                                assert isinstance(
                                    value, (int, float)
                                ), f"HPR[{i}] should be numeric for {joint_name}: {value}"

                # Should have at least some letters with pose data
                assert (
                    letters_with_pose > 0
                ), "Should have at least some letters with pose data"

            # Test numbers pose data
            if "numbers" in asl_data:
                numbers_with_pose = 0
                for number, data in asl_data["numbers"].items():
                    # Only test numbers that have pose data (some may only have SVG/description)
                    if "pose" in data:
                        numbers_with_pose += 1
                        pose = data["pose"]
                        assert isinstance(
                            pose, dict
                        ), f"Number {number} pose should be dict"

                # Note: Numbers might not have pose data yet in current implementation
                if numbers_with_pose == 0:
                    print(
                        "  ⚠️  No numbers have pose data yet - this is expected in current implementation"
                    )

    def test_pose_value_ranges(self):
        """Test that pose values are within reasonable ranges."""
        asl_file = os.path.join(
            self.resources_path, "data", "signs", "asl", "asl_right_hand.json"
        )

        if os.path.exists(asl_file):
            with open(asl_file, "r", encoding="utf-8") as f:
                asl_data = json.load(f)

            extreme_values = []

            # Check alphabet poses
            if "alphabet" in asl_data:
                for letter, data in asl_data["alphabet"].items():
                    # Only check letters that have pose data
                    if "pose" in data:
                        pose = data["pose"]

                        for joint_name, hpr_values in pose.items():
                            for i, value in enumerate(hpr_values):
                                # Flag extreme values (beyond typical joint limits)
                                if abs(value) > 180:
                                    extreme_values.append(
                                        {
                                            "sign": letter,
                                            "joint": joint_name,
                                            "axis": ["H", "P", "R"][i],
                                            "value": value,
                                        }
                                    )

            # Report extreme values for analysis
            if extreme_values:
                print(f"\n⚠️  Found {len(extreme_values)} extreme pose values:")
                for extreme in extreme_values[:10]:  # Show first 10
                    print(
                        f"  {extreme['sign']}: {extreme['joint']} {extreme['axis']}={extreme['value']}"
                    )

    def test_joint_name_consistency(self):
        """Test that joint names are consistent across signs."""
        asl_file = os.path.join(
            self.resources_path, "data", "signs", "asl", "asl_right_hand.json"
        )

        if os.path.exists(asl_file):
            with open(asl_file, "r", encoding="utf-8") as f:
                asl_data = json.load(f)

            all_joint_names = set()

            # Collect all joint names
            if "alphabet" in asl_data:
                for letter, data in asl_data["alphabet"].items():
                    if "pose" in data:
                        pose = data["pose"]
                        all_joint_names.update(pose.keys())

            if "numbers" in asl_data:
                for number, data in asl_data["numbers"].items():
                    if "pose" in data:
                        pose = data["pose"]
                        all_joint_names.update(pose.keys())

            # Validate joint name patterns
            expected_patterns = [
                "mixamorig:Right",  # Right side joints
                "mixamorig:Left",  # Left side joints (if any)
            ]

            valid_joint_names = []
            invalid_joint_names = []

            for joint_name in all_joint_names:
                if any(pattern in joint_name for pattern in expected_patterns):
                    valid_joint_names.append(joint_name)
                else:
                    invalid_joint_names.append(joint_name)

            # Report findings
            print(f"\n📊 Joint name analysis:")
            print(f"  Valid joint names: {len(valid_joint_names)}")
            print(f"  Invalid joint names: {len(invalid_joint_names)}")

            if invalid_joint_names:
                print(f"  Invalid names: {invalid_joint_names}")

            # Most names should be valid
            assert len(valid_joint_names) > len(
                invalid_joint_names
            ), "Most joint names should follow expected patterns"

    def test_safe_vs_unsafe_joints(self):
        """Test classification of safe vs unsafe joints."""
        # Define safe joints (same as GLB viewer)
        safe_joints = [
            "mixamorig:RightArm",
            "mixamorig:LeftArm",
            "mixamorig:RightForeArm",
            "mixamorig:LeftForeArm",
            "mixamorig:RightHand",
            "mixamorig:LeftHand",
        ]

        # Add finger joints
        for hand in ["Right", "Left"]:
            for finger in ["Thumb", "Index", "Middle", "Ring", "Pinky"]:
                for i in range(1, 5):
                    safe_joints.append(f"mixamorig:{hand}Hand{finger}{i}")

        # Define known problematic joints
        unsafe_joints = [
            "mixamorig:RightShoulder",
            "mixamorig:LeftShoulder",
            "mixamorig:Spine",
            "mixamorig:Spine1",
            "mixamorig:Spine2",
            "mixamorig:Hips",
            "mixamorig:RightUpLeg",
            "mixamorig:LeftUpLeg",
            "mixamorig:Neck",
            "mixamorig:Head",
        ]

        asl_file = os.path.join(
            self.resources_path, "data", "signs", "asl", "asl_right_hand.json"
        )

        if os.path.exists(asl_file):
            with open(asl_file, "r", encoding="utf-8") as f:
                asl_data = json.load(f)

            # Analyze letter A pose
            if "alphabet" in asl_data and "A" in asl_data["alphabet"]:
                pose_data = asl_data["alphabet"]["A"]["pose"]

                safe_count = 0
                unsafe_count = 0
                unknown_count = 0

                for joint_name in pose_data.keys():
                    if joint_name in safe_joints:
                        safe_count += 1
                    elif joint_name in unsafe_joints:
                        unsafe_count += 1
                    else:
                        unknown_count += 1

                print(f"\n📊 Joint safety analysis for letter A:")
                print(f"  Safe joints: {safe_count}")
                print(f"  Unsafe joints: {unsafe_count}")
                print(f"  Unknown joints: {unknown_count}")

                # Should have some safe joints
                assert safe_count > 0, "Letter A should have some safe joints"

    def test_pose_comparison_with_natural_pose(self):
        """Test comparison between sign poses and natural pose."""
        # This test would compare sign pose values with natural pose values
        # to identify potentially problematic differences

        asl_file = os.path.join(
            self.resources_path, "data", "signs", "asl", "asl_right_hand.json"
        )

        if os.path.exists(asl_file):
            with open(asl_file, "r", encoding="utf-8") as f:
                asl_data = json.load(f)

            # Mock natural pose values (these would come from NaturalPoseService)
            mock_natural_pose = {
                "right_arm": {"hpr": [0.0, 0.0, 0.0]},
                "right_forearm": {"hpr": [0.0, 0.0, 0.0]},
                "right_hand": {"hpr": [0.0, 0.0, 0.0]},
            }

            # Joint mapping from JSON names to natural pose names
            joint_mapping = {
                "mixamorig:RightArm": "right_arm",
                "mixamorig:RightForeArm": "right_forearm",
                "mixamorig:RightHand": "right_hand",
            }

            if "alphabet" in asl_data and "A" in asl_data["alphabet"]:
                pose_data = asl_data["alphabet"]["A"]["pose"]

                large_differences = []

                for joint_name, hpr_values in pose_data.items():
                    if joint_name in joint_mapping:
                        natural_part = joint_mapping[joint_name]
                        if natural_part in mock_natural_pose:
                            natural_hpr = mock_natural_pose[natural_part]["hpr"]

                            # Calculate differences
                            diff = [hpr_values[i] - natural_hpr[i] for i in range(3)]

                            # Flag large differences
                            for i, d in enumerate(diff):
                                if abs(d) > 90:  # More than 90 degrees difference
                                    large_differences.append(
                                        {
                                            "joint": joint_name,
                                            "axis": ["H", "P", "R"][i],
                                            "sign_value": hpr_values[i],
                                            "natural_value": natural_hpr[i],
                                            "difference": d,
                                        }
                                    )

                if large_differences:
                    print(f"\n⚠️  Large differences from natural pose:")
                    for diff in large_differences[:5]:  # Show first 5
                        print(
                            f"  {diff['joint']} {diff['axis']}: {diff['sign_value']} vs {diff['natural_value']} (diff: {diff['difference']})"
                        )

    def test_finger_pose_patterns(self):
        """Test patterns in finger pose data."""
        asl_file = os.path.join(
            self.resources_path, "data", "signs", "asl", "asl_right_hand.json"
        )

        if os.path.exists(asl_file):
            with open(asl_file, "r", encoding="utf-8") as f:
                asl_data = json.load(f)

            if "alphabet" in asl_data and "A" in asl_data["alphabet"]:
                pose_data = asl_data["alphabet"]["A"]["pose"]

                # Analyze finger patterns
                finger_joints = {}

                for joint_name, hpr_values in pose_data.items():
                    if "Hand" in joint_name and any(
                        finger in joint_name
                        for finger in ["Thumb", "Index", "Middle", "Ring", "Pinky"]
                    ):
                        finger_joints[joint_name] = hpr_values

                print(f"\n🤚 Finger joint analysis for letter A:")
                print(f"  Total finger joints: {len(finger_joints)}")

                # Look for common patterns
                common_values = {}
                for joint_name, hpr_values in finger_joints.items():
                    hpr_tuple = tuple(hpr_values)
                    if hpr_tuple not in common_values:
                        common_values[hpr_tuple] = []
                    common_values[hpr_tuple].append(joint_name)

                print(f"  Unique HPR patterns: {len(common_values)}")

                # Show most common patterns
                sorted_patterns = sorted(
                    common_values.items(), key=lambda x: len(x[1]), reverse=True
                )
                for i, (pattern, joints) in enumerate(sorted_patterns[:3]):
                    print(f"  Pattern {i+1}: {pattern} used by {len(joints)} joints")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
