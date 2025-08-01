import sys
from datetime import datetime
from typing import Any, Dict, Optional

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

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

        # Set up application
        self.setup_application()
        self.setup_event_handlers()

        # Show startup screen if no user mode is set
        self.check_user_mode()

        # Apply saved theme and font settings
        self.apply_theme_and_font_settings()

        # Set up application shutdown handling
        self._setup_shutdown_handling()

        log_function_exit(get_logger(), "HelpMeSignApp.__init__")

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
            self.logger.info("Application shutting down, cleaning up resources...")

            # Simple cleanup - just log the event
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
        """Set up event handlers for UI components"""
        # Connect text processing signals
        self.main_window.process_requested.connect(self.process_text)
        self.main_window.clear_requested.connect(self.clear_text)

        # Connect settings signal
        self.main_window.settings_requested.connect(self.show_settings)

        # Set initial mode
        self.update_ui_for_mode(get_text("modes.sign_translate.name"))

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

    def process_text(self) -> None:
        """Process the input text based on current mode"""
        try:
            input_text = self.main_window.get_input_text()  # type: ignore

            if not input_text.strip():
                self.main_window.set_output_text(get_text("ui.output.empty_message"))  # type: ignore
                return

            # Process based on current mode
            if self.user_mode == get_text("modes.sign_translate.name"):
                # Convert text to sign language representation
                output = self.convert_to_sign_language(input_text)
                self.main_window.set_output_text(output)  # type: ignore
                self.main_window.set_status(
                    f"{get_text('ui.status.converted_prefix')}{input_text}{get_text('ui.status.converted_suffix')}"
                )

            elif self.user_mode == get_text("modes.learn.name"):
                # Educational mode - show sign language information
                output = self.get_sign_language_info(input_text)
                self.main_window.set_output_text(output)  # type: ignore
                self.main_window.set_status(
                    f"{get_text('ui.status.learning_prefix')}{input_text}{get_text('ui.status.learning_suffix')}"
                )

            else:
                # Default to Sign & Translate
                output = self.convert_to_sign_language(input_text)
                self.main_window.set_output_text(output)  # type: ignore
                self.main_window.set_status(
                    f"{get_text('ui.status.converted_prefix')}{input_text}{get_text('ui.status.converted_suffix')}"
                )

        except Exception as e:
            self.logger.error(f"Error processing text: {e}")
            self.main_window.set_output_text(f"{get_text('ui.status.error_prefix')}{e}")  # type: ignore

    def convert_to_sign_language(self, text: str) -> str:
        """Convert text to sign language representation"""
        # This is a placeholder implementation
        # In a real application, this would use a sign language translation service
        words = text.lower().split()
        sign_representations = []

        for word in words:
            # Simple mapping for demonstration
            if word in ["hello", "hi"]:
                sign_representations.append(get_text("sign_language.conversion.hello"))
            elif word in ["thank", "thanks", "thank you"]:
                sign_representations.append(
                    get_text("sign_language.conversion.thank_you")
                )
            elif word in ["yes"]:
                sign_representations.append(get_text("sign_language.conversion.yes"))
            elif word in ["no"]:
                sign_representations.append(get_text("sign_language.conversion.no"))
            elif word in ["please"]:
                sign_representations.append(get_text("sign_language.conversion.please"))
            elif word in ["sorry"]:
                sign_representations.append(get_text("sign_language.conversion.sorry"))
            else:
                sign_representations.append(
                    f"{get_text('sign_language.conversion.spell_prefix')}{' '.join(word.upper())}"
                )

        return "\n".join(sign_representations)

    def get_sign_language_info(self, text: str) -> str:
        """Get educational information about sign language"""
        # This is a placeholder implementation
        # In a real application, this would provide educational content
        basic_signs = get_dict("sign_language.learning.basic_signs")
        tips = get_list("sign_language.learning.tips")

        result = f"{get_text('sign_language.learning.title_prefix')}{text}{get_text('sign_language.learning.title_suffix')}\n\n"
        result += f"{get_text('sign_language.learning.basic_signs_title')}\n"

        for sign_name, sign_description in basic_signs.items():
            result += f"• {sign_description}\n"

        result += f"\n{get_text('sign_language.learning.tips_title')}\n"
        for tip in tips:
            result += f"• {tip}\n"

        result += f"\n{get_text('sign_language.learning.practice_prefix')}{text}{get_text('sign_language.learning.practice_suffix')}"

        return result

    def clear_text(self) -> None:
        """Clear input and output text"""
        self.main_window.clear_input()  # type: ignore
        self.main_window.clear_output()  # type: ignore
        self.main_window.set_status(get_text("ui.status.cleared"))

    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration"""
        return self.config

    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """Save configuration"""
        try:
            self.config.update(config_data)
            return self.resource_manager.save_config(self.config)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False

    def check_user_mode(self) -> None:
        """Check if user mode is set and show startup screen if needed"""
        try:
            # Try to get user mode with environment-specific config
            mode = get_user_mode(self.environment)

            if mode:
                self.user_mode = mode
                self.update_ui_for_mode(mode)
                self.logger.info(f"User mode loaded: {mode}")
            else:
                # No user mode set, show startup screen
                self.logger.info("No user mode set, showing startup screen")
                self.show_startup_screen()

        except Exception as e:
            self.logger.warning(f"Error checking user mode: {e}")
            # Show startup screen on error
            self.show_startup_screen()

    def show_startup_screen(self) -> None:
        """Show the startup screen for mode selection"""
        try:
            self.logger.info("Showing startup screen")

            # Show startup screen
            mode = show_startup_screen()

            if mode:
                self.user_mode = mode
                set_user_mode(mode, self.environment)
                self.update_ui_for_mode(mode)
                self.logger.info(f"User mode set from startup screen: {mode}")
            else:
                # Default to Sign & Translate if no selection
                self.user_mode = get_text("modes.sign_translate.name")
                set_user_mode(self.user_mode, self.environment)
                self.update_ui_for_mode(self.user_mode)
                self.logger.info("No mode selected, using default: Sign & Translate")

        except Exception as e:
            self.logger.error(f"Error showing startup screen: {e}")
            # Default to Sign & Translate on error
            self.user_mode = get_text("modes.sign_translate.name")
            self.update_ui_for_mode(self.user_mode)

    def update_ui_for_mode(self, mode: str) -> None:
        """Update the UI to reflect the current mode"""
        try:
            self.main_window.set_mode(mode)
            self.main_window.set_status(f"Mode: {mode}")
            self.logger.info(f"UI updated for mode: {mode}")
        except Exception as e:
            self.logger.error(f"Error updating UI for mode: {e}")

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
        """Handle all settings changes from settings dialog"""
        try:
            # Update user mode
            self.user_mode = mode
            self.update_ui_for_mode(mode)

            # Apply theme and font size changes
            self.apply_theme_and_font_settings()

            self.logger.info(f"Settings applied: mode={mode}")
        except Exception as e:
            self.logger.error(f"Error applying settings: {e}")

    def apply_theme_and_font_settings(self) -> None:
        """Apply theme and font size settings to the UI"""
        try:
            from PySide6.QtWidgets import QApplication

            from .startup import get_font_size, get_theme

            # Get current settings
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

            # Apply font size (placeholder for future implementation)
            self.logger.info(f"Font size setting: {font_size}")

        except Exception as e:
            self.logger.error(f"Error applying theme and font settings: {e}")

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
        """Handle mode change from settings dialog"""
        try:
            self.user_mode = mode
            set_user_mode(mode, self.environment)
            self.update_ui_for_mode(mode)
            self.logger.info(f"User mode changed from settings: {mode}")
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
