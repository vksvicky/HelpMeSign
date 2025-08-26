"""
Tests for the refactored AnimateGesturePanel components.
Tests the main panel and all manager classes.
"""

from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.helpmesign.modes.learn.animate_panel import AnimateGesturePanel
from src.helpmesign.modes.learn.animate_panel.animation_manager import AnimationManager
from src.helpmesign.modes.learn.animate_panel.model_manager import ModelManager
from src.helpmesign.modes.learn.animate_panel.panda3d_manager import Panda3DManager
from src.helpmesign.modes.learn.animate_panel.rendering_manager import RenderingManager


class TestAnimateGesturePanel:
    """Test the main AnimateGesturePanel class."""

    def test_initialization(self):
        """Test panel initialization."""
        panel = AnimateGesturePanel()

        assert panel._log is not None
        assert panel._headless is True  # No QApplication in test environment
        assert panel._panda_ready is False
        assert panel._is_animating is False
        assert panel._shutdown_requested is False

        # Check managers are initialized
        assert isinstance(panel._panda_manager, Panda3DManager)
        assert isinstance(panel._rendering_manager, RenderingManager)
        assert isinstance(panel._animation_manager, AnimationManager)
        assert isinstance(panel._model_manager, ModelManager)

    def test_set_language(self):
        """Test setting language."""
        panel = AnimateGesturePanel()
        panel.set_language("ASL")
        # Method should not raise any exceptions

    def test_load_character(self):
        """Test loading character."""
        panel = AnimateGesturePanel()

        with patch.object(panel._panda_manager, "ensure_panda") as mock_ensure:
            with patch.object(panel._model_manager, "load_model_internal") as mock_load:
                panel.load_character("test_model.glb")

                mock_ensure.assert_called_once()
                mock_load.assert_called_once_with("test_model.glb")

    def test_play_gesture(self):
        """Test playing gesture."""
        panel = AnimateGesturePanel()

        with patch.object(
            panel._animation_manager, "get_letter_pose_from_signs"
        ) as mock_get:
            with patch.object(panel._animation_manager, "apply_pose") as mock_apply:
                mock_get.return_value = {"RightHand": [0, 0, 0]}

                panel.play_gesture("A", "right")

                mock_get.assert_called_once_with("A", "right")
                mock_apply.assert_called_once_with({"RightHand": [0, 0, 0]})

    def test_play_phrase(self):
        """Test playing phrase."""
        panel = AnimateGesturePanel()

        with patch.object(
            panel._animation_manager, "apply_word_with_animation"
        ) as mock_apply:
            panel.play_phrase("HELLO", "right")

            mock_apply.assert_called_once_with("HELLO", "right")

    def test_cleanup(self):
        """Test cleanup method."""
        panel = AnimateGesturePanel()
        timer_mock = Mock()
        animation_timer_mock = Mock()
        phrase_timer_mock = Mock()
        panel._timer = timer_mock
        panel._animation_timer = animation_timer_mock
        panel._phrase_timer = phrase_timer_mock

        with patch.object(panel._panda_manager, "shutdown") as mock_shutdown:
            panel.cleanup()

            assert panel._shutdown_requested is True
            timer_mock.stop.assert_called_once()
            animation_timer_mock.stop.assert_called_once()
            phrase_timer_mock.stop.assert_called_once()
            mock_shutdown.assert_called_once()

            # Check that timers are set to None after stopping
            assert panel._timer is None
            assert panel._animation_timer is None
            assert panel._phrase_timer is None


class TestPanda3DManager:
    """Test the Panda3D manager."""

    def test_initialization(self):
        """Test manager initialization."""
        parent_panel = Mock()
        manager = Panda3DManager(parent_panel)

        assert manager.parent_panel == parent_panel
        assert manager._log is not None

    def test_ensure_panda_already_ready(self):
        """Test ensure_panda when already ready."""
        parent_panel = Mock()
        parent_panel._panda_ready = True

        manager = Panda3DManager(parent_panel)
        manager.ensure_panda()

        # Should return early without doing anything

    def test_shutdown_test_environment(self):
        """Test shutdown in test environment."""
        parent_panel = Mock()
        timer_mock = Mock()
        animation_timer_mock = Mock()
        phrase_timer_mock = Mock()
        parent_panel._timer = timer_mock
        parent_panel._animation_timer = animation_timer_mock
        parent_panel._phrase_timer = phrase_timer_mock

        manager = Panda3DManager(parent_panel)

        with patch("sys.argv", ["pytest"]):
            manager.shutdown()

            timer_mock.stop.assert_called_once()
            animation_timer_mock.stop.assert_called_once()
            phrase_timer_mock.stop.assert_called_once()
            assert parent_panel._actor is None
            assert parent_panel._panda_ready is False

            # Check that timers are set to None after stopping
            assert parent_panel._timer is None
            assert parent_panel._animation_timer is None
            assert parent_panel._phrase_timer is None


class TestRenderingManager:
    """Test the rendering manager."""

    def test_initialization(self):
        """Test manager initialization."""
        parent_panel = Mock()
        manager = RenderingManager(parent_panel)

        assert manager.parent_panel == parent_panel
        assert manager._log is not None
        assert manager._capture_counter == 0
        assert manager._capture_every_n_frames == 3

    def test_on_frame_not_ready(self):
        """Test on_frame when Panda3D not ready."""
        parent_panel = Mock()
        parent_panel._panda_ready = False

        manager = RenderingManager(parent_panel)
        manager.on_frame()

        # Should return early without doing anything

    def test_on_frame_shutdown_requested(self):
        """Test on_frame when shutdown requested."""
        parent_panel = Mock()
        parent_panel._panda_ready = True
        parent_panel._shutdown_requested = True

        manager = RenderingManager(parent_panel)
        manager.on_frame()

        # Should return early without doing anything

    def test_update_render_target_size_not_ready(self):
        """Test update_render_target_size when not ready."""
        parent_panel = Mock()
        parent_panel._panda_ready = False

        manager = RenderingManager(parent_panel)
        manager.update_render_target_size()

        # Should return early without doing anything


class TestAnimationManager:
    """Test the animation manager."""

    def test_initialization(self):
        """Test manager initialization."""
        parent_panel = Mock()
        manager = AnimationManager(parent_panel)

        assert manager.parent_panel == parent_panel
        assert manager._log is not None

    def test_get_letter_pose_from_signs_no_loader(self):
        """Test getting letter pose when no sign loader."""
        parent_panel = Mock()
        parent_panel.sign_loader = None

        manager = AnimationManager(parent_panel)
        result = manager.get_letter_pose_from_signs("A", "right")

        assert result is None

    def test_get_letter_pose_from_signs_with_loader(self):
        """Test getting letter pose with sign loader."""
        parent_panel = Mock()
        parent_panel.sign_loader = Mock()
        parent_panel.sign_loader.get_sign_data.return_value = {
            "pose": {"RightHand": [0, 0, 0]}
        }

        manager = AnimationManager(parent_panel)
        result = manager.get_letter_pose_from_signs("A", "right")

        assert result == {"RightHand": [0, 0, 0]}
        parent_panel.sign_loader.get_sign_data.assert_called_once_with("A", "right")

    def test_apply_word_with_animation_no_word(self):
        """Test applying word animation with no word."""
        parent_panel = Mock()
        parent_panel._actor = Mock()
        parent_panel._is_animating = False

        manager = AnimationManager(parent_panel)
        manager.apply_word_with_animation("", "right")

        assert parent_panel._is_animating is False

    def test_apply_word_with_animation_no_actor(self):
        """Test applying word animation with no actor."""
        parent_panel = Mock()
        parent_panel._actor = None
        parent_panel._is_animating = False

        manager = AnimationManager(parent_panel)
        manager.apply_word_with_animation("HELLO", "right")

        assert parent_panel._is_animating is False

    def test_apply_word_with_animation_success(self):
        """Test applying word animation successfully."""
        parent_panel = Mock()
        parent_panel._actor = Mock()

        manager = AnimationManager(parent_panel)
        manager.apply_word_with_animation("HELLO", "right")

        assert parent_panel._is_animating is True
        assert parent_panel._current_word == "HELLO"
        assert parent_panel._current_hand == "right"
        assert parent_panel._word_index == 0

    def test_reset_to_neutral_pose(self):
        """Test resetting to neutral pose."""
        parent_panel = Mock()
        parent_panel._actor = Mock()
        parent_panel._is_animating = True
        parent_panel._wave_active = True
        parent_panel._intro_active = True

        manager = AnimationManager(parent_panel)
        manager.reset_to_neutral_pose()

        assert parent_panel._is_animating is False
        assert parent_panel._wave_active is False
        assert parent_panel._intro_active is False
        parent_panel._actor.pose.assert_called_once_with("idle", 0)


class TestModelManager:
    """Test the model manager."""

    def test_initialization(self):
        """Test manager initialization."""
        parent_panel = Mock()
        manager = ModelManager(parent_panel)

        assert manager.parent_panel == parent_panel
        assert manager._log is not None

    def test_load_model_internal_not_ready(self):
        """Test loading model when Panda3D not ready."""
        parent_panel = Mock()
        parent_panel._panda_ready = False

        manager = ModelManager(parent_panel)
        manager.load_model_internal("test.glb")

        # Should return early without doing anything

    def test_validate_pose_before_application_empty_pose(self):
        """Test pose validation with empty pose."""
        parent_panel = Mock()
        manager = ModelManager(parent_panel)

        result = manager.validate_pose_before_application({})
        assert result is False

    def test_validate_pose_before_application_none_pose(self):
        """Test pose validation with None pose."""
        parent_panel = Mock()
        manager = ModelManager(parent_panel)

        result = manager.validate_pose_before_application(None)
        assert result is False

    def test_is_pose_anatomically_valid_empty_pose(self):
        """Test anatomical validation with empty pose."""
        parent_panel = Mock()
        manager = ModelManager(parent_panel)

        result = manager.is_pose_anatomically_valid({})
        assert result is False

    def test_get_joint_constraint_info(self):
        """Test getting joint constraint info."""
        parent_panel = Mock()
        manager = ModelManager(parent_panel)

        result = manager.get_joint_constraint_info("RightHand")
        assert result is None  # Currently returns None

    def test_best_alias_found(self):
        """Test finding best alias for joint name."""
        parent_panel = Mock()
        parent_panel._model_np = Mock()
        parent_panel._model_np.find.return_value = Mock()
        parent_panel._model_np.find.return_value.isEmpty.return_value = False

        manager = ModelManager(parent_panel)
        result = manager._best_alias("RightHand")

        assert result == "RightHand"  # Should find the first alias

    def test_best_alias_not_found(self):
        """Test finding best alias when not found."""
        parent_panel = Mock()
        parent_panel._model_np = Mock()
        parent_panel._model_np.find.return_value = Mock()
        parent_panel._model_np.find.return_value.isEmpty.return_value = True

        manager = ModelManager(parent_panel)
        result = manager._best_alias("UnknownJoint")

        assert result == "UnknownJoint"  # Should return original name


class TestAnimateGesturePanelIntegration:
    """Integration tests for AnimateGesturePanel."""

    def test_manager_coordination(self):
        """Test that managers work together properly."""
        panel = AnimateGesturePanel()

        # Test that managers are properly connected
        assert panel._panda_manager.parent_panel == panel
        assert panel._rendering_manager.parent_panel == panel
        assert panel._animation_manager.parent_panel == panel
        assert panel._model_manager.parent_panel == panel

    def test_delegation_to_managers(self):
        """Test that methods properly delegate to managers."""
        panel = AnimateGesturePanel()

        with patch.object(panel._animation_manager, "apply_pose") as mock_apply:
            panel._apply_pose({"RightHand": [0, 0, 0]})
            mock_apply.assert_called_once_with({"RightHand": [0, 0, 0]})

        with patch.object(
            panel._animation_manager, "reset_to_neutral_pose"
        ) as mock_reset:
            panel._reset_to_neutral_pose()
            mock_reset.assert_called_once()

        with patch.object(panel._model_manager, "_find_node_by_names") as mock_find:
            panel._find_node_by_names(["RightHand"])
            mock_find.assert_called_once_with(["RightHand"])

    def test_cleanup_coordination(self):
        """Test that cleanup properly coordinates all managers."""
        panel = AnimateGesturePanel()
        timer_mock = Mock()
        animation_timer_mock = Mock()
        phrase_timer_mock = Mock()
        panel._timer = timer_mock
        panel._animation_timer = animation_timer_mock
        panel._phrase_timer = phrase_timer_mock

        with patch.object(panel._panda_manager, "shutdown") as mock_shutdown:
            panel.cleanup()

            # Check that all timers are stopped
            timer_mock.stop.assert_called_once()
            animation_timer_mock.stop.assert_called_once()
            phrase_timer_mock.stop.assert_called_once()

            # Check that Panda3D manager is shutdown
            mock_shutdown.assert_called_once()

            # Check that references are cleared
            assert panel._actor is None
            assert panel._model_np is None
            assert panel._camera is None
            assert panel._showbase is None
            assert panel._color_tex is None
            assert panel._panda_ready is False

            # Check that timers are set to None after stopping
            assert panel._timer is None
            assert panel._animation_timer is None
            assert panel._phrase_timer is None
