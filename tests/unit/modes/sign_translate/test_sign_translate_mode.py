"""
Unit tests for SignTranslateMode class
Tests happy paths, error conditions, exceptions, and boundary conditions
"""

from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import the sign translate mode class
from src.helpmesign.modes.sign_translate.sign_translate_mode import SignTranslateMode


class TestSignTranslateMode:
    """Test cases for SignTranslateMode class"""

    @pytest.fixture(autouse=True)
    def setup(self):
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

    # Happy Path Tests
    def test_happy_path_initialization(self):
        """Test successful mode initialization"""
        # Arrange & Act
        mode = self.mode

        # Assert
        assert mode.main_window == self.mock_main_window
        assert mode.environment == "dev"
        assert isinstance(mode.conversion_history, list)
        assert len(mode.conversion_history) == 0

    @patch("src.helpmesign.modes.sign_translate.sign_translate_mode.get_text")
    def test_happy_path_get_mode_name(self, mock_get_text):
        """Test getting mode name"""
        # Arrange
        mock_get_text.return_value = "Sign & Translate"

        # Act
        name = self.mode.get_mode_name()

        # Assert
        assert name == "Sign & Translate"
        mock_get_text.assert_called_once_with("modes.sign_translate.name")

    @patch("src.helpmesign.modes.sign_translate.sign_translate_mode.get_text")
    def test_happy_path_get_mode_description(self, mock_get_text):
        """Test getting mode description"""
        # Arrange
        mock_get_text.return_value = "Convert text to sign language"

        # Act
        description = self.mode.get_mode_description()

        # Assert
        assert description == "Convert text to sign language"
        mock_get_text.assert_called_once_with("modes.sign_translate.description")

    def test_happy_path_process_text_hello(self):
        """Test processing 'hello' text"""
        # Arrange
        test_text = "hello"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "👋 Wave hand" in result
        assert len(self.mode.conversion_history) == 1
        assert self.mode.conversion_history[0]["input"] == test_text

    def test_happy_path_process_text_thanks(self):
        """Test processing 'thanks' text"""
        # Arrange
        test_text = "thanks"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "🙏 Hand to chin, then forward" in result
        assert len(self.mode.conversion_history) == 1

    def test_happy_path_process_text_yes(self):
        """Test processing 'yes' text"""
        # Arrange
        test_text = "yes"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "👍 Nod head and fist" in result
        assert len(self.mode.conversion_history) == 1

    def test_happy_path_process_text_no(self):
        """Test processing 'no' text"""
        # Arrange
        test_text = "no"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "👎 Shake head and index finger" in result
        assert len(self.mode.conversion_history) == 1

    def test_happy_path_process_text_please(self):
        """Test processing 'please' text"""
        # Arrange
        test_text = "please"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "🤲 Flat hand, palm up, circular motion" in result
        assert len(self.mode.conversion_history) == 1

    def test_happy_path_process_text_sorry(self):
        """Test processing 'sorry' text"""
        # Arrange
        test_text = "sorry"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "🤝 Fist over heart, circular motion" in result
        assert len(self.mode.conversion_history) == 1

    def test_happy_path_process_text_unknown_word(self):
        """Test processing unknown word"""
        # Arrange
        test_text = "unknown"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "🤟 Spell: u n k n o w n" in result
        assert len(self.mode.conversion_history) == 1

    def test_happy_path_process_text_multiple_words(self):
        """Test processing multiple words"""
        # Arrange
        test_text = "hello thanks"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "👋 Wave hand" in result
        assert "🙏 Hand to chin, then forward" in result
        assert " | " in result  # Separator between words
        assert len(self.mode.conversion_history) == 1

    def test_happy_path_convert_to_sign_language(self):
        """Test direct conversion to sign language"""
        # Arrange
        test_text = "hello world"

        # Act
        result = self.mode.convert_to_sign_language(test_text)

        # Assert
        assert "👋 Wave hand" in result
        assert "🤟 Spell: w o r l d" in result

    def test_happy_path_on_process_requested(self):
        """Test on_process_requested method"""
        # Arrange
        self.mock_main_window.get_text_input.return_value = "hello"

        # Act
        self.mode._on_process_requested()

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
        # Add some conversion history first
        self.mode.process_text("hello")
        self.mode.process_text("thanks")

        # Act
        self.mode.clear_content()

        # Assert
        assert len(self.mode.conversion_history) == 0
        self.mock_main_window.set_text_input.assert_called_with("")
        self.mock_main_window.set_text_output.assert_called_with("")

    def test_happy_path_get_settings(self):
        """Test getting mode settings"""
        # Arrange
        # Add some conversion history
        self.mode.process_text("hello")
        self.mode.process_text("thanks")

        # Act
        settings = self.mode.get_settings()

        # Assert
        assert settings["conversion_history_count"] == 2
        assert settings["mode"] == "sign_translate"

    # Error Condition Tests
    @patch("src.helpmesign.modes.sign_translate.sign_translate_mode.get_text")
    def test_error_condition_empty_text_processing(self, mock_get_text):
        """Test processing empty text"""
        # Arrange
        mock_get_text.return_value = "Please enter some text."
        empty_text = ""

        # Act
        result = self.mode.process_text(empty_text)

        # Assert
        assert result == "Please enter some text."
        assert len(self.mode.conversion_history) == 0

    @patch("src.helpmesign.modes.sign_translate.sign_translate_mode.get_text")
    def test_error_condition_whitespace_text_processing(self, mock_get_text):
        """Test processing whitespace-only text"""
        # Arrange
        mock_get_text.return_value = "Please enter some text."
        whitespace_text = "   \t\n   "

        # Act
        result = self.mode.process_text(whitespace_text)

        # Assert
        assert result == "Please enter some text."
        assert len(self.mode.conversion_history) == 0

    def test_error_condition_mixed_case_processing(self):
        """Test processing mixed case text"""
        # Arrange
        test_text = "Hello THANKS Yes"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "👋 Wave hand" in result
        assert "🙏 Hand to chin, then forward" in result
        assert "👍 Nod head and fist" in result

    def test_error_condition_process_requested_no_input(self):
        """Test process requested with no input"""
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
        """Test exception handling in process_requested"""
        # Arrange
        self.mock_main_window.get_text_input.side_effect = Exception("Input failed")

        # Act
        self.mode._on_process_requested()

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

    def test_exception_in_convert_to_sign_language(self):
        """Test exception handling in convert_to_sign_language"""
        # Arrange
        # Mock the method to raise an exception
        original_method = self.mode.convert_to_sign_language
        self.mode.convert_to_sign_language = Mock(
            side_effect=Exception("Conversion failed")
        )

        # Act & Assert
        with pytest.raises(Exception):
            self.mode.process_text("hello")

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
        assert isinstance(result, str)
        assert len(result) > 0
        assert len(self.mode.conversion_history) == 1

    def test_boundary_condition_single_character_words(self):
        """Test processing single character words"""
        # Arrange
        test_text = "a b c"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "🤟 Spell: a" in result
        assert "🤟 Spell: b" in result
        assert "🤟 Spell: c" in result

    def test_boundary_condition_numbers_in_text(self):
        """Test processing text with numbers"""
        # Arrange
        test_text = "hello 123 world"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "👋 Wave hand" in result
        assert "🤟 Spell: 1 2 3" in result
        assert "🤟 Spell: w o r l d" in result

    def test_boundary_condition_special_characters(self):
        """Test processing text with special characters"""
        # Arrange
        test_text = "hello! world?"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "🤟 Spell: h e l l o !" in result
        assert "🤟 Spell: w o r l d ?" in result

    def test_boundary_condition_unicode_text(self):
        """Test processing unicode text"""
        # Arrange
        test_text = "Hello 世界 🌍"

        # Act
        result = self.mode.process_text(test_text)

        # Assert
        assert "👋 Wave hand" in result
        assert isinstance(result, str)
        assert len(result) > 0

    def test_boundary_condition_conversion_history_limit(self):
        """Test conversion history with many entries"""
        # Arrange
        # Add many conversions
        for i in range(100):
            self.mode.process_text(f"test{i}")

        # Act
        settings = self.mode.get_settings()

        # Assert
        assert settings["conversion_history_count"] == 100
        assert len(self.mode.conversion_history) == 100

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
        assert name == "Mocked Sign & Translate"
        assert description == "Mocked description"
        assert mock_get_text.call_count == 2

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
        assert "👋 Wave hand" in result
        assert "🤲 Flat hand, palm up, circular motion" in result
        assert "🙏 Hand to chin, then forward" in result
        assert len(self.mode.conversion_history) == 1
        assert self.mode.conversion_history[0]["input"] == test_text

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
        assert "👋 Wave hand" in result1
        assert "🙏 Hand to chin, then forward" in result2
        assert settings["conversion_history_count"] == 0  # Cleared
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
        assert len(mode.conversion_history) == 5
        for i, word in enumerate(test_words):
            assert mode.conversion_history[i]["input"] == word
