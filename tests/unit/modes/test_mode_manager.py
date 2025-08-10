"""
Unit tests for ModeManager class
Tests happy paths, error conditions, exceptions, and boundary conditions
"""

from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import the mode manager class
from src.helpmesign.modes.mode_manager import ModeManager
from tests.mocks.qt.qt_module_mocks import activate_qt_mocks, deactivate_qt_mocks
from tests.mocks.qt.qt_test_case import QtTestCase


class TestModeManager(QtTestCase):
    """Test cases for ModeManager class"""

    def create_mocked_mode_manager(self):
        """Helper method to create a mode manager with mocked modes"""
        with patch(
            "src.helpmesign.modes.mode_manager.LearnMode"
        ) as mock_learn_mode_class, patch(
            "src.helpmesign.modes.mode_manager.SignTranslateMode"
        ) as mock_sign_translate_mode_class:

            # Create mock mode instances
            mock_sign_translate_mode = Mock()
            mock_sign_translate_mode.get_mode_name.return_value = "Sign & Translate"
            mock_sign_translate_mode.get_mode_description.return_value = (
                "Sign Translation Mode"
            )
            mock_sign_translate_mode.process_text.side_effect = lambda text: (
                "Translated: hello"
                if isinstance(text, str)
                else (_ for _ in ()).throw(
                    AttributeError("'NoneType' object has no attribute 'lower'")
                )
            )
            mock_sign_translate_mode.get_settings.return_value = {
                "theme": "light",
                "font_size": 12,
            }
            mock_sign_translate_mode.deactivate = Mock()
            mock_sign_translate_mode.activate = Mock(
                side_effect=lambda: self.mock_main_window.set_mode("sign_translate")
            )
            mock_sign_translate_mode_class.return_value = mock_sign_translate_mode

            mock_learn_mode = Mock()
            mock_learn_mode.get_mode_name.return_value = "Learn Sign Language"
            mock_learn_mode.get_mode_description.return_value = "Learning Mode"
            mock_learn_mode.process_text.side_effect = lambda text: (
                "Processed: hello"
                if isinstance(text, str)
                else (_ for _ in ()).throw(
                    AttributeError("'NoneType' object has no attribute 'lower'")
                )
            )
            mock_learn_mode.get_settings.return_value = {
                "theme": "light",
                "font_size": 12,
            }
            mock_learn_mode.deactivate = Mock()
            mock_learn_mode.activate = Mock(
                side_effect=lambda: self.mock_main_window.set_mode("learn")
            )
            mock_learn_mode_class.return_value = mock_learn_mode

            # Create the mode manager instance with mocked modes
            return ModeManager(self.mock_main_window)

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures"""
        # Activate Qt mocks to prevent fatal errors
        activate_qt_mocks()

        # Create a mock main window
        self.mock_main_window = Mock()
        self.mock_main_window.set_mode = Mock()
        self.mock_main_window.set_status = Mock()

        yield

        # Clean up
        deactivate_qt_mocks()

    # Happy Path Tests
    def test_happy_path_initialization(self):
        """Test successful mode manager initialization"""
        # Arrange & Act
        manager = self.create_mocked_mode_manager()

        # Assert
        assert manager.main_window == self.mock_main_window
        assert isinstance(manager.modes, dict)
        assert manager.current_mode is not None
        assert "sign_translate" in manager.modes
        assert "learn" in manager.modes

    def test_happy_path_get_available_modes(self):
        """Test getting available modes"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        modes = manager.get_available_modes()

        # Assert
        assert isinstance(modes, dict)
        assert "sign_translate" in modes
        assert "learn" in modes
        assert len(modes) == 2
        # Should return a copy, not the original
        assert modes is not manager.modes

    def test_happy_path_get_current_mode(self):
        """Test getting current mode"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        current_mode = manager.get_current_mode()

        # Assert
        assert current_mode is not None
        assert current_mode == manager.modes["sign_translate"]

    @patch("src.helpmesign.modes.sign_translate.sign_translate_mode.get_text")
    def test_happy_path_get_current_mode_name(self, mock_get_text):
        """Test getting current mode name"""
        # Arrange
        mock_get_text.return_value = "Sign & Translate"
        manager = self.create_mocked_mode_manager()

        # Act
        mode_name = manager.get_current_mode_name()

        # Assert
        assert isinstance(mode_name, str)
        assert len(mode_name) > 0

    def test_happy_path_switch_mode_by_name(self):
        """Test switching mode by name"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        success = manager.switch_mode("learn")

        # Assert
        assert success
        assert manager.current_mode == manager.modes["learn"]

    @patch("src.helpmesign.modes.sign_translate.sign_translate_mode.get_text")
    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_happy_path_switch_mode_by_display_name(
        self, mock_learn_get_text, mock_sign_get_text
    ):
        """Test switching mode by display name"""
        # Arrange
        mock_sign_get_text.return_value = "Sign & Translate"
        mock_learn_get_text.return_value = "Learn Sign Language"
        manager = self.create_mocked_mode_manager()

        # Act
        success = manager.switch_mode_by_display_name("Learn Sign Language")

        # Assert
        assert success
        assert manager.current_mode == manager.modes["learn"]

    def test_happy_path_process_text(self):
        """Test processing text"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        test_text = "hello world"

        # Act
        result = manager.process_text(test_text)

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0

    def test_happy_path_clear_content(self):
        """Test clearing content"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act & Assert (should not raise any exceptions)
        try:
            manager.clear_content()
        except Exception as e:
            assert False, f"clear_content() raised {e} unexpectedly!"

    def test_happy_path_get_mode_settings(self):
        """Test getting mode settings"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        settings = manager.get_mode_settings()

        # Assert
        assert isinstance(settings, dict)

    def test_happy_path_apply_mode_settings(self):
        """Test applying mode settings"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        test_settings = {"theme": "dark", "font_size": 16}

        # Act & Assert (should not raise any exceptions)
        try:
            manager.apply_mode_settings(test_settings)
        except Exception as e:
            assert False, f"apply_mode_settings() raised {e} unexpectedly!"

    def test_happy_path_get_mode_descriptions(self):
        """Test getting mode descriptions"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        descriptions = manager.get_mode_descriptions()

        # Assert
        assert isinstance(descriptions, dict)
        assert "sign_translate" in descriptions
        assert "learn" in descriptions
        assert len(descriptions) == 2

    # Error Condition Tests
    def test_error_condition_switch_to_invalid_mode(self):
        """Test switching to invalid mode"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        success = manager.switch_mode("invalid_mode")

        # Assert
        assert not success
        assert manager.current_mode == manager.modes["sign_translate"]

    def test_error_condition_switch_to_invalid_display_name(self):
        """Test switching to invalid display name"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        success = manager.switch_mode_by_display_name("Invalid Mode")

        # Assert
        assert not success
        assert manager.current_mode == manager.modes["sign_translate"]

    def test_error_condition_empty_mode_name(self):
        """Test switching with empty mode name"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        success = manager.switch_mode("")

        # Assert
        assert not success
        assert manager.current_mode == manager.modes["sign_translate"]

    def test_error_condition_none_mode_name(self):
        """Test switching with None mode name"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        success = manager.switch_mode(None)

        # Assert
        assert not success
        assert manager.current_mode == manager.modes["sign_translate"]

    def test_error_condition_empty_display_name(self):
        """Test switching with empty display name"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        success = manager.switch_mode_by_display_name("")

        # Assert
        assert not success
        assert manager.current_mode == manager.modes["sign_translate"]

    def test_error_condition_none_display_name(self):
        """Test switching with None display name"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        success = manager.switch_mode_by_display_name(None)

        # Assert
        assert not success
        assert manager.current_mode == manager.modes["sign_translate"]

    def test_error_condition_process_text_no_current_mode(self):
        """Test processing text when no current mode"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        manager.current_mode = None

        # Act
        result = manager.process_text("test")

        # Assert
        assert result == "No active mode"

    def test_error_condition_clear_content_no_current_mode(self):
        """Test clearing content when no current mode"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        manager.current_mode = None

        # Act & Assert (should not raise any exceptions)
        try:
            manager.clear_content()
        except Exception as e:
            assert False, f"clear_content() raised {e} unexpectedly!"

    def test_error_condition_get_mode_settings_no_current_mode(self):
        """Test getting mode settings when no current mode"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        manager.current_mode = None

        # Act
        settings = manager.get_mode_settings()

        # Assert
        assert settings == {}

    def test_error_condition_apply_mode_settings_no_current_mode(self):
        """Test applying mode settings when no current mode"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        manager.current_mode = None
        test_settings = {"theme": "dark"}

        # Act & Assert (should not raise any exceptions)
        try:
            manager.apply_mode_settings(test_settings)
        except Exception as e:
            assert False, f"apply_mode_settings() raised {e} unexpectedly!"

    # Exception Tests
    def test_exception_in_switch_mode(self):
        """Test exception handling in switch_mode"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        # Mock current mode to raise exception during deactivation
        manager.current_mode.deactivate = Mock(
            side_effect=Exception("Deactivation failed")
        )

        # Act
        success = manager.switch_mode("learn")

        # Assert
        assert not success

    def test_exception_in_switch_mode_by_display_name(self):
        """Test exception handling in switch_mode_by_display_name"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        # Mock current mode to raise exception during deactivation
        manager.current_mode.deactivate = Mock(
            side_effect=Exception("Deactivation failed")
        )

        # Act
        success = manager.switch_mode_by_display_name("Learn Sign Language")

        # Assert
        assert not success

    def test_exception_in_process_text(self):
        """Test exception handling in process_text"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        # Mock current mode to raise exception during text processing
        manager.current_mode.process_text = Mock(
            side_effect=Exception("Processing failed")
        )

        # Act & Assert
        with pytest.raises(Exception):
            manager.process_text("test")

    def test_exception_in_clear_content(self):
        """Test exception handling in clear_content"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        # Mock current mode to raise exception during content clearing
        manager.current_mode.clear_content = Mock(side_effect=Exception("Clear failed"))

        # Act & Assert
        with pytest.raises(Exception):
            manager.clear_content()

    def test_exception_in_get_mode_settings(self):
        """Test exception handling in get_mode_settings"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        # Mock current mode to raise exception during settings retrieval
        manager.current_mode.get_settings = Mock(
            side_effect=Exception("Settings failed")
        )

        # Act & Assert
        with pytest.raises(Exception):
            manager.get_mode_settings()

    def test_exception_in_apply_mode_settings(self):
        """Test exception handling in apply_mode_settings"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        # Mock current mode to raise exception during settings application
        manager.current_mode.apply_settings = Mock(
            side_effect=Exception("Apply failed")
        )
        test_settings = {"theme": "dark"}

        # Act & Assert
        with pytest.raises(Exception):
            manager.apply_mode_settings(test_settings)

    # Boundary Condition Tests
    def test_boundary_condition_switch_mode_multiple_times(self):
        """Test switching mode multiple times"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        success1 = manager.switch_mode("learn")
        success2 = manager.switch_mode("sign_translate")
        success3 = manager.switch_mode("learn")

        # Assert
        assert success1
        assert success2
        assert success3
        assert manager.current_mode == manager.modes["learn"]

    def test_boundary_condition_switch_to_same_mode(self):
        """Test switching to the same mode"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        original_mode = manager.current_mode

        # Act
        success = manager.switch_mode("sign_translate")

        # Assert
        assert success
        assert manager.current_mode == original_mode

    def test_boundary_condition_very_long_text_processing(self):
        """Test processing very long text"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        long_text = "a" * 10000

        # Act
        result = manager.process_text(long_text)

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0

    @patch("src.helpmesign.modes.sign_translate.sign_translate_mode.get_text")
    def test_boundary_condition_empty_text_processing(self, mock_get_text):
        """Test processing empty text"""
        # Arrange
        mock_get_text.return_value = "Empty message"
        manager = self.create_mocked_mode_manager()
        empty_text = ""

        # Act
        result = manager.process_text(empty_text)

        # Assert
        assert isinstance(result, str)

    def test_boundary_condition_unicode_text_processing(self):
        """Test processing unicode text"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        unicode_text = "Hello 世界 🌍 🚀"

        # Act
        result = manager.process_text(unicode_text)

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0

    def test_boundary_condition_special_characters_text_processing(self):
        """Test processing text with special characters"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        special_text = "!@#$%^&*()_+-=[]{}|;':\",./<>?"

        # Act
        result = manager.process_text(special_text)

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0

    def test_boundary_condition_none_text_processing(self):
        """Test processing None text"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act & Assert
        with pytest.raises(AttributeError):
            manager.process_text(None)

    def test_boundary_condition_non_string_text_processing(self):
        """Test processing non-string text"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act & Assert
        with pytest.raises(AttributeError):
            manager.process_text(123)

        with pytest.raises(AttributeError):
            manager.process_text(["list", "of", "strings"])

        with pytest.raises(AttributeError):
            manager.process_text({"key": "value"})

    def test_boundary_condition_environment_values(self):
        """Test different environment values"""
        # Arrange & Act
        manager_dev = ModeManager(self.mock_main_window)
        manager_prod = ModeManager(self.mock_main_window)
        manager_test = ModeManager(self.mock_main_window)

        # Assert
        assert not hasattr(manager_dev, "environment")
        assert not hasattr(manager_prod, "environment")
        assert not hasattr(manager_test, "environment")

    def test_boundary_condition_empty_environment(self):
        """Test empty environment string"""
        # Arrange & Act
        manager = ModeManager(self.mock_main_window)

        # Assert
        assert not hasattr(manager, "environment")

    # Mock Tests
    def test_mock_main_window_interaction(self):
        """Test interaction with mocked main window"""
        # Arrange
        mock_window = Mock()
        mock_window.set_mode = Mock()
        mock_window.set_status = Mock()

        # Act
        manager = ModeManager(mock_window)

        # Assert
        assert manager.main_window == mock_window
        assert manager.current_mode is not None

    # Integration Tests (within unit test scope)
    @patch("src.helpmesign.modes.sign_translate.sign_translate_mode.get_text")
    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_integration_complete_mode_switching_workflow(
        self, mock_learn_get_text, mock_sign_get_text
    ):
        """Test complete mode switching workflow"""
        # Arrange
        mock_sign_get_text.return_value = "Sign & Translate"
        mock_learn_get_text.return_value = "Learn Sign Language"
        manager = self.create_mocked_mode_manager()

        # Act
        # Switch to learn mode
        success1 = manager.switch_mode("learn")
        mode1 = manager.get_current_mode()
        name1 = manager.get_current_mode_name()

        # Switch back to sign translate mode
        success2 = manager.switch_mode("sign_translate")
        mode2 = manager.get_current_mode()
        name2 = manager.get_current_mode_name()

        # Assert
        assert success1
        assert success2
        assert mode1 == manager.modes["learn"]
        assert mode2 == manager.modes["sign_translate"]
        assert name1 != name2

    def test_integration_mode_lifecycle_with_switching(self):
        """Test complete mode lifecycle with switching"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act - Complete lifecycle
        # Start with sign translate mode
        initial_mode = manager.get_current_mode()
        initial_name = manager.get_current_mode_name()

        # Switch to learn mode
        success = manager.switch_mode("learn")
        learn_mode = manager.get_current_mode()
        learn_name = manager.get_current_mode_name()

        # Process text in learn mode
        result = manager.process_text("hello")

        # Switch back to sign translate mode
        success2 = manager.switch_mode("sign_translate")
        final_mode = manager.get_current_mode()

        # Assert
        assert success
        assert success2
        assert initial_mode == manager.modes["sign_translate"]
        assert learn_mode == manager.modes["learn"]
        assert final_mode == manager.modes["sign_translate"]
        assert isinstance(result, str)

    def test_integration_all_modes_functionality(self):
        """Test functionality of all available modes"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        test_text = "hello"

        # Act
        # Test sign translate mode
        manager.switch_mode("sign_translate")
        sign_result = manager.process_text(test_text)

        # Test learn mode
        manager.switch_mode("learn")
        learn_result = manager.process_text(test_text)

        # Get settings from both modes
        sign_settings = manager.get_mode_settings()
        manager.switch_mode("sign_translate")
        learn_settings = manager.get_mode_settings()

        # Assert
        assert isinstance(sign_result, str)
        assert isinstance(learn_result, str)
        assert isinstance(sign_settings, dict)
        assert isinstance(learn_settings, dict)
        assert (
            sign_result != learn_result
        )  # Different modes should produce different results
