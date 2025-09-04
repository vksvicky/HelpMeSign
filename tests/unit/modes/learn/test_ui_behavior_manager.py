"""
Tests for LearnModeUIBehaviorManager
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from src.helpmesign.modes.learn.ui_behavior_manager import LearnModeUIBehaviorManager


class TestLearnModeUIBehaviorManager:
    """Test cases for LearnModeUIBehaviorManager"""

    @pytest.fixture
    def mock_learn_mode(self):
        """Create a mock learn mode for testing"""
        mock_mode = Mock()
        mock_mode.logger = Mock()
        mock_mode.current_font_size = 12
        return mock_mode

    @pytest.fixture
    def behavior_manager(self, mock_learn_mode):
        """Create a behavior manager instance for testing"""
        with patch(
            "src.helpmesign.modes.learn.ui_behavior_manager.get_sign_language_loader"
        ):
            return LearnModeUIBehaviorManager(mock_learn_mode)

    def test_init(self, behavior_manager, mock_learn_mode):
        """Test initialization"""
        assert behavior_manager.learn_mode == mock_learn_mode
        assert (
            behavior_manager.PLACEHOLDER_STYLE
            == "text-align: center; color: #6b7b8c; font-style: italic; padding: 20px;"
        )

    def test_set_placeholder_text_success(self, behavior_manager, mock_learn_mode):
        """Test successful placeholder text setting"""
        # Mock the sign_instructions_label
        mock_label = Mock()
        mock_learn_mode.sign_instructions_label = mock_label

        # Mock get_text
        with patch(
            "src.helpmesign.modes.learn.ui_behavior_manager.get_text"
        ) as mock_get_text:
            mock_get_text.return_value = "Sign will appear here"

            behavior_manager._set_placeholder_text()

            # Verify the label was set with correct HTML content
            expected_html = f'<div style="{behavior_manager.PLACEHOLDER_STYLE} font-size: 12px;">Sign will appear here</div>'
            mock_label.setText.assert_called_once_with(expected_html)

            # Verify logging
            mock_learn_mode.logger.debug.assert_called_once_with(
                "Placeholder text set: 'Sign will appear here' with font size: 12px"
            )

    def test_set_placeholder_text_missing_label(
        self, behavior_manager, mock_learn_mode
    ):
        """Test placeholder text setting when label doesn't exist"""
        # Don't set sign_instructions_label
        behavior_manager._set_placeholder_text()

        # Should not raise error, just handle gracefully
        # The method should check if the label exists before proceeding
        pass

    def test_set_placeholder_text_exception(self, behavior_manager, mock_learn_mode):
        """Test placeholder text setting with exception"""
        mock_label = Mock()
        mock_label.setText.side_effect = Exception("Test error")
        mock_learn_mode.sign_instructions_label = mock_label

        with patch(
            "src.helpmesign.modes.learn.ui_behavior_manager.get_text"
        ) as mock_get_text:
            mock_get_text.return_value = "Sign will appear here"

            behavior_manager._set_placeholder_text()

            # Should log the error
            mock_learn_mode.logger.error.assert_called_once_with(
                "Error setting placeholder text: Test error"
            )

    def test_clear_sign_clicked_success(self, behavior_manager, mock_learn_mode):
        """Test successful clear sign button click"""
        # Mock all required components
        mock_svg_widget = Mock()
        mock_svg_widget.load = Mock()
        # Remove setText method to simulate QSvgWidget (which doesn't have setText)
        delattr(mock_svg_widget, "setText")
        mock_learn_mode.sign_svg_widget = mock_svg_widget

        # Ensure the mock is properly set up
        assert hasattr(mock_learn_mode.sign_svg_widget, "load")
        assert not hasattr(mock_learn_mode.sign_svg_widget, "setText")

        mock_label = Mock()
        mock_learn_mode.sign_instructions_label = mock_label

        mock_clear_btn = Mock()
        mock_learn_mode.clear_sign_btn = mock_clear_btn

        mock_alphabet_buttons = {}
        mock_learn_mode.alphabet_buttons = mock_alphabet_buttons

        mock_number_buttons = {}
        mock_learn_mode.number_buttons = mock_number_buttons

        mock_learn_mode.current_character = "A"
        mock_learn_mode.current_char_type = "alphabet"

        mock_main_window = Mock()
        mock_learn_mode.main_window = mock_main_window

        # Mock character manager
        mock_character_manager = Mock()
        mock_learn_mode.character_manager = mock_character_manager

        # Mock get_text
        with patch(
            "src.helpmesign.modes.learn.ui_behavior_manager.get_text"
        ) as mock_get_text:
            mock_get_text.return_value = "Sign will appear here"

            behavior_manager._on_clear_sign_clicked()

            # Verify SVG widget was cleared
            mock_svg_widget.load.assert_called_once_with("")

            # Verify placeholder text was set
            expected_html = f'<div style="{behavior_manager.PLACEHOLDER_STYLE} font-size: 12px;">Sign will appear here</div>'
            mock_label.setText.assert_called_once_with(expected_html)

            # Verify clear button was hidden
            mock_clear_btn.setVisible.assert_called_once_with(False)

            # Verify button selections were cleared
            assert mock_character_manager.update_button_selection.call_count == 2

            # Verify current character tracking was reset
            assert mock_learn_mode.current_character is None
            assert mock_learn_mode.current_char_type is None

            # Verify status was updated
            mock_main_window.set_status.assert_called_once_with("Sign display cleared")

    def test_clear_sign_clicked_missing_components(
        self, behavior_manager, mock_learn_mode
    ):
        """Test clear sign button click with missing components"""
        # Don't set any components
        behavior_manager._on_clear_sign_clicked()

        # Should not raise error, just handle gracefully
        mock_learn_mode.logger.error.assert_not_called()

    def test_clear_sign_clicked_exception(self, behavior_manager, mock_learn_mode):
        """Test clear sign button click with exception"""
        mock_svg_widget = Mock()
        mock_svg_widget.load.side_effect = Exception("Test error")
        # Remove setText method to simulate QSvgWidget
        delattr(mock_svg_widget, "setText")
        mock_learn_mode.sign_svg_widget = mock_svg_widget

        behavior_manager._on_clear_sign_clicked()

        # Should log the error
        mock_learn_mode.logger.error.assert_called_once_with(
            "Error clearing sign: Test error"
        )

    def test_font_size_configuration_integration(
        self, behavior_manager, mock_learn_mode
    ):
        """Test that font size is properly retrieved from configuration"""
        # Test with different font sizes
        test_cases = [10, 12, 16, 20]

        for font_size in test_cases:
            mock_learn_mode.current_font_size = font_size

            mock_label = Mock()
            mock_learn_mode.sign_instructions_label = mock_label

            with patch(
                "src.helpmesign.modes.learn.ui_behavior_manager.get_text"
            ) as mock_get_text:
                mock_get_text.return_value = "Sign will appear here"

                behavior_manager._set_placeholder_text()

                # Verify the correct font size was used
                expected_html = f'<div style="{behavior_manager.PLACEHOLDER_STYLE} font-size: {font_size}px;">Sign will appear here</div>'
                mock_label.setText.assert_called_with(expected_html)

                # Reset for next iteration
                mock_label.setText.reset_mock()

    def test_placeholder_style_consistency(self, behavior_manager):
        """Test that placeholder style is consistent and well-formed"""
        style = behavior_manager.PLACEHOLDER_STYLE

        # Should contain all required CSS properties
        assert "text-align: center" in style
        assert "color: #6b7b8c" in style
        assert "font-style: italic" in style
        assert "padding: 20px" in style

        # Should not contain font-size (it's added dynamically)
        assert "font-size" not in style

        # Should end with semicolon for proper CSS formatting
        assert style.endswith(";")

    def test_clear_button_functionality_complete(
        self, behavior_manager, mock_learn_mode
    ):
        """Test that clear button completely resets the sign display state"""
        # Mock all components
        mock_svg_widget = Mock()
        mock_svg_widget.load = Mock()
        # Remove setText method to simulate QSvgWidget
        delattr(mock_svg_widget, "setText")
        mock_learn_mode.sign_svg_widget = mock_svg_widget

        mock_label = Mock()
        mock_learn_mode.sign_instructions_label = mock_label

        mock_clear_btn = Mock()
        mock_learn_mode.clear_sign_btn = mock_clear_btn

        # Mock character manager
        mock_character_manager = Mock()
        mock_learn_mode.character_manager = mock_character_manager

        # Mock main window
        mock_main_window = Mock()
        mock_learn_mode.main_window = mock_main_window

        with patch(
            "src.helpmesign.modes.learn.ui_behavior_manager.get_text"
        ) as mock_get_text:
            mock_get_text.return_value = "Sign will appear here"

            behavior_manager._on_clear_sign_clicked()

            # Verify ALL components were properly reset
            assert mock_svg_widget.load.called  # SVG cleared
            assert mock_label.setText.called  # Placeholder text set
            assert mock_clear_btn.setVisible.called  # Button hidden
            assert mock_main_window.set_status.called  # Status updated


if __name__ == "__main__":
    pytest.main([__file__])
