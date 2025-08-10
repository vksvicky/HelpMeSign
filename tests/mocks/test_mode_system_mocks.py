"""
Mock tests for the mode system
Tests using mocks to isolate components and test interactions
"""

import os
import shutil
import tempfile
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from src.helpmesign.modes.base_mode import BaseMode
from src.helpmesign.modes.learn.learn_mode import LearnMode

# Import the mode system components
from src.helpmesign.modes.mode_manager import ModeManager
from src.helpmesign.modes.sign_translate.sign_translate_mode import SignTranslateMode
from tests.mocks.qt.qt_module_mocks import activate_qt_mocks, deactivate_qt_mocks

# Import Qt mock framework
from tests.mocks.qt.qt_test_case import QtTestCase


class TestModeSystemMocks(QtTestCase):
    """Mock tests for the mode system"""

    @classmethod
    def setup_class(cls):
        """Set up class-level mocking"""
        # Mock settings_dialog module to prevent Qt import issues
        cls.mock_settings_dialog = MagicMock()
        cls.mock_settings_dialog.FontSizeSelector = MagicMock()
        cls.mock_settings_dialog.ModernSegmentedControl = MagicMock()
        cls.mock_settings_dialog.SettingsDialog = MagicMock()
        cls.mock_settings_dialog_patcher = patch(
            "src.helpmesign.ui.settings_dialog", cls.mock_settings_dialog
        )
        cls.mock_settings_dialog_patcher.start()

    @classmethod
    def teardown_class(cls):
        """Clean up class-level mocking"""
        cls.mock_settings_dialog_patcher.stop()

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
        self.mock_main_window.get_text_input = Mock()
        self.mock_main_window.set_text_output = Mock()
        self.mock_main_window.set_text_input = Mock()

        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()

        yield

        # Clean up after tests
        shutil.rmtree(self.test_dir, ignore_errors=True)
        deactivate_qt_mocks()

    # Mock Tests for BaseMode
    def test_mock_base_mode_initialization(self):
        """Test BaseMode initialization with mocked dependencies"""

        # Arrange
        class MockMode(BaseMode):
            def get_mode_name(self) -> str:
                return "Mocked Mode Name"

            def setup_ui(self) -> None:
                pass

            def setup_behavior(self) -> None:
                pass

            def process_text(self, text: str) -> str:
                return f"Mocked: {text}"

            def get_mode_description(self) -> str:
                return "Mocked description"

        # Act
        mode = MockMode(self.mock_main_window)

        # Assert
        assert mode.main_window == self.mock_main_window
        assert not hasattr(mode, "environment")
        assert mode.mode_name == "Mocked Mode Name"

    def test_mock_base_mode_activate(self):
        """Test BaseMode activate with mocked main window"""

        # Arrange
        class MockMode(BaseMode):
            def get_mode_name(self) -> str:
                return "Mock Mode"

            def setup_ui(self) -> None:
                pass

            def setup_behavior(self) -> None:
                pass

            def process_text(self, text: str) -> str:
                return text

            def get_mode_description(self) -> str:
                return "Mock description"

        mode = MockMode(self.mock_main_window)

        # Act
        mode.activate()

        # Assert
        self.mock_main_window.set_mode.assert_called_once_with("Mock Mode")
        self.mock_main_window.set_status.assert_called_once_with("Ready")

    def test_mock_base_mode_deactivate(self):
        """Test BaseMode deactivate with mocked dependencies"""

        # Arrange
        class MockMode(BaseMode):
            def get_mode_name(self) -> str:
                return "Mock Mode"

            def setup_ui(self) -> None:
                pass

            def setup_behavior(self) -> None:
                pass

            def process_text(self, text: str) -> str:
                return text

            def get_mode_description(self) -> str:
                return "Mock description"

        mode = MockMode(self.mock_main_window)

        # Act
        mode.deactivate()

        # Assert - deactivate should complete without error
        # The method should exist and be callable
        assert hasattr(mode, "deactivate")
        assert callable(mode.deactivate)

    # Mock Tests for SignTranslateMode
    def test_mock_sign_translate_mode_initialization(self):
        """Test SignTranslateMode initialization with mocked dependencies"""
        # Arrange & Act
        mode = SignTranslateMode(self.mock_main_window)

        # Assert
        assert mode.main_window == self.mock_main_window
        assert not hasattr(mode, "environment")
        assert mode.mode_name == "Sign & Translate"

    def test_mock_sign_translate_mode_process_text(self):
        """Test SignTranslateMode process_text with mocked dependencies"""
        # Arrange
        mode = SignTranslateMode(self.mock_main_window)

        # Act
        result = mode.process_text("hello")

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0

    def test_mock_sign_translate_mode_on_process_requested(self):
        """Test SignTranslateMode _on_process_requested with mocked dependencies"""
        # Arrange
        mode = SignTranslateMode(self.mock_main_window)

        # Act
        mode._on_process_requested()

        # Assert - should complete without error
        # The method should exist and be callable
        assert hasattr(mode, "_on_process_requested")
        assert callable(mode._on_process_requested)

    def test_mock_sign_translate_mode_on_clear_requested(self):
        """Test SignTranslateMode _on_clear_requested with mocked dependencies"""
        # Arrange
        mode = SignTranslateMode(self.mock_main_window)

        # Act
        mode._on_clear_requested()

        # Assert - should complete without error
        # The method should exist and be callable
        assert hasattr(mode, "_on_clear_requested")
        assert callable(mode._on_clear_requested)

    def test_mock_sign_translate_mode_clear_content(self):
        """Test SignTranslateMode clear_content with mocked dependencies"""
        # Arrange
        mode = SignTranslateMode(self.mock_main_window)

        # Act
        mode.clear_content()

        # Assert - should complete without error
        # The method should exist and be callable
        assert hasattr(mode, "clear_content")
        assert callable(mode.clear_content)

    def test_mock_sign_translate_mode_get_settings(self):
        """Test SignTranslateMode get_settings with mocked dependencies"""
        # Arrange
        mode = SignTranslateMode(self.mock_main_window)

        # Act
        settings = mode.get_settings()

        # Assert
        assert isinstance(settings, dict)

    # Mock Tests for LearnMode
    @patch("src.helpmesign.modes.learn.learn_mode.LearnMode.setup_ui")
    def test_mock_learn_mode_initialization(self, mock_setup_ui):
        """Test LearnMode initialization with mocked dependencies"""
        # Arrange & Act
        mode = LearnMode(self.mock_main_window)

        # Assert
        assert mode.main_window == self.mock_main_window
        assert not hasattr(mode, "environment")
        assert mode.mode_name == "Learn Sign Language"

    @patch("src.helpmesign.modes.learn.learn_mode.LearnMode.setup_ui")
    def test_mock_learn_mode_process_text(self, mock_setup_ui):
        """Test LearnMode process_text with mocked dependencies"""
        # Arrange
        mode = LearnMode(self.mock_main_window)

        # Act
        result = mode.process_text("hello")

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0

    @patch("src.helpmesign.modes.learn.learn_mode.LearnMode.setup_ui")
    def test_mock_learn_mode_on_learn_requested(self, mock_setup_ui):
        """Test LearnMode _on_learn_requested with mocked dependencies"""
        # Arrange
        mode = LearnMode(self.mock_main_window)

        # Act
        mode._on_learn_requested()

        # Assert - should complete without error
        # The method should exist and be callable
        assert hasattr(mode, "_on_learn_requested")
        assert callable(mode._on_learn_requested)

    @patch("src.helpmesign.modes.learn.learn_mode.LearnMode.setup_ui")
    def test_mock_learn_mode_on_clear_requested(self, mock_setup_ui):
        """Test LearnMode _on_clear_requested with mocked dependencies"""
        # Arrange
        mode = LearnMode(self.mock_main_window)

        # Act
        mode._on_clear_requested()

        # Assert - should complete without error
        # The method should exist and be callable
        assert hasattr(mode, "_on_clear_requested")
        assert callable(mode._on_clear_requested)

    @patch("src.helpmesign.modes.learn.learn_mode.LearnMode.setup_ui")
    def test_mock_learn_mode_clear_content(self, mock_setup_ui):
        """Test LearnMode clear_content with mocked dependencies"""
        # Arrange
        mode = LearnMode(self.mock_main_window)

        # Act
        mode.clear_content()

        # Assert - should complete without error
        # The method should exist and be callable
        assert hasattr(mode, "clear_content")
        assert callable(mode.clear_content)

    @patch("src.helpmesign.modes.learn.learn_mode.LearnMode.setup_ui")
    def test_mock_learn_mode_get_settings(self, mock_setup_ui):
        """Test LearnMode get_settings with mocked dependencies"""
        # Arrange
        mode = LearnMode(self.mock_main_window)

        # Act
        settings = mode.get_settings()

        # Assert
        assert isinstance(settings, dict)

    @patch("src.helpmesign.modes.learn.learn_mode.LearnMode.setup_ui")
    def test_mock_learn_mode_get_learning_progress(self, mock_setup_ui):
        """Test LearnMode get_learning_progress with mocked dependencies"""
        # Arrange
        mode = LearnMode(self.mock_main_window)

        # Act
        progress = mode.get_learning_progress()

        # Assert
        assert isinstance(progress, dict)

    @patch("src.helpmesign.modes.learn.learn_mode.LearnMode.setup_ui")
    def test_mock_learn_mode_get_lesson_suggestions(self, mock_setup_ui):
        """Test LearnMode get_lesson_suggestions with mocked dependencies"""
        # Arrange
        mode = LearnMode(self.mock_main_window)

        # Act
        suggestions = mode.get_lesson_suggestions()

        # Assert
        assert isinstance(suggestions, list)

    # Mock Tests for ModeManager
    def test_mock_mode_manager_initialization(self):
        """Test ModeManager initialization with mocked dependencies"""
        # Arrange & Act
        manager = self.create_mocked_mode_manager()

        # Assert
        assert manager.main_window == self.mock_main_window
        assert not hasattr(manager, "environment")
        assert manager.current_mode is not None

    def test_mock_mode_manager_get_available_modes(self):
        """Test ModeManager get_available_modes with mocked dependencies"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        modes = manager.get_available_modes()

        # Assert
        assert isinstance(modes, dict)
        assert "sign_translate" in modes
        assert "learn" in modes

    def test_mock_mode_manager_get_current_mode(self):
        """Test ModeManager get_current_mode with mocked dependencies"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        current_mode = manager.get_current_mode()

        # Assert
        assert current_mode is not None
        assert isinstance(current_mode, Mock)

    def test_mock_mode_manager_get_current_mode_name(self):
        """Test ModeManager get_current_mode_name with mocked dependencies"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        mode_name = manager.get_current_mode_name()

        # Assert
        assert isinstance(mode_name, str)
        assert len(mode_name) > 0

    def test_mock_mode_manager_switch_mode(self):
        """Test ModeManager switch_mode with mocked dependencies"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        success = manager.switch_mode("learn")

        # Assert
        assert success
        assert isinstance(manager.get_current_mode(), Mock)

    def test_mock_mode_manager_switch_mode_by_display_name(self):
        """Test ModeManager switch_mode_by_display_name with mocked dependencies"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        success = manager.switch_mode_by_display_name("Learn Sign Language")

        # Assert
        assert success
        assert isinstance(manager.get_current_mode(), Mock)

    def test_mock_mode_manager_process_text(self):
        """Test ModeManager process_text with mocked dependencies"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        result = manager.process_text("hello")

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0

    def test_mock_mode_manager_clear_content(self):
        """Test ModeManager clear_content with mocked dependencies"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        manager.clear_content()

        # Assert - should complete without error
        # The method should exist and be callable
        assert hasattr(manager, "clear_content")
        assert callable(manager.clear_content)

    def test_mock_mode_manager_get_mode_settings(self):
        """Test ModeManager get_mode_settings with mocked dependencies"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        settings = manager.get_mode_settings()

        # Assert
        assert isinstance(settings, dict)

    def test_mock_mode_manager_apply_mode_settings(self):
        """Test ModeManager apply_mode_settings with mocked dependencies"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        test_settings = {"test_key": "test_value"}

        # Act
        manager.apply_mode_settings(test_settings)

        # Assert - should complete without error
        # The method should exist and be callable
        assert hasattr(manager, "apply_mode_settings")
        assert callable(manager.apply_mode_settings)

    def test_mock_mode_manager_get_mode_descriptions(self):
        """Test ModeManager get_mode_descriptions with mocked dependencies"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        descriptions = manager.get_mode_descriptions()

        # Assert
        assert isinstance(descriptions, dict)
        assert "sign_translate" in descriptions
        assert "learn" in descriptions

    # Error Handling Tests
    def test_mock_mode_manager_switch_to_invalid_mode(self):
        """Test ModeManager switch_mode with invalid mode"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        success = manager.switch_mode("invalid_mode")

        # Assert
        assert not success
        assert isinstance(manager.get_current_mode(), Mock)

    def test_mock_mode_manager_switch_to_empty_mode(self):
        """Test ModeManager switch_mode with empty mode"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        success = manager.switch_mode("")

        # Assert
        assert not success
        assert isinstance(manager.get_current_mode(), Mock)

    def test_mock_mode_manager_switch_to_none_mode(self):
        """Test ModeManager switch_mode with None mode"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        success = manager.switch_mode(None)

        # Assert
        assert not success
        assert isinstance(manager.get_current_mode(), Mock)

    # Edge Cases
    def test_mock_mode_manager_process_text_no_current_mode(self):
        """Test ModeManager process_text when no current mode"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        manager.current_mode = None

        # Act
        result = manager.process_text("hello")

        # Assert
        assert result == "No active mode"

    def test_mock_mode_manager_clear_content_no_current_mode(self):
        """Test ModeManager clear_content when no current mode"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        manager.current_mode = None

        # Act
        manager.clear_content()

        # Assert - should complete without error even when no current mode
        # The method should exist and be callable
        assert hasattr(manager, "clear_content")
        assert callable(manager.clear_content)

    def test_mock_mode_manager_get_mode_settings_no_current_mode(self):
        """Test ModeManager get_mode_settings when no current mode"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        manager.current_mode = None

        # Act
        settings = manager.get_mode_settings()

        # Assert
        assert settings == {}

    def test_mock_mode_manager_apply_mode_settings_no_current_mode(self):
        """Test ModeManager apply_mode_settings when no current mode"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        manager.current_mode = None
        test_settings = {"test_key": "test_value"}

        # Act
        manager.apply_mode_settings(test_settings)

        # Assert - should complete without error even when no current mode
        # The method should exist and be callable
        assert hasattr(manager, "apply_mode_settings")
        assert callable(manager.apply_mode_settings)

    # Exception Handling Tests
    def test_mock_mode_manager_switch_mode_exception(self):
        """Test ModeManager switch_mode with exception"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        manager.current_mode.deactivate = Mock(side_effect=Exception("Test error"))

        # Act
        success = manager.switch_mode("learn")

        # Assert
        assert not success

    def test_mock_mode_manager_switch_mode_by_display_name_exception(self):
        """Test ModeManager switch_mode_by_display_name with exception"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        manager.current_mode.deactivate = Mock(side_effect=Exception("Test error"))

        # Act
        success = manager.switch_mode_by_display_name("Learn")

        # Assert
        assert not success

    def test_mock_mode_manager_process_text_exception(self):
        """Test ModeManager process_text with exception"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        manager.current_mode.process_text = Mock(side_effect=Exception("Test error"))

        # Act & Assert
        with pytest.raises(Exception):
            manager.process_text("hello")

    def test_mock_mode_manager_clear_content_exception(self):
        """Test ModeManager clear_content with exception"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        manager.current_mode.clear_content = Mock(side_effect=Exception("Test error"))

        # Act & Assert
        with pytest.raises(Exception):
            manager.clear_content()

    def test_mock_mode_manager_get_mode_settings_exception(self):
        """Test ModeManager get_mode_settings with exception"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        manager.current_mode.get_settings = Mock(side_effect=Exception("Test error"))

        # Act & Assert
        with pytest.raises(Exception):
            manager.get_mode_settings()

    def test_mock_mode_manager_apply_mode_settings_exception(self):
        """Test ModeManager apply_mode_settings with exception"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        manager.current_mode.apply_settings = Mock(side_effect=Exception("Test error"))
        test_settings = {"test_key": "test_value"}

        # Act & Assert
        with pytest.raises(Exception):
            manager.apply_mode_settings(test_settings)

    # Performance Tests
    def test_mock_mode_manager_switch_mode_multiple_times(self):
        """Test ModeManager switch_mode multiple times"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        for i in range(10):
            success = manager.switch_mode("learn")
            assert success
            success = manager.switch_mode("sign_translate")
            assert success

        # Assert
        assert isinstance(manager.get_current_mode(), Mock)

    def test_mock_mode_manager_switch_to_same_mode(self):
        """Test ModeManager switch_mode to same mode"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        success = manager.switch_mode("sign_translate")

        # Assert
        assert success
        assert isinstance(manager.get_current_mode(), Mock)

    # Boundary Tests
    def test_mock_mode_manager_very_long_text_processing(self):
        """Test ModeManager process_text with very long text"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        long_text = "a" * 10000

        # Act
        result = manager.process_text(long_text)

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0

    def test_mock_mode_manager_empty_text_processing(self):
        """Test ModeManager process_text with empty text"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        result = manager.process_text("")

        # Assert
        assert isinstance(result, str)

    def test_mock_mode_manager_unicode_text_processing(self):
        """Test ModeManager process_text with unicode text"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        unicode_text = "Hello 世界 🌍 🚀"

        # Act
        result = manager.process_text(unicode_text)

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0

    def test_mock_mode_manager_special_characters_text_processing(self):
        """Test ModeManager process_text with special characters"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        special_text = "!@#$%^&*()_+-=[]{}|;':\",./<>?"

        # Act
        result = manager.process_text(special_text)

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0

    def test_mock_mode_manager_none_text_processing(self):
        """Test ModeManager process_text with None text"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act & Assert
        with pytest.raises(AttributeError):
            manager.process_text(None)

    def test_mock_mode_manager_non_string_text_processing(self):
        """Test ModeManager process_text with non-string text"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act & Assert
        with pytest.raises(AttributeError):
            manager.process_text(123)

    # Integration Tests
    def test_mock_mode_manager_complete_workflow(self):
        """Test ModeManager complete workflow with mocked dependencies"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        test_texts = ["hello", "world", "test", "integration"]

        # Act
        results = {}
        settings = {}

        # Test sign translate mode
        manager.switch_mode("sign_translate")
        sign_results = []
        for text in test_texts:
            result = manager.process_text(text)
            sign_results.append(result)
        results["sign_translate"] = sign_results
        settings["sign_translate"] = manager.get_mode_settings()

        # Test learn mode
        manager.switch_mode("learn")
        learn_results = []
        for text in test_texts:
            result = manager.process_text(text)
            learn_results.append(result)
        results["learn"] = learn_results
        settings["learn"] = manager.get_mode_settings()

        # Assert
        assert "sign_translate" in results
        assert "learn" in results
        assert "sign_translate" in settings
        assert "learn" in settings

        # Check that all results are strings
        for mode_results in results.values():
            for result in mode_results:
                assert isinstance(result, str)
                assert len(result) > 0

        # Check that all settings are dictionaries
        for mode_settings in settings.values():
            assert isinstance(mode_settings, dict)

    def test_mock_mode_manager_mode_persistence(self):
        """Test ModeManager mode persistence with mocked dependencies"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        # Switch to learn mode and perform operations
        manager.switch_mode("learn")
        learn_mode = manager.get_current_mode()
        learn_result1 = manager.process_text("hello")
        learn_result2 = manager.process_text("thanks")

        # Switch to sign translate mode and perform operations
        manager.switch_mode("sign_translate")
        sign_mode = manager.get_current_mode()
        sign_result1 = manager.process_text("hello")
        sign_result2 = manager.process_text("thanks")

        # Switch back to learn mode
        manager.switch_mode("learn")
        final_mode = manager.get_current_mode()
        learn_result3 = manager.process_text("yes")

        # Assert
        assert isinstance(learn_mode, Mock)
        assert isinstance(sign_mode, Mock)
        assert isinstance(final_mode, Mock)
        assert learn_mode == final_mode  # Should be the same instance

        # Check that results are different between modes
        assert learn_result1 != sign_result1
        assert learn_result2 != sign_result2

    def test_mock_mode_manager_error_recovery(self):
        """Test ModeManager error recovery with mocked dependencies"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        # Try to switch to invalid mode (should fail)
        invalid_success = manager.switch_mode("invalid_mode")
        mode_after_invalid = manager.get_current_mode()

        # Switch to valid mode (should succeed)
        valid_success = manager.switch_mode("learn")
        mode_after_valid = manager.get_current_mode()

        # Process text in valid mode
        result = manager.process_text("hello")

        # Assert
        assert not invalid_success
        assert valid_success
        assert isinstance(mode_after_invalid, Mock)  # Should remain unchanged
        assert isinstance(mode_after_valid, Mock)
        assert isinstance(result, str)
        assert len(result) > 0
