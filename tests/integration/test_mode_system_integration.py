"""
Integration tests for the mode system
Tests interactions between modes, mode manager, and main application
"""

import os
import shutil
import tempfile
import unittest
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

from src.helpmesign.modes.base_mode import BaseMode
from src.helpmesign.modes.learn.learn_mode import LearnMode

# Import the mode system components
from src.helpmesign.modes.mode_manager import ModeManager
from src.helpmesign.modes.sign_translate.sign_translate_mode import SignTranslateMode


class TestModeSystemIntegration(unittest.TestCase):
    """Integration tests for the mode system"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a mock main window with all required methods
        self.mock_main_window = Mock()
        self.mock_main_window.set_mode = Mock()
        self.mock_main_window.set_status = Mock()
        self.mock_main_window.get_text_input = Mock()
        self.mock_main_window.set_text_output = Mock()
        self.mock_main_window.set_text_input = Mock()

        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()

        # Create the mode manager instance
        self.mode_manager = ModeManager(self.mock_main_window, "dev")

    def tearDown(self):
        """Clean up after tests"""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # Happy Path Integration Tests
    def test_happy_path_mode_manager_with_sign_translate_mode(self):
        """Test mode manager integration with sign translate mode"""
        # Arrange
        manager = self.mode_manager

        # Act
        # Switch to sign translate mode
        success = manager.switch_mode("sign_translate")
        current_mode = manager.get_current_mode()
        mode_name = manager.get_current_mode_name()

        # Process text
        result = manager.process_text("hello")

        # Assert
        self.assertTrue(success)
        self.assertIsInstance(current_mode, SignTranslateMode)
        self.assertIsInstance(mode_name, str)
        self.assertGreater(len(mode_name), 0)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_happy_path_mode_manager_with_learn_mode(self):
        """Test mode manager integration with learn mode"""
        # Arrange
        manager = self.mode_manager

        # Act
        # Switch to learn mode
        success = manager.switch_mode("learn")
        current_mode = manager.get_current_mode()
        mode_name = manager.get_current_mode_name()

        # Process text
        result = manager.process_text("hello")

        # Assert
        self.assertTrue(success)
        self.assertIsInstance(current_mode, LearnMode)
        self.assertIsInstance(mode_name, str)
        self.assertGreater(len(mode_name), 0)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_happy_path_mode_switching_integration(self):
        """Test complete mode switching integration"""
        # Arrange
        manager = self.mode_manager

        # Act
        # Start with sign translate mode
        manager.switch_mode("sign_translate")
        sign_result = manager.process_text("hello")
        sign_mode = manager.get_current_mode()

        # Switch to learn mode
        manager.switch_mode("learn")
        learn_result = manager.process_text("hello")
        learn_mode = manager.get_current_mode()

        # Switch back to sign translate mode
        manager.switch_mode("sign_translate")
        final_mode = manager.get_current_mode()

        # Assert
        self.assertIsInstance(sign_mode, SignTranslateMode)
        self.assertIsInstance(learn_mode, LearnMode)
        self.assertIsInstance(final_mode, SignTranslateMode)
        self.assertIsInstance(sign_result, str)
        self.assertIsInstance(learn_result, str)
        self.assertNotEqual(
            sign_result, learn_result
        )  # Different modes should produce different results

    def test_happy_path_mode_settings_integration(self):
        """Test mode settings integration"""
        # Arrange
        manager = self.mode_manager

        # Act
        # Test sign translate mode settings
        manager.switch_mode("sign_translate")
        sign_settings = manager.get_mode_settings()

        # Test learn mode settings
        manager.switch_mode("learn")
        learn_settings = manager.get_mode_settings()

        # Apply settings to both modes
        test_settings = {"test_key": "test_value"}
        manager.apply_mode_settings(test_settings)

        # Assert
        self.assertIsInstance(sign_settings, dict)
        self.assertIsInstance(learn_settings, dict)
        self.assertIn("mode", sign_settings)
        self.assertIn("mode", learn_settings)
        self.assertEqual(sign_settings["mode"], "sign_translate")
        self.assertEqual(learn_settings["mode"], "learn")

    def test_happy_path_mode_descriptions_integration(self):
        """Test mode descriptions integration"""
        # Arrange
        manager = self.mode_manager

        # Act
        descriptions = manager.get_mode_descriptions()

        # Assert
        self.assertIsInstance(descriptions, dict)
        self.assertIn("sign_translate", descriptions)
        self.assertIn("learn", descriptions)
        self.assertIsInstance(descriptions["sign_translate"], str)
        self.assertIsInstance(descriptions["learn"], str)
        self.assertGreater(len(descriptions["sign_translate"]), 0)
        self.assertGreater(len(descriptions["learn"]), 0)

    def test_happy_path_mode_lifecycle_integration(self):
        """Test complete mode lifecycle integration"""
        # Arrange
        manager = self.mode_manager

        # Act
        # Complete lifecycle for sign translate mode
        manager.switch_mode("sign_translate")
        sign_mode = manager.get_current_mode()
        sign_mode.activate()
        sign_result = manager.process_text("hello")
        sign_settings = manager.get_mode_settings()
        manager.clear_content()
        sign_mode.deactivate()

        # Complete lifecycle for learn mode
        manager.switch_mode("learn")
        learn_mode = manager.get_current_mode()
        learn_mode.activate()
        learn_result = manager.process_text("hello")
        learn_settings = manager.get_mode_settings()
        manager.clear_content()
        learn_mode.deactivate()

        # Assert
        self.assertIsInstance(sign_mode, SignTranslateMode)
        self.assertIsInstance(learn_mode, LearnMode)
        self.assertIsInstance(sign_result, str)
        self.assertIsInstance(learn_result, str)
        self.assertIsInstance(sign_settings, dict)
        self.assertIsInstance(learn_settings, dict)

    # Error Condition Integration Tests
    def test_error_condition_mode_switching_with_invalid_mode(self):
        """Test mode switching with invalid mode"""
        # Arrange
        manager = self.mode_manager
        original_mode = manager.get_current_mode()

        # Act
        success = manager.switch_mode("invalid_mode")
        current_mode = manager.get_current_mode()

        # Assert
        self.assertFalse(success)
        self.assertEqual(current_mode, original_mode)  # Should remain unchanged

    def test_error_condition_mode_switching_with_empty_mode(self):
        """Test mode switching with empty mode name"""
        # Arrange
        manager = self.mode_manager
        original_mode = manager.get_current_mode()

        # Act
        success = manager.switch_mode("")
        current_mode = manager.get_current_mode()

        # Assert
        self.assertFalse(success)
        self.assertEqual(current_mode, original_mode)  # Should remain unchanged

    def test_error_condition_mode_switching_with_none_mode(self):
        """Test mode switching with None mode name"""
        # Arrange
        manager = self.mode_manager
        original_mode = manager.get_current_mode()

        # Act
        success = manager.switch_mode(None)
        current_mode = manager.get_current_mode()

        # Assert
        self.assertFalse(success)
        self.assertEqual(current_mode, original_mode)  # Should remain unchanged

    def test_error_condition_empty_text_processing_integration(self):
        """Test empty text processing across modes"""
        # Arrange
        manager = self.mode_manager

        # Act
        # Test empty text in sign translate mode
        manager.switch_mode("sign_translate")
        sign_result = manager.process_text("")

        # Test empty text in learn mode
        manager.switch_mode("learn")
        learn_result = manager.process_text("")

        # Assert
        self.assertIsInstance(sign_result, str)
        self.assertIsInstance(learn_result, str)

    def test_error_condition_whitespace_text_processing_integration(self):
        """Test whitespace text processing across modes"""
        # Arrange
        manager = self.mode_manager
        whitespace_text = "   \n\t   "

        # Act
        # Test whitespace text in sign translate mode
        manager.switch_mode("sign_translate")
        sign_result = manager.process_text(whitespace_text)

        # Test whitespace text in learn mode
        manager.switch_mode("learn")
        learn_result = manager.process_text(whitespace_text)

        # Assert
        self.assertIsInstance(sign_result, str)
        self.assertIsInstance(learn_result, str)

    # Exception Integration Tests
    def test_exception_integration_mode_switching_failure(self):
        """Test exception handling during mode switching"""
        # Arrange
        manager = self.mode_manager
        # Mock the current mode to raise an exception during deactivation
        manager.current_mode.deactivate = Mock(
            side_effect=Exception("Deactivation failed")
        )

        # Act
        success = manager.switch_mode("learn")

        # Assert
        self.assertFalse(success)

    def test_exception_integration_text_processing_failure(self):
        """Test exception handling during text processing"""
        # Arrange
        manager = self.mode_manager
        # Mock the current mode to raise an exception during text processing
        manager.current_mode.process_text = Mock(
            side_effect=Exception("Processing failed")
        )

        # Act & Assert
        with self.assertRaises(Exception):
            manager.process_text("test")

    def test_exception_integration_settings_failure(self):
        """Test exception handling during settings operations"""
        # Arrange
        manager = self.mode_manager
        # Mock the current mode to raise an exception during settings retrieval
        manager.current_mode.get_settings = Mock(
            side_effect=Exception("Settings failed")
        )

        # Act & Assert
        with self.assertRaises(Exception):
            manager.get_mode_settings()

    # Boundary Condition Integration Tests
    def test_boundary_condition_very_long_text_integration(self):
        """Test very long text processing across modes"""
        # Arrange
        manager = self.mode_manager
        long_text = "hello " * 1000  # 6000 character string

        # Act
        # Test long text in sign translate mode
        manager.switch_mode("sign_translate")
        sign_result = manager.process_text(long_text)

        # Test long text in learn mode
        manager.switch_mode("learn")
        learn_result = manager.process_text(long_text)

        # Assert
        self.assertIsInstance(sign_result, str)
        self.assertIsInstance(learn_result, str)
        self.assertGreater(len(sign_result), 0)
        self.assertGreater(len(learn_result), 0)

    def test_boundary_condition_unicode_text_integration(self):
        """Test unicode text processing across modes"""
        # Arrange
        manager = self.mode_manager
        unicode_text = "Hello 世界 🌍 🚀"

        # Act
        # Test unicode text in sign translate mode
        manager.switch_mode("sign_translate")
        sign_result = manager.process_text(unicode_text)

        # Test unicode text in learn mode
        manager.switch_mode("learn")
        learn_result = manager.process_text(unicode_text)

        # Assert
        self.assertIsInstance(sign_result, str)
        self.assertIsInstance(learn_result, str)
        self.assertGreater(len(sign_result), 0)
        self.assertGreater(len(learn_result), 0)

    def test_boundary_condition_special_characters_integration(self):
        """Test special characters processing across modes"""
        # Arrange
        manager = self.mode_manager
        special_text = "!@#$%^&*()_+-=[]{}|;':\",./<>?"

        # Act
        # Test special characters in sign translate mode
        manager.switch_mode("sign_translate")
        sign_result = manager.process_text(special_text)

        # Test special characters in learn mode
        manager.switch_mode("learn")
        learn_result = manager.process_text(special_text)

        # Assert
        self.assertIsInstance(sign_result, str)
        self.assertIsInstance(learn_result, str)
        self.assertGreater(len(sign_result), 0)
        self.assertGreater(len(learn_result), 0)

    def test_boundary_condition_multiple_mode_switches_integration(self):
        """Test multiple mode switches in sequence"""
        # Arrange
        manager = self.mode_manager

        # Act
        # Perform multiple mode switches
        switches = []
        for i in range(10):
            mode_name = "sign_translate" if i % 2 == 0 else "learn"
            success = manager.switch_mode(mode_name)
            current_mode = manager.get_current_mode()
            switches.append((success, type(current_mode)))

        # Assert
        for success, mode_type in switches:
            self.assertTrue(success)
            self.assertIn(mode_type, [SignTranslateMode, LearnMode])

    def test_boundary_condition_rapid_mode_switching_integration(self):
        """Test rapid mode switching"""
        # Arrange
        manager = self.mode_manager

        # Act
        # Rapidly switch between modes
        for i in range(50):
            mode_name = "sign_translate" if i % 2 == 0 else "learn"
            success = manager.switch_mode(mode_name)
            if not success:
                break

        # Assert
        self.assertTrue(success)  # All switches should succeed
        self.assertIsNotNone(manager.get_current_mode())

    # Mock Integration Tests
    def test_mock_integration_main_window_interaction(self):
        """Test integration with mocked main window"""
        # Arrange
        mock_window = Mock()
        mock_window.set_mode = Mock()
        mock_window.set_status = Mock()
        mock_window.get_text_input = Mock(return_value="test")
        mock_window.set_text_output = Mock()
        mock_window.set_text_input = Mock()

        # Act
        manager = ModeManager(mock_window, "dev")
        manager.switch_mode("sign_translate")
        # Process text to trigger main window interaction
        manager.process_text("hello")

        # Assert
        mock_window.set_mode.assert_called()
        # The process_text call should trigger some main window interaction
        # but the exact calls depend on the mode implementation

    # Complex Integration Tests
    def test_complex_integration_complete_workflow(self):
        """Test complete workflow integration"""
        # Arrange
        manager = self.mode_manager
        test_texts = ["hello", "thanks", "yes", "no", "please", "sorry"]

        # Act
        results = {}
        settings = {}

        # Test sign translate mode
        manager.switch_mode("sign_translate")
        sign_results = []
        for text in test_texts:
            result = manager.process_text(text)
            sign_results.append(result)
        results["sign_translate"] = sign_results
        settings["sign_translate"] = manager.get_mode_settings()

        # Test learn mode
        manager.switch_mode("learn")
        learn_results = []
        for text in test_texts:
            result = manager.process_text(text)
            learn_results.append(result)
        results["learn"] = learn_results
        settings["learn"] = manager.get_mode_settings()

        # Assert
        self.assertIn("sign_translate", results)
        self.assertIn("learn", results)
        self.assertIn("sign_translate", settings)
        self.assertIn("learn", settings)

        # Check that all results are strings
        for mode_results in results.values():
            for result in mode_results:
                self.assertIsInstance(result, str)
                self.assertGreater(len(result), 0)

        # Check that all settings are dictionaries
        for mode_settings in settings.values():
            self.assertIsInstance(mode_settings, dict)

    def test_complex_integration_mode_persistence(self):
        """Test mode persistence across operations"""
        # Arrange
        manager = self.mode_manager

        # Act
        # Switch to learn mode and perform operations
        manager.switch_mode("learn")
        learn_mode = manager.get_current_mode()
        learn_result1 = manager.process_text("hello")
        learn_result2 = manager.process_text("thanks")

        # Switch to sign translate mode and perform operations
        manager.switch_mode("sign_translate")
        sign_mode = manager.get_current_mode()
        sign_result1 = manager.process_text("hello")
        sign_result2 = manager.process_text("thanks")

        # Switch back to learn mode
        manager.switch_mode("learn")
        final_mode = manager.get_current_mode()
        learn_result3 = manager.process_text("yes")

        # Assert
        self.assertIsInstance(learn_mode, LearnMode)
        self.assertIsInstance(sign_mode, SignTranslateMode)
        self.assertIsInstance(final_mode, LearnMode)
        self.assertEqual(learn_mode, final_mode)  # Should be the same instance

        # Check that results are different between modes
        self.assertNotEqual(learn_result1, sign_result1)
        self.assertNotEqual(learn_result2, sign_result2)

    def test_complex_integration_error_recovery(self):
        """Test error recovery in mode system"""
        # Arrange
        manager = self.mode_manager

        # Act
        # Try to switch to invalid mode (should fail)
        invalid_success = manager.switch_mode("invalid_mode")
        mode_after_invalid = manager.get_current_mode()

        # Switch to valid mode (should succeed)
        valid_success = manager.switch_mode("learn")
        mode_after_valid = manager.get_current_mode()

        # Process text in valid mode
        result = manager.process_text("hello")

        # Assert
        self.assertFalse(invalid_success)
        self.assertTrue(valid_success)
        self.assertIsInstance(
            mode_after_invalid, SignTranslateMode
        )  # Should remain unchanged
        self.assertIsInstance(mode_after_valid, LearnMode)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


if __name__ == "__main__":
    unittest.main()
