#!/usr/bin/env python3
"""
Settings dialog for HelpMeSign application
Modern, professional design with multiple sections
"""

from typing import Callable, Optional

from PySide6.QtCore import QSize, Qt, Signal
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
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..utils.font_manager import get_body_font, get_button_font, get_heading_font
from ..utils.language_manager import get_dict, get_list, get_text
from ..core.startup import get_all_settings, save_all_settings


class ModernSegmentedControl(QFrame):
    """Modern segmented control widget for mode selection"""

    # Signal emitted when selection changes
    selection_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.options = [
            get_text("modes.sign_translate.name"),
            get_text("modes.learn.name"),
        ]
        self.selected_index = 0
        self.hover_index = -1
        self.setup_ui()
        self.setup_style()

    def setup_ui(self):
        """Set up the segmented control UI"""
        self.setMinimumHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMouseTracking(True)

    def setup_style(self):
        """Set up the visual style"""
        self.setStyleSheet(
            """
            ModernSegmentedControl {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 3px;
            }
        """
        )

    def paintEvent(self, event):
        """Custom paint event for the segmented control"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        try:
            # Get widget dimensions
            width = self.width()
            height = self.height()

            # Calculate segment dimensions
            segment_width = (width - 6) // len(self.options)
            segment_height = height - 6

            # Draw segments
            for i, option in enumerate(self.options):
                x = 3 + i * segment_width
                y = 3

                # Determine colors based on state
                if i == self.selected_index:
                    # Selected segment - modern blue
                    bg_color = QColor("#3b82f6")
                    text_color = QColor("#ffffff")
                    border_color = QColor("#2563eb")
                elif i == self.hover_index:
                    # Hover segment - light blue
                    bg_color = QColor("#dbeafe")
                    text_color = QColor("#1e40af")
                    border_color = QColor("#93c5fd")
                else:
                    # Normal segment - transparent
                    bg_color = QColor("#ffffff")
                    text_color = QColor("#64748b")
                    border_color = QColor("#e2e8f0")

                # Draw segment background
                painter.setBrush(QBrush(bg_color))
                painter.setPen(QPen(border_color, 1))
                painter.drawRoundedRect(x, y, segment_width, segment_height, 10, 10)

                # Draw text
                painter.setPen(QPen(text_color))
                font = get_body_font()
                font.setWeight(
                    QFont.Weight.Bold
                    if i == self.selected_index
                    else QFont.Weight.Normal
                )
                painter.setFont(font)

                # Center text in segment
                text_rect = painter.boundingRect(
                    x, y, segment_width, segment_height, Qt.AlignCenter, option
                )
                painter.drawText(text_rect, Qt.AlignCenter, option)
        finally:
            painter.end()

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            self.handle_click(event.pos())

    def mouseMoveEvent(self, event):
        """Handle mouse move events for hover effects"""
        self.handle_hover(event.pos())

    def handle_click(self, pos):
        """Handle click events"""
        width = self.width()
        segment_width = (width - 6) // len(self.options)

        for i in range(len(self.options)):
            x = 3 + i * segment_width
            if x <= pos.x() <= x + segment_width:
                if i != self.selected_index:
                    self.selected_index = i
                    self.selection_changed.emit(self.options[i])
                    self.update()
                break

    def handle_hover(self, pos):
        """Handle hover effects"""
        width = self.width()
        segment_width = (width - 6) // len(self.options)

        hover_index = -1
        for i in range(len(self.options)):
            x = 3 + i * segment_width
            if x <= pos.x() <= x + segment_width:
                hover_index = i
                break

        if hover_index != self.hover_index:
            self.hover_index = hover_index
            self.update()

    def leaveEvent(self, event):
        """Handle leave events"""
        self.hover_index = -1
        self.update()

    def get_selection(self) -> str:
        """Get the currently selected option"""
        return self.options[self.selected_index]

    def set_selection(self, option: str) -> None:
        """Set the selected option"""
        if option in self.options:
            self.selected_index = self.options.index(option)
            self.update()


class SettingsDialog(QDialog):
    """Modern settings dialog for user preferences"""

    # Signal emitted when settings are applied
    settings_applied = Signal(str)

    def __init__(self, parent=None, current_mode: str = "Sign & Translate", environment: str = "dev"):
        super().__init__(parent)
        self.current_mode = current_mode
        self.environment = environment
        self.current_settings = get_all_settings(environment)
        self.setup_ui()
        self.load_current_settings()
        self.setup_behavior()

    def setup_ui(self):
        """Set up the modern settings dialog UI"""
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setFixedSize(600, 460)  # Reduced height since we removed subtitle
        self.setStyleSheet(
            """
            QDialog {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """
        )

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header - simplified without subtitle
        header_frame = QFrame()
        header_frame.setStyleSheet(
            """
            QFrame {
                background-color: #f8fafc;
                border-bottom: 1px solid #e2e8f0;
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }
        """
        )
        header_frame.setFixedHeight(20)  # Minimal height since we removed subtitle

        layout.addWidget(header_frame)

        # Content area with tabs
        content_frame = QFrame()
        content_frame.setStyleSheet(
            """
            QFrame {
                background-color: #ffffff;
            }
        """
        )
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(24)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(
            """
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
        """
        )

        # General tab
        general_tab = self.create_general_tab()
        self.tab_widget.addTab(general_tab, "General")

        # Appearance tab
        appearance_tab = self.create_appearance_tab()
        self.tab_widget.addTab(appearance_tab, "Appearance")

        content_layout.addWidget(self.tab_widget)
        layout.addWidget(content_frame)

        # Footer with buttons
        footer_frame = QFrame()
        footer_frame.setStyleSheet(
            """
            QFrame {
                background-color: #f8fafc;
                border-top: 1px solid #e2e8f0;
                border-bottom-left-radius: 16px;
                border-bottom-right-radius: 16px;
            }
        """
        )
        footer_frame.setFixedHeight(80)

        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(24, 20, 24, 20)
        footer_layout.setSpacing(12)

        # Reset to defaults button
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.setFont(get_button_font())
        self.reset_button.setFixedSize(120, 36)
        self.reset_button.setStyleSheet(
            """
            QPushButton {
                background-color: #f1f5f9;
                color: #64748b;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
                color: #475569;
            }
            QPushButton:pressed {
                background-color: #cbd5e1;
            }
        """
        )
        self.reset_button.clicked.connect(self.reset_to_defaults)
        footer_layout.addWidget(self.reset_button)

        footer_layout.addStretch()

        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFont(get_button_font())
        self.cancel_button.setFixedSize(80, 36)
        self.cancel_button.setStyleSheet(
            """
            QPushButton {
                background-color: #f1f5f9;
                color: #64748b;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
                color: #475569;
            }
            QPushButton:pressed {
                background-color: #cbd5e1;
            }
        """
        )
        self.cancel_button.clicked.connect(self.reject)
        footer_layout.addWidget(self.cancel_button)

        # OK button
        self.ok_button = QPushButton("Save Changes")
        self.ok_button.setFont(get_button_font())
        self.ok_button.setDefault(True)
        self.ok_button.setFixedSize(100, 36)
        self.ok_button.setStyleSheet(
            """
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """
        )
        self.ok_button.clicked.connect(self.apply_settings)
        footer_layout.addWidget(self.ok_button)

        layout.addWidget(footer_frame)

    def create_general_tab(self):
        """Create the General settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Application Mode section
        mode_group = QGroupBox("Application Mode")
        mode_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: 600;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 16px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px 0 8px;
                background-color: #ffffff;
                color: #1e293b;
                font-size: 14px;
            }
        """
        )

        mode_layout = QVBoxLayout(mode_group)
        mode_layout.setContentsMargins(20, 20, 20, 20)
        mode_layout.setSpacing(16)

        # Mode selection label
        mode_label = QLabel("Select your preferred mode:")
        mode_label.setFont(get_body_font())
        mode_label.setStyleSheet("color: #64748b; font-size: 13px; margin-bottom: 4px;")
        mode_layout.addWidget(mode_label)

        # Modern segmented control
        self.segmented_control = ModernSegmentedControl()
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

    def create_appearance_tab(self):
        """Create the Appearance settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Theme section
        theme_group = QGroupBox("Theme")
        theme_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: 600;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 16px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px 0 8px;
                background-color: #ffffff;
                color: #1e293b;
                font-size: 14px;
            }
        """
        )

        theme_layout = QVBoxLayout(theme_group)
        theme_layout.setContentsMargins(20, 20, 20, 20)
        theme_layout.setSpacing(12)

        # Theme selection
        theme_label = QLabel("Choose your preferred theme:")
        theme_label.setFont(get_body_font())
        theme_label.setStyleSheet(
            "color: #64748b; font-size: 13px; font-weight: 500; margin-bottom: 8px;"
        )
        theme_layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        self.theme_combo.setCurrentText("Light")
        self.theme_combo.setFixedHeight(40)
        self.theme_combo.setStyleSheet(
            """
            QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 8px 12px;
                background-color: #ffffff;
                color: #1e293b;
                font-weight: 500;
                font-size: 13px;
                min-width: 200px;
            }
            QComboBox:hover {
                border-color: #94a3b8;
            }
            QComboBox:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #64748b;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background-color: #ffffff;
                selection-background-color: #3b82f6;
                selection-color: #ffffff;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 13px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #f1f5f9;
            }
        """
        )
        theme_layout.addWidget(self.theme_combo)

        # Font size section
        font_group = QGroupBox("Font Size")
        font_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: 600;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 16px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px 0 8px;
                background-color: #ffffff;
                color: #1e293b;
                font-size: 14px;
            }
        """
        )

        font_layout = QVBoxLayout(font_group)
        font_layout.setContentsMargins(20, 20, 20, 20)
        font_layout.setSpacing(16)

        font_label = QLabel("Adjust text size:")
        font_label.setFont(get_body_font())
        font_label.setStyleSheet(
            "color: #64748b; font-size: 13px; font-weight: 500; margin-bottom: 8px;"
        )
        font_layout.addWidget(font_label)

        # Slider container for better styling
        slider_container = QFrame()
        slider_container.setStyleSheet(
            """
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
            }
        """
        )
        slider_layout = QVBoxLayout(slider_container)
        slider_layout.setContentsMargins(16, 16, 16, 16)
        slider_layout.setSpacing(12)

        self.font_slider = QSlider(Qt.Horizontal)
        self.font_slider.setRange(8, 24)
        self.font_slider.setValue(12)
        self.font_slider.setFixedHeight(20)
        self.font_slider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                border: none;
                height: 4px;
                background: #e2e8f0;
                border-radius: 2px;
                margin: 0px;
            }
            QSlider::handle:horizontal {
                background: #3b82f6;
                border: 2px solid #ffffff;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #2563eb;
            }
            QSlider::sub-page:horizontal {
                background: #3b82f6;
                border-radius: 2px;
            }
        """
        )
        slider_layout.addWidget(self.font_slider)

        # Font size display with better styling
        self.font_size_label = QLabel("12px")
        self.font_size_label.setFont(get_body_font())
        self.font_size_label.setAlignment(Qt.AlignCenter)
        self.font_size_label.setStyleSheet(
            """
            QLabel {
                color: #1e293b;
                font-weight: 600;
                font-size: 13px;
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 6px 12px;
                margin-top: 8px;
                max-width: 60px;
            }
        """
        )
        slider_layout.addWidget(self.font_size_label)

        font_layout.addWidget(slider_container)

        # Connect font slider
        self.font_slider.valueChanged.connect(
            lambda value: self.font_size_label.setText(f"{value}px")
        )

        layout.addWidget(theme_group)
        layout.addWidget(font_group)
        layout.addStretch()
        return tab

    def load_current_settings(self):
        """Load current settings and initialize UI controls"""
        # Set mode
        saved_mode = self.current_settings.get("user_mode", self.current_mode)
        self.segmented_control.set_selection(saved_mode)
        
        # Set theme
        saved_theme = self.current_settings.get("theme", "Light")
        self.theme_combo.setCurrentText(saved_theme)
        
        # Set font size
        saved_font_size = self.current_settings.get("font_size", 12)
        self.font_slider.setValue(saved_font_size)
        self.font_size_label.setText(f"{saved_font_size}px")
        
        # Update description
        self.update_description(saved_mode)

    def setup_behavior(self):
        """Set up dialog behavior"""
        # Connect segmented control signal
        self.segmented_control.selection_changed.connect(self.update_description)

        # Set focus to OK button
        self.ok_button.setFocus()

        # Update initial description
        self.update_description(self.current_mode)

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
        """Reset all settings to default values"""
        # Reset mode to Sign & Translate
        default_mode = get_text("modes.sign_translate.name")
        self.segmented_control.set_selection(default_mode)
        
        # Reset appearance settings
        self.theme_combo.setCurrentText("Light")
        self.font_slider.setValue(12)
        self.font_size_label.setText("12px")
        
        # Update description
        self.update_description(default_mode)

    def apply_settings(self):
        """Apply the current settings and save to config"""
        # Collect all current settings
        new_settings = {
            "user_mode": self.segmented_control.get_selection(),
            "theme": self.theme_combo.currentText(),
            "font_size": self.font_slider.value(),
        }
        
        # Save settings to config
        if save_all_settings(new_settings, self.environment):
            # Emit signal with new mode
            self.settings_applied.emit(new_settings["user_mode"])
            self.accept()
        else:
            # Show error message if save failed
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Error",
                "Failed to save settings. Please try again.",
                QMessageBox.StandardButton.Ok
            )

    def get_selected_mode(self) -> str:
        """Get the currently selected mode"""
        return self.segmented_control.get_selection()


def show_settings_dialog(
    parent=None,
    current_mode: str = "Sign & Translate",
    callback: Optional[Callable[[str], None]] = None,
    environment: str = "dev",
) -> Optional[str]:
    """
    Show the modern settings dialog

    Args:
        parent: Parent widget
        current_mode: Currently selected mode
        callback: Optional callback function to call when settings are applied
        environment: Environment to use for settings (dev/prod)

    Returns:
        Selected mode if dialog was accepted, None if cancelled
    """
    dialog = SettingsDialog(parent, current_mode, environment)

    if callback:
        dialog.settings_applied.connect(callback)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_selected_mode()
    else:
        return None
