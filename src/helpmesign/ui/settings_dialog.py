#!/usr/bin/env python3
"""
Settings dialog for HelpMeSign application
Modern, professional design with multiple sections
"""

from typing import Callable, Optional

from PySide6.QtCore import QRect, QSize, Qt, Signal
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

from ..core.startup import get_all_settings, save_all_settings
from ..utils.font_manager import get_body_font, get_button_font, get_heading_font
from ..utils.language_manager import get_dict, get_list, get_text
from ..utils.logger import get_logger
from ..utils.theme_manager import apply_theme, get_theme_manager


class ModernSegmentedControl(QFrame):
    """Modern segmented control widget"""

    selection_changed = Signal(str)

    def __init__(self, options: list[str], parent=None):
        super().__init__(parent)
        self.options = options
        self.selected_index = 0
        self.hover_index = -1
        self.setFixedHeight(40)
        self.setMouseTracking(True)

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

            # Debug logging
            self.logger.debug(
                f"ModernSegmentedControl: Current theme detected as: {current_theme}"
            )

            if current_theme == "Dark":
                # Dark theme colors - dark backgrounds
                self.bg_color = "#1e293b"  # Dark background to match dialog
                self.selected_bg = "#3b82f6"  # Blue for selected
                self.selected_text = "#ffffff"  # White text for selected
                self.unselected_bg = "#334155"  # Dark gray for unselected
                self.unselected_text = "#cbd5e1"  # Light gray text for unselected
                self.hover_bg = "#475569"  # Lighter gray for hover
                self.border_color = "#475569"  # Border color
                self.logger.debug("ModernSegmentedControl: Applied dark theme colors")
            else:
                # Light theme colors - light backgrounds
                self.bg_color = "#ffffff"  # White background to match dialog
                self.selected_bg = "#3b82f6"  # Blue for selected
                self.selected_text = "#ffffff"  # White text for selected
                self.unselected_bg = "#f1f5f9"  # Light gray for unselected
                self.unselected_text = "#64748b"  # Gray text for unselected
                self.hover_bg = "#e2e8f0"  # Light gray for hover
                self.border_color = "#d1d5db"  # Border color
                self.logger.debug("ModernSegmentedControl: Applied light theme colors")
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
            # Update colors based on current theme
            self._update_colors()

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

    def set_selection(self, option: str):
        """Set the selected option"""
        if option in self.options:
            self.selected_index = self.options.index(option)
            self.update()
            self.selection_changed.emit(option)

    def get_selection(self) -> str:
        """Get the currently selected option"""
        return self.options[self.selected_index]


class SettingsDialog(QDialog):
    """Modern settings dialog for user preferences"""

    # Signal emitted when settings are applied
    settings_applied = Signal(str)

    def __init__(
        self,
        parent=None,
        current_mode: str = "Sign & Translate",
        environment: str = "dev",
    ):
        super().__init__(parent)
        self.current_mode = current_mode
        self.environment = environment
        self.current_settings = get_all_settings(environment)
        self.logger = get_logger("helpmesign.settings")

        # Set dialog properties to prevent blocking main app
        self.setModal(False)  # Make it non-modal so CMD+Q works
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        self.setup_ui()
        self.load_current_settings()
        self.setup_behavior()

    def setup_ui(self):
        """Set up the settings dialog UI"""
        # Set window properties
        self.setWindowTitle("Settings")
        self.setFixedSize(600, 460)
        self.setModal(False)

        # Apply initial theme styling
        self._apply_initial_theme()

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header frame (minimal)
        header_frame = QFrame()
        header_frame.setFixedHeight(20)
        header_frame.setContentsMargins(20, 10, 20, 10)
        main_layout.addWidget(header_frame)

        # Content frame
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 0, 20, 20)
        content_layout.setSpacing(20)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_general_tab(), "General")
        self.tab_widget.addTab(self.create_appearance_tab(), "Appearance")
        content_layout.addWidget(self.tab_widget)

        # Footer frame
        footer_frame = QFrame()
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(20, 0, 20, 20)
        footer_layout.setSpacing(12)

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
                background-color: #1e293b;
                color: #f8fafc;
            }
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
            QGroupBox {
                font-weight: 600;
                color: #f8fafc;
                border: 1px solid #475569;
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
            QPushButton#primary {
                background-color: #3b82f6;
                color: white;
                border: none;
            }
            QPushButton#primary:hover {
                background-color: #60a5fa;
            }
            QPushButton#primary:pressed {
                background-color: #2563eb;
            }
            QLabel {
                color: #f8fafc;
            }
            QSlider::groove:horizontal {
                border: 1px solid #475569;
                height: 8px;
                background: #334155;
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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Theme Group
        theme_group = QGroupBox("Theme")
        # Remove hardcoded styling - let theme-based styling take over
        theme_layout = QVBoxLayout(theme_group)
        theme_layout.setContentsMargins(16, 20, 16, 16)
        theme_layout.setSpacing(12)

        # Theme segmented control
        self.theme_control = ModernSegmentedControl(
            ["Light", "Dark", "System"], parent=theme_group
        )
        self.theme_control.setFixedHeight(40)
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
        font_layout.setContentsMargins(16, 20, 16, 16)
        font_layout.setSpacing(12)

        # Font size label
        font_label = QLabel("Adjust text size:")
        # Remove hardcoded styling - let theme-based styling take over
        font_layout.addWidget(font_label)

        # Font size slider
        self.font_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_slider.setRange(10, 20)
        self.font_slider.setValue(12)
        # Remove hardcoded styling - let theme-based styling take over
        font_layout.addWidget(self.font_slider)

        # Font size value label
        self.font_size_label = QLabel("12px")
        # Remove hardcoded styling - let theme-based styling take over
        self.font_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_layout.addWidget(self.font_size_label)

        # Connect font slider
        self.font_slider.valueChanged.connect(
            lambda value: self.font_size_label.setText(f"{value}px")
        )

        # Connect theme control for real-time preview
        self.theme_control.selection_changed.connect(self._on_theme_changed)

        layout.addWidget(theme_group)
        layout.addWidget(font_group)
        layout.addStretch()
        return tab

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

                    self.logger.info(f"Theme preview applied: {theme_name}")
                else:
                    self.logger.error(f"Failed to apply theme preview: {theme_name}")

        except Exception as e:
            self.logger.error(f"Error applying theme preview: {e}")

    def _update_all_segmented_controls(self, theme_name: str) -> None:
        """Update all segmented controls to match the current theme"""
        try:
            # Update mode selection segmented control
            if hasattr(self, "segmented_control"):
                self.segmented_control._update_colors()
                self.segmented_control.update()
                self.segmented_control.repaint()

            # Update theme selection segmented control
            if hasattr(self, "theme_control"):
                self.theme_control._update_colors()
                self.theme_control.update()
                self.theme_control.repaint()

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
                self.segmented_control._update_colors()
                self.segmented_control.update()

            if hasattr(self, "theme_control"):
                self.theme_control._update_colors()
                self.theme_control.update()

        except Exception as e:
            self.logger.error(f"Error updating dialog theme: {e}")

    def load_current_settings(self):
        """Load current settings and initialize UI controls"""
        # Set mode
        saved_mode = self.current_settings.get("user_mode", self.current_mode)
        self.segmented_control.set_selection(saved_mode)

        # Set theme
        saved_theme = self.current_settings.get("theme", "Light")
        self.theme_control.set_selection(saved_theme)

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
        self.theme_control.set_selection("Light")
        self.font_slider.setValue(12)
        self.font_size_label.setText("12px")

        # Update description
        self.update_description(default_mode)

    def apply_settings(self):
        """Apply the current settings and save to config"""
        # Collect all current settings
        new_settings = {
            "user_mode": self.segmented_control.get_selection(),
            "theme": self.theme_control.get_selection(),
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
                QMessageBox.StandardButton.Ok,
            )

    def get_selected_mode(self) -> str:
        """Get the currently selected mode"""
        return self.segmented_control.get_selection()

    def closeEvent(self, event):
        """Handle dialog close event properly"""
        try:
            # Simple cleanup without theme restoration to prevent conflicts
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
            # Simple rejection without theme restoration
            super().reject()
        except Exception as e:
            self.logger.error(f"Error in reject: {e}")
            super().reject()

    def accept(self):
        """Handle dialog acceptance (Save Changes button)"""
        try:
            # No cleanup needed here as we're applying the new settings
            super().accept()
        except Exception as e:
            self.logger.error(f"Error in accept: {e}")
            super().accept()


def show_settings_dialog(
    parent=None,
    current_mode: str = "Sign & Translate",
    callback: Optional[Callable[[str], None]] = None,
    environment: str = "dev",
) -> Optional[str]:
    """Show the settings dialog and return the selected mode"""
    try:
        dialog = SettingsDialog(parent, current_mode, environment)

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
        logger.error(f"Error creating settings dialog: {e}")
        return None
