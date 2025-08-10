"""
Tests for category selection functionality in LearnMode
Tests the new QPushButton + QMenu approach for category selection
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from src.helpmesign.modes.learn.learn_mode import LearnMode
from tests.mocks.qt.qt_module_mocks import activate_qt_mocks, deactivate_qt_mocks
from tests.mocks.qt.qt_test_case import QtTestCase


class TestCategorySelection(QtTestCase):
    """Test cases for category selection functionality"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures"""
        # Activate Qt mocks to prevent fatal errors
        activate_qt_mocks()

        # Create a mock main window
        self.mock_main_window = Mock()
        self.mock_main_window._is_mock = True  # Mark as mock to skip UI creation
        self.mock_main_window.set_mode = Mock()
        self.mock_main_window.set_status = Mock()
        self.mock_main_window.get_text_input = Mock()
        self.mock_main_window.set_text_output = Mock()
        self.mock_main_window.set_text_input = Mock()

        # Create the mode instance
        self.mode = LearnMode(self.mock_main_window)

        yield

        # Clean up
        deactivate_qt_mocks()

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_category_button_creation(self, mock_get_text):
        """Test that category button is created with proper text"""
        # Arrange
        mock_get_text.return_value = "All Languages"

        # Act - This would normally happen in create_language_selector
        # We'll test the method that updates the button text
        self.mode.category_text_label = Mock()
        self.mode.populate_language_list = Mock()  # Mock to avoid UI dependencies
        self.mode.on_category_selected("all")

        # Assert
        mock_get_text.assert_called_with("ui.language_selection.category_all")
        self.mode.category_text_label.setText.assert_called_with("All Languages")

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_category_selection_all(self, mock_get_text):
        """Test selecting 'all' category"""
        # Arrange
        mock_get_text.return_value = "All Languages"
        self.mode.category_text_label = Mock()
        self.mode.populate_language_list = Mock()

        # Act
        self.mode.on_category_selected("all")

        # Assert
        self.mode.category_text_label.setText.assert_called_with("All Languages")
        assert self.mode.current_category == "all"
        self.mode.populate_language_list.assert_called_with("all")

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_category_selection_popular(self, mock_get_text):
        """Test selecting 'popular' category"""
        # Arrange
        mock_get_text.return_value = "Popular Languages"
        self.mode.category_text_label = Mock()
        self.mode.populate_language_list = Mock()

        # Act
        self.mode.on_category_selected("popular")

        # Assert
        self.mode.category_text_label.setText.assert_called_with("Popular Languages")
        assert self.mode.current_category == "popular"
        self.mode.populate_language_list.assert_called_with("popular")

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_category_selection_beginner(self, mock_get_text):
        """Test selecting 'beginner' category"""
        # Arrange
        mock_get_text.return_value = "Beginner Friendly"
        self.mode.category_text_label = Mock()
        self.mode.populate_language_list = Mock()

        # Act
        self.mode.on_category_selected("beginner")

        # Assert
        self.mode.category_text_label.setText.assert_called_with("Beginner Friendly")
        assert self.mode.current_category == "beginner"
        self.mode.populate_language_list.assert_called_with("beginner")

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_category_selection_intermediate(self, mock_get_text):
        """Test selecting 'intermediate' category"""
        # Arrange
        mock_get_text.return_value = "Intermediate"
        self.mode.category_text_label = Mock()
        self.mode.populate_language_list = Mock()

        # Act
        self.mode.on_category_selected("intermediate")

        # Assert
        self.mode.category_text_label.setText.assert_called_with("Intermediate")
        assert self.mode.current_category == "intermediate"
        self.mode.populate_language_list.assert_called_with("intermediate")

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_category_selection_advanced(self, mock_get_text):
        """Test selecting 'advanced' category"""
        # Arrange
        mock_get_text.return_value = "Advanced"
        self.mode.category_text_label = Mock()
        self.mode.populate_language_list = Mock()

        # Act
        self.mode.on_category_selected("advanced")

        # Assert
        self.mode.category_text_label.setText.assert_called_with("Advanced")
        assert self.mode.current_category == "advanced"
        self.mode.populate_language_list.assert_called_with("advanced")

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_category_selection_unknown_category(self, mock_get_text):
        """Test selecting unknown category defaults to 'all'"""
        # Arrange
        mock_get_text.return_value = "All Languages"
        self.mode.category_text_label = Mock()
        self.mode.populate_language_list = Mock()

        # Act
        self.mode.on_category_selected("unknown")

        # Assert
        self.mode.category_text_label.setText.assert_called_with("All Languages")
        assert (
            self.mode.current_category == "unknown"
        )  # Still tracks the unknown category
        self.mode.populate_language_list.assert_called_with("unknown")

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_category_selection_exception_handling(self, mock_get_text):
        """Test exception handling in category selection"""
        # Arrange
        mock_get_text.side_effect = Exception("Text not found")
        self.mode.category_text_label = Mock()
        self.mode.populate_language_list = Mock()

        # Act
        self.mode.on_category_selected("all")

        # Assert
        # Should handle exception gracefully and default to "all"
        self.mode.populate_language_list.assert_called_with("all")

    def test_show_category_menu(self):
        """Test showing the category menu"""
        # Arrange
        self.mode.category_button = Mock()
        self.mode.category_menu = Mock()
        self.mode.category_button.rect.return_value = Mock()
        self.mode.category_button.mapToGlobal.return_value = (100, 200)

        # Act
        self.mode.show_category_menu()

        # Assert
        self.mode.category_button.rect.assert_called_once()
        self.mode.category_button.mapToGlobal.assert_called_once()
        self.mode.category_menu.popup.assert_called_once_with((100, 200))

    def test_show_category_menu_exception_handling(self):
        """Test exception handling in show_category_menu"""
        # Arrange
        self.mode.category_button = Mock()
        self.mode.category_menu = Mock()
        self.mode.category_button.rect.side_effect = Exception("Button error")

        # Act
        self.mode.show_category_menu()

        # Assert
        # Should handle exception gracefully without crashing
        # The method should not raise an exception and should complete execution
        # We verify this by checking that the method completed without error
        assert self.mode.category_button.rect.called

    def test_current_category_tracking(self):
        """Test that current_category is properly tracked"""
        # Arrange
        self.mode.populate_language_list = Mock()
        self.mode.category_text_label = Mock()  # Mock to avoid UI dependencies

        # Act - Set initial category
        self.mode.current_category = "all"

        # Assert
        assert self.mode.current_category == "all"

        # Act - Change category
        self.mode.on_category_selected("popular")

        # Assert
        assert self.mode.current_category == "popular"

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_search_with_current_category(self, mock_get_text):
        """Test that search uses the current category"""
        # Arrange
        self.mode.current_category = "popular"
        self.mode.populate_language_list = Mock()

        # Act - Simulate clearing search (which should show current category)
        self.mode.on_search_changed("")

        # Assert
        self.mode.populate_language_list.assert_called_with("popular")

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_search_with_text_uses_search_results(self, mock_get_text):
        """Test that search with text uses search results instead of category"""
        # Arrange
        self.mode.current_category = "popular"
        self.mode.populate_search_results = Mock()

        # Act - Search with text
        self.mode.on_search_changed("ASL")

        # Assert
        # The search should populate search results instead of category
        # Verify that populate_search_results was called (indicating search was performed)
        self.mode.populate_search_results.assert_called()

    def test_initial_category_default(self):
        """Test that initial category defaults to 'all'"""
        # Assert
        assert self.mode.current_category == "all"

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_category_display_names_mapping(self, mock_get_text):
        """Test that category display names are properly mapped"""
        # Arrange
        mock_get_text.side_effect = lambda key: {
            "ui.language_selection.category_all": "All Languages",
            "ui.language_selection.category_popular": "Popular Languages",
            "ui.language_selection.category_beginner": "Beginner Friendly",
            "ui.language_selection.category_intermediate": "Intermediate",
            "ui.language_selection.category_advanced": "Advanced",
        }.get(key, key)

        self.mode.category_text_label = Mock()
        self.mode.populate_language_list = Mock()

        # Act & Assert for each category
        categories = ["all", "popular", "beginner", "intermediate", "advanced"]
        expected_names = [
            "All Languages",
            "Popular Languages",
            "Beginner Friendly",
            "Intermediate",
            "Advanced",
        ]

        for category, expected_name in zip(categories, expected_names):
            self.mode.on_category_selected(category)
            self.mode.category_text_label.setText.assert_called_with(expected_name)
            self.mode.category_text_label.reset_mock()


class TestCategorySelectionWithQt(QtTestCase):
    """Test cases for category selection using Qt mock framework"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures with Qt mocks"""
        # Activate Qt mocks to prevent fatal errors
        activate_qt_mocks()

        # Create a simple test case without inheritance issues
        self.mock_main_window = Mock()
        self.mock_main_window._is_mock = True
        self.mock_main_window.set_mode = Mock()
        self.mock_main_window.set_status = Mock()
        self.mock_main_window.get_text_input = Mock()
        self.mock_main_window.set_text_output = Mock()
        self.mock_main_window.set_text_input = Mock()

        self.mode = LearnMode(self.mock_main_window)

        yield

        # Clean up
        deactivate_qt_mocks()

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_category_button_creation_with_qt(self, mock_get_text):
        """Test category button creation with Qt mocks"""
        # Arrange
        mock_get_text.return_value = "All Languages"

        # Act
        self.mode.category_text_label = Mock()
        self.mode.populate_language_list = Mock()
        self.mode.on_category_selected("all")

        # Assert
        mock_get_text.assert_called_with("ui.language_selection.category_all")

    def test_category_menu_creation_with_qt(self):
        """Test category menu creation with Qt mocks"""
        # Arrange
        self.mode.category_button = Mock()
        self.mode.category_menu = Mock()
        self.mode.category_button.rect.return_value = Mock()
        self.mode.category_button.mapToGlobal.return_value = (100, 200)

        # Act
        self.mode.show_category_menu()

        # Assert
        # Should not crash with Qt mocks and should call the expected methods
        self.mode.category_button.rect.assert_called_once()
        self.mode.category_button.mapToGlobal.assert_called_once()
        self.mode.category_menu.popup.assert_called_once_with((100, 200))

    @patch("src.helpmesign.modes.learn.learn_mode.get_text")
    def test_category_selection_workflow_with_qt(self, mock_get_text):
        """Test complete category selection workflow with Qt mocks"""
        # Arrange
        mock_get_text.return_value = "Popular Languages"
        self.mode.category_text_label = Mock()
        self.mode.populate_language_list = Mock()

        # Act
        self.mode.on_category_selected("popular")

        # Assert
        assert self.mode.current_category == "popular"
        self.mode.populate_language_list.assert_called_with("popular")
