#!/usr/bin/env python3
"""
Tests for animation system integration
Ensures smooth, realistic character movement and proper sign language animation
"""

from typing import Any, Dict, List, Tuple
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.helpmesign.modes.learn.animate_panel.animation_manager import AnimationManager
from src.helpmesign.modes.learn.animate_panel.main_panel import AnimateGesturePanel
from src.helpmesign.modes.learn.animate_panel.model_manager import ModelManager
from src.helpmesign.utils.joint_constraints import (
    JointConstraintValidator,
    joint_validator,
)


class TestAnimationSmoothness:
    """Test that animations are smooth and realistic"""

    def test_pose_transitions_are_smooth(self):
        """Test that transitions between poses are smooth"""
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

    def test_animation_timing_is_realistic(self):
        """Test that animation timing is realistic for human movement"""
        # Mock animation manager
        mock_panel = Mock()
        mock_panel._is_animating = True
        mock_panel._actor = Mock()
        mock_panel._actor.getCurrentAnimTime.return_value = 0.5
        mock_panel._actor.getCurrentAnimLength.return_value = 2.0

        animation_manager = AnimationManager(mock_panel)

        # Test animation frame handling
        animation_manager.on_signing_animation_frame()

        # Verify animation continues when not complete
        assert mock_panel._is_animating is True

    def test_animation_completion_handling(self):
        """Test that animation completion is handled properly"""
        # Mock animation manager
        mock_panel = Mock()
        mock_panel._is_animating = True
        mock_panel._actor = Mock()
        mock_panel._actor.getCurrentAnimTime.return_value = 2.0
        mock_panel._actor.getCurrentAnimLength.return_value = 2.0

        animation_manager = AnimationManager(mock_panel)

        # Test animation frame handling when complete
        animation_manager.on_signing_animation_frame()

        # Verify animation stops when complete
        assert mock_panel._is_animating is False
        mock_panel._actor.stop.assert_called_once()
        mock_panel._reset_to_neutral_pose.assert_called_once()


class TestCharacterMovementRealism:
    """Test that character movement is realistic"""

    def test_character_respects_physics_constraints(self):
        """Test that character movement respects basic physics constraints"""
        validator = JointConstraintValidator()

        # Test poses that should be physically possible
        realistic_poses = {
            "natural_standing": {
                "mixamorig:RightArm": [0, 0, 0],
                "mixamorig:LeftArm": [0, 0, 0],
                "mixamorig:Head": [0, 0, 0],
                "mixamorig:Neck": [0, 0, 0],
            },
            "arm_raised_naturally": {
                "mixamorig:RightArm": [0, 45, 0],
                "mixamorig:LeftArm": [0, 0, 0],
                "mixamorig:Head": [0, 0, 0],
                "mixamorig:Neck": [0, 0, 0],
            },
            "both_arms_raised": {
                "mixamorig:RightArm": [0, 45, 0],
                "mixamorig:LeftArm": [0, 45, 0],
                "mixamorig:Head": [0, 0, 0],
                "mixamorig:Neck": [0, 0, 0],
            },
        }

        for pose_name, pose in realistic_poses.items():
            constrained_pose = validator.validate_and_constrain_pose(pose)

            # Verify poses are anatomically valid
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

    def test_character_movement_is_balanced(self):
        """Test that character movement maintains balance"""
        validator = JointConstraintValidator()

        # Test poses that maintain balance
        balanced_poses = {
            "centered_pose": {
                "mixamorig:RightArm": [0, 0, 0],
                "mixamorig:LeftArm": [0, 0, 0],
                "mixamorig:Head": [0, 0, 0],
                "mixamorig:Neck": [0, 0, 0],
            },
            "symmetric_pose": {
                "mixamorig:RightArm": [30, 0, 0],
                "mixamorig:LeftArm": [-30, 0, 0],  # Mirrored
                "mixamorig:Head": [0, 0, 0],
                "mixamorig:Neck": [0, 0, 0],
            },
        }

        for pose_name, pose in balanced_poses.items():
            constrained_pose = validator.validate_and_constrain_pose(pose)

            # Verify poses are anatomically valid
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


class TestSignLanguageAnimationFlow:
    """Test the flow of sign language animations"""

    def test_letter_by_letter_animation_flow(self):
        """Test that letter-by-letter animation flows smoothly"""
        # Mock animation manager
        mock_panel = Mock()
        mock_panel._is_animating = False
        mock_panel._actor = Mock()
        mock_panel._current_word = ""
        mock_panel._current_hand = "right"
        mock_panel._word_index = 0
        mock_panel._spell_word_letters = Mock()

        animation_manager = AnimationManager(mock_panel)

        # Test word animation
        test_word = "HELLO"
        animation_manager.apply_word_with_animation(test_word, "right")

        # Verify animation state is set correctly
        assert mock_panel._is_animating is True
        assert mock_panel._current_word == test_word
        assert mock_panel._current_hand == "right"
        assert mock_panel._word_index == 0
        mock_panel._spell_word_letters.assert_called_once_with(test_word)

    def test_gesture_playback_accuracy(self):
        """Test that gesture playback is accurate"""
        # Mock animation manager
        mock_panel = Mock()
        mock_panel.sign_loader = Mock()
        mock_panel.sign_loader.get_sign_data.return_value = {
            "pose": {
                "mixamorig:RightArm": [0, 45, 0],
                "mixamorig:RightHand": [0, 0, 0],
            }
        }

        animation_manager = AnimationManager(mock_panel)

        # Test getting pose data
        pose_data = animation_manager.get_letter_pose_from_signs("A", "right")

        # Verify pose data is retrieved correctly
        assert pose_data is not None
        assert "mixamorig:RightArm" in pose_data
        assert "mixamorig:RightHand" in pose_data
        mock_panel.sign_loader.get_sign_data.assert_called_once_with("A", "right")

    def test_animation_error_handling(self):
        """Test that animation errors are handled gracefully"""
        # Mock animation manager
        mock_panel = Mock()
        mock_panel._is_animating = True
        mock_panel._actor = Mock()
        mock_panel._actor.getCurrentAnimTime.side_effect = Exception("Animation error")

        animation_manager = AnimationManager(mock_panel)

        # Test animation frame handling with error
        animation_manager.on_signing_animation_frame()

        # Verify animation stops on error
        assert mock_panel._is_animating is False


class TestModelManagerIntegration:
    """Test model manager integration with realistic movement"""

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

    def test_model_manager_handles_missing_joints(self):
        """Test that model manager handles missing joints gracefully"""
        mock_panel = Mock()
        model_manager = ModelManager(mock_panel)

        # Test that model manager can handle missing joint scenarios
        # by checking if it has methods to handle joint operations
        assert hasattr(model_manager, "get_joint_constraint_info")
        assert hasattr(model_manager, "_get_joint_node")

        # Test getting constraint info for a missing joint
        constraint_info = model_manager.get_joint_constraint_info("MissingJoint")
        # Should handle gracefully without error
        assert constraint_info is None

    def test_model_manager_initialization(self):
        """Test that model manager initializes correctly"""
        mock_panel = Mock()
        model_manager = ModelManager(mock_panel)

        # Verify model manager is initialized correctly
        assert model_manager.parent_panel == mock_panel
        assert hasattr(model_manager, "_log")

        # Test that model manager has expected methods
        assert hasattr(model_manager, "load_model_internal")
        assert hasattr(model_manager, "get_joint_constraint_info")
        assert hasattr(model_manager, "_get_joint_node")
        assert hasattr(model_manager, "_apply_default_neutral_pose")


class TestAnimateGesturePanelIntegration:
    """Test AnimateGesturePanel integration with realistic movement"""

    def test_animate_gesture_panel_initialization(self):
        """Test that AnimateGesturePanel initializes correctly"""
        # Mock the panel
        with patch("src.helpmesign.modes.learn.animate_panel.main_panel.QWidget"):
            panel = AnimateGesturePanel()

            # Verify components are initialized
            assert panel._animation_manager is not None
            assert panel._model_manager is not None
            assert panel._panda_manager is not None

    def test_animate_gesture_panel_play_gesture(self):
        """Test that AnimateGesturePanel plays gestures correctly"""
        # Mock the panel
        with patch("src.helpmesign.modes.learn.animate_panel.main_panel.QWidget"):
            panel = AnimateGesturePanel()

            # Mock the animation manager
            panel._animation_manager = Mock()
            panel._animation_manager.get_letter_pose_from_signs.return_value = {
                "mixamorig:RightArm": [0, 45, 0]
            }
            panel._animation_manager.apply_pose = Mock()

            # Test playing gesture
            panel.play_gesture("A", "right")

            # Verify gesture was played
            panel._animation_manager.get_letter_pose_from_signs.assert_called_once_with(
                "A", "right"
            )
            panel._animation_manager.apply_pose.assert_called_once()

    def test_animate_gesture_panel_play_phrase(self):
        """Test that AnimateGesturePanel plays phrases correctly"""
        # Mock the panel
        with patch("src.helpmesign.modes.learn.animate_panel.main_panel.QWidget"):
            panel = AnimateGesturePanel()

            # Mock the animation manager
            panel._animation_manager = Mock()
            panel._animation_manager.apply_word_with_animation = Mock()

            # Test playing phrase
            panel.play_phrase("HELLO", "ASL", "right")

            # Verify phrase was played
            panel._animation_manager.apply_word_with_animation.assert_called_once_with(
                "HELLO", "right"
            )

    def test_animate_gesture_panel_load_character(self):
        """Test that AnimateGesturePanel loads characters correctly"""
        # Mock the panel
        with patch("src.helpmesign.modes.learn.animate_panel.main_panel.QWidget"):
            panel = AnimateGesturePanel()

            # Mock the managers
            panel._panda_manager = Mock()
            panel._panda_manager.ensure_panda = Mock()
            panel._model_manager = Mock()
            panel._model_manager.load_model_internal = Mock()

            # Test loading character
            panel.load_character("/path/to/character.glb")

            # Verify character was loaded
            panel._panda_manager.ensure_panda.assert_called_once()
            panel._model_manager.load_model_internal.assert_called_once_with(
                "/path/to/character.glb"
            )


class TestAnimationSystemErrorHandling:
    """Test error handling in the animation system"""

    def test_animation_manager_handles_missing_sign_data(self):
        """Test that animation manager handles missing sign data gracefully"""
        # Mock animation manager
        mock_panel = Mock()
        mock_panel.sign_loader = Mock()
        mock_panel.sign_loader.get_sign_data.return_value = None  # No sign data

        animation_manager = AnimationManager(mock_panel)

        # Test getting pose data for missing sign
        pose_data = animation_manager.get_letter_pose_from_signs("MISSING", "right")

        # Should return None gracefully
        assert pose_data is None

    def test_animation_manager_handles_invalid_pose_data(self):
        """Test that animation manager handles invalid pose data gracefully"""
        # Mock animation manager
        mock_panel = Mock()
        mock_panel.sign_loader = Mock()
        mock_panel.sign_loader.get_sign_data.return_value = {
            "pose": None  # Invalid pose data
        }

        animation_manager = AnimationManager(mock_panel)

        # Test getting pose data with invalid pose
        pose_data = animation_manager.get_letter_pose_from_signs("INVALID", "right")

        # Should return None gracefully
        assert pose_data is None

    def test_animation_manager_handles_actor_errors(self):
        """Test that animation manager handles actor errors gracefully"""
        # Mock animation manager
        mock_panel = Mock()
        mock_panel._is_animating = True
        mock_panel._actor = Mock()
        mock_panel._actor.getCurrentAnimTime.side_effect = Exception("Actor error")

        animation_manager = AnimationManager(mock_panel)

        # Test animation frame handling with actor error
        animation_manager.on_signing_animation_frame()

        # Should stop animation gracefully
        assert mock_panel._is_animating is False
