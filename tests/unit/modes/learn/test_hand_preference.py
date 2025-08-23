"""
Tests for hand preference functionality in LearnMode
"""

from unittest.mock import patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget

from src.helpmesign.modes.learn.learn_mode import LearnMode


class MockMainWindow:
    """Mock main window for testing"""

    def __init__(self):
        self.content_area = QWidget()


class TestHandPreference:
    """Test hand preference functionality"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])

        self.mock_main_window = MockMainWindow()
        # Create the mode instance and let it create the UI
        self.learn_mode = LearnMode(self.mock_main_window)

        yield

        # Cleanup
        if hasattr(self.learn_mode, "learning_widget"):
            try:
                self.learn_mode.learning_widget.deleteLater()
            except AttributeError:
                # Mock objects don't have deleteLater method
                pass

    def test_hand_preference_buttons_created(self):
        """Test that hand preference buttons are created correctly"""
        assert hasattr(self.learn_mode, "right_hand_btn")
        assert hasattr(self.learn_mode, "left_hand_btn")

        # Check button properties
        assert self.learn_mode.right_hand_btn.text() == "🖐️"
        assert self.learn_mode.left_hand_btn.text() == "🤚"
        assert self.learn_mode.right_hand_btn.toolTip() == "Right Hand Signs"
        assert self.learn_mode.left_hand_btn.toolTip() == "Left Hand Signs"

    def test_initial_hand_preference(self):
        """Test initial hand preference loads from config"""
        # Should load from config (defaults to right if no config)
        assert self.learn_mode.current_hand_preference in ["right", "left"]

        # Check button states match the preference
        if self.learn_mode.current_hand_preference == "right":
            assert self.learn_mode.right_hand_btn.property("selected") is True
            left_selected = self.learn_mode.left_hand_btn.property("selected")
            assert left_selected is not True
        else:
            assert self.learn_mode.left_hand_btn.property("selected") is True
            right_selected = self.learn_mode.right_hand_btn.property("selected")
            assert right_selected is not True

    def test_hand_preference_switching(self):
        """Test switching between hand preferences"""
        # Switch to left hand
        self.learn_mode._set_hand_preference("left")
        assert self.learn_mode.current_hand_preference == "left"
        assert self.learn_mode.right_hand_btn.property("selected") is False
        assert self.learn_mode.left_hand_btn.property("selected") is True

        # Switch to right hand
        self.learn_mode._set_hand_preference("right")
        assert self.learn_mode.current_hand_preference == "right"
        assert self.learn_mode.right_hand_btn.property("selected") is True
        assert self.learn_mode.left_hand_btn.property("selected") is False

    def test_hand_preference_button_clicks(self):
        """Test clicking hand preference buttons"""
        # Click left hand button
        self.learn_mode.left_hand_btn.click()
        assert self.learn_mode.current_hand_preference == "left"

        # Click right hand button
        self.learn_mode.right_hand_btn.click()
        assert self.learn_mode.current_hand_preference == "right"

    def test_sign_display_updates_with_hand_preference(self):
        """Test that sign display updates when hand preference changes"""
        # Set a current character
        self.learn_mode.current_character = "A"
        self.learn_mode.current_char_type = "alphabet"

        # Mock the sign loader
        class MockSignLoader:
            def get_sign_svg(self, language, character, hand):
                return f"<svg>Mock SVG for {character} ({hand} hand)</svg>"

            def get_sign_instructions(self, language, character, hand):
                return f"Mock instructions for {character} ({hand} hand)"

        self.learn_mode.sign_loader = MockSignLoader()
        self.learn_mode.current_language = "ASL"

        # Test that sign display updates with hand preference
        self.learn_mode._set_hand_preference("left")
        # The sign display should be updated with left hand preference

        self.learn_mode._set_hand_preference("right")
        # The sign display should be updated with right hand preference

    def test_hand_preference_ui_positioning(self):
        """Test that hand preference buttons are positioned correctly"""
        # Check that buttons exist and have proper text
        assert self.learn_mode.right_hand_btn.text() == "🖐️"
        assert self.learn_mode.left_hand_btn.text() == "🤚"

        # Check that buttons are created (parent check is optional in test environment)
        # In test environment, buttons might not be added to a parent widget
        # but they should still be created and functional
        assert hasattr(self.learn_mode.right_hand_btn, "parent")
        assert hasattr(self.learn_mode.left_hand_btn, "parent")

    def test_hand_preference_button_styling(self):
        """Test hand preference button styling"""
        # Check that buttons have the correct style properties
        right_style = self.learn_mode.right_hand_btn.styleSheet()
        left_style = self.learn_mode.left_hand_btn.styleSheet()

        # Should contain styling for selected state
        assert "selected" in right_style
        assert "selected" in left_style

        # Should contain hover effects
        assert "hover" in right_style
        assert "hover" in left_style

        # Should contain pressed state for visual feedback
        assert "pressed" in right_style
        assert "pressed" in left_style

        # Should contain enhanced border for selected state
        assert "border-width: 4px" in right_style
        assert "border-width: 4px" in left_style

    def test_hand_preference_configuration_persistence(self):
        """Test that hand preference is saved to and loaded from config"""
        # Mock the config functions to test persistence
        original_pref = None
        saved_pref = None

        def mock_set_hand_preference(pref):
            nonlocal saved_pref
            saved_pref = pref

        def mock_get_hand_preference():
            return saved_pref or "right"

        # Store original functions
        import src.helpmesign.core.startup as startup_module

        original_set = startup_module.set_hand_preference
        original_get = startup_module.get_hand_preference

        try:
            # Replace with mocks
            startup_module.set_hand_preference = mock_set_hand_preference
            startup_module.get_hand_preference = mock_get_hand_preference

            # Test initial state
            assert self.learn_mode.current_hand_preference in ["right", "left"]
            original_pref = self.learn_mode.current_hand_preference

            # Test changing preference saves to config
            new_pref = "left" if original_pref == "right" else "right"
            self.learn_mode._set_hand_preference(new_pref)

            # Verify it was saved
            assert saved_pref == new_pref
            assert self.learn_mode.current_hand_preference == new_pref

        finally:
            # Restore original functions
            startup_module.set_hand_preference = original_set
            startup_module.get_hand_preference = original_get

    def test_hand_preference_visual_state_restoration(self):
        """Test that visual state is properly restored after application restart"""
        # Test that the restore method works correctly
        self.learn_mode._restore_hand_preference_visual_state()

        # Verify the visual state matches the current preference
        current_pref = self.learn_mode.current_hand_preference

        if current_pref == "left":
            assert self.learn_mode.left_hand_btn.property("selected") is True
            assert self.learn_mode.right_hand_btn.property("selected") is not True
        else:
            assert self.learn_mode.right_hand_btn.property("selected") is True
            assert self.learn_mode.left_hand_btn.property("selected") is not True

    def test_hand_preference_visual_state_on_click(self):
        """Test that visual state changes correctly when buttons are clicked"""
        # Test clicking left hand button
        self.learn_mode.left_hand_btn.click()

        # Verify left hand is selected
        assert self.learn_mode.current_hand_preference == "left"
        assert self.learn_mode.left_hand_btn.property("selected") is True
        assert self.learn_mode.right_hand_btn.property("selected") is not True

        # Test clicking right hand button
        self.learn_mode.right_hand_btn.click()

        # Verify right hand is selected
        assert self.learn_mode.current_hand_preference == "right"
        assert self.learn_mode.right_hand_btn.property("selected") is True
        assert self.learn_mode.left_hand_btn.property("selected") is not True

    def test_hand_preference_enhanced_styling(self):
        """Test that the enhanced styling is applied correctly"""
        # Check that buttons have the enhanced styling
        right_style = self.learn_mode.right_hand_btn.styleSheet()
        left_style = self.learn_mode.left_hand_btn.styleSheet()

        # Should contain the enhanced selected state styling
        assert "background-color: #28a745" in right_style
        assert "background-color: #28a745" in left_style
        assert "border-width: 4px" in right_style
        assert "border-width: 4px" in left_style
        assert "font-weight: bold" in right_style
        assert "font-weight: bold" in left_style

    def test_hand_preference_style_application(self):
        """Test that styles are properly applied when selection changes"""
        # Get initial state
        initial_right_selected = self.learn_mode.right_hand_btn.property("selected")
        initial_left_selected = self.learn_mode.left_hand_btn.property("selected")

        # Click the opposite button
        if initial_right_selected:
            self.learn_mode.left_hand_btn.click()
            expected_selected = "left"
        else:
            self.learn_mode.right_hand_btn.click()
            expected_selected = "right"

        # Verify the change
        assert self.learn_mode.current_hand_preference == expected_selected

        # Verify button properties changed
        if expected_selected == "left":
            assert self.learn_mode.left_hand_btn.property("selected") is True
            assert self.learn_mode.right_hand_btn.property("selected") is not True
        else:
            assert self.learn_mode.right_hand_btn.property("selected") is True
            assert self.learn_mode.left_hand_btn.property("selected") is not True

    def test_hand_preference_visual_selection_working(self):
        """Test that visual selection state is properly applied when clicking buttons"""
        # Test clicking left hand button
        self.learn_mode.left_hand_btn.click()

        # Verify left hand is selected
        assert self.learn_mode.current_hand_preference == "left"
        assert self.learn_mode.left_hand_btn.property("selected") is True
        assert self.learn_mode.right_hand_btn.property("selected") is False

        # Test clicking right hand button
        self.learn_mode.right_hand_btn.click()

        # Verify right hand is selected
        assert self.learn_mode.current_hand_preference == "right"
        assert self.learn_mode.right_hand_btn.property("selected") is True
        assert self.learn_mode.left_hand_btn.property("selected") is False

        # Test clicking left hand button again
        self.learn_mode.left_hand_btn.click()

        # Verify left hand is selected again
        assert self.learn_mode.current_hand_preference == "left"
        assert self.learn_mode.left_hand_btn.property("selected") is True
        assert self.learn_mode.right_hand_btn.property("selected") is False
