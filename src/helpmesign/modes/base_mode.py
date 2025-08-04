"""
Base mode class for HelpMeSign application modes
Provides common functionality and interface for all modes
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


class BaseMode(ABC):
    """Abstract base class for all application modes"""

    def __init__(self, main_window, environment: str = "dev"):
        """
        Initialize the mode
        
        Args:
            main_window: Reference to the main application window
            environment: Application environment (dev, prod, etc.)
        """
        self.main_window = main_window
        self.environment = environment
        self.mode_name = self.get_mode_name()
        self.setup_ui()
        self.setup_behavior()

    @abstractmethod
    def get_mode_name(self) -> str:
        """Get the display name for this mode"""
        pass

    @abstractmethod
    def setup_ui(self) -> None:
        """Set up the mode-specific UI components"""
        pass

    @abstractmethod
    def setup_behavior(self) -> None:
        """Set up mode-specific behavior and event handlers"""
        pass

    @abstractmethod
    def process_text(self, text: str) -> str:
        """Process input text according to mode-specific logic"""
        pass

    @abstractmethod
    def get_mode_description(self) -> str:
        """Get a description of what this mode does"""
        pass

    def activate(self) -> None:
        """Activate this mode - called when switching to this mode"""
        self.update_ui()
        self.main_window.set_mode(self.mode_name)
        self.main_window.set_status("Ready")

    def deactivate(self) -> None:
        """Deactivate this mode - called when switching away from this mode"""
        pass

    def update_ui(self) -> None:
        """Update the UI to reflect the current mode"""
        pass

    def get_settings(self) -> Dict[str, Any]:
        """Get mode-specific settings"""
        return {}

    def apply_settings(self, settings: Dict[str, Any]) -> None:
        """Apply mode-specific settings"""
        pass

    def clear_content(self) -> None:
        """Clear all content in this mode"""
        pass 