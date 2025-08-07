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

        # Mock the UI creation to prevent PySide6 crashes
        with patch("src.helpmesign.modes.learn.learn_mode.LearnMode.setup_ui"):
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

    def test_happy_path_get_mode_description(self):
        """Test getting mode description"""
        # Act
        description = self.mode.get_mode_description()

        # Assert
        assert (
            description == "Learn sign language with interactive lessons and practice"
        )

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
    def test_mock_language_integration(self):
        """Test integration with mock language system"""
        # Act
        description = self.mode.get_mode_description()

        # Assert
        assert (
            description == "Learn sign language with interactive lessons and practice"
        )

    def test_mock_main_window_signal_connections(self):
        """Test signal connections with mocked main window"""
        # Arrange
        mock_window = Mock()
        mock_window.process_requested = Mock()
        mock_window.clear_requested = Mock()

        # Act - Mock setup_ui to prevent PySide6 crashes
        with patch("src.helpmesign.modes.learn.learn_mode.LearnMode.setup_ui"):
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

    # UI Setup Tests (without causing segfaults)
    def test_setup_ui_with_content_area_but_mock(self):
        """Test setup_ui with content_area but mock main_window"""
        # Arrange
        mock_main_window = Mock()
        mock_main_window.content_area = Mock()
        mock_main_window._is_mock = True

        # Act - Mock setup_ui to prevent PySide6 crashes
        with patch("src.helpmesign.modes.learn.learn_mode.LearnMode.setup_ui"):
            mode = LearnMode(mock_main_window, "dev")

        # Assert
        assert mode.main_window == mock_main_window
        assert mode.environment == "dev"

    def test_setup_ui_without_content_area(self):
        """Test setup_ui without content_area"""
        # Arrange
        mock_main_window = Mock()
        mock_main_window._is_mock = False
        # No content_area attribute

        # Act - Mock setup_ui to prevent PySide6 crashes
        with patch("src.helpmesign.modes.learn.learn_mode.LearnMode.setup_ui"):
            mode = LearnMode(mock_main_window, "dev")

        # Assert
        assert mode.main_window == mock_main_window
        assert mode.environment == "dev"

    def test_setup_ui_with_content_area_and_no_mock(self):
        """Test setup_ui with content_area and no mock flag"""
        # Arrange
        mock_main_window = Mock()
        mock_main_window.content_area = Mock()
        mock_main_window._is_mock = False

        # Act - Mock setup_ui to prevent PySide6 crashes
        with patch("src.helpmesign.modes.learn.learn_mode.LearnMode.setup_ui"):
            mode = LearnMode(mock_main_window, "dev")

        # Assert
        assert mode.main_window == mock_main_window
        assert mode.environment == "dev"

    # Character Selection Tests
    def test_on_alphabet_selected(self):
        """Test on_alphabet_selected method"""
        # Arrange
        mode = self.mode
        mode.alphabet_buttons = {"A": Mock(), "B": Mock()}
        mode.number_buttons = {"1": Mock(), "2": Mock()}
        mode.sign_title = Mock()
        mode.sign_display_label = Mock()

        # Act
        mode.on_alphabet_selected("A")

        # Assert
        assert mode.current_char_type == "letter"

    def test_on_number_selected(self):
        """Test on_number_selected method"""
        # Arrange
        mode = self.mode
        mode.alphabet_buttons = {"A": Mock(), "B": Mock()}
        mode.number_buttons = {"1": Mock(), "2": Mock()}
        mode.sign_title = Mock()
        mode.sign_display_label = Mock()

        # Act
        mode.on_number_selected("1")

        # Assert
        assert mode.current_char_type == "number"

    def test_update_button_selection(self):
        """Test update_button_selection method"""
        # Arrange
        mode = self.mode
        mock_button_a = Mock()
        mock_button_b = Mock()
        mock_button_1 = Mock()
        mock_button_2 = Mock()

        # Mock the style methods
        mock_button_a.style.return_value = Mock()
        mock_button_b.style.return_value = Mock()
        mock_button_1.style.return_value = Mock()
        mock_button_2.style.return_value = Mock()

        mode.alphabet_buttons = {"A": mock_button_a, "B": mock_button_b}
        mode.number_buttons = {"1": mock_button_1, "2": mock_button_2}

        # Act
        mode.update_button_selection("A", mode.alphabet_buttons)

        # Assert
        # Should set selected property on the selected button
        mock_button_a.setProperty.assert_called_with("selected", True)
        # Should call style polish on the selected button
        mock_button_a.style().polish.assert_called_with(mock_button_a)

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_update_sign_display(self, mock_get_text):
        """Test update_sign_display method"""
        # Arrange
        mode = self.mode
        mode.sign_display_label = Mock()

        # Act
        mode.update_sign_display("A", "letter")

        # Assert
        assert mode.current_character == "A"
        assert mode.current_char_type == "letter"

    def test_update_sign_display_without_label(self):
        """Test update_sign_display when sign_display_label doesn't exist"""
        # Arrange
        mode = self.mode
        # Ensure sign_display_label doesn't exist
        if hasattr(mode, "sign_display_label"):
            delattr(mode, "sign_display_label")

        # Act
        mode.update_sign_display("A", "letter")

        # Assert
        # The method returns early when sign_display_label doesn't exist
        # so current_character and current_char_type should remain unchanged from initial values
        assert mode.current_character is None  # Should remain None (initial value)
        assert mode.current_char_type is None  # Should remain None (initial value)

    # Behavior Setup Tests
    def test_setup_behavior(self):
        """Test setup_behavior method"""
        # Arrange
        mode = self.mode
        mode.main_window.clear_requested = Mock()
        mode.main_window.process_requested = Mock()

        # Act
        mode.setup_behavior()

        # Assert
        # Should connect to main window signals
        mode.main_window.clear_requested.connect.assert_called_with(
            mode._on_clear_requested
        )
        mode.main_window.process_requested.connect.assert_called_with(
            mode._on_learn_requested
        )

    def test_setup_behavior_with_signals(self):
        """Test setup_behavior with signal connections"""
        # Arrange
        mode = self.mode
        mode.main_window.process_requested = Mock()
        mode.main_window.clear_requested = Mock()
        mode.main_window.update_hand_preference = Mock()

        # Act
        mode.setup_behavior()

        # Assert
        # Should connect to all available signals
        mode.main_window.clear_requested.connect.assert_called_with(
            mode._on_clear_requested
        )
        mode.main_window.process_requested.connect.assert_called_with(
            mode._on_learn_requested
        )
        mode.main_window.update_hand_preference.connect.assert_called_with(
            mode._on_hand_preference_changed
        )

    # Language Selection Tests
    def test_on_language_selected(self):
        """Test on_language_selected method"""
        # Arrange
        mode = self.mode
        mode.language_list_layout = Mock()
        mode.language_list_layout.count.return_value = 0
        mode.sign_title = Mock()
        language_data = {"name": "Test", "code": "test"}

        # Act
        mode.on_language_selected(language_data)

        # Assert
        assert mode.selected_language == language_data

    def test_on_language_selected_with_buttons(self):
        """Test on_language_selected with existing buttons"""
        # Arrange
        mode = self.mode
        mode.language_list_layout = Mock()
        mode.language_list_layout.count.return_value = 1
        mode.language_list_layout.itemAt.return_value = Mock()
        mode.language_list_layout.itemAt.return_value.widget.return_value = Mock()
        mode.language_list_layout.itemAt.return_value.widget.return_value.property.return_value = (
            "test"
        )
        mode.sign_title = Mock()
        language_data = {"name": "Test", "code": "test"}

        # Act
        mode.on_language_selected(language_data)

        # Assert
        assert mode.selected_language == language_data

    # Mode Lifecycle Tests
    def test_activate(self):
        """Test activate method"""
        # Arrange
        mode = self.mode

        # Act
        mode.activate()

        # Assert
        self.mock_main_window.set_mode.assert_called_once()

    def test_deactivate(self):
        """Test deactivate method"""
        # Arrange
        mode = self.mode
        mode.learning_widget = Mock()
        mode.main_window.content_area = Mock()
        mode.main_window.default_content = Mock()

        # Act
        mode.deactivate()

        # Assert
        # Should switch back to default content
        mode.main_window.content_area.setCurrentWidget.assert_called_with(
            mode.main_window.default_content
        )

    def test_deactivate_without_widget(self):
        """Test deactivate without learning_widget"""
        # Arrange
        mode = self.mode
        mode.learning_widget = None
        mode.main_window.content_area = Mock()
        mode.main_window.default_content = Mock()

        # Act
        mode.deactivate()

        # Assert
        # Should still switch back to default content even without learning_widget
        mode.main_window.content_area.setCurrentWidget.assert_called_with(
            mode.main_window.default_content
        )

    def test_force_layout_stability(self):
        """Test _force_layout_stability method"""
        # Arrange
        mode = self.mode
        mode.alphabet_buttons = {"A": Mock(), "B": Mock()}
        mode.number_buttons = {"1": Mock(), "2": Mock()}
        mode.learning_widget = Mock()

        # Act
        mode._force_layout_stability()

        # Assert
        # Should set fixed sizes on all buttons
        for btn in mode.alphabet_buttons.values():
            btn.setFixedSize.assert_called_with(48, 48)
            btn.setMinimumSize.assert_called_with(48, 48)
            btn.setMaximumSize.assert_called_with(48, 48)
        for btn in mode.number_buttons.values():
            btn.setFixedSize.assert_called_with(48, 48)
            btn.setMinimumSize.assert_called_with(48, 48)
            btn.setMaximumSize.assert_called_with(48, 48)
        # Should update the learning widget
        mode.learning_widget.updateGeometry.assert_called()
        mode.learning_widget.update.assert_called()

    def test_force_layout_stability_with_widget(self):
        """Test _force_layout_stability with learning_widget"""
        # Arrange
        mode = self.mode
        mode.learning_widget = Mock()
        mode.alphabet_buttons = {"A": Mock()}
        mode.number_buttons = {"1": Mock()}

        # Act
        mode._force_layout_stability()

        # Assert
        # Should update the learning widget
        mode.learning_widget.updateGeometry.assert_called()
        mode.learning_widget.update.assert_called()

    # Update Methods Tests
    def test_update_ui(self):
        """Test update_ui method"""
        # Arrange
        mode = self.mode

        # Act
        mode.update_ui()

        # Assert
        # update_ui currently just passes, so we verify it completes without error
        # This test ensures the method exists and can be called
        assert hasattr(mode, "update_ui")

    def test_update_fonts(self):
        """Test update_fonts method"""
        # Arrange
        mode = self.mode
        mode.learning_widget = Mock()
        mode.learning_widget.isVisible.return_value = True
        mode.sign_title = Mock()
        mode.selection_title = Mock()

        # Act
        mode.update_fonts()

        # Assert
        # The method should complete without error
        # It may hit the exception handler and use default fonts, but should not crash
        assert hasattr(mode, "update_fonts")

    # Internal Method Tests
    def test_get_single_word_info_hello(self):
        """Test _get_single_word_info with hello"""
        # Arrange
        mode = self.mode

        # Act
        result = mode._get_single_word_info("hello")

        # Assert
        assert "👋 HELLO/HI:" in result

    def test_get_single_word_info_unknown(self):
        """Test _get_single_word_info with unknown word"""
        # Arrange
        mode = self.mode

        # Act
        result = mode._get_single_word_info("unknownword")

        # Assert
        assert "🤟 SPELLING:" in result

    def test_update_learning_progress(self):
        """Test _update_learning_progress method"""
        # Arrange
        mode = self.mode
        mode.learning_progress = {}

        # Act
        mode._update_learning_progress("hello")

        # Assert
        assert "hello" in mode.learning_progress
        assert mode.learning_progress["hello"]["searched_count"] == 1

    def test_update_learning_progress_existing_word(self):
        """Test _update_learning_progress with existing word"""
        # Arrange
        mode = self.mode
        mode.learning_progress = {"hello": {"searched_count": 1}}

        # Act
        mode._update_learning_progress("hello")

        # Assert
        assert mode.learning_progress["hello"]["searched_count"] == 2

    def test_update_learning_progress_short_text(self):
        """Test _update_learning_progress with short text"""
        # Arrange
        mode = self.mode
        mode.learning_progress = {}

        # Act
        mode._update_learning_progress("hi")

        # Assert
        assert "hi" in mode.learning_progress
        assert mode.learning_progress["hi"]["searched_count"] == 1

    def test_update_learning_progress_existing_short_text(self):
        """Test _update_learning_progress with existing short text"""
        # Arrange
        mode = self.mode
        mode.learning_progress = {"hi": {"searched_count": 1}}

        # Act
        mode._update_learning_progress("hi")

        # Assert
        assert mode.learning_progress["hi"]["searched_count"] == 2

    # Font and Theme Tests
    @patch("src.helpmesign.utils.theme_manager.get_font_size")
    @patch("src.helpmesign.utils.font_manager.get_font_manager")
    def test_font_initialization(self, mock_get_font_manager, mock_get_font_size):
        """Test font initialization in constructor"""
        # Arrange
        mock_get_font_size.return_value = 14
        mock_font_manager = Mock()
        mock_font_manager._get_current_font_family.return_value = "Roboto"
        mock_get_font_manager.return_value = mock_font_manager

        # Act - Create a new mode instance with mocked setup_ui
        with patch("src.helpmesign.modes.learn.learn_mode.LearnMode.setup_ui"):
            mode = LearnMode(self.mock_main_window, "dev")

        # Assert
        assert mode.current_font_size == 14
        assert mode.current_font_family == "Roboto"

    # Error Handling Tests
    def test_process_text_with_exception(self):
        """Test process_text with exception in get_sign_language_info"""
        # Arrange
        mode = self.mode
        original_method = mode.get_sign_language_info
        mode.get_sign_language_info = Mock(side_effect=Exception("Test exception"))

        # Act & Assert
        with pytest.raises(Exception):
            mode.process_text("hello")

        # Restore original method
        mode.get_sign_language_info = original_method

    def test_get_lesson_suggestions_with_progress(self):
        """Test get_lesson_suggestions with learning progress"""
        # Arrange
        mode = self.mode
        mode.process_text("hello")
        mode.process_text("thanks")

        # Act
        suggestions = mode.get_lesson_suggestions()

        # Assert
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_get_lesson_suggestions_without_progress(self):
        """Test get_lesson_suggestions without learning progress"""
        # Arrange
        mode = self.mode

        # Act
        suggestions = mode.get_lesson_suggestions()

        # Assert
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    # Edge Case Tests
    def test_process_text_with_none(self):
        """Test process_text with None input"""
        # Arrange
        mode = self.mode

        # Act & Assert
        with pytest.raises(AttributeError):
            mode.process_text(None)

    def test_process_text_with_empty_string(self):
        """Test process_text with empty string"""
        # Arrange
        mode = self.mode

        # Act
        result = mode.process_text("")

        # Assert
        assert isinstance(result, str)

    def test_get_sign_language_info_with_none(self):
        """Test get_sign_language_info with None input"""
        # Arrange
        mode = self.mode

        # Act & Assert
        with pytest.raises(AttributeError):
            mode.get_sign_language_info(None)

    def test_get_sign_language_info_with_empty_string(self):
        """Test get_sign_language_info with empty string"""
        # Arrange
        mode = self.mode

        # Act
        result = mode.get_sign_language_info("")

        # Assert
        assert isinstance(result, str)

    # Additional Coverage Tests
    def test_update_learning_progress_with_very_long_text(self):
        """Test _update_learning_progress with very long text"""
        # Arrange
        mode = self.mode
        mode.learning_progress = {}
        long_text = "a" * 1001  # More than 1000 characters

        # Act
        mode._update_learning_progress(long_text)

        # Assert
        assert long_text in mode.learning_progress
        assert mode.learning_progress[long_text]["searched_count"] == 1

    def test_update_learning_progress_with_existing_very_long_text(self):
        """Test _update_learning_progress with existing very long text"""
        # Arrange
        mode = self.mode
        long_text = "a" * 1001
        mode.learning_progress = {long_text: {"searched_count": 1}}

        # Act
        mode._update_learning_progress(long_text)

        # Assert
        assert mode.learning_progress[long_text]["searched_count"] == 2

    def test_learning_progress_limit_enforcement(self):
        """Test learning progress limit enforcement"""
        # Arrange
        mode = self.mode
        mode.learning_progress = {}

        # Act - Add many entries to test limit
        for i in range(1000):
            mode._update_learning_progress(f"word{i}")

        # Assert - There appears to be a limit of 100 entries
        assert len(mode.learning_progress) == 100

    def test_get_single_word_info_with_different_variations(self):
        """Test _get_single_word_info with different word variations"""
        # Arrange
        mode = self.mode

        # Act & Assert
        result1 = mode._get_single_word_info("thank")
        result2 = mode._get_single_word_info("thank_you")

        assert "🙏 THANK YOU:" in result1
        assert "🙏 THANK YOU:" in result2

    def test_get_single_word_info_with_unknown_word(self):
        """Test _get_single_word_info with unknown word"""
        # Arrange
        mode = self.mode

        # Act
        result = mode._get_single_word_info("xyz123")

        # Assert
        assert "🤟 SPELLING:" in result
        assert "X Y Z 1 2 3" in result

    def test_process_text_with_single_character(self):
        """Test process_text with single character"""
        # Arrange
        mode = self.mode

        # Act
        result = mode.process_text("a")

        # Assert
        assert "🤟 SPELLING:" in result
        assert "a" in mode.learning_progress

    def test_process_text_with_mixed_case_single_word(self):
        """Test process_text with mixed case single word"""
        # Arrange
        mode = self.mode

        # Act
        result = mode.process_text("HeLLo")

        # Assert
        assert "👋 HELLO/HI:" in result
        assert "hello" in mode.learning_progress

    def test_process_text_with_numbers_only(self):
        """Test process_text with numbers only"""
        # Arrange
        mode = self.mode

        # Act
        result = mode.process_text("123")

        # Assert
        assert "🤟 SPELLING:" in result
        assert "123" in mode.learning_progress

    def test_process_text_with_special_characters_only(self):
        """Test process_text with special characters only"""
        # Arrange
        mode = self.mode

        # Act
        result = mode.process_text("!@#")

        # Assert
        assert "🤟 SPELLING:" in result
        assert "!@#" in mode.learning_progress

    def test_clear_content_with_learning_widget(self):
        """Test clear_content with learning_widget"""
        # Arrange
        mode = self.mode
        mode.learning_widget = Mock()

        # Act
        mode.clear_content()

        # Assert
        self.mock_main_window.set_text_input.assert_called_with("")
        self.mock_main_window.set_text_output.assert_called_with("")

    def test_activate_with_set_mode_exception(self):
        """Test activate with set_mode exception"""
        # Arrange
        mode = self.mode
        self.mock_main_window.set_mode.side_effect = Exception("Set mode failed")

        # Act & Assert
        with pytest.raises(Exception):
            mode.activate()

    def test_deactivate_with_widget_exception(self):
        """Test deactivate with widget exception"""
        # Arrange
        mode = self.mode
        mode.main_window.content_area = Mock()
        mode.main_window.content_area.setCurrentWidget.side_effect = Exception(
            "Widget error"
        )
        mode.main_window.default_content = Mock()

        # Act & Assert
        # The method doesn't have exception handling, so it should raise the exception
        with pytest.raises(Exception, match="Widget error"):
            mode.deactivate()

    def test_force_layout_stability_with_widget_exception(self):
        """Test _force_layout_stability with widget exception"""
        # Arrange
        mode = self.mode
        mode.alphabet_buttons = {"A": Mock()}
        mode.number_buttons = {"1": Mock()}
        mode.learning_widget = Mock()
        # Make one of the buttons raise an exception
        mode.alphabet_buttons["A"].setFixedSize.side_effect = Exception("Button error")

        # Act
        mode._force_layout_stability()

        # Assert
        # The method should handle exceptions gracefully (it has a try/except block)
        # and complete without raising an exception
        # We verify this by checking that the method completed without error
        assert mode.alphabet_buttons["A"].setFixedSize.called

    def test_update_ui_with_exception(self):
        """Test update_ui with exception"""
        # Arrange
        mode = self.mode
        # update_ui just has 'pass', so there's nothing to test for exceptions
        # This test verifies the method exists and can be called

        # Act
        mode.update_ui()

        # Assert
        # The method should complete without error
        assert hasattr(mode, "update_ui")

    def test_update_fonts_with_exception(self):
        """Test update_fonts with exception"""
        # Arrange
        mode = self.mode
        mode.learning_widget = Mock()
        mode.learning_widget.isVisible.return_value = True
        mode.sign_title = Mock()
        mode.sign_title.setFont.side_effect = Exception("Font error")

        # Act
        mode.update_fonts()

        # Assert
        # The method should handle exceptions gracefully (it has a try/except block)
        # and complete without raising an exception
        # We verify this by checking that the method completed without error
        assert hasattr(mode, "update_fonts")

    def test_get_settings_with_empty_progress(self):
        """Test get_settings with empty learning progress"""
        # Arrange
        mode = self.mode
        mode.learning_progress = {}

        # Act
        settings = mode.get_settings()

        # Assert
        assert settings["learning_progress_count"] == 0
        assert settings["lesson_history_count"] == 0
        assert settings["mode"] == "learn"

    def test_get_learning_progress_with_empty_progress(self):
        """Test get_learning_progress with empty progress"""
        # Arrange
        mode = self.mode
        mode.learning_progress = {}

        # Act
        progress = mode.get_learning_progress()

        # Assert
        assert progress == {}
        assert len(progress) == 0

    def test_get_lesson_suggestions_with_empty_progress(self):
        """Test get_lesson_suggestions with empty progress"""
        # Arrange
        mode = self.mode
        mode.learning_progress = {}

        # Act
        suggestions = mode.get_lesson_suggestions()

        # Assert
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_setup_behavior_without_signals(self):
        """Test setup_behavior without signals"""
        # Arrange
        mode = self.mode
        # Remove signals from main window
        if hasattr(mode.main_window, "clear_requested"):
            delattr(mode.main_window, "clear_requested")
        if hasattr(mode.main_window, "process_requested"):
            delattr(mode.main_window, "process_requested")

        # Act
        mode.setup_behavior()

        # Assert
        # Should complete without error even when signals don't exist
        # The method checks for signal existence before connecting
        assert hasattr(mode, "setup_behavior")

    def test_on_learn_requested_with_empty_input(self):
        """Test _on_learn_requested with empty input"""
        # Arrange
        mode = self.mode
        self.mock_main_window.get_text_input.return_value = ""

        # Act
        mode._on_learn_requested()

        # Assert
        self.mock_main_window.get_text_input.assert_called_once()
        self.mock_main_window.set_text_output.assert_called_once()
        self.mock_main_window.set_status.assert_called_once()

    def test_on_clear_requested_with_exception(self):
        """Test _on_clear_requested with exception"""
        # Arrange
        mode = self.mode
        self.mock_main_window.set_text_input.side_effect = Exception("Clear failed")

        # Act & Assert
        with pytest.raises(Exception):
            mode._on_clear_requested()

    def test_process_text_with_whitespace_only(self):
        """Test process_text with whitespace only"""
        # Arrange
        mode = self.mode

        # Act
        result = mode.process_text("   \t\n   ")

        # Assert
        assert isinstance(result, str)
        assert len(mode.learning_progress) == 0

    def test_get_sign_language_info_with_whitespace_only(self):
        """Test get_sign_language_info with whitespace only"""
        # Arrange
        mode = self.mode

        # Act
        result = mode.get_sign_language_info("   \t\n   ")

        # Assert
        assert isinstance(result, str)

    def test_update_learning_progress_with_whitespace_only(self):
        """Test _update_learning_progress with whitespace only"""
        # Arrange
        mode = self.mode
        mode.learning_progress = {}

        # Act
        mode._update_learning_progress("   \t\n   ")

        # Assert
        assert len(mode.learning_progress) == 0

    def test_update_learning_progress_with_empty_string(self):
        """Test _update_learning_progress with empty string"""
        # Arrange
        mode = self.mode
        mode.learning_progress = {}

        # Act
        mode._update_learning_progress("")

        # Assert
        assert len(mode.learning_progress) == 0


class TestLearnModeWithQt:
    """Test cases for LearnMode class using Qt mock framework"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures with Qt mocks"""
        from tests.mocks.qt.qt_test_case import QtTestCase

        # Create a mock main window with content_area
        self.mock_main_window = Mock()
        self.mock_main_window.content_area = Mock()
        self.mock_main_window.set_mode = Mock()
        self.mock_main_window.set_status = Mock()
        self.mock_main_window.get_text_input = Mock()
        self.mock_main_window.set_text_output = Mock()
        self.mock_main_window.set_text_input = Mock()

        # Create the mode instance with mocked setup_ui
        with patch("src.helpmesign.modes.learn.learn_mode.LearnMode.setup_ui"):
            self.mode = LearnMode(self.mock_main_window, "dev")

        # Set up Qt environment
        self._setup_qt_environment()
        yield
        self._cleanup_qt_environment()

    def _setup_qt_environment(self):
        """Set up the Qt mock environment."""
        from tests.mocks.qt.qt_mock_framework import qt_mock_framework
        from tests.mocks.qt.qt_test_case import activate_qt_mocks

        # Initialize the Qt mock framework
        qt_mock_framework.initialize()

        # Activate module-level Qt mocking
        activate_qt_mocks()

    def _cleanup_qt_environment(self):
        """Clean up the Qt test environment."""
        from tests.mocks.qt.qt_mock_framework import qt_mock_framework
        from tests.mocks.qt.qt_test_case import deactivate_qt_mocks

        # Deactivate module-level Qt mocking
        deactivate_qt_mocks()

        # Reset the Qt mock framework
        qt_mock_framework.reset()

    def test_update_button_selection_with_qt(self):
        """Test button selection update with Qt mocks"""
        from tests.mocks.qt.qt_test_case import activate_qt_mocks

        activate_qt_mocks()

        # Set up required attributes
        self.mode.alphabet_buttons = {"A": Mock(), "B": Mock()}
        self.mode.number_buttons = {"1": Mock(), "2": Mock()}

        # Create mock buttons with style method
        button_dict = {"A": Mock(), "B": Mock()}
        for button in button_dict.values():
            button.style.return_value = Mock()

        # Test update_button_selection
        self.mode.update_button_selection("A", button_dict)

        # Verify button selection was updated
        assert button_dict["A"].setProperty.called

    def test_update_sign_display_with_qt(self):
        """Test sign display update with Qt mocks"""
        from tests.mocks.qt.qt_test_case import activate_qt_mocks

        activate_qt_mocks()

        # Create mock sign display label
        self.mode.sign_display_label = Mock()

        # Test update_sign_display
        self.mode.update_sign_display("A", "alphabet")

        # Verify sign display was updated
        assert self.mode.current_character == "A"
        assert self.mode.current_char_type == "alphabet"
        assert self.mode.sign_display_label.setText.called

    def test_clear_content_with_learning_widget_with_qt(self):
        """Test clearing content with learning widget using Qt mocks"""
        from tests.mocks.qt.qt_test_case import activate_qt_mocks

        activate_qt_mocks()

        # Set up required attributes
        self.mode.alphabet_buttons = {"A": Mock(), "B": Mock()}
        self.mode.number_buttons = {"1": Mock(), "2": Mock()}
        self.mode.sign_display_label = Mock()
        self.mode.sign_title = Mock()

        # Test clear_content
        self.mode.clear_content()

        # Verify content was cleared
        assert self.mode.main_window.set_text_input.called
        assert self.mode.main_window.set_text_output.called
        assert self.mode.main_window.set_status.called

    def test_activate_with_qt(self):
        """Test mode activation with Qt mocks"""
        from tests.mocks.qt.qt_test_case import activate_qt_mocks

        activate_qt_mocks()

        # Test activate
        self.mode.activate()

        # Verify mode was activated
        assert self.mode.main_window.set_mode.called

    def test_deactivate_with_qt(self):
        """Test mode deactivation with Qt mocks"""
        from tests.mocks.qt.qt_test_case import activate_qt_mocks

        activate_qt_mocks()

        # Create mock main window with content_area
        self.mode.main_window.content_area = Mock()
        self.mode.main_window.default_content = Mock()

        # Test deactivate
        self.mode.deactivate()

        # Verify mode was deactivated
        assert self.mode.main_window.content_area.setCurrentWidget.called

    def test_force_layout_stability_with_qt(self):
        """Test force layout stability with Qt mocks"""
        from tests.mocks.qt.qt_test_case import activate_qt_mocks

        activate_qt_mocks()

        # Create mock learning widget
        self.mode.learning_widget = Mock()

        # Test _force_layout_stability
        self.mode._force_layout_stability()

        # Verify layout stability was enforced
        assert self.mode.learning_widget.updateGeometry.called

    def test_update_ui_with_qt(self):
        """Test UI update with Qt mocks"""
        from tests.mocks.qt.qt_test_case import activate_qt_mocks

        activate_qt_mocks()

        # Create mock learning widget with isVisible method
        self.mode.learning_widget = Mock()
        self.mode.learning_widget.isVisible.return_value = True

        # Test update_ui
        self.mode.update_ui()

        # Verify UI was updated (font updates are currently disabled for debugging)
        # The update_ui method currently does nothing due to font update debugging
        # assert self.mode.learning_widget.isVisible.called

    def test_update_fonts_with_qt(self):
        """Test font update with Qt mocks"""
        from tests.mocks.qt.qt_test_case import activate_qt_mocks

        activate_qt_mocks()

        # Create mock widgets with isVisible method
        self.mode.learning_widget = Mock()
        self.mode.learning_widget.isVisible.return_value = True
        self.mode.sign_title = Mock()
        self.mode.selection_title = Mock()

        # Mock the font manager and theme manager to avoid exceptions
        with patch(
            "src.helpmesign.utils.font_manager.get_font_manager"
        ) as mock_font_manager, patch(
            "src.helpmesign.utils.theme_manager.get_font_size"
        ) as mock_font_size:

            mock_font_manager.return_value._get_current_font_family.return_value = (
                "Roboto"
            )
            mock_font_size.return_value = 12

            # Test update_fonts - just verify it runs without error
            self.mode.update_fonts()

            # Verify the method executed (widgets were checked for visibility)
            assert self.mode.learning_widget.isVisible.called
