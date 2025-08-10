"""
Qt Module Mocks

Module-level mock implementations that can replace PySide6 modules entirely.
This prevents segfaults by intercepting Qt imports at the module level.
"""

import sys
from typing import Any, Dict, Optional
from unittest.mock import MagicMock

from .qt_mock_framework import (
    MockQApplication,
    MockQByteArray,
    MockQComboBox,
    MockQDialog,
    MockQFrame,
    MockQLabel,
    MockQObject,
    MockQPushButton,
    MockQRect,
    MockQScrollArea,
    MockQSize,
    MockQSizePolicy,
    MockQWidget,
    MockSignal,
)


class MockQtWidgets:
    """Mock PySide6.QtWidgets module."""

    def __init__(self):
        # Core widget classes
        self.QWidget = MockQWidget
        self.QDialog = MockQDialog
        self.QFrame = MockQFrame
        self.QLabel = MockQLabel
        self.QPushButton = MockQPushButton
        self.QComboBox = MockQComboBox

        # Layout classes
        self.QVBoxLayout = MagicMock()
        self.QHBoxLayout = MagicMock()
        self.QGridLayout = MagicMock()

        # Container classes
        self.QGroupBox = MagicMock()
        self.QScrollArea = MockQScrollArea
        self.QTabWidget = MagicMock()
        self.QTabBar = MagicMock()

        # Input classes
        self.QLineEdit = MagicMock()
        self.QTextEdit = MagicMock()
        self.QCheckBox = MagicMock()
        self.QRadioButton = MagicMock()
        self.QButtonGroup = MagicMock()
        self.QSlider = MagicMock()
        self.QListWidget = MagicMock()
        self.QListWidgetItem = MagicMock()
        self.QMenu = MagicMock()

        # Application
        self.QApplication = MockQApplication

        # Constants
        self.Qt = MagicMock()
        self.Qt.AlignLeft = 1
        self.Qt.AlignRight = 2
        self.Qt.AlignCenter = 4
        self.Qt.AlignTop = 8
        self.Qt.AlignBottom = 16
        self.Qt.AlignVCenter = 32
        self.Qt.AlignHCenter = 64
        self.Qt.AlignJustify = 128

        # Focus policies
        self.Qt.NoFocus = 0
        self.Qt.TabFocus = 1
        self.Qt.ClickFocus = 2
        self.Qt.StrongFocus = 3
        self.Qt.WheelFocus = 4

        # Context menu policies
        self.Qt.DefaultContextMenu = 0
        self.Qt.ActionsContextMenu = 1
        self.Qt.CustomContextMenu = 2
        self.Qt.PreventContextMenu = 3

        # Frame styles - support both old and new syntax
        self.QFrame.NoFrame = 0
        self.QFrame.Box = 1
        self.QFrame.Panel = 2
        self.QFrame.StyledPanel = 3
        self.QFrame.HLine = 4
        self.QFrame.VLine = 5
        self.QFrame.WinPanel = 6

        # Add Shape enum for newer PySide6 syntax
        self.QFrame.Shape = MagicMock()
        # Expose QSizePolicy via QtWidgets as well (some code imports from here)
        self.QSizePolicy = MockQSizePolicy
        self.QFrame.Shape.NoFrame = 0
        self.QFrame.Shape.Box = 1
        self.QFrame.Shape.Panel = 2
        self.QFrame.Shape.StyledPanel = 3
        self.QFrame.Shape.HLine = 4
        self.QFrame.Shape.VLine = 5
        self.QFrame.Shape.WinPanel = 6


class MockQtCore:
    """Mock PySide6.QtCore module."""

    def __init__(self):
        # Core classes - QObject should be MockQWidget for consistency
        self.QObject = MockQWidget  # Use MockQWidget instead of MockQObject
        self.QCoreApplication = MagicMock()
        self.QEventLoop = MagicMock()
        self.QTimer = MagicMock()
        self.QThread = MagicMock()
        self.QEvent = MagicMock()
        self.QMouseEvent = MagicMock()
        self.QKeyEvent = MagicMock()
        self.QPaintEvent = MagicMock()

        # Geometry classes
        self.QSize = MockQSize
        self.QRect = MockQRect
        self.QSizePolicy = MockQSizePolicy
        self.QByteArray = MockQByteArray

        # Signal/Slot system
        self.Signal = MockSignal
        self.Slot = MagicMock()
        self.pyqtSignal = MockSignal  # Alternative name

        # Constants
        self.Qt = MagicMock()
        self.Qt.LeftButton = 1
        self.Qt.RightButton = 2
        self.Qt.MiddleButton = 4

        # Key constants
        self.Qt.Key_Return = 16777220
        self.Qt.Key_Enter = 16777221
        self.Qt.Key_Escape = 16777216
        self.Qt.Key_Tab = 16777217
        self.Qt.Key_Backtab = 16777218
        self.Qt.Key_Backspace = 16777219
        self.Qt.Key_Delete = 16777223
        self.Qt.Key_Insert = 16777222
        self.Qt.Key_Home = 16777232
        self.Qt.Key_End = 16777233
        self.Qt.Key_Left = 16777234
        self.Qt.Key_Up = 16777235
        self.Qt.Key_Right = 16777236
        self.Qt.Key_Down = 16777237
        self.Qt.Key_PageUp = 16777238
        self.Qt.Key_PageDown = 16777239

        # Modifier keys
        self.Qt.NoModifier = 0
        self.Qt.ShiftModifier = 1
        self.Qt.ControlModifier = 2
        self.Qt.AltModifier = 4
        self.Qt.MetaModifier = 8

        # Dialog results
        self.QDialog = MagicMock()
        self.QDialog.Accepted = 1
        self.QDialog.Rejected = 0


class MockQtGui:
    """Mock PySide6.QtGui module."""

    def __init__(self):
        # Painting classes
        self.QPainter = MagicMock()
        self.QFont = MagicMock()
        self.QColor = MagicMock()
        self.QPen = MagicMock()
        self.QBrush = MagicMock()
        self.QPixmap = MagicMock()
        self.QIcon = MagicMock()

        # Font weight constants
        self.QFont = MagicMock()
        self.QFont.Thin = 0
        self.QFont.ExtraLight = 12
        self.QFont.Light = 25
        self.QFont.Normal = 50
        self.QFont.Medium = 57
        self.QFont.DemiBold = 63
        self.QFont.Bold = 75
        self.QFont.ExtraBold = 81
        self.QFont.Black = 87

        # Color constants
        self.QColor = MagicMock()
        self.QColor.black = MagicMock()
        self.QColor.white = MagicMock()
        self.QColor.red = MagicMock()
        self.QColor.green = MagicMock()
        self.QColor.blue = MagicMock()
        self.QColor.yellow = MagicMock()
        self.QColor.cyan = MagicMock()
        self.QColor.magenta = MagicMock()
        self.QColor.gray = MagicMock()
        self.QColor.darkGray = MagicMock()
        self.QColor.lightGray = MagicMock()
        self.QColor.transparent = MagicMock()


class MockPySide6:
    """Complete mock PySide6 module replacement."""

    def __init__(self):
        self.QtWidgets = MockQtWidgets()
        self.QtCore = MockQtCore()
        self.QtGui = MockQtGui()

        # Make Qt constants available at top level
        self.Qt = self.QtCore.Qt

        # Common aliases
        self.QWidget = self.QtWidgets.QWidget
        self.QDialog = self.QtWidgets.QDialog
        self.QApplication = self.QtWidgets.QApplication
        self.QObject = self.QtCore.QObject
        self.Signal = self.QtCore.Signal
        self.Slot = self.QtCore.Slot

        # Make all Qt classes available at top level for convenience
        self.QFrame = self.QtWidgets.QFrame
        self.QLabel = self.QtWidgets.QLabel
        self.QPushButton = self.QtWidgets.QPushButton
        self.QComboBox = self.QtWidgets.QComboBox
        self.QVBoxLayout = self.QtWidgets.QVBoxLayout
        self.QHBoxLayout = self.QtWidgets.QHBoxLayout
        self.QGridLayout = self.QtWidgets.QGridLayout
        self.QGroupBox = self.QtWidgets.QGroupBox
        self.QScrollArea = self.QtWidgets.QScrollArea
        self.QTabWidget = self.QtWidgets.QTabWidget
        self.QTabBar = self.QtWidgets.QTabBar
        self.QLineEdit = self.QtWidgets.QLineEdit
        self.QTextEdit = self.QtWidgets.QTextEdit
        self.QCheckBox = self.QtWidgets.QCheckBox
        self.QRadioButton = self.QtWidgets.QRadioButton
        self.QButtonGroup = self.QtWidgets.QButtonGroup
        self.QSlider = self.QtWidgets.QSlider
        self.QSize = self.QtCore.QSize
        self.QRect = self.QtCore.QRect
        self.QSizePolicy = self.QtCore.QSizePolicy
        self.QByteArray = self.QtCore.QByteArray
        self.QPainter = self.QtGui.QPainter
        self.QFont = self.QtGui.QFont
        self.QColor = self.QtGui.QColor
        self.QPen = self.QtGui.QPen
        self.QBrush = self.QtGui.QBrush
        self.QPixmap = self.QtGui.QPixmap
        self.QIcon = self.QtGui.QIcon


class QtModuleMocker:
    """Manager for Qt module mocking."""

    def __init__(self):
        self._original_modules = {}
        self._is_active = False
        self._mock_pyside6 = MockPySide6()

    def activate(self):
        """Activate Qt module mocking."""
        if self._is_active:
            return

        # Store original modules
        self._original_modules = {}
        for module_name in [
            "PySide6",
            "PySide6.QtWidgets",
            "PySide6.QtCore",
            "PySide6.QtGui",
        ]:
            if module_name in sys.modules:
                self._original_modules[module_name] = sys.modules[module_name]

        # Replace modules with mocks
        sys.modules["PySide6"] = self._mock_pyside6
        sys.modules["PySide6.QtWidgets"] = self._mock_pyside6.QtWidgets
        sys.modules["PySide6.QtCore"] = self._mock_pyside6.QtCore
        sys.modules["PySide6.QtGui"] = self._mock_pyside6.QtGui

        # Also make Qt classes available at the top level of PySide6
        for attr_name in dir(self._mock_pyside6):
            if not attr_name.startswith("_"):
                setattr(
                    sys.modules["PySide6"],
                    attr_name,
                    getattr(self._mock_pyside6, attr_name),
                )

        self._is_active = True

    def deactivate(self):
        """Deactivate Qt module mocking."""
        if not self._is_active:
            return

        # Restore original modules
        for module_name, original_module in self._original_modules.items():
            if original_module is not None:
                sys.modules[module_name] = original_module
            elif module_name in sys.modules:
                del sys.modules[module_name]

        self._original_modules.clear()
        self._is_active = False

    def is_active(self) -> bool:
        """Check if Qt module mocking is active."""
        return self._is_active

    def get_mock(self, module_name: str) -> Optional[Any]:
        """Get a mock module by name."""
        if not self._is_active:
            return None

        if module_name == "PySide6":
            return self._mock_pyside6
        elif module_name == "PySide6.QtWidgets":
            return self._mock_pyside6.QtWidgets
        elif module_name == "PySide6.QtCore":
            return self._mock_pyside6.QtCore
        elif module_name == "PySide6.QtGui":
            return self._mock_pyside6.QtGui

        return None

    def reset_mocks(self):
        """Reset all mock objects to their initial state."""
        # Reset the mock framework
        from .qt_mock_registry import qt_mock_registry

        qt_mock_registry.reset_all_mocks()


# Global instance
qt_module_mocker = QtModuleMocker()


def activate_qt_mocks():
    """Activate Qt module mocking globally."""
    qt_module_mocker.activate()


def deactivate_qt_mocks():
    """Deactivate Qt module mocking globally."""
    qt_module_mocker.deactivate()


def is_qt_mocks_active() -> bool:
    """Check if Qt module mocking is active."""
    return qt_module_mocker.is_active()


def get_qt_mock(module_name: str) -> Optional[Any]:
    """Get a Qt mock module by name."""
    return qt_module_mocker.get_mock(module_name)


def reset_qt_mocks():
    """Reset all Qt mocks."""
    qt_module_mocker.reset_mocks()
