"""
Startup screen module for HelpMeSign
Handles user choice between sign and learn modes
"""

import getpass
import hashlib
import hmac
import json
import os
import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

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

from ..utils.font_manager import get_button_font, get_heading_font, get_title_font
from ..utils.language_manager import get_dict, get_list, get_text
from ..utils.logger import get_logger


class StartupScreen(QDialog):
    """Startup screen with user choice functionality"""

    # Signal emitted when user makes a choice
    choice_made = Signal(str)

    def __init__(self, parent=None):
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

    def __init__(self, environment: str = "dev"):
        self.config_dir = Path.home() / ".helpmesign"
        self.config_file = self.config_dir / "user_config.secure"
        self.environment = environment.lower()
        self.logger = get_logger("helpmesign.config")

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
            self.environment,  # Environment (dev/prod)
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
            import uuid

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
            # Add metadata
            config["timestamp"] = self.get_timestamp()
            config["environment"] = self.environment
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

    def load_config(self) -> Optional[Dict[str, Any]]:
        """Load configuration with HMAC verification"""
        try:
            if not self.config_file.exists():
                self.logger.debug("Configuration file does not exist")
                return None

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

            # Verify environment compatibility
            if config.get("environment") != self.environment:
                self.logger.warning(
                    f"Environment mismatch: expected {self.environment}, got {config.get('environment')}"
                )
                # Still return config but log warning

            self.logger.info("Configuration loaded and verified successfully")
            return config

        except FileNotFoundError:
            self.logger.debug("Configuration file not found")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in configuration file: {e}")
            return None
        except ValueError as e:
            self.logger.error(f"Configuration verification failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            return None

    def get_user_mode(self) -> Optional[str]:
        """Get user's preferred mode"""
        try:
            config = self.load_config()
            if config:
                return config.get("user_mode")
            return None
        except Exception as e:
            self.logger.warning(f"Could not get user mode: {e}")
            return None

    def set_user_mode(self, mode: str) -> bool:
        """Set user's preferred mode"""
        try:
            config = self.load_config() or {}
            config["user_mode"] = mode
            return self.save_config(config)
        except Exception as e:
            self.logger.error(f"Could not set user mode: {e}")
            return False

    def get_theme(self) -> str:
        """Get user's preferred theme"""
        try:
            config = self.load_config()
            if config:
                return config.get("theme", "Light")
            return "Light"
        except Exception as e:
            self.logger.warning(f"Could not get theme: {e}")
            return "Light"

    def set_theme(self, theme: str) -> bool:
        """Set user's preferred theme"""
        try:
            config = self.load_config() or {}
            config["theme"] = theme
            return self.save_config(config)
        except Exception as e:
            self.logger.error(f"Could not set theme: {e}")
            return False

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
            config = self.load_config() or {}
            config["font_size"] = font_size
            return self.save_config(config)
        except Exception as e:
            self.logger.error(f"Could not set font size: {e}")
            return False

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all user settings"""
        try:
            config = self.load_config() or {}
            return {
                "user_mode": config.get(
                    "user_mode", get_text("modes.sign_translate.name")
                ),
                "theme": config.get("theme", "Light"),
                "font_size": config.get("font_size", 12),
            }
        except Exception as e:
            self.logger.warning(f"Could not get all settings: {e}")
            return {
                "user_mode": get_text("modes.sign_translate.name"),
                "theme": "Light",
                "font_size": 12,
            }

    def save_all_settings(self, settings: Dict[str, Any]) -> bool:
        """Save all user settings"""
        try:
            config = self.load_config() or {}
            config.update(settings)
            return self.save_config(config)
        except Exception as e:
            self.logger.error(f"Could not save all settings: {e}")
            return False

    def get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()


def show_startup_screen(parent=None) -> Optional[str]:
    """Show startup screen and return user choice"""
    try:
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


def get_user_mode(environment: str = "dev") -> Optional[str]:
    """Get user's preferred mode"""
    try:
        config_manager = SecureConfigManager(environment)
        return config_manager.get_user_mode()
    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error getting user mode: {e}")
        return None


def set_user_mode(mode: str, environment: str = "dev") -> bool:
    """Set user's preferred mode"""
    try:
        config_manager = SecureConfigManager(environment)
        return config_manager.set_user_mode(mode)
    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error setting user mode: {e}")
        return False


def get_theme(environment: str = "dev") -> str:
    """Get user's preferred theme"""
    try:
        config_manager = SecureConfigManager(environment)
        return config_manager.get_theme()
    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error getting theme: {e}")
        return "Light"


def set_theme(theme: str, environment: str = "dev") -> bool:
    """Set user's preferred theme"""
    try:
        config_manager = SecureConfigManager(environment)
        return config_manager.set_theme(theme)
    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error setting theme: {e}")
        return False


def get_font_size(environment: str = "dev") -> int:
    """Get user's preferred font size"""
    try:
        config_manager = SecureConfigManager(environment)
        return config_manager.get_font_size()
    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error getting font size: {e}")
        return 12


def set_font_size(font_size: int, environment: str = "dev") -> bool:
    """Set user's preferred font size"""
    try:
        config_manager = SecureConfigManager(environment)
        return config_manager.set_font_size(font_size)
    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error setting font size: {e}")
        return False


def get_all_settings(environment: str = "dev") -> Dict[str, Any]:
    """Get all user settings"""
    try:
        config_manager = SecureConfigManager(environment)
        return config_manager.get_all_settings()
    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error getting all settings: {e}")
        return {
            "user_mode": get_text("modes.sign_translate.name"),
            "theme": "Light",
            "font_size": 12,
        }


def save_all_settings(settings: Dict[str, Any], environment: str = "dev") -> bool:
    """Save all user settings"""
    try:
        config_manager = SecureConfigManager(environment)
        return config_manager.save_all_settings(settings)
    except Exception as e:
        logger = get_logger("helpmesign.startup")
        logger.error(f"Error saving all settings: {e}")
        return False
