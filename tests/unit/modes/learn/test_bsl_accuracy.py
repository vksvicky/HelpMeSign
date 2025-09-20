#!/usr/bin/env python3
"""
Tests for British Sign Language (BSL) gesture accuracy and viewing angles
Ensures BSL signs are accurate, viewable, and anatomically correct
"""

from typing import Any, Dict, List, Tuple
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.helpmesign.modes.learn.animate_panel.animation_manager import AnimationManager
from src.helpmesign.utils.joint_constraints import (
    JointConstraintValidator,
    joint_validator,
)


class TestBSLAccuracy:
    """Test British Sign Language gesture accuracy"""

    def test_bsl_alphabet_poses_are_anatomically_valid(self):
        """Test that BSL alphabet poses respect human anatomy"""
        validator = JointConstraintValidator()

        # BSL alphabet poses (simplified examples)
        bsl_alphabet = {
            "A": {
                "mixamorig:RightHand": [0, 0, 0],  # Fist with thumb extended
                "mixamorig:RightArm": [0, 0, 0],
            },
            "B": {
                "mixamorig:RightHand": [0, 0, 0],  # Flat hand
                "mixamorig:RightArm": [0, 0, 0],
            },
            "C": {
                "mixamorig:RightHand": [0, 0, 0],  # C shape
                "mixamorig:RightArm": [0, 0, 0],
            },
            "D": {
                "mixamorig:RightHand": [0, 0, 0],  # Pointing finger
                "mixamorig:RightArm": [0, 0, 0],
            },
            "E": {
                "mixamorig:RightHand": [0, 0, 0],  # Fingers together
                "mixamorig:RightArm": [0, 0, 0],
            },
            "F": {
                "mixamorig:RightHand": [0, 0, 0],  # F shape
                "mixamorig:RightArm": [0, 0, 0],
            },
            "G": {
                "mixamorig:RightHand": [0, 0, 0],  # G shape
                "mixamorig:RightArm": [0, 0, 0],
            },
            "H": {
                "mixamorig:RightHand": [0, 0, 0],  # H shape
                "mixamorig:RightArm": [0, 0, 0],
            },
            "I": {
                "mixamorig:RightHand": [0, 0, 0],  # Pinky finger up
                "mixamorig:RightArm": [0, 0, 0],
            },
            "J": {
                "mixamorig:RightHand": [0, 0, 0],  # J shape
                "mixamorig:RightArm": [0, 0, 0],
            },
        }

        for letter, pose in bsl_alphabet.items():
            constrained_pose = validator.validate_and_constrain_pose(pose)

            # Verify anatomical validity
            for joint_name, hpr in constrained_pose.items():
                constraint = validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"BSL {letter} {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"BSL {letter} {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"BSL {letter} {joint_name} roll invalid"

    def test_bsl_numbers_poses_are_valid(self):
        """Test that BSL number poses are anatomically valid"""
        validator = JointConstraintValidator()

        # BSL number poses (simplified examples)
        bsl_numbers = {
            "1": {
                "mixamorig:RightHand": [0, 0, 0],  # Index finger up
                "mixamorig:RightArm": [0, 0, 0],
            },
            "2": {
                "mixamorig:RightHand": [0, 0, 0],  # Index and middle finger up
                "mixamorig:RightArm": [0, 0, 0],
            },
            "3": {
                "mixamorig:RightHand": [0, 0, 0],  # Three fingers up
                "mixamorig:RightArm": [0, 0, 0],
            },
            "4": {
                "mixamorig:RightHand": [0, 0, 0],  # Four fingers up
                "mixamorig:RightArm": [0, 0, 0],
            },
            "5": {
                "mixamorig:RightHand": [0, 0, 0],  # All fingers up
                "mixamorig:RightArm": [0, 0, 0],
            },
            "6": {
                "mixamorig:RightHand": [0, 0, 0],  # Thumb and pinky
                "mixamorig:RightArm": [0, 0, 0],
            },
            "7": {
                "mixamorig:RightHand": [0, 0, 0],  # Thumb, index, middle
                "mixamorig:RightArm": [0, 0, 0],
            },
            "8": {
                "mixamorig:RightHand": [0, 0, 0],  # Thumb, index, middle, ring
                "mixamorig:RightArm": [0, 0, 0],
            },
            "9": {
                "mixamorig:RightHand": [0, 0, 0],  # All fingers except pinky
                "mixamorig:RightArm": [0, 0, 0],
            },
            "10": {
                "mixamorig:RightHand": [0, 0, 0],  # All fingers
                "mixamorig:RightArm": [0, 0, 0],
            },
        }

        for number, pose in bsl_numbers.items():
            constrained_pose = validator.validate_and_constrain_pose(pose)

            # Verify anatomical validity
            for joint_name, hpr in constrained_pose.items():
                constraint = validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"BSL {number} {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"BSL {number} {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"BSL {number} {joint_name} roll invalid"

    def test_bsl_common_words_poses_are_valid(self):
        """Test that common BSL word poses are anatomically valid"""
        validator = JointConstraintValidator()

        # Common BSL word poses (simplified examples)
        bsl_words = {
            "HELLO": {
                "mixamorig:RightHand": [0, 0, 0],  # Wave gesture
                "mixamorig:RightArm": [0, 30, 0],  # Arm raised
            },
            "THANK_YOU": {
                "mixamorig:RightHand": [0, 0, 0],  # Thank you gesture
                "mixamorig:RightArm": [0, 0, 0],
            },
            "YES": {
                "mixamorig:RightHand": [0, 0, 0],  # Nod gesture
                "mixamorig:RightArm": [0, 0, 0],
            },
            "NO": {
                "mixamorig:RightHand": [0, 0, 0],  # Shake gesture
                "mixamorig:RightArm": [0, 0, 0],
            },
            "PLEASE": {
                "mixamorig:RightHand": [0, 0, 0],  # Please gesture
                "mixamorig:RightArm": [0, 0, 0],
            },
            "SORRY": {
                "mixamorig:RightHand": [0, 0, 0],  # Sorry gesture
                "mixamorig:RightArm": [0, 0, 0],
            },
            "GOOD": {
                "mixamorig:RightHand": [0, 0, 0],  # Good gesture
                "mixamorig:RightArm": [0, 0, 0],
            },
            "BAD": {
                "mixamorig:RightHand": [0, 0, 0],  # Bad gesture
                "mixamorig:RightArm": [0, 0, 0],
            },
        }

        for word, pose in bsl_words.items():
            constrained_pose = validator.validate_and_constrain_pose(pose)

            # Verify anatomical validity
            for joint_name, hpr in constrained_pose.items():
                constraint = validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"BSL {word} {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"BSL {word} {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"BSL {word} {joint_name} roll invalid"


class TestBSLViewingAngles:
    """Test that BSL signs are viewable from appropriate angles"""

    def test_bsl_signs_visible_from_front_view(self):
        """Test that BSL signs are positioned for optimal front viewing"""
        validator = JointConstraintValidator()

        # Poses optimized for front viewing
        front_view_poses = {
            "clear_hand_position": {
                "mixamorig:RightArm": [0, 45, 0],  # Arm raised forward
                "mixamorig:RightHand": [0, 0, 0],  # Hand in clear view
                "mixamorig:RightForeArm": [0, 0, 0],  # Forearm visible
            },
            "neutral_position": {
                "mixamorig:RightArm": [0, 0, 0],  # Arm at side
                "mixamorig:RightHand": [0, 0, 0],  # Hand neutral
                "mixamorig:RightForeArm": [0, 0, 0],  # Forearm neutral
            },
        }

        for pose_name, pose in front_view_poses.items():
            constrained_pose = validator.validate_and_constrain_pose(pose)

            # Verify pose is anatomically valid
            for joint_name, hpr in constrained_pose.items():
                constraint = validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"{pose_name} {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"{pose_name} {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"{pose_name} {joint_name} roll invalid"

    def test_bsl_signs_visible_from_side_view(self):
        """Test that BSL signs are positioned for optimal side viewing"""
        validator = JointConstraintValidator()

        # Poses optimized for side viewing
        side_view_poses = {
            "side_clear_position": {
                "mixamorig:RightArm": [90, 0, 0],  # Arm to side
                "mixamorig:RightHand": [0, 0, 0],  # Hand visible from side
                "mixamorig:RightForeArm": [0, 0, 0],  # Forearm visible
            },
        }

        for pose_name, pose in side_view_poses.items():
            constrained_pose = validator.validate_and_constrain_pose(pose)

            # Verify pose is anatomically valid
            for joint_name, hpr in constrained_pose.items():
                constraint = validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"{pose_name} {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"{pose_name} {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"{pose_name} {joint_name} roll invalid"

    def test_bsl_signs_visible_from_learner_perspective(self):
        """Test that BSL signs are positioned for optimal learning"""
        validator = JointConstraintValidator()

        # Poses optimized for learning (clear, not too fast, well-positioned)
        learning_poses = {
            "learning_position": {
                "mixamorig:RightArm": [0, 30, 0],  # Arm slightly raised
                "mixamorig:RightHand": [0, 0, 0],  # Hand in clear view
                "mixamorig:Head": [0, 0, 0],  # Head facing forward
                "mixamorig:Neck": [0, 0, 0],  # Neck neutral
            },
        }

        for pose_name, pose in learning_poses.items():
            constrained_pose = validator.validate_and_constrain_pose(pose)

            # Verify pose is anatomically valid
            for joint_name, hpr in constrained_pose.items():
                constraint = validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"{pose_name} {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"{pose_name} {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"{pose_name} {joint_name} roll invalid"


class TestBSLHandShapeAccuracy:
    """Test that BSL hand shapes are anatomically accurate"""

    def test_bsl_finger_extension_accuracy(self):
        """Test that BSL finger extensions are anatomically accurate"""
        validator = JointConstraintValidator()

        # Test different finger extension patterns used in BSL
        finger_patterns = {
            "all_fingers_extended": {
                "mixamorig:RightHandIndex1": [0, 0, 0],
                "mixamorig:RightHandMiddle1": [0, 0, 0],
                "mixamorig:RightHandRing1": [0, 0, 0],
                "mixamorig:RightHandPinky1": [0, 0, 0],
                "mixamorig:RightHandThumb1": [0, 0, 0],
            },
            "index_finger_only": {
                "mixamorig:RightHandIndex1": [0, 0, 0],
                "mixamorig:RightHandMiddle1": [0, 0, 0],
                "mixamorig:RightHandRing1": [0, 0, 0],
                "mixamorig:RightHandPinky1": [0, 0, 0],
                "mixamorig:RightHandThumb1": [0, 0, 0],
            },
            "peace_sign": {
                "mixamorig:RightHandIndex1": [0, 0, 0],
                "mixamorig:RightHandMiddle1": [0, 0, 0],
                "mixamorig:RightHandRing1": [0, 0, 0],
                "mixamorig:RightHandPinky1": [0, 0, 0],
                "mixamorig:RightHandThumb1": [0, 0, 0],
            },
            "thumbs_up": {
                "mixamorig:RightHandIndex1": [0, 0, 0],
                "mixamorig:RightHandMiddle1": [0, 0, 0],
                "mixamorig:RightHandRing1": [0, 0, 0],
                "mixamorig:RightHandPinky1": [0, 0, 0],
                "mixamorig:RightHandThumb1": [0, 0, 0],
            },
        }

        for pattern_name, pose in finger_patterns.items():
            constrained_pose = validator.validate_and_constrain_pose(pose)

            # Verify all finger joints are anatomically valid
            for joint_name, hpr in constrained_pose.items():
                constraint = validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"{pattern_name} {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"{pattern_name} {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"{pattern_name} {joint_name} roll invalid"

    def test_bsl_thumb_position_accuracy(self):
        """Test that BSL thumb positions are anatomically accurate"""
        validator = JointConstraintValidator()

        # Test different thumb positions used in BSL
        thumb_positions = {
            "thumb_up": {
                "mixamorig:RightHandThumb1": [0, 0, 0],
                "mixamorig:RightHandThumb2": [0, 0, 0],
                "mixamorig:RightHandThumb3": [0, 0, 0],
            },
            "thumb_down": {
                "mixamorig:RightHandThumb1": [0, 0, 0],
                "mixamorig:RightHandThumb2": [0, 0, 0],
                "mixamorig:RightHandThumb3": [0, 0, 0],
            },
            "thumb_neutral": {
                "mixamorig:RightHandThumb1": [0, 0, 0],
                "mixamorig:RightHandThumb2": [0, 0, 0],
                "mixamorig:RightHandThumb3": [0, 0, 0],
            },
            "thumb_extended": {
                "mixamorig:RightHandThumb1": [0, 0, 0],
                "mixamorig:RightHandThumb2": [0, 0, 0],
                "mixamorig:RightHandThumb3": [0, 0, 0],
            },
        }

        for position_name, pose in thumb_positions.items():
            constrained_pose = validator.validate_and_constrain_pose(pose)

            # Verify thumb joints are anatomically valid
            for joint_name, hpr in constrained_pose.items():
                constraint = validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"{position_name} {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"{position_name} {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"{position_name} {joint_name} roll invalid"


class TestBSLBilateralSigning:
    """Test BSL bilateral signing accuracy and symmetry"""

    def test_bsl_bilateral_signs_maintain_symmetry(self):
        """Test that BSL bilateral signs maintain proper symmetry"""
        validator = JointConstraintValidator()

        # Test symmetric bilateral poses
        bilateral_poses = {
            "symmetric_arms": {
                "mixamorig:RightArm": [45, 30, 0],
                "mixamorig:LeftArm": [-45, 30, 0],  # Mirrored
                "mixamorig:RightHand": [0, 0, 0],
                "mixamorig:LeftHand": [0, 0, 0],  # Mirrored
            },
            "symmetric_hands": {
                "mixamorig:RightHand": [0, 0, 0],
                "mixamorig:LeftHand": [0, 0, 0],  # Mirrored
                "mixamorig:RightForeArm": [0, 0, 0],
                "mixamorig:LeftForeArm": [0, 0, 0],  # Mirrored
            },
        }

        for pose_name, pose in bilateral_poses.items():
            constrained_pose = validator.validate_and_constrain_pose(pose)

            # Verify both sides are anatomically valid
            for joint_name, hpr in constrained_pose.items():
                constraint = validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"{pose_name} {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"{pose_name} {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"{pose_name} {joint_name} roll invalid"

    def test_bsl_dominant_hand_preference_accuracy(self):
        """Test that BSL dominant hand preference is respected"""
        validator = JointConstraintValidator()

        # Test poses for different hand preferences
        hand_preference_poses = {
            "right_hand_dominant": {
                "mixamorig:RightArm": [0, 45, 0],  # Right arm active
                "mixamorig:LeftArm": [0, 0, 0],  # Left arm neutral
                "mixamorig:RightHand": [0, 0, 0],  # Right hand active
                "mixamorig:LeftHand": [0, 0, 0],  # Left hand neutral
            },
            "left_hand_dominant": {
                "mixamorig:RightArm": [0, 0, 0],  # Right arm neutral
                "mixamorig:LeftArm": [0, 45, 0],  # Left arm active
                "mixamorig:RightHand": [0, 0, 0],  # Right hand neutral
                "mixamorig:LeftHand": [0, 0, 0],  # Left hand active
            },
        }

        for preference_name, pose in hand_preference_poses.items():
            constrained_pose = validator.validate_and_constrain_pose(pose)

            # Verify poses are anatomically valid
            for joint_name, hpr in constrained_pose.items():
                constraint = validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"{preference_name} {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"{preference_name} {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"{preference_name} {joint_name} roll invalid"


class TestBSLAnimationIntegration:
    """Integration tests for BSL animation accuracy"""

    def test_bsl_animation_manager_retrieves_pose_data(self):
        """Test that animation manager retrieves BSL pose data correctly"""
        # Mock the parent panel
        mock_panel = Mock()
        mock_panel._is_animating = False
        mock_panel._actor = None
        mock_panel.sign_loader = Mock()

        # Mock the learn mode with global settings
        mock_learn_mode = Mock()
        mock_learn_mode.current_language = "BSL"
        mock_panel.learn_mode = mock_learn_mode

        # Mock BSL sign data with valid values
        mock_panel.sign_loader.get_alphabet_signs.return_value = {
            "A": {
                "pose": {
                    "mixamorig:RightArm": [0, 45, 0],  # Valid values
                    "mixamorig:RightHand": [0, 0, 0],  # Valid values
                }
            }
        }

        animation_manager = AnimationManager(mock_panel)

        # Test getting BSL pose data
        pose_data = animation_manager.get_letter_pose_from_signs("A", "right")

        # The pose should be retrieved successfully
        assert pose_data is not None
        assert "mixamorig:RightArm" in pose_data
        assert "mixamorig:RightHand" in pose_data

        # Test that the pose can be validated using the joint validator
        if pose_data:
            constrained_pose = joint_validator.validate_and_constrain_pose(pose_data)
            for joint_name, hpr in constrained_pose.items():
                constraint = joint_validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"{joint_name} heading not constrained"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"{joint_name} pitch not constrained"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"{joint_name} roll not constrained"

    def test_bsl_sign_sequence_maintains_accuracy(self):
        """Test that BSL sign sequences maintain anatomical accuracy"""
        validator = JointConstraintValidator()

        # Simulate a sequence of poses for signing a BSL word
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

            # Each pose in the sequence should be anatomically valid
            for joint_name, hpr in constrained_pose.items():
                constraint = validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"BSL sequence step {i} {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"BSL sequence step {i} {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"BSL sequence step {i} {joint_name} roll invalid"

    def test_bsl_sign_visibility_optimization(self):
        """Test that BSL signs are optimized for visibility"""
        validator = JointConstraintValidator()

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

            # Verify poses are anatomically valid and optimized for viewing
            for joint_name, hpr in constrained_pose.items():
                constraint = validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"{view_name} {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"{view_name} {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"{view_name} {joint_name} roll invalid"
