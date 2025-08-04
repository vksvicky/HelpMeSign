"""
Mock tests for the mode system
Tests using mocks to isolate components and test interactions
"""

import os
import shutil
import tempfile
import unittest
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, call, patch

from src.helpmesign.modes.base_mode import BaseMode
from src.helpmesign.modes.learn.learn_mode import LearnMode

# Import the mode system components
from src.helpmesign.modes.mode_manager import ModeManager
from src.helpmesign.modes.sign_translate.sign_translate_mode import SignTranslateMode


class TestModeSystemMocks(unittest.TestCase):
    """Mock tests for the mode system"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a mock main window
        self.mock_main_window = Mock()
        self.mock_main_window.set_mode = Mock()
        self.mock_main_window.set_status = Mock()
        self.mock_main_window.get_text_input = Mock()
        self.mock_main_window.set_text_output = Mock()
        self.mock_main_window.set_text_input = Mock()

        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after tests"""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

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
        mode = MockMode(self.mock_main_window, "dev")

        # Assert
        self.assertEqual(mode.main_window, self.mock_main_window)
        self.assertEqual(mode.environment, "dev")
        self.assertEqual(mode.mode_name, "Mocked Mode Name")

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

        mode = MockMode(self.mock_main_window, "dev")

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

        mode = MockMode(self.mock_main_window, "dev")

        # Act
        mode.deactivate()

        # Assert
        # Should not raise any exceptions and not call any main window methods

    # Mock Tests for SignTranslateMode
    def test_mock_sign_translate_mode_initialization(self):
        """Test SignTranslateMode initialization with mocked dependencies"""
        # Arrange

        # Act
        mode = SignTranslateMode(self.mock_main_window, "dev")

        # Assert
        self.assertEqual(mode.main_window, self.mock_main_window)
        self.assertEqual(mode.environment, "dev")
        self.assertIsInstance(mode.conversion_history, list)
        self.assertEqual(len(mode.conversion_history), 0)

    def test_mock_sign_translate_mode_process_text(self):
        """Test SignTranslateMode text processing with mocked dependencies"""
        # Arrange
        mode = SignTranslateMode(self.mock_main_window, "dev")
        test_text = "hello"

        # Act
        result = mode.process_text(test_text)

        # Assert
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        self.assertEqual(len(mode.conversion_history), 1)
        self.assertEqual(mode.conversion_history[0]["input"], test_text)

    def test_mock_sign_translate_mode_on_process_requested(self):
        """Test SignTranslateMode process requested with mocked main window"""
        # Arrange
        mode = SignTranslateMode(self.mock_main_window, "dev")
        self.mock_main_window.get_text_input.return_value = "hello"

        # Act
        mode._on_process_requested()

        # Assert
        self.mock_main_window.get_text_input.assert_called_once()
        self.mock_main_window.set_text_output.assert_called_once()
        self.mock_main_window.set_status.assert_called_once()

    def test_mock_sign_translate_mode_on_clear_requested(self):
        """Test SignTranslateMode clear requested with mocked main window"""
        # Arrange
        mode = SignTranslateMode(self.mock_main_window, "dev")

        # Act
        mode._on_clear_requested()

        # Assert
        self.mock_main_window.set_text_input.assert_called_once_with("")
        self.mock_main_window.set_text_output.assert_called_once_with("")
        self.mock_main_window.set_status.assert_called_once()

    def test_mock_sign_translate_mode_clear_content(self):
        """Test SignTranslateMode clear content with mocked dependencies"""
        # Arrange
        mode = SignTranslateMode(self.mock_main_window, "dev")
        mode.conversion_history = [{"input": "test", "output": "result"}]

        # Act
        mode.clear_content()

        # Assert
        self.mock_main_window.set_text_input.assert_called_once_with("")
        self.mock_main_window.set_text_output.assert_called_once_with("")
        self.assertEqual(len(mode.conversion_history), 0)

    def test_mock_sign_translate_mode_get_settings(self):
        """Test SignTranslateMode get settings with mocked dependencies"""
        # Arrange
        mode = SignTranslateMode(self.mock_main_window, "dev")
        mode.conversion_history = [{"input": "test", "output": "result"}]

        # Act
        settings = mode.get_settings()

        # Assert
        self.assertEqual(settings["conversion_history_count"], 1)
        self.assertEqual(settings["mode"], "sign_translate")

    # Mock Tests for LearnMode
    def test_mock_learn_mode_initialization(self):
        """Test LearnMode initialization with mocked dependencies"""
        # Arrange

        # Act
        mode = LearnMode(self.mock_main_window, "dev")

        # Assert
        self.assertEqual(mode.main_window, self.mock_main_window)
        self.assertEqual(mode.environment, "dev")
        self.assertIsInstance(mode.learning_progress, dict)
        self.assertIsInstance(mode.lesson_history, list)
        self.assertIsNone(mode.current_lesson)

    def test_mock_learn_mode_process_text(self):
        """Test LearnMode text processing with mocked dependencies"""
        # Arrange
        mode = LearnMode(self.mock_main_window, "dev")
        test_text = "hello"

        # Act
        result = mode.process_text(test_text)

        # Assert
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        self.assertIn("hello", mode.learning_progress)

    def test_mock_learn_mode_on_learn_requested(self):
        """Test LearnMode learn requested with mocked main window"""
        # Arrange
        mode = LearnMode(self.mock_main_window, "dev")
        self.mock_main_window.get_text_input.return_value = "hello"

        # Act
        mode._on_learn_requested()

        # Assert
        self.mock_main_window.get_text_input.assert_called_once()
        self.mock_main_window.set_text_output.assert_called_once()
        self.mock_main_window.set_status.assert_called_once()

    def test_mock_learn_mode_on_clear_requested(self):
        """Test LearnMode clear requested with mocked main window"""
        # Arrange
        mode = LearnMode(self.mock_main_window, "dev")

        # Act
        mode._on_clear_requested()

        # Assert
        self.mock_main_window.set_text_input.assert_called_once_with("")
        self.mock_main_window.set_text_output.assert_called_once_with("")
        self.mock_main_window.set_status.assert_called_once()

    def test_mock_learn_mode_clear_content(self):
        """Test LearnMode clear content with mocked dependencies"""
        # Arrange
        mode = LearnMode(self.mock_main_window, "dev")
        mode.learning_progress = {"test": {"searched_count": 1}}

        # Act
        mode.clear_content()

        # Assert
        self.mock_main_window.set_text_input.assert_called_once_with("")
        self.mock_main_window.set_text_output.assert_called_once_with("")
        # Learning progress should NOT be cleared
        self.assertIn("test", mode.learning_progress)

    def test_mock_learn_mode_get_settings(self):
        """Test LearnMode get settings with mocked dependencies"""
        # Arrange
        mode = LearnMode(self.mock_main_window, "dev")
        mode.learning_progress = {"test": {"searched_count": 1}}
        mode.lesson_history = ["lesson1", "lesson2"]

        # Act
        settings = mode.get_settings()

        # Assert
        self.assertEqual(settings["learning_progress_count"], 1)
        self.assertEqual(settings["lesson_history_count"], 2)
        self.assertEqual(settings["mode"], "learn")

    def test_mock_learn_mode_get_learning_progress(self):
        """Test LearnMode get learning progress with mocked dependencies"""
        # Arrange
        mode = LearnMode(self.mock_main_window, "dev")
        mode.learning_progress = {"test": {"searched_count": 1}}

        # Act
        progress = mode.get_learning_progress()

        # Assert
        self.assertEqual(progress, {"test": {"searched_count": 1}})
        self.assertIsNot(progress, mode.learning_progress)  # Should be a copy

    def test_mock_learn_mode_get_lesson_suggestions(self):
        """Test LearnMode get lesson suggestions with mocked dependencies"""
        # Arrange
        mode = LearnMode(self.mock_main_window, "dev")

        # Act
        suggestions = mode.get_lesson_suggestions()

        # Assert
        self.assertIsInstance(suggestions, list)
        self.assertIn("Basic Greetings", suggestions)
        self.assertIn("Common Phrases", suggestions)
        self.assertIn("Numbers", suggestions)
        self.assertIn("Colors", suggestions)

    # Mock Tests for ModeManager
    def test_mock_mode_manager_initialization(self):
        """Test ModeManager initialization with mocked dependencies"""
        # Arrange

        # Act
        manager = ModeManager(self.mock_main_window, "dev")

        # Assert
        self.assertEqual(manager.main_window, self.mock_main_window)
        self.assertEqual(manager.environment, "dev")
        self.assertIsInstance(manager.modes, dict)
        self.assertIsNotNone(manager.current_mode)
        self.assertIn("sign_translate", manager.modes)
        self.assertIn("learn", manager.modes)

    def test_mock_mode_manager_get_available_modes(self):
        """Test ModeManager get available modes with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")

        # Act
        modes = manager.get_available_modes()

        # Assert
        self.assertIsInstance(modes, dict)
        self.assertIn("sign_translate", modes)
        self.assertIn("learn", modes)
        self.assertEqual(len(modes), 2)
        self.assertIsNot(modes, manager.modes)  # Should return a copy

    def test_mock_mode_manager_get_current_mode(self):
        """Test ModeManager get current mode with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")

        # Act
        current_mode = manager.get_current_mode()

        # Assert
        self.assertIsNotNone(current_mode)
        self.assertEqual(current_mode, manager.modes["sign_translate"])

    def test_mock_mode_manager_get_current_mode_name(self):
        """Test ModeManager get current mode name with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")

        # Act
        mode_name = manager.get_current_mode_name()

        # Assert
        self.assertIsInstance(mode_name, str)
        self.assertGreater(len(mode_name), 0)

    def test_mock_mode_manager_switch_mode(self):
        """Test ModeManager switch mode with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")

        # Act
        success = manager.switch_mode("learn")

        # Assert
        self.assertTrue(success)
        self.assertEqual(manager.current_mode, manager.modes["learn"])

    def test_mock_mode_manager_switch_mode_by_display_name(self):
        """Test ModeManager switch mode by display name with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")

        # Act
        success = manager.switch_mode_by_display_name("Learn Sign Language")

        # Assert
        self.assertTrue(success)
        self.assertEqual(manager.current_mode, manager.modes["learn"])

    def test_mock_mode_manager_process_text(self):
        """Test ModeManager process text with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        test_text = "hello"

        # Act
        result = manager.process_text(test_text)

        # Assert
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_mock_mode_manager_clear_content(self):
        """Test ModeManager clear content with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")

        # Act
        manager.clear_content()

        # Assert
        # Should not raise any exceptions

    def test_mock_mode_manager_get_mode_settings(self):
        """Test ModeManager get mode settings with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")

        # Act
        settings = manager.get_mode_settings()

        # Assert
        self.assertIsInstance(settings, dict)

    def test_mock_mode_manager_apply_mode_settings(self):
        """Test ModeManager apply mode settings with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        test_settings = {"key": "value"}

        # Act
        manager.apply_mode_settings(test_settings)

        # Assert
        # Should not raise any exceptions

    def test_mock_mode_manager_get_mode_descriptions(self):
        """Test ModeManager get mode descriptions with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")

        # Act
        descriptions = manager.get_mode_descriptions()

        # Assert
        self.assertIsInstance(descriptions, dict)
        self.assertIn("sign_translate", descriptions)
        self.assertIn("learn", descriptions)
        self.assertEqual(len(descriptions), 2)

    # Mock Tests for Error Conditions
    def test_mock_mode_manager_switch_to_invalid_mode(self):
        """Test ModeManager switch to invalid mode with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        original_mode = manager.get_current_mode()

        # Act
        success = manager.switch_mode("invalid_mode")
        current_mode = manager.get_current_mode()

        # Assert
        self.assertFalse(success)
        self.assertEqual(current_mode, original_mode)  # Should remain unchanged

    def test_mock_mode_manager_switch_to_empty_mode(self):
        """Test ModeManager switch to empty mode with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        original_mode = manager.get_current_mode()

        # Act
        success = manager.switch_mode("")
        current_mode = manager.get_current_mode()

        # Assert
        self.assertFalse(success)
        self.assertEqual(current_mode, original_mode)  # Should remain unchanged

    def test_mock_mode_manager_switch_to_none_mode(self):
        """Test ModeManager switch to None mode with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        original_mode = manager.get_current_mode()

        # Act
        success = manager.switch_mode(None)
        current_mode = manager.get_current_mode()

        # Assert
        self.assertFalse(success)
        self.assertEqual(current_mode, original_mode)  # Should remain unchanged

    def test_mock_mode_manager_process_text_no_current_mode(self):
        """Test ModeManager process text when no current mode with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        manager.current_mode = None

        # Act
        result = manager.process_text("test")

        # Assert
        self.assertEqual(result, "No active mode")

    def test_mock_mode_manager_clear_content_no_current_mode(self):
        """Test ModeManager clear content when no current mode with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        manager.current_mode = None

        # Act
        manager.clear_content()

        # Assert
        # Should not raise any exceptions

    def test_mock_mode_manager_get_mode_settings_no_current_mode(self):
        """Test ModeManager get mode settings when no current mode with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        manager.current_mode = None

        # Act
        settings = manager.get_mode_settings()

        # Assert
        self.assertEqual(settings, {})

    def test_mock_mode_manager_apply_mode_settings_no_current_mode(self):
        """Test ModeManager apply mode settings when no current mode with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        manager.current_mode = None
        test_settings = {"key": "value"}

        # Act
        manager.apply_mode_settings(test_settings)

        # Assert
        # Should not raise any exceptions

    # Mock Tests for Exception Handling
    def test_mock_mode_manager_switch_mode_exception(self):
        """Test ModeManager switch mode with exception handling"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        # Mock the current mode to raise an exception during deactivation
        manager.current_mode.deactivate = Mock(
            side_effect=Exception("Deactivation failed")
        )

        # Act
        success = manager.switch_mode("learn")

        # Assert
        self.assertFalse(success)

    def test_mock_mode_manager_switch_mode_by_display_name_exception(self):
        """Test ModeManager switch mode by display name with exception handling"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        # Mock the current mode to raise an exception during deactivation
        manager.current_mode.deactivate = Mock(
            side_effect=Exception("Deactivation failed")
        )

        # Act
        success = manager.switch_mode_by_display_name("Learn Sign Language")

        # Assert
        self.assertFalse(success)

    def test_mock_mode_manager_process_text_exception(self):
        """Test ModeManager process text with exception handling"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        # Mock the current mode to raise an exception during text processing
        manager.current_mode.process_text = Mock(
            side_effect=Exception("Processing failed")
        )

        # Act & Assert
        with self.assertRaises(Exception):
            manager.process_text("test")

    def test_mock_mode_manager_clear_content_exception(self):
        """Test ModeManager clear content with exception handling"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        # Mock the current mode to raise an exception during content clearing
        manager.current_mode.clear_content = Mock(side_effect=Exception("Clear failed"))

        # Act & Assert
        with self.assertRaises(Exception):
            manager.clear_content()

    def test_mock_mode_manager_get_mode_settings_exception(self):
        """Test ModeManager get mode settings with exception handling"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        # Mock the current mode to raise an exception during settings retrieval
        manager.current_mode.get_settings = Mock(
            side_effect=Exception("Settings failed")
        )

        # Act & Assert
        with self.assertRaises(Exception):
            manager.get_mode_settings()

    def test_mock_mode_manager_apply_mode_settings_exception(self):
        """Test ModeManager apply mode settings with exception handling"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        # Mock the current mode to raise an exception during settings application
        manager.current_mode.apply_settings = Mock(
            side_effect=Exception("Apply failed")
        )
        test_settings = {"key": "value"}

        # Act & Assert
        with self.assertRaises(Exception):
            manager.apply_mode_settings(test_settings)

    # Mock Tests for Boundary Conditions
    def test_mock_mode_manager_switch_mode_multiple_times(self):
        """Test ModeManager switch mode multiple times with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")

        # Act
        success1 = manager.switch_mode("learn")
        success2 = manager.switch_mode("sign_translate")
        success3 = manager.switch_mode("learn")

        # Assert
        self.assertTrue(success1)
        self.assertTrue(success2)
        self.assertTrue(success3)
        self.assertEqual(manager.current_mode, manager.modes["learn"])

    def test_mock_mode_manager_switch_to_same_mode(self):
        """Test ModeManager switch to same mode with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        original_mode = manager.current_mode

        # Act
        success = manager.switch_mode("sign_translate")

        # Assert
        self.assertTrue(success)
        self.assertEqual(manager.current_mode, original_mode)

    def test_mock_mode_manager_very_long_text_processing(self):
        """Test ModeManager very long text processing with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        long_text = "hello " * 1000  # 6000 character string

        # Act
        result = manager.process_text(long_text)

        # Assert
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_mock_mode_manager_empty_text_processing(self):
        """Test ModeManager empty text processing with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        empty_text = ""

        # Act
        result = manager.process_text(empty_text)

        # Assert
        self.assertIsInstance(result, str)

    def test_mock_mode_manager_unicode_text_processing(self):
        """Test ModeManager unicode text processing with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        unicode_text = "Hello 世界 🌍 🚀"

        # Act
        result = manager.process_text(unicode_text)

        # Assert
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_mock_mode_manager_special_characters_text_processing(self):
        """Test ModeManager special characters text processing with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        special_text = "!@#$%^&*()_+-=[]{}|;':\",./<>?"

        # Act
        result = manager.process_text(special_text)

        # Assert
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_mock_mode_manager_none_text_processing(self):
        """Test ModeManager None text processing with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")

        # Act & Assert
        with self.assertRaises(AttributeError):
            manager.process_text(None)

    def test_mock_mode_manager_non_string_text_processing(self):
        """Test ModeManager non-string text processing with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")

        # Act & Assert
        with self.assertRaises(AttributeError):
            manager.process_text(123)

        with self.assertRaises(AttributeError):
            manager.process_text(["list", "of", "strings"])

        with self.assertRaises(AttributeError):
            manager.process_text({"key": "value"})

    # Mock Tests for Complex Scenarios
    def test_mock_mode_manager_complete_workflow(self):
        """Test ModeManager complete workflow with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")
        test_texts = ["hello", "thanks", "yes", "no", "please", "sorry"]

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
        self.assertIn("sign_translate", results)
        self.assertIn("learn", results)
        self.assertIn("sign_translate", settings)
        self.assertIn("learn", settings)

        # Check that all results are strings
        for mode_results in results.values():
            for result in mode_results:
                self.assertIsInstance(result, str)
                self.assertGreater(len(result), 0)

        # Check that all settings are dictionaries
        for mode_settings in settings.values():
            self.assertIsInstance(mode_settings, dict)

    def test_mock_mode_manager_mode_persistence(self):
        """Test ModeManager mode persistence with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")

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
        self.assertIsInstance(learn_mode, LearnMode)
        self.assertIsInstance(sign_mode, SignTranslateMode)
        self.assertIsInstance(final_mode, LearnMode)
        self.assertEqual(learn_mode, final_mode)  # Should be the same instance

        # Check that results are different between modes
        self.assertNotEqual(learn_result1, sign_result1)
        self.assertNotEqual(learn_result2, sign_result2)

    def test_mock_mode_manager_error_recovery(self):
        """Test ModeManager error recovery with mocked dependencies"""
        # Arrange
        manager = ModeManager(self.mock_main_window, "dev")

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
        self.assertFalse(invalid_success)
        self.assertTrue(valid_success)
        self.assertIsInstance(
            mode_after_invalid, SignTranslateMode
        )  # Should remain unchanged
        self.assertIsInstance(mode_after_valid, LearnMode)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


if __name__ == "__main__":
    unittest.main()
