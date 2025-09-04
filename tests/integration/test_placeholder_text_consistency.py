"""
Integration tests for placeholder text consistency
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel

from src.helpmesign.modes.learn.ui_behavior_manager import LearnModeUIBehaviorManager
from src.helpmesign.modes.learn.ui_components import LearnModeUIComponents


class TestPlaceholderTextConsistency:
    """Integration tests for placeholder text consistency"""

    @pytest.fixture(scope="class")
    def qapp(self):
        """Create QApplication for testing"""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
        # Cleanup handled by pytest

    @pytest.fixture
    def mock_learn_mode(self):
        """Create a mock learn mode for testing"""
        mock_mode = Mock()
        mock_mode.logger = Mock()
        mock_mode.current_font_size = 12
        mock_mode.current_theme = "Light"
        return mock_mode

    @pytest.fixture
    def behavior_manager(self, mock_learn_mode):
        """Create a behavior manager instance for testing"""
        with patch(
            "src.helpmesign.modes.learn.ui_behavior_manager.get_sign_language_loader"
        ):
            return LearnModeUIBehaviorManager(mock_learn_mode)

    @pytest.fixture
    def ui_components(self, mock_learn_mode):
        """Create UI components instance for testing"""
        with patch("src.helpmesign.modes.learn.ui_components.testing_env", False):
            return LearnModeUIComponents(mock_learn_mode)

    def test_placeholder_text_consistency_between_launch_and_clear(
        self, behavior_manager, mock_learn_mode
    ):
        """Test that placeholder text looks identical on app launch vs after clearing"""
        # Mock the sign_instructions_label
        mock_label = Mock()
        mock_learn_mode.sign_instructions_label = mock_label

        # Mock get_text
        with patch(
            "src.helpmesign.modes.learn.ui_behavior_manager.get_text"
        ) as mock_get_text:
            mock_get_text.return_value = "Sign will appear here"

            # Simulate app launch - set placeholder text
            behavior_manager._set_placeholder_text()
            launch_html = mock_label.setText.call_args[0][0]

            # Reset mock
            mock_label.setText.reset_mock()

            # Simulate clear button click - set placeholder text again
            behavior_manager._on_clear_sign_clicked()
            clear_html = mock_label.setText.call_args[0][0]

            # Verify both calls set the EXACT same HTML content
            assert (
                launch_html == clear_html
            ), f"HTML content differs: launch='{launch_html}' vs clear='{clear_html}'"

            # Verify both contain the correct styling
            assert "text-align: center" in launch_html
            assert "color: #6b7b8c" in launch_html
            assert "font-style: italic" in launch_html
            assert "padding: 20px" in launch_html
            assert "font-size: 12px" in launch_html

    def test_font_size_dynamic_configuration(self, behavior_manager, mock_learn_mode):
        """Test that font size changes are reflected in placeholder text"""
        # Mock the sign_instructions_label
        mock_label = Mock()
        mock_learn_mode.sign_instructions_label = mock_label

        # Mock get_text
        with patch(
            "src.helpmesign.modes.learn.ui_behavior_manager.get_text"
        ) as mock_get_text:
            mock_get_text.return_value = "Sign will appear here"

            # Test with different font sizes
            test_cases = [10, 12, 16, 20]

            for font_size in test_cases:
                mock_learn_mode.current_font_size = font_size
                mock_label.setText.reset_mock()

                behavior_manager._set_placeholder_text()

                # Verify the correct font size was used
                html_content = mock_label.setText.call_args[0][0]
                assert f"font-size: {font_size}px" in html_content

    def test_clear_button_complete_functionality(
        self, behavior_manager, mock_learn_mode
    ):
        """Test that clear button completely resets the UI state"""
        # Mock all required components
        mock_svg_widget = Mock()
        mock_svg_widget.load = Mock()
        # Remove setText method to simulate QSvgWidget
        delattr(mock_svg_widget, "setText")
        mock_learn_mode.sign_svg_widget = mock_svg_widget

        mock_label = Mock()
        mock_learn_mode.sign_instructions_label = mock_label

        mock_clear_btn = Mock()
        mock_learn_mode.clear_sign_btn = mock_clear_btn

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

            # Set some initial state
            mock_learn_mode.current_character = "A"
            mock_learn_mode.current_char_type = "alphabet"

            behavior_manager._on_clear_sign_clicked()

            # Verify ALL components were properly reset
            assert mock_svg_widget.load.called  # SVG cleared
            assert mock_label.setText.called  # Placeholder text set
            assert mock_clear_btn.setVisible.called  # Button hidden
            assert mock_main_window.set_status.called  # Status updated

            # Verify character tracking was reset
            assert mock_learn_mode.current_character is None
            assert mock_learn_mode.current_char_type is None

    def test_placeholder_text_initialization_timing(
        self, behavior_manager, mock_learn_mode
    ):
        """Test that placeholder text is set at the right time"""
        # Mock the sign_instructions_label
        mock_label = Mock()
        mock_learn_mode.sign_instructions_label = mock_label

        # Mock get_text
        with patch(
            "src.helpmesign.modes.learn.ui_behavior_manager.get_text"
        ) as mock_get_text:
            mock_get_text.return_value = "Sign will appear here"

            # Simulate the initialization sequence
            behavior_manager._set_placeholder_text()

            # Verify the label was set with placeholder text
            assert mock_label.setText.called

            # Verify the content is correct
            html_content = mock_label.setText.call_args[0][0]
            assert "Sign will appear here" in html_content
            assert "text-align: center" in html_content

    def test_no_hardcoded_values_in_styling(self, behavior_manager):
        """Test that no hardcoded values exist in the styling"""
        style = behavior_manager.PLACEHOLDER_STYLE

        # Should not contain any hardcoded font sizes
        assert "font-size" not in style

        # Should contain only the base styling properties
        assert "text-align: center" in style
        assert "color: #6b7b8c" in style
        assert "font-style: italic" in style
        assert "padding: 20px" in style

    def test_error_handling_robustness(self, behavior_manager, mock_learn_mode):
        """Test that the system handles errors gracefully"""
        # Mock the sign_instructions_label to raise an exception
        mock_label = Mock()
        mock_label.setText.side_effect = Exception("Test error")
        mock_learn_mode.sign_instructions_label = mock_label

        # Should not crash, should log the error
        behavior_manager._set_placeholder_text()
        mock_learn_mode.logger.error.assert_called_once_with(
            "Error setting placeholder text: Test error"
        )


if __name__ == "__main__":
    pytest.main([__file__])
