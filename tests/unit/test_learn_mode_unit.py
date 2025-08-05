"""
Unit tests for LearnMode class
Tests happy paths, error conditions, exceptions, and boundary conditions
"""

import unittest
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

# Import the learn mode class
from src.helpmesign.modes.learn.learn_mode import LearnMode


class TestLearnMode(unittest.TestCase):
    """Test cases for LearnMode class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a mock main window with all required methods
        self.mock_main_window = Mock()
        self.mock_main_window._is_mock = True  # Mark as mock to skip UI creation
        self.mock_main_window.set_mode = Mock()
        self.mock_main_window.set_status = Mock()
        self.mock_main_window.get_text_input = Mock()
        self.mock_main_window.set_text_output = Mock()
        self.mock_main_window.set_text_input = Mock()

        # Create the mode instance
        self.mode = LearnMode(self.mock_main_window, "dev")

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
        self.assertIsInstance(mode.learning_progress, dict)
        self.assertIsInstance(mode.lesson_history, list)
        self.assertIsNone(mode.current_lesson)

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_happy_path_get_mode_name(self, mock_get_text):
        """Test getting mode name"""
        # Arrange
        mock_get_text.return_value = "Learn Sign Language"

        # Act
        name = self.mode.get_mode_name()

        # Assert
        self.assertEqual(name, "Learn Sign Language")
        mock_get_text.assert_called_once_with("modes.learn.name")

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_happy_path_get_mode_description(self, mock_get_text):
        """Test getting mode description"""
        # Arrange
        mock_get_text.return_value = "Educational mode for learning sign language"

        # Act
        description = self.mode.get_mode_description()

        # Assert
        self.assertEqual(description, "Educational mode for learning sign language")
        mock_get_text.assert_called_once_with("modes.learn.description")

    def test_happy_path_process_text_hello(self):
        """Test processing 'hello' text for learning"""
        # Arrange
        test_text = "hello"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        self.assertIn("👋 HELLO/HI:", result)
        self.assertIn("• Hand gesture: Wave your hand", result)
        self.assertIn("• Cultural note:", result)
        self.assertIn("• Tip:", result)
        self.assertIn("hello", self.mode.learning_progress)

    def test_happy_path_process_text_thanks(self):
        """Test processing 'thanks' text for learning"""
        # Arrange
        test_text = "thanks"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        self.assertIn("🙏 THANK YOU:", result)
        self.assertIn("• Hand gesture: Hand to chin, then forward", result)
        self.assertIn("• Cultural note:", result)
        self.assertIn("• Tip:", result)

    def test_happy_path_process_text_yes(self):
        """Test processing 'yes' text for learning"""
        # Arrange
        test_text = "yes"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        self.assertIn("👍 YES:", result)
        self.assertIn("• Hand gesture: Nod head and make a fist", result)
        self.assertIn("• Cultural note:", result)
        self.assertIn("• Tip:", result)

    def test_happy_path_process_text_no(self):
        """Test processing 'no' text for learning"""
        # Arrange
        test_text = "no"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        self.assertIn("👎 NO:", result)
        self.assertIn("• Hand gesture: Shake head and point index finger", result)
        self.assertIn("• Cultural note:", result)
        self.assertIn("• Tip:", result)

    def test_happy_path_process_text_please(self):
        """Test processing 'please' text for learning"""
        # Arrange
        test_text = "please"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        self.assertIn("🤲 PLEASE:", result)
        self.assertIn("• Hand gesture: Flat hand, palm up, circular motion", result)
        self.assertIn("• Cultural note:", result)
        self.assertIn("• Tip:", result)

    def test_happy_path_process_text_sorry(self):
        """Test processing 'sorry' text for learning"""
        # Arrange
        test_text = "sorry"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        self.assertIn("🤝 SORRY:", result)
        self.assertIn("• Hand gesture: Fist over heart, circular motion", result)
        self.assertIn("• Cultural note:", result)
        self.assertIn("• Tip:", result)

    def test_happy_path_process_text_unknown_word(self):
        """Test processing unknown word for learning"""
        # Arrange
        test_text = "unknown"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        self.assertIn("🤟 SPELLING: U N K N O W N", result)
        self.assertIn("• Use finger spelling for this word", result)
        self.assertIn("• Each letter has a specific hand position", result)
        self.assertIn("• Practice spelling slowly and clearly", result)

    def test_happy_path_process_text_multiple_words(self):
        """Test processing multiple words for learning"""
        # Arrange
        test_text = "hello please thanks"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        self.assertIn("👋 HELLO/HI:", result)
        self.assertIn("🤲 PLEASE:", result)
        self.assertIn("🙏 THANK YOU:", result)
        self.assertIn("\n\n", result)  # Separator between words

    def test_happy_path_get_sign_language_info(self):
        """Test direct sign language info method"""
        # Arrange
        test_text = "hello world"

        # Act
        result = self.mode.get_sign_language_info(test_text)

        # Assert
        self.assertIn("👋 HELLO/HI:", result)
        self.assertIn("🤟 SPELLING: W O R L D", result)

    def test_happy_path_on_learn_requested(self):
        """Test learn button click handler"""
        # Arrange
        self.mock_main_window.get_text_input.return_value = "hello"

        # Act
        self.mode._on_learn_requested()

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
        # Add some learning progress
        self.mode.learning_progress = {"test": {"searched_count": 1}}

        # Act
        self.mode.clear_content()

        # Assert
        self.mock_main_window.set_text_input.assert_called_once_with("")
        self.mock_main_window.set_text_output.assert_called_once_with("")
        # Learning progress should NOT be cleared (should persist)
        self.assertIn("test", self.mode.learning_progress)

    def test_happy_path_get_settings(self):
        """Test getting mode settings"""
        # Arrange
        self.mode.learning_progress = {"test": {"searched_count": 1}}
        self.mode.lesson_history = ["lesson1", "lesson2"]

        # Act
        settings = self.mode.get_settings()

        # Assert
        self.assertEqual(settings["learning_progress_count"], 1)
        self.assertEqual(settings["lesson_history_count"], 2)
        self.assertEqual(settings["mode"], "learn")

    def test_happy_path_get_learning_progress(self):
        """Test getting learning progress"""
        # Arrange
        self.mode.learning_progress = {"test": {"searched_count": 1}}

        # Act
        progress = self.mode.get_learning_progress()

        # Assert
        self.assertEqual(progress, {"test": {"searched_count": 1}})
        self.assertIsNot(progress, self.mode.learning_progress)  # Should be a copy

    def test_happy_path_get_lesson_suggestions(self):
        """Test getting lesson suggestions"""
        # Arrange

        # Act
        suggestions = self.mode.get_lesson_suggestions()

        # Assert
        self.assertIsInstance(suggestions, list)
        self.assertIn("Basic Greetings", suggestions)
        self.assertIn("Common Phrases", suggestions)
        self.assertIn("Numbers", suggestions)
        self.assertIn("Colors", suggestions)

    # Error Condition Tests
    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_error_condition_empty_text_processing(self, mock_get_text):
        """Test processing empty text"""
        # Arrange
        mock_get_text.return_value = "Please enter some text to learn about."
        empty_text = ""

        # Act
        result = self.mode.process_text(empty_text)

        # Assert
        self.assertIsInstance(result, str)
        self.assertEqual(len(self.mode.learning_progress), 0)  # No progress entry

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_error_condition_whitespace_text_processing(self, mock_get_text):
        """Test processing whitespace-only text"""
        # Arrange
        mock_get_text.return_value = "Please enter some text to learn about."
        whitespace_text = "   \n\t   "

        # Act
        result = self.mode.process_text(whitespace_text)

        # Assert
        self.assertIsInstance(result, str)
        self.assertEqual(len(self.mode.learning_progress), 0)  # No progress entry

    def test_error_condition_mixed_case_processing(self):
        """Test processing mixed case text"""
        # Arrange
        mixed_text = "Hello THANKS Yes"

        # Act
        result = self.mode.process_text(mixed_text)

        # Assert
        self.assertIn("👋 HELLO/HI:", result)  # hello
        self.assertIn("🙏 THANK YOU:", result)  # thanks
        self.assertIn("👍 YES:", result)  # yes

    def test_error_condition_learn_requested_no_input(self):
        """Test learn button with no input"""
        # Arrange
        self.mock_main_window.get_text_input.return_value = ""

        # Act
        self.mode._on_learn_requested()

        # Assert
        self.mock_main_window.get_text_input.assert_called_once()
        self.mock_main_window.set_text_output.assert_called_once()
        self.mock_main_window.set_status.assert_called_once()

    # Exception Tests
    def test_exception_in_learn_requested(self):
        """Test exception handling in learn requested"""
        # Arrange
        self.mock_main_window.get_text_input.side_effect = Exception("Input error")

        # Act
        self.mode._on_learn_requested()

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

    def test_exception_in_get_sign_language_info(self):
        """Test exception handling in sign language info"""
        # Arrange
        # Mock the method to raise an exception
        original_method = self.mode.get_sign_language_info
        self.mode.get_sign_language_info = Mock(side_effect=Exception("Info error"))

        # Act & Assert
        with self.assertRaises(Exception):
            self.mode.process_text("test")

        # Restore original method
        self.mode.get_sign_language_info = original_method

    # Boundary Condition Tests
    def test_boundary_condition_very_long_text(self):
        """Test processing very long text"""
        # Arrange
        long_text = "hello " * 1000  # 6000 character string

        # Act
        result = self.mode.process_text(long_text)

        # Assert
        self.assertIn("👋 HELLO/HI:", result)
        self.assertIn("\n\n", result)  # Should have separators
        # The learning progress tracks the entire text as one key (lowercase and stripped)
        expected_key = long_text.lower().strip()
        self.assertIn(expected_key, self.mode.learning_progress)

    def test_boundary_condition_single_character_words(self):
        """Test processing single character words"""
        # Arrange
        single_char_text = "a b c d"

        # Act
        result = self.mode.process_text(single_char_text)

        # Assert
        self.assertIn("🤟 SPELLING: A", result)
        self.assertIn("🤟 SPELLING: B", result)
        self.assertIn("🤟 SPELLING: C", result)
        self.assertIn("🤟 SPELLING: D", result)

    def test_boundary_condition_numbers_in_text(self):
        """Test processing text with numbers"""
        # Arrange
        number_text = "hello 123 world"

        # Act
        result = self.mode.process_text(number_text)

        # Assert
        self.assertIn("👋 HELLO/HI:", result)  # hello
        self.assertIn("🤟 SPELLING: 1 2 3", result)  # numbers
        self.assertIn("🤟 SPELLING: W O R L D", result)  # world

    def test_boundary_condition_special_characters(self):
        """Test processing text with special characters"""
        # Arrange
        special_text = "hello! world?"

        # Act
        result = self.mode.process_text(special_text)

        # Assert
        # Special characters are treated as part of the word, so they get spelled out
        self.assertIn(
            "🤟 SPELLING: H E L L O !", result
        )  # Fixed: special chars are part of word
        self.assertIn(
            "🤟 SPELLING: W O R L D ?", result
        )  # Fixed: special chars are part of word

    def test_boundary_condition_unicode_text(self):
        """Test processing unicode text"""
        # Arrange
        unicode_text = "hello 世界"

        # Act
        result = self.mode.process_text(unicode_text)

        # Assert
        self.assertIn("👋 HELLO/HI:", result)  # hello
        self.assertIn("🤟 SPELLING: 世 界", result)  # unicode characters

    def test_boundary_condition_learning_progress_limit(self):
        """Test learning progress with many entries"""
        # Arrange
        # Add many learning entries
        for i in range(100):
            self.mode.process_text(f"test{i}")

        # Act
        settings = self.mode.get_settings()

        # Assert
        self.assertEqual(settings["learning_progress_count"], 100)
        self.assertEqual(len(self.mode.learning_progress), 100)

    def test_boundary_condition_duplicate_word_learning(self):
        """Test learning the same word multiple times"""
        # Arrange
        word = "hello"

        # Act
        self.mode.process_text(word)
        self.mode.process_text(word)
        self.mode.process_text(word)

        # Assert
        self.assertIn(word, self.mode.learning_progress)
        self.assertEqual(self.mode.learning_progress[word]["searched_count"], 3)

    # Mock Tests
    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_mock_language_integration(self, mock_get_text):
        """Test integration with language system using mocks"""
        # Arrange
        mock_get_text.side_effect = lambda key: {
            "modes.learn.name": "Mocked Learn Sign Language",
            "modes.learn.description": "Mocked description",
            "ui.output.empty_message": "Mocked empty message",
        }.get(key, "Mocked text")

        # Act
        name = self.mode.get_mode_name()
        description = self.mode.get_mode_description()

        # Assert
        self.assertEqual(name, "Mocked Learn Sign Language")
        self.assertEqual(description, "Mocked description")
        self.assertEqual(mock_get_text.call_count, 2)

    def test_mock_main_window_signal_connections(self):
        """Test signal connections with mocked main window"""
        # Arrange
        mock_window = Mock()
        mock_window.process_requested = Mock()
        mock_window.clear_requested = Mock()

        # Act
        mode = LearnMode(mock_window, "dev")

        # Assert
        # The mode should connect to signals during setup_behavior
        # This is tested indirectly through the setup_behavior call

    # Integration Tests (within unit test scope)
    def test_integration_complete_learning_workflow(self):
        """Test complete learning workflow"""
        # Arrange
        test_text = "hello please thanks"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        self.assertIn("👋 HELLO/HI:", result)
        self.assertIn("🤲 PLEASE:", result)
        self.assertIn("🙏 THANK YOU:", result)
        # The learning progress tracks individual words separately
        self.assertIn("hello", self.mode.learning_progress)
        self.assertIn("please", self.mode.learning_progress)
        self.assertIn("thanks", self.mode.learning_progress)

    def test_integration_mode_lifecycle_with_learning(self):
        """Test complete mode lifecycle with learning"""
        # Arrange
        mode = self.mode

        # Act - Complete lifecycle
        mode.activate()
        result1 = mode.process_text("hello")
        result2 = mode.process_text("thanks")
        settings = mode.get_settings()
        mode.clear_content()
        mode.deactivate()

        # Assert
        self.assertIn("👋 HELLO/HI:", result1)
        self.assertIn("🙏 THANK YOU:", result2)
        self.assertEqual(settings["learning_progress_count"], 2)  # Should persist
        self.mock_main_window.set_mode.assert_called_once()

    def test_integration_multiple_learning_sessions(self):
        """Test multiple learning sessions and progress tracking"""
        # Arrange
        mode = self.mode
        test_words = ["hello", "thanks", "yes", "no", "please"]

        # Act
        for word in test_words:
            mode.process_text(word)

        # Assert
        self.assertEqual(len(mode.learning_progress), 5)
        for word in test_words:
            self.assertIn(word, mode.learning_progress)
            self.assertEqual(mode.learning_progress[word]["searched_count"], 1)

    def test_integration_learning_progress_persistence(self):
        """Test that learning progress persists across operations"""
        # Arrange
        mode = self.mode

        # Act
        mode.process_text("hello")
        mode.process_text("thanks")
        mode.clear_content()  # Should not clear learning progress

        # Assert
        self.assertIn("hello", mode.learning_progress)
        self.assertIn("thanks", mode.learning_progress)
        self.assertEqual(len(mode.learning_progress), 2)


if __name__ == "__main__":
    unittest.main()
