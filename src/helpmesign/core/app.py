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
from .startup import (
    SecureConfigManager,
    get_user_mode,
    set_user_mode,
    show_startup_screen,
)


class HelpMeSignApp:
    """Main application class for HelpMeSign"""

    def __init__(self, environment: str = "dev"):
        """
        Initialize the HelpMeSign application

        Args:
            environment: Environment to run in ("dev" or "prod")
        """
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
        self.user_mode = None

        # Create main window
        self.main_window = MainWindow(title=f"HelpMeSign ({self.environment.upper()})")
        self.logger.debug("Main window created")

        # Set up application
        self.setup_application()
        self.setup_event_handlers()

        # Show startup screen if no user mode is set
        self.check_user_mode()

        log_function_exit(get_logger(), "HelpMeSignApp.__init__")

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
                if app and app.windowIcon().isNull():
                    app.setWindowIcon(QIcon(icon_path))

                self.logger.info("App icon loaded successfully")
            else:
                self.logger.warning("App icon not found")
        except Exception as e:
            self.logger.warning(f"Could not load app icon: {e}")

    def process_text(self) -> None:
        """Process the input text based on current mode"""
        try:
            input_text = self.main_window.get_input_text()

            if not input_text.strip():
                self.main_window.set_output_text(get_text("ui.output.empty_message"))
                return

            # Process based on current mode
            if self.user_mode == get_text("modes.sign_translate.name"):
                # Convert text to sign language representation
                output = self.convert_to_sign_language(input_text)
                self.main_window.set_output_text(output)
                self.main_window.set_status(
                    f"{get_text('ui.status.converted_prefix')}{input_text}{get_text('ui.status.converted_suffix')}"
                )

            elif self.user_mode == get_text("modes.learn.name"):
                # Educational mode - show sign language information
                output = self.get_sign_language_info(input_text)
                self.main_window.set_output_text(output)
                self.main_window.set_status(
                    f"{get_text('ui.status.learning_prefix')}{input_text}{get_text('ui.status.learning_suffix')}"
                )

            else:
                # Default to Sign & Translate
                output = self.convert_to_sign_language(input_text)
                self.main_window.set_output_text(output)
                self.main_window.set_status(
                    f"{get_text('ui.status.converted_prefix')}{input_text}{get_text('ui.status.converted_suffix')}"
                )

        except Exception as e:
            self.logger.error(f"Error processing text: {e}")
            self.main_window.set_output_text(f"{get_text('ui.status.error_prefix')}{e}")

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
        self.main_window.clear_input()
        self.main_window.clear_output()
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
            current_mode = self.user_mode or "Sign & Translate"

            # Show settings dialog
            selected_mode = show_settings_dialog(
                parent=self.main_window,
                current_mode=current_mode,
                callback=self.set_user_mode_from_settings,
            )

            if selected_mode:
                self.user_mode = selected_mode
                set_user_mode(selected_mode, self.environment)
                self.update_ui_for_mode(selected_mode)
                self.logger.info(f"User mode changed via settings: {selected_mode}")

        except Exception as e:
            self.logger.error(f"Error showing settings: {e}")

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
