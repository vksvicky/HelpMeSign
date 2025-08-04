import sys
from datetime import datetime
from typing import Any, Dict, Optional

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication

from ..modes.mode_manager import ModeManager
from ..ui.components import MainWindow
from ..ui.settings_dialog import show_settings_dialog
from ..utils.language_manager import get_dict, get_list, get_text
from ..utils.logger import (
    get_logger,
    log_exception,
    log_function_entry,
    log_function_exit,
    setup_logging,
)
from ..utils.resource_manager import ResourceManager
from ..utils.theme_manager import apply_theme, get_theme_manager
from .startup import (
    SecureConfigManager,
    get_user_mode,
    set_user_mode,
    show_startup_screen,
)


class HelpMeSignApp:
    """Main application class for HelpMeSign"""

    def __init__(self, environment: str = "dev"):
        """Initialize the HelpMeSign application"""
        self.environment = environment.lower()
        log_function_entry(
            get_logger(), "HelpMeSignApp.__init__", environment=environment
        )

        # Add shutdown flag to prevent operations during shutdown
        self._shutting_down = False

        # Add settings save flag to prevent infinite loops
        self._settings_save_in_progress: bool = False

        self.resource_manager = ResourceManager()

        # Load configuration based on environment
        self.config = self.resource_manager.load_config()

        # Set up logging based on environment
        self.logger = setup_logging(self.config, environment=self.environment)
        self.logger.info(
            f"Initializing HelpMeSign application in {self.environment} environment"
        )

        # Initialize user mode
        self.user_mode: Optional[str] = None

        # Create main window
        self.main_window = MainWindow(title=f"HelpMeSign ({self.environment.upper()})")
        self.logger.debug("Main window created")

        # Initialize mode manager
        self.mode_manager = ModeManager(self.main_window, self.environment)
        self.logger.debug("Mode manager initialized")

        # Set up application
        self.setup_application()
        self.setup_event_handlers()

        # Show startup screen if no user mode is set
        self.check_user_mode()

        # Apply saved theme and font settings
        self.apply_theme_and_font_settings()

        # Add a small delay to ensure all components are fully initialized
        # before applying font settings
        from PySide6.QtCore import QTimer

        QTimer.singleShot(100, self._delayed_font_application)

        # Set up application shutdown handling
        self._setup_shutdown_handling()

        log_function_exit(get_logger(), "HelpMeSignApp.__init__")

    def _delayed_font_application(self) -> None:
        """Apply font settings after a delay to ensure all components are initialized"""
        try:
            from .startup import get_font_size

            font_size = get_font_size(self.environment)
            self.logger.debug(f"Delayed font application for size: {font_size}px")

            # Re-apply font size to ensure all components are updated
            self._apply_font_size_setting(font_size)

        except Exception as e:
            self.logger.error(f"Error in delayed font application: {e}")

    def _setup_shutdown_handling(self):
        """Set up proper application shutdown handling"""
        try:
            from PySide6.QtWidgets import QApplication

            app = QApplication.instance()
            if app:
                # Connect to aboutToQuit signal for cleanup
                app.aboutToQuit.connect(self._cleanup_on_shutdown)
                self.logger.debug("Shutdown handling set up")
        except Exception as e:
            self.logger.error(f"Error setting up shutdown handling: {e}")

    def _cleanup_on_shutdown(self):
        """Clean up resources when application is shutting down"""
        try:
            # Set shutdown flag to prevent further operations
            self._shutting_down = True

            self.logger.info("Application shutting down, cleaning up resources...")

            # Disconnect all signals to prevent callbacks during shutdown
            try:
                if hasattr(self, "main_window") and self.main_window:
                    self.main_window.process_requested.disconnect()
                    self.main_window.clear_requested.disconnect()
                    self.main_window.settings_requested.disconnect()
            except Exception as e:
                self.logger.debug(f"Error disconnecting signals: {e}")

            # Clear references to prevent circular references
            self.main_window = None
            self.resource_manager = None

            self.logger.info("Cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during shutdown cleanup: {e}")

    def _check_shutdown_state(self):
        """Check if application is in shutdown state"""
        # Removed to prevent segmentation faults
        pass

    def setup_application(self) -> None:
        """Set up the application configuration and appearance"""
        # Set app icon if available
        self.set_app_icon()

        # Set window size from config or default based on environment
        if self.environment == "prod":
            window_width = self.config.get("window_size", {}).get("width", 1024)
            window_height = self.config.get("window_size", {}).get("height", 1024)
        else:  # dev environment
            window_width = self.config.get("dev_window_size", {}).get("width", 1200)
            window_height = self.config.get("dev_window_size", {}).get("height", 800)

        self.main_window.resize(window_width, window_height)

        # Set window title based on environment
        title = get_text("ui.main_window.title")
        self.main_window.set_title(title)

        # Focus on input field
        self.main_window.focus_input()

    def setup_event_handlers(self) -> None:
        """Set up event handlers for the main window"""
        try:
            # Connect main window signals to mode manager
            self.main_window.process_requested.connect(self._on_process_requested)
            self.main_window.clear_requested.connect(self._on_clear_requested)
            self.main_window.settings_requested.connect(self.show_settings)

            self.logger.debug("Event handlers set up successfully")
        except Exception as e:
            self.logger.error(f"Error setting up event handlers: {e}")

    def _on_process_requested(self) -> None:
        """Handle process button click using current mode"""
        try:
            input_text = self.main_window.get_text_input()
            output_text = self.mode_manager.process_text(input_text)
            self.main_window.set_text_output(output_text)

            # Update status based on current mode
            current_mode_name = self.mode_manager.get_current_mode_name()
            status_message = f"Processed text using {current_mode_name}"
            self.main_window.set_status(status_message)

        except Exception as e:
            self.logger.error(f"Error processing text: {e}")
            self.main_window.set_text_output(f"Error: {e}")
            self.main_window.set_status("Error occurred")

    def _on_clear_requested(self) -> None:
        """Handle clear button click using current mode"""
        try:
            self.mode_manager.clear_content()
            self.main_window.set_status("Content cleared")
        except Exception as e:
            self.logger.error(f"Error clearing content: {e}")
            self.main_window.set_status("Error clearing content")

    def set_app_icon(self) -> None:
        """Set the application icon if available"""
        try:
            icon_path = self.resource_manager.get_image_path("icon.png")
            if self.resource_manager.resource_exists("image", "icon.png"):
                # Set icon on the main window
                self.main_window.set_icon(icon_path)

                # Set icon on the QApplication for menubar and dock
                app = QApplication.instance()
                if app and hasattr(app, "windowIcon") and app.windowIcon().isNull():
                    app.setWindowIcon(QIcon(icon_path))  # type: ignore

                self.logger.info("App icon loaded successfully")
            else:
                self.logger.warning("App icon not found")
        except Exception as e:
            self.logger.warning(f"Could not load app icon: {e}")

    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration"""
        return self.config

    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """Save configuration data"""
        try:
            self.config = config_data
            return True
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False

    def check_user_mode(self) -> None:
        """Check if user mode is set and handle accordingly"""
        try:
            # Get saved user mode
            saved_mode = get_user_mode(self.environment)

            if saved_mode:
                # Switch to saved mode using mode manager
                success = self.mode_manager.switch_mode_by_display_name(saved_mode)
                if success:
                    self.user_mode = saved_mode
                    self.logger.info(f"Switched to saved mode: {saved_mode}")
                else:
                    # Fallback to default mode
                    self.mode_manager.switch_mode("sign_translate")
                    self.user_mode = get_text("modes.sign_translate.name")
                    self.logger.warning(
                        f"Failed to switch to saved mode {saved_mode}, using default"
                    )
            else:
                # No saved mode, show startup screen
                self.show_startup_screen()

        except Exception as e:
            self.logger.error(f"Error checking user mode: {e}")
            # Fallback to default mode
            self.mode_manager.switch_mode("sign_translate")
            self.user_mode = get_text("modes.sign_translate.name")

    def show_startup_screen(self) -> None:
        """Show the startup screen for mode selection"""
        try:
            # Show startup screen and get selected mode
            selected_mode = show_startup_screen(self.environment)

            if selected_mode:
                # Switch to selected mode using mode manager
                success = self.mode_manager.switch_mode_by_display_name(selected_mode)
                if success:
                    self.user_mode = selected_mode
                    set_user_mode(selected_mode, self.environment)
                    self.logger.info(f"User selected mode: {selected_mode}")
                else:
                    # Fallback to default mode
                    self.mode_manager.switch_mode("sign_translate")
                    self.user_mode = get_text("modes.sign_translate.name")
                    self.logger.warning(
                        f"Failed to switch to selected mode {selected_mode}, using default"
                    )
            else:
                # No mode selected, use default
                self.mode_manager.switch_mode("sign_translate")
                self.user_mode = get_text("modes.sign_translate.name")
                self.logger.info("No mode selected, using default")

        except Exception as e:
            self.logger.error(f"Error showing startup screen: {e}")
            # Fallback to default mode
            self.mode_manager.switch_mode("sign_translate")
            self.user_mode = get_text("modes.sign_translate.name")

    def show_settings(self) -> None:
        """Show the settings dialog"""
        try:
            from .startup import get_user_mode

            # Get current mode
            current_mode = get_user_mode(self.environment)
            if not current_mode:
                current_mode = self.user_mode or get_text("modes.sign_translate.name")

            # Show settings dialog (non-modal)
            selected_mode = show_settings_dialog(
                parent=self.main_window,
                current_mode=current_mode,
                callback=self.handle_settings_changed,
                environment=self.environment,
                main_window=self.main_window,
            )

            # Handle the result
            if selected_mode:
                self.logger.info(f"Settings dialog returned mode: {selected_mode}")
            else:
                self.logger.info("Settings dialog was cancelled")

        except Exception as e:
            self.logger.error(f"Error showing settings: {e}")
            log_exception(self.logger, "show_settings")

    def handle_settings_changed(self, mode: str) -> None:
        """Handle settings changes from the settings dialog"""
        try:
            # Prevent infinite loops during settings save
            if (
                hasattr(self, "_settings_save_in_progress")
                and self._settings_save_in_progress
            ):
                self.logger.debug("Settings save in progress, skipping mode update")
                return

            self._settings_save_in_progress = True

            # Switch to new mode using mode manager
            success = self.mode_manager.switch_mode_by_display_name(mode)
            if success:
                self.user_mode = mode
                self.logger.info(f"Switched to mode: {mode}")
            else:
                self.logger.warning(f"Failed to switch to mode: {mode}")

            # Apply theme and font settings
            self.apply_theme_and_font_settings()

            self._settings_save_in_progress = False

        except Exception as e:
            self.logger.error(f"Error handling settings change: {e}")
            self._settings_save_in_progress = False

    def apply_theme_and_font_settings(self) -> None:
        """Apply theme and font size settings to the UI"""
        try:
            from PySide6.QtWidgets import QApplication

            from .startup import get_font_size, get_theme

            # Get current settings (these calls are safe and won't trigger save loops)
            theme = get_theme(self.environment)
            font_size = get_font_size(self.environment)

            # Apply theme to QApplication
            app = QApplication.instance()
            if app and isinstance(app, QApplication):
                success = apply_theme(theme, app)
                if success:
                    self.logger.info(f"Theme applied successfully: {theme}")

                    # Update main window styling
                    self._update_main_window_theme()
                else:
                    self.logger.error(f"Failed to apply theme: {theme}")
            else:
                self.logger.warning(
                    "No QApplication instance found for theme application"
                )

            # Apply font size
            self._apply_font_size_setting(font_size)
            self.logger.info(f"Font size setting applied: {font_size}")

        except Exception as e:
            self.logger.error(f"Error applying theme and font settings: {e}")

    def _apply_font_size_setting(self, font_size: int) -> None:
        """Apply font size setting to the main window using centralized system"""
        try:
            # Check if app is shutting down
            if hasattr(self, "_shutting_down") and self._shutting_down:
                self.logger.debug("App shutting down, skipping font size application")
                return

            from ..utils.theme_manager import (
                apply_font_size_to_widget_tree,
                set_font_size,
            )

            # Set the font size in the theme manager FIRST
            set_font_size(font_size)
            self.logger.debug(f"Font size set in theme manager: {font_size}px")

            # Apply font size to the entire main window widget tree
            apply_font_size_to_widget_tree(self.main_window)

            # Apply font size directly to specific components for immediate effect
            self._apply_font_size_directly(font_size)

            # Force a small delay to ensure all components are updated
            from PySide6.QtCore import QCoreApplication

            QCoreApplication.processEvents()

            self.logger.info(f"Font size applied to main window: {font_size}px")
        except Exception as e:
            self.logger.error(f"Error applying font size setting: {e}")

    def _apply_font_size_directly(self, font_size: int) -> None:
        """Apply font size directly to specific UI components for immediate effect"""
        try:
            # Check if app is shutting down
            if hasattr(self, "_shutting_down") and self._shutting_down:
                self.logger.debug("App shutting down, skipping direct font application")
                return

            # Check if main window is still valid
            if not hasattr(self, "main_window") or self.main_window is None:
                self.logger.debug(
                    "Main window not available, skipping direct font application"
                )
                return

            from PySide6.QtGui import QFont

            # Create a new font with the specified size
            new_font = QFont()
            new_font.setPointSize(font_size)

            # Apply to text input components
            if hasattr(self.main_window, "text_input_frame"):
                if hasattr(self.main_window.text_input_frame, "text_input"):
                    self.main_window.text_input_frame.text_input.setFont(new_font)
                if hasattr(self.main_window.text_input_frame, "process_button"):
                    self.main_window.text_input_frame.process_button.setFont(new_font)
                if hasattr(self.main_window.text_input_frame, "clear_button"):
                    self.main_window.text_input_frame.clear_button.setFont(new_font)

            # Apply to output components
            if hasattr(self.main_window, "output_frame"):
                if hasattr(self.main_window.output_frame, "text_output"):
                    self.main_window.output_frame.text_output.setFont(new_font)

            # Apply to status bar
            if hasattr(self.main_window, "status_bar"):
                if hasattr(self.main_window.status_bar, "status_label"):
                    self.main_window.status_bar.status_label.setFont(new_font)

            # Apply to menu bar
            if hasattr(self.main_window, "menuBar"):
                menu_bar = self.main_window.menuBar()
                if menu_bar:
                    menu_bar.setFont(new_font)

            # Update fonts using the MainWindow's update_fonts method LAST
            # This ensures all font manager functions use the updated font size
            if hasattr(self.main_window, "update_fonts"):
                self.main_window.update_fonts()
                self.logger.debug("MainWindow update_fonts() called successfully")

            # Force refresh
            self.main_window.update()
            self.main_window.repaint()

            self.logger.debug(
                f"Direct font size application completed for {font_size}px"
            )

        except Exception as e:
            self.logger.error(f"Error applying font size directly: {e}")

    def _update_input_fields_theme_with_font_size(self, input_style: str) -> None:
        """Update input field styling with font size"""
        try:
            if hasattr(self.main_window, "text_input_frame"):
                if hasattr(self.main_window.text_input_frame, "text_input"):
                    self.main_window.text_input_frame.text_input.setStyleSheet(
                        input_style
                    )

            if hasattr(self.main_window, "output_frame"):
                if hasattr(self.main_window.output_frame, "text_output"):
                    self.main_window.output_frame.text_output.setStyleSheet(input_style)
        except Exception as e:
            self.logger.error(f"Error updating input fields theme with font size: {e}")

    def _update_buttons_theme_with_font_size(
        self, primary_style: str, secondary_style: str
    ) -> None:
        """Update button styling with font size"""
        try:
            if hasattr(self.main_window, "text_input_frame"):
                if hasattr(self.main_window.text_input_frame, "process_button"):
                    self.main_window.text_input_frame.process_button.setStyleSheet(
                        primary_style
                    )
                if hasattr(self.main_window.text_input_frame, "clear_button"):
                    self.main_window.text_input_frame.clear_button.setStyleSheet(
                        secondary_style
                    )
        except Exception as e:
            self.logger.error(f"Error updating buttons theme with font size: {e}")

    def _update_input_fields_font_size(self, font: QFont) -> None:
        """Update input field font sizes (legacy method - kept for compatibility)"""
        try:
            if hasattr(self.main_window, "text_input_frame"):
                if hasattr(self.main_window.text_input_frame, "text_input"):
                    self.main_window.text_input_frame.text_input.setFont(font)

            if hasattr(self.main_window, "output_frame"):
                if hasattr(self.main_window.output_frame, "text_output"):
                    self.main_window.output_frame.text_output.setFont(font)
        except Exception as e:
            self.logger.error(f"Error updating input fields font size: {e}")

    def _update_buttons_font_size(self, font: QFont) -> None:
        """Update button font sizes (legacy method - kept for compatibility)"""
        try:
            if hasattr(self.main_window, "text_input_frame"):
                if hasattr(self.main_window.text_input_frame, "process_button"):
                    self.main_window.text_input_frame.process_button.setFont(font)
                if hasattr(self.main_window.text_input_frame, "clear_button"):
                    self.main_window.text_input_frame.clear_button.setFont(font)
        except Exception as e:
            self.logger.error(f"Error updating buttons font size: {e}")

    def _update_main_window_theme(self) -> None:
        """Update main window styling to match current theme"""
        try:
            from ..utils.theme_manager import get_theme_color, get_theme_style

            # Apply theme styles to main window
            main_window_style = get_theme_style("main_window")
            if main_window_style:
                self.main_window.setStyleSheet(main_window_style)

            # Update specific components
            self._update_input_fields_theme()
            self._update_buttons_theme()

            # Force update of the main window
            self.main_window.update()
            self.main_window.repaint()

            self.logger.info("Main window theme updated")

        except Exception as e:
            self.logger.error(f"Error updating main window theme: {e}")

    def _update_input_fields_theme(self) -> None:
        """Update input field styling to match current theme"""
        try:
            from ..utils.theme_manager import get_theme_style

            input_style = get_theme_style("input_field")
            if input_style:
                # Apply to text input and output areas
                if hasattr(self.main_window, "text_input_frame"):
                    if hasattr(self.main_window.text_input_frame, "text_input"):
                        self.main_window.text_input_frame.text_input.setStyleSheet(
                            input_style
                        )

                if hasattr(self.main_window, "output_frame"):
                    if hasattr(self.main_window.output_frame, "text_output"):
                        self.main_window.output_frame.text_output.setStyleSheet(
                            input_style
                        )

        except Exception as e:
            self.logger.error(f"Error updating input fields theme: {e}")

    def _update_buttons_theme(self) -> None:
        """Update button styling to match current theme"""
        try:
            from ..utils.theme_manager import get_theme_style

            primary_button_style = get_theme_style("button_primary")
            secondary_button_style = get_theme_style("button_secondary")

            if primary_button_style and hasattr(self.main_window, "text_input_frame"):
                if hasattr(self.main_window.text_input_frame, "process_button"):
                    self.main_window.text_input_frame.process_button.setStyleSheet(
                        primary_button_style
                    )

            if secondary_button_style and hasattr(self.main_window, "text_input_frame"):
                if hasattr(self.main_window.text_input_frame, "clear_button"):
                    self.main_window.text_input_frame.clear_button.setStyleSheet(
                        secondary_button_style
                    )

        except Exception as e:
            self.logger.error(f"Error updating buttons theme: {e}")

    def set_user_mode_from_settings(self, mode: str) -> None:
        """Set user mode from settings dialog"""
        try:
            self.user_mode = mode
            set_user_mode(mode, self.environment)
            self.logger.info(f"User mode set from settings: {mode}")
        except Exception as e:
            self.logger.error(f"Error setting user mode from settings: {e}")

    def get_user_mode(self) -> Optional[str]:
        """Get the current user mode"""
        return self.user_mode

    def get_resource_info(self) -> Dict[str, Any]:
        """Get information about available resources"""
        return self.resource_manager.get_resource_info()

    def show(self) -> None:
        """Show the main window"""
        self.main_window.show()

    def run(self) -> None:
        """Run the application"""
        self.show()
        self.logger.info("Application started successfully")


def create_app(environment: str = "dev") -> HelpMeSignApp:
    """Create and return a HelpMeSign application instance"""
    return HelpMeSignApp(environment)
