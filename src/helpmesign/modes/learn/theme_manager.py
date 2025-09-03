"""
Theme and font management for LearnMode
"""

import logging
from typing import Optional

from ...utils.theme_manager import get_font_family, get_theme_manager


class LearnModeThemeManager:
    """Manages theme and font initialization for LearnMode"""

    def __init__(self, learn_mode):
        self.learn_mode = learn_mode
        self.logger = logging.getLogger(__name__)

    def initialize_theme_and_font_info(self, main_window) -> None:
        """Initialize theme and font information from main window or config"""
        try:
            # Try to get theme and font info from main window first
            if hasattr(main_window, "theme") and hasattr(main_window, "font_size"):
                self.learn_mode.current_theme = main_window.theme
                self.learn_mode.current_font_size = main_window.font_size
                self.logger.debug(
                    f"Using theme and font from main window: {self.learn_mode.current_theme}, {self.learn_mode.current_font_size}"
                )
            else:
                # Fallback to config
                from src.helpmesign.core.startup import get_all_settings

                settings = get_all_settings()
                self.learn_mode.current_theme = settings.get("theme", "Light")
                self.learn_mode.current_font_size = settings.get("font_size", 16)
                self.logger.debug(
                    f"Using theme and font from config: {self.learn_mode.current_theme}, {self.learn_mode.current_font_size}"
                )

            # Get effective theme (handle System theme)
            self.learn_mode.effective_theme = self._get_effective_theme_from_theme(
                self.learn_mode.current_theme
            )

            # Get font family from theme manager
            self.learn_mode.current_font_family = get_font_family()

        except Exception as e:
            self.logger.error(f"Error initializing theme and font info: {e}")
            # Fallback to defaults
            self.learn_mode.current_theme = "Light"
            self.learn_mode.effective_theme = "Light"
            self.learn_mode.current_font_size = 16
            self.learn_mode.current_font_family = "Roboto"

    def _get_effective_theme_from_theme(self, theme: str) -> str:
        """Get effective theme (Dark/Light) from theme name"""
        if theme == "System":
            # Detect system theme
            try:
                theme_manager = get_theme_manager()
                current_theme = theme_manager.get_current_theme()

                if current_theme.startswith("System ("):
                    if "Dark" in current_theme:
                        return "Dark"
                    else:
                        return "Light"
                else:
                    return "Light"  # Fallback
            except Exception:
                return "Light"  # Fallback
        elif theme == "Dark":
            return "Dark"
        else:
            return "Light"
