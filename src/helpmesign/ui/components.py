#!/usr/bin/env python3
"""
UI Components for HelpMeSign Application
"""

import os
import platform
from typing import Callable, Optional

from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..utils.font_manager import (
    get_body_font,
    get_button_font,
    get_input_font,
    get_label_font,
    get_small_font,
)
from ..utils.language_manager import get_dict, get_list, get_text
from ..utils.logger import get_logger


def get_os_shortcuts():
    """Get OS-specific keyboard shortcuts from language configuration"""
    system = platform.system().lower()

    # Map system names to language keys
    system_map = {"darwin": "macos", "windows": "windows", "linux": "linux"}

    # Get the appropriate OS key
    os_key = system_map.get(system, "linux")  # Default to Linux for unknown systems

    # Get shortcuts from language configuration
    shortcuts = get_dict(f"os_shortcuts.{os_key}")

    # Fallback to Linux shortcuts if the specific OS is not found
    if not shortcuts:
        shortcuts = get_dict("os_shortcuts.linux")

    return shortcuts


class TextInputFrame(QWidget):
    """Widget containing text input and processing controls"""

    # Signals
    process_requested = Signal()
    clear_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        """Set up the text input UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Input label
        label = QLabel(get_text("ui.text_input.label"))
        label.setFont(get_label_font())
        layout.addWidget(label)

        # Text input
        self.text_input = QLineEdit()
        self.text_input.setFont(get_input_font())
        self.text_input.setPlaceholderText(get_text("ui.text_input.placeholder_alt"))
        self.text_input.returnPressed.connect(self.process_requested.emit)
        layout.addWidget(self.text_input)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Process button
        self.process_button = QPushButton(get_text("ui.text_input.process_button"))
        self.process_button.setFont(get_button_font())
        self.process_button.clicked.connect(self.process_requested.emit)
        button_layout.addWidget(self.process_button)

        # Clear button
        self.clear_button = QPushButton(get_text("ui.text_input.clear_button"))
        self.clear_button.setFont(get_button_font())
        self.clear_button.clicked.connect(self.clear_requested.emit)
        button_layout.addWidget(self.clear_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def setup_shortcuts(self):
        """Set up keyboard shortcuts"""
        # Process shortcut
        process_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        process_shortcut.activated.connect(self.process_requested.emit)

        # Clear shortcut
        clear_shortcut = QShortcut(QKeySequence("Ctrl+Shift+K"), self)
        clear_shortcut.activated.connect(self.clear_requested.emit)

    def get_text(self) -> str:
        """Get text from input field"""
        return self.text_input.text()

    def set_text(self, text: str) -> None:
        """Set text in input field"""
        self.text_input.setText(text)

    def clear_text(self) -> None:
        """Clear text input"""
        self.text_input.clear()

    def focus_input(self) -> None:
        """Focus on the input field"""
        self.text_input.setFocus()


class OutputFrame(QWidget):
    """Widget containing text output display"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the output UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Output label
        label = QLabel(get_text("ui.output.label"))
        label.setFont(get_label_font())
        layout.addWidget(label)

        # Text output
        self.text_output = QTextEdit()
        self.text_output.setFont(get_body_font())
        self.text_output.setReadOnly(True)
        self.text_output.setPlaceholderText(get_text("ui.output.placeholder"))
        layout.addWidget(self.text_output)

    def add_text(self, text: str) -> None:
        """Add text to output"""
        self.text_output.append(text)

    def clear_text(self) -> None:
        """Clear text output"""
        self.text_output.clear()

    def get_text(self) -> str:
        """Get text from output"""
        return self.text_output.toPlainText()

    def set_text(self, text: str) -> None:
        """Set text in output"""
        self.text_output.setPlainText(text)


class StatusBar(QFrame):
    """Status bar widget with system resource monitoring"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_cleaned_up = False
        self._shutting_down = False
        self.current_mode = get_text("modes.sign_translate.name")
        self.setup_ui()
        self.setup_system_monitor()

    def setup_ui(self):
        """Set up the status bar UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Status label (will show both status and mode) - left side
        self.status_label = QLabel(get_text("ui.status.default"))
        self.status_label.setFont(get_small_font())
        layout.addWidget(self.status_label)

        # Language chip (place it on the right, before resources)
        # We first add a stretch so items after it go to the right side
        layout.addStretch()
        self.language_chip = QPushButton()
        self.language_chip.setObjectName("languageChip")
        self.language_chip.setCursor(Qt.PointingHandCursor)
        self.language_chip.setStyleSheet(
            """
            QPushButton#languageChip {
                border: 1px solid #e0e6ef; border-radius: 6px; background: #ffffff;
                padding: 2px 8px; font-weight: 600;
            }
            QPushButton#languageChip:hover { background: #f5f7fb; }
            """
        )
        self.language_chip.clicked.connect(self._on_language_chip_click)
        # Initialize with saved language
        try:
            from ..core.startup import get_all_settings
            from ..utils.language_loader import get_all_languages

            code = get_all_settings().get("selected_language", "ASL")
            flag = "🌐"
            for lang in get_all_languages():
                if lang.get("code") == code:
                    flag = lang.get("flag", "🌐")
                    break
            self.language_chip.setText(f"{flag} {code}")
        except Exception:
            self.language_chip.setText("🌐 ASL")
        layout.addWidget(self.language_chip)

        # System monitor button on the right side (fixed size)
        self.setup_system_monitor_button()

    def setup_system_monitor_button(self):
        """Set up the system monitor display on the right side of status bar"""
        # Create a professional status display widget
        self.system_monitor_widget = QWidget()
        self.system_monitor_widget.setFixedHeight(20)
        self.system_monitor_widget.setCursor(Qt.PointingHandCursor)
        self.system_monitor_widget.mousePressEvent = self._on_system_monitor_click

        # Layout for the status display
        status_layout = QHBoxLayout(self.system_monitor_widget)
        status_layout.setContentsMargins(8, 2, 8, 2)
        status_layout.setSpacing(8)

        # CPU status with percentage
        self.cpu_status = QLabel(
            f"{get_text('ui.system_monitor.cpu_prefix')}0{get_text('ui.system_monitor.percent_suffix')}"
        )
        self.cpu_status.setStyleSheet(
            """
            QLabel {
                color: #2c3e50;
                font-size: 10px;
                font-weight: 500;
                padding: 2px 4px;
                border-radius: 3px;
                background-color: #e8f5e8;
            }
        """
        )
        status_layout.addWidget(self.cpu_status)

        # Memory status with percentage
        self.memory_status = QLabel(
            f"{get_text('ui.system_monitor.ram_prefix')}0{get_text('ui.system_monitor.percent_suffix')}"
        )
        self.memory_status.setStyleSheet(
            """
            QLabel {
                color: #2c3e50;
                font-size: 10px;
                font-weight: 500;
                padding: 2px 4px;
                border-radius: 3px;
                background-color: #e8f5e8;
            }
        """
        )
        status_layout.addWidget(self.memory_status)

        # App memory status
        self.app_status = QLabel(
            f"{get_text('ui.system_monitor.app_prefix')}0{get_text('ui.system_monitor.mb_suffix')}"
        )
        self.app_status.setStyleSheet(
            """
            QLabel {
                color: #2c3e50;
                font-size: 10px;
                font-weight: 500;
                padding: 2px 4px;
                border-radius: 3px;
                background-color: #e8f5e8;
            }
        """
        )
        status_layout.addWidget(self.app_status)

        # Overall status indicator
        self.overall_status = QLabel(get_text("ui.system_monitor.status_indicator"))
        self.overall_status.setStyleSheet(
            """
            QLabel {
                color: #27ae60;
                font-size: 12px;
                font-weight: bold;
            }
        """
        )
        status_layout.addWidget(self.overall_status)

        # Add the widget to the main status bar layout
        self.layout().addWidget(self.system_monitor_widget)

        # Set up the system monitor
        self.setup_system_monitor()

        # Set up timer for status updates (parented to the status bar for safe cleanup)
        self.status_update_timer = QTimer(self)
        self.status_update_timer.timeout.connect(self._update_status_display)
        self.status_update_timer.start(5000)  # Update every 5 seconds

        # Initial update
        self._update_status_display()

    def _on_system_monitor_click(self, event):
        """Handle click on system monitor status display"""
        if event.button() == Qt.LeftButton:
            self._show_system_monitor_panel()

    def _on_language_chip_click(self):
        """Handle click on language chip to open selector panel"""
        self._show_language_selector_panel()

    def _update_status_display(self):
        """Update the status bar display with current system metrics"""
        try:
            # Check if we're being cleaned up or if the widget is being destroyed
            if (
                self._is_cleaned_up
                or self._shutting_down
                or not hasattr(self, "system_monitor")
                or not self.system_monitor
            ):
                return

            # Check if the widget still exists and is valid
            if not self.isVisible() or self.isHidden():
                return

            # Check if the application is shutting down
            if (
                hasattr(self, "status_update_timer")
                and not self.status_update_timer.isActive()
            ):
                return

            resources = self.system_monitor.get_resources()
            if not resources:
                return

            # Update CPU status with percentage and color
            cpu_text = f"{get_text('ui.system_monitor.cpu_prefix')}{resources.cpu_percent:.0f}{get_text('ui.system_monitor.percent_suffix')}"
            if resources.cpu_percent < 50:
                cpu_color = "#e8f5e8"  # Light green
                text_color = "#27ae60"
            elif resources.cpu_percent < 80:
                cpu_color = "#fff3cd"  # Light yellow
                text_color = "#f39c12"
            else:
                cpu_color = "#f8d7da"  # Light red
                text_color = "#dc3545"

            self.cpu_status.setText(cpu_text)
            self.cpu_status.setStyleSheet(
                f"""
                QLabel {{
                    color: {text_color};
                    font-size: 10px;
                    font-weight: 500;
                    padding: 2px 4px;
                    border-radius: 3px;
                    background-color: {cpu_color};
                }}
            """
            )

            # Update Memory status with percentage and color
            mem_text = f"{get_text('ui.system_monitor.ram_prefix')}{resources.memory_percent:.0f}{get_text('ui.system_monitor.percent_suffix')}"
            if resources.memory_percent < 60:
                mem_color = "#e8f5e8"  # Light green
                text_color = "#27ae60"
            elif resources.memory_percent < 85:
                mem_color = "#fff3cd"  # Light yellow
                text_color = "#f39c12"
            else:
                mem_color = "#f8d7da"  # Light red
                text_color = "#dc3545"

            self.memory_status.setText(mem_text)
            self.memory_status.setStyleSheet(
                f"""
                QLabel {{
                    color: {text_color};
                    font-size: 10px;
                    font-weight: 500;
                    padding: 2px 4px;
                    border-radius: 3px;
                    background-color: {mem_color};
                }}
            """
            )

            # Update App memory status with color
            app_text = f"{get_text('ui.system_monitor.app_prefix')}{resources.app_memory_mb:.0f}{get_text('ui.system_monitor.mb_suffix')}"
            if resources.app_memory_mb < 200:
                app_color = "#e8f5e8"  # Light green
                text_color = "#27ae60"
            elif resources.app_memory_mb < 500:
                app_color = "#fff3cd"  # Light yellow
                text_color = "#f39c12"
            else:
                app_color = "#f8d7da"  # Light red
                text_color = "#dc3545"

            self.app_status.setText(app_text)
            self.app_status.setStyleSheet(
                f"""
                QLabel {{
                    color: {text_color};
                    font-size: 10px;
                    font-weight: 500;
                    padding: 2px 4px;
                    border-radius: 3px;
                    background-color: {app_color};
                }}
            """
            )

            # Update overall status indicator
            if resources.cpu_percent < 30 and resources.memory_percent < 50:
                self.overall_status.setText(
                    get_text("ui.system_monitor.status_indicator")
                )
                self.overall_status.setStyleSheet(
                    """
                    QLabel {
                        color: #27ae60;
                        font-size: 12px;
                        font-weight: bold;
                    }
                """
                )
            elif resources.cpu_percent < 70 and resources.memory_percent < 80:
                self.overall_status.setText(
                    get_text("ui.system_monitor.status_indicator")
                )
                self.overall_status.setStyleSheet(
                    """
                    QLabel {
                        color: #f39c12;
                        font-size: 12px;
                        font-weight: bold;
                    }
                """
                )
            else:
                self.overall_status.setText(
                    get_text("ui.system_monitor.status_indicator")
                )
                self.overall_status.setStyleSheet(
                    """
                    QLabel {
                        color: #dc3545;
                        font-size: 12px;
                        font-weight: bold;
                    }
                """
                )

        except Exception as e:
            if hasattr(self, "logger"):
                self.logger.error(f"Failed to update status display: {e}")

    def _show_system_monitor_panel(self):
        """Show the system monitor panel"""
        try:
            # Get the main window
            main_window = self.window()
            if not main_window:
                return

            # If panel exists and is visible, hide it
            if (
                hasattr(main_window, "system_monitor_panel")
                and main_window.system_monitor_panel
                and main_window.system_monitor_panel.isVisible()
            ):
                main_window.system_monitor_panel.hide()
                return

            # If panel exists but is hidden, show it
            if (
                hasattr(main_window, "system_monitor_panel")
                and main_window.system_monitor_panel
                and not main_window.system_monitor_panel.isVisible()
            ):
                main_window.system_monitor_panel.show()
                return

            # Create new panel
            main_window.system_monitor_panel = SystemMonitorPanel(main_window)

            # Position panel as overlay in bottom-right corner
            panel = main_window.system_monitor_panel
            panel.setParent(main_window)
            panel.raise_()

            # Calculate position (bottom-right corner with some margin)
            window_rect = main_window.rect()
            panel_x = window_rect.width() - panel.width() - 20
            panel_y = window_rect.height() - panel.height() - 80  # Above status bar

            panel.move(panel_x, panel_y)
            panel.show()

        except Exception as e:
            if hasattr(self, "logger"):
                self.logger.error(f"Error showing system monitor panel: {e}")

    def _show_language_selector_panel(self):
        """Show the language selector panel near the status bar"""
        try:
            main_window = self.window()
            if not main_window:
                return

            # Toggle if already open
            if (
                hasattr(main_window, "language_selector_panel")
                and main_window.language_selector_panel
                and main_window.language_selector_panel.isVisible()
            ):
                main_window.language_selector_panel.hide()
                # Hide overlay close button if present
                try:
                    if (
                        hasattr(main_window, "language_selector_close_btn")
                        and main_window.language_selector_close_btn
                    ):
                        main_window.language_selector_close_btn.hide()
                except Exception:
                    pass
                return

            if (
                hasattr(main_window, "language_selector_panel")
                and main_window.language_selector_panel
                and not main_window.language_selector_panel.isVisible()
            ):
                main_window.language_selector_panel.show()
                # Reposition/show overlay or child close button
                try:
                    panel = main_window.language_selector_panel
                    close_btn = None
                    if (
                        hasattr(main_window, "language_selector_close_btn")
                        and main_window.language_selector_close_btn
                    ):
                        close_btn = main_window.language_selector_close_btn
                        # Sibling overlay placement
                        g = panel.geometry()
                        x = g.x() + g.width() - close_btn.width() - 8
                        y_above = g.y() - close_btn.height() - 8
                        y = y_above if y_above >= 4 else 4
                        close_btn.move(x, y)
                        close_btn.show()
                        close_btn.raise_()
                    elif hasattr(panel, "_lang_close_btn") and panel._lang_close_btn:
                        close_btn = panel._lang_close_btn
                        x = panel.width() - close_btn.width() - 8
                        y_above = -close_btn.height() - 8
                        # Child-of-panel placement
                        close_btn.move(panel.width() - close_btn.width() - 8, 8)
                        close_btn.show()
                        close_btn.raise_()
                except Exception:
                    pass
                return

            # Create and show new simple selector panel
            from PySide6.QtWidgets import QGridLayout, QLineEdit, QVBoxLayout, QWidget

            from ..utils.language_loader import get_all_languages
            from ..utils.theme_manager import get_theme_manager, get_theme_style

            panel = QWidget(main_window)
            # Match resource panel object name so theme style targets apply
            panel.setObjectName("SystemMonitorPanel")
            # Use the same background/border as resource panel for current theme
            from ..utils.theme_manager import get_complete_style

            panel.setStyleSheet(get_complete_style("system_monitor_panel"))
            try:
                from PySide6.QtCore import Qt as _Qt

                panel.setAttribute(_Qt.WidgetAttribute.WA_StyledBackground, True)
                panel.setAutoFillBackground(True)
            except Exception:
                pass
            # Match left-side selector width/spacing more closely
            panel.setFixedWidth(400)
            panel.setFixedHeight(280)

            lay = QVBoxLayout(panel)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setSpacing(8)

            # Search + Category in a single row (like the left-side selector)
            search = QLineEdit()
            search.setPlaceholderText(
                get_text("ui.language_selection.search_placeholder")
            )
            # Apply the same search styling used in the left-side selector
            try:
                from ..utils.theme_manager import get_complete_style

                search.setStyleSheet(get_complete_style("learn_mode_search_box"))
            except Exception:
                pass
            from PySide6.QtWidgets import QHBoxLayout, QMenu, QPushButton

            filter_bar = QHBoxLayout()
            filter_bar.setContentsMargins(0, 0, 0, 0)
            filter_bar.setSpacing(12)

            category_btn = QPushButton(get_text("ui.language_selection.category_all"))
            category_btn.setObjectName("categoryButton")
            try:
                from ..utils.theme_manager import get_complete_style

                category_btn.setStyleSheet(
                    get_complete_style("learn_mode_category_button")
                )
            except Exception:
                pass
            category_menu = QMenu(category_btn)
            try:
                from ..utils.theme_manager import get_complete_style

                category_menu.setStyleSheet(
                    get_complete_style("learn_mode_category_menu")
                )
            except Exception:
                pass

            categories = [
                (get_text("ui.language_selection.category_all"), "all"),
                (get_text("ui.language_selection.category_popular"), "popular"),
                (get_text("ui.language_selection.category_beginner"), "beginner"),
                (
                    get_text("ui.language_selection.category_intermediate"),
                    "intermediate",
                ),
                (get_text("ui.language_selection.category_advanced"), "advanced"),
            ]

            from ..utils.language_loader import get_language_categories

            cat_map = {}
            for label, key in categories:
                act = category_menu.addAction(label)
                cat_map[act] = key

            def on_category_triggered(action):
                key = cat_map.get(action, "all")
                category_btn.setText(action.text())
                cats = get_language_categories()
                items = cats.get(key, cats.get("all", []))
                populate(items)

            category_menu.triggered.connect(on_category_triggered)
            category_btn.setMenu(category_menu)
            # Add search (takes 3/4) and category dropdown (1/4)
            filter_bar.addWidget(search, 3)
            filter_bar.addWidget(category_btn, 1)
            lay.addLayout(filter_bar)

            # Grid of language buttons
            grid_host = QWidget()
            grid = QGridLayout(grid_host)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setSpacing(8)
            lay.addWidget(grid_host)

            try:
                languages = get_all_languages()
            except Exception:
                languages = []

            def populate(items):
                while grid.count():
                    item = grid.takeAt(0)
                    if item.widget():
                        item.widget().setParent(None)
                for i, lang in enumerate(items):
                    btn = QPushButton(
                        f"{lang.get('flag','🌐')} {lang.get('code','--')}"
                    )
                    # Apply same button style as the left-side language list
                    try:
                        from ..utils.theme_manager import get_complete_style

                        btn.setStyleSheet(
                            get_complete_style("learn_mode_language_button")
                        )
                    except Exception:
                        pass
                    # Single-selection behavior: ensure only one is checked
                    btn.setCheckable(True)

                    def _on_click(checked=False, L=lang, B=btn):
                        # Uncheck all other buttons
                        for j in range(grid.count()):
                            w = grid.itemAt(j).widget()
                            if w and w is not B:
                                w.setChecked(False)
                        on_select(L)

                    btn.clicked.connect(_on_click)
                    grid.addWidget(btn, i // 4, i % 4)

            def on_select(language: dict):
                code = language.get("code", "ASL")
                flag = language.get("flag", "🌐")
                try:
                    from ..core.startup import get_all_settings, save_all_settings

                    settings = get_all_settings()
                    settings["selected_language"] = code
                    save_all_settings(settings)
                except Exception:
                    pass
                self.language_chip.setText(f"{flag} {code}")
                # Emit selection via the MainWindow so active mode updates hand-signs
                try:
                    mw = self.window()
                    if mw and hasattr(mw, "language_selected"):
                        mw.language_selected.emit(code)
                except Exception:
                    pass
                panel.hide()
                # Ensure overlay close button is hidden when panel is closed
                try:
                    mw = self.window()
                    if (
                        mw
                        and hasattr(mw, "language_selector_close_btn")
                        and mw.language_selector_close_btn
                    ):
                        mw.language_selector_close_btn.hide()
                except Exception:
                    pass

            def on_search(text: str):
                t = text.strip().lower()
                if not t:
                    populate(languages)
                else:
                    filtered = [
                        l
                        for l in languages
                        if t in l.get("name", "").lower()
                        or t in l.get("code", "").lower()
                    ]
                    populate(filtered)

            search.textChanged.connect(on_search)
            populate(languages)

            # Position near bottom-right similar to system monitor panel
            window_rect = main_window.rect()
            panel_x = window_rect.width() - panel.width() - 20
            panel_y = window_rect.height() - panel.height() - 80
            panel.move(panel_x, panel_y)
            panel.show()

            from PySide6.QtCore import Qt

            # Floating X (sibling overlay on the main window, not inside the panel layout)
            close_btn = QPushButton("×", main_window)
            close_btn.setFixedSize(20, 20)
            close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            close_btn.setToolTip(get_text("ui.system_monitor.close_tooltip"))

            # High-contrast, theme-aware style
            try:
                from ..utils.theme_manager import get_theme_manager

                is_dark = (
                    get_theme_manager().get_current_theme().lower().startswith("dark")
                )
                close_btn.setStyleSheet(
                    (
                        "QPushButton { background:#2c2c2e; color:#ebebf5; border:1px solid #48484a; border-radius:10px; }"
                        "QPushButton:hover { background:#3a3a3c; border-color:#5a5a5c; }"
                    )
                    if is_dark
                    else (
                        "QPushButton { background:#f0f2f5; color:#1e293b; border:1px solid #e0e6ef; border-radius:10px; }"
                        "QPushButton:hover { background:#e6e9ef; }"
                    )
                )
            except Exception:
                pass

            def _place_close():
                g = panel.geometry()  # coords relative to main_window
                x = g.x() + g.width() - close_btn.width() - 8
                y_above = g.y() - close_btn.height() - 8
                # Always prefer above; clamp to top edge if needed
                y = y_above if y_above >= 4 else 4
                close_btn.move(x, y)
                close_btn.raise_()

            def _hide_both():
                try:
                    panel.hide()
                finally:
                    close_btn.hide()

            close_btn.clicked.connect(_hide_both)
            _place_close()
            close_btn.show()

            # Keep references so it persists
            main_window.language_selector_close_btn = close_btn

            # Reposition on panel move/resize
            _old_resize = panel.resizeEvent

            def _resize(ev):
                if _old_resize:
                    _old_resize(ev)
                _place_close()

            panel.resizeEvent = _resize

            _old_move = panel.moveEvent

            def _move(ev):
                if _old_move:
                    _old_move(ev)
                _place_close()

            panel.moveEvent = _move

            # Hide/remove close when panel is hidden/destroyed
            def _on_destroyed(*_):
                try:
                    close_btn.hide()
                finally:
                    # Drop reference so it can be re-created next time
                    if hasattr(main_window, "language_selector_close_btn"):
                        main_window.language_selector_close_btn = None

            panel.destroyed.connect(_on_destroyed)

            main_window.language_selector_panel = panel
        except Exception as e:
            if hasattr(self, "logger"):
                self.logger.error(f"Error showing language selector panel: {e}")

    def setup_system_monitor(self):
        """Set up the system monitor"""
        try:
            from ..utils.system_monitor import get_system_monitor

            self.system_monitor = get_system_monitor()
            self.system_monitor.start_monitoring()

        except Exception as e:
            if hasattr(self, "logger"):
                self.logger.error(f"Error setting up system monitor: {e}")
            self.system_monitor = None

    def cleanup(self):
        """Clean up system monitor resources"""
        if self._is_cleaned_up:
            return

        self._is_cleaned_up = True
        self._shutting_down = True

        try:
            # Stop status update timer immediately and disconnect signals
            if hasattr(self, "status_update_timer") and self.status_update_timer:
                try:
                    self.status_update_timer.timeout.disconnect()
                except:
                    pass  # Signal might already be disconnected
                self.status_update_timer.stop()
                self.status_update_timer = None

            # Stop system monitor
            if hasattr(self, "system_monitor") and self.system_monitor:
                try:
                    self.system_monitor.stop_monitoring()
                except:
                    pass  # System monitor might already be stopped
                self.system_monitor = None

            # Clean up panel if exists
            main_window = self.window()
            if (
                main_window
                and hasattr(main_window, "system_monitor_panel")
                and main_window.system_monitor_panel
            ):
                try:
                    main_window.system_monitor_panel.cleanup()
                    # Avoid deleteLater during shutdown to prevent double-free
                    main_window.system_monitor_panel.hide()
                    main_window.system_monitor_panel = None
                except:
                    pass  # Panel might already be cleaned up

        except Exception as e:
            if hasattr(self, "logger"):
                self.logger.error(f"Error during cleanup: {e}")
            else:
                print(f"Error during cleanup: {e}")

    def set_status(self, message: str) -> None:
        """Set status message"""
        # Show mode and status together on the left
        mode_text = f"{get_text('ui.status.mode_prefix')}{self.current_mode}"
        full_message = f"{mode_text} | {message}"
        self.status_label.setText(full_message)

    def get_status(self) -> str:
        """Get current status message"""
        return self.status_label.text()

    def set_mode(self, mode: str) -> None:
        """Set mode display"""
        self.current_mode = mode

        # Set specific text for learning mode
        if mode == get_text("modes.learn.name"):
            self.status_label.setText(get_text("ui.status.learning_mode"))
            return

        # Show status bar for other modes
        self.show()

        # Update the status to show the new mode
        current_status = self.get_status()
        # Extract just the status part (after the mode)
        if " | " in current_status:
            status_part = current_status.split(" | ", 1)[1]
        else:
            status_part = get_text("ui.status.default")
        self.set_status(status_part)


class MainWindow(QMainWindow):
    """Main application window"""

    # Signals
    process_requested = Signal()
    clear_requested = Signal()
    settings_requested = Signal()
    update_hand_preference = Signal(str)  # Signal for hand preference changes
    language_selected = Signal(
        str
    )  # New: emit when a language is chosen from status bar

    def __init__(self, title: str = get_text("app.name")):
        super().__init__()
        self.title = title
        self.setWindowTitle(title)
        self.setup_ui()
        self.setup_menu()
        self.setup_shortcuts()

        # Initialize logger
        from ..utils.logger import get_logger

        self.logger = get_logger("helpmesign.main_window")

    def setup_ui(self):
        """Set up the main window UI"""
        self.setWindowTitle(self.title)
        # Window size is managed in app.py via configuration (fixed size).
        # Do not set a fixed size here to avoid duplication and conflicts.

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout - vertical for main content
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Create content area for mode switching
        from PySide6.QtWidgets import QStackedWidget

        self.content_area = QStackedWidget()

        # Create default content (text input + output)
        self.text_input_frame = TextInputFrame()
        self.output_frame = OutputFrame()
        self.default_content = QWidget()
        default_layout = QVBoxLayout(self.default_content)
        default_layout.addWidget(self.text_input_frame)
        default_layout.addWidget(self.output_frame)
        self.content_area.addWidget(self.default_content)

        # Add content area to main layout
        main_layout.addWidget(self.content_area)

        # Create status bar (always visible)
        self.status_bar = StatusBar()
        main_layout.addWidget(self.status_bar)

        # Initialize system monitor panel as None
        self.system_monitor_panel = None

        # Connect signals
        self.text_input_frame.process_requested.connect(self.process_requested.emit)
        self.text_input_frame.clear_requested.connect(self.clear_requested.emit)

    def setup_menu(self):
        """Set up the application menu bar"""
        menubar = self.menuBar()

        # CRITICAL FIX: Set native menu bar BEFORE creating menus
        if platform.system().lower() == "darwin":
            menubar.setNativeMenuBar(True)
            # On macOS, the first menu becomes the application menu
            # DON'T set a custom name - let Qt use the application name
            app_menu = menubar.addMenu("")  # Empty string lets Qt use app name
            # DO NOT call app_menu.setTitle() - this overrides the app name!
        else:
            app_menu = menubar.addMenu(get_text("menu.file.name"))

        # About action
        about_action = QAction(get_text("menu.helpmesign.about"), self)
        about_action.triggered.connect(self.show_about)
        app_menu.addAction(about_action)

        app_menu.addSeparator()

        # Quit action
        quit_action = QAction(get_text("menu.file.quit"), self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        app_menu.addAction(quit_action)

        # Settings menu
        settings_menu = menubar.addMenu(get_text("menu.settings.name"))

        # Preferences action
        preferences_action = QAction(get_text("menu.settings.preferences"), self)
        preferences_action.setShortcut(QKeySequence("Ctrl+,"))
        preferences_action.triggered.connect(self.settings_requested.emit)
        settings_menu.addAction(preferences_action)

        # Help menu
        help_menu = menubar.addMenu(get_text("menu.help.name"))

        # Help action
        help_action = QAction(get_text("menu.help.help"), self)
        help_action.setShortcut(QKeySequence("F1"))
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        # Force the application name to be used in the menu
        from PySide6.QtCore import QCoreApplication

        app_name = get_text("app.name")
        QCoreApplication.setApplicationName(app_name)

    def setup_shortcuts(self):
        """Set up global keyboard shortcuts"""
        # Process shortcut
        process_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        process_shortcut.activated.connect(self.process_requested.emit)

        # Clear shortcut
        clear_shortcut = QShortcut(QKeySequence("Ctrl+Shift+K"), self)
        clear_shortcut.activated.connect(self.clear_requested.emit)

        # Settings shortcut
        settings_shortcut = QShortcut(QKeySequence("Ctrl+,"), self)
        settings_shortcut.activated.connect(self.settings_requested.emit)

    def set_icon(self, icon_path: str) -> None:
        """Set the window icon"""
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def set_title(self, title: str) -> None:
        """Set the window title"""
        self.setWindowTitle(title)

    def set_mode(self, mode: str) -> None:
        """Set the application mode"""
        self.status_bar.set_mode(mode)

    def clear_all(self) -> None:
        """Clear all text areas"""
        self.text_input_frame.clear_text()
        self.output_frame.clear_text()
        self.status_bar.set_status(get_text("ui.status.cleared"))

    def show_about(self) -> None:
        """Show the about dialog"""
        about_text = get_text("about.content")
        QMessageBox.about(self, get_text("about.title"), about_text)

    def show_help(self) -> None:
        """Show the help dialog"""
        help_text = f"""
        <h2>{get_text('help.title')}</h2>
        <h3>{get_text('help.getting_started_title')}</h3>
        """

        # Add getting started steps
        steps = get_list("help.getting_started_steps")
        for step in steps:
            help_text += f"<p>{step}</p>"

        help_text += f"<h3>{get_text('help.keyboard_shortcuts_title')}</h3>"

        # Add keyboard shortcuts
        shortcuts = get_dict("help.keyboard_shortcuts")
        for shortcut_key, shortcut_text in shortcuts.items():
            help_text += f"<p><b>{shortcut_text}</b></p>"

        QMessageBox.information(self, get_text("help.title"), help_text)

    def get_text_input(self) -> str:
        """Get text from input field"""
        return self.text_input_frame.get_text()

    def set_text_input(self, text: str) -> None:
        """Set text in input field"""
        self.text_input_frame.set_text(text)

    def get_text_output(self) -> str:
        """Get text from output field"""
        return self.output_frame.get_text()

    def set_text_output(self, text: str) -> None:
        """Set text in output field"""
        self.output_frame.set_text(text)

    def add_text_output(self, text: str) -> None:
        """Add text to output field"""
        self.output_frame.add_text(text)

    def set_status(self, message: str) -> None:
        """Set status bar message"""
        self.status_bar.set_status(message)

    def focus_input(self) -> None:
        """Focus on the input field"""
        self.text_input_frame.focus_input()

    def emit_hand_preference_change(self, hand_preference: str) -> None:
        """Update hand preference and emit signal"""
        self.update_hand_preference.emit(hand_preference)

    def update_fonts(self) -> None:
        """Update fonts in the window following the defined process:
        Only update fonts in the currently visible/active window
        """
        # DEBUG: Commented out all font updates to debug hand preference override issue
        # try:
        #     # Only update fonts if this window is currently visible
        #     if not self.isVisible():
        #         self.logger.debug("Window not visible, skipping font updates")
        #         return

        #     # Update text input frame fonts
        #     if hasattr(self, "text_input_frame"):
        #         # Update label
        #         label = self.text_input_frame.findChild(QLabel)
        #         if label:
        #             label.setFont(get_label_font())
        #             self.logger.debug("Updated text input frame label font")

        #         # Update text input
        #         if hasattr(self.text_input_frame, "text_input"):
        #             self.text_input_frame.text_input.setFont(get_input_font())
        #             self.logger.debug("Updated text input font")

        #         # Update buttons
        #         if hasattr(self.text_input_frame, "process_button"):
        #             self.text_input_frame.process_button.setFont(get_button_font())
        #             self.logger.debug("Updated process button font")
        #         if hasattr(self.text_input_frame, "clear_button"):
        #             self.text_input_frame.clear_button.setFont(get_button_font())
        #             self.logger.debug("Updated clear button font")

        #     # Update output frame fonts
        #     if hasattr(self, "output_frame"):
        #         # Update label
        #         label = self.output_frame.findChild(QLabel)
        #         if label:
        #             label.setFont(get_label_font())
        #             self.logger.debug("Updated output frame label font")

        #         # Update text output
        #         if hasattr(self.output_frame, "text_output"):
        #             self.output_frame.text_output.setFont(get_body_font())
        #             self.logger.debug("Updated text output font")

        #     # Update status bar fonts
        #     if hasattr(self, "status_bar"):
        #         if hasattr(self.status_bar, "status_label"):
        #             self.status_bar.status_label.setFont(get_small_font())
        #             self.logger.debug("Updated status label font")
        #         if hasattr(self.status_bar, "mode_label"):
        #             self.status_bar.mode_label.setFont(get_small_font())
        #             self.logger.debug("Updated mode label font")

        #     # Update menu bar font
        #     if hasattr(self, "menuBar"):
        #         menu_bar = self.menuBar()
        #         if menu_bar:
        #             menu_bar.setFont(get_small_font())
        #             self.logger.debug("Updated menu bar font")

        #     # Force refresh
        #     self.update()
        #     self.repaint()

        #     self.logger.debug("MainWindow fonts updated successfully")

        # except Exception as e:
        #     # Log error but don't crash
        #     import logging

        #     logging.error(f"Error updating fonts: {e}")

        # DEBUG: Just log that font updates are disabled
        self.logger.debug("Font updates disabled for debugging hand preference issue")

    def closeEvent(self, event):
        """Handle window close event"""
        try:
            # Clean up status bar (includes system monitor)
            if hasattr(self, "status_bar"):
                self.status_bar.cleanup()

            # Force garbage collection to help prevent memory issues
            import gc

            gc.collect()

            self.logger.info("MainWindow closing - cleanup completed")

        except Exception as e:
            self.logger.error(f"Error in closeEvent: {e}")

        # Accept the close event
        event.accept()


class SystemMonitorPanel(QWidget):
    """Innovative overlay panel for system monitoring details"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(320)
        self.setFixedHeight(300)
        self.setup_ui()
        self.setup_system_monitor()

        # Set up timer for updates (parented to the panel for safe cleanup)
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(3000)  # Update every 3 seconds

        # Animation properties
        self.animation = None
        self.target_opacity = 0.95

        # Initial update
        self._update_display()

    def setup_ui(self):
        """Set up the innovative panel UI"""
        # Apply theme-based style from theme manager for consistent look (light/dark)
        from PySide6.QtCore import Qt

        from ..utils.theme_manager import get_theme_manager, get_theme_style

        self.setObjectName("SystemMonitorPanel")
        self.setStyleSheet(get_theme_style("system_monitor_panel"))
        # Ensure the stylesheet background actually paints (no translucency)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)

        # Resolve theme-aware text colors from theme manager (no hard-coded branch)
        theme = get_theme_manager()
        self._title_color = theme.get_theme_color("text_primary")
        self._metric_title_color = theme.get_theme_color("text_muted")
        self._metric_value_color = theme.get_theme_color("text_primary")
        # Fallback for separator using border_secondary
        self._separator_color = theme.get_theme_color("border_secondary")

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Simple flat layout - no nested containers
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title_label = QLabel(get_text("ui.system_monitor.panel_title"))
        title_label.setFont(get_small_font())
        title_label.setStyleSheet(
            """
            QLabel {
                color: %s;
                font-weight: bold;
                font-size: 12px;
            }
        """
            % self._title_color
        )
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Close button
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(20, 20)
        self.close_button.clicked.connect(self._close_panel)
        self.close_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2c2c2e;
                color: #ebebf5;
                border: 1px solid #48484a;
                border-radius: 10px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3a3a3c;
                border-color: #5a5a5c;
            }
        """
        )
        header_layout.addWidget(self.close_button)

        main_layout.addLayout(header_layout)

        # Create metrics display directly in main layout
        self._create_metrics_display(main_layout)

    def _create_metrics_display(self, parent_layout):
        """Create simple metrics display without nested containers"""
        # Create metric rows directly in parent layout
        self._create_metric_card(
            get_text("ui.system_monitor.metrics.cpu"), "cpu_label", "#4a5568"
        )
        self._create_metric_card(
            get_text("ui.system_monitor.metrics.memory"), "memory_label", "#4a5568"
        )
        self._create_metric_card(
            get_text("ui.system_monitor.metrics.application"),
            "app_memory_label",
            "#4a5568",
        )
        self._create_metric_card(
            get_text("ui.system_monitor.metrics.disk"), "disk_label", "#4a5568"
        )
        self._create_metric_card(
            get_text("ui.system_monitor.metrics.uptime"), "uptime_label", "#4a5568"
        )

        # Add insights and recommendations
        self._create_insights_card()
        self._create_recommendations_card()

    def _create_metric_card(self, title, label_attr, color):
        """Create a clean metric row"""
        # Create a simple row layout without card borders
        row_widget = QWidget()
        row_widget.setFixedHeight(24)

        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 2, 0, 2)
        row_layout.setSpacing(8)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(
            """
            QLabel {
                color: %s;
                font-weight: 500;
                font-size: 11px;
                min-width: 80px;
            }
        """
            % self._metric_title_color
        )
        row_layout.addWidget(title_label)

        # Value
        value_label = QLabel("--")
        value_label.setStyleSheet(
            """
            QLabel {
                color: %s;
                font-weight: 600;
                font-size: 11px;
            }
        """
            % self._metric_value_color
        )
        row_layout.addWidget(value_label)
        row_layout.addStretch()

        # Store reference to the label
        setattr(self, label_attr, value_label)

        # Add to the main layout (parent_layout)
        # We need to find the main layout from the parent
        if hasattr(self, "main_layout"):
            self.main_layout.addWidget(row_widget)
        else:
            # Store the main layout reference
            self.main_layout = self.layout()
            self.main_layout.addWidget(row_widget)

    def _create_insights_card(self):
        """Create insights section"""
        # Add a separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(
            "QFrame { background-color: %s; }" % self._separator_color
        )
        separator.setFixedHeight(1)
        self.main_layout.addWidget(separator)

        # Add some spacing
        spacer = QWidget()
        spacer.setFixedHeight(4)
        self.main_layout.addWidget(spacer)

        # Insights label
        self.insights_label = QLabel(
            get_text("ui.system_monitor.insights.system_running_well")
        )
        self.insights_label.setStyleSheet(
            """
            QLabel {
                color: #28a745;
                font-weight: 500;
                font-size: 10px;
                padding: 2px 0;
            }
        """
        )
        self.insights_label.setWordWrap(True)
        self.main_layout.addWidget(self.insights_label)

    def _create_recommendations_card(self):
        """Create recommendations section"""
        # Recommendations label
        self.recommendations_label = QLabel(
            get_text("ui.system_monitor.recommendations.no_actions")
        )
        self.recommendations_label.setStyleSheet(
            """
            QLabel {
                color: #6c757d;
                font-weight: 500;
                font-size: 10px;
                padding: 2px 0;
            }
        """
        )
        self.recommendations_label.setWordWrap(True)
        self.main_layout.addWidget(self.recommendations_label)

    def setup_system_monitor(self):
        """Set up the system monitor"""
        try:
            from ..utils.system_monitor import get_system_monitor

            self.system_monitor = get_system_monitor()
        except Exception as e:
            self.system_monitor = None

    def _update_display(self):
        """Update the system monitor display"""
        try:
            # Re-apply theme on every update to reflect runtime theme changes
            from ..utils.theme_manager import get_theme_manager, get_theme_style

            self.setStyleSheet(get_theme_style("system_monitor_panel"))
            theme = get_theme_manager()
            self._title_color = theme.get_theme_color("text_primary")
            self._metric_title_color = theme.get_theme_color("text_muted")
            self._metric_value_color = theme.get_theme_color("text_primary")
            self._separator_color = theme.get_theme_color("border_secondary")

            # Check if the widget is still valid and visible
            if not self.isVisible() or self.isHidden():
                return

            if not self.system_monitor:
                return

            resources = self.system_monitor.get_resources()
            if not resources:
                return

            # Update metrics
            self._update_metrics_display(resources)

            # Update insights
            self._update_insights_display(resources)

            # Update recommendations
            self._update_recommendations_display(resources)

        except Exception as e:
            # Silently ignore errors during updates to prevent crashes
            pass

    def _update_metrics_display(self, resources):
        """Update the metrics display with professional formatting"""
        # CPU - Show percentage and app usage
        cpu_text = (
            f"{resources.cpu_percent:.1f}% (App: {resources.app_cpu_percent:.1f}%)"
        )
        self.cpu_label.setText(cpu_text)

        # Memory - Show percentage and total
        mem_text = f"{resources.memory_percent:.1f}% ({resources.memory_used_mb:.0f}MB / {resources.memory_total_mb:.0f}MB)"
        self.memory_label.setText(mem_text)

        # App Memory - Show usage and threads
        app_text = f"{resources.app_memory_mb:.0f}MB ({resources.app_threads} threads)"
        self.app_memory_label.setText(app_text)

        # Disk - Show percentage and total
        disk_text = f"{resources.disk_usage_percent:.1f}% ({resources.disk_used_gb:.1f}GB / {resources.disk_total_gb:.1f}GB)"
        self.disk_label.setText(disk_text)

        # Uptime - Show hours
        uptime_text = f"{resources.uptime_hours:.1f} hours"
        self.uptime_label.setText(uptime_text)

    def _update_insights_display(self, resources):
        """Update the insights display"""
        insights = []

        if resources.cpu_percent > 80:
            insights.append(get_text("ui.system_monitor.insights.high_cpu"))
        elif resources.cpu_percent < 20:
            insights.append(get_text("ui.system_monitor.insights.optimal_cpu"))

        if resources.memory_percent > 85:
            insights.append(get_text("ui.system_monitor.insights.high_memory"))
        elif resources.memory_percent < 40:
            insights.append(get_text("ui.system_monitor.insights.healthy_memory"))

        if resources.app_memory_mb > 500:
            insights.append(get_text("ui.system_monitor.insights.high_app_memory"))
        else:
            insights.append(get_text("ui.system_monitor.insights.normal_app_memory"))

        if resources.disk_usage_percent > 90:
            insights.append(get_text("ui.system_monitor.insights.low_disk_space"))
        elif resources.disk_usage_percent < 50:
            insights.append(get_text("ui.system_monitor.insights.plenty_disk_space"))

        if not insights:
            insights.append(get_text("ui.system_monitor.insights.system_running_well"))

        self.insights_label.setText(" | ".join(insights[:2]))  # Show top 2 insights

    def _update_recommendations_display(self, resources):
        """Update the recommendations display"""
        recommendations = []

        if resources.cpu_percent > 80:
            recommendations.append(
                get_text("ui.system_monitor.recommendations.close_apps")
            )
        if resources.memory_percent > 85:
            recommendations.append(
                get_text("ui.system_monitor.recommendations.add_ram")
            )
        if resources.app_memory_mb > 500:
            recommendations.append(
                get_text("ui.system_monitor.recommendations.restart_app")
            )
        if resources.disk_usage_percent > 90:
            recommendations.append(
                get_text("ui.system_monitor.recommendations.clean_disk")
            )
        if resources.uptime_hours > 168:  # 7 days
            recommendations.append(
                get_text("ui.system_monitor.recommendations.system_restart")
            )

        if not recommendations:
            recommendations.append(
                get_text("ui.system_monitor.recommendations.no_actions")
            )

        self.recommendations_label.setText(
            " | ".join(recommendations[:1])
        )  # Show top 1 recommendation

    def _close_panel(self):
        """Close the panel"""
        self.hide()

    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, "update_timer") and self.update_timer:
            try:
                self.update_timer.timeout.disconnect()
            except Exception:
                pass
            self.update_timer.stop()
            # Avoid deleteLater during app shutdown to prevent allocator issues
            self.update_timer = None
        if hasattr(self, "system_monitor") and self.system_monitor:
            self.system_monitor.stop_monitoring()
