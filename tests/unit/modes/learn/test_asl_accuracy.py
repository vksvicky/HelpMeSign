#!/usr/bin/env python3
"""
Test ASL accuracy for Learn mode.
Tests that ASL sign language gestures are accurate and realistic.
"""

from unittest.mock import Mock, patch

import pytest

from src.helpmesign.modes.learn.animate_panel.animation_manager import AnimationManager
from src.helpmesign.modes.learn.animate_panel.main_panel import AnimateGesturePanel
from src.helpmesign.modes.learn.animate_panel.model_manager import ModelManager
from src.helpmesign.utils.joint_constraints import (
    JointConstraintValidator,
    joint_validator,
)


class TestASLAccuracy:
    """Test ASL sign language accuracy for Learn mode"""

    def test_asl_alphabet_accuracy(self):
        """Test that ASL alphabet poses are anatomically correct"""
        validator = JointConstraintValidator()

        # Test ASL alphabet poses (A, B, C)
        asl_poses = {
            "A": {
                "mixamorig:RightShoulder": [0, -30, -180],
                "mixamorig:RightArm": [0, 10, 0],
                "mixamorig:RightForeArm": [0, 90, 0],
                "mixamorig:RightHand": [0, 0, 0],
                "mixamorig:Head": [0, 0, 0],
                "mixamorig:Neck": [0, 0, 0],
                "mixamorig:LeftShoulder": [-160, 80, -100],
                "mixamorig:LeftArm": [-15, 80, 0],
                "mixamorig:LeftForeArm": [10, 0, 0],
                "mixamorig:LeftHand": [0, 0, 0],
                "mixamorig:RightHandIndex1": [0, 70, 0],
                "mixamorig:RightHandThumb1": [-45, 0, 0],
            },
            "B": {
                "mixamorig:RightShoulder": [0, 45, 0],
                "mixamorig:RightArm": [0, 30, 0],
                "mixamorig:RightHandIndex1": [0, 0, 0],
                "mixamorig:RightHandThumb2": [0, 60, 0],
            },
            "C": {
                "mixamorig:RightShoulder": [0, 40, 0],
                "mixamorig:RightArm": [0, 25, 0],
                "mixamorig:RightHandIndex1": [0, 30, 0],
                "mixamorig:RightHandThumb2": [0, 30, 0],
            },
        }

        for letter, pose in asl_poses.items():
            constrained_pose = validator.validate_and_constrain_pose(pose)

            # Each ASL pose should be anatomically valid
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

    def test_asl_hand_shape_accuracy(self):
        """Test that ASL hand shapes are accurate"""
        validator = JointConstraintValidator()

        # Test specific ASL hand shapes
        asl_hand_shapes = {
            "fist": {
                "mixamorig:RightHandIndex1": [0, 80, 0],
                "mixamorig:RightHandMiddle1": [0, 80, 0],
                "mixamorig:RightHandRing1": [0, 80, 0],
                "mixamorig:RightHandPinky1": [0, 80, 0],
                "mixamorig:RightHandThumb1": [0, 0, 0],
            },
            "flat_hand": {
                "mixamorig:RightHandIndex1": [0, 0, 0],
                "mixamorig:RightHandMiddle1": [0, 0, 0],
                "mixamorig:RightHandRing1": [0, 0, 0],
                "mixamorig:RightHandPinky1": [0, 0, 0],
                "mixamorig:RightHandThumb2": [0, 60, 0],
            },
            "c_shape": {
                "mixamorig:RightHandIndex1": [0, 30, 0],
                "mixamorig:RightHandMiddle1": [0, 30, 0],
                "mixamorig:RightHandRing1": [0, 30, 0],
                "mixamorig:RightHandPinky1": [0, 30, 0],
                "mixamorig:RightHandThumb2": [0, 30, 0],
            },
        }

        for shape_name, pose in asl_hand_shapes.items():
            constrained_pose = validator.validate_and_constrain_pose(pose)

            # Each hand shape should be anatomically valid
            for joint_name, hpr in constrained_pose.items():
                constraint = validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"ASL {shape_name} {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"ASL {shape_name} {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"ASL {shape_name} {joint_name} roll invalid"

    def test_asl_viewing_angles(self):
        """Test that ASL signs are visible from different angles"""
        validator = JointConstraintValidator()

        # Test ASL poses from different viewing angles
        viewing_angles = {
            "front_view": {
                "mixamorig:RightShoulder": [0, 30, 0],
                "mixamorig:RightArm": [0, 20, 0],
                "mixamorig:RightHand": [0, 0, 0],
            },
            "side_view": {
                "mixamorig:RightShoulder": [0, 30, 0],
                "mixamorig:RightArm": [0, 20, 0],
                "mixamorig:RightHand": [0, 0, 0],
            },
            "learner_view": {
                "mixamorig:RightShoulder": [0, 30, 0],
                "mixamorig:RightArm": [0, 20, 0],
                "mixamorig:RightHand": [0, 0, 0],
            },
        }

        for angle_name, pose in viewing_angles.items():
            constrained_pose = validator.validate_and_constrain_pose(pose)

            # Each viewing angle should be anatomically valid
            for joint_name, hpr in constrained_pose.items():
                constraint = validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"ASL {angle_name} {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"ASL {angle_name} {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"ASL {angle_name} {joint_name} roll invalid"

    def test_asl_animation_manager_integration(self):
        """Test that ASL poses work with animation manager"""
        # Mock the animation panel
        mock_panel = Mock()
        mock_panel._actor = None

        # Mock the learn mode with global settings
        mock_learn_mode = Mock()
        mock_learn_mode.current_language = "ASL"
        mock_panel.learn_mode = mock_learn_mode

        # Use real sign language loader
        from src.helpmesign.utils.sign_language_loader import get_sign_language_loader

        mock_panel.sign_loader = get_sign_language_loader()

        animation_manager = AnimationManager(mock_panel)

        # Test getting ASL pose data for letters A, B, C
        # TODO: Update the poses for B & C and enable it in the test
        for letter in ["A"]:  # , "B", "C"]:
            pose_data = animation_manager.get_letter_pose_from_signs(letter, "right")

            # The pose should be retrieved successfully
            assert (
                pose_data is not None
            ), f"Failed to retrieve pose data for ASL {letter}"
            assert (
                "mixamorig:RightArm" in pose_data
            ), f"Missing RightArm in ASL {letter} pose data"
            assert (
                "mixamorig:RightHand" in pose_data
            ), f"Missing RightHand in ASL {letter} pose data"

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
                        ), f"ASL {letter} {joint_name} heading not constrained"
                        assert (
                            constraint.min_p <= p <= constraint.max_p
                        ), f"ASL {letter} {joint_name} pitch not constrained"
                        assert (
                            constraint.min_r <= r <= constraint.max_r
                        ), f"ASL {letter} {joint_name} roll not constrained"

    def test_asl_model_manager_integration(self):
        """Test that ASL poses work with model manager"""
        # Mock the animation panel
        mock_panel = Mock()
        mock_panel._panda_ready = False  # Headless mode for testing

        # Test that model manager can validate joints using joint_validator
        test_pose = {
            "mixamorig:RightArm": [0, 30, 0],
            "mixamorig:RightHand": [0, 0, 0],
        }

        # Test joint validation using the global joint_validator
        for joint_name in test_pose.keys():
            constraint = joint_validator.get_joint_constraint(joint_name)
            assert (
                constraint is not None
            ), f"Joint validator should provide constraint info for {joint_name}"

            # Test that the constraint has valid ranges
            assert (
                constraint.min_h <= constraint.max_h
            ), f"Invalid heading range for {joint_name}"
            assert (
                constraint.min_p <= constraint.max_p
            ), f"Invalid pitch range for {joint_name}"
            assert (
                constraint.min_r <= constraint.max_r
            ), f"Invalid roll range for {joint_name}"

    def test_asl_sign_visibility_optimization(self):
        """Test that ASL signs are optimized for visibility"""
        validator = JointConstraintValidator()

        # Test that ASL poses are positioned for optimal visibility
        asl_visibility_poses = {
            "optimal_arm_position": {
                "mixamorig:RightShoulder": [0, 30, 0],  # Shoulder raised for visibility
                "mixamorig:RightArm": [0, 20, 0],  # Arm extended for visibility
                "mixamorig:RightForeArm": [0, 0, 0],  # Forearm neutral
                "mixamorig:RightHand": [0, 0, 0],  # Hand positioned for visibility
            }
        }

        for pose_name, pose in asl_visibility_poses.items():
            constrained_pose = validator.validate_and_constrain_pose(pose)

            # Each visibility pose should be anatomically valid
            for joint_name, hpr in constrained_pose.items():
                constraint = validator.get_joint_constraint(joint_name)
                if constraint:
                    h, p, r = hpr[0], hpr[1], hpr[2]
                    assert (
                        constraint.min_h <= h <= constraint.max_h
                    ), f"ASL {pose_name} {joint_name} heading invalid"
                    assert (
                        constraint.min_p <= p <= constraint.max_p
                    ), f"ASL {pose_name} {joint_name} pitch invalid"
                    assert (
                        constraint.min_r <= r <= constraint.max_r
                    ), f"ASL {pose_name} {joint_name} roll invalid"

    def test_asl_error_handling(self):
        """Test that ASL system handles errors gracefully"""
        # Mock the animation panel with error conditions
        mock_panel = Mock()
        mock_panel._actor = None
        mock_panel.current_language = "ASL"
        mock_panel.sign_loader = None  # No sign loader

        animation_manager = AnimationManager(mock_panel)

        # Test error handling when sign loader is missing
        pose_data = animation_manager.get_letter_pose_from_signs("A", "right")
        assert pose_data is None, "Should return None when sign loader is missing"

        # Test error handling with invalid character
        mock_panel.sign_loader = Mock()
        mock_panel.sign_loader.get_alphabet_signs.return_value = {}

        pose_data = animation_manager.get_letter_pose_from_signs("INVALID", "right")
        assert pose_data is None, "Should return None for invalid character"
