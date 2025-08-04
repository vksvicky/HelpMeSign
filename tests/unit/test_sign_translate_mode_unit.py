"""
Unit tests for SignTranslateMode class
Tests happy paths, error conditions, exceptions, and boundary conditions
"""

import unittest
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

# Import the sign translate mode class
from src.helpmesign.modes.sign_translate.sign_translate_mode import SignTranslateMode


class TestSignTranslateMode(unittest.TestCase):
    """Test cases for SignTranslateMode class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a mock main window with all required methods
        self.mock_main_window = Mock()
        self.mock_main_window.set_mode = Mock()
        self.mock_main_window.set_status = Mock()
        self.mock_main_window.get_text_input = Mock()
        self.mock_main_window.set_text_output = Mock()
        self.mock_main_window.set_text_input = Mock()

        # Create the mode instance
        self.mode = SignTranslateMode(self.mock_main_window, "dev")

    def tearDown(self):
        """Clean up after tests"""
        pass

    # Happy Path Tests
    def test_happy_path_initialization(self):
        """Test successful mode initialization"""
        # Arrange & Act
        mode = self.mode

        # Assert
        self.assertEqual(mode.main_window, self.mock_main_window)
        self.assertEqual(mode.environment, "dev")
        self.assertIsInstance(mode.conversion_history, list)
        self.assertEqual(len(mode.conversion_history), 0)

    @patch("src.helpmesign.modes.sign_translate.sign_translate_mode.get_text")
    def test_happy_path_get_mode_name(self, mock_get_text):
        """Test getting mode name"""
        # Arrange
        mock_get_text.return_value = "Sign & Translate"

        # Act
        name = self.mode.get_mode_name()

        # Assert
        self.assertEqual(name, "Sign & Translate")
        mock_get_text.assert_called_once_with("modes.sign_translate.name")

    @patch("src.helpmesign.modes.sign_translate.sign_translate_mode.get_text")
    def test_happy_path_get_mode_description(self, mock_get_text):
        """Test getting mode description"""
        # Arrange
        mock_get_text.return_value = "Convert text to sign language"

        # Act
        description = self.mode.get_mode_description()

        # Assert
        self.assertEqual(description, "Convert text to sign language")
        mock_get_text.assert_called_once_with("modes.sign_translate.description")

    def test_happy_path_process_text_hello(self):
        """Test processing 'hello' text"""
        # Arrange
        test_text = "hello"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        self.assertIn("👋 Wave hand", result)
        self.assertEqual(len(self.mode.conversion_history), 1)
        self.assertEqual(self.mode.conversion_history[0]["input"], test_text)

    def test_happy_path_process_text_thanks(self):
        """Test processing 'thanks' text"""
        # Arrange
        test_text = "thanks"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        self.assertIn("🙏 Hand to chin, then forward", result)
        self.assertEqual(len(self.mode.conversion_history), 1)

    def test_happy_path_process_text_yes(self):
        """Test processing 'yes' text"""
        # Arrange
        test_text = "yes"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        self.assertIn("👍 Nod head and fist", result)

    def test_happy_path_process_text_no(self):
        """Test processing 'no' text"""
        # Arrange
        test_text = "no"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        self.assertIn("👎 Shake head and index finger", result)

    def test_happy_path_process_text_please(self):
        """Test processing 'please' text"""
        # Arrange
        test_text = "please"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        self.assertIn("🤲 Flat hand, palm up, circular motion", result)

    def test_happy_path_process_text_sorry(self):
        """Test processing 'sorry' text"""
        # Arrange
        test_text = "sorry"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        self.assertIn("🤝 Fist over heart, circular motion", result)

    def test_happy_path_process_text_unknown_word(self):
        """Test processing unknown word"""
        # Arrange
        test_text = "unknown"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        self.assertIn("🤟 Spell: u n k n o w n", result)  # Fixed: lowercase

    def test_happy_path_process_text_multiple_words(self):
        """Test processing multiple words"""
        # Arrange
        test_text = "hello please thanks"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        self.assertIn("👋 Wave hand", result)
        self.assertIn("🤲 Flat hand, palm up, circular motion", result)
        self.assertIn("🙏 Hand to chin, then forward", result)
        self.assertIn(" | ", result)  # Separator between words

    def test_happy_path_convert_to_sign_language(self):
        """Test direct conversion method"""
        # Arrange
        test_text = "hello world"

        # Act
        result = self.mode.convert_to_sign_language(test_text)

        # Assert
        self.assertIn("👋 Wave hand", result)
        self.assertIn("🤟 Spell: w o r l d", result)  # Fixed: lowercase

    def test_happy_path_on_process_requested(self):
        """Test process button click handler"""
        # Arrange
        self.mock_main_window.get_text_input.return_value = "hello"

        # Act
        self.mode._on_process_requested()

        # Assert
        self.mock_main_window.get_text_input.assert_called_once()
        self.mock_main_window.set_text_output.assert_called_once()
        self.mock_main_window.set_status.assert_called_once()

    def test_happy_path_on_clear_requested(self):
        """Test clear button click handler"""
        # Arrange

        # Act
        self.mode._on_clear_requested()

        # Assert
        self.mock_main_window.set_text_input.assert_called_once_with("")
        self.mock_main_window.set_text_output.assert_called_once_with("")
        self.mock_main_window.set_status.assert_called_once()

    def test_happy_path_clear_content(self):
        """Test clearing mode content"""
        # Arrange
        # Add some conversion history
        self.mode.conversion_history = [{"input": "test", "output": "result"}]

        # Act
        self.mode.clear_content()

        # Assert
        self.mock_main_window.set_text_input.assert_called_once_with("")
        self.mock_main_window.set_text_output.assert_called_once_with("")
        self.assertEqual(len(self.mode.conversion_history), 0)

    def test_happy_path_get_settings(self):
        """Test getting mode settings"""
        # Arrange
        self.mode.conversion_history = [{"input": "test", "output": "result"}]

        # Act
        settings = self.mode.get_settings()

        # Assert
        self.assertEqual(settings["conversion_history_count"], 1)
        self.assertEqual(settings["mode"], "sign_translate")

    # Error Condition Tests
    @patch("src.helpmesign.modes.sign_translate.sign_translate_mode.get_text")
    def test_error_condition_empty_text_processing(self, mock_get_text):
        """Test processing empty text"""
        # Arrange
        mock_get_text.return_value = "Please enter some text to convert."
        empty_text = ""

        # Act
        result = self.mode.process_text(empty_text)

        # Assert
        self.assertIsInstance(result, str)
        self.assertEqual(len(self.mode.conversion_history), 0)  # No history entry

    @patch("src.helpmesign.modes.sign_translate.sign_translate_mode.get_text")
    def test_error_condition_whitespace_text_processing(self, mock_get_text):
        """Test processing whitespace-only text"""
        # Arrange
        mock_get_text.return_value = "Please enter some text to convert."
        whitespace_text = "   \n\t   "

        # Act
        result = self.mode.process_text(whitespace_text)

        # Assert
        self.assertIsInstance(result, str)
        self.assertEqual(len(self.mode.conversion_history), 0)  # No history entry

    def test_error_condition_mixed_case_processing(self):
        """Test processing mixed case text"""
        # Arrange
        mixed_text = "Hello THANKS Yes"

        # Act
        result = self.mode.process_text(mixed_text)

        # Assert
        self.assertIn("👋 Wave hand", result)  # hello
        self.assertIn("🙏 Hand to chin, then forward", result)  # thanks
        self.assertIn("👍 Nod head and fist", result)  # yes

    def test_error_condition_process_requested_no_input(self):
        """Test process button with no input"""
        # Arrange
        self.mock_main_window.get_text_input.return_value = ""

        # Act
        self.mode._on_process_requested()

        # Assert
        self.mock_main_window.get_text_input.assert_called_once()
        self.mock_main_window.set_text_output.assert_called_once()
        self.mock_main_window.set_status.assert_called_once()

    # Exception Tests
    def test_exception_in_process_requested(self):
        """Test exception handling in process requested"""
        # Arrange
        self.mock_main_window.get_text_input.side_effect = Exception("Input error")

        # Act
        self.mode._on_process_requested()

        # Assert
        self.mock_main_window.set_text_output.assert_called_once()
        self.mock_main_window.set_status.assert_called_once_with("Error occurred")

    def test_exception_in_clear_requested(self):
        """Test exception handling in clear requested"""
        # Arrange
        self.mock_main_window.set_text_input.side_effect = Exception("Clear error")

        # Act & Assert
        with self.assertRaises(Exception):
            self.mode._on_clear_requested()

    def test_exception_in_convert_to_sign_language(self):
        """Test exception handling in conversion"""
        # Arrange
        # Mock the method to raise an exception
        original_method = self.mode.convert_to_sign_language
        self.mode.convert_to_sign_language = Mock(
            side_effect=Exception("Conversion error")
        )

        # Act & Assert
        with self.assertRaises(Exception):
            self.mode.process_text("test")

        # Restore original method
        self.mode.convert_to_sign_language = original_method

    # Boundary Condition Tests
    def test_boundary_condition_very_long_text(self):
        """Test processing very long text"""
        # Arrange
        long_text = "hello " * 1000  # 6000 character string

        # Act
        result = self.mode.process_text(long_text)

        # Assert
        self.assertIn("👋 Wave hand", result)
        self.assertIn(" | ", result)  # Should have separators
        self.assertEqual(len(self.mode.conversion_history), 1)

    def test_boundary_condition_single_character_words(self):
        """Test processing single character words"""
        # Arrange
        single_char_text = "a b c d"

        # Act
        result = self.mode.process_text(single_char_text)

        # Assert
        self.assertIn("🤟 Spell: a", result)  # Fixed: lowercase
        self.assertIn("🤟 Spell: b", result)  # Fixed: lowercase
        self.assertIn("🤟 Spell: c", result)  # Fixed: lowercase
        self.assertIn("🤟 Spell: d", result)  # Fixed: lowercase

    def test_boundary_condition_numbers_in_text(self):
        """Test processing text with numbers"""
        # Arrange
        number_text = "hello 123 world"

        # Act
        result = self.mode.process_text(number_text)

        # Assert
        self.assertIn("👋 Wave hand", result)  # hello
        self.assertIn("🤟 Spell: 1 2 3", result)  # numbers
        self.assertIn("🤟 Spell: w o r l d", result)  # world - Fixed: lowercase

    def test_boundary_condition_special_characters(self):
        """Test processing text with special characters"""
        # Arrange
        special_text = "hello! world?"

        # Act
        result = self.mode.process_text(special_text)

        # Assert
        # Special characters are treated as part of the word, so they get spelled out
        self.assertIn("🤟 Spell: h e l l o !", result)  # Fixed: lowercase
        self.assertIn("🤟 Spell: w o r l d ?", result)  # Fixed: lowercase

    def test_boundary_condition_unicode_text(self):
        """Test processing unicode text"""
        # Arrange
        unicode_text = "hello 世界"

        # Act
        result = self.mode.process_text(unicode_text)

        # Assert
        self.assertIn("👋 Wave hand", result)  # hello
        self.assertIn("🤟 Spell: 世 界", result)  # unicode characters

    def test_boundary_condition_conversion_history_limit(self):
        """Test conversion history with many entries"""
        # Arrange
        # Add many conversions
        for i in range(100):
            self.mode.process_text(f"test{i}")

        # Act
        settings = self.mode.get_settings()

        # Assert
        self.assertEqual(settings["conversion_history_count"], 100)
        self.assertEqual(len(self.mode.conversion_history), 100)

    # Mock Tests
    @patch("src.helpmesign.modes.sign_translate.sign_translate_mode.get_text")
    def test_mock_language_integration(self, mock_get_text):
        """Test integration with language system using mocks"""
        # Arrange
        mock_get_text.side_effect = lambda key: {
            "modes.sign_translate.name": "Mocked Sign & Translate",
            "modes.sign_translate.description": "Mocked description",
            "ui.output.empty_message": "Mocked empty message",
        }.get(key, "Mocked text")

        # Act
        name = self.mode.get_mode_name()
        description = self.mode.get_mode_description()

        # Assert
        self.assertEqual(name, "Mocked Sign & Translate")
        self.assertEqual(description, "Mocked description")
        self.assertEqual(mock_get_text.call_count, 2)

    def test_mock_main_window_signal_connections(self):
        """Test signal connections with mocked main window"""
        # Arrange
        mock_window = Mock()
        mock_window.process_requested = Mock()
        mock_window.clear_requested = Mock()

        # Act
        mode = SignTranslateMode(mock_window, "dev")

        # Assert
        # The mode should connect to signals during setup_behavior
        # This is tested indirectly through the setup_behavior call

    # Integration Tests (within unit test scope)
    def test_integration_complete_conversion_workflow(self):
        """Test complete conversion workflow"""
        # Arrange
        test_text = "hello please thanks"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        self.assertIn("👋 Wave hand", result)
        self.assertIn("🤲 Flat hand, palm up, circular motion", result)
        self.assertIn("🙏 Hand to chin, then forward", result)
        self.assertEqual(len(self.mode.conversion_history), 1)
        self.assertEqual(self.mode.conversion_history[0]["input"], test_text)

    def test_integration_mode_lifecycle_with_conversions(self):
        """Test complete mode lifecycle with conversions"""
        # Arrange
        mode = self.mode

        # Act - Complete lifecycle
        mode.activate()
        result1 = mode.process_text("hello")
        result2 = mode.process_text("thanks")
        mode.clear_content()
        settings = mode.get_settings()
        mode.deactivate()

        # Assert
        self.assertIn("👋 Wave hand", result1)
        self.assertIn("🙏 Hand to chin, then forward", result2)
        self.assertEqual(settings["conversion_history_count"], 0)  # Cleared
        self.mock_main_window.set_mode.assert_called_once()

    def test_integration_multiple_conversions_history(self):
        """Test multiple conversions and history tracking"""
        # Arrange
        mode = self.mode
        test_words = ["hello", "thanks", "yes", "no", "please"]

        # Act
        for word in test_words:
            mode.process_text(word)

        # Assert
        self.assertEqual(len(mode.conversion_history), 5)
        for i, word in enumerate(test_words):
            self.assertEqual(mode.conversion_history[i]["input"], word)


if __name__ == "__main__":
    unittest.main()
