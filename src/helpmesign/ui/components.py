#!/usr/bin/env python3
"""
UI Components for HelpMeSign Application
"""

import os
import platform
from typing import Optional, Callable
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QFrame,
    QMessageBox,
    QMenuBar,
    QSizePolicy,
    QScrollArea,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QKeySequence, QAction, QShortcut

from ..utils.font_manager import (
    get_label_font,
    get_input_font,
    get_button_font,
    get_body_font,
    get_small_font,
)
from ..utils.language_manager import get_text, get_list, get_dict


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
    """Status bar widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the status bar UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Status label
        self.status_label = QLabel(get_text("ui.status.default"))
        self.status_label.setFont(get_small_font())
        layout.addWidget(self.status_label)

        layout.addStretch()

        # Mode label
        self.mode_label = QLabel(
            f"{get_text('ui.status.mode_prefix')}{get_text('modes.sign_translate.name')}"
        )
        self.mode_label.setFont(get_small_font())
        layout.addWidget(self.mode_label)

    def set_status(self, message: str) -> None:
        """Set status message"""
        self.status_label.setText(message)

    def get_status(self) -> str:
        """Get current status message"""
        return self.status_label.text()

    def set_mode(self, mode: str) -> None:
        """Set mode display"""
        self.mode_label.setText(f"{get_text('ui.status.mode_prefix')}{mode}")


class MainWindow(QMainWindow):
    """Main application window"""

    # Signals
    process_requested = Signal()
    clear_requested = Signal()
    settings_requested = Signal()

    def __init__(self, title: str = get_text("app.name")):
        super().__init__()
        self.title = title
        self.setup_ui()
        self.setup_menu()
        self.setup_shortcuts()

    def setup_ui(self):
        """Set up the main window UI"""
        self.setWindowTitle(self.title)
        self.setMinimumSize(800, 600)
        self.resize(1024, 1024)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Create UI components
        self.text_input_frame = TextInputFrame()
        self.output_frame = OutputFrame()
        self.status_bar = StatusBar()

        # Add components to layout
        main_layout.addWidget(self.text_input_frame)
        main_layout.addWidget(self.output_frame)
        main_layout.addWidget(self.status_bar)

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

        # HelpMeSign menu (macOS) / File menu (Windows/Linux)
        if platform.system().lower() == "darwin":
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
