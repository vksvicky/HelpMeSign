"""
Mode manager for HelpMeSign application
Handles switching between different application modes
"""

from typing import Dict, Optional

from ..utils.language_manager import get_text
from .base_mode import BaseMode
from .learn.learn_mode import LearnMode
from .sign_translate.sign_translate_mode import SignTranslateMode


class ModeManager:
    """Manages different application modes and handles mode switching"""

    def __init__(self, main_window, environment: str = "dev"):
        """
        Initialize the mode manager

        Args:
            main_window: Reference to the main application window
            environment: Application environment (dev, prod, etc.)
        """
        self.main_window = main_window
        self.environment = environment
        self.modes: Dict[str, BaseMode] = {}
        self.current_mode: Optional[BaseMode] = None

        self._initialize_modes()

    def _initialize_modes(self) -> None:
        """Initialize all available modes"""
        # Create mode instances
        self.modes["sign_translate"] = SignTranslateMode(
            self.main_window, self.environment
        )
        self.modes["learn"] = LearnMode(self.main_window, self.environment)

        # Set default mode
        self.current_mode = self.modes["sign_translate"]

    def get_available_modes(self) -> Dict[str, BaseMode]:
        """Get all available modes"""
        return self.modes.copy()

    def get_current_mode(self) -> Optional[BaseMode]:
        """Get the currently active mode"""
        return self.current_mode

    def get_current_mode_name(self) -> str:
        """Get the name of the currently active mode"""
        if self.current_mode:
            return self.current_mode.get_mode_name()
        return "Unknown"

    def switch_mode(self, mode_name: str) -> bool:
        """
        Switch to a different mode

        Args:
            mode_name: Name of the mode to switch to

        Returns:
            True if mode switch was successful, False otherwise
        """
        try:
            # Validate mode name
            if mode_name not in self.modes:
                return False

            # Deactivate current mode
            if self.current_mode:
                self.current_mode.deactivate()

            # Switch to new mode
            self.current_mode = self.modes[mode_name]
            self.current_mode.activate()

            return True

        except Exception as e:
            # Log error and return False
            print(f"Error switching to mode {mode_name}: {e}")
            return False

    def switch_mode_by_display_name(self, display_name: str) -> bool:
        """
        Switch to a mode by its display name

        Args:
            display_name: Display name of the mode (e.g., "Sign & Translate")

        Returns:
            True if mode switch was successful, False otherwise
        """
        for mode_name, mode in self.modes.items():
            if mode.get_mode_name() == display_name:
                return self.switch_mode(mode_name)
        return False

    def process_text(self, text: str) -> str:
        """
        Process text using the current mode

        Args:
            text: Input text to process

        Returns:
            Processed output from the current mode
        """
        if self.current_mode:
            return self.current_mode.process_text(text)
        return "No active mode"

    def clear_content(self) -> None:
        """Clear content in the current mode"""
        if self.current_mode:
            self.current_mode.clear_content()

    def get_mode_settings(self) -> Dict:
        """Get settings from the current mode"""
        if self.current_mode:
            return self.current_mode.get_settings()
        return {}

    def apply_mode_settings(self, settings: Dict) -> None:
        """Apply settings to the current mode"""
        if self.current_mode:
            self.current_mode.apply_settings(settings)

    def get_mode_descriptions(self) -> Dict[str, str]:
        """Get descriptions for all available modes"""
        descriptions = {}
        for mode_name, mode in self.modes.items():
            descriptions[mode_name] = mode.get_mode_description()
        return descriptions
