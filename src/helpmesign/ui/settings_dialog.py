#!/usr/bin/env python3
"""
Settings dialog for HelpMeSign application
Follows macOS design patterns
"""

from typing import Callable, Optional

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QVBoxLayout,
)

from ..utils.font_manager import get_body_font, get_button_font, get_heading_font
from ..utils.language_manager import get_dict, get_list, get_text


class SegmentedControl(QFrame):
    """Custom segmented control widget for mode selection"""

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
        self.setMinimumHeight(50)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)

    def setup_style(self):
        """Set up the visual style"""
        self.setStyleSheet(
            """
            SegmentedControl {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                padding: 4px;
            }
        """
        )

    def paintEvent(self, event):
        """Custom paint event for the segmented control"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get widget dimensions
        width = self.width()
        height = self.height()

        # Calculate segment dimensions
        segment_width = (width - 8) // len(self.options)
        segment_height = height - 8

        # Draw segments
        for i, option in enumerate(self.options):
            x = 4 + i * segment_width
            y = 4

            # Determine colors based on state
            if i == self.selected_index:
                # Selected segment - business blue
                bg_color = QColor("#2563eb")
                text_color = QColor("#ffffff")
            elif i == self.hover_index:
                # Hover segment - light blue
                bg_color = QColor("#dbeafe")
                text_color = QColor("#1e40af")
            else:
                # Normal segment - light gray
                bg_color = QColor("#f8fafc")
                text_color = QColor("#64748b")

            # Draw segment background
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(QColor("#e2e8f0"), 1))
            painter.drawRoundedRect(x, y, segment_width, segment_height, 6, 6)

            # Draw text
            painter.setPen(QPen(text_color))
            font = get_body_font()
            font.setPointSize(10)
            painter.setFont(font)

            # Center text in segment
            text_rect = painter.boundingRect(
                x, y, segment_width, segment_height, Qt.AlignCenter, option
            )
            painter.drawText(text_rect, Qt.AlignCenter, option)

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            self.handle_click(event.pos())

    def mouseMoveEvent(self, event):
        """Handle mouse move events for hover effects"""
        self.handle_hover(event.pos())

    def handle_click(self, pos):
        """Handle click events to change selection"""
        width = self.width()
        segment_width = (width - 8) // len(self.options)

        for i in range(len(self.options)):
            x = 4 + i * segment_width
            if x <= pos.x() <= x + segment_width:
                if i != self.selected_index:
                    self.selected_index = i
                    self.selection_changed.emit(self.options[i])
                    self.update()  # Trigger repaint
                break

    def handle_hover(self, pos):
        """Handle hover events"""
        width = self.width()
        segment_width = (width - 8) // len(self.options)

        new_hover_index = -1
        for i in range(len(self.options)):
            x = 4 + i * segment_width
            if x <= pos.x() <= x + segment_width:
                new_hover_index = i
                break

        if new_hover_index != self.hover_index:
            self.hover_index = new_hover_index
            self.update()  # Trigger repaint

    def leaveEvent(self, event):
        """Handle mouse leave events"""
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
    """Settings dialog for user preferences"""

    # Signal emitted when settings are applied
    settings_applied = Signal(str)

    def __init__(self, parent=None, current_mode: str = "Sign & Translate"):
        super().__init__(parent)
        self.current_mode = current_mode
        self.setup_ui()
        self.setup_behavior()

    def setup_ui(self):
        """Set up the settings dialog UI"""
        self.setWindowTitle(get_text("settings.title"))
        self.setModal(True)
        self.setFixedSize(400, 300)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Title
        title_label = QLabel(get_text("settings.title"))
        title_label.setFont(get_heading_font())
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Mode selection section
        mode_label = QLabel(get_text("settings.mode_label"))
        mode_label.setFont(get_body_font())
        layout.addWidget(mode_label)

        # Segmented control for mode selection
        self.segmented_control = SegmentedControl()
        self.segmented_control.set_selection(self.current_mode)
        layout.addWidget(self.segmented_control)

        # Description
        self.description_label = QLabel()
        self.description_label.setFont(get_body_font())
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.description_label)

        # Update description based on current selection
        self.update_description(self.current_mode)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # OK button
        self.ok_button = QPushButton(get_text("settings.buttons.ok"))
        self.ok_button.setFont(get_button_font())
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.ok_button)

        # Cancel button
        self.cancel_button = QPushButton(get_text("settings.buttons.cancel"))
        self.cancel_button.setFont(get_button_font())
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        button_layout.addStretch()  # Push buttons to the right
        layout.addLayout(button_layout)

        # Add stretch to push content to the top
        layout.addStretch()

    def setup_behavior(self):
        """Set up dialog behavior"""
        # Connect segmented control signal
        self.segmented_control.selection_changed.connect(self.update_description)

        # Set focus to OK button
        self.ok_button.setFocus()

    def update_description(self, mode: str):
        """Update the description based on selected mode"""
        if mode == get_text("modes.sign_translate.name"):
            description = get_text("modes.sign_translate.description")
        else:  # Learn Sign Language
            description = get_text("modes.learn.description")

        self.description_label.setText(description)

    def apply_settings(self):
        """Apply the current settings"""
        selected_mode = self.segmented_control.get_selection()
        self.settings_applied.emit(selected_mode)
        self.accept()

    def get_selected_mode(self) -> str:
        """Get the currently selected mode"""
        return self.segmented_control.get_selection()


def show_settings_dialog(
    parent=None,
    current_mode: str = "Sign & Translate",
    callback: Optional[Callable[[str], None]] = None,
) -> Optional[str]:
    """
    Show the settings dialog

    Args:
        parent: Parent widget
        current_mode: Currently selected mode
        callback: Optional callback function to call when settings are applied

    Returns:
        Selected mode if dialog was accepted, None if cancelled
    """
    dialog = SettingsDialog(parent, current_mode)

    if callback:
        dialog.settings_applied.connect(callback)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_selected_mode()
    else:
        return None
