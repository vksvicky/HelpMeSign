"""
Startup screen and configuration management for HelpMeSign
"""

import getpass
import hashlib
import hmac
import json
import os
import platform
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

if TYPE_CHECKING:
    from PySide6.QtCore import Qt, QTimer, Signal
    from PySide6.QtGui import QFont, QPixmap
    from PySide6.QtWidgets import (
        QDialog,
        QFrame,
        QHBoxLayout,
        QLabel,
        QMessageBox,
        QPushButton,
        QSizePolicy,
        QVBoxLayout,
    )

# Try to import PySide6 components
try:
    from PySide6.QtCore import Qt, QTimer, Signal
    from PySide6.QtGui import QFont, QPixmap
    from PySide6.QtWidgets import (
        QDialog,
        QFrame,
        QHBoxLayout,
        QLabel,
        QMessageBox,
        QPushButton,
        QSizePolicy,
        QVBoxLayout,
    )

    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

from ..utils.language_manager import get_dict, get_list, get_text
from ..utils.logger import get_logger

# Conditional font manager import
try:
    from ..utils.font_manager import get_button_font, get_heading_font, get_title_font

    FONT_MANAGER_AVAILABLE = True
except ImportError:
    FONT_MANAGER_AVAILABLE = False

    # Create dummy functions with proper return types
    def get_button_font() -> Union[QFont, None]:  # type: ignore
        return None

    def get_heading_font() -> Union[QFont, None]:  # type: ignore
        return None

    def get_title_font() -> Union[QFont, None]:  # type: ignore
        return None


class StartupScreen(QDialog):
    """Startup screen with user choice functionality"""

    # Signal emitted when user makes a choice
    choice_made = Signal(str)

    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            raise ImportError("PySide6 is required for StartupScreen")

        super().__init__(parent)
        self.logger = get_logger("helpmesign.startup")
        self.logger.info("Initializing startup screen")

        # Set window properties
        self.setWindowTitle(get_text("startup.title"))
        self.setFixedSize(500, 400)
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)

        # Setup UI
        self.setup_ui()
        self.setup_behavior()

        # Load previous choice
        self.load_previous_choice()

        self.logger.debug("Startup screen initialized")

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title_label = QLabel(get_text("startup.title"))
        title_label.setFont(get_title_font())
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel(get_text("startup.subtitle"))
        subtitle_label.setFont(get_heading_font())
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        layout.addWidget(subtitle_label)

        # Mode selection buttons
        self.create_mode_buttons(layout)

        # Info text
        info_label = QLabel(get_text("startup.info_text"))
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #95a5a6; font-size: 11px; margin-top: 20px;")
        layout.addWidget(info_label)

        self.setLayout(layout)

    def create_mode_buttons(self, layout):
        """Create mode selection buttons"""
        # Container for buttons
        button_container = QFrame()
        button_container.setStyleSheet(
            """
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                padding: 20px;
            }
        """
        )

        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)

        # Sign & Translate mode
        sign_translate_btn = QPushButton(get_text("modes.sign_translate.button_text"))
        sign_translate_btn.setFont(get_button_font())
        sign_translate_btn.setFixedHeight(50)
        sign_translate_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """
        )
        sign_translate_btn.clicked.connect(lambda: self.make_choice("sign_translate"))
        button_layout.addWidget(sign_translate_btn)

        # Learn mode
        learn_btn = QPushButton(get_text("modes.learn.button_text"))
        learn_btn.setFont(get_button_font())
        learn_btn.setFixedHeight(50)
        learn_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """
        )
        learn_btn.clicked.connect(lambda: self.make_choice("learn"))
        button_layout.addWidget(learn_btn)

        button_container.setLayout(button_layout)
        layout.addWidget(button_container)

        # Store button references for highlighting
        self.sign_translate_btn = sign_translate_btn
        self.learn_btn = learn_btn

    def setup_behavior(self):
        """Setup dialog behavior"""
        # Center on screen
        self.center_on_screen()

        # Auto-close after 30 seconds if no choice made
        self.auto_close_timer = QTimer()
        self.auto_close_timer.timeout.connect(self.auto_close)
        self.auto_close_timer.start(30000)  # 30 seconds

    def center_on_screen(self):
        """Center the dialog on the screen"""
        screen = self.screen()
        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def load_previous_choice(self):
        """Load and highlight previous user choice"""
        try:
            config_manager = SecureConfigManager()
            previous_mode = config_manager.get_user_mode()
            if previous_mode:
                self.highlight_previous_choice(previous_mode)
                self.logger.debug(f"Previous mode loaded: {previous_mode}")
        except Exception as e:
            self.logger.warning(f"Could not load previous choice: {e}")

    def highlight_previous_choice(self, mode: str):
        """Highlight the previously selected mode"""
        if mode == "sign_translate":
            self.sign_translate_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #2980b9;
                    color: white;
                    border: 3px solid #21618c;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #21618c;
                }
            """
            )
            self.sign_translate_btn.setText(
                get_text("modes.sign_translate.previous_choice_text")
            )
        elif mode == "learn":
            self.learn_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #229954;
                    color: white;
                    border: 3px solid #1e8449;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1e8449;
                }
            """
            )
            self.learn_btn.setText(get_text("modes.learn.previous_choice_text"))

    def make_choice(self, choice: str):
        """Handle user choice"""
        try:
            # Stop auto-close timer
            self.auto_close_timer.stop()

            # Save choice
            config_manager = SecureConfigManager()
            if config_manager.set_user_mode(choice):
                self.logger.info(f"User choice saved: {choice}")
            else:
                self.logger.warning("Failed to save user choice")

            # Emit signal
            self.choice_made.emit(choice)

            # Close dialog
            self.accept()

        except Exception as e:
            self.logger.error(f"Error handling user choice: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save your choice: {e}")

    def auto_close(self):
        """Auto-close dialog if no choice made"""
        self.logger.info(get_text("startup.auto_close_message"))
        self.reject()

    def get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()


class SecureConfigManager:
    """Secure configuration manager with system-derived key protection"""

    def __init__(self) -> None:
        self.config_dir = Path.home() / ".helpmesign"
        self.config_file = self.config_dir / "user_config.secure"
        self.logger = get_logger("helpmesign.config")
        self._saving_settings: bool = False

        # Ensure config directory exists with secure permissions
        self.config_dir.mkdir(mode=0o700, exist_ok=True)

    def _derive_secret_key(self) -> bytes:
        """
        Derive secret key from system/user-specific data
        This makes it virtually impossible to decrypt without knowing the derivation method
        """
        # Get system-specific identifiers
        system_info = [
            platform.system(),  # OS (Windows, Darwin, Linux)
            platform.machine(),  # Architecture (x86_64, arm64, etc.)
            platform.node(),  # Hostname
            getpass.getuser(),  # Username
            str(Path.home()),  # Home directory path
            get_text("app.name"),  # Application identifier
            self._get_mac_address(),  # MAC address for machine uniqueness
        ]

        # Create a unique salt for this system/user
        salt = "|".join(system_info).encode("utf-8")

        # Use PBKDF2 to derive a key from the salt
        # This makes it computationally expensive to brute force
        import hashlib

        key = hashlib.pbkdf2_hmac(
            "sha256",
            salt,
            salt,  # Use salt as both password and salt
            iterations=100000,  # High iteration count for security
            dklen=32,  # 32 bytes for SHA-256
        )

        self.logger.debug("Secret key derived from system data")
        return key

    def _get_mac_address(self) -> str:
        """Get the primary MAC address of the machine"""
        try:
            # Get the MAC address as a hex string
            mac = uuid.getnode()
            mac_address = ":".join(
                [
                    "{:02x}".format((mac >> elements) & 0xFF)
                    for elements in range(0, 2 * 6, 2)
                ][::-1]
            )
            self.logger.debug(f"MAC address retrieved: {mac_address}")
            return mac_address
        except Exception as e:
            self.logger.warning(f"Could not get MAC address: {e}")
            return "unknown_mac"

    def _create_hmac(self, data: str) -> bytes:
        """Create HMAC signature for data"""
        key = self._derive_secret_key()
        return hmac.new(key, data.encode("utf-8"), hashlib.sha256).digest()

    def _verify_hmac(self, data: str, signature: bytes) -> bool:
        """Verify HMAC signature for data"""
        expected_signature = self._create_hmac(data)
        return hmac.compare_digest(signature, expected_signature)

    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration with HMAC protection"""
        try:
            # Ensure config directory exists
            self.config_dir.mkdir(mode=0o700, exist_ok=True)

            # Add metadata
            config["timestamp"] = self.get_timestamp()
            config["version"] = "1.0"

            # Convert to JSON with consistent ordering
            json_data = json.dumps(config, sort_keys=True, separators=(",", ":"))

            # Create HMAC signature
            signature = self._create_hmac(json_data)

            # Save data and signature
            with open(self.config_file, "wb") as f:
                f.write(json_data.encode("utf-8"))
                f.write(b"\n---SIGNATURE---\n")
                f.write(signature)

            # Set restrictive permissions
            os.chmod(self.config_file, 0o600)  # Owner only

            self.logger.info("Configuration saved securely")
            return True

        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False

    def load_config(self) -> Dict[str, Any]:
        """Load configuration with HMAC verification"""
        try:
            if not self.config_file.exists():
                self.logger.debug(
                    "Configuration file does not exist, creating default configuration"
                )
                return self._create_default_config()

            with open(self.config_file, "rb") as f:
                content = f.read()

            # Split data and signature
            parts = content.split(b"\n---SIGNATURE---\n")
            if len(parts) != 2:
                raise ValueError("Invalid configuration file format")

            json_data = parts[0].decode("utf-8")
            signature = parts[1]

            # Verify signature
            if not self._verify_hmac(json_data, signature):
                raise ValueError("Configuration file has been tampered with")

            # Parse JSON
            config = json.loads(json_data)

            # Environment field is deprecated; ignore if present

            self.logger.info("Configuration loaded and verified successfully")
            return config

        except FileNotFoundError:
            self.logger.debug(
                "Configuration file not found, creating default configuration"
            )
            return self._create_default_config()
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in configuration file: {e}")
            return self._create_default_config()
        except ValueError as e:
            self.logger.error(f"Configuration verification failed: {e}")
            return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            return self._create_default_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """Create and save default configuration"""
        try:
            from ..utils.language_manager import get_text

            default_config = {
                "user_mode": get_text("modes.sign_translate.name"),
                "theme": "Light",
                "font_size": 12,
                "hand_preference": "right",
                "selected_language": "ASL",
                "version": "1.0",
                "timestamp": self.get_timestamp(),
            }

            # Save the default configuration
            if self.save_config(default_config):
                self.logger.info("Default configuration created and saved successfully")
                return default_config
            else:
                self.logger.error("Failed to save default configuration")
                return {}

        except Exception as e:
            self.logger.error(f"Error creating default configuration: {e}")
            return {}

    def get_user_mode(self) -> Optional[str]:
        """Get user's preferred mode"""
        try:
            config = self.load_config()
            return config.get("user_mode")
        except Exception as e:
            self.logger.warning(f"Could not get user mode: {e}")
            return None

    def set_user_mode(self, mode: str) -> bool:
        """Set user's preferred mode"""
        try:
            # Check if we're already in a save operation to prevent infinite loops
            if hasattr(self, "_saving_settings") and self._saving_settings:
                self.logger.warning("Already saving settings, skipping mode save")
                return True

            config = self.load_config() or {}
            config["user_mode"] = mode
            config["last_updated"] = self.get_timestamp()
            return self.save_config(config)
        except Exception as e:
            self.logger.error(f"Could not save user mode: {e}")
            return False

    def get_theme(self) -> str:
        """Get user's preferred theme"""
        try:
            config = self.load_config()
            if config:
                theme = config.get("theme", "Light")
                # If theme is "System", resolve it to the actual system theme
                if theme == "System":
                    return self._resolve_system_theme()
                return theme
            return "Light"
        except Exception as e:
            self.logger.warning(f"Could not get theme: {e}")
            return "Light"

    def _resolve_system_theme(self) -> str:
        """Resolve System theme to actual Light or Dark based on OS preference"""
        try:
            from ..utils.theme_manager import get_theme_manager

            theme_manager = get_theme_manager()
            return theme_manager._detect_system_theme()
        except Exception as e:
            self.logger.warning(
                f"Could not resolve system theme: {e}, defaulting to Light"
            )
            return "Light"

    def set_theme(self, theme: str) -> bool:
        """Set user's preferred theme with validation"""
        try:
            # Validate theme value
            if not self._validate_theme(theme):
                self.logger.error(f"Invalid theme value: {theme}")
                return False

            # Check if we're already in a save operation to prevent infinite loops
            if hasattr(self, "_saving_settings") and self._saving_settings:
                self.logger.warning("Already saving settings, skipping theme save")
                return True

            config = self.load_config() or {}
            config["theme"] = theme
            config["last_updated"] = self.get_timestamp()
            config["theme_last_changed"] = self.get_timestamp()
            return self.save_config(config)
        except Exception as e:
            self.logger.error(f"Could not save theme: {e}")
            return False

    def _validate_theme(self, theme: str) -> bool:
        """Validate theme value"""
        valid_themes = ["Light", "Dark", "System"]
        if theme not in valid_themes:
            self.logger.warning(
                f"Invalid theme '{theme}'. Valid themes are: {valid_themes}"
            )
            return False
        return True

    def get_font_size(self) -> int:
        """Get user's preferred font size"""
        try:
            config = self.load_config()
            if config:
                return config.get("font_size", 12)
            return 12
        except Exception as e:
            self.logger.warning(f"Could not get font size: {e}")
            return 12

    def set_font_size(self, font_size: int) -> bool:
        """Set user's preferred font size"""
        try:
            # Check if we're already in a save operation to prevent infinite loops
            if hasattr(self, "_saving_settings") and self._saving_settings:
                self.logger.warning("Already saving settings, skipping font size save")
                return True

            config = self.load_config() or {}
            config["font_size"] = font_size
            config["last_updated"] = self.get_timestamp()
            return self.save_config(config)
        except Exception as e:
            self.logger.error(f"Could not save font size: {e}")
            return False

    def get_hand_preference(self) -> str:
        """Get user's preferred hand"""
        try:
            config = self.load_config()
            if config:
                return config.get("hand_preference", "right")
            return "right"
        except Exception as e:
            self.logger.warning(f"Could not get hand preference: {e}")
            return "right"

    def set_hand_preference(self, hand_preference: str) -> bool:
        """Set user's preferred hand"""
        try:
            # Check if we're already in a save operation to prevent infinite loops
            if hasattr(self, "_saving_settings") and self._saving_settings:
                self.logger.warning(
                    "Already saving settings, skipping hand preference save"
                )
                return True

            config = self.load_config() or {}
            config["hand_preference"] = hand_preference
            config["last_updated"] = self.get_timestamp()
            return self.save_config(config)
        except Exception as e:
            self.logger.error(f"Could not save hand preference: {e}")
            return False

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all user settings"""
        try:
            config = self.load_config() or {}
            theme = config.get("theme", "Light")
            # If theme is "System", resolve it to the actual system theme
            if theme == "System":
                theme = self._resolve_system_theme()

            return {
                "user_mode": config.get(
                    "user_mode", get_text("modes.sign_translate.name")
                ),
                "theme": theme,
                "font_size": config.get("font_size", 12),
                "hand_preference": config.get("hand_preference", "right"),
                "selected_language": config.get("selected_language", "ASL"),
            }
        except Exception as e:
            self.logger.warning(f"Could not get all settings: {e}")
            return {
                "user_mode": get_text("modes.sign_translate.name"),
                "theme": "Light",
                "font_size": 12,
                "hand_preference": "right",
                "selected_language": "ASL",
            }

    def save_all_settings(self, settings: Dict[str, Any]) -> bool:
        """Save all user settings with validation"""
        try:
            # Check if we're already in a save operation to prevent infinite loops
            if hasattr(self, "_saving_settings") and self._saving_settings:
                self.logger.warning("Already saving settings, skipping recursive call")
                return True

            # Validate settings before saving
            if not self._validate_settings(settings):
                self.logger.error("Settings validation failed")
                return False

            self._saving_settings = True

            # Load existing config only if we need to merge with existing settings
            existing_config = self.load_config() or {}

            # Track changes for timestamps
            current_timestamp = self.get_timestamp()

            # Update with new settings and add timestamps for changed values
            for key, value in settings.items():
                if existing_config.get(key) != value:
                    existing_config[key] = value
                    # Add specific timestamp for this setting
                    existing_config[f"{key}_last_changed"] = current_timestamp

            # Always update the general last_updated timestamp
            existing_config["last_updated"] = current_timestamp

            # Save the updated config
            result = self.save_config(existing_config)

            # Clear the flag
            self._saving_settings = False

            return result
        except Exception as e:
            self.logger.error(f"Could not save all settings: {e}")
            # Clear the flag on error
            if hasattr(self, "_saving_settings"):
                self._saving_settings = False
            return False

    def _validate_settings(self, settings: Dict[str, Any]) -> bool:
        """Validate all settings before saving"""
        try:
            # Validate theme if present
            if "theme" in settings:
                if not self._validate_theme(settings["theme"]):
                    return False

            # Validate font size if present
            if "font_size" in settings:
                font_size = settings["font_size"]
                if not isinstance(font_size, int) or font_size < 8 or font_size > 72:
                    self.logger.warning(
                        f"Invalid font size: {font_size}. Must be between 8 and 72"
                    )
                    return False

            # Validate user mode if present
            if "user_mode" in settings:
                valid_modes = ["Sign & Translate", "Learn Sign Language"]
                if settings["user_mode"] not in valid_modes:
                    self.logger.warning(
                        f"Invalid user mode: {settings['user_mode']}. Valid modes: {valid_modes}"
                    )
                    return False

            # Validate hand preference if present
            if "hand_preference" in settings:
                valid_hands = ["left", "right"]
                if settings["hand_preference"] not in valid_hands:
                    self.logger.warning(
                        f"Invalid hand preference: {settings['hand_preference']}. Valid options: {valid_hands}"
                    )
                    return False

            return True
        except Exception as e:
            self.logger.error(f"Error validating settings: {e}")
            return False

    def get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()

    def get_settings_with_timestamps(self) -> Dict[str, Any]:
        """Get all settings with their last changed timestamps"""
        try:
            config = self.load_config() or {}
            settings = self.get_all_settings()

            # Add timestamp information
            settings["last_updated"] = config.get("last_updated", "Never")
            settings["theme_last_changed"] = config.get("theme_last_changed", "Never")
            settings["font_size_last_changed"] = config.get(
                "font_size_last_changed", "Never"
            )
            settings["user_mode_last_changed"] = config.get(
                "user_mode_last_changed", "Never"
            )
            settings["hand_preference_last_changed"] = config.get(
                "hand_preference_last_changed", "Never"
            )

            return settings
        except Exception as e:
            self.logger.error(f"Could not get settings with timestamps: {e}")
            return {}


def show_startup_screen(parent=None) -> Optional[str]:
    """Show startup screen and return user choice"""
    try:
        if not PYSIDE6_AVAILABLE:
            logger = get_logger("helpmesign.startup")
            logger.error("PySide6 is not available, cannot show startup screen")
            return None

        dialog = StartupScreen(parent)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            # Get the choice from the signal
            return dialog.property("user_choice")
        return None

    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error showing startup screen: {e}")
        return None


def get_user_mode() -> Optional[str]:
    """Get user's preferred mode"""
    try:
        config_manager = SecureConfigManager()
        return config_manager.get_user_mode()
    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error getting user mode: {e}")
        return None


def set_user_mode(mode: str) -> bool:
    """Set user's preferred mode"""
    try:
        config_manager = SecureConfigManager()
        return config_manager.set_user_mode(mode)
    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error setting user mode: {e}")
        return False


def get_theme() -> str:
    """Get user's preferred theme"""
    try:
        config_manager = SecureConfigManager()
        return config_manager.get_theme()
    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error getting theme: {e}")
        return "Light"


def set_theme(theme: str) -> bool:
    """Set user's preferred theme"""
    try:
        config_manager = SecureConfigManager()
        return config_manager.set_theme(theme)
    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error setting theme: {e}")
        return False


def get_font_size() -> int:
    """Get user's preferred font size"""
    try:
        config_manager = SecureConfigManager()
        return config_manager.get_font_size()
    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error getting font size: {e}")
        return 12


def set_font_size(font_size: int) -> bool:
    """Set user's preferred font size"""
    try:
        config_manager = SecureConfigManager()
        return config_manager.set_font_size(font_size)
    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error setting font size: {e}")
        return False


def get_hand_preference() -> str:
    """Get user's preferred hand"""
    try:
        config_manager = SecureConfigManager()
        return config_manager.get_hand_preference()
    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error getting hand preference: {e}")
        return "right"


def set_hand_preference(hand_preference: str) -> bool:
    """Set user's preferred hand"""
    try:
        config_manager = SecureConfigManager()
        return config_manager.set_hand_preference(hand_preference)
    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error setting hand preference: {e}")
        return False


def get_all_settings() -> Dict[str, Any]:
    """Get all user settings"""
    try:
        config_manager = SecureConfigManager()
        return config_manager.get_all_settings()
    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error getting all settings: {e}")
        return {
            "user_mode": get_text("modes.sign_translate.name"),
            "theme": "Light",
            "font_size": 12,
            "hand_preference": "right",
        }


def save_all_settings(settings: Dict[str, Any]) -> bool:
    """Save all user settings"""
    try:
        config_manager = SecureConfigManager()
        return config_manager.save_all_settings(settings)
    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error saving all settings: {e}")
        return False


def get_settings_with_timestamps() -> Dict[str, Any]:
    """Get all user settings with their last changed timestamps"""
    try:
        config_manager = SecureConfigManager()
        return config_manager.get_settings_with_timestamps()
    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error getting settings with timestamps: {e}")
        return {}
