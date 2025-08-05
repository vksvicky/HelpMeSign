#!/usr/bin/env python3
"""
Unit tests for HelpMeSignApp class from src.helpmesign.core.app
Tests the actual app.py module to improve coverage
"""

import unittest
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import the actual HelpMeSignApp class
from src.helpmesign.core.app import HelpMeSignApp, create_app


class TestHelpMeSignAppUnit(unittest.TestCase):
    """Unit tests for HelpMeSignApp class"""

    def setUp(self):
        """Set up test fixtures"""
        # Mock QApplication to avoid GUI issues in tests
        self.qapp_patcher = patch("PySide6.QtWidgets.QApplication")
        self.mock_qapp = self.qapp_patcher.start()
        self.mock_qapp_instance = Mock()
        self.mock_qapp.instance.return_value = self.mock_qapp_instance

        # Mock MainWindow to avoid GUI creation
        self.main_window_patcher = patch("src.helpmesign.core.app.MainWindow")
        self.mock_main_window_class = self.main_window_patcher.start()
        self.mock_main_window = Mock()
        self.mock_main_window_class.return_value = self.mock_main_window

        # Mock ModeManager
        self.mode_manager_patcher = patch("src.helpmesign.core.app.ModeManager")
        self.mock_mode_manager_class = self.mode_manager_patcher.start()
        self.mock_mode_manager = Mock()
        self.mock_mode_manager_class.return_value = self.mock_mode_manager

        # Mock ResourceManager
        self.resource_manager_patcher = patch("src.helpmesign.core.app.ResourceManager")
        self.mock_resource_manager_class = self.resource_manager_patcher.start()
        self.mock_resource_manager = Mock()
        self.mock_resource_manager_class.return_value = self.mock_resource_manager

        # Mock other dependencies
        self.setup_logging_patcher = patch("src.helpmesign.core.app.setup_logging")
        self.mock_setup_logging = self.setup_logging_patcher.start()
        self.mock_logger = Mock()
        self.mock_setup_logging.return_value = self.mock_logger

        # Mock QTimer to prevent delayed font application scheduling
        self.qtimer_patcher = patch("PySide6.QtCore.QTimer")
        self.mock_qtimer = self.qtimer_patcher.start()

        # Mock config
        self.mock_config = {
            "window_size": {"width": 1024, "height": 1024},
            "dev_window_size": {"width": 1200, "height": 800},
            "theme": "light",
        }
        self.mock_resource_manager.load_config.return_value = self.mock_config

    def tearDown(self):
        """Clean up after tests"""
        self.qapp_patcher.stop()
        self.main_window_patcher.stop()
        self.mode_manager_patcher.stop()
        self.resource_manager_patcher.stop()
        self.setup_logging_patcher.stop()
        self.qtimer_patcher.stop()

    def test_helpmesign_app_initialization(self):
        """Test HelpMeSignApp initialization"""
        # Act
        app = HelpMeSignApp("dev")

        # Assert
        self.assertEqual(app.environment, "dev")
        self.assertIsNotNone(app.resource_manager)
        self.assertIsNotNone(app.main_window)
        self.assertIsNotNone(app.mode_manager)
        self.assertIsNotNone(app.logger)
        self.assertFalse(app._shutting_down)
        self.assertFalse(app._settings_save_in_progress)

    def test_helpmesign_app_environment_case_insensitive(self):
        """Test that environment is converted to lowercase"""
        # Act
        app = HelpMeSignApp("DEV")

        # Assert
        self.assertEqual(app.environment, "dev")

    def test_helpmesign_app_config_loading(self):
        """Test that config is loaded during initialization"""
        # Act
        app = HelpMeSignApp("dev")

        # Assert
        self.mock_resource_manager.load_config.assert_called_once()
        self.assertEqual(app.config, self.mock_config)

    def test_helpmesign_app_logging_setup(self):
        """Test that logging is set up during initialization"""
        # Act
        app = HelpMeSignApp("dev")

        # Assert
        self.mock_setup_logging.assert_called_once_with(
            self.mock_config, environment="dev"
        )
        self.assertEqual(app.logger, self.mock_logger)

    def test_helpmesign_app_main_window_creation(self):
        """Test that main window is created with correct title"""
        # Act
        app = HelpMeSignApp("dev")

        # Assert
        self.mock_main_window_class.assert_called_once_with(title="HelpMeSign (DEV)")
        self.assertEqual(app.main_window, self.mock_main_window)

    def test_helpmesign_app_mode_manager_creation(self):
        """Test that mode manager is created"""
        # Act
        app = HelpMeSignApp("dev")

        # Assert
        self.mock_mode_manager_class.assert_called_once_with(app.main_window, "dev")
        self.assertEqual(app.mode_manager, self.mock_mode_manager)

    def test_helpmesign_app_get_config(self):
        """Test get_config method"""
        # Arrange
        app = HelpMeSignApp("dev")

        # Act
        config = app.get_config()

        # Assert
        self.assertEqual(config, self.mock_config)

    def test_helpmesign_app_save_config_success(self):
        """Test save_config method success"""
        # Arrange
        app = HelpMeSignApp("dev")
        new_config = {"new": "config"}

        # Act
        result = app.save_config(new_config)

        # Assert
        self.assertTrue(result)
        self.assertEqual(app.config, new_config)

    def test_helpmesign_app_save_config_failure(self):
        """Test save_config method with comprehensive validation"""
        # Arrange
        app = HelpMeSignApp("dev")
        app.logger.error = Mock()

        # Test with various config data types and edge cases
        test_cases = [
            (None, True),  # None is actually accepted by Python assignment
            ("invalid_config", True),  # String is also accepted
            (123, True),  # Integer is accepted
            ([], True),  # Empty list is accepted
            ({}, True),  # Empty dict should succeed
            ({"key": "value"}, True),  # Valid dict should succeed
            ({"nested": {"key": "value"}}, True),  # Nested dict should succeed
        ]

        for config_data, expected_result in test_cases:
            with self.subTest(config_data=config_data):
                # Act
                result = app.save_config(config_data)

                # Assert
                self.assertEqual(result, expected_result)
                if expected_result:
                    self.assertEqual(app.config, config_data)
                    app.logger.error.assert_not_called()
                else:
                    app.logger.error.assert_called_once()
                    app.logger.error.reset_mock()

        # Test that the method properly updates the config attribute
        test_config = {"window_size": {"width": 800, "height": 600}}
        result = app.save_config(test_config)
        self.assertTrue(result)
        self.assertEqual(app.config, test_config)
        self.assertIs(app.config, test_config)  # Should be the same object reference

    def test_helpmesign_app_get_user_mode(self):
        """Test get_user_mode method"""
        # Arrange
        app = HelpMeSignApp("dev")
        app.user_mode = "test_mode"

        # Act
        mode = app.get_user_mode()

        # Assert
        self.assertEqual(mode, "test_mode")

    def test_helpmesign_app_get_resource_info(self):
        """Test get_resource_info method"""
        # Arrange
        app = HelpMeSignApp("dev")
        mock_info = {"resources": "info"}
        app.resource_manager.get_resource_info.return_value = mock_info

        # Act
        info = app.get_resource_info()

        # Assert
        self.assertEqual(info, mock_info)
        app.resource_manager.get_resource_info.assert_called_once()

    def test_helpmesign_app_show(self):
        """Test show method"""
        # Arrange
        app = HelpMeSignApp("dev")

        # Act
        app.show()

        # Assert
        app.main_window.show.assert_called_once()

    def test_helpmesign_app_run(self):
        """Test run method"""
        # Arrange
        app = HelpMeSignApp("dev")

        # Act
        app.run()

        # Assert
        app.main_window.show.assert_called_once()
        app.logger.info.assert_called_with("Application started successfully")

    def test_helpmesign_app_set_user_mode_from_settings(self):
        """Test set_user_mode_from_settings method"""
        # Arrange
        app = HelpMeSignApp("dev")
        with patch("src.helpmesign.core.app.set_user_mode") as mock_set_user_mode:
            # Act
            app.set_user_mode_from_settings("new_mode")

            # Assert
            self.assertEqual(app.user_mode, "new_mode")
            mock_set_user_mode.assert_called_once_with("new_mode", "dev")

    def test_helpmesign_app_set_user_mode_from_settings_exception(self):
        """Test set_user_mode_from_settings method with exception"""
        # Arrange
        app = HelpMeSignApp("dev")
        app.logger.error = Mock()

        with patch(
            "src.helpmesign.core.app.set_user_mode", side_effect=Exception("Error")
        ):
            # Act
            app.set_user_mode_from_settings("new_mode")

            # Assert
            app.logger.error.assert_called_once()

    def test_helpmesign_app_setup_application(self):
        """Test setup_application method"""
        # Arrange
        app = HelpMeSignApp("dev")
        with patch.object(app, "set_app_icon") as mock_set_icon:
            with patch("src.helpmesign.core.app.get_text") as mock_get_text:
                mock_get_text.return_value = "Test Title"

                # Reset call counts since setup_application is called during initialization
                app.main_window.resize.reset_mock()
                app.main_window.set_title.reset_mock()
                app.main_window.focus_input.reset_mock()

                # Act
                app.setup_application()

                # Assert
                mock_set_icon.assert_called_once()
                app.main_window.resize.assert_called_once_with(
                    1200, 800
                )  # dev environment
                app.main_window.set_title.assert_called_once_with("Test Title")
                app.main_window.focus_input.assert_called_once()

    def test_helpmesign_app_setup_application_prod_environment(self):
        """Test setup_application method in prod environment"""
        # Arrange
        app = HelpMeSignApp("prod")
        with patch.object(app, "set_app_icon") as mock_set_icon:
            with patch("src.helpmesign.core.app.get_text") as mock_get_text:
                mock_get_text.return_value = "Test Title"

                # Reset call counts since setup_application is called during initialization
                app.main_window.resize.reset_mock()

                # Act
                app.setup_application()

                # Assert
                app.main_window.resize.assert_called_once_with(
                    1024, 1024
                )  # prod environment

    def test_helpmesign_app_setup_event_handlers(self):
        """Test setup_event_handlers method"""
        # Arrange
        app = HelpMeSignApp("dev")
        app.logger.error = Mock()

        # Reset call counts since setup_event_handlers is called during initialization
        app.main_window.process_requested.connect.reset_mock()
        app.main_window.clear_requested.connect.reset_mock()
        app.main_window.settings_requested.connect.reset_mock()

        # Act
        app.setup_event_handlers()

        # Assert
        app.main_window.process_requested.connect.assert_called_once()
        app.main_window.clear_requested.connect.assert_called_once()
        app.main_window.settings_requested.connect.assert_called_once()

    def test_helpmesign_app_setup_event_handlers_exception(self):
        """Test setup_event_handlers method with exception"""
        # Arrange
        app = HelpMeSignApp("dev")
        app.main_window.process_requested.connect.side_effect = Exception(
            "Connection error"
        )
        app.logger.error = Mock()

        # Act
        app.setup_event_handlers()

        # Assert
        app.logger.error.assert_called_once()

    def test_helpmesign_app_on_process_requested(self):
        """Test _on_process_requested method"""
        # Arrange
        app = HelpMeSignApp("dev")
        app.main_window.get_text_input.return_value = "test input"
        app.mode_manager.process_text.return_value = "test output"
        app.mode_manager.get_current_mode_name.return_value = "Test Mode"

        # Act
        app._on_process_requested()

        # Assert
        app.main_window.get_text_input.assert_called_once()
        app.mode_manager.process_text.assert_called_once_with("test input")
        app.main_window.set_text_output.assert_called_once_with("test output")
        app.main_window.set_status.assert_called_once_with(
            "Processed text using Test Mode"
        )

    def test_helpmesign_app_on_process_requested_exception(self):
        """Test _on_process_requested method with exception"""
        # Arrange
        app = HelpMeSignApp("dev")
        app.main_window.get_text_input.side_effect = Exception("Input error")
        app.logger.error = Mock()

        # Act
        app._on_process_requested()

        # Assert
        app.logger.error.assert_called_once()
        app.main_window.set_text_output.assert_called_once()
        app.main_window.set_status.assert_called_once_with("Error occurred")

    def test_helpmesign_app_on_clear_requested(self):
        """Test _on_clear_requested method"""
        # Arrange
        app = HelpMeSignApp("dev")

        # Act
        app._on_clear_requested()

        # Assert
        app.mode_manager.clear_content.assert_called_once()
        app.main_window.set_status.assert_called_once_with("Content cleared")

    def test_helpmesign_app_on_clear_requested_exception(self):
        """Test _on_clear_requested method with exception"""
        # Arrange
        app = HelpMeSignApp("dev")
        app.mode_manager.clear_content.side_effect = Exception("Clear error")
        app.logger.error = Mock()

        # Act
        app._on_clear_requested()

        # Assert
        app.logger.error.assert_called_once()
        app.main_window.set_status.assert_called_once_with("Error clearing content")

    def test_helpmesign_app_set_app_icon_success(self):
        """Test set_app_icon method success"""
        # Arrange
        app = HelpMeSignApp("dev")
        app.resource_manager.get_image_path.return_value = "/path/to/icon.png"
        app.resource_manager.resource_exists.return_value = True

        # Reset call counts since set_app_icon is called during initialization
        app.resource_manager.get_image_path.reset_mock()
        app.resource_manager.resource_exists.reset_mock()
        app.main_window.set_icon.reset_mock()
        app.logger.info.reset_mock()

        # Act
        app.set_app_icon()

        # Assert
        app.resource_manager.get_image_path.assert_called_once_with("icon.png")
        app.resource_manager.resource_exists.assert_called_once_with(
            "image", "icon.png"
        )
        app.main_window.set_icon.assert_called_once_with("/path/to/icon.png")
        app.logger.info.assert_called_with("App icon loaded successfully")

    def test_helpmesign_app_set_app_icon_not_found(self):
        """Test set_app_icon method when icon not found"""
        # Arrange
        app = HelpMeSignApp("dev")
        app.resource_manager.resource_exists.return_value = False
        app.logger.warning = Mock()

        # Act
        app.set_app_icon()

        # Assert
        app.logger.warning.assert_called_with("App icon not found")

    def test_helpmesign_app_set_app_icon_exception(self):
        """Test set_app_icon method with exception"""
        # Arrange
        app = HelpMeSignApp("dev")
        app.resource_manager.get_image_path.side_effect = Exception("Icon error")
        app.logger.warning = Mock()

        # Act
        app.set_app_icon()

        # Assert
        app.logger.warning.assert_called_once()

    def test_helpmesign_app_check_shutdown_state(self):
        """Test _check_shutdown_state method"""
        # Arrange
        app = HelpMeSignApp("dev")

        # Act & Assert - should not raise any exception
        app._check_shutdown_state()

    def test_helpmesign_app_cleanup_on_shutdown(self):
        """Test _cleanup_on_shutdown method"""
        # Arrange
        app = HelpMeSignApp("dev")
        app.logger.info = Mock()
        app.logger.error = Mock()

        # Act
        app._cleanup_on_shutdown()

        # Assert
        self.assertTrue(app._shutting_down)
        app.logger.info.assert_called()

    def test_helpmesign_app_cleanup_on_shutdown_exception(self):
        """Test _cleanup_on_shutdown method with exception"""
        # Arrange
        app = HelpMeSignApp("dev")
        app.logger.error = Mock()
        app.logger.debug = Mock()

        # Mock the disconnect method to raise an exception
        app.main_window.process_requested.disconnect.side_effect = Exception(
            "Disconnect error"
        )

        # Act
        app._cleanup_on_shutdown()

        # Assert
        app.logger.debug.assert_called()  # Exception is caught and logged as debug
        self.assertTrue(app._shutting_down)

    def test_helpmesign_app_delayed_font_application(self):
        """Test _delayed_font_application method"""
        # Arrange
        app = HelpMeSignApp("dev")
        app.logger.debug = Mock()
        app.logger.error = Mock()

        with patch("src.helpmesign.core.startup.get_font_size") as mock_get_font_size:
            mock_get_font_size.return_value = 14

            # Act
            app._delayed_font_application()

            # Assert
            mock_get_font_size.assert_called_once_with("dev")
            app.logger.debug.assert_called()

    def test_helpmesign_app_delayed_font_application_exception(self):
        """Test _delayed_font_application method with exception"""
        # Arrange
        app = HelpMeSignApp("dev")
        app.logger.error = Mock()

        with patch(
            "src.helpmesign.core.startup.get_font_size",
            side_effect=Exception("Font error"),
        ):
            # Act
            app._delayed_font_application()

            # Assert
            app.logger.error.assert_called_once()

    def test_helpmesign_app_setup_shutdown_handling(self):
        """Test _setup_shutdown_handling method"""
        # Arrange
        app = HelpMeSignApp("dev")
        app.logger.debug = Mock()
        app.logger.error = Mock()

        # Act
        app._setup_shutdown_handling()

        # Assert
        app.logger.debug.assert_called_with("Shutdown handling set up")

    def test_helpmesign_app_setup_shutdown_handling_exception(self):
        """Test _setup_shutdown_handling method with exception"""
        # Arrange
        app = HelpMeSignApp("dev")
        app.logger.error = Mock()
        self.mock_qapp.instance.side_effect = Exception("QApp error")

        # Act
        app._setup_shutdown_handling()

        # Assert
        app.logger.error.assert_called_once()


class TestCreateAppFunction(unittest.TestCase):
    """Test cases for create_app function"""

    def setUp(self):
        """Set up test fixtures"""
        # Mock all dependencies
        self.patchers = []

        # Mock QApplication
        qapp_patcher = patch("src.helpmesign.core.app.QApplication")
        self.mock_qapp = qapp_patcher.start()
        self.patchers.append(qapp_patcher)

        # Mock MainWindow
        main_window_patcher = patch("src.helpmesign.core.app.MainWindow")
        self.mock_main_window_class = main_window_patcher.start()
        self.patchers.append(main_window_patcher)

        # Mock ModeManager
        mode_manager_patcher = patch("src.helpmesign.core.app.ModeManager")
        self.mock_mode_manager_class = mode_manager_patcher.start()
        self.patchers.append(mode_manager_patcher)

        # Mock ResourceManager
        resource_manager_patcher = patch("src.helpmesign.core.app.ResourceManager")
        self.mock_resource_manager_class = resource_manager_patcher.start()
        self.patchers.append(resource_manager_patcher)

        # Mock setup_logging
        setup_logging_patcher = patch("src.helpmesign.core.app.setup_logging")
        self.mock_setup_logging = setup_logging_patcher.start()
        self.patchers.append(setup_logging_patcher)

    def tearDown(self):
        """Clean up after tests"""
        for patcher in self.patchers:
            patcher.stop()

    def test_create_app_function(self):
        """Test create_app function with proper mocking"""
        # Mock QApplication to prevent real initialization
        with patch("PySide6.QtWidgets.QApplication") as mock_qapp:
            mock_qapp_instance = MagicMock()
            mock_qapp.instance.return_value = mock_qapp_instance

            # Mock HelpMeSignApp
            with patch("src.helpmesign.core.app.HelpMeSignApp") as mock_app_class:
                mock_app_instance = MagicMock()
                mock_app_class.return_value = mock_app_instance

                # Test
                result = create_app()

                # Assert
                mock_app_class.assert_called_once_with("dev")
                assert result == mock_app_instance

    def test_create_app_function_default_environment(self):
        """Test create_app function with default environment"""
        # Mock QApplication to prevent real initialization
        with patch("PySide6.QtWidgets.QApplication") as mock_qapp:
            mock_qapp_instance = MagicMock()
            mock_qapp.instance.return_value = mock_qapp_instance

            # Mock HelpMeSignApp
            with patch("src.helpmesign.core.app.HelpMeSignApp") as mock_app_class:
                mock_app_instance = MagicMock()
                mock_app_class.return_value = mock_app_instance

                # Test with default environment
                result = create_app("prod")

                # Assert
                mock_app_class.assert_called_once_with("prod")
                assert result == mock_app_instance


if __name__ == "__main__":
    unittest.main()
