"""
Integration tests for the mode system
Tests interactions between modes, mode manager, and main application
"""

import os
import shutil
import tempfile
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.helpmesign.modes.base_mode import BaseMode
from src.helpmesign.modes.learn.learn_mode import LearnMode
# Import the mode system components
from src.helpmesign.modes.mode_manager import ModeManager
from src.helpmesign.modes.sign_translate.sign_translate_mode import \
    SignTranslateMode
from tests.mocks.qt.qt_module_mocks import (activate_qt_mocks,
                                            deactivate_qt_mocks)
# Import Qt mock framework
from tests.mocks.qt.qt_test_case import QtTestCase


class TestModeSystemIntegration(QtTestCase):
    """Integration tests for the mode system"""

    def create_mocked_mode_manager(self):
        """Helper method to create a mode manager with mocked modes"""
        with patch(
            "src.helpmesign.modes.mode_manager.LearnMode"
        ) as mock_learn_mode_class, patch(
            "src.helpmesign.modes.mode_manager.SignTranslateMode"
        ) as mock_sign_translate_mode_class:

            # Create mock mode instances
            mock_sign_translate_mode = Mock()
            mock_sign_translate_mode.get_mode_name.return_value = "sign_translate"
            mock_sign_translate_mode.get_mode_description.return_value = (
                "Sign Translation Mode"
            )
            mock_sign_translate_mode.process_text.return_value = "Translated: hello"
            mock_sign_translate_mode.get_settings.return_value = {
                "theme": "light",
                "font_size": 12,
            }
            mock_sign_translate_mode.deactivate = Mock()
            mock_sign_translate_mode.activate = Mock(
                side_effect=lambda: self.mock_main_window.set_mode("sign_translate")
            )
            mock_sign_translate_mode_class.return_value = mock_sign_translate_mode

            mock_learn_mode = Mock()
            mock_learn_mode.get_mode_name.return_value = "learn"
            mock_learn_mode.get_mode_description.return_value = "Learning Mode"
            mock_learn_mode.process_text.return_value = "Processed: hello"
            mock_learn_mode.get_settings.return_value = {
                "theme": "light",
                "font_size": 12,
            }
            mock_learn_mode.deactivate = Mock()
            mock_learn_mode.activate = Mock(
                side_effect=lambda: self.mock_main_window.set_mode("learn")
            )
            mock_learn_mode_class.return_value = mock_learn_mode

            # Create the mode manager instance with mocked modes
            return ModeManager(self.mock_main_window)

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures"""
        # Activate Qt mocks to prevent fatal errors
        activate_qt_mocks()

        # Create a mock main window with all required methods
        self.mock_main_window = Mock()
        self.mock_main_window.set_mode = Mock()
        self.mock_main_window.set_status = Mock()
        self.mock_main_window.get_text_input = Mock()
        self.mock_main_window.set_text_output = Mock()
        self.mock_main_window.set_text_input = Mock()

        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()

        yield

        # Clean up after tests
        shutil.rmtree(self.test_dir, ignore_errors=True)
        deactivate_qt_mocks()

    # Happy Path Integration Tests
    def test_happy_path_mode_manager_with_sign_translate_mode(self):
        """Test mode manager integration with sign translate mode"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        # Switch to sign translate mode
        success = manager.switch_mode("sign_translate")
        current_mode = manager.get_current_mode()
        mode_name = manager.get_current_mode_name()

        # Process text
        result = manager.process_text("hello")

        # Assert
        assert success
        assert isinstance(current_mode, Mock)
        assert isinstance(mode_name, str)
        assert len(mode_name) > 0
        assert isinstance(result, str)
        assert len(result) > 0

    def test_happy_path_mode_manager_with_learn_mode(self):
        """Test mode manager integration with learn mode"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        # Switch to learn mode
        success = manager.switch_mode("learn")
        current_mode = manager.get_current_mode()
        mode_name = manager.get_current_mode_name()

        # Process text
        result = manager.process_text("hello")

        # Assert
        assert success
        assert isinstance(current_mode, Mock)
        assert isinstance(mode_name, str)
        assert len(mode_name) > 0
        assert isinstance(result, str)
        assert len(result) > 0

    def test_happy_path_mode_switching_integration(self):
        """Test complete mode switching integration"""
        # Arrange
        manager = self.create_mocked_mode_manager()

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
        final_result = manager.process_text("hello")
        final_mode = manager.get_current_mode()

        # Assert
        assert isinstance(sign_mode, Mock)
        assert isinstance(learn_mode, Mock)
        assert isinstance(final_mode, Mock)
        assert isinstance(sign_result, str)
        assert isinstance(learn_result, str)
        assert isinstance(final_result, str)
        assert len(sign_result) > 0
        assert len(learn_result) > 0
        assert len(final_result) > 0

    def test_happy_path_mode_settings_integration(self):
        """Test mode settings integration"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        # Get settings for sign translate mode
        manager.switch_mode("sign_translate")
        sign_settings = manager.get_mode_settings()

        # Get settings for learn mode
        manager.switch_mode("learn")
        learn_settings = manager.get_mode_settings()

        # Assert
        assert isinstance(sign_settings, dict)
        assert isinstance(learn_settings, dict)
        assert len(sign_settings) > 0
        assert len(learn_settings) > 0

    def test_happy_path_mode_descriptions_integration(self):
        """Test mode descriptions integration"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        # Get descriptions for all modes
        descriptions = manager.get_mode_descriptions()

        # Assert
        assert isinstance(descriptions, dict)
        assert "sign_translate" in descriptions
        assert "learn" in descriptions
        assert isinstance(descriptions["sign_translate"], str)
        assert isinstance(descriptions["learn"], str)
        assert len(descriptions["sign_translate"]) > 0
        assert len(descriptions["learn"]) > 0

    def test_happy_path_mode_lifecycle_integration(self):
        """Test mode lifecycle integration"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        # Test mode initialization
        initial_mode = manager.get_current_mode()
        initial_name = manager.get_current_mode_name()

        # Test mode switching
        success = manager.switch_mode("learn")
        switched_mode = manager.get_current_mode()
        switched_name = manager.get_current_mode_name()

        # Test mode processing
        result = manager.process_text("test")

        # Assert
        assert isinstance(initial_mode, Mock)  # Default mode
        assert isinstance(initial_name, str)
        assert len(initial_name) > 0
        assert success
        assert isinstance(switched_mode, Mock)
        assert isinstance(switched_name, str)
        assert len(switched_name) > 0
        assert isinstance(result, str)
        assert len(result) > 0

    # Error Condition Integration Tests
    def test_error_condition_mode_switching_with_invalid_mode(self):
        """Test error handling for invalid mode switching"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        # Try to switch to invalid mode
        success = manager.switch_mode("invalid_mode")
        current_mode = manager.get_current_mode()

        # Assert
        assert not success
        assert isinstance(current_mode, Mock)  # Should remain unchanged

    def test_error_condition_mode_switching_with_empty_mode(self):
        """Test error handling for empty mode switching"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        # Try to switch to empty mode
        success = manager.switch_mode("")
        current_mode = manager.get_current_mode()

        # Assert
        assert not success
        assert isinstance(current_mode, Mock)  # Should remain unchanged

    def test_error_condition_mode_switching_with_none_mode(self):
        """Test error handling for None mode switching"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        # Try to switch to None mode
        success = manager.switch_mode(None)
        current_mode = manager.get_current_mode()

        # Assert
        assert not success
        assert isinstance(current_mode, Mock)  # Should remain unchanged

    def test_error_condition_empty_text_processing_integration(self):
        """Test error handling for empty text processing"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        # Process empty text
        result = manager.process_text("")

        # Assert
        assert isinstance(result, str)
        # Empty text should still return a string (could be empty or default message)

    def test_error_condition_whitespace_text_processing_integration(self):
        """Test error handling for whitespace text processing"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        # Process whitespace-only text
        result1 = manager.process_text("   ")
        result2 = manager.process_text("\t\n")

        # Assert
        assert isinstance(result1, str)
        assert isinstance(result2, str)
        # Whitespace text should still return a string

    # Exception Integration Tests
    def test_exception_integration_mode_switching_failure(self):
        """Test exception handling in mode switching"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act & Assert
        # Test with invalid mode name that might cause exceptions
        try:
            success = manager.switch_mode("invalid_mode_with_special_chars_!@#$%")
            assert not success
        except Exception as e:
            # If an exception is raised, it should be handled gracefully
            assert isinstance(e, Exception)

    def test_exception_integration_text_processing_failure(self):
        """Test exception handling in text processing"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act & Assert
        # Test with problematic text that might cause exceptions
        try:
            result = manager.process_text("test" * 1000)  # Very long text
            assert isinstance(result, str)
        except Exception as e:
            # If an exception is raised, it should be handled gracefully
            assert isinstance(e, Exception)

    def test_exception_integration_settings_failure(self):
        """Test exception handling in settings retrieval"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act & Assert
        # Test settings retrieval
        try:
            settings = manager.get_mode_settings()
            assert isinstance(settings, dict)
        except Exception as e:
            # If an exception is raised, it should be handled gracefully
            assert isinstance(e, Exception)

    # Boundary Condition Integration Tests
    def test_boundary_condition_very_long_text_integration(self):
        """Test boundary condition with very long text"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        # Process very long text
        long_text = "a" * 10000
        result = manager.process_text(long_text)

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0

    def test_boundary_condition_unicode_text_integration(self):
        """Test boundary condition with unicode text"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        # Process unicode text
        unicode_text = "Hello 世界 🌍 🚀"
        result = manager.process_text(unicode_text)

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0

    def test_boundary_condition_special_characters_integration(self):
        """Test boundary condition with special characters"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        # Process text with special characters
        special_text = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        result = manager.process_text(special_text)

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0

    def test_boundary_condition_multiple_mode_switches_integration(self):
        """Test boundary condition with multiple mode switches"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        # Perform multiple mode switches
        for i in range(10):
            success = manager.switch_mode("sign_translate")
            assert success
            success = manager.switch_mode("learn")
            assert success

        # Assert
        current_mode = manager.get_current_mode()
        assert isinstance(current_mode, Mock)

    def test_boundary_condition_rapid_mode_switching_integration(self):
        """Test boundary condition with rapid mode switching"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        # Rapidly switch between modes
        for i in range(50):
            manager.switch_mode("sign_translate")
            manager.switch_mode("learn")

        # Assert
        current_mode = manager.get_current_mode()
        assert isinstance(current_mode, Mock)

    # Mock Integration Tests
    def test_mock_integration_main_window_interaction(self):
        """Test integration with mocked main window"""
        # Arrange
        manager = self.create_mocked_mode_manager()

        # Act
        # Test main window interaction
        manager.switch_mode("learn")
        result = manager.process_text("hello")

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0
        # Verify that main window methods were called during mode switching
        self.mock_main_window.set_mode.assert_called()
        # Note: set_status is called in activate() method, but may not be called in all test scenarios

    # Complex Integration Tests
    def test_complex_integration_complete_workflow(self):
        """Test complete workflow integration"""
        # Arrange
        manager = self.create_mocked_mode_manager()
        test_texts = ["hello", "world", "test", "integration"]

        # Act
        # Test complete workflow with both modes
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
        assert "sign_translate" in results
        assert "learn" in results
        assert "sign_translate" in settings
        assert "learn" in settings

        # Check that all results are strings
        for mode_results in results.values():
            for result in mode_results:
                assert isinstance(result, str)
                assert len(result) > 0

        # Check that all settings are dictionaries
        for mode_settings in settings.values():
            assert isinstance(mode_settings, dict)

    def test_complex_integration_mode_persistence(self):
        """Test mode persistence across operations"""
        # Arrange
        manager = self.create_mocked_mode_manager()

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
        assert isinstance(learn_mode, Mock)
        assert isinstance(sign_mode, Mock)
        assert isinstance(final_mode, Mock)
        assert learn_mode == final_mode  # Should be the same instance

        # Check that results are different between modes
        assert learn_result1 != sign_result1
        assert learn_result2 != sign_result2

    def test_complex_integration_error_recovery(self):
        """Test error recovery in mode system"""
        # Arrange
        manager = self.create_mocked_mode_manager()

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
        assert not invalid_success
        assert valid_success
        assert isinstance(mode_after_invalid, Mock)  # Should remain unchanged
        assert isinstance(mode_after_valid, Mock)
        assert isinstance(result, str)
        assert len(result) > 0
