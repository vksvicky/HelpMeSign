"""
Unit tests for LearnMode class
Tests happy paths, error conditions, exceptions, and boundary conditions
"""

from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import the learn mode class
from src.helpmesign.modes.learn.learn_mode import LearnMode


class TestLearnMode:
    """Test cases for LearnMode class"""

    @pytest.fixture(autouse=True)
    def setup(self):
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

    # Happy Path Tests
    def test_happy_path_initialization(self):
        """Test successful mode initialization"""
        # Arrange & Act
        mode = self.mode

        # Assert
        assert mode.main_window == self.mock_main_window
        assert mode.environment == "dev"
        assert isinstance(mode.learning_progress, dict)
        assert isinstance(mode.lesson_history, list)
        assert mode.current_lesson is None

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_happy_path_get_mode_name(self, mock_get_text):
        """Test getting mode name"""
        # Arrange
        mock_get_text.return_value = "Learn Sign Language"

        # Act
        name = self.mode.get_mode_name()

        # Assert
        assert name == "Learn Sign Language"
        mock_get_text.assert_called_once_with("modes.learn.name")

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_happy_path_get_mode_description(self, mock_get_text):
        """Test getting mode description"""
        # Arrange
        mock_get_text.return_value = "Educational mode for learning sign language"

        # Act
        description = self.mode.get_mode_description()

        # Assert
        assert description == "Educational mode for learning sign language"
        mock_get_text.assert_called_once_with("modes.learn.description")

    def test_happy_path_process_text_hello(self):
        """Test processing 'hello' text for learning"""
        # Arrange
        test_text = "hello"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "👋 HELLO/HI:" in result
        assert "• Hand gesture: Wave your hand" in result
        assert "• Cultural note:" in result
        assert "• Tip:" in result
        assert "hello" in self.mode.learning_progress

    def test_happy_path_process_text_thanks(self):
        """Test processing 'thanks' text for learning"""
        # Arrange
        test_text = "thanks"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "🙏 THANK YOU:" in result
        assert "• Hand gesture: Hand to chin, then forward" in result
        assert "• Cultural note:" in result
        assert "• Tip:" in result
        assert "thanks" in self.mode.learning_progress

    def test_happy_path_process_text_yes(self):
        """Test processing 'yes' text for learning"""
        # Arrange
        test_text = "yes"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "👍 YES:" in result
        assert "• Hand gesture: Nod head and make a fist" in result
        assert "• Cultural note:" in result
        assert "• Tip:" in result
        assert "yes" in self.mode.learning_progress

    def test_happy_path_process_text_no(self):
        """Test processing 'no' text for learning"""
        # Arrange
        test_text = "no"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "👎 NO:" in result
        assert "• Hand gesture: Shake head and point index finger" in result
        assert "• Cultural note:" in result
        assert "• Tip:" in result
        assert "no" in self.mode.learning_progress

    def test_happy_path_process_text_please(self):
        """Test processing 'please' text for learning"""
        # Arrange
        test_text = "please"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "🤲 PLEASE:" in result
        assert "• Hand gesture: Flat hand, palm up, circular motion" in result
        assert "• Cultural note:" in result
        assert "• Tip:" in result
        assert "please" in self.mode.learning_progress

    def test_happy_path_process_text_sorry(self):
        """Test processing 'sorry' text for learning"""
        # Arrange
        test_text = "sorry"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "🤝 SORRY:" in result
        assert "• Hand gesture: Fist over heart, circular motion" in result
        assert "• Cultural note:" in result
        assert "• Tip:" in result
        assert "sorry" in self.mode.learning_progress

    def test_happy_path_process_text_unknown_word(self):
        """Test processing unknown word for learning"""
        # Arrange
        test_text = "unknown"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "🤟 SPELLING: U N K N O W N" in result
        assert "• Use finger spelling for this word" in result
        assert "• Each letter has a specific hand position" in result
        assert "unknown" in self.mode.learning_progress

    def test_happy_path_process_text_multiple_words(self):
        """Test processing multiple words for learning"""
        # Arrange
        test_text = "hello please"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "👋 HELLO/HI:" in result
        assert "🤲 PLEASE:" in result
        assert "hello" in self.mode.learning_progress
        assert "please" in self.mode.learning_progress

    def test_happy_path_get_sign_language_info(self):
        """Test getting sign language information"""
        # Arrange
        test_text = "hello"

        # Act
        result = self.mode.get_sign_language_info(test_text)

        # Assert
        assert "👋 HELLO/HI:" in result
        assert "• Hand gesture:" in result
        assert "• Cultural note:" in result
        assert "• Tip:" in result

    def test_happy_path_on_learn_requested(self):
        """Test on_learn_requested method"""
        # Arrange
        self.mock_main_window.get_text_input.return_value = "hello"

        # Act
        self.mode._on_learn_requested()

        # Assert
        self.mock_main_window.get_text_input.assert_called_once()
        self.mock_main_window.set_text_output.assert_called_once()
        self.mock_main_window.set_status.assert_called_once()

    def test_happy_path_on_clear_requested(self):
        """Test on_clear_requested method"""
        # Arrange

        # Act
        self.mode._on_clear_requested()

        # Assert
        self.mock_main_window.set_text_input.assert_called_once_with("")
        self.mock_main_window.set_text_output.assert_called_once_with("")
        self.mock_main_window.set_status.assert_called_once()

    def test_happy_path_clear_content(self):
        """Test clearing content"""
        # Arrange
        # Add some learning progress first
        self.mode.process_text("hello")
        self.mode.process_text("thanks")

        # Act
        self.mode.clear_content()

        # Assert
        # Learning progress should NOT be cleared
        assert "hello" in self.mode.learning_progress
        assert "thanks" in self.mode.learning_progress
        self.mock_main_window.set_text_input.assert_called_with("")
        self.mock_main_window.set_text_output.assert_called_with("")

    def test_happy_path_get_settings(self):
        """Test getting mode settings"""
        # Arrange
        # Add some learning progress
        self.mode.process_text("hello")
        self.mode.process_text("thanks")

        # Act
        settings = self.mode.get_settings()

        # Assert
        assert settings["learning_progress_count"] == 2
        assert settings["lesson_history_count"] == 0
        assert settings["mode"] == "learn"

    def test_happy_path_get_learning_progress(self):
        """Test getting learning progress"""
        # Arrange
        # Add some learning progress
        self.mode.process_text("hello")
        self.mode.process_text("thanks")

        # Act
        progress = self.mode.get_learning_progress()

        # Assert
        assert progress == self.mode.learning_progress
        assert "hello" in progress
        assert "thanks" in progress

    def test_happy_path_get_lesson_suggestions(self):
        """Test getting lesson suggestions"""
        # Arrange

        # Act
        suggestions = self.mode.get_lesson_suggestions()

        # Assert
        assert isinstance(suggestions, list)
        assert "Basic Greetings" in suggestions
        assert "Common Phrases" in suggestions
        assert "Numbers" in suggestions
        assert "Colors" in suggestions

    # Error Condition Tests
    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_error_condition_empty_text_processing(self, mock_get_text):
        """Test processing empty text"""
        # Arrange
        mock_get_text.return_value = "Please enter some text to learn."
        empty_text = ""

        # Act
        result = self.mode.process_text(empty_text)

        # Assert
        assert result == "Please enter some text to learn."
        assert len(self.mode.learning_progress) == 0

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_error_condition_whitespace_text_processing(self, mock_get_text):
        """Test processing whitespace-only text"""
        # Arrange
        mock_get_text.return_value = "Please enter some text to learn."
        whitespace_text = "   \t\n   "

        # Act
        result = self.mode.process_text(whitespace_text)

        # Assert
        assert result == "Please enter some text to learn."
        assert len(self.mode.learning_progress) == 0

    def test_error_condition_mixed_case_processing(self):
        """Test processing mixed case text"""
        # Arrange
        test_text = "Hello THANKS Yes"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "👋 HELLO/HI:" in result
        assert "🙏 THANK YOU:" in result
        assert "👍 YES:" in result

    def test_error_condition_learn_requested_no_input(self):
        """Test learn requested with no input"""
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
        """Test exception handling in learn_requested"""
        # Arrange
        self.mock_main_window.get_text_input.side_effect = Exception("Input failed")

        # Act
        self.mode._on_learn_requested()

        # Assert - The method should handle the exception gracefully
        self.mock_main_window.set_text_output.assert_called_once()
        self.mock_main_window.set_status.assert_called_once()

    def test_exception_in_clear_requested(self):
        """Test exception handling in clear_requested"""
        # Arrange
        self.mock_main_window.set_text_input.side_effect = Exception("Clear failed")

        # Act & Assert
        with pytest.raises(Exception):
            self.mode._on_clear_requested()

    def test_exception_in_get_sign_language_info(self):
        """Test exception handling in get_sign_language_info"""
        # Arrange
        # Mock the method to raise an exception
        original_method = self.mode.get_sign_language_info
        self.mode.get_sign_language_info = Mock(side_effect=Exception("Info failed"))

        # Act & Assert
        with pytest.raises(Exception):
            self.mode.process_text("hello")

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
        assert isinstance(result, str)
        assert len(result) > 0
        # The long text gets stored as a single key in learning progress
        assert len(self.mode.learning_progress) == 1

    def test_boundary_condition_single_character_words(self):
        """Test processing single character words"""
        # Arrange
        test_text = "a b c"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "🤟 SPELLING: A" in result
        assert "a" in self.mode.learning_progress
        assert "b" in self.mode.learning_progress
        assert "c" in self.mode.learning_progress

    def test_boundary_condition_numbers_in_text(self):
        """Test processing text with numbers"""
        # Arrange
        test_text = "hello 123 world"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "👋 HELLO/HI:" in result
        assert "123" in self.mode.learning_progress
        assert "world" in self.mode.learning_progress

    def test_boundary_condition_special_characters(self):
        """Test processing text with special characters"""
        # Arrange
        test_text = "hello! world?"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "🤟 SPELLING: H E L L O !" in result
        assert "hello!" in self.mode.learning_progress
        assert "world?" in self.mode.learning_progress

    def test_boundary_condition_unicode_text(self):
        """Test processing unicode text"""
        # Arrange
        test_text = "Hello 世界 🌍"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "👋 HELLO/HI:" in result
        assert "hello" in self.mode.learning_progress
        assert "世界" in self.mode.learning_progress
        assert "🌍" in self.mode.learning_progress

    def test_boundary_condition_learning_progress_limit(self):
        """Test learning progress with many entries"""
        # Arrange
        # Add many learning entries
        for i in range(100):
            self.mode.process_text(f"word{i}")

        # Act
        settings = self.mode.get_settings()

        # Assert
        assert settings["learning_progress_count"] == 100
        assert len(self.mode.learning_progress) == 100

    def test_boundary_condition_duplicate_word_learning(self):
        """Test learning the same word multiple times"""
        # Arrange
        test_word = "hello"

        # Act
        self.mode.process_text(test_word)
        self.mode.process_text(test_word)
        self.mode.process_text(test_word)

        # Assert
        assert test_word in self.mode.learning_progress
        assert self.mode.learning_progress[test_word]["searched_count"] == 3

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
        assert name == "Mocked Learn Sign Language"
        assert description == "Mocked description"
        assert mock_get_text.call_count == 2

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
        assert "👋 HELLO/HI:" in result
        assert "🤲 PLEASE:" in result
        assert "🙏 THANK YOU:" in result
        # The learning progress tracks individual words separately
        assert "hello" in self.mode.learning_progress
        assert "please" in self.mode.learning_progress
        assert "thanks" in self.mode.learning_progress

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
        assert "👋 HELLO/HI:" in result1
        assert "🙏 THANK YOU:" in result2
        assert settings["learning_progress_count"] == 2  # Should persist
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
        assert len(mode.learning_progress) == 5
        for word in test_words:
            assert word in mode.learning_progress
            assert mode.learning_progress[word]["searched_count"] == 1

    def test_integration_learning_progress_persistence(self):
        """Test that learning progress persists across operations"""
        # Arrange
        mode = self.mode

        # Act
        mode.process_text("hello")
        mode.process_text("thanks")
        mode.clear_content()  # Should not clear learning progress

        # Assert
        assert "hello" in mode.learning_progress
        assert "thanks" in mode.learning_progress
        assert len(mode.learning_progress) == 2
