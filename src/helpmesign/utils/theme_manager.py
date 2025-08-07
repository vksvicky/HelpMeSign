#!/usr/bin/env python3
"""
Theme manager for HelpMeSign application
Handles theme application and UI styling
"""

from typing import Any, Dict, Optional

try:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QPalette
    from PySide6.QtWidgets import QApplication, QWidget

    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

    # Create mock classes for when PySide6 is not available
    class Qt:  # type: ignore
        pass

    class QColor:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

    class QPalette:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

    class QApplication:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

    class QWidget:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass


from .logger import get_logger


class ThemeManager:
    """Manages application themes and styling"""

    def __init__(self):
        self.logger = get_logger("helpmesign.theme")
        self.current_theme = "Light"
        self.current_font_size = 12  # Default font size
        self.current_font_family = "Roboto"  # Default font family
        self.themes = {
            "Light": self._get_light_theme(),
            "Dark": self._get_dark_theme(),
            "System": self._get_system_theme(),
        }

    def set_font_size(self, font_size: int) -> None:
        """Set the current font size"""
        self.current_font_size = font_size
        self.logger.info(f"Font size set to: {font_size}px")

    def get_font_size(self) -> int:
        """Get the current font size"""
        return self.current_font_size

    def set_font_family(self, font_family: str) -> None:
        """Set the current font family"""
        self.current_font_family = font_family
        self.logger.info(f"Font family set to: {font_family}")

    def get_font_family(self) -> str:
        """Get the current font family"""
        return self.current_font_family

    def get_font_size_style(self, component: str = "general") -> str:
        """Get font size style for a specific component"""
        font_size = self.current_font_size

        # Component-specific font size adjustments
        size_adjustments = {
            "general": font_size,
            "small": max(8, font_size - 2),
            "large": min(24, font_size + 2),
            "title": min(24, font_size + 4),
            "button": font_size,
            "input": font_size,
            "label": font_size,
        }

        adjusted_size = size_adjustments.get(component, font_size)

        return f"font-size: {adjusted_size}px;"

    def get_complete_style(self, component: str, include_font_size: bool = True) -> str:
        """Get complete style including theme and font size"""
        theme_style = self.get_theme_style(component)

        if include_font_size:
            font_style = self.get_font_size_style(component)

            # Replace existing font-size declarations or add new ones
            import re

            # Pattern to match font-size declarations
            font_size_pattern = r"font-size:\s*\d+px;"

            if re.search(font_size_pattern, theme_style):
                # Replace existing font-size declarations
                theme_style = re.sub(font_size_pattern, font_style.strip(), theme_style)
            else:
                # Add font-size to the style if none exists
                if "{" in theme_style and "}" in theme_style:
                    # Insert font-size before the closing brace
                    insert_pos = theme_style.rfind("}")
                    if insert_pos != -1:
                        theme_style = (
                            theme_style[:insert_pos]
                            + f"    {font_style}\n"
                            + theme_style[insert_pos:]
                        )

        return theme_style

    def force_font_size_update(self, widget, component: str = "general") -> None:
        """Force update a widget's font size"""
        if not PYSIDE6_AVAILABLE:
            self.logger.debug("PySide6 not available, skipping font size update")
            return

        try:
            if widget is None:
                return

            # Check if widget is still valid
            if not hasattr(widget, "setStyleSheet"):
                return

            # Check if widget is being destroyed
            if hasattr(widget, "isDestroyed") and widget.isDestroyed():
                return

            # Check if widget is visible and not being destroyed
            if hasattr(widget, "isVisible") and not widget.isVisible():
                return

            # Get the complete style with font size
            complete_style = self.get_complete_style(component, include_font_size=True)

            # Apply the style
            widget.setStyleSheet(complete_style)

        except Exception as e:
            self.logger.warning(f"Error forcing font size update: {e}")

    def apply_font_size_to_widget_tree(
        self, root_widget, component_map: Optional[Dict[str, str]] = None
    ) -> None:
        """Apply font size to an entire widget tree"""
        if not PYSIDE6_AVAILABLE:
            self.logger.debug(
                "PySide6 not available, skipping widget tree font size application"
            )
            return

        try:
            if root_widget is None:
                self.logger.warning(
                    "Root widget is None, skipping font size application"
                )
                return

            # Additional safety check for widget validity
            if not hasattr(root_widget, "setStyleSheet"):
                self.logger.warning(
                    "Root widget is not a valid Qt widget, skipping font size application"
                )
                return

            # Check if widget is being destroyed
            if hasattr(root_widget, "isDestroyed") and root_widget.isDestroyed():
                self.logger.warning(
                    "Root widget is being destroyed, skipping font size application"
                )
                return

            if component_map is None:
                component_map = {
                    "QMainWindow": "main_window",
                    "QDialog": "dialog",
                    "QPushButton": "button_primary",
                    "QLineEdit": "input_field",
                    "QTextEdit": "input_field",
                    "QGroupBox": "group_box",
                    "QTabWidget": "tab_widget",
                    "QLabel": "label",
                    "QSlider": "general",
                    "QTabBar": "tab_widget",
                }

            # Apply to root widget
            root_type = root_widget.__class__.__name__
            component = component_map.get(root_type, "general")
            self.force_font_size_update(root_widget, component)

            # Apply to all child widgets (find all types, not just same type as root)
            from PySide6.QtWidgets import QWidget

            # Get all child widgets recursively with safety check
            try:
                all_children = root_widget.findChildren(QWidget)

                # Limit the number of children to prevent infinite loops
                max_children = 1000
                if len(all_children) > max_children:
                    self.logger.warning(
                        f"Too many child widgets ({len(all_children)}), limiting to {max_children}"
                    )
                    all_children = all_children[:max_children]

                # Apply font size to each child widget
                for i, child in enumerate(all_children):
                    try:
                        # Check if child is being destroyed
                        if hasattr(child, "isDestroyed") and child.isDestroyed():
                            continue

                        if child is None or not child.isVisible():
                            continue

                        # Additional safety check for child widget validity
                        if not hasattr(child, "setStyleSheet"):
                            continue

                        child_type = child.__class__.__name__
                        child_component = component_map.get(child_type, "general")
                        self.force_font_size_update(child, child_component)

                        # Add a small delay every 100 widgets to prevent UI freezing
                        if i % 100 == 0 and i > 0:
                            from PySide6.QtCore import QCoreApplication

                            QCoreApplication.processEvents()

                    except Exception as child_error:
                        self.logger.warning(
                            f"Error applying font size to child widget {i}: {child_error}"
                        )
                        continue

            except Exception as children_error:
                self.logger.error(f"Error finding child widgets: {children_error}")

        except Exception as e:
            self.logger.error(f"Error applying font size to widget tree: {e}")

    def _get_light_theme(self) -> Dict[str, Any]:
        """Get light theme colors and styles"""
        return {
            "name": "Light",
            "colors": {
                "primary": "#3b82f6",
                "primary_hover": "#2563eb",
                "primary_pressed": "#1d4ed8",
                "background": "#ffffff",
                "background_secondary": "#f8fafc",
                "background_tertiary": "#f1f5f9",
                "text_primary": "#1e293b",
                "text_secondary": "#64748b",
                "text_muted": "#94a3b8",
                "border": "#e2e8f0",
                "border_secondary": "#d1d5db",
                "success": "#10b981",
                "warning": "#f59e0b",
                "error": "#ef4444",
            },
            "styles": {
                "main_window": """
                    QMainWindow {
                        background-color: #ffffff;
                        color: #1e293b;
                        font-size: 12px;
                    }
                """,
                "dialog": """
                    QDialog {
                        background-color: #ffffff;
                        border: 1px solid #e2e8f0;
                        border-radius: 16px;
                        color: #1e293b;
                        font-size: 12px;
                    }
                    QDialog QLabel {
                        color: #1e293b;
                        font-size: 12px;
                    }
                """,
                "button_primary": """
                    QPushButton {
                        background-color: #3b82f6;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-weight: 500;
                        padding: 10px 20px;
                        font-size: 12px;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #2563eb;
                    }
                    QPushButton:pressed {
                        background-color: #1d4ed8;
                    }
                    QPushButton:disabled {
                        background-color: #94a3b8;
                        color: #cbd5e1;
                    }
                """,
                "button_secondary": """
                    QPushButton {
                        background-color: #f1f5f9;
                        color: #64748b;
                        border: 1px solid #d1d5db;
                        border-radius: 8px;
                        font-weight: 500;
                        padding: 10px 20px;
                        font-size: 12px;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #e2e8f0;
                        color: #475569;
                    }
                    QPushButton:pressed {
                        background-color: #cbd5e1;
                    }
                    QPushButton:disabled {
                        background-color: #f8fafc;
                        color: #cbd5e1;
                        border-color: #e2e8f0;
                    }
                """,
                "input_field": """
                    QLineEdit, QTextEdit {
                        background-color: #ffffff;
                        color: #1e293b;
                        border: 1px solid #d1d5db;
                        border-radius: 8px;
                        padding: 8px 12px;
                        font-size: 12px;
                    }
                    QLineEdit:focus, QTextEdit:focus {
                        border-color: #3b82f6;
                        outline: none;
                    }
                """,
                "group_box": """
                    QGroupBox {
                        font-weight: 600;
                        color: #1e293b;
                        border: 1px solid #e2e8f0;
                        border-radius: 12px;
                        margin-top: 12px;
                        padding-top: 16px;
                        background-color: #ffffff;
                        font-size: 12px;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        left: 16px;
                        padding: 0 8px 0 8px;
                        background-color: #ffffff;
                        color: #1e293b;
                        font-size: 12px;
                        font-weight: 600;
                    }
                """,
                "tab_widget": """
                    QTabWidget::pane {
                        border: none;
                        background-color: #ffffff;
                    }
                    QTabBar::tab {
                        background-color: #f1f5f9;
                        color: #64748b;
                        padding: 12px 24px;
                        margin-right: 4px;
                        border-top-left-radius: 8px;
                        border-top-right-radius: 8px;
                        font-weight: 500;
                        font-size: 12px;
                        border: none;
                    }
                    QTabBar::tab:selected {
                        background-color: #ffffff;
                        color: #1e293b;
                        border-bottom: 2px solid #3b82f6;
                    }
                    QTabBar::tab:hover:!selected {
                        background-color: #e2e8f0;
                        color: #475569;
                    }
                """,
            },
        }

    def _get_dark_theme(self) -> Dict[str, Any]:
        """Get dark theme colors and styles"""
        return {
            "name": "Dark",
            "colors": {
                "primary": "#0a84ff",  # macOS blue
                "primary_hover": "#409cff",
                "primary_pressed": "#0056d6",
                "background": "#1c1c1e",  # macOS dark background
                "background_secondary": "#2c2c2e",  # macOS dark secondary
                "background_tertiary": "#3a3a3c",  # macOS dark tertiary
                "text_primary": "#ffffff",  # White text
                "text_secondary": "#ebebf5",  # Light gray text
                "text_muted": "#8e8e93",  # Muted gray text
                "border": "#38383a",  # Dark border
                "border_secondary": "#48484a",  # Secondary border
                "success": "#30d158",  # macOS green
                "warning": "#ff9f0a",  # macOS orange
                "error": "#ff453a",  # macOS red
            },
            "styles": {
                "main_window": """
                    QMainWindow {
                        background-color: #1c1c1e;
                        color: #ffffff;
                        font-size: 12px;
                    }
                """,
                "dialog": """
                    QDialog {
                        background-color: #1c1c1e;
                        border: 1px solid #38383a;
                        border-radius: 16px;
                        color: #ffffff;
                        font-size: 12px;
                    }
                    QDialog QLabel {
                        color: #ffffff;
                        font-size: 12px;
                    }
                """,
                "button_primary": """
                    QPushButton {
                        background-color: #0a84ff;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-weight: 500;
                        padding: 10px 20px;
                        font-size: 12px;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #409cff;
                    }
                    QPushButton:pressed {
                        background-color: #0056d6;
                    }
                    QPushButton:disabled {
                        background-color: #8e8e93;
                        color: #ebebf5;
                    }
                """,
                "button_secondary": """
                    QPushButton {
                        background-color: #2c2c2e;
                        color: #ebebf5;
                        border: 1px solid #48484a;
                        border-radius: 8px;
                        font-weight: 500;
                        padding: 10px 20px;
                        font-size: 12px;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #3a3a3c;
                        color: #ffffff;
                    }
                    QPushButton:pressed {
                        background-color: #48484a;
                    }
                    QPushButton:disabled {
                        background-color: #1c1c1e;
                        color: #8e8e93;
                        border-color: #38383a;
                    }
                """,
                "input_field": """
                    QLineEdit, QTextEdit {
                        background-color: #2c2c2e;
                        color: #ffffff;
                        border: 1px solid #48484a;
                        border-radius: 8px;
                        padding: 8px 12px;
                        font-size: 12px;
                    }
                    QLineEdit:focus, QTextEdit:focus {
                        border-color: #0a84ff;
                        outline: none;
                    }
                """,
                "group_box": """
                    QGroupBox {
                        font-weight: 600;
                        color: #ffffff;
                        border: 1px solid #38383a;
                        border-radius: 12px;
                        margin-top: 12px;
                        padding-top: 16px;
                        background-color: #1c1c1e;
                        font-size: 12px;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        left: 16px;
                        padding: 0 8px 0 8px;
                        background-color: #1c1c1e;
                        color: #ffffff;
                        font-size: 12px;
                        font-weight: 600;
                    }
                """,
                "tab_widget": """
                    QTabWidget::pane {
                        border: none;
                        background-color: #1c1c1e;
                    }
                    QTabBar::tab {
                        background-color: #2c2c2e;
                        color: #ebebf5;
                        padding: 12px 24px;
                        margin-right: 4px;
                        border-top-left-radius: 8px;
                        border-top-right-radius: 8px;
                        font-weight: 500;
                        font-size: 12px;
                        border: none;
                    }
                    QTabBar::tab:selected {
                        background-color: #1c1c1e;
                        color: #ffffff;
                        border-bottom: 2px solid #0a84ff;
                    }
                    QTabBar::tab:hover:!selected {
                        background-color: #3a3a3c;
                        color: #ffffff;
                    }
                """,
            },
        }

    def _get_system_theme(self) -> Dict[str, Any]:
        """Get system theme (follows OS preference)"""
        # Detect the current system theme preference
        system_theme = self._detect_system_theme()
        if system_theme == "Dark":
            return self._get_dark_theme()
        else:
            return self._get_light_theme()

    def _detect_system_theme(self) -> str:
        """Detect the current system theme preference"""
        try:
            import platform
            import subprocess
            import sys

            system = platform.system()

            if system == "Darwin":  # macOS
                return self._detect_macos_theme()
            elif system == "Windows":
                return self._detect_windows_theme()
            elif system == "Linux":
                return self._detect_linux_theme()
            else:
                self.logger.debug(
                    f"Unknown system: {system}, defaulting to light theme"
                )
                return "Light"

        except Exception as e:
            self.logger.warning(
                f"Error detecting system theme: {e}, defaulting to light theme"
            )
            return "Light"

    def _detect_macos_theme(self) -> str:
        """Detect macOS system theme"""
        try:
            import subprocess

            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip() == "Dark":
                return "Dark"
            else:
                return "Light"
        except Exception as e:
            self.logger.debug(
                f"Error detecting macOS theme: {e}, defaulting to light theme"
            )
            return "Light"

    def _detect_windows_theme(self) -> str:
        """Detect Windows system theme"""
        try:
            import subprocess

            result = subprocess.run(
                [
                    "reg",
                    "query",
                    "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                    "/v",
                    "AppsUseLightTheme",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                # If AppsUseLightTheme is 0, it means dark theme is enabled
                if "0x0" in result.stdout:
                    return "Dark"
                else:
                    return "Light"
            else:
                return "Light"
        except Exception as e:
            self.logger.debug(
                f"Error detecting Windows theme: {e}, defaulting to light theme"
            )
            return "Light"

    def _detect_linux_theme(self) -> str:
        """Detect Linux system theme"""
        try:
            import os
            import subprocess

            # Try to detect GTK theme
            gtk_theme = os.environ.get("GTK_THEME", "")
            if "dark" in gtk_theme.lower():
                return "Dark"

            # Try to detect KDE theme
            kde_theme = os.environ.get("KDEWM", "")
            if kde_theme:
                # For KDE, we'd need to check the actual theme file
                # This is a simplified approach
                pass

            # Try to detect using gsettings (GNOME)
            try:
                result = subprocess.run(
                    ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0 and "dark" in result.stdout.lower():
                    return "Dark"
            except:
                pass

            # Default to light theme for Linux
            return "Light"

        except Exception as e:
            self.logger.debug(
                f"Error detecting Linux theme: {e}, defaulting to light theme"
            )
            return "Light"

    def apply_theme(self, theme_name: str, app: Optional[QApplication] = None) -> bool:
        """Apply a theme to the application"""
        if not PYSIDE6_AVAILABLE:
            self.logger.debug("PySide6 not available, skipping theme application")
            return True

        try:
            # Handle "System" theme by detecting current system preference
            if theme_name == "System":
                detected_theme = self._detect_system_theme()
                self.logger.info(f"System theme detected as: {detected_theme}")

                # Apply the detected theme
                if detected_theme == "Dark":
                    theme = self.themes["Dark"]
                    self.current_theme = "System (Dark)"
                else:
                    theme = self.themes["Light"]
                    self.current_theme = "System (Light)"
            else:
                if theme_name not in self.themes:
                    self.logger.error(f"Theme '{theme_name}' not found")
                    return False

                self.current_theme = theme_name
                theme = self.themes[theme_name]

            # Store current font size
            current_font_size = self.current_font_size

            # Apply theme to application
            if app and isinstance(app, QApplication):
                self._apply_to_application(app, theme)
                self._refresh_all_widgets(app)

            # Restore font size after theme change
            self.current_font_size = current_font_size

            self.logger.info(f"Theme '{theme_name}' applied successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error applying theme '{theme_name}': {e}")
            return False

    def _apply_to_application(self, app: QApplication, theme: Dict[str, Any]) -> None:
        """Apply theme to QApplication"""
        if not PYSIDE6_AVAILABLE:
            self.logger.debug(
                "PySide6 not available, skipping application theme application"
            )
            return

        # Set application palette
        palette = QPalette()
        colors = theme["colors"]

        # Set palette colors using ColorRole enum
        palette.setColor(QPalette.ColorRole.Window, QColor(colors["background"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors["text_primary"]))
        palette.setColor(
            QPalette.ColorRole.Base, QColor(colors["background_secondary"])
        )
        palette.setColor(
            QPalette.ColorRole.AlternateBase, QColor(colors["background_tertiary"])
        )
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors["background"]))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors["text_primary"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors["text_primary"]))
        palette.setColor(
            QPalette.ColorRole.Button, QColor(colors["background_secondary"])
        )
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors["text_primary"]))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(colors["error"]))
        palette.setColor(QPalette.ColorRole.Link, QColor(colors["primary"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors["primary"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))

        app.setPalette(palette)

        # Force refresh of all widgets
        self._refresh_all_widgets(app)

    def _refresh_all_widgets(self, app: QApplication) -> None:
        """Force refresh all widgets to apply theme changes"""
        if not PYSIDE6_AVAILABLE:
            self.logger.debug("PySide6 not available, skipping widget refresh")
            return

        try:
            # Get all top-level widgets
            for widget in app.topLevelWidgets():
                if widget.isVisible():
                    widget.update()
                    widget.repaint()

                    # Also update child widgets
                    for child in widget.findChildren(QWidget):
                        child.update()
                        child.repaint()
        except Exception as e:
            self.logger.error(f"Error refreshing widgets: {e}")

    def get_theme_style(self, component: str) -> str:
        """Get style for a specific component"""
        theme = self.themes.get(self.current_theme, self.themes["Light"])
        return theme["styles"].get(component, "")

    def get_theme_color(self, color_name: str) -> str:
        """Get a specific color from the current theme"""
        theme = self.themes.get(self.current_theme, self.themes["Light"])
        return theme["colors"].get(color_name, "#000000")

    def get_current_theme(self) -> str:
        """Get the current theme name"""
        return self.current_theme


# Global theme manager instance
_theme_manager = None


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def apply_theme(theme_name: str, app: Optional[QApplication] = None) -> bool:
    """Apply a theme to the application"""
    return get_theme_manager().apply_theme(theme_name, app)


def get_theme_style(component: str) -> str:
    """Get style for a specific component"""
    return get_theme_manager().get_theme_style(component)


def get_theme_color(color_name: str) -> str:
    """Get a specific color from the current theme"""
    return get_theme_manager().get_theme_color(color_name)


def set_font_size(font_size: int) -> None:
    """Set the application font size"""
    get_theme_manager().set_font_size(font_size)


def get_font_size() -> int:
    """Get the current application font size"""
    return get_theme_manager().get_font_size()


def set_font_family(font_family: str) -> None:
    """Set the application font family"""
    get_theme_manager().set_font_family(font_family)


def get_font_family() -> str:
    """Get the current application font family"""
    return get_theme_manager().get_font_family()


def get_font_size_style(component: str = "general") -> str:
    """Get font size style for a specific component"""
    return get_theme_manager().get_font_size_style(component)


def get_complete_style(component: str, include_font_size: bool = True) -> str:
    """Get complete style including theme and font size"""
    return get_theme_manager().get_complete_style(component, include_font_size)


def force_font_size_update(widget, component: str = "general") -> None:
    """Force update a widget's font size"""
    get_theme_manager().force_font_size_update(widget, component)


def apply_font_size_to_widget_tree(
    root_widget, component_map: Optional[Dict[str, str]] = None
) -> None:
    """Apply font size to an entire widget tree"""
    get_theme_manager().apply_font_size_to_widget_tree(root_widget, component_map)
