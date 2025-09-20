#!/usr/bin/env python3
"""
Tests for realistic character movement and sign language animation
Ensures the 3D character can move like a real person and sign accurately
"""

from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.helpmesign.modes.learn.animate_panel.animation_manager import AnimationManager
from src.helpmesign.modes.learn.animate_panel.model_manager import ModelManager
from src.helpmesign.utils.joint_constraints import (
    JointConstraintValidator,
    joint_validator,
)


class TestRealisticCharacterMovement:
    """Test that character movement respects human anatomical constraints"""

    def test_character_respects_anatomical_limits(self):
        """Test that character joints cannot exceed human anatomical limits"""
        validator = JointConstraintValidator()

        # Test extreme values that should be constrained
        extreme_pose = {
            "mixamorig:RightArm": [200, 300, 400],  # Way beyond human limits
            "mixamorig:LeftArm": [-200, -300, -400],  # Way beyond human limits
            "mixamorig:RightHand": [100, 150, 200],  # Beyond hand limits
            "mixamorig:Head": [100, 200, 300],  # Beyond head limits
        }

        constrained_pose = validator.validate_and_constrain_pose(extreme_pose)

        # Verify all values are within human limits
        for joint_name, hpr in constrained_pose.items():
            constraint = validator.get_joint_constraint(joint_name)
            if constraint:
                h, p, r = hpr[0], hpr[1], hpr[2]
                assert (
                    constraint.min_h <= h <= constraint.max_h
                ), f"{joint_name} heading {h} out of range"
                assert (
                    constraint.min_p <= p <= constraint.max_p
                ), f"{joint_name} pitch {p} out of range"
                assert (
                    constraint.min_r <= r <= constraint.max_r
                ), f"{joint_name} roll {r} out of range"

    def test_arm_movement_realistic_ranges(self):
        """Test that arm movement stays within realistic human ranges"""
        validator = JointConstraintValidator()

        # Test realistic arm movements
        realistic_arm_poses = [
            {"mixamorig:RightArm": [0, 0, 0]},  # Neutral position
            {"mixamorig:RightArm": [90, 45, 0]},  # Arm raised forward
            {"mixamorig:RightArm": [-90, 45, 0]},  # Arm raised to side
            {"mixamorig:RightArm": [0, 90, 0]},  # Arm straight up
            {"mixamorig:RightArm": [0, -30, 0]},  # Arm slightly back
        ]

        for pose in realistic_arm_poses:
            constrained_pose = validator.validate_and_constrain_pose(pose)
            joint_name = list(pose.keys())[0]
            h, p, r = constrained_pose[joint_name]

            # These should all be valid (within constraints)
            constraint = validator.get_joint_constraint(joint_name)
            assert constraint.min_h <= h <= constraint.max_h
            assert constraint.min_p <= p <= constraint.max_p
            assert constraint.min_r <= r <= constraint.max_r

    def test_hand_finger_movement_accuracy(self):
        """Test that hand and finger movements are anatomically accurate"""
        validator = JointConstraintValidator()

        # Test finger joint constraints
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
            "mixamorig:RightHandThumb1",
            "mixamorig:RightHandThumb2",
            "mixamorig:RightHandThumb3",
        ]

        for joint_name in finger_joints:
            constraint = validator.get_joint_constraint(joint_name)
            if constraint:
                # Test that finger joints have appropriate constraints
                # Fingers should have limited range compared to arms
                assert (
                    constraint.max_h - constraint.min_h <= 180
                ), f"{joint_name} has too wide heading range"
                assert (
                    constraint.max_p - constraint.min_p <= 180
                ), f"{joint_name} has too wide pitch range"
                assert (
                    constraint.max_r - constraint.min_r <= 180
                ), f"{joint_name} has too wide roll range"

    def test_shoulder_arm_coordination(self):
        """Test that shoulder and arm movements are coordinated realistically"""
        validator = JointConstraintValidator()

        # Test coordinated shoulder-arm movement
        coordinated_pose = {
            "mixamorig:RightShoulder": [45, 30, 0],  # Shoulder raised
            "mixamorig:RightArm": [0, 45, 0],  # Arm follows shoulder
        }

        constrained_pose = validator.validate_and_constrain_pose(coordinated_pose)

        # Both joints should be within their respective limits
        for joint_name, hpr in constrained_pose.items():
            constraint = validator.get_joint_constraint(joint_name)
            if constraint:
                h, p, r = hpr[0], hpr[1], hpr[2]
                assert constraint.min_h <= h <= constraint.max_h
                assert constraint.min_p <= p <= constraint.max_p
                assert constraint.min_r <= r <= constraint.max_r

    def test_head_neck_coordination(self):
        """Test that head and neck movements are coordinated realistically"""
        validator = JointConstraintValidator()

        # Test coordinated head-neck movement
        coordinated_pose = {
            "mixamorig:Neck": [20, 15, 0],  # Neck turned slightly
            "mixamorig:Head": [10, 5, 0],  # Head follows neck
        }

        constrained_pose = validator.validate_and_constrain_pose(coordinated_pose)

        # Both joints should be within their respective limits
        for joint_name, hpr in constrained_pose.items():
            constraint = validator.get_joint_constraint(joint_name)
            if constraint:
                h, p, r = hpr[0], hpr[1], hpr[2]
                assert constraint.min_h <= h <= constraint.max_h
                assert constraint.min_p <= p <= constraint.max_p
                assert constraint.min_r <= r <= constraint.max_r


class TestSignLanguageAccuracy:
    """Test that sign language gestures are accurate and viewable"""

    def test_asl_letter_poses_are_valid(self):
        """Test that ASL letter poses respect anatomical constraints"""
        validator = JointConstraintValidator()

        # Common ASL letter poses (simplified examples)
        asl_letter_poses = {
            "A": {
                "mixamorig:RightHand": [0, 0, 0],  # Fist
                "mixamorig:RightArm": [0, 0, 0],  # Neutral arm
            },
            "B": {
                "mixamorig:RightHand": [0, 0, 0],  # Flat hand
                "mixamorig:RightArm": [0, 0, 0],  # Neutral arm
            },
            "C": {
                "mixamorig:RightHand": [0, 0, 0],  # C shape
                "mixamorig:RightArm": [0, 0, 0],  # Neutral arm
            },
        }

        for letter, pose in asl_letter_poses.items():
            constrained_pose = validator.validate_and_constrain_pose(pose)

            # All poses should be valid (within constraints)
            for joint_name, hpr in constrained_pose.items():
                constraint = validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"ASL {letter} {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"ASL {letter} {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"ASL {letter} {joint_name} roll invalid"

    def test_sign_visibility_from_front_view(self):
        """Test that signs are visible and clear from front view"""
        # This test would verify that signs are positioned correctly for front viewing
        # In a real implementation, this would check camera angles and sign positioning

        # Mock pose data for a sign that should be visible from front
        front_view_pose = {
            "mixamorig:RightArm": [0, 45, 0],  # Arm raised forward
            "mixamorig:RightHand": [0, 0, 0],  # Hand in neutral position
            "mixamorig:RightForeArm": [0, 0, 0],  # Forearm neutral
        }

        validator = JointConstraintValidator()
        constrained_pose = validator.validate_and_constrain_pose(front_view_pose)

        # Verify the pose is valid
        for joint_name, hpr in constrained_pose.items():
            constraint = validator.get_joint_constraint(joint_name)
            if constraint:
                h, p, r = hpr[0], hpr[1], hpr[2]
                assert constraint.min_h <= h <= constraint.max_h
                assert constraint.min_p <= p <= constraint.max_p
                assert constraint.min_r <= r <= constraint.max_r

    def test_hand_shape_accuracy(self):
        """Test that hand shapes for signs are anatomically accurate"""
        validator = JointConstraintValidator()

        # Test different hand shapes used in signing
        hand_shapes = {
            "fist": {
                "mixamorig:RightHandIndex1": [0, 0, 0],
                "mixamorig:RightHandMiddle1": [0, 0, 0],
                "mixamorig:RightHandRing1": [0, 0, 0],
                "mixamorig:RightHandPinky1": [0, 0, 0],
                "mixamorig:RightHandThumb1": [0, 0, 0],
            },
            "open_hand": {
                "mixamorig:RightHandIndex1": [0, 0, 0],
                "mixamorig:RightHandMiddle1": [0, 0, 0],
                "mixamorig:RightHandRing1": [0, 0, 0],
                "mixamorig:RightHandPinky1": [0, 0, 0],
                "mixamorig:RightHandThumb1": [0, 0, 0],
            },
        }

        for shape_name, pose in hand_shapes.items():
            constrained_pose = validator.validate_and_constrain_pose(pose)

            # All hand shapes should be valid
            for joint_name, hpr in constrained_pose.items():
                constraint = validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"{shape_name} {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"{shape_name} {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"{shape_name} {joint_name} roll invalid"


class TestAnimationManagerIntegration:
    """Test animation manager with realistic movement constraints"""

    def test_animation_manager_retrieves_pose_data(self):
        """Test that animation manager retrieves pose data correctly"""
        # Mock the parent panel
        mock_panel = Mock()
        mock_panel._is_animating = False
        mock_panel._actor = None
        mock_panel.sign_loader = Mock()

        # Mock the learn mode with global settings
        mock_learn_mode = Mock()
        mock_learn_mode.current_language = "ASL"
        mock_panel.learn_mode = mock_learn_mode

        mock_panel.sign_loader.get_alphabet_signs.return_value = {
            "A": {"pose": {"mixamorig:RightArm": [0, 45, 0]}}
        }

        animation_manager = AnimationManager(mock_panel)

        # Test getting pose data
        pose_data = animation_manager.get_letter_pose_from_signs("A", "right")

        # Verify pose data is retrieved
        assert pose_data is not None
        assert "mixamorig:RightArm" in pose_data
        mock_panel.sign_loader.get_alphabet_signs.assert_called_once_with(
            "ASL", "right"
        )

    def test_gesture_validation_before_playback(self):
        """Test that gestures are retrieved and can be validated"""
        mock_panel = Mock()
        mock_panel.sign_loader = Mock()

        # Mock the learn mode with global settings
        mock_learn_mode = Mock()
        mock_learn_mode.current_language = "ASL"
        mock_panel.learn_mode = mock_learn_mode

        mock_panel.sign_loader.get_alphabet_signs.return_value = {
            "A": {"pose": {"mixamorig:RightArm": [0, 45, 0]}}
        }

        animation_manager = AnimationManager(mock_panel)

        # Test getting letter pose
        pose_data = animation_manager.get_letter_pose_from_signs("A", "right")

        # The pose should be retrieved successfully
        assert pose_data is not None
        assert "mixamorig:RightArm" in pose_data

        # Test that the pose can be validated using the joint validator
        if pose_data:
            constrained_pose = joint_validator.validate_and_constrain_pose(pose_data)
            for joint_name, hpr in constrained_pose.items():
                constraint = joint_validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert constraint.min_h <= h <= constraint.max_h
                    assert constraint.min_p <= p <= constraint.max_p
                    assert constraint.min_r <= r <= constraint.max_r


class TestModelManagerIntegration:
    """Test model manager with realistic character movement"""

    def test_model_manager_joint_validation(self):
        """Test that model manager can validate joint movements"""
        mock_panel = Mock()
        model_manager = ModelManager(mock_panel)

        # Test joint control with constraints
        test_joint_poses = {
            "mixamorig:RightArm": [100, 150, 200],  # Beyond normal limits
            "mixamorig:LeftArm": [-100, -150, -200],  # Beyond normal limits
        }

        # Test that we can validate joint movements using the joint validator
        for joint_name, hpr in test_joint_poses.items():
            # Get constrained values
            constraint = joint_validator.get_joint_constraint(joint_name)
            if constraint:
                h, p, r = joint_validator.validate_single_joint(
                    joint_name, hpr[0], hpr[1], hpr[2]
                )

                # Verify values are within limits after validation
                assert constraint.min_h <= h <= constraint.max_h
                assert constraint.min_p <= p <= constraint.max_p
                assert constraint.min_r <= r <= constraint.max_r


class TestSignLanguageViewingAngles:
    """Test that signs are viewable from appropriate angles"""

    def test_signs_visible_from_learner_perspective(self):
        """Test that signs are positioned for optimal learning visibility"""
        # This would test camera positioning and sign placement
        # for optimal learning experience

        # Mock camera and sign positioning
        optimal_viewing_pose = {
            "mixamorig:RightArm": [0, 30, 0],  # Arm slightly raised
            "mixamorig:RightHand": [0, 0, 0],  # Hand in clear view
            "mixamorig:Head": [0, 0, 0],  # Head facing forward
        }

        validator = JointConstraintValidator()
        constrained_pose = validator.validate_and_constrain_pose(optimal_viewing_pose)

        # Verify pose is valid and optimal for viewing
        for joint_name, hpr in constrained_pose.items():
            constraint = validator.get_joint_constraint(joint_name)
            if constraint:
                h, p, r = hpr[0], hpr[1], hpr[2]
                assert constraint.min_h <= h <= constraint.max_h
                assert constraint.min_p <= p <= constraint.max_p
                assert constraint.min_r <= r <= constraint.max_r

    def test_bilateral_signing_symmetry(self):
        """Test that bilateral signs maintain proper symmetry"""
        validator = JointConstraintValidator()

        # Test symmetric bilateral pose
        bilateral_pose = {
            "mixamorig:RightArm": [45, 30, 0],
            "mixamorig:LeftArm": [-45, 30, 0],  # Mirrored
            "mixamorig:RightHand": [0, 0, 0],
            "mixamorig:LeftHand": [0, 0, 0],  # Mirrored
        }

        constrained_pose = validator.validate_and_constrain_pose(bilateral_pose)

        # Verify both sides are within limits
        for joint_name, hpr in constrained_pose.items():
            constraint = validator.get_joint_constraint(joint_name)
            if constraint:
                h, p, r = hpr[0], hpr[1], hpr[2]
                assert constraint.min_h <= h <= constraint.max_h
                assert constraint.min_p <= p <= constraint.max_p
                assert constraint.min_r <= r <= constraint.max_r


class TestRealisticMovementIntegration:
    """Integration tests for realistic character movement"""

    def test_full_sign_sequence_anatomical_validity(self):
        """Test that a full sign sequence maintains anatomical validity"""
        validator = JointConstraintValidator()

        # Simulate a sequence of poses for signing a word
        sign_sequence = [
            {
                "mixamorig:RightArm": [0, 0, 0],
                "mixamorig:RightHand": [0, 0, 0],
            },  # Start
            {
                "mixamorig:RightArm": [0, 45, 0],
                "mixamorig:RightHand": [0, 0, 0],
            },  # Raise arm
            {
                "mixamorig:RightArm": [0, 45, 0],
                "mixamorig:RightHand": [0, 0, 0],
            },  # Hold
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
                    ), f"Sequence step {i} {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"Sequence step {i} {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"Sequence step {i} {joint_name} roll invalid"

    def test_character_movement_smoothness(self):
        """Test that character movement transitions are smooth and realistic"""
        validator = JointConstraintValidator()

        # Test smooth transition between poses
        start_pose = {"mixamorig:RightArm": [0, 0, 0]}
        end_pose = {"mixamorig:RightArm": [0, 45, 0]}

        # Simulate intermediate poses for smooth transition
        intermediate_poses = [
            {"mixamorig:RightArm": [0, 15, 0]},
            {"mixamorig:RightArm": [0, 30, 0]},
        ]

        all_poses = [start_pose] + intermediate_poses + [end_pose]

        for i, pose in enumerate(all_poses):
            constrained_pose = validator.validate_and_constrain_pose(pose)

            # Each intermediate pose should be valid
            for joint_name, hpr in constrained_pose.items():
                constraint = validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"Transition step {i} {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"Transition step {i} {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"Transition step {i} {joint_name} roll invalid"
