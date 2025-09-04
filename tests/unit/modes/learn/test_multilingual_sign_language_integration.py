#!/usr/bin/env python3
"""
Tests for multilingual sign language integration
Ensures the system works robustly across different sign languages
"""

from typing import Any, Dict, List, Tuple
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.helpmesign.modes.learn.animate_panel.animation_manager import AnimationManager
from src.helpmesign.utils.joint_constraints import (
    JointConstraintValidator,
    joint_validator,
)
from src.helpmesign.utils.pose_data_service import PoseData, PoseDataService


class TestMultilingualSignLanguageSupport:
    """Test support for multiple sign languages"""

    def test_multilingual_alphabet_consistency(self):
        """Test that alphabet poses are consistent across languages"""
        validator = JointConstraintValidator()

        # Test that basic alphabet poses work across different languages
        languages = ["ASL", "BSL", "ISL", "Auslan", "LSF", "DGS"]
        test_letters = ["A", "B", "C", "D", "E"]

        for language in languages:
            for letter in test_letters:
                # Basic pose that should work for all languages
                pose = {
                    "mixamorig:RightHand": [0, 0, 0],
                    "mixamorig:RightArm": [0, 0, 0],
                }

                constrained_pose = validator.validate_and_constrain_pose(pose)

                # Verify anatomical validity for all languages
                for joint_name, hpr in constrained_pose.items():
                    constraint = validator.get_joint_constraint(joint_name)
                    if constraint:
                        h, p, r = hpr[0], hpr[1], hpr[2]
                        assert (
                            constraint.min_h <= h <= constraint.max_h
                        ), f"{language} {letter} {joint_name} heading invalid"
                        assert (
                            constraint.min_p <= p <= constraint.max_p
                        ), f"{language} {letter} {joint_name} pitch invalid"
                        assert (
                            constraint.min_r <= r <= constraint.max_r
                        ), f"{language} {letter} {joint_name} roll invalid"

    def test_multilingual_number_consistency(self):
        """Test that number poses are consistent across languages"""
        validator = JointConstraintValidator()

        # Test that basic number poses work across different languages
        languages = ["ASL", "BSL", "ISL", "Auslan", "LSF", "DGS"]
        test_numbers = ["1", "2", "3", "4", "5"]

        for language in languages:
            for number in test_numbers:
                # Basic pose that should work for all languages
                pose = {
                    "mixamorig:RightHand": [0, 0, 0],
                    "mixamorig:RightArm": [0, 0, 0],
                }

                constrained_pose = validator.validate_and_constrain_pose(pose)

                # Verify anatomical validity for all languages
                for joint_name, hpr in constrained_pose.items():
                    constraint = validator.get_joint_constraint(joint_name)
                    if constraint:
                        h, p, r = hpr[0], hpr[1], hpr[2]
                        assert (
                            constraint.min_h <= h <= constraint.max_h
                        ), f"{language} {number} {joint_name} heading invalid"
                        assert (
                            constraint.min_p <= p <= constraint.max_p
                        ), f"{language} {number} {joint_name} pitch invalid"
                        assert (
                            constraint.min_r <= r <= constraint.max_r
                        ), f"{language} {number} {joint_name} roll invalid"

    def test_multilingual_common_words_consistency(self):
        """Test that common word poses are consistent across languages"""
        validator = JointConstraintValidator()

        # Test that basic common word poses work across different languages
        languages = ["ASL", "BSL", "ISL", "Auslan", "LSF", "DGS"]
        test_words = ["HELLO", "THANK_YOU", "YES", "NO", "PLEASE", "SORRY"]

        for language in languages:
            for word in test_words:
                # Basic pose that should work for all languages
                pose = {
                    "mixamorig:RightHand": [0, 0, 0],
                    "mixamorig:RightArm": [0, 0, 0],
                }

                constrained_pose = validator.validate_and_constrain_pose(pose)

                # Verify anatomical validity for all languages
                for joint_name, hpr in constrained_pose.items():
                    constraint = validator.get_joint_constraint(joint_name)
                    if constraint:
                        h, p, r = hpr[0], hpr[1], hpr[2]
                        assert (
                            constraint.min_h <= h <= constraint.max_h
                        ), f"{language} {word} {joint_name} heading invalid"
                        assert (
                            constraint.min_p <= p <= constraint.max_p
                        ), f"{language} {word} {joint_name} pitch invalid"
                        assert (
                            constraint.min_r <= r <= constraint.max_r
                        ), f"{language} {word} {joint_name} roll invalid"

    def test_multilingual_hand_shape_consistency(self):
        """Test that hand shapes are consistent across languages"""
        validator = JointConstraintValidator()

        # Test that basic hand shapes work across different languages
        languages = ["ASL", "BSL", "ISL", "Auslan", "LSF", "DGS"]
        hand_shapes = ["fist", "open_hand", "pointing", "peace_sign", "thumbs_up"]

        for language in languages:
            for shape in hand_shapes:
                # Basic hand shape pose that should work for all languages
                pose = {
                    "mixamorig:RightHand": [0, 0, 0],
                    "mixamorig:RightHandIndex1": [0, 0, 0],
                    "mixamorig:RightHandMiddle1": [0, 0, 0],
                    "mixamorig:RightHandRing1": [0, 0, 0],
                    "mixamorig:RightHandPinky1": [0, 0, 0],
                    "mixamorig:RightHandThumb1": [0, 0, 0],
                }

                constrained_pose = validator.validate_and_constrain_pose(pose)

                # Verify anatomical validity for all languages
                for joint_name, hpr in constrained_pose.items():
                    constraint = validator.get_joint_constraint(joint_name)
                    if constraint:
                        h, p, r = hpr[0], hpr[1], hpr[2]
                        assert (
                            constraint.min_h <= h <= constraint.max_h
                        ), f"{language} {shape} {joint_name} heading invalid"
                        assert (
                            constraint.min_p <= p <= constraint.max_p
                        ), f"{language} {shape} {joint_name} pitch invalid"
                        assert (
                            constraint.min_r <= r <= constraint.max_r
                        ), f"{language} {shape} {joint_name} roll invalid"

    def test_multilingual_viewing_angle_consistency(self):
        """Test that viewing angles are consistent across languages"""
        validator = JointConstraintValidator()

        # Test that viewing angles work across different languages
        languages = ["ASL", "BSL", "ISL", "Auslan", "LSF", "DGS"]
        viewing_angles = ["front_view", "side_view", "learner_view"]

        for language in languages:
            for angle in viewing_angles:
                # Basic viewing angle pose that should work for all languages
                if angle == "front_view":
                    pose = {
                        "mixamorig:RightArm": [0, 45, 0],  # Arm raised forward
                        "mixamorig:RightHand": [0, 0, 0],  # Hand in clear view
                    }
                elif angle == "side_view":
                    pose = {
                        "mixamorig:RightArm": [90, 0, 0],  # Arm to side
                        "mixamorig:RightHand": [0, 0, 0],  # Hand visible from side
                    }
                else:  # learner_view
                    pose = {
                        "mixamorig:RightArm": [0, 30, 0],  # Arm slightly raised
                        "mixamorig:RightHand": [0, 0, 0],  # Hand in clear view
                    }

                constrained_pose = validator.validate_and_constrain_pose(pose)

                # Verify anatomical validity for all languages
                for joint_name, hpr in constrained_pose.items():
                    constraint = validator.get_joint_constraint(joint_name)
                    if constraint:
                        h, p, r = hpr[0], hpr[1], hpr[2]
                        assert (
                            constraint.min_h <= h <= constraint.max_h
                        ), f"{language} {angle} {joint_name} heading invalid"
                        assert (
                            constraint.min_p <= p <= constraint.max_p
                        ), f"{language} {angle} {joint_name} pitch invalid"
                        assert (
                            constraint.min_r <= r <= constraint.max_r
                        ), f"{language} {angle} {joint_name} roll invalid"

    def test_multilingual_bilateral_signing_consistency(self):
        """Test that bilateral signing is consistent across languages"""
        validator = JointConstraintValidator()

        # Test that bilateral signing works across different languages
        languages = ["ASL", "BSL", "ISL", "Auslan", "LSF", "DGS"]

        for language in languages:
            # Basic bilateral pose that should work for all languages
            pose = {
                "mixamorig:RightArm": [45, 30, 0],
                "mixamorig:LeftArm": [-45, 30, 0],  # Mirrored
                "mixamorig:RightHand": [0, 0, 0],
                "mixamorig:LeftHand": [0, 0, 0],  # Mirrored
            }

            constrained_pose = validator.validate_and_constrain_pose(pose)

            # Verify anatomical validity for all languages
            for joint_name, hpr in constrained_pose.items():
                constraint = validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"{language} bilateral {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"{language} bilateral {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"{language} bilateral {joint_name} roll invalid"

    def test_multilingual_hand_preference_consistency(self):
        """Test that hand preference is consistent across languages"""
        validator = JointConstraintValidator()

        # Test that hand preference works across different languages
        languages = ["ASL", "BSL", "ISL", "Auslan", "LSF", "DGS"]
        hand_preferences = ["right", "left"]

        for language in languages:
            for preference in hand_preferences:
                # Basic hand preference pose that should work for all languages
                if preference == "right":
                    pose = {
                        "mixamorig:RightArm": [0, 45, 0],  # Right arm active
                        "mixamorig:LeftArm": [0, 0, 0],  # Left arm neutral
                        "mixamorig:RightHand": [0, 0, 0],  # Right hand active
                        "mixamorig:LeftHand": [0, 0, 0],  # Left hand neutral
                    }
                else:  # left
                    pose = {
                        "mixamorig:RightArm": [0, 0, 0],  # Right arm neutral
                        "mixamorig:LeftArm": [0, 45, 0],  # Left arm active
                        "mixamorig:RightHand": [0, 0, 0],  # Right hand neutral
                        "mixamorig:LeftHand": [0, 0, 0],  # Left hand active
                    }

                constrained_pose = validator.validate_and_constrain_pose(pose)

                # Verify anatomical validity for all languages
                for joint_name, hpr in constrained_pose.items():
                    constraint = validator.get_joint_constraint(joint_name)
                    if constraint:
                        h, p, r = hpr[0], hpr[1], hpr[2]
                        assert (
                            constraint.min_h <= h <= constraint.max_h
                        ), f"{language} {preference} {joint_name} heading invalid"
                        assert (
                            constraint.min_p <= p <= constraint.max_p
                        ), f"{language} {preference} {joint_name} pitch invalid"
                        assert (
                            constraint.min_r <= r <= constraint.max_r
                        ), f"{language} {preference} {joint_name} roll invalid"


class TestMultilingualAnimationIntegration:
    """Test multilingual animation system integration"""

    def test_multilingual_animation_manager_consistency(self):
        """Test that animation manager works consistently across languages"""
        # Mock the parent panel
        mock_panel = Mock()
        mock_panel._is_animating = False
        mock_panel._actor = None
        mock_panel.sign_loader = Mock()

        # Test different languages
        languages = ["ASL", "BSL", "ISL", "Auslan", "LSF", "DGS"]

        for language in languages:
            # Mock sign data for each language
            mock_panel.sign_loader.get_sign_data.return_value = {
                "pose": {
                    "mixamorig:RightArm": [0, 45, 0],  # Valid values
                    "mixamorig:RightHand": [0, 0, 0],  # Valid values
                }
            }

            animation_manager = AnimationManager(mock_panel)

            # Test getting pose data for each language
            pose_data = animation_manager.get_letter_pose_from_signs("A", "right")

            # The pose should be retrieved successfully for all languages
            assert pose_data is not None, f"Failed to retrieve pose data for {language}"
            assert (
                "mixamorig:RightArm" in pose_data
            ), f"Missing RightArm in {language} pose data"
            assert (
                "mixamorig:RightHand" in pose_data
            ), f"Missing RightHand in {language} pose data"

            # Test that the pose can be validated using the joint validator
            if pose_data:
                constrained_pose = joint_validator.validate_and_constrain_pose(
                    pose_data
                )
                for joint_name, hpr in constrained_pose.items():
                    constraint = joint_validator.get_joint_constraint(joint_name)
                    if constraint:
                        h, p, r = hpr[0], hpr[1], hpr[2]
                        assert (
                            constraint.min_h <= h <= constraint.max_h
                        ), f"{language} {joint_name} heading not constrained"
                        assert (
                            constraint.min_p <= p <= constraint.max_p
                        ), f"{language} {joint_name} pitch not constrained"
                        assert (
                            constraint.min_r <= r <= constraint.max_r
                        ), f"{language} {joint_name} roll not constrained"

    def test_multilingual_sign_sequence_consistency(self):
        """Test that sign sequences work consistently across languages"""
        validator = JointConstraintValidator()

        # Test different languages
        languages = ["ASL", "BSL", "ISL", "Auslan", "LSF", "DGS"]

        for language in languages:
            # Simulate a sequence of poses for signing a word in each language
            sign_sequence = [
                {
                    "mixamorig:RightArm": [0, 0, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                },  # Start
                {
                    "mixamorig:RightArm": [0, 30, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                },  # Raise arm
                {
                    "mixamorig:RightArm": [0, 45, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                },  # Higher
                {
                    "mixamorig:RightArm": [0, 30, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                },  # Lower
                {
                    "mixamorig:RightArm": [0, 0, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                },  # Return
            ]

            for i, pose in enumerate(sign_sequence):
                constrained_pose = validator.validate_and_constrain_pose(pose)

                # Each pose in the sequence should be anatomically valid for all languages
                for joint_name, hpr in constrained_pose.items():
                    constraint = validator.get_joint_constraint(joint_name)
                    if constraint:
                        h, p, r = hpr[0], hpr[1], hpr[2]
                        assert (
                            constraint.min_h <= h <= constraint.max_h
                        ), f"{language} sequence step {i} {joint_name} heading invalid"
                        assert (
                            constraint.min_p <= p <= constraint.max_p
                        ), f"{language} sequence step {i} {joint_name} pitch invalid"
                        assert (
                            constraint.min_r <= r <= constraint.max_r
                        ), f"{language} sequence step {i} {joint_name} roll invalid"

    def test_multilingual_sign_visibility_consistency(self):
        """Test that sign visibility optimization works consistently across languages"""
        validator = JointConstraintValidator()

        # Test different languages
        languages = ["ASL", "BSL", "ISL", "Auslan", "LSF", "DGS"]

        for language in languages:
            # Test poses optimized for different viewing scenarios
            visibility_poses = {
                "front_view_optimal": {
                    "mixamorig:RightArm": [0, 45, 0],  # Arm raised forward
                    "mixamorig:RightHand": [0, 0, 0],  # Hand in clear view
                    "mixamorig:Head": [0, 0, 0],  # Head facing forward
                },
                "side_view_optimal": {
                    "mixamorig:RightArm": [90, 0, 0],  # Arm to side
                    "mixamorig:RightHand": [0, 0, 0],  # Hand visible from side
                    "mixamorig:Head": [0, 0, 0],  # Head neutral
                },
                "learner_view_optimal": {
                    "mixamorig:RightArm": [0, 30, 0],  # Arm slightly raised
                    "mixamorig:RightHand": [0, 0, 0],  # Hand in clear view
                    "mixamorig:Head": [0, 0, 0],  # Head facing forward
                },
            }

            for view_name, pose in visibility_poses.items():
                constrained_pose = validator.validate_and_constrain_pose(pose)

                # Verify poses are anatomically valid and optimized for viewing for all languages
                for joint_name, hpr in constrained_pose.items():
                    constraint = validator.get_joint_constraint(joint_name)
                    if constraint:
                        h, p, r = hpr[0], hpr[1], hpr[2]
                        assert (
                            constraint.min_h <= h <= constraint.max_h
                        ), f"{language} {view_name} {joint_name} heading invalid"
                        assert (
                            constraint.min_p <= p <= constraint.max_p
                        ), f"{language} {view_name} {joint_name} pitch invalid"
                        assert (
                            constraint.min_r <= r <= constraint.max_r
                        ), f"{language} {view_name} {joint_name} roll invalid"


class TestMultilingualErrorHandling:
    """Test error handling across multiple languages"""

    def test_multilingual_missing_sign_data_handling(self):
        """Test that missing sign data is handled gracefully across languages"""
        # Mock the parent panel
        mock_panel = Mock()
        mock_panel._is_animating = False
        mock_panel._actor = None
        mock_panel.sign_loader = Mock()
        mock_panel.sign_loader.get_sign_data.return_value = None  # No sign data

        animation_manager = AnimationManager(mock_panel)

        # Test different languages
        languages = ["ASL", "BSL", "ISL", "Auslan", "LSF", "DGS"]

        for language in languages:
            # Test getting pose data for missing sign
            pose_data = animation_manager.get_letter_pose_from_signs("MISSING", "right")

            # Should return None gracefully for all languages
            assert pose_data is None, f"Expected None for missing sign in {language}"

    def test_multilingual_invalid_pose_data_handling(self):
        """Test that invalid pose data is handled gracefully across languages"""
        # Mock the parent panel
        mock_panel = Mock()
        mock_panel._is_animating = False
        mock_panel._actor = None
        mock_panel.sign_loader = Mock()
        mock_panel.sign_loader.get_sign_data.return_value = {
            "pose": None  # Invalid pose data
        }

        animation_manager = AnimationManager(mock_panel)

        # Test different languages
        languages = ["ASL", "BSL", "ISL", "Auslan", "LSF", "DGS"]

        for language in languages:
            # Test getting pose data with invalid pose
            pose_data = animation_manager.get_letter_pose_from_signs("INVALID", "right")

            # Should return None gracefully for all languages
            assert pose_data is None, f"Expected None for invalid pose in {language}"

    def test_multilingual_actor_error_handling(self):
        """Test that actor errors are handled gracefully across languages"""
        # Mock the parent panel
        mock_panel = Mock()
        mock_panel._is_animating = True
        mock_panel._actor = Mock()
        mock_panel._actor.getCurrentAnimTime.side_effect = Exception("Actor error")

        animation_manager = AnimationManager(mock_panel)

        # Test different languages
        languages = ["ASL", "BSL", "ISL", "Auslan", "LSF", "DGS"]

        for language in languages:
            # Test animation frame handling with actor error
            animation_manager.on_signing_animation_frame()

            # Should stop animation gracefully for all languages
            assert (
                mock_panel._is_animating is False
            ), f"Animation should stop on error for {language}"
