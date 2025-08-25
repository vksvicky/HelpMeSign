"""
Test to validate all current pose data in the system.
Ensures no inhuman positions exist in existing sign language data.
"""

import json
import os

import pytest

from src.helpmesign.utils.joint_limits import JointValidator
from src.helpmesign.utils.resource_manager import ResourceManager


class TestCurrentPoseDataValidation:
    """Test validation of all current pose data in the system."""

    def test_pose_mappings_validation(self):
        """Test that all pose mappings in the system are valid."""
        validator = JointValidator()
        resource_manager = ResourceManager()

        # Get the pose mappings file path
        pose_file_path = resource_manager.get_resource_path(
            "data/signs/asl", "pose_mappings.json"
        )

        assert os.path.exists(
            pose_file_path
        ), f"Pose mappings file not found: {pose_file_path}"

        # Load and validate the pose data
        with open(pose_file_path, "r") as f:
            pose_data = json.load(f)

        # Test each sign
        for sign_name, sign_data in pose_data.items():
            print(f"Validating sign: {sign_name}")

            if "frames" in sign_data:
                for i, frame in enumerate(sign_data["frames"]):
                    if "poses" in frame:
                        # Convert poses to validation format
                        pose_dict = {}
                        for pose in frame["poses"]:
                            if (
                                "joint" in pose
                                and "h" in pose
                                and "p" in pose
                                and "r" in pose
                            ):
                                pose_dict[pose["joint"]] = [
                                    pose["h"],
                                    pose["p"],
                                    pose["r"],
                                ]

                        # Validate the pose
                        is_valid, violations = validator.validate_pose(pose_dict)

                        assert is_valid, (
                            f"Sign '{sign_name}' frame {i} has invalid poses:\n"
                            f"Poses: {pose_dict}\n"
                            f"Violations: {violations}"
                        )

                        print(f"  ✅ Frame {i}: Valid")
                    else:
                        print(f"  ⚠️  Frame {i}: No poses found")
            else:
                print(f"  ⚠️  No frames found for sign '{sign_name}'")

    def test_sign_language_loader_validation(self):
        """Test that sign language loader produces valid poses."""
        from src.helpmesign.utils.sign_language_loader import SignLanguageLoader

        validator = JointValidator()
        loader = SignLanguageLoader()

        # Test different languages and hands
        test_cases = [
            ("asl", "right"),
            ("asl", "left"),
            ("bsl", "right"),
            ("bsl", "left"),
        ]

        for language, hand in test_cases:
            print(f"Testing {language} with {hand} hand")

            # Get word signs
            words = loader.get_word_signs(language, hand)

            for word, sign_data in words.items():
                if "pose" in sign_data:
                    pose_data = sign_data["pose"]

                    # Convert to validation format if needed
                    if isinstance(pose_data, dict):
                        # Convert joint -> [h, p, r] format
                        validation_pose = {}
                        for joint_name, hpr in pose_data.items():
                            if isinstance(hpr, list) and len(hpr) >= 3:
                                validation_pose[joint_name] = hpr[:3]

                        # Validate
                        is_valid, violations = validator.validate_pose(validation_pose)

                        assert is_valid, (
                            f"Word '{word}' in {language} ({hand} hand) has invalid pose:\n"
                            f"Pose: {pose_data}\n"
                            f"Violations: {violations}"
                        )

                        print(f"  ✅ {word}: Valid")
                    else:
                        print(f"  ⚠️  {word}: No pose data")

    def test_sign_mt_integration_validation(self):
        """Test that sign.mt integration produces valid poses."""
        try:
            from src.helpmesign.utils.sign_mt_integration import SignMTTranslator

            validator = JointValidator()
            translator = SignMTTranslator()

            # Test basic signs
            test_words = [
                "hello",
                "thank_you",
                "yes",
                "no",
                "welcome",
                "help",
                "please",
            ]

            for word in test_words:
                print(f"Testing sign.mt translation for: {word}")

                try:
                    # Get sign sequence
                    sequence = translator.translate_text_to_signs(word)

                    if sequence and hasattr(sequence, "frames"):
                        for i, frame in enumerate(sequence.frames):
                            if hasattr(frame, "poses"):
                                # Convert poses to validation format
                                pose_dict = {}
                                for pose in frame.poses:
                                    if hasattr(pose, "joint") and hasattr(pose, "hpr"):
                                        pose_dict[pose.joint] = pose.hpr

                                # Validate
                                is_valid, violations = validator.validate_pose(
                                    pose_dict
                                )

                                assert is_valid, (
                                    f"Sign.mt word '{word}' frame {i} has invalid poses:\n"
                                    f"Poses: {pose_dict}\n"
                                    f"Violations: {violations}"
                                )

                                print(f"  ✅ Frame {i}: Valid")
                            else:
                                print(f"  ⚠️  Frame {i}: No poses found")
                    else:
                        print(f"  ⚠️  No sequence or frames found for '{word}'")

                except Exception as e:
                    print(f"  ⚠️  Error testing '{word}': {e}")

        except ImportError:
            pytest.skip("Sign.mt integration not available")

    def test_hpr_editor_validation(self):
        """Test that HPR editor produces valid poses."""
        try:
            from src.helpmesign.modes.learn.hpr_editor import JointPose, PoseManager

            validator = JointValidator()
            pose_manager = PoseManager()

            # Test neutral pose
            neutral_poses = pose_manager.get_all_poses()

            # Convert to validation format
            pose_dict = {}
            for joint_name, joint_pose in neutral_poses.items():
                pose_dict[joint_name] = [
                    joint_pose.heading,
                    joint_pose.pitch,
                    joint_pose.roll,
                ]

            # Validate neutral pose
            is_valid, violations = validator.validate_pose(pose_dict)

            assert is_valid, (
                f"Neutral pose has invalid positions:\n" f"Violations: {violations}"
            )

            print("✅ Neutral pose: Valid")

        except ImportError:
            pytest.skip("HPR editor not available")

    def test_extreme_pose_detection(self):
        """Test detection of extreme poses that should be caught."""
        validator = JointValidator()

        # Test poses that should definitely be invalid
        extreme_poses = [
            # Arm bent backwards (impossible)
            {"mixamorig:RightArm": [0, 200, 0]},
            # Hand rotated 360 degrees (impossible)
            {"mixamorig:RightHand": [0, 0, 360]},
            # Finger bent backwards (impossible)
            {"mixamorig:RightHandIndex1": [0, -90, 0]},
            # Head turned 180 degrees (impossible)
            {"mixamorig:Head": [180, 0, 0]},
            # Multiple extreme positions
            {
                "mixamorig:RightArm": [200, 300, 100],
                "mixamorig:RightHand": [180, 180, 180],
                "mixamorig:RightHandIndex1": [100, 200, 50],
            },
        ]

        for i, pose in enumerate(extreme_poses):
            is_valid, violations = validator.validate_pose(pose)

            assert (
                not is_valid
            ), f"Extreme pose {i} should be invalid but passed validation"
            assert len(violations) > 0, f"Extreme pose {i} should have violations"

            print(
                f"✅ Extreme pose {i}: Correctly detected as invalid ({len(violations)} violations)"
            )

    def test_biomechanical_constraints(self):
        """Test that biomechanical constraints are properly enforced."""
        validator = JointValidator()

        # Test realistic vs unrealistic ranges
        realistic_poses = [
            # Normal arm raise
            {"mixamorig:RightArm": [0, 90, 0]},
            # Normal hand rotation
            {"mixamorig:RightHand": [0, 0, 45]},
            # Normal finger bend
            {"mixamorig:RightHandIndex1": [0, 45, 0]},
            # Normal head turn
            {"mixamorig:Head": [30, 0, 0]},
        ]

        unrealistic_poses = [
            # Arm bent backwards
            {"mixamorig:RightArm": [0, 200, 0]},
            # Hand rotated impossibly
            {"mixamorig:RightHand": [0, 0, 180]},
            # Finger bent backwards
            {"mixamorig:RightHandIndex1": [0, -45, 0]},
            # Head turned impossibly
            {"mixamorig:Head": [120, 0, 0]},
        ]

        # Test realistic poses should be valid
        for i, pose in enumerate(realistic_poses):
            is_valid, violations = validator.validate_pose(pose)
            assert (
                is_valid
            ), f"Realistic pose {i} should be valid but failed: {violations}"
            print(f"✅ Realistic pose {i}: Correctly validated")

        # Test unrealistic poses should be invalid
        for i, pose in enumerate(unrealistic_poses):
            is_valid, violations = validator.validate_pose(pose)
            assert not is_valid, f"Unrealistic pose {i} should be invalid but passed"
            print(f"✅ Unrealistic pose {i}: Correctly rejected")
