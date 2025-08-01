#!/usr/bin/env python3
"""
Theme manager for HelpMeSign application
Handles theme application and UI styling
"""

from typing import Any, Dict, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QWidget

from .logger import get_logger


class ThemeManager:
    """Manages application themes and styling"""

    def __init__(self):
        self.logger = get_logger("helpmesign.theme")
        self.current_theme = "Light"
        self.themes = {
            "Light": self._get_light_theme(),
            "Dark": self._get_dark_theme(),
            "System": self._get_system_theme(),
        }

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
                    }
                """,
                "dialog": """
                    QDialog {
                        background-color: #ffffff;
                        border: 1px solid #e2e8f0;
                        border-radius: 16px;
                        color: #1e293b;
                    }
                    QDialog QLabel {
                        color: #1e293b;
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
                        font-size: 14px;
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
                        font-size: 14px;
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
                        font-size: 14px;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        left: 16px;
                        padding: 0 8px 0 8px;
                        background-color: #ffffff;
                        color: #1e293b;
                        font-size: 14px;
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
                        font-size: 14px;
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
                "primary": "#3b82f6",
                "primary_hover": "#60a5fa",
                "primary_pressed": "#2563eb",
                "background": "#0f172a",
                "background_secondary": "#1e293b",
                "background_tertiary": "#334155",
                "text_primary": "#f8fafc",
                "text_secondary": "#cbd5e1",
                "text_muted": "#94a3b8",
                "border": "#334155",
                "border_secondary": "#475569",
                "success": "#10b981",
                "warning": "#f59e0b",
                "error": "#ef4444",
            },
            "styles": {
                "main_window": """
                    QMainWindow {
                        background-color: #0f172a;
                        color: #f8fafc;
                    }
                """,
                "dialog": """
                    QDialog {
                        background-color: #1e293b;
                        border: 1px solid #334155;
                        border-radius: 16px;
                        color: #f8fafc;
                    }
                    QDialog QLabel {
                        color: #f8fafc;
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
                        font-size: 14px;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #60a5fa;
                    }
                    QPushButton:pressed {
                        background-color: #2563eb;
                    }
                    QPushButton:disabled {
                        background-color: #94a3b8;
                        color: #cbd5e1;
                    }
                """,
                "button_secondary": """
                    QPushButton {
                        background-color: #334155;
                        color: #cbd5e1;
                        border: 1px solid #475569;
                        border-radius: 8px;
                        font-weight: 500;
                        padding: 10px 20px;
                        font-size: 14px;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #475569;
                        color: #f1f5f9;
                    }
                    QPushButton:pressed {
                        background-color: #64748b;
                    }
                    QPushButton:disabled {
                        background-color: #f8fafc;
                        color: #cbd5e1;
                        border-color: #e2e8f0;
                    }
                """,
                "input_field": """
                    QLineEdit, QTextEdit {
                        background-color: #1e293b;
                        color: #f8fafc;
                        border: 1px solid #475569;
                        border-radius: 8px;
                        padding: 8px 12px;
                    }
                    QLineEdit:focus, QTextEdit:focus {
                        border-color: #3b82f6;
                        outline: none;
                    }
                """,
                "group_box": """
                    QGroupBox {
                        font-weight: 600;
                        color: #f8fafc;
                        border: 1px solid #334155;
                        border-radius: 12px;
                        margin-top: 12px;
                        padding-top: 16px;
                        background-color: #1e293b;
                        font-size: 14px;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        left: 16px;
                        padding: 0 8px 0 8px;
                        background-color: #1e293b;
                        color: #f8fafc;
                        font-size: 14px;
                        font-weight: 600;
                    }
                """,
                "tab_widget": """
                    QTabWidget::pane {
                        border: none;
                        background-color: #1e293b;
                    }
                    QTabBar::tab {
                        background-color: #334155;
                        color: #cbd5e1;
                        padding: 12px 24px;
                        margin-right: 4px;
                        border-top-left-radius: 8px;
                        border-top-right-radius: 8px;
                        font-weight: 500;
                        font-size: 14px;
                        border: none;
                    }
                    QTabBar::tab:selected {
                        background-color: #1e293b;
                        color: #f8fafc;
                        border-bottom: 2px solid #3b82f6;
                    }
                    QTabBar::tab:hover:!selected {
                        background-color: #475569;
                        color: #f1f5f9;
                    }
                """,
            },
        }

    def _get_system_theme(self) -> Dict[str, Any]:
        """Get system theme (follows OS preference)"""
        # For now, default to light theme
        # In the future, this could detect OS theme preference
        return self._get_light_theme()

    def apply_theme(self, theme_name: str, app: Optional[QApplication] = None) -> bool:
        """Apply a theme to the application"""
        try:
            if theme_name not in self.themes:
                self.logger.warning(f"Unknown theme: {theme_name}, using Light")
                theme_name = "Light"

            self.current_theme = theme_name
            theme = self.themes[theme_name]

            self.logger.info(f"Applying theme: {theme_name}")

            # Apply to QApplication if provided
            if app:
                self._apply_to_application(app, theme)

                # Force application update
                app.processEvents()

            return True

        except Exception as e:
            self.logger.error(f"Error applying theme {theme_name}: {e}")
            return False

    def _apply_to_application(self, app: QApplication, theme: Dict[str, Any]) -> None:
        """Apply theme to QApplication"""
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
