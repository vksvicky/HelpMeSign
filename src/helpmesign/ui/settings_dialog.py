#!/usr/bin/env python3
"""
Settings dialog for HelpMeSign application
Provides a modern, user-friendly interface for managing application preferences
"""

import os
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

if TYPE_CHECKING:
    from PySide6.QtCore import QCoreApplication, QRect, QSize, Qt, Signal
    from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
    from PySide6.QtWidgets import (
        QButtonGroup,
        QCheckBox,
        QComboBox,
        QDialog,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QRadioButton,
        QScrollArea,
        QSizePolicy,
        QSlider,
        QTabBar,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

# Try to import PySide6 components
try:
    from PySide6.QtCore import QCoreApplication, QRect, QSize, Qt, Signal
    from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
    from PySide6.QtWidgets import (
        QButtonGroup,
        QCheckBox,
        QComboBox,
        QDialog,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QRadioButton,
        QScrollArea,
        QSizePolicy,
        QSlider,
        QTabBar,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

from ..core.startup import get_all_settings, save_all_settings
from ..utils.language_manager import get_dict, get_list, get_text
from ..utils.logger import get_logger

# Conditional font manager import
try:
    from ..utils.font_manager import get_body_font, get_button_font, get_heading_font

    FONT_MANAGER_AVAILABLE = True
except ImportError:
    FONT_MANAGER_AVAILABLE = False

    # Create dummy functions with proper return types
    def get_body_font() -> Union[QFont, None]:  # type: ignore
        return None

    def get_button_font() -> Union[QFont, None]:  # type: ignore
        return None

    def get_heading_font() -> Union[QFont, None]:  # type: ignore
        return None


# Conditional theme manager import
try:
    from ..utils.theme_manager import apply_theme, get_theme_manager

    THEME_MANAGER_AVAILABLE = True
except ImportError:
    THEME_MANAGER_AVAILABLE = False

    # Create dummy functions with proper signatures
    def apply_theme(*args: Any, **kwargs: Any) -> Union[bool, None]:  # type: ignore
        return None

    def get_theme_manager() -> Union[Any, None]:  # type: ignore
        return None


class FontSizeSelector(QWidget):
    """Innovative font size selector with visual preview"""

    size_changed = Signal(int)

    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            raise ImportError("PySide6 is required for FontSizeSelector")

        super().__init__(parent)
        self.current_size = 12
        self.sizes = [10, 11, 12, 13, 14, 15, 16, 17, 18]
        self.hover_index = -1
        self.setMouseTracking(True)
        # Remove fixed height to allow dynamic sizing
        self.setMinimumHeight(80)
        self.setMaximumHeight(120)

        # Initialize logger
        from ..utils.logger import get_logger

        self.logger = get_logger("helpmesign.font_selector")

        # Get theme-aware colors
        self._update_colors()

    def _update_colors(self):
        """Update colors based on current theme"""
        try:
            from ..utils.theme_manager import get_theme_manager

            theme_manager = get_theme_manager()
            current_theme = theme_manager.get_current_theme()

            if current_theme == "Dark":
                self.bg_color = "#1c1c1e"
                self.selected_bg = "#0a84ff"
                self.selected_text = "#ffffff"
                self.unselected_bg = "#2c2c2e"
                self.unselected_text = "#ebebf5"
                self.hover_bg = "#3a3a3c"
                self.border_color = "#38383a"
            else:
                self.bg_color = "#ffffff"
                self.selected_bg = "#3b82f6"
                self.selected_text = "#ffffff"
                self.unselected_bg = "#f1f5f9"
                self.unselected_text = "#64748b"
                self.hover_bg = "#e2e8f0"
                self.border_color = "#d1d5db"
        except Exception as e:
            self.logger.error(f"Error getting theme colors: {e}")
            # Fallback colors
            self.bg_color = "#ffffff"
            self.selected_bg = "#3b82f6"
            self.selected_text = "#ffffff"
            self.unselected_bg = "#f1f5f9"
            self.unselected_text = "#64748b"
            self.hover_bg = "#e2e8f0"
            self.border_color = "#d1d5db"

    def paintEvent(self, event):
        """Custom paint event for the font size selector"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Update colors based on current theme
        self._update_colors()

        # Calculate item width and height with better spacing
        item_width = self.width() // len(self.sizes)
        item_height = self.height() - 25  # Increased space for labels

        # Draw background
        painter.fillRect(self.rect(), QColor(self.bg_color))

        # Draw font size options
        for i, size in enumerate(self.sizes):
            x = i * item_width
            item_rect = QRect(
                x + 3, 3, item_width - 6, item_height
            )  # Increased margins

            # Determine colors based on state
            if size == self.current_size:
                bg_color = self.selected_bg
                text_color = self.selected_text
            elif i == self.hover_index:
                bg_color = self.hover_bg
                text_color = self.unselected_text
            else:
                bg_color = self.unselected_bg
                text_color = self.unselected_text

            # Draw background
            painter.fillRect(item_rect, QColor(bg_color))

            # Draw border
            painter.setPen(QPen(QColor(self.border_color), 1))
            painter.drawRect(item_rect)

            # Draw sample text
            font = QFont()
            font.setPointSize(size)
            painter.setFont(font)
            painter.setPen(QColor(text_color))

            # Sample text that shows the size
            sample_text = "Aa"
            text_rect = item_rect.adjusted(6, 6, -6, -6)  # Increased padding
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, sample_text)

            # Draw size label below
            label_font = QFont()
            label_font.setPointSize(9)  # Slightly larger label font
            painter.setFont(label_font)
            painter.setPen(QColor(text_color))

            size_text = f"{size}px"
            label_rect = QRect(
                x + 3, item_height + 6, item_width - 6, 20
            )  # Increased height
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, size_text)

    def mousePressEvent(self, event):
        """Handle mouse press to select font size"""
        if event.button() == Qt.MouseButton.LeftButton:
            item_width = self.width() // len(self.sizes)
            index = int(event.position().x() // item_width)

            if 0 <= index < len(self.sizes):
                new_size = self.sizes[index]
                if new_size != self.current_size:
                    self.current_size = new_size
                    self.size_changed.emit(new_size)
                    self.update()

    def mouseMoveEvent(self, event):
        """Handle mouse move for hover effects"""
        item_width = self.width() // len(self.sizes)
        index = int(event.position().x() // item_width)

        if 0 <= index < len(self.sizes):
            if self.hover_index != index:
                self.hover_index = index
                self.update()
        elif self.hover_index != -1:
            self.hover_index = -1
            self.update()

    def leaveEvent(self, event):
        """Handle mouse leave event"""
        if self.hover_index != -1:
            self.hover_index = -1
            self.update()

    def set_size(self, size: int):
        """Set the current font size"""
        if size in self.sizes and size != self.current_size:
            self.current_size = size
            self.update()
            self.repaint()

            # Add debugging
            try:
                from ..utils.logger import get_logger

                logger = get_logger("helpmesign.font_selector")
                logger.debug(
                    f"Font size selector set_size called: {size}px, current_size now: {self.current_size}"
                )
            except:
                pass

    def get_size(self) -> int:
        """Get the current font size"""
        return self.current_size

    def force_color_update(self):
        """Force update colors when theme changes"""
        self._update_colors()
        self.update()


class ModernSegmentedControl(QFrame):
    """Modern segmented control widget"""

    selection_changed = Signal(str)

    def __init__(self, options: List[str], parent=None):
        if not PYSIDE6_AVAILABLE:
            raise ImportError("PySide6 is required for ModernSegmentedControl")

        super().__init__(parent)
        self.options = options
        self.selected_option = options[0] if options else ""
        self.selected_index = 0 if options else -1
        self.hover_index = -1
        self.setMouseTracking(True)
        self.setFixedHeight(40)

        # Initialize logger
        from ..utils.logger import get_logger

        self.logger = get_logger("helpmesign.segmented_control")

        # Get theme-aware colors
        self._update_colors()

    def _update_colors(self):
        """Update colors based on current theme"""
        try:
            from ..utils.theme_manager import get_theme_manager

            theme_manager = get_theme_manager()
            current_theme = theme_manager.get_current_theme()

            # Only log when theme actually changes (not on every paint event)
            if not hasattr(self, "_last_theme") or self._last_theme != current_theme:
                self.logger.debug(
                    f"ModernSegmentedControl: Theme changed to: {current_theme}"
                )
                self._last_theme = current_theme

            if current_theme == "Dark":
                # Dark theme colors - macOS-style dark backgrounds
                self.bg_color = "#1c1c1e"  # macOS dark background
                self.selected_bg = "#0a84ff"  # macOS blue for selected
                self.selected_text = "#ffffff"  # White text for selected
                self.unselected_bg = "#2c2c2e"  # macOS dark secondary for unselected
                self.unselected_text = "#ebebf5"  # Light gray text for unselected
                self.hover_bg = "#3a3a3c"  # macOS dark tertiary for hover
                self.border_color = "#38383a"  # Dark border color
            else:
                # Light theme colors - light backgrounds
                self.bg_color = "#ffffff"  # White background to match dialog
                self.selected_bg = "#3b82f6"  # Blue for selected
                self.selected_text = "#ffffff"  # White text for selected
                self.unselected_bg = "#f1f5f9"  # Light gray for unselected
                self.unselected_text = "#64748b"  # Gray text for unselected
                self.hover_bg = "#e2e8f0"  # Light gray for hover
                self.border_color = "#d1d5db"  # Border color
        except Exception as e:
            # Fallback colors if theme manager fails
            self.logger.error(
                f"ModernSegmentedControl: Error getting theme, using fallback: {e}"
            )
            self.bg_color = "#ffffff"
            self.selected_bg = "#3b82f6"
            self.selected_text = "#ffffff"
            self.unselected_bg = "#f1f5f9"
            self.unselected_text = "#64748b"
            self.hover_bg = "#e2e8f0"
            self.border_color = "#d1d5db"

    def paintEvent(self, event):
        """Custom paint event for the segmented control"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        try:
            # Only update colors if theme has changed (not on every paint)
            if not hasattr(self, "_colors_initialized"):
                self._update_colors()
                self._colors_initialized = True

            # Calculate segment width
            segment_width = self.width() // len(self.options)
            segment_height = self.height()

            # Draw background
            painter.fillRect(self.rect(), QColor(self.bg_color))

            # Draw segments
            for i, option in enumerate(self.options):
                x = i * segment_width
                segment_rect = QRect(x, 0, segment_width, segment_height)

                # Determine colors based on state
                if i == self.selected_index:
                    bg_color = self.selected_bg
                    text_color = self.selected_text
                elif i == self.hover_index:
                    bg_color = self.hover_bg
                    text_color = self.unselected_text
                else:
                    bg_color = self.unselected_bg
                    text_color = self.unselected_text

                # Draw segment background
                painter.fillRect(segment_rect, QColor(bg_color))

                # Draw segment border
                painter.setPen(QPen(QColor(self.border_color), 1))
                painter.drawRect(segment_rect)

                # Draw text
                painter.setPen(QColor(text_color))
                font = painter.font()
                font.setWeight(
                    QFont.Weight.Bold
                    if i == self.selected_index
                    else QFont.Weight.Normal
                )
                painter.setFont(font)

                # Center text in segment
                text_rect = segment_rect
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, option)

        finally:
            painter.end()

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.MouseButton.LeftButton:
            segment_width = self.width() // len(self.options)
            clicked_index = int(event.position().x() // segment_width)

            if 0 <= clicked_index < len(self.options):
                self.set_selection(self.options[clicked_index])

    def mouseMoveEvent(self, event):
        """Handle mouse move events for hover effects"""
        segment_width = self.width() // len(self.options)
        hover_index = int(event.position().x() // segment_width)

        if 0 <= hover_index < len(self.options):
            self.hover_index = hover_index
        else:
            self.hover_index = -1

        self.update()

    def leaveEvent(self, event):
        """Handle mouse leave events"""
        self.hover_index = -1
        self.update()

    def force_color_update(self):
        """Force update colors when theme changes"""
        self._update_colors()
        self._colors_initialized = True
        self.update()

    def set_selection(self, option: str):
        """Set the selected option"""
        if option in self.options:
            self.selected_index = self.options.index(option)
            self.selected_option = option
            self.update()  # Trigger repaint
            self.selection_changed.emit(option)
        else:
            self.logger.warning(
                f"Option '{option}' not found in options: {self.options}"
            )

    def get_selection(self) -> str:
        """Get the currently selected option"""
        return self.selected_option


class SettingsDialog(QDialog):
    """Modern settings dialog for user preferences"""

    # Signal emitted when settings are applied
    settings_applied = Signal(str)

    def __init__(
        self,
        parent=None,
        current_mode: str = "Sign & Translate",
        environment: str = "dev",
        main_window=None,
    ):
        if not PYSIDE6_AVAILABLE:
            raise ImportError("PySide6 is required for SettingsDialog")

        super().__init__(parent)
        self.logger = get_logger("helpmesign.settings")
        self.environment = environment
        self.main_window = main_window
        self.current_mode = current_mode

        # Initialize settings tracking
        self.original_settings: Dict[str, Any] = {}
        self.current_settings: Dict[str, Any] = {}
        self._applying_settings = False

        # Reset loop detection counters
        self._reset_loop_detection()

        # Setup UI
        self.setup_ui()

        # Load current settings
        self.load_current_settings()

        # Setup behavior
        self.setup_behavior()

        # Apply initial theme
        self._apply_initial_theme()

        self.logger.info("Settings dialog initialized")

    def _reset_loop_detection(self):
        """Reset loop detection counters"""
        self._save_call_depth = 0
        self._theme_change_depth = 0

    def showEvent(self, event):
        """Handle dialog show event"""
        super().showEvent(event)
        # Reset loop detection when dialog is shown
        self._reset_loop_detection()

        # Re-enable all controls when dialog is shown
        self._enable_all_controls()

        self.logger.debug(
            "Settings dialog shown - loop detection reset and controls enabled"
        )

    def _enable_all_controls(self):
        """Enable all controls in the dialog"""
        try:
            # Re-enable font size selector
            if hasattr(self, "font_size_selector"):
                self.font_size_selector.setEnabled(True)

            # Re-enable theme control
            if hasattr(self, "theme_control"):
                self.theme_control.setEnabled(True)

            # Re-enable mode selector
            if hasattr(self, "segmented_control"):
                self.segmented_control.setEnabled(True)

            # Re-enable buttons
            if hasattr(self, "ok_button"):
                self.ok_button.setEnabled(True)
            if hasattr(self, "cancel_button"):
                self.cancel_button.setEnabled(True)
            if hasattr(self, "reset_button"):
                self.reset_button.setEnabled(True)

        except Exception as e:
            self.logger.error(f"Error enabling controls: {e}")

    def setup_ui(self):
        """Set up the settings dialog UI"""
        # Set window properties
        self.setWindowTitle("Settings")
        # Remove fixed size to allow dynamic sizing based on font size
        self.setMinimumSize(600, 460)
        self.resize(700, 550)  # Start with a larger default size
        self.setModal(False)

        # Apply initial theme styling
        self._apply_initial_theme()

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header frame (minimal)
        header_frame = QFrame()
        header_frame.setFixedHeight(30)  # Increased from 20
        header_frame.setContentsMargins(20, 15, 20, 15)  # Increased margins
        main_layout.addWidget(header_frame)

        # Content frame
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(25, 0, 25, 25)  # Increased margins
        content_layout.setSpacing(25)  # Increased spacing

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_general_tab(), "General")
        self.tab_widget.addTab(self.create_appearance_tab(), "Appearance")
        self.tab_widget.addTab(self.create_preferences_tab(), "Preferences")

        # Tab bar styling will be applied after settings are loaded
        content_layout.addWidget(self.tab_widget)

        # Footer frame
        footer_frame = QFrame()
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(25, 0, 25, 25)  # Increased margins
        footer_layout.setSpacing(15)  # Increased spacing

        # Reset button
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_to_defaults)
        footer_layout.addWidget(self.reset_button)

        footer_layout.addStretch()

        # Cancel and Save buttons
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button = QPushButton("Save Changes")
        self.ok_button.setObjectName("primary")  # For primary button styling
        self.ok_button.clicked.connect(self.apply_settings)
        footer_layout.addWidget(self.cancel_button)
        footer_layout.addWidget(self.ok_button)

        main_layout.addWidget(content_frame)
        main_layout.addWidget(footer_frame)

    def _apply_initial_theme(self):
        """Apply the current theme styling to the dialog"""
        try:
            from ..utils.theme_manager import get_theme_manager

            theme_manager = get_theme_manager()
            current_theme = theme_manager.get_current_theme()

            self.logger.debug(
                f"Settings dialog: Initial theme detected as: {current_theme}"
            )

            # Apply theme-specific styling
            if current_theme == "Dark":
                self.logger.debug("Settings dialog: Applying dark theme")
                self._apply_dark_theme()
            else:
                self.logger.debug("Settings dialog: Applying light theme")
                self._apply_light_theme()

            # Update GroupBox styling
            self._update_group_box_styling(current_theme)

            # Update all segmented controls to match the initial theme
            self._update_all_segmented_controls(current_theme)

        except Exception as e:
            self.logger.error(f"Error applying initial theme: {e}")
            # Fallback to light theme
            self.logger.debug("Settings dialog: Falling back to light theme")
            self._apply_light_theme()

    def _apply_light_theme(self):
        """Apply light theme styling"""
        self.logger.debug("Applying light theme styling to settings dialog")
        self.setStyleSheet(
            """
            QDialog {
                background-color: #ffffff;
                color: #1e293b;
            }
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
            QGroupBox {
                font-weight: 600;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 16px;
                background-color: #ffffff !important;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px 0 8px;
                background-color: #ffffff !important;
                color: #1e293b;
                font-size: 14px;
                font-weight: 600;
            }
            QGroupBox * {
                background-color: #ffffff !important;
            }
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
            QPushButton#primary {
                background-color: #3b82f6;
                color: white;
                border: none;
            }
            QPushButton#primary:hover {
                background-color: #2563eb;
            }
            QPushButton#primary:pressed {
                background-color: #1d4ed8;
            }
            QLabel {
                color: #1e293b;
            }
            QSlider::groove:horizontal {
                border: 1px solid #d1d5db;
                height: 8px;
                background: #f1f5f9;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3b82f6;
                border: 2px solid #3b82f6;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #3b82f6;
                border-radius: 4px;
            }
        """
        )
        self.logger.debug("Light theme styling applied successfully")

    def _apply_dark_theme(self):
        """Apply dark theme styling"""
        self.setStyleSheet(
            """
            QDialog {
                background-color: #1c1c1e;
                color: #ffffff;
            }
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
                font-size: 14px;
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
            QGroupBox {
                font-weight: 600;
                color: #ffffff;
                border: 1px solid #38383a;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 16px;
                background-color: #1c1c1e;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px 0 8px;
                background-color: #1c1c1e;
                color: #ffffff;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton {
                background-color: #2c2c2e;
                color: #ebebf5;
                border: 1px solid #48484a;
                border-radius: 8px;
                font-weight: 500;
                padding: 10px 20px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3a3a3c;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #48484a;
            }
            QPushButton#primary {
                background-color: #0a84ff;
                color: white;
                border: none;
            }
            QPushButton#primary:hover {
                background-color: #409cff;
            }
            QPushButton#primary:pressed {
                background-color: #0056d6;
            }
            QLabel {
                color: #ffffff;
            }
            QSlider::groove:horizontal {
                border: 1px solid #48484a;
                height: 8px;
                background: #2c2c2e;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0a84ff;
                border: 2px solid #0a84ff;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #0a84ff;
                border-radius: 4px;
            }
        """
        )

    def create_general_tab(self):
        """Create the General settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Application Mode section
        mode_group = QGroupBox("Application Mode")
        # Remove hardcoded styling - let theme-based styling take over

        mode_layout = QVBoxLayout(mode_group)
        mode_layout.setContentsMargins(20, 20, 20, 20)
        mode_layout.setSpacing(16)

        # Mode selection label
        mode_label = QLabel("Select your preferred mode:")
        mode_label.setFont(get_body_font())
        mode_label.setStyleSheet("color: #64748b; font-size: 13px; margin-bottom: 4px;")
        mode_layout.addWidget(mode_label)

        # Modern segmented control
        self.segmented_control = ModernSegmentedControl(
            [
                get_text("modes.sign_translate.name"),
                get_text("modes.learn.name"),
            ]
        )
        self.segmented_control.set_selection(self.current_mode)
        mode_layout.addWidget(self.segmented_control)

        # Mode description with better styling
        self.description_label = QLabel()
        self.description_label.setFont(get_body_font())
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet(
            """
            QLabel {
                color: #64748b;
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
                line-height: 1.5;
                font-size: 13px;
            }
        """
        )
        mode_layout.addWidget(self.description_label)

        layout.addWidget(mode_group)

        # Other general settings can be added here
        layout.addStretch()
        return tab

    def create_appearance_tab(self) -> QWidget:
        """Create the appearance tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(25, 25, 25, 25)  # Increased margins
        layout.setSpacing(25)  # Increased spacing

        # Theme Group
        theme_group = QGroupBox("Theme")
        # Remove hardcoded styling - let theme-based styling take over
        theme_layout = QVBoxLayout(theme_group)
        theme_layout.setContentsMargins(20, 25, 20, 20)  # Increased margins
        theme_layout.setSpacing(15)  # Increased spacing

        # Theme segmented control
        self.theme_control = ModernSegmentedControl(
            ["Light", "Dark", "System"], parent=theme_group
        )
        self.theme_control.setFixedHeight(45)  # Increased height
        self.theme_control.selection_changed.connect(self._on_theme_changed)
        theme_layout.addWidget(self.theme_control)

        # Theme description
        self.theme_description = QLabel("Choose your preferred theme")
        # Remove hardcoded styling - let theme-based styling take over
        theme_layout.addWidget(self.theme_description)

        # Font Size Group
        font_group = QGroupBox("Font Size")
        # Remove hardcoded styling - let theme-based styling take over
        font_layout = QVBoxLayout(font_group)
        font_layout.setContentsMargins(20, 25, 20, 20)  # Increased margins
        font_layout.setSpacing(15)  # Increased spacing

        # Font size label
        font_label = QLabel("Choose your preferred text size:")
        # Remove hardcoded styling - let theme-based styling take over
        font_layout.addWidget(font_label)

        # Font size selector (replaces slider)
        self.font_size_selector = FontSizeSelector()
        self.font_size_selector.set_size(12)  # Default size
        self.font_size_selector.setFixedHeight(
            60
        )  # Increased height for better visibility
        font_layout.addWidget(self.font_size_selector)

        # Connect theme control for real-time preview
        self.theme_control.selection_changed.connect(self._on_theme_changed)

        layout.addWidget(theme_group)
        layout.addWidget(font_group)
        layout.addStretch()
        return tab

    def create_preferences_tab(self) -> QWidget:
        """Create the preferences tab with hand preference settings"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(25, 25, 25, 25)  # Increased margins
        layout.setSpacing(25)  # Increased spacing

        # Hand Preference Group
        hand_preference_title = get_text("ui.language_selection.hand_preference_title")
        # Fallback to string if get_text returns a mock object
        if hasattr(hand_preference_title, "__call__") or not isinstance(
            hand_preference_title, str
        ):
            hand_preference_title = "Hand Preference"
        hand_group = QGroupBox(hand_preference_title)
        hand_layout = QVBoxLayout(hand_group)
        hand_layout.setContentsMargins(20, 25, 20, 20)  # Increased margins
        hand_layout.setSpacing(15)  # Increased spacing

        # Hand preference description
        hand_description = QLabel(
            "Choose your preferred hand for sign language gestures"
        )
        hand_layout.addWidget(hand_description)

        # Hand preference radio buttons
        self.hand_button_group = QButtonGroup()

        right_hand_text = get_text("ui.language_selection.right_hand")
        if hasattr(right_hand_text, "__call__") or not isinstance(right_hand_text, str):
            right_hand_text = "Right Hand"
        self.right_hand_radio = QRadioButton(right_hand_text)
        self.right_hand_radio.setChecked(True)  # Default to right hand
        self.hand_button_group.addButton(self.right_hand_radio)
        hand_layout.addWidget(self.right_hand_radio)

        left_hand_text = get_text("ui.language_selection.left_hand")
        if hasattr(left_hand_text, "__call__") or not isinstance(left_hand_text, str):
            left_hand_text = "Left Hand"
        self.left_hand_radio = QRadioButton(left_hand_text)
        self.hand_button_group.addButton(self.left_hand_radio)
        hand_layout.addWidget(self.left_hand_radio)

        # Connect hand preference changes
        self.right_hand_radio.toggled.connect(self._on_hand_preference_changed)
        self.left_hand_radio.toggled.connect(self._on_hand_preference_changed)

        layout.addWidget(hand_group)
        layout.addStretch()
        return tab

    def _on_hand_preference_changed(self) -> None:
        """Handle hand preference changes"""
        try:
            # Get the selected hand preference
            if self.right_hand_radio.isChecked():
                hand_preference = "right"
            elif self.left_hand_radio.isChecked():
                hand_preference = "left"
            else:
                hand_preference = "right"  # Default fallback

            # Store the preference in current settings
            self.current_settings["hand_preference"] = hand_preference

            self.logger.debug(f"Hand preference changed to: {hand_preference}")

            # Update any relevant UI components that depend on hand preference
            if hasattr(self, "main_window") and self.main_window:
                # Notify main window of hand preference change
                if hasattr(self.main_window, "update_hand_preference"):
                    self.main_window.update_hand_preference(hand_preference)

        except Exception as e:
            self.logger.error(f"Error handling hand preference change: {e}")

    def _update_group_box_styling(self, theme_name: str) -> None:
        """Update GroupBox styling based on the current theme"""
        try:
            from ..utils.theme_manager import get_theme_manager

            theme_manager = get_theme_manager()
            group_box_style = theme_manager.get_theme_style("group_box")

            # Find all GroupBox widgets in the dialog and update their styling
            for group_box in self.findChildren(QGroupBox):
                group_box.setStyleSheet(group_box_style)

            self.logger.debug(f"Updated GroupBox styling for theme: {theme_name}")
        except Exception as e:
            self.logger.error(f"Error updating GroupBox styling: {e}")

    def _on_theme_changed(self, theme_name: str) -> None:
        """Handle theme change in real-time"""
        try:
            # More robust loop detection - track call depth
            if hasattr(self, "_theme_change_depth"):
                self._theme_change_depth += 1
            else:
                self._theme_change_depth = 1

            # Prevent deep recursion
            if self._theme_change_depth > 3:
                self.logger.error(
                    f"Theme change depth too high ({self._theme_change_depth}) - preventing loop"
                )
                return

            from PySide6.QtWidgets import QApplication

            app = QApplication.instance()
            if app and isinstance(app, QApplication):
                success = apply_theme(theme_name, app)
                if success:
                    # Update dialog styling to match new theme
                    if theme_name == "Dark":
                        self._apply_dark_theme()
                    else:
                        self._apply_light_theme()

                    # Update GroupBox styling
                    self._update_group_box_styling(theme_name)

                    # Update theme description based on selection
                    self._update_theme_description(theme_name)

                    # Force update of the dialog
                    self.update()
                    self.repaint()

                    # Update all segmented controls to match the new theme
                    self._update_all_segmented_controls(theme_name)

                    # Don't update main window preview during initialization
                    # This prevents overriding the font size that was just set
                    # Main window preview will be updated when user actually changes theme

                    self.logger.info(f"Theme preview applied: {theme_name}")
                else:
                    self.logger.error(f"Failed to apply theme preview: {theme_name}")

        except Exception as e:
            self.logger.error(f"Error applying theme preview: {e}")
        finally:
            # Reduce call depth
            if hasattr(self, "_theme_change_depth"):
                self._theme_change_depth = max(0, self._theme_change_depth - 1)

    def _update_all_segmented_controls(self, theme_name: str) -> None:
        """Update all segmented controls to match the current theme"""
        try:
            # Update mode selection segmented control
            if hasattr(self, "segmented_control"):
                self.segmented_control.force_color_update()

            # Update theme selection segmented control
            if hasattr(self, "theme_control"):
                self.theme_control.force_color_update()

            # Update font size selector
            if hasattr(self, "font_size_selector"):
                self.font_size_selector.force_color_update()

            self.logger.debug(f"Updated all segmented controls for theme: {theme_name}")
        except Exception as e:
            self.logger.error(f"Error updating segmented controls: {e}")

    def _update_theme_description(self, theme_name: str) -> None:
        """Update theme description based on selected theme"""
        descriptions = {
            "Light": "Clean, bright interface with high contrast",
            "Dark": "Easy on the eyes with reduced brightness",
            "System": "Follows your operating system preference",
        }
        description = descriptions.get(theme_name, "Choose your preferred theme")
        self.theme_description.setText(description)

    def _update_dialog_theme(self, theme_name: str) -> None:
        """Update dialog styling to match the selected theme"""
        try:
            from ..utils.theme_manager import get_theme_color, get_theme_style

            # Apply dialog theme
            dialog_style = get_theme_style("dialog")
            if dialog_style:
                self.setStyleSheet(dialog_style)

            # Apply tab widget theme
            tab_style = get_theme_style("tab_widget")
            if tab_style:
                self.tab_widget.setStyleSheet(tab_style)

            # Apply group box styling
            group_box_style = get_theme_style("group_box")
            if group_box_style:
                # Apply to all group boxes in the dialog
                for child in self.findChildren(QGroupBox):
                    child.setStyleSheet(group_box_style)

            # Apply button styling
            primary_button_style = get_theme_style("button_primary")
            secondary_button_style = get_theme_style("button_secondary")

            if primary_button_style and hasattr(self, "ok_button"):
                self.ok_button.setStyleSheet(primary_button_style)

            if secondary_button_style:
                if hasattr(self, "cancel_button"):
                    self.cancel_button.setStyleSheet(secondary_button_style)
                if hasattr(self, "reset_button"):
                    self.reset_button.setStyleSheet(secondary_button_style)

            # Update segmented control colors
            if hasattr(self, "segmented_control"):
                self.segmented_control.force_color_update()

            if hasattr(self, "theme_control"):
                self.theme_control.force_color_update()

            # Update font size selector
            if hasattr(self, "font_size_selector"):
                self.font_size_selector.force_color_update()

        except Exception as e:
            self.logger.error(f"Error updating dialog theme: {e}")

    def load_current_settings(self):
        """Load current settings from config"""
        try:
            self.current_settings = get_all_settings(self.environment)
            self.original_settings = self.current_settings.copy()

            # Reset loop detection when loading settings
            self._reset_loop_detection()

            self.logger.info(f"Current settings loaded: {self.current_settings}")

            # Initialize UI controls with loaded settings
            self._initialize_ui_controls()

        except Exception as e:
            self.logger.error(f"Error loading current settings: {e}")
            # Set defaults if loading fails
            self.current_settings = {
                "user_mode": get_text("modes.sign_translate.name"),
                "theme": "Light",
                "font_size": 12,
            }
            self.original_settings = self.current_settings.copy()
            self._initialize_ui_controls()

    def _initialize_ui_controls(self):
        """Initialize UI controls with current settings"""
        try:
            # Set mode
            saved_mode = self.current_settings.get("user_mode", self.current_mode)
            self.segmented_control.set_selection(saved_mode)

            # Set theme
            saved_theme = self.current_settings.get("theme", "Light")
            self.theme_control.set_selection(saved_theme)

            # Set font size
            saved_font_size = self.current_settings.get("font_size", 12)
            self.font_size_selector.set_size(saved_font_size)

            # Set hand preference
            saved_hand_preference = self.current_settings.get(
                "hand_preference", "right"
            )
            if saved_hand_preference == "left":
                self.left_hand_radio.setChecked(True)
            else:
                self.right_hand_radio.setChecked(True)

            # Update description
            self.update_description(saved_mode)

            # Apply tab bar styling after settings are loaded
            self._apply_tab_bar_styling(saved_font_size)

            # Ensure all controls are enabled
            self._enable_all_controls()

        except Exception as e:
            self.logger.error(f"Error initializing UI controls: {e}")

    def setup_behavior(self):
        """Set up dialog behavior"""
        # Connect segmented control signal
        self.segmented_control.selection_changed.connect(self.update_description)

        # Connect theme control for real-time preview
        self.theme_control.selection_changed.connect(self._on_theme_changed)

        # Connect font size selector for real-time preview
        self.font_size_selector.size_changed.connect(self._on_font_size_changed)

        # Connect buttons
        self.reset_button.clicked.connect(self.reset_to_defaults)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self.apply_settings)

    def update_description(self, mode: str):
        """Update the description based on selected mode"""
        if mode == get_text("modes.sign_translate.name"):
            description = "Convert text to sign language symbols and gestures"
        else:  # Learn Sign Language
            description = (
                "Educational mode for learning sign language vocabulary and grammar"
            )

        self.description_label.setText(description)

    def reset_to_defaults(self):
        """Reset theme and font size to default values, keeping current mode unchanged"""
        try:
            # Keep current mode unchanged
            current_mode = self.segmented_control.get_selection()

            # Reset only theme, font size, and hand preference to default values
            default_theme = "Light"
            default_font_size = 12
            default_hand_preference = "right"

            # Update UI controls (only theme, font size, and hand preference)
            self.theme_control.set_selection(default_theme)
            self.font_size_selector.set_size(default_font_size)
            self.right_hand_radio.setChecked(True)  # Default to right hand

            # Update current settings (keep current mode)
            self.current_settings = {
                "user_mode": current_mode,
                "theme": default_theme,
                "font_size": default_font_size,
                "hand_preference": default_hand_preference,
            }

            # Apply changes immediately for preview
            self.update_description(current_mode)
            self._on_theme_changed(default_theme)
            self._on_font_size_changed(default_font_size)
            self._apply_tab_bar_styling(default_font_size)

            self.logger.info(
                f"Settings reset to defaults (mode kept as: {current_mode})"
            )
        except Exception as e:
            self.logger.error(f"Error resetting to defaults: {e}")

    def apply_settings(self):
        """Apply and save the current settings"""
        try:
            # Prevent infinite loops
            if hasattr(self, "_applying_settings") and self._applying_settings:
                self.logger.debug("Settings already being applied, skipping")
                return

            if hasattr(self, "_save_call_depth") and self._save_call_depth >= 3:
                self.logger.error(
                    "Save call depth too high (3) - preventing infinite loop"
                )
                return

            # Set flags to prevent loops
            self._applying_settings = True
            if not hasattr(self, "_save_call_depth"):
                self._save_call_depth = 0
            self._save_call_depth += 1

            # Set main window flag to prevent loops
            if hasattr(self, "main_window") and self.main_window:
                self.main_window._settings_save_in_progress = True

            # Get current settings
            hand_preference = "left" if self.left_hand_radio.isChecked() else "right"
            new_settings = {
                "user_mode": self.segmented_control.get_selection(),
                "theme": self.theme_control.get_selection(),
                "font_size": self.font_size_selector.get_size(),
                "hand_preference": hand_preference,
            }

            self.logger.info(
                f"Saving settings (depth {self._save_call_depth}): {new_settings}"
            )

            # Save settings
            if save_all_settings(new_settings, self.environment):
                # Update original settings to current state
                self.original_settings = new_settings.copy()

                # Emit signal with new mode
                self.settings_applied.emit(new_settings["user_mode"])

                self.logger.info(f"Settings saved successfully: {new_settings}")

                # Close dialog after a small delay to ensure save completes
                from PySide6.QtCore import QTimer

                QTimer.singleShot(100, self._close_dialog_after_save)

            else:
                # Only show error dialog if not in test environment
                import sys

                if (
                    "pytest" not in sys.modules
                    and "test" not in self.environment.lower()
                ):
                    from PySide6.QtWidgets import QMessageBox

                    QMessageBox.critical(
                        self,
                        "Error",
                        "Failed to save settings. Please try again.",
                        QMessageBox.StandardButton.Ok,
                    )
                self.logger.error("Failed to save settings")
        except Exception as e:
            self.logger.error(f"Error applying settings: {e}")
            # Only show error dialog if not in test environment
            import sys

            if "pytest" not in sys.modules and "test" not in self.environment.lower():
                from PySide6.QtWidgets import QMessageBox

                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error applying settings: {e}",
                    QMessageBox.StandardButton.Ok,
                )
        finally:
            # Clear the applying settings flag and reduce call depth
            self._applying_settings = False
            if hasattr(self, "_save_call_depth"):
                self._save_call_depth = max(0, self._save_call_depth - 1)

            # Clear the main window flag
            if hasattr(self, "main_window") and self.main_window:
                self.main_window._settings_save_in_progress = False

    def _close_dialog_after_save(self):
        """Close the dialog after settings have been saved"""
        try:
            self.logger.debug("Closing dialog after successful save")
            self.close()
        except Exception as e:
            self.logger.error(f"Error closing dialog after save: {e}")
            # Fallback to accept if close fails
            try:
                self.accept()
            except Exception as e2:
                self.logger.error(f"Error accepting dialog: {e2}")

    def get_selected_mode(self) -> str:
        """Get the currently selected mode"""
        return self.segmented_control.get_selection()

    def closeEvent(self, event):
        """Handle dialog close event"""
        try:
            self.logger.info("Settings dialog closed - restoring original settings")

            # Restore original settings if dialog wasn't accepted
            if not hasattr(self, "_accepted"):
                self._restore_original_settings()

            # Clean up theme preview
            self._cleanup_theme_preview()

            # Accept the close event
            event.accept()
        except Exception as e:
            self.logger.error(f"Error in closeEvent: {e}")
            event.accept()

    def _cleanup_theme_preview(self):
        """Clean up theme preview - simplified to prevent conflicts"""
        try:
            # Don't restore theme automatically - let the main app handle it
            self.logger.debug("Theme preview cleanup completed")
        except Exception as e:
            self.logger.error(f"Error cleaning up theme preview: {e}")

    def reject(self):
        """Handle dialog rejection (Cancel button or ESC key)"""
        try:
            self.logger.info("Settings dialog cancelled - restoring original settings")

            # Restore original settings
            self._restore_original_settings()

            # Close dialog
            super().reject()
        except Exception as e:
            self.logger.error(f"Error rejecting settings dialog: {e}")
            super().reject()

    def _restore_original_settings(self):
        """Restore original settings and apply them"""
        try:
            # Restore original theme
            original_theme = self.original_settings.get("theme", "Light")
            self._on_theme_changed(original_theme)

            # Restore original font size
            original_font_size = self.original_settings.get("font_size", 12)
            self._on_font_size_changed(original_font_size)
            self._apply_tab_bar_styling(original_font_size)

            # Restore original mode
            original_mode = self.original_settings.get("user_mode", "Sign & Translate")
            self.update_description(original_mode)

            self.logger.info("Original settings restored")
        except Exception as e:
            self.logger.error(f"Error restoring original settings: {e}")

    def accept(self):
        """Handle dialog acceptance (Save Changes button)"""
        try:
            # Mark dialog as accepted to prevent any further font size updates
            self._accepted = True

            # Apply settings (this will save and close)
            self.apply_settings()

            # Ensure dialog closes even if apply_settings doesn't call accept
            if not self.isHidden():
                super().accept()

        except Exception as e:
            self.logger.error(f"Error in accept: {e}")
            super().accept()

    def _update_main_window_preview(self, theme_name: str) -> None:
        """Update main window styling for theme preview"""
        try:
            from ..utils.theme_manager import get_theme_style

            # Apply theme styles to main window
            main_window_style = get_theme_style("main_window")
            if main_window_style:
                self.main_window.setStyleSheet(main_window_style)

            # Update input fields
            input_style = get_theme_style("input_field")
            if input_style:
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

            # Update buttons
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

            # Force update of the main window
            self.main_window.update()
            self.main_window.repaint()

            self.logger.debug(f"Main window theme preview updated for: {theme_name}")
        except Exception as e:
            self.logger.error(f"Error updating main window theme preview: {e}")

    def _on_font_size_changed(self, font_size: int) -> None:
        """Handle font size change in real-time"""
        try:
            # Update current settings (but don't save yet)
            self.current_settings["font_size"] = font_size

            # Apply font size preview to both dialog and main window
            self._apply_font_size_preview(font_size)

            # Force the font size selector to update its visual appearance
            self._update_font_size_selector_visual(font_size)

            # Apply tab bar styling for the new font size
            self._apply_tab_bar_styling(font_size)

        except Exception as e:
            self.logger.error(f"Error applying font size preview: {e}")

    def _update_main_window_content_fonts(self, font_size: int) -> None:
        """Update font sizes in the main window content area"""
        try:
            if not self.main_window:
                return

            from PySide6.QtGui import QFont
            from PySide6.QtWidgets import (
                QButtonGroup,
                QLabel,
                QLineEdit,
                QPushButton,
                QTabBar,
                QTabWidget,
                QTextEdit,
                QWidget,
            )

            from ..utils.theme_manager import get_theme_manager

            # Update the theme manager's font size first
            theme_manager = get_theme_manager()
            theme_manager.set_font_size(font_size)

            # Create a new font with the specified size
            new_font = QFont()
            new_font.setPointSize(font_size)

            # Get all child widgets from the main window
            all_widgets = self.main_window.findChildren(QWidget)

            updated_count = 0
            for widget in all_widgets:
                try:
                    if widget is None or not widget.isVisible():
                        continue

                    # Update font for specific widget types in the main window
                    if isinstance(widget, (QLabel, QLineEdit, QPushButton, QTextEdit)):
                        widget.setFont(new_font)
                        # Force theme manager to update this widget's stylesheet
                        if isinstance(widget, QLabel):
                            theme_manager.force_font_size_update(widget, "label")
                        elif isinstance(widget, QLineEdit):
                            theme_manager.force_font_size_update(widget, "input_field")
                        elif isinstance(widget, QPushButton):
                            theme_manager.force_font_size_update(
                                widget, "button_primary"
                            )
                        elif isinstance(widget, QTextEdit):
                            theme_manager.force_font_size_update(widget, "input_field")
                        updated_count += 1
                        self.logger.debug(
                            f"Updated main window content font for {widget.__class__.__name__} to {font_size}px"
                        )
                    elif isinstance(widget, QTabWidget):
                        # For tab widgets, update the tab bar font
                        if hasattr(widget, "tabBar"):
                            tab_bar = widget.tabBar()
                            tab_bar.setFont(new_font)
                            theme_manager.force_font_size_update(tab_bar, "tab_widget")
                            updated_count += 1
                            self.logger.debug(
                                f"Updated main window content font for QTabBar to {font_size}px"
                            )
                    elif isinstance(widget, QTabBar):
                        # Direct tab bar widgets
                        widget.setFont(new_font)
                        theme_manager.force_font_size_update(widget, "tab_widget")
                        updated_count += 1
                        self.logger.debug(
                            f"Updated main window content font for QTabBar to {font_size}px"
                        )
                    elif isinstance(widget, QButtonGroup):
                        # Button groups - update all buttons in the group
                        for button in widget.buttons():
                            if button.isVisible():
                                button.setFont(new_font)
                                theme_manager.force_font_size_update(
                                    button, "button_primary"
                                )
                                updated_count += 1
                                self.logger.debug(
                                    f"Updated main window content font for QButtonGroup button to {font_size}px"
                                )

                except Exception as widget_error:
                    # Continue with other widgets if one fails
                    self.logger.warning(
                        f"Error updating main window widget {widget.__class__.__name__}: {widget_error}"
                    )
                    continue

            self.logger.debug(
                f"Main window content font updates applied to {updated_count} widgets"
            )

            # Force immediate repaint of the main window
            self.main_window.update()
            self.main_window.repaint()
            QCoreApplication.processEvents()

        except Exception as e:
            self.logger.error(f"Error updating main window content fonts: {e}")

    def _update_font_size_selector_visual(self, font_size: int) -> None:
        """Update the visual appearance of the font size selector"""
        try:
            if hasattr(self, "font_size_selector"):
                # Update the font size selector's current size
                self.font_size_selector.set_size(font_size)

                # Force the font size selector to repaint
                self.font_size_selector.update()
                self.font_size_selector.repaint()

                # Also force the parent dialog to repaint
                self.update()
                self.repaint()

                # Force Qt to process all pending events
                QCoreApplication.processEvents()

                self.logger.debug(
                    f"Font size selector visual updated to: {font_size}px"
                )
        except Exception as e:
            self.logger.error(f"Error updating font size selector visual: {e}")

    def _apply_font_size_preview(self, font_size: int) -> None:
        """Apply font size preview to both settings dialog and main window"""
        try:
            # Update the font size selector visual
            self._update_font_size_selector_visual(font_size)

            # Preview the font size changes
            self._preview_font_size(font_size)

            self.logger.debug(f"Font size preview applied: {font_size}px")
        except Exception as e:
            self.logger.error(f"Error applying font size preview: {e}")

    def _update_dialog_font_size(self, font_size: int) -> None:
        """Update dialog font size using centralized system"""
        try:
            # Don't apply font size if dialog is being closed, accepted, or applying settings
            if (
                hasattr(self, "_accepted")
                or hasattr(self, "_applying_settings")
                or not self.isVisible()
                or self.isHidden()
            ):
                return

            # Check if dialog is being destroyed
            if hasattr(self, "isDestroyed") and self.isDestroyed():
                return

            from ..utils.theme_manager import apply_font_size_to_widget_tree

            # Apply font size to the entire dialog widget tree
            # Note: set_font_size is already called in _apply_font_size_preview
            apply_font_size_to_widget_tree(self)

            # Also directly update font objects for immediate visual feedback
            self._update_widget_fonts_directly(font_size)

            # Dynamically resize the dialog based on font size
            self._adjust_dialog_size_for_font(font_size)

            # Force the dialog to refresh its appearance
            self.update()
            self.repaint()

            # Force the font size selector to refresh its appearance
            if hasattr(self, "font_size_selector"):
                self.font_size_selector.update()
                self.font_size_selector.repaint()

            self.logger.debug(f"Dialog font size updated to: {font_size}px")

        except Exception as e:
            self.logger.error(f"Error updating dialog font size: {e}")

    def _adjust_dialog_size_for_font(self, font_size: int) -> None:
        """Adjust dialog size based on font size to ensure content fits properly"""
        try:
            # Base size for font size 12
            base_width = 700
            base_height = 550

            # Calculate size multiplier based on font size
            # Font sizes: 10, 12, 14, 16, 18, 20, 22, 24, 26, 28
            size_multiplier = font_size / 12.0

            # Apply multiplier with reasonable bounds
            new_width = int(base_width * size_multiplier)
            new_height = int(base_height * size_multiplier)

            # Ensure minimum and maximum sizes
            new_width = max(600, min(new_width, 1200))
            new_height = max(460, min(new_height, 900))

            # Resize the dialog
            self.resize(new_width, new_height)

            # Ensure the dialog stays on screen
            self._ensure_dialog_on_screen()

            self.logger.debug(
                f"Dialog resized to {new_width}x{new_height} for font size {font_size}"
            )

        except Exception as e:
            self.logger.error(f"Error adjusting dialog size: {e}")

    def _ensure_dialog_on_screen(self) -> None:
        """Ensure the dialog stays within screen bounds"""
        try:
            from PySide6.QtWidgets import QApplication

            # Get screen geometry
            screen = QApplication.primaryScreen()
            screen_geometry = screen.geometry()

            # Get current dialog geometry
            dialog_geometry = self.geometry()

            # Check if dialog is outside screen bounds
            if dialog_geometry.right() > screen_geometry.right():
                # Move dialog left
                new_x = screen_geometry.right() - dialog_geometry.width()
                dialog_geometry.moveLeft(new_x)

            if dialog_geometry.bottom() > screen_geometry.bottom():
                # Move dialog up
                new_y = screen_geometry.bottom() - dialog_geometry.height()
                dialog_geometry.moveTop(new_y)

            if dialog_geometry.left() < screen_geometry.left():
                # Move dialog right
                dialog_geometry.moveLeft(screen_geometry.left())

            if dialog_geometry.top() < screen_geometry.top():
                # Move dialog down
                dialog_geometry.moveTop(screen_geometry.top())

            # Apply the adjusted geometry
            self.setGeometry(dialog_geometry)

        except Exception as e:
            self.logger.error(f"Error ensuring dialog on screen: {e}")

    def _update_widget_fonts_directly(self, font_size: int) -> None:
        """Directly update font objects of widgets for immediate visual feedback"""
        try:
            # Check if dialog is being destroyed
            if hasattr(self, "isDestroyed") and self.isDestroyed():
                return

            from PySide6.QtGui import QFont
            from PySide6.QtWidgets import (
                QButtonGroup,
                QGroupBox,
                QLabel,
                QPushButton,
                QTabBar,
                QTabWidget,
                QWidget,
            )

            from ..utils.theme_manager import get_theme_manager

            # Update the theme manager's font size first
            theme_manager = get_theme_manager()
            theme_manager.set_font_size(font_size)

            # Create a new font with the specified size
            new_font = QFont()
            new_font.setPointSize(font_size)

            # Get all child widgets
            all_widgets = self.findChildren(QWidget)

            updated_count = 0
            for widget in all_widgets:
                try:
                    # Check if widget is being destroyed
                    if hasattr(widget, "isDestroyed") and widget.isDestroyed():
                        continue

                    if widget is None or not widget.isVisible():
                        continue

                    # Update font for specific widget types that should show font size changes
                    if isinstance(widget, (QLabel, QPushButton, QGroupBox)):
                        # Set the font directly
                        widget.setFont(new_font)
                        # Force theme manager to update this widget's stylesheet
                        if isinstance(widget, QLabel):
                            theme_manager.force_font_size_update(widget, "label")
                        elif isinstance(widget, QPushButton):
                            theme_manager.force_font_size_update(
                                widget, "button_primary"
                            )
                        elif isinstance(widget, QGroupBox):
                            theme_manager.force_font_size_update(widget, "group_box")
                        updated_count += 1
                        self.logger.debug(
                            f"Updated font for {widget.__class__.__name__} to {font_size}px"
                        )
                    elif isinstance(widget, QTabWidget):
                        # For tab widgets, update the tab bar font and adjust height
                        if hasattr(widget, "tabBar"):
                            tab_bar = widget.tabBar()
                            tab_bar.setFont(new_font)

                            # Use the new tab bar styling method
                            self._apply_tab_bar_styling(font_size)

                            theme_manager.force_font_size_update(tab_bar, "tab_widget")
                            updated_count += 1
                            self.logger.debug(
                                f"Updated font for QTabWidget to {font_size}px"
                            )
                    elif isinstance(widget, QTabBar):
                        # Direct tab bar widgets
                        widget.setFont(new_font)

                        # Use the new tab bar styling method
                        self._apply_tab_bar_styling(font_size)

                        theme_manager.force_font_size_update(widget, "tab_widget")
                        updated_count += 1
                        self.logger.debug(
                            f"Updated font for direct QTabBar to {font_size}px"
                        )
                    elif isinstance(widget, QButtonGroup):
                        # Button groups - update all buttons in the group
                        for button in widget.buttons():
                            if button.isVisible():
                                button.setFont(new_font)
                                theme_manager.force_font_size_update(
                                    button, "button_primary"
                                )
                                updated_count += 1
                                self.logger.debug(
                                    f"Updated font for QButtonGroup button to {font_size}px"
                                )

                except Exception as widget_error:
                    # Continue with other widgets if one fails
                    self.logger.warning(
                        f"Error updating widget {widget.__class__.__name__}: {widget_error}"
                    )
                    continue

            self.logger.debug(f"Direct font updates applied to {updated_count} widgets")

            # Force immediate repaint of the dialog
            self.update()
            self.repaint()

        except Exception as e:
            self.logger.error(f"Error updating widget fonts directly: {e}")

    def _apply_tab_bar_styling(self, font_size: int) -> None:
        """Apply tab bar styling based on the current font size"""
        try:
            # Get the tab bar from the tab widget
            tab_bar = self.tab_widget.tabBar()

            # Calculate padding based on font size
            base_padding = 8
            padding_multiplier = font_size / 12.0
            padding = int(base_padding * padding_multiplier)
            # Ensure minimum padding for usability
            padding = max(4, padding)

            # Get current theme for proper colors
            from ..utils.theme_manager import get_theme_manager

            theme_manager = get_theme_manager()
            current_theme = theme_manager.get_current_theme()

            if current_theme == "Dark":
                # Dark theme tab bar styling
                tab_bar.setStyleSheet(
                    f"""
                    QTabBar::tab {{
                        background-color: #374151;
                        color: #d1d5db;
                        padding: {padding}px {padding * 2}px;
                        margin-right: 2px;
                        border: none;
                        border-radius: 4px;
                        font-size: {font_size}px;
                        min-height: {font_size + 4}px;
                    }}
                    QTabBar::tab:selected {{
                        background-color: #3b82f6;
                        color: #ffffff;
                    }}
                    QTabBar::tab:hover {{
                        background-color: #4b5563;
                    }}
                """
                )
            else:
                # Light theme tab bar styling
                tab_bar.setStyleSheet(
                    f"""
                    QTabBar::tab {{
                        background-color: #f3f4f6;
                        color: #374151;
                        padding: {padding}px {padding * 2}px;
                        margin-right: 2px;
                        border: none;
                        border-radius: 4px;
                        font-size: {font_size}px;
                        min-height: {font_size + 4}px;
                    }}
                    QTabBar::tab:selected {{
                        background-color: #3b82f6;
                        color: #ffffff;
                    }}
                    QTabBar::tab:hover {{
                        background-color: #e5e7eb;
                    }}
                """
                )

            self.logger.debug(f"Applied tab bar styling for font size {font_size}px")

        except Exception as e:
            self.logger.error(f"Error applying tab bar styling: {e}")

    def _update_main_window_font_size(self, font_size: int) -> None:
        """Update main window font size using centralized system"""
        try:
            # Don't apply font size if dialog is being closed, accepted, applying settings, or main window is not available
            if (
                hasattr(self, "_accepted")
                or hasattr(self, "_applying_settings")
                or not self.main_window
                or not self.main_window.isVisible()
                or self.main_window.isHidden()
            ):
                return

            from ..utils.theme_manager import apply_font_size_to_widget_tree

            # Apply font size to the entire main window widget tree
            # Note: set_font_size is already called in _apply_font_size_preview
            apply_font_size_to_widget_tree(self.main_window)

            # Also directly update font objects for immediate visual feedback
            self._update_main_window_fonts_directly(font_size)

            self.logger.debug(f"Main window font size updated to: {font_size}px")

        except Exception as e:
            self.logger.error(f"Error updating main window font size: {e}")

    def _update_main_window_fonts_directly(self, font_size: int) -> None:
        """Directly update font objects of main window widgets for immediate visual feedback"""
        try:
            # Don't apply font size if dialog is being closed, accepted, applying settings, or main window is not available
            if (
                hasattr(self, "_accepted")
                or hasattr(self, "_applying_settings")
                or not self.main_window
                or not self.main_window.isVisible()
                or self.main_window.isHidden()
            ):
                return

            from PySide6.QtGui import QFont
            from PySide6.QtWidgets import (
                QLabel,
                QLineEdit,
                QPushButton,
                QTabBar,
                QTextEdit,
                QWidget,
            )

            from ..utils.theme_manager import get_theme_manager

            # Update the theme manager's font size first
            theme_manager = get_theme_manager()
            theme_manager.set_font_size(font_size)

            # Create a new font with the specified size
            new_font = QFont()
            new_font.setPointSize(font_size)

            # Get all child widgets from the main window
            all_widgets = self.main_window.findChildren(QWidget)

            updated_count = 0
            for widget in all_widgets:
                try:
                    # Check if widget is being destroyed
                    if hasattr(widget, "isDestroyed") and widget.isDestroyed():
                        continue

                    if widget is None or not widget.isVisible():
                        self.logger.debug(
                            f"Skipping invisible widget: {widget.__class__.__name__}"
                        )
                        continue

                    # Update font for specific widget types that should show font size changes
                    if isinstance(widget, (QLabel, QLineEdit, QPushButton, QTextEdit)):
                        # Set the font directly
                        widget.setFont(new_font)
                        # Force theme manager to update this widget's stylesheet
                        if isinstance(widget, QLabel):
                            theme_manager.force_font_size_update(widget, "label")
                        elif isinstance(widget, QLineEdit):
                            theme_manager.force_font_size_update(widget, "input_field")
                        elif isinstance(widget, QPushButton):
                            theme_manager.force_font_size_update(
                                widget, "button_primary"
                            )
                        elif isinstance(widget, QTextEdit):
                            theme_manager.force_font_size_update(widget, "input_field")
                        updated_count += 1
                        self.logger.debug(
                            f"Updated main window content font for {widget.__class__.__name__} to {font_size}px"
                        )

                except Exception as widget_error:
                    # Continue with other widgets if one fails
                    self.logger.warning(
                        f"Error updating main window widget {widget.__class__.__name__}: {widget_error}"
                    )
                    continue

            self.logger.debug(
                f"Main window direct font updates applied to {updated_count} widgets"
            )

        except Exception as e:
            self.logger.error(f"Error updating main window fonts directly: {e}")

    def _preview_font_size(self, font_size: int) -> None:
        """Preview font size changes without saving"""
        try:
            self.logger.debug(f"Font size preview applied: {font_size}px")

            # Update settings dialog fonts directly
            self._update_widget_fonts_directly(font_size)

            # Update main window fonts directly if available
            if self.main_window:
                self._update_main_window_fonts_directly(font_size)

        except Exception as e:
            self.logger.error(f"Error previewing font size: {e}")


def show_settings_dialog(
    parent=None,
    current_mode: str = "Sign & Translate",
    callback: Optional[Callable[[str], None]] = None,
    environment: str = "dev",
    main_window=None,
) -> Optional[str]:
    """Show the settings dialog and return the selected mode"""
    try:
        if not PYSIDE6_AVAILABLE:
            logger = get_logger("helpmesign.settings")
            logger.error("PySide6 is not available, cannot show settings dialog")
            return None

        dialog = SettingsDialog(parent, current_mode, environment, main_window)

        # Connect the callback if provided
        if callback:
            dialog.settings_applied.connect(callback)

        # Show the dialog non-modally
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

        # Return None immediately since it's non-modal
        # The callback will handle the result when user clicks Save Changes
        return None

    except Exception as e:
        logger = get_logger("helpmesign.settings")
        logger.error(f"Error showing settings dialog: {e}")
        return None
