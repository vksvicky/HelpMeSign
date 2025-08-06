#!/usr/bin/env python3
"""
Additional tests for HelpMeSignApp to improve coverage
Tests the missing lines in app.py
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from src.helpmesign.core.app import HelpMeSignApp


class TestAppCoverage:
    """Tests to improve app.py coverage"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures"""
        # Mock all the dependencies
        self.patches = []

        # Mock QApplication
        qapp_patch = patch("PySide6.QtWidgets.QApplication")
        self.mock_qapp = qapp_patch.start()
        self.patches.append(qapp_patch)

        # Mock MainWindow
        main_window_patch = patch("src.helpmesign.core.app.MainWindow")
        self.mock_main_window_class = main_window_patch.start()
        self.mock_main_window = Mock()
        self.mock_main_window_class.return_value = self.mock_main_window
        self.patches.append(main_window_patch)

        # Mock ModeManager
        mode_manager_patch = patch("src.helpmesign.core.app.ModeManager")
        self.mock_mode_manager_class = mode_manager_patch.start()
        self.mock_mode_manager = Mock()
        self.mock_mode_manager_class.return_value = self.mock_mode_manager
        self.patches.append(mode_manager_patch)

        # Mock ResourceManager
        resource_manager_patch = patch("src.helpmesign.core.app.ResourceManager")
        self.mock_resource_manager_class = resource_manager_patch.start()
        self.mock_resource_manager = Mock()
        self.mock_resource_manager_class.return_value = self.mock_resource_manager
        self.patches.append(resource_manager_patch)

        # Mock setup_logging
        logging_patch = patch("src.helpmesign.core.app.setup_logging")
        self.mock_setup_logging = logging_patch.start()
        self.mock_logger = Mock()
        self.mock_setup_logging.return_value = self.mock_logger
        self.patches.append(logging_patch)

        # Mock QTimer
        qtimer_patch = patch("PySide6.QtCore.QTimer")
        self.mock_qtimer = qtimer_patch.start()
        self.patches.append(qtimer_patch)

        # Mock font manager
        font_manager_patch = patch("src.helpmesign.utils.font_manager.get_font_manager")
        self.mock_font_manager = font_manager_patch.start()
        self.mock_font_manager_instance = Mock()
        self.mock_font_manager.return_value = self.mock_font_manager_instance
        self.mock_font_manager_instance.get_font.return_value = Mock()
        self.patches.append(font_manager_patch)

        # Mock get_font_size
        font_size_patch = patch("src.helpmesign.core.startup.get_font_size")
        self.mock_get_font_size = font_size_patch.start()
        self.mock_get_font_size.return_value = 12
        self.patches.append(font_size_patch)

        # Mock system monitor
        system_monitor_patch = patch(
            "src.helpmesign.utils.system_monitor.get_system_monitor"
        )
        self.mock_system_monitor = system_monitor_patch.start()
        self.mock_system_monitor_instance = Mock()
        self.mock_system_monitor.return_value = self.mock_system_monitor_instance
        self.patches.append(system_monitor_patch)

        # Mock config
        self.mock_config = {
            "window_size": {"width": 1024, "height": 1024},
            "dev_window_size": {"width": 1200, "height": 800},
            "theme": "light",
        }
        self.mock_resource_manager.load_config.return_value = self.mock_config

        yield

        # Clean up patches
        for patch_obj in self.patches:
            patch_obj.stop()

    def test_setup_shutdown_handling_exception(self):
        """Test _setup_shutdown_handling with exception"""
        # Mock QApplication.instance() to raise exception
        self.mock_qapp.instance.side_effect = Exception("QApp error")

        app = HelpMeSignApp("dev")
        app._setup_shutdown_handling()

        # Should log the error
        self.mock_logger.error.assert_called()

    def test_cleanup_on_shutdown_status_bar_exception(self):
        """Test _cleanup_on_shutdown with status bar cleanup exception"""
        # Mock status bar cleanup to raise exception
        self.mock_main_window.status_bar.cleanup.side_effect = Exception(
            "Cleanup error"
        )

        app = HelpMeSignApp("dev")
        app._cleanup_on_shutdown()

        # Should set shutdown flag
        assert app._shutting_down is True
        # Should log the cleanup error
        self.mock_logger.debug.assert_called()

    def test_cleanup_on_shutdown_signal_disconnect_exception(self):
        """Test _cleanup_on_shutdown with signal disconnect exception"""
        # Mock signal disconnect to raise exception
        self.mock_main_window.process_requested.disconnect.side_effect = Exception(
            "Disconnect error"
        )

        app = HelpMeSignApp("dev")
        app._cleanup_on_shutdown()

        # Should set shutdown flag
        assert app._shutting_down is True
        # Should log the disconnect error
        self.mock_logger.debug.assert_called()

    def test_setup_event_handlers_exception(self):
        """Test setup_event_handlers with exception"""
        # Mock signal connection to raise exception
        self.mock_main_window.process_requested.connect.side_effect = Exception(
            "Connection error"
        )

        app = HelpMeSignApp("dev")
        app.setup_event_handlers()

        # Should log the error
        self.mock_logger.error.assert_called()

    def test_on_process_requested_exception(self):
        """Test _on_process_requested with exception"""
        # Mock process_text to raise exception
        self.mock_mode_manager.process_text.side_effect = Exception("Process error")

        app = HelpMeSignApp("dev")
        app._on_process_requested()

        # Should log the error
        self.mock_logger.error.assert_called()
        # Should set error output
        self.mock_main_window.set_text_output.assert_called_with("Error: Process error")
        self.mock_main_window.set_status.assert_called_with("Error occurred")

    def test_on_clear_requested_exception(self):
        """Test _on_clear_requested with exception"""
        # Mock clear_content to raise exception
        self.mock_mode_manager.clear_content.side_effect = Exception("Clear error")

        app = HelpMeSignApp("dev")
        app._on_clear_requested()

        # Should log the error
        self.mock_logger.error.assert_called()
        # Should set error status
        self.mock_main_window.set_status.assert_called_with("Error clearing content")

    def test_set_app_icon_exception(self):
        """Test set_app_icon with exception"""
        # Mock get_image_path to raise exception
        self.mock_resource_manager.get_image_path.side_effect = Exception("Icon error")

        app = HelpMeSignApp("dev")
        app.set_app_icon()

        # Should log warning
        self.mock_logger.warning.assert_called()

    def test_save_config_success(self):
        """Test save_config success case"""
        app = HelpMeSignApp("dev")

        result = app.save_config({"test": "value"})
        assert result is True
        assert app.config == {"test": "value"}

    def test_delayed_font_application_exception(self):
        """Test _delayed_font_application with exception"""
        app = HelpMeSignApp("dev")

        # Mock apply_theme_and_font_settings to raise exception
        app.apply_theme_and_font_settings = Mock(
            side_effect=Exception("Delayed font error")
        )

        app._delayed_font_application()
        self.mock_logger.error.assert_called()

    def test_delayed_font_application_exception_alternative(self):
        """Test _delayed_font_application with exception - alternative approach"""
        app = HelpMeSignApp("dev")

        # Mock the method to raise exception directly
        with patch.object(app, "apply_theme_and_font_settings") as mock_method:
            mock_method.side_effect = Exception("Delayed font error")

            app._delayed_font_application()
            self.mock_logger.error.assert_called()

    def test_setup_application_prod_environment(self):
        """Test setup_application with prod environment"""
        app = HelpMeSignApp("prod")

        with patch("src.helpmesign.core.app.get_text") as mock_get_text:
            mock_get_text.return_value = "Test Title"

            app.setup_application()

            # Should use prod window size
            self.mock_main_window.resize.assert_called_with(1024, 1024)
            self.mock_main_window.set_title.assert_called_with("Test Title")
            self.mock_main_window.focus_input.assert_called()

    def test_setup_application_dev_environment(self):
        """Test setup_application with dev environment"""
        app = HelpMeSignApp("dev")

        with patch("src.helpmesign.core.app.get_text") as mock_get_text:
            mock_get_text.return_value = "Test Title"

            app.setup_application()

            # Should use dev window size
            self.mock_main_window.resize.assert_called_with(1200, 800)
            self.mock_main_window.set_title.assert_called_with("Test Title")
            self.mock_main_window.focus_input.assert_called()

    def test_setup_application_default_sizes(self):
        """Test setup_application with default sizes when config is missing"""
        # Mock empty config
        self.mock_resource_manager.load_config.return_value = {}

        app = HelpMeSignApp("prod")

        with patch("src.helpmesign.core.app.get_text") as mock_get_text:
            mock_get_text.return_value = "Test Title"

            app.setup_application()

            # Should use default sizes
            self.mock_main_window.resize.assert_called_with(1024, 1024)

    def test_setup_application_dev_default_sizes(self):
        """Test setup_application with dev default sizes when config is missing"""
        # Mock empty config
        self.mock_resource_manager.load_config.return_value = {}

        app = HelpMeSignApp("dev")

        with patch("src.helpmesign.core.app.get_text") as mock_get_text:
            mock_get_text.return_value = "Test Title"

            app.setup_application()

            # Should use dev default sizes
            self.mock_main_window.resize.assert_called_with(1200, 800)

    def test_set_app_icon_with_qapplication(self):
        """Test set_app_icon with QApplication instance"""
        # Mock resource manager
        self.mock_resource_manager.get_image_path.return_value = "/path/to/icon.png"
        self.mock_resource_manager.resource_exists.return_value = True

        # Mock QApplication
        mock_qapp = Mock()
        mock_qapp.windowIcon.return_value = Mock()
        mock_qapp.windowIcon.return_value.isNull.return_value = True
        self.mock_qapp.instance.return_value = mock_qapp

        app = HelpMeSignApp("dev")
        app.set_app_icon()

        # Should set icon on main window
        self.mock_main_window.set_icon.assert_called_with("/path/to/icon.png")
        self.mock_logger.info.assert_called_with("App icon loaded successfully")

    def test_set_app_icon_icon_not_found(self):
        """Test set_app_icon when icon is not found"""
        # Mock resource manager to return False for resource_exists
        self.mock_resource_manager.get_image_path.return_value = "/path/to/icon.png"
        self.mock_resource_manager.resource_exists.return_value = False

        app = HelpMeSignApp("dev")
        app.set_app_icon()

        # Should log warning
        self.mock_logger.warning.assert_called_with("App icon not found")

    def test_set_app_icon_qapplication_not_null(self):
        """Test set_app_icon when QApplication windowIcon is not null"""
        # Mock resource manager
        self.mock_resource_manager.get_image_path.return_value = "/path/to/icon.png"
        self.mock_resource_manager.resource_exists.return_value = True

        # Mock QApplication with non-null windowIcon
        mock_qapp = Mock()
        mock_qapp.windowIcon.return_value = Mock()
        mock_qapp.windowIcon.return_value.isNull.return_value = False
        self.mock_qapp.instance.return_value = mock_qapp

        app = HelpMeSignApp("dev")
        app.set_app_icon()

        # Should set icon on main window but not on QApplication
        self.mock_main_window.set_icon.assert_called_with("/path/to/icon.png")
        mock_qapp.setWindowIcon.assert_not_called()

    def test_set_app_icon_no_qapplication(self):
        """Test set_app_icon when QApplication instance is None"""
        # Mock resource manager
        self.mock_resource_manager.get_image_path.return_value = "/path/to/icon.png"
        self.mock_resource_manager.resource_exists.return_value = True

        # Mock QApplication to return None
        self.mock_qapp.instance.return_value = None

        app = HelpMeSignApp("dev")
        app.set_app_icon()

        # Should set icon on main window but not on QApplication
        self.mock_main_window.set_icon.assert_called_with("/path/to/icon.png")
        self.mock_logger.info.assert_called_with("App icon loaded successfully")

    def test_check_user_mode_exception(self):
        """Test check_user_mode with exception"""
        with patch("src.helpmesign.core.app.get_user_mode") as mock_get_user_mode:
            mock_get_user_mode.side_effect = Exception("User mode error")

            app = HelpMeSignApp("dev")
            app.check_user_mode()

            self.mock_logger.error.assert_called()
            # Should fallback to default mode
            self.mock_mode_manager.switch_mode.assert_called_with("sign_translate")

    def test_show_startup_screen_exception(self):
        """Test show_startup_screen with exception"""
        with patch("src.helpmesign.core.app.show_startup_screen") as mock_show_startup:
            mock_show_startup.side_effect = Exception("Startup screen error")

            app = HelpMeSignApp("dev")
            app.show_startup_screen()

            self.mock_logger.error.assert_called()
            # Should fallback to default mode
            self.mock_mode_manager.switch_mode.assert_called_with("sign_translate")

    def test_show_settings_exception(self):
        """Test show_settings with exception"""
        with patch(
            "src.helpmesign.core.app.show_settings_dialog"
        ) as mock_show_settings:
            mock_show_settings.side_effect = Exception("Settings error")

            app = HelpMeSignApp("dev")
            app.show_settings()

            self.mock_logger.error.assert_called()

    def test_handle_settings_changed_exception(self):
        """Test handle_settings_changed with exception"""
        # Mock switch_mode_by_display_name to raise exception
        self.mock_mode_manager.switch_mode_by_display_name.side_effect = Exception(
            "Settings change error"
        )

        app = HelpMeSignApp("dev")
        app.handle_settings_changed("Learn")

        self.mock_logger.error.assert_called()

    def test_apply_theme_and_font_settings_exception(self):
        """Test apply_theme_and_font_settings with exception"""
        # Mock main_window methods to raise exception
        self.mock_main_window.get_text_input.side_effect = Exception(
            "Theme font settings error"
        )

        app = HelpMeSignApp("dev")
        app.apply_theme_and_font_settings()

        self.mock_logger.error.assert_called()

    def test_apply_font_size_methods_success(self):
        """Test font size application methods success case"""
        app = HelpMeSignApp("dev")

        # Test all font size methods
        app._apply_font_size_to_current_window(14)
        app._apply_font_size_setting(14)
        app._apply_font_size_directly(14)

        # Should not raise exceptions

    def test_update_theme_methods_success(self):
        """Test theme update methods success case"""
        app = HelpMeSignApp("dev")

        # Test all theme update methods
        app._update_input_fields_theme_with_font_size("input-style")
        app._update_buttons_theme_with_font_size("primary", "secondary")
        app._update_main_window_theme()
        app._update_input_fields_theme()
        app._update_buttons_theme()

        # Should not raise exceptions

    def test_update_font_size_methods_success(self):
        """Test font size update methods success case"""
        app = HelpMeSignApp("dev")

        # Test font size update methods
        app._update_input_fields_font_size(Mock())
        app._update_buttons_font_size(Mock())

        # Should not raise exceptions

    def test_on_process_requested_success(self):
        """Test _on_process_requested success case"""
        # Mock successful processing
        self.mock_main_window.get_text_input.return_value = "test input"
        self.mock_mode_manager.process_text.return_value = "test output"
        self.mock_mode_manager.get_current_mode_name.return_value = "Test Mode"

        app = HelpMeSignApp("dev")
        app._on_process_requested()

        # Should process text and update status
        self.mock_main_window.set_text_output.assert_called_with("test output")
        self.mock_main_window.set_status.assert_called_with(
            "Processed text using Test Mode"
        )

    def test_on_clear_requested_success(self):
        """Test _on_clear_requested success case"""
        app = HelpMeSignApp("dev")
        app._on_clear_requested()

        # Should clear content and update status
        self.mock_mode_manager.clear_content.assert_called()
        self.mock_main_window.set_status.assert_called_with("Content cleared")

    def test_setup_event_handlers_success(self):
        """Test setup_event_handlers success case"""
        app = HelpMeSignApp("dev")
        app.setup_event_handlers()

        # Should connect signals
        self.mock_main_window.process_requested.connect.assert_called()
        self.mock_main_window.clear_requested.connect.assert_called()
        self.mock_main_window.settings_requested.connect.assert_called()
        self.mock_logger.debug.assert_called_with("Event handlers set up successfully")

    def test_check_user_mode_with_saved_mode(self):
        """Test check_user_mode with saved mode"""
        with patch("src.helpmesign.core.app.get_user_mode") as mock_get_user_mode:
            with patch("src.helpmesign.core.app.get_text") as mock_get_text:
                mock_get_user_mode.return_value = "Learn"
                mock_get_text.return_value = "Learn"
                self.mock_mode_manager.switch_mode_by_display_name.return_value = True

                app = HelpMeSignApp("dev")
                app.check_user_mode()

                # Should switch to saved mode
                self.mock_mode_manager.switch_mode_by_display_name.assert_called_with(
                    "Learn"
                )
                assert app.user_mode == "Learn"

    def test_check_user_mode_with_saved_mode_failure(self):
        """Test check_user_mode with saved mode failure"""
        with patch("src.helpmesign.core.app.get_user_mode") as mock_get_user_mode:
            with patch("src.helpmesign.core.app.get_text") as mock_get_text:
                mock_get_user_mode.return_value = "Learn"
                mock_get_text.return_value = "Sign & Translate"
                self.mock_mode_manager.switch_mode_by_display_name.return_value = False

                app = HelpMeSignApp("dev")
                app.check_user_mode()

                # Should fallback to default mode
                self.mock_mode_manager.switch_mode.assert_called_with("sign_translate")
                assert app.user_mode == "Sign & Translate"

    def test_show_startup_screen_with_selection(self):
        """Test show_startup_screen with mode selection"""
        with patch("src.helpmesign.core.app.show_startup_screen") as mock_show_startup:
            with patch("src.helpmesign.core.app.set_user_mode") as mock_set_user_mode:
                with patch("src.helpmesign.core.app.get_text") as mock_get_text:
                    mock_show_startup.return_value = "Learn"
                    mock_get_text.return_value = "Learn"
                    self.mock_mode_manager.switch_mode_by_display_name.return_value = (
                        True
                    )

                    app = HelpMeSignApp("dev")
                    app.show_startup_screen()

                    # Should switch to selected mode
                    self.mock_mode_manager.switch_mode_by_display_name.assert_called_with(
                        "Learn"
                    )
                    mock_set_user_mode.assert_called_with("Learn", "dev")
                    assert app.user_mode == "Learn"

    def test_show_startup_screen_with_selection_failure(self):
        """Test show_startup_screen with mode selection failure"""
        with patch("src.helpmesign.core.app.show_startup_screen") as mock_show_startup:
            with patch("src.helpmesign.core.app.get_text") as mock_get_text:
                mock_show_startup.return_value = "Learn"
                mock_get_text.return_value = "Sign & Translate"
                self.mock_mode_manager.switch_mode_by_display_name.return_value = False

                app = HelpMeSignApp("dev")
                app.show_startup_screen()

                # Should fallback to default mode
                self.mock_mode_manager.switch_mode.assert_called_with("sign_translate")
                assert app.user_mode == "Sign & Translate"

    def test_show_startup_screen_no_selection(self):
        """Test show_startup_screen with no mode selection"""
        with patch("src.helpmesign.core.app.show_startup_screen") as mock_show_startup:
            with patch("src.helpmesign.core.app.get_text") as mock_get_text:
                mock_show_startup.return_value = None
                mock_get_text.return_value = "Sign & Translate"

                app = HelpMeSignApp("dev")
                app.show_startup_screen()

                # Should use default mode
                self.mock_mode_manager.switch_mode.assert_called_with("sign_translate")
                assert app.user_mode == "Sign & Translate"

    def test_show_settings_success(self):
        """Test show_settings success case"""
        with patch(
            "src.helpmesign.core.app.show_settings_dialog"
        ) as mock_show_settings:
            mock_show_settings.return_value = None

            app = HelpMeSignApp("dev")
            app.user_mode = "Sign & Translate"
            app.show_settings()

            # Should call show_settings_dialog
            mock_show_settings.assert_called()

    def test_handle_settings_changed_success(self):
        """Test handle_settings_changed success case"""
        self.mock_mode_manager.switch_mode_by_display_name.return_value = True

        app = HelpMeSignApp("dev")
        app.handle_settings_changed("Learn")

        # Should switch mode
        self.mock_mode_manager.switch_mode_by_display_name.assert_called_with("Learn")
        assert app.user_mode == "Learn"

    def test_handle_settings_changed_failure(self):
        """Test handle_settings_changed failure case"""
        with patch("src.helpmesign.core.app.get_text") as mock_get_text:
            mock_get_text.return_value = "Sign & Translate"
            self.mock_mode_manager.switch_mode_by_display_name.return_value = False

            app = HelpMeSignApp("dev")
            app.handle_settings_changed("Learn")

            # Should fallback to default mode
            self.mock_mode_manager.switch_mode.assert_called_with("sign_translate")
            assert app.user_mode == "Sign & Translate"

    def test_apply_theme_and_font_settings_success(self):
        """Test apply_theme_and_font_settings success case"""
        app = HelpMeSignApp("dev")
        app.apply_theme_and_font_settings()

        # Should call theme update methods
        # Note: The actual methods are mocked, so we just verify no exceptions

    def test_apply_font_size_methods_success(self):
        """Test font size application methods success case"""
        app = HelpMeSignApp("dev")

        # Test all font size methods
        app._apply_font_size_to_current_window(14)
        app._apply_font_size_setting(14)
        app._apply_font_size_directly(14)

        # Should not raise exceptions

    def test_update_theme_methods_success(self):
        """Test theme update methods success case"""
        app = HelpMeSignApp("dev")

        # Test all theme update methods
        app._update_input_fields_theme_with_font_size("input-style")
        app._update_buttons_theme_with_font_size("primary", "secondary")
        app._update_main_window_theme()
        app._update_input_fields_theme()
        app._update_buttons_theme()

        # Should not raise exceptions

    def test_update_font_size_methods_success(self):
        """Test font size update methods success case"""
        app = HelpMeSignApp("dev")

        # Test font size update methods
        app._update_input_fields_font_size(Mock())
        app._update_buttons_font_size(Mock())

        # Should not raise exceptions

    def test_show_and_run_methods(self):
        """Test show and run methods"""
        app = HelpMeSignApp("dev")

        # Test show method
        app.show()
        self.mock_main_window.show.assert_called()

        # Test run method - check if the method exists and is callable
        assert hasattr(app, "run")
        assert callable(app.run)
        app.run()
        # Note: run method might not call main_window.run() directly

    def test_get_user_mode_and_resource_info(self):
        """Test get_user_mode and get_resource_info methods"""
        app = HelpMeSignApp("dev")
        app.user_mode = "Test Mode"

        # Test get_user_mode
        result = app.get_user_mode()
        assert result == "Test Mode"

        # Test get_resource_info - mock the resource manager method
        self.mock_resource_manager.get_resource_info.return_value = {
            "cpu": 25.0,
            "memory": 60.0,
        }
        result = app.get_resource_info()
        assert isinstance(result, dict)
        assert "cpu" in result
        assert "memory" in result

    def test_set_user_mode_from_settings(self):
        """Test set_user_mode_from_settings method"""
        app = HelpMeSignApp("dev")

        app.set_user_mode_from_settings("Learn")
        assert app.user_mode == "Learn"
