"""
Unit tests for ModeManager class
Tests happy paths, error conditions, exceptions, and boundary conditions
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the mode manager class
from src.helpmesign.modes.mode_manager import ModeManager


class TestModeManager(unittest.TestCase):
    """Test cases for ModeManager class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a mock main window
        self.mock_main_window = Mock()
        self.mock_main_window.set_mode = Mock()
        self.mock_main_window.set_status = Mock()
        
        # Create the mode manager instance
        self.mode_manager = ModeManager(self.mock_main_window, "dev")

    def tearDown(self):
        """Clean up after tests"""
        pass

    # Happy Path Tests
    def test_happy_path_initialization(self):
        """Test successful mode manager initialization"""
        # Arrange & Act
        manager = self.mode_manager
        
        # Assert
        self.assertEqual(manager.main_window, self.mock_main_window)
        self.assertEqual(manager.environment, "dev")
        self.assertIsInstance(manager.modes, dict)
        self.assertIsNotNone(manager.current_mode)
        self.assertIn("sign_translate", manager.modes)
        self.assertIn("learn", manager.modes)

    def test_happy_path_get_available_modes(self):
        """Test getting available modes"""
        # Arrange
        manager = self.mode_manager
        
        # Act
        modes = manager.get_available_modes()
        
        # Assert
        self.assertIsInstance(modes, dict)
        self.assertIn("sign_translate", modes)
        self.assertIn("learn", modes)
        self.assertEqual(len(modes), 2)
        # Should return a copy, not the original
        self.assertIsNot(modes, manager.modes)

    def test_happy_path_get_current_mode(self):
        """Test getting current mode"""
        # Arrange
        manager = self.mode_manager
        
        # Act
        current_mode = manager.get_current_mode()
        
        # Assert
        self.assertIsNotNone(current_mode)
        self.assertEqual(current_mode, manager.modes["sign_translate"])

    @patch('src.helpmesign.modes.sign_translate.sign_translate_mode.get_text')
    def test_happy_path_get_current_mode_name(self, mock_get_text):
        """Test getting current mode name"""
        # Arrange
        mock_get_text.return_value = "Sign & Translate"
        manager = self.mode_manager
        
        # Act
        mode_name = manager.get_current_mode_name()
        
        # Assert
        self.assertIsInstance(mode_name, str)
        self.assertGreater(len(mode_name), 0)

    def test_happy_path_switch_mode_by_name(self):
        """Test switching mode by name"""
        # Arrange
        manager = self.mode_manager
        
        # Act
        success = manager.switch_mode("learn")
        
        # Assert
        self.assertTrue(success)
        self.assertEqual(manager.current_mode, manager.modes["learn"])

    @patch('src.helpmesign.modes.sign_translate.sign_translate_mode.get_text')
    @patch('src.helpmesign.modes.learn.learn_mode.get_text')
    def test_happy_path_switch_mode_by_display_name(self, mock_learn_get_text, mock_sign_get_text):
        """Test switching mode by display name"""
        # Arrange
        mock_sign_get_text.return_value = "Sign & Translate"
        mock_learn_get_text.return_value = "Learn Sign Language"
        manager = self.mode_manager
        
        # Act
        success = manager.switch_mode_by_display_name("Learn Sign Language")
        
        # Assert
        self.assertTrue(success)
        self.assertEqual(manager.current_mode, manager.modes["learn"])

    def test_happy_path_process_text(self):
        """Test processing text with current mode"""
        # Arrange
        manager = self.mode_manager
        test_text = "hello"
        
        # Act
        result = manager.process_text(test_text)
        
        # Assert
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_happy_path_clear_content(self):
        """Test clearing content in current mode"""
        # Arrange
        manager = self.mode_manager
        
        # Act
        manager.clear_content()
        
        # Assert
        # Should not raise any exceptions

    def test_happy_path_get_mode_settings(self):
        """Test getting mode settings"""
        # Arrange
        manager = self.mode_manager
        
        # Act
        settings = manager.get_mode_settings()
        
        # Assert
        self.assertIsInstance(settings, dict)

    def test_happy_path_apply_mode_settings(self):
        """Test applying mode settings"""
        # Arrange
        manager = self.mode_manager
        test_settings = {"key": "value"}
        
        # Act
        manager.apply_mode_settings(test_settings)
        
        # Assert
        # Should not raise any exceptions

    def test_happy_path_get_mode_descriptions(self):
        """Test getting mode descriptions"""
        # Arrange
        manager = self.mode_manager
        
        # Act
        descriptions = manager.get_mode_descriptions()
        
        # Assert
        self.assertIsInstance(descriptions, dict)
        self.assertIn("sign_translate", descriptions)
        self.assertIn("learn", descriptions)
        self.assertEqual(len(descriptions), 2)

    # Error Condition Tests
    def test_error_condition_switch_to_invalid_mode(self):
        """Test switching to invalid mode name"""
        # Arrange
        manager = self.mode_manager
        
        # Act
        success = manager.switch_mode("invalid_mode")
        
        # Assert
        self.assertFalse(success)
        # Current mode should remain unchanged
        self.assertEqual(manager.current_mode, manager.modes["sign_translate"])

    def test_error_condition_switch_to_invalid_display_name(self):
        """Test switching to invalid display name"""
        # Arrange
        manager = self.mode_manager
        
        # Act
        success = manager.switch_mode_by_display_name("Invalid Mode Name")
        
        # Assert
        self.assertFalse(success)
        # Current mode should remain unchanged
        self.assertEqual(manager.current_mode, manager.modes["sign_translate"])

    def test_error_condition_empty_mode_name(self):
        """Test switching to empty mode name"""
        # Arrange
        manager = self.mode_manager
        
        # Act
        success = manager.switch_mode("")
        
        # Assert
        self.assertFalse(success)

    def test_error_condition_none_mode_name(self):
        """Test switching to None mode name"""
        # Arrange
        manager = self.mode_manager
        
        # Act
        success = manager.switch_mode(None)
        
        # Assert
        self.assertFalse(success)

    def test_error_condition_empty_display_name(self):
        """Test switching to empty display name"""
        # Arrange
        manager = self.mode_manager
        
        # Act
        success = manager.switch_mode_by_display_name("")
        
        # Assert
        self.assertFalse(success)

    def test_error_condition_none_display_name(self):
        """Test switching to None display name"""
        # Arrange
        manager = self.mode_manager
        
        # Act
        success = manager.switch_mode_by_display_name(None)
        
        # Assert
        self.assertFalse(success)

    def test_error_condition_process_text_no_current_mode(self):
        """Test processing text when no current mode"""
        # Arrange
        manager = self.mode_manager
        manager.current_mode = None
        
        # Act
        result = manager.process_text("test")
        
        # Assert
        self.assertEqual(result, "No active mode")

    def test_error_condition_clear_content_no_current_mode(self):
        """Test clearing content when no current mode"""
        # Arrange
        manager = self.mode_manager
        manager.current_mode = None
        
        # Act
        manager.clear_content()
        
        # Assert
        # Should not raise any exceptions

    def test_error_condition_get_mode_settings_no_current_mode(self):
        """Test getting settings when no current mode"""
        # Arrange
        manager = self.mode_manager
        manager.current_mode = None
        
        # Act
        settings = manager.get_mode_settings()
        
        # Assert
        self.assertEqual(settings, {})

    def test_error_condition_apply_mode_settings_no_current_mode(self):
        """Test applying settings when no current mode"""
        # Arrange
        manager = self.mode_manager
        manager.current_mode = None
        test_settings = {"key": "value"}
        
        # Act
        manager.apply_mode_settings(test_settings)
        
        # Assert
        # Should not raise any exceptions

    # Exception Tests
    def test_exception_in_switch_mode(self):
        """Test exception handling in mode switching"""
        # Arrange
        manager = self.mode_manager
        # Mock the current mode to raise an exception during deactivation
        manager.current_mode.deactivate = Mock(side_effect=Exception("Deactivation failed"))
        
        # Act
        success = manager.switch_mode("learn")
        
        # Assert
        self.assertFalse(success)

    def test_exception_in_switch_mode_by_display_name(self):
        """Test exception handling in display name mode switching"""
        # Arrange
        manager = self.mode_manager
        # Mock the current mode to raise an exception during deactivation
        manager.current_mode.deactivate = Mock(side_effect=Exception("Deactivation failed"))
        
        # Act
        success = manager.switch_mode_by_display_name("Learn Sign Language")
        
        # Assert
        self.assertFalse(success)

    def test_exception_in_process_text(self):
        """Test exception handling in text processing"""
        # Arrange
        manager = self.mode_manager
        # Mock the current mode to raise an exception during text processing
        manager.current_mode.process_text = Mock(side_effect=Exception("Processing failed"))
        
        # Act & Assert
        with self.assertRaises(Exception):
            manager.process_text("test")

    def test_exception_in_clear_content(self):
        """Test exception handling in content clearing"""
        # Arrange
        manager = self.mode_manager
        # Mock the current mode to raise an exception during content clearing
        manager.current_mode.clear_content = Mock(side_effect=Exception("Clear failed"))
        
        # Act & Assert
        with self.assertRaises(Exception):
            manager.clear_content()

    def test_exception_in_get_mode_settings(self):
        """Test exception handling in getting mode settings"""
        # Arrange
        manager = self.mode_manager
        # Mock the current mode to raise an exception during settings retrieval
        manager.current_mode.get_settings = Mock(side_effect=Exception("Settings failed"))
        
        # Act & Assert
        with self.assertRaises(Exception):
            manager.get_mode_settings()

    def test_exception_in_apply_mode_settings(self):
        """Test exception handling in applying mode settings"""
        # Arrange
        manager = self.mode_manager
        # Mock the current mode to raise an exception during settings application
        manager.current_mode.apply_settings = Mock(side_effect=Exception("Apply failed"))
        test_settings = {"key": "value"}
        
        # Act & Assert
        with self.assertRaises(Exception):
            manager.apply_mode_settings(test_settings)

    # Boundary Condition Tests
    def test_boundary_condition_switch_mode_multiple_times(self):
        """Test switching modes multiple times"""
        # Arrange
        manager = self.mode_manager
        
        # Act
        success1 = manager.switch_mode("learn")
        success2 = manager.switch_mode("sign_translate")
        success3 = manager.switch_mode("learn")
        
        # Assert
        self.assertTrue(success1)
        self.assertTrue(success2)
        self.assertTrue(success3)
        self.assertEqual(manager.current_mode, manager.modes["learn"])

    def test_boundary_condition_switch_to_same_mode(self):
        """Test switching to the same mode"""
        # Arrange
        manager = self.mode_manager
        original_mode = manager.current_mode
        
        # Act
        success = manager.switch_mode("sign_translate")
        
        # Assert
        self.assertTrue(success)
        self.assertEqual(manager.current_mode, original_mode)

    def test_boundary_condition_very_long_text_processing(self):
        """Test processing very long text"""
        # Arrange
        manager = self.mode_manager
        long_text = "hello " * 1000  # 6000 character string
        
        # Act
        result = manager.process_text(long_text)
        
        # Assert
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    @patch('src.helpmesign.modes.sign_translate.sign_translate_mode.get_text')
    def test_boundary_condition_empty_text_processing(self, mock_get_text):
        """Test processing empty text"""
        # Arrange
        mock_get_text.return_value = "Please enter some text."
        manager = self.mode_manager
        empty_text = ""
        
        # Act
        result = manager.process_text(empty_text)
        
        # Assert
        self.assertIsInstance(result, str)

    def test_boundary_condition_unicode_text_processing(self):
        """Test processing unicode text"""
        # Arrange
        manager = self.mode_manager
        unicode_text = "Hello 世界 🌍 🚀"
        
        # Act
        result = manager.process_text(unicode_text)
        
        # Assert
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_boundary_condition_special_characters_text_processing(self):
        """Test processing text with special characters"""
        # Arrange
        manager = self.mode_manager
        special_text = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        # Act
        result = manager.process_text(special_text)
        
        # Assert
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_boundary_condition_none_text_processing(self):
        """Test processing None text"""
        # Arrange
        manager = self.mode_manager
        
        # Act & Assert
        with self.assertRaises(AttributeError):
            manager.process_text(None)

    def test_boundary_condition_non_string_text_processing(self):
        """Test processing non-string text"""
        # Arrange
        manager = self.mode_manager
        
        # Act & Assert
        with self.assertRaises(AttributeError):
            manager.process_text(123)
        
        with self.assertRaises(AttributeError):
            manager.process_text(["list", "of", "strings"])
        
        with self.assertRaises(AttributeError):
            manager.process_text({"key": "value"})

    def test_boundary_condition_environment_values(self):
        """Test different environment values"""
        # Arrange & Act
        manager_dev = ModeManager(self.mock_main_window, "dev")
        manager_prod = ModeManager(self.mock_main_window, "prod")
        manager_test = ModeManager(self.mock_main_window, "test")
        
        # Assert
        self.assertEqual(manager_dev.environment, "dev")
        self.assertEqual(manager_prod.environment, "prod")
        self.assertEqual(manager_test.environment, "test")

    def test_boundary_condition_empty_environment(self):
        """Test empty environment string"""
        # Arrange & Act
        manager = ModeManager(self.mock_main_window, "")
        
        # Assert
        self.assertEqual(manager.environment, "")

    # Mock Tests
    def test_mock_main_window_interaction(self):
        """Test interaction with mocked main window"""
        # Arrange
        mock_window = Mock()
        mock_window.set_mode = Mock()
        mock_window.set_status = Mock()
        
        # Act
        manager = ModeManager(mock_window, "dev")
        
        # Assert
        self.assertEqual(manager.main_window, mock_window)
        self.assertIsNotNone(manager.current_mode)

    # Integration Tests (within unit test scope)
    @patch('src.helpmesign.modes.sign_translate.sign_translate_mode.get_text')
    @patch('src.helpmesign.modes.learn.learn_mode.get_text')
    def test_integration_complete_mode_switching_workflow(self, mock_learn_get_text, mock_sign_get_text):
        """Test complete mode switching workflow"""
        # Arrange
        mock_sign_get_text.return_value = "Sign & Translate"
        mock_learn_get_text.return_value = "Learn Sign Language"
        manager = self.mode_manager
        
        # Act
        # Switch to learn mode
        success1 = manager.switch_mode("learn")
        mode1 = manager.get_current_mode()
        name1 = manager.get_current_mode_name()
        
        # Switch back to sign translate mode
        success2 = manager.switch_mode("sign_translate")
        mode2 = manager.get_current_mode()
        name2 = manager.get_current_mode_name()
        
        # Assert
        self.assertTrue(success1)
        self.assertTrue(success2)
        self.assertEqual(mode1, manager.modes["learn"])
        self.assertEqual(mode2, manager.modes["sign_translate"])
        self.assertNotEqual(name1, name2)

    def test_integration_mode_lifecycle_with_switching(self):
        """Test complete mode lifecycle with switching"""
        # Arrange
        manager = self.mode_manager
        
        # Act - Complete lifecycle
        # Start with sign translate mode
        initial_mode = manager.get_current_mode()
        initial_name = manager.get_current_mode_name()
        
        # Switch to learn mode
        success = manager.switch_mode("learn")
        learn_mode = manager.get_current_mode()
        learn_name = manager.get_current_mode_name()
        
        # Process text in learn mode
        result = manager.process_text("hello")
        
        # Switch back to sign translate mode
        success2 = manager.switch_mode("sign_translate")
        final_mode = manager.get_current_mode()
        
        # Assert
        self.assertTrue(success)
        self.assertTrue(success2)
        self.assertEqual(initial_mode, manager.modes["sign_translate"])
        self.assertEqual(learn_mode, manager.modes["learn"])
        self.assertEqual(final_mode, manager.modes["sign_translate"])
        self.assertIsInstance(result, str)

    def test_integration_all_modes_functionality(self):
        """Test functionality of all available modes"""
        # Arrange
        manager = self.mode_manager
        test_text = "hello"
        
        # Act
        # Test sign translate mode
        manager.switch_mode("sign_translate")
        sign_result = manager.process_text(test_text)
        
        # Test learn mode
        manager.switch_mode("learn")
        learn_result = manager.process_text(test_text)
        
        # Get settings from both modes
        sign_settings = manager.get_mode_settings()
        manager.switch_mode("sign_translate")
        learn_settings = manager.get_mode_settings()
        
        # Assert
        self.assertIsInstance(sign_result, str)
        self.assertIsInstance(learn_result, str)
        self.assertIsInstance(sign_settings, dict)
        self.assertIsInstance(learn_settings, dict)
        self.assertNotEqual(sign_result, learn_result)  # Different modes should produce different results


if __name__ == '__main__':
    unittest.main() 