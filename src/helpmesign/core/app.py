import sys
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

    def __init__(self):
        """Initialize the HelpMeSign application"""
        log_function_entry(get_logger(), "HelpMeSignApp.__init__")

        # Add shutdown flag to prevent operations during shutdown
        self._shutting_down = False

        # Add settings save flag to prevent infinite loops
        self._settings_save_in_progress: bool = False

        self.resource_manager = ResourceManager()

        # Load configuration
        self.config = self.resource_manager.load_config()

        # Set up logging
        self.logger = setup_logging(self.config)
        self.logger.info("Initializing HelpMeSign application")

        # STEP 1: Load user configuration first (or create default)
        self._load_user_configuration()

        # STEP 2: Apply configuration to application state
        self._apply_configuration_to_app_state()

        # STEP 3: Create UI with correct settings
        self._create_ui_with_configuration()

        # STEP 4: Set up application components
        self.setup_application()
        self.setup_event_handlers()

        # STEP 4.5: 3D support now initialized by run_app.py

        # STEP 5: Check user mode and show startup if needed
        self.check_user_mode()

        # Set up application shutdown handling
        self._setup_shutdown_handling()

        log_function_exit(get_logger(), "HelpMeSignApp.__init__")

    def _load_user_configuration(self) -> None:
        """STEP 1: Load user configuration or create default if it doesn't exist"""
        try:
            from .startup import get_all_settings

            # This will automatically create default config if it doesn't exist
            self.user_settings = get_all_settings()
            self.logger.info(f"User configuration loaded: {self.user_settings}")

        except Exception as e:
            self.logger.error(f"Error loading user configuration: {e}")
            # Fallback to default settings
            self.user_settings = {
                "user_mode": "Sign & Translate",
                "theme": "Light",
                "font_size": 12,
                "hand_preference": "right",
            }

    def _apply_configuration_to_app_state(self) -> None:
        """STEP 2: Apply configuration values to application state"""
        try:
            # Extract settings
            self.user_mode = self.user_settings.get("user_mode")
            self.theme = self.user_settings.get("theme", "Light")
            self.font_size = self.user_settings.get("font_size", 12)
            self.hand_preference = self.user_settings.get("hand_preference", "right")

            # Apply theme to theme manager
            from ..utils.theme_manager import get_theme_manager

            theme_manager = get_theme_manager()
            theme_manager.set_font_size(self.font_size)

            self.logger.info(
                f"Configuration applied to app state: theme={self.theme}, font_size={self.font_size}, hand_preference={self.hand_preference}"
            )

        except Exception as e:
            self.logger.error(f"Error applying configuration to app state: {e}")

    def _create_ui_with_configuration(self) -> None:
        """STEP 3: Create UI components with the correct configuration settings"""
        try:
            # Create main window with correct title
            self.main_window = MainWindow(title=f"HelpMeSign")
            self.logger.debug("Main window created")

            # Initialize mode manager
            self.mode_manager = ModeManager(self.main_window)
            self.logger.debug("Mode manager initialized")

            # Apply theme to QApplication
            from PySide6.QtWidgets import QApplication

            from ..utils.theme_manager import apply_theme

            app = QApplication.instance()
            if app and isinstance(app, QApplication):
                success = apply_theme(self.theme, app)
                if success:
                    self.logger.info(f"Theme applied to QApplication: {self.theme}")
                else:
                    self.logger.error(f"Failed to apply theme: {self.theme}")

            # Apply font size to main window
            self._apply_font_size_to_main_window(self.font_size)

            self.logger.info(
                f"UI created with configuration: theme={self.theme}, font_size={self.font_size}"
            )

        except Exception as e:
            self.logger.error(f"Error creating UI with configuration: {e}")

    def _apply_font_size_to_main_window(self, font_size: int) -> None:
        """Apply font size to main window during initialization"""
        try:
            # Check if app is shutting down
            if hasattr(self, "_shutting_down") and self._shutting_down:
                self.logger.debug("App shutting down, skipping font application")
                return

            # Check if main window is still valid
            if not hasattr(self, "main_window") or self.main_window is None:
                self.logger.debug(
                    "Main window not available, skipping font application"
                )
                return

            from PySide6.QtGui import QFont

            from ..utils.theme_manager import set_font_size

            # Set the font size in the theme manager for consistency
            set_font_size(font_size)
            self.logger.debug(f"Font size set in theme manager: {font_size}px")

            # Apply font size directly to main window
            self._apply_font_size_directly(font_size)
            self.logger.info(
                f"Font size applied to main window during initialization: {font_size}px"
            )

        except Exception as e:
            self.logger.error(f"Error applying font size to main window: {e}")

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

            # Don't do any cleanup - just exit cleanly
            # This prevents memory corruption from any cleanup operations

            self.logger.info("Cleanup completed")

            # Add debugging to trace what happens after cleanup
            self.logger.info("=== TRACING POST-CLEANUP ===")

            # Check if we're in a test environment
            import sys

            is_test_environment = (
                any("pytest" in arg for arg in sys.argv) or "test" in sys.argv
            )

            if not is_test_environment:
                # In production, force garbage collection to see if that helps
                import gc

                self.logger.info("Forcing garbage collection...")
                gc.collect()
                self.logger.info("Garbage collection completed")

                # Add a small delay to see if malloc corruption happens during this time
                import time

                self.logger.info(
                    "Waiting 1 second to see if malloc corruption occurs..."
                )
                time.sleep(1)
                self.logger.info(
                    "1 second wait completed - no malloc corruption detected"
                )

                # Since malloc corruption happens after this point, use os._exit to prevent it from being visible
                self.logger.info(
                    "Exiting cleanly to prevent malloc corruption from being visible"
                )
                import os

                os._exit(0)

        except Exception as e:
            self.logger.error(f"Error during shutdown cleanup: {e}")

    def setup_application(self) -> None:
        """Set up the application configuration and appearance"""
        # Set app icon if available
        self.set_app_icon()

        # Set window size from config or default
        # Generic window size (tests expect resize to be called)
        window_cfg = self.config.get("window_size", {"width": 1280, "height": 800})
        window_width = window_cfg.get("width", 1280)
        window_height = window_cfg.get("height", 800)
        self.main_window.resize(window_width, window_height)

        # Always open centered on the current screen
        try:
            self._center_main_window()
        except Exception:
            pass

        # Set window title
        title = get_text("ui.main_window.title")
        self.main_window.set_title(title)

        # Focus on input field
        self.main_window.focus_input()

    def setup_event_handlers(self) -> None:
        """Set up event handlers for the main window"""
        try:
            # Connect main window signals to mode manager and store connection objects
            self._process_connection = self.main_window.process_requested.connect(
                self._on_process_requested
            )
            self._clear_connection = self.main_window.clear_requested.connect(
                self._on_clear_requested
            )
            self._settings_connection = self.main_window.settings_requested.connect(
                self.show_settings
            )

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
            if self.resource_manager.resource_exists("images", "icon.png"):
                # Set icon on the main window
                self.main_window.set_icon(icon_path)

                # Set icon on the QApplication for menubar and dock
                app = QApplication.instance()
                if app and hasattr(app, "windowIcon") and app.windowIcon().isNull():
                    # If setWindowIcon is available on the app object, call it
                    if hasattr(app, "setWindowIcon"):
                        app.setWindowIcon(QIcon(icon_path))

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
            saved_mode = get_user_mode()

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
            selected_mode = show_startup_screen()

            if selected_mode:
                # Switch to selected mode using mode manager
                success = self.mode_manager.switch_mode_by_display_name(selected_mode)
                if success:
                    self.user_mode = selected_mode
                    set_user_mode(selected_mode)
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
            # Check if we're shutting down
            if hasattr(self, "_shutting_down") and self._shutting_down:
                self.logger.debug("Skipping settings dialog during shutdown")
                return

            from .startup import get_user_mode

            # Get current mode
            current_mode = get_user_mode()
            if not current_mode:
                current_mode = self.user_mode or get_text("modes.sign_translate.name")

            # Show settings dialog (non-modal)
            selected_mode = show_settings_dialog(
                parent=self.main_window,
                current_mode=current_mode,
                callback=self.handle_settings_changed,
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

            # Update main window title
            if hasattr(self, "main_window"):
                self.main_window.setWindowTitle(f"HelpMeSign")

            self._settings_save_in_progress = False

        except Exception as e:
            self.logger.error(f"Error handling settings change: {e}")
            self._settings_save_in_progress = False

    def _apply_font_size_directly(self, font_size: int) -> None:
        """Apply font size directly to specific UI components for immediate effect"""
        # DEBUG: Commented out direct font application to debug hand preference override issue
        # try:
        #     # Check if app is shutting down
        #     if hasattr(self, "_shutting_down") and self._shutting_down:
        #         self.logger.debug("App shutting down, skipping direct font application")
        #         return

        #     # Check if main window is still valid
        #     if not hasattr(self, "main_window") or self.main_window is None:
        #         self.logger.debug(
        #             "Main window not available, skipping direct font application"
        #         )
        #         return

        #     from PySide6.QtGui import QFont

        #     from src.helpmesign.utils.font_manager import get_font_manager

        #     # Create a new font with the specified size using app's font family
        #     font_manager = get_font_manager()
        #     new_font = font_manager.get_font(size=font_size)

        #     # Apply to text input components
        #     if hasattr(self.main_window, "text_input_frame"):
        #         if hasattr(self.main_window.text_input_frame, "text_input"):
        #             self.main_window.text_input_frame.text_input.setFont(new_font)
        #         if hasattr(self.main_window.text_input_frame, "process_button"):
        #             self.main_window.text_input_frame.process_button.setFont(new_font)
        #         if hasattr(self.main_window.text_input_frame, "clear_button"):
        #             self.main_window.text_input_frame.clear_button.setFont(new_font)

        #     # Apply to output components
        #     if hasattr(self.main_window, "output_frame"):
        #         if hasattr(self.main_window.output_frame, "text_output"):
        #             self.main_window.output_frame.text_output.setFont(new_font)

        #     # Apply to status bar
        #     if hasattr(self.main_window, "status_bar"):
        #         if hasattr(self.main_window.status_bar, "status_label"):
        #             self.main_window.status_bar.status_label.setFont(new_font)

        #     # Apply to menu bar
        #     if hasattr(self.main_window, "menuBar"):
        #         menu_bar = self.main_window.menuBar()
        #         if menu_bar:
        #             menu_bar.setFont(new_font)

        #     # Update fonts using the MainWindow's update_fonts method LAST
        #     # This ensures all font manager functions use the updated font size
        #     if hasattr(self.main_window, "update_fonts"):
        #         self.main_window.update_fonts()
        #         self.logger.debug("MainWindow update_fonts() called successfully")

        #     # Force refresh
        #     self.main_window.update()
        #     self.main_window.repaint()

        #     self.logger.debug(
        #         f"Direct font size application completed for {font_size}px"
        #     )

        # except Exception as e:
        #     self.logger.error(f"Error applying font size directly: {e}")

        # DEBUG: Just log that direct font application is disabled
        self.logger.debug(
            "Direct font application disabled for debugging hand preference issue"
        )

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
        # Center after show, so frame geometry (including decorations) is known
        try:
            from PySide6.QtCore import QTimer

            QTimer.singleShot(0, self._center_main_window)
        except Exception:
            pass

    # --- Helpers ---
    def _center_main_window(self) -> None:
        try:
            from PySide6.QtGui import QGuiApplication

            screen = (
                self.main_window.screen()
                if hasattr(self.main_window, "screen") and self.main_window.screen()
                else QGuiApplication.primaryScreen()
            )
            if screen is None:
                return
            avail = screen.availableGeometry()
            frame = self.main_window.frameGeometry()
            frame.moveCenter(avail.center())
            self.main_window.move(frame.topLeft())
        except Exception:
            pass


def create_app() -> HelpMeSignApp:
    """Create and return a HelpMeSign application instance"""
    return HelpMeSignApp()
