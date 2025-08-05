"""
Font Manager for HelpMeSign Application
Handles loading and managing Roboto fonts across the application
"""

import os
import platform
from typing import Any, Dict, Optional

from PySide6.QtGui import QFont, QFontDatabase

from .logger import get_logger


class FontManager:
    """Manages application fonts"""

    def __init__(self):
        self.fonts_loaded = False
        self.font_families = {}
        self._fonts_initialized = False
        self.logger = get_logger("helpmesign.fonts")
        # Don't load fonts immediately to avoid Qt initialization issues

    def _ensure_fonts_loaded(self) -> None:
        """Ensure fonts are loaded (called lazily)"""
        if self._fonts_initialized:
            return

        try:
            # Get the path to the fonts directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(current_dir))
            )
            fonts_dir = os.path.join(project_root, "resources", "fonts")

            # Roboto font files - all contain "Roboto" as the family name
            font_files = [
                "Roboto-Regular.ttf",
                "Roboto-Bold.ttf",
                "Roboto-Light.ttf",
                "Roboto-Medium.ttf",
                "Roboto-Thin.ttf",
            ]

            # Try to load fonts if they exist
            for filename in font_files:
                font_path = os.path.join(fonts_dir, filename)
                if os.path.exists(font_path) and os.path.getsize(font_path) > 0:
                    try:
                        # Load the font using Qt
                        font_id = QFontDatabase.addApplicationFont(font_path)
                        if font_id != -1:
                            # Get the actual font family name from Qt
                            families = QFontDatabase.applicationFontFamilies(font_id)
                            if families:
                                self.font_families[filename] = families[
                                    0
                                ]  # Use first family name
                    except Exception as e:
                        self.logger.warning(f"Could not load font {filename}: {e}")

            if self.font_families:
                self.fonts_loaded = True
                self.logger.info(f"Loaded {len(self.font_families)} Roboto fonts")
                self.logger.debug(
                    f"Available font families: {list(self.font_families.values())}"
                )
            else:
                self.logger.warning("No Roboto fonts found, using system fonts")

        except Exception as e:
            self.logger.error(f"Error loading fonts: {e}")

        self._fonts_initialized = True

    def get_font(
        self,
        family: Optional[str] = None,
        size: int = 10,
        weight: int = QFont.Normal,  # type: ignore
        italic: bool = False,
    ) -> QFont:
        """Get a QFont object for Qt widgets"""
        self._ensure_fonts_loaded()

        # Use current font family if none specified
        if family is None:
            family = self._get_current_font_family()

        if not self.fonts_loaded:
            # Fallback to system fonts
            if family == "Roboto":
                family = "Arial" if platform.system() == "Windows" else "Helvetica"

        font = QFont(family, size)
        font.setWeight(weight)  # type: ignore
        font.setItalic(italic)
        return font

    def get_title_font(self) -> QFont:
        """Get font for titles"""
        # Use current font size from theme manager with title adjustment
        current_size = self._get_current_font_size()
        title_size = min(24, current_size + 4)  # Title is larger than base
        return self.get_font("Roboto", title_size, QFont.Bold)  # type: ignore

    def get_heading_font(self) -> QFont:
        """Get font for headings"""
        # Use current font size from theme manager with heading adjustment
        current_size = self._get_current_font_size()
        heading_size = min(20, current_size + 2)  # Heading is larger than base
        return self.get_font("Roboto", heading_size, QFont.Bold)  # type: ignore

    def get_subheading_font(self) -> QFont:
        """Get font for subheadings"""
        # Use current font size from theme manager with subheading adjustment
        current_size = self._get_current_font_size()
        subheading_size = min(
            18, current_size + 1
        )  # Subheading is slightly larger than base
        return self.get_font("Roboto", subheading_size, QFont.Bold)  # type: ignore

    def get_body_font(self) -> QFont:
        """Get font for body text"""
        # Use current font size from theme manager
        current_size = self._get_current_font_size()
        return self.get_font("Roboto", current_size, QFont.Normal)  # type: ignore

    def get_small_font(self) -> QFont:
        """Get font for small text"""
        # Use current font size from theme manager with small adjustment
        current_size = self._get_current_font_size()
        small_size = max(8, current_size - 2)  # Small is smaller than base
        return self.get_font("Roboto", small_size, QFont.Normal)  # type: ignore

    def get_button_font(self) -> QFont:
        """Get font for buttons"""
        # Use current font size from theme manager
        current_size = self._get_current_font_size()
        return self.get_font("Roboto", current_size, QFont.Bold)  # type: ignore

    def get_label_font(self) -> QFont:
        """Get font for labels"""
        # Use current font size from theme manager
        current_size = self._get_current_font_size()
        return self.get_font("Roboto", current_size, QFont.Normal)  # type: ignore

    def get_input_font(self) -> QFont:
        """Get font for input fields"""
        # Use current font size from theme manager
        current_size = self._get_current_font_size()
        return self.get_font("Roboto", current_size, QFont.Normal)  # type: ignore

    def get_menu_font(self) -> QFont:
        """Get font for menu items"""
        # Use current font size from theme manager
        current_size = self._get_current_font_size()
        return self.get_font("Roboto", current_size, QFont.Normal)  # type: ignore

    def _get_current_font_size(self) -> int:
        """Get the current font size from the theme manager"""
        try:
            from .theme_manager import get_font_size

            return get_font_size()
        except Exception:
            # Fallback to default size if theme manager is not available
            return 12

    def _get_current_font_family(self) -> str:
        """Get the current font family from the theme manager"""
        try:
            from .theme_manager import get_font_family

            return get_font_family()
        except Exception:
            # Fallback to default family if theme manager is not available
            return "Roboto"


# Global font manager instance
_font_manager = None


def get_font_manager() -> FontManager:
    """Get the global font manager instance"""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
    return _font_manager


def get_font(
    family: str = "Roboto",
    size: int = 10,
    weight: int = QFont.Normal,  # type: ignore
    italic: bool = False,
) -> QFont:
    """Get a QFont object for Qt widgets"""
    return get_font_manager().get_font(family, size, weight, italic)


def get_title_font() -> QFont:
    """Get font for titles"""
    return get_font_manager().get_title_font()


def get_heading_font() -> QFont:
    """Get font for headings"""
    return get_font_manager().get_heading_font()


def get_subheading_font() -> QFont:
    """Get font for subheadings"""
    return get_font_manager().get_subheading_font()


def get_body_font() -> QFont:
    """Get font for body text"""
    return get_font_manager().get_body_font()


def get_small_font() -> QFont:
    """Get font for small text"""
    return get_font_manager().get_small_font()


def get_button_font() -> QFont:
    """Get font for buttons"""
    return get_font_manager().get_button_font()


def get_label_font() -> QFont:
    """Get font for labels"""
    return get_font_manager().get_label_font()


def get_input_font() -> QFont:
    """Get font for input fields"""
    return get_font_manager().get_input_font()


def get_menu_font() -> QFont:
    """Get font for menu items"""
    return get_font_manager().get_menu_font()
