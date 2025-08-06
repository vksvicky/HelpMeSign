"""
Qt Mock Framework

Core framework for mocking Qt classes and functionality.
Provides mock implementations of Qt classes that behave like real Qt objects.
"""

from typing import Any, Callable, Dict, List, Optional
from unittest.mock import MagicMock, Mock, PropertyMock

from .qt_mock_registry import qt_mock_registry


class MockQObject:
    """Base mock for QObject functionality."""

    def __init__(self, parent=None):
        self._parent = parent
        self._children = []
        self._signals = {}
        self._slots = {}
        self._properties = {}
        self._object_name = ""

        if parent and hasattr(parent, "_children"):
            parent._children.append(self)

    def setParent(self, parent):
        """Set the parent of this object."""
        if self._parent and hasattr(self._parent, "_children"):
            if self in self._parent._children:
                self._parent._children.remove(self)

        self._parent = parent
        if parent and hasattr(parent, "_children"):
            parent._children.append(self)

    def parent(self):
        """Get the parent of this object."""
        return self._parent

    def children(self):
        """Get the children of this object."""
        return self._children.copy()

    def setObjectName(self, name: str):
        """Set the object name."""
        self._object_name = name

    def objectName(self) -> str:
        """Get the object name."""
        return self._object_name

    def connect(self, signal, slot):
        """Connect a signal to a slot."""
        if signal not in self._signals:
            self._signals[signal] = []
        self._signals[signal].append(slot)

    def disconnect(self, signal, slot):
        """Disconnect a signal from a slot."""
        if signal in self._signals and slot in self._signals[signal]:
            self._signals[signal].remove(slot)

    def emit(self, signal, *args):
        """Emit a signal to all connected slots."""
        if signal in self._signals:
            for slot in self._signals[signal]:
                if callable(slot):
                    slot(*args)


class MockQWidget(MockQObject):
    """Mock implementation of QWidget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._visible = False
        self._enabled = True
        self._geometry = MockQRect(0, 0, 100, 100)
        self._size_policy = MockQSizePolicy()
        self._layout = None
        self._window_title = ""
        self._tool_tip = ""
        self._status_tip = ""
        self._whats_this = ""
        self._focus_policy = 0  # NoFocus
        self._mouse_tracking = False
        self._updates_enabled = True
        self._context_menu_policy = 0  # DefaultContextMenu
        self._style_sheet = ""

        # Register with registry
        qt_mock_registry.register_mock(
            f"QWidget_{id(self)}",
            self,
            {
                "visible": self._visible,
                "enabled": self._enabled,
                "geometry": self._geometry,
                "layout": self._layout,
            },
        )

    def show(self):
        """Show the widget."""
        self._visible = True
        qt_mock_registry.update_mock_state(f"QWidget_{id(self)}", {"visible": True})

    def hide(self):
        """Hide the widget."""
        self._visible = False
        qt_mock_registry.update_mock_state(f"QWidget_{id(self)}", {"visible": False})

    def isVisible(self) -> bool:
        """Check if the widget is visible."""
        return self._visible

    def setVisible(self, visible: bool):
        """Set the visibility of the widget."""
        self._visible = visible
        qt_mock_registry.update_mock_state(f"QWidget_{id(self)}", {"visible": visible})

    def setEnabled(self, enabled: bool):
        """Set the enabled state of the widget."""
        self._enabled = enabled
        qt_mock_registry.update_mock_state(f"QWidget_{id(self)}", {"enabled": enabled})

    def isEnabled(self) -> bool:
        """Check if the widget is enabled."""
        return self._enabled

    def setGeometry(self, x: int, y: int, width: int, height: int):
        """Set the geometry of the widget."""
        self._geometry = MockQRect(x, y, width, height)
        qt_mock_registry.update_mock_state(
            f"QWidget_{id(self)}", {"geometry": self._geometry}
        )

    def geometry(self) -> "MockQRect":
        """Get the geometry of the widget."""
        return self._geometry

    def setLayout(self, layout):
        """Set the layout of the widget."""
        self._layout = layout
        if layout:
            layout.setParent(self)
        qt_mock_registry.update_mock_state(f"QWidget_{id(self)}", {"layout": layout})

    def layout(self):
        """Get the layout of the widget."""
        return self._layout

    def setWindowTitle(self, title: str):
        """Set the window title."""
        self._window_title = title

    def windowTitle(self) -> str:
        """Get the window title."""
        return self._window_title

    def setToolTip(self, tip: str):
        """Set the tool tip."""
        self._tool_tip = tip

    def toolTip(self) -> str:
        """Get the tool tip."""
        return self._tool_tip

    def setStatusTip(self, tip: str):
        """Set the status tip."""
        self._status_tip = tip

    def statusTip(self) -> str:
        """Get the status tip."""
        return self._status_tip

    def setWhatsThis(self, text: str):
        """Set the what's this text."""
        self._whats_this = text

    def whatsThis(self) -> str:
        """Get the what's this text."""
        return self._whats_this

    def setFocusPolicy(self, policy: int):
        """Set the focus policy."""
        self._focus_policy = policy

    def focusPolicy(self) -> int:
        """Get the focus policy."""
        return self._focus_policy

    def setMouseTracking(self, enable: bool):
        """Set mouse tracking."""
        self._mouse_tracking = enable

    def hasMouseTracking(self) -> bool:
        """Check if mouse tracking is enabled."""
        return self._mouse_tracking

    def setUpdatesEnabled(self, enable: bool):
        """Set updates enabled."""
        self._updates_enabled = enable

    def updatesEnabled(self) -> bool:
        """Check if updates are enabled."""
        return self._updates_enabled

    def update(self):
        """Update the widget."""
        pass  # Mock implementation

    def repaint(self):
        """Repaint the widget."""
        pass  # Mock implementation

    def close(self) -> bool:
        """Close the widget."""
        self.hide()
        return True

    def raise_(self):
        """Raise the widget to the top."""
        pass  # Mock implementation

    def lower(self):
        """Lower the widget to the bottom."""
        pass  # Mock implementation

    def sizeHint(self) -> "MockQSize":
        """Get the size hint."""
        return MockQSize(100, 100)

    def minimumSizeHint(self) -> "MockQSize":
        """Get the minimum size hint."""
        return MockQSize(50, 50)

    # Add missing methods for tests
    def paintEvent(self, event):
        """Handle paint events."""
        pass

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        pass

    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        pass

    def leaveEvent(self, event):
        """Handle leave events."""
        pass

    def setStyleSheet(self, style_sheet: str):
        """Set the style sheet."""
        self._style_sheet = style_sheet

    def styleSheet(self) -> str:
        """Get the style sheet."""
        return self._style_sheet


class MockQDialog(MockQWidget):
    """Mock implementation of QDialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._modal = False
        self._result = 0  # Rejected
        self._accepted = False
        self._rejected = False

    def setModal(self, modal: bool):
        """Set the modal state."""
        self._modal = modal

    def isModal(self) -> bool:
        """Check if the dialog is modal."""
        return self._modal

    def exec(self) -> int:
        """Execute the dialog."""
        # Mock implementation - return the current result
        return self._result

    def accept(self):
        """Accept the dialog."""
        self._result = 1  # Accepted
        self._accepted = True
        self.close()

    def reject(self):
        """Reject the dialog."""
        self._result = 0  # Rejected
        self._rejected = True
        self.close()

    def result(self) -> int:
        """Get the dialog result."""
        return self._result


class MockQFrame(MockQWidget):
    """Mock implementation of QFrame."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._frame_style = 0  # NoFrame
        self._line_width = 1
        self._mid_line_width = 0

    def setFrameStyle(self, style: int):
        """Set the frame style."""
        self._frame_style = style

    def frameStyle(self) -> int:
        """Get the frame style."""
        return self._frame_style

    def setLineWidth(self, width: int):
        """Set the line width."""
        self._line_width = width

    def lineWidth(self) -> int:
        """Get the line width."""
        return self._line_width


class MockQLabel(MockQWidget):
    """Mock implementation of QLabel."""

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = text
        self._pixmap = None
        self._alignment = 0  # AlignLeft | AlignVCenter
        self._word_wrap = False
        self._text_format = 0  # PlainText

    def setText(self, text: str):
        """Set the text."""
        self._text = text

    def text(self) -> str:
        """Get the text."""
        return self._text

    def setPixmap(self, pixmap):
        """Set the pixmap."""
        self._pixmap = pixmap

    def pixmap(self):
        """Get the pixmap."""
        return self._pixmap

    def setAlignment(self, alignment: int):
        """Set the alignment."""
        self._alignment = alignment

    def alignment(self) -> int:
        """Get the alignment."""
        return self._alignment

    def setWordWrap(self, on: bool):
        """Set word wrap."""
        self._word_wrap = on

    def wordWrap(self) -> bool:
        """Check if word wrap is enabled."""
        return self._word_wrap


class MockQPushButton(MockQWidget):
    """Mock implementation of QPushButton."""

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = text
        self._icon = None
        self._checkable = False
        self._checked = False
        self._auto_repeat = False
        self._auto_repeat_delay = 300
        self._auto_repeat_interval = 100
        self._clicked_signal = MockSignal()

    def setText(self, text: str):
        """Set the text."""
        self._text = text

    def text(self) -> str:
        """Get the text."""
        return self._text

    def setIcon(self, icon):
        """Set the icon."""
        self._icon = icon

    def icon(self):
        """Get the icon."""
        return self._icon

    def setCheckable(self, checkable: bool):
        """Set if the button is checkable."""
        self._checkable = checkable

    def isCheckable(self) -> bool:
        """Check if the button is checkable."""
        return self._checkable

    def setChecked(self, checked: bool):
        """Set the checked state."""
        self._checked = checked

    def isChecked(self) -> bool:
        """Check if the button is checked."""
        return self._checked

    def click(self):
        """Simulate a click."""
        if self._checkable:
            self._checked = not self._checked
        self._clicked_signal.emit(self._checked)

    @property
    def clicked_signal(self):
        """Get the clicked signal."""
        return self._clicked_signal


class MockQComboBox(MockQWidget):
    """Mock implementation of QComboBox."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._current_index = -1
        self._current_text = ""
        self._editable = False
        self._max_count = 32767
        self._current_text_changed_signal = MockSignal()
        self._current_index_changed_signal = MockSignal()

    def addItem(self, text: str, user_data=None):
        """Add an item to the combo box."""
        self._items.append((text, user_data))
        if self._current_index == -1:
            self.setCurrentIndex(0)

    def addItems(self, texts: List[str]):
        """Add multiple items to the combo box."""
        for text in texts:
            self.addItem(text)

    def setCurrentIndex(self, index: int):
        """Set the current index."""
        if 0 <= index < len(self._items):
            self._current_index = index
            self._current_text = self._items[index][0]
            self._current_index_changed_signal.emit(index)
            self._current_text_changed_signal.emit(self._current_text)

    def currentIndex(self) -> int:
        """Get the current index."""
        return self._current_index

    def setCurrentText(self, text: str):
        """Set the current text."""
        for i, (item_text, _) in enumerate(self._items):
            if item_text == text:
                self.setCurrentIndex(i)
                break

    def currentText(self) -> str:
        """Get the current text."""
        return self._current_text

    def count(self) -> int:
        """Get the number of items."""
        return len(self._items)

    def itemText(self, index: int) -> str:
        """Get the text of an item."""
        if 0 <= index < len(self._items):
            return self._items[index][0]
        return ""

    def clear(self):
        """Clear all items."""
        self._items.clear()
        self._current_index = -1
        self._current_text = ""


class MockQSize:
    """Mock implementation of QSize."""

    def __init__(self, width: int = 0, height: int = 0):
        self._width = width
        self._height = height

    def width(self) -> int:
        """Get the width."""
        return self._width

    def height(self) -> int:
        """Get the height."""
        return self._height

    def setWidth(self, width: int):
        """Set the width."""
        self._width = width

    def setHeight(self, height: int):
        """Set the height."""
        self._height = height

    def __eq__(self, other):
        if isinstance(other, MockQSize):
            return self._width == other._width and self._height == other._height
        return False


class MockQRect:
    """Mock implementation of QRect."""

    def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0):
        self._x = x
        self._y = y
        self._width = width
        self._height = height

    def x(self) -> int:
        """Get the x coordinate."""
        return self._x

    def y(self) -> int:
        """Get the y coordinate."""
        return self._y

    def width(self) -> int:
        """Get the width."""
        return self._width

    def height(self) -> int:
        """Get the height."""
        return self._height

    def left(self) -> int:
        """Get the left coordinate."""
        return self._x

    def top(self) -> int:
        """Get the top coordinate."""
        return self._y

    def right(self) -> int:
        """Get the right coordinate."""
        return self._x + self._width

    def bottom(self) -> int:
        """Get the bottom coordinate."""
        return self._y + self._height

    def setRect(self, x: int, y: int, width: int, height: int):
        """Set the rectangle."""
        self._x = x
        self._y = y
        self._width = width
        self._height = height

    def __eq__(self, other):
        if isinstance(other, MockQRect):
            return (
                self._x == other._x
                and self._y == other._y
                and self._width == other._width
                and self._height == other._height
            )
        return False


class MockQSizePolicy:
    """Mock implementation of QSizePolicy."""

    def __init__(self):
        self._horizontal_policy = 0  # Fixed
        self._vertical_policy = 0  # Fixed
        self._horizontal_stretch = 0
        self._vertical_stretch = 0

    def setHorizontalPolicy(self, policy: int):
        """Set the horizontal policy."""
        self._horizontal_policy = policy

    def horizontalPolicy(self) -> int:
        """Get the horizontal policy."""
        return self._horizontal_policy

    def setVerticalPolicy(self, policy: int):
        """Set the vertical policy."""
        self._vertical_policy = policy

    def verticalPolicy(self) -> int:
        """Get the vertical policy."""
        return self._vertical_policy


class MockSignal:
    """Mock implementation of Qt signals."""

    def __init__(self, *args):
        """Initialize signal with optional type arguments."""
        self._slots = []
        self._signal_types = args

    def connect(self, slot: Callable):
        """Connect a slot to this signal."""
        self._slots.append(slot)

    def disconnect(self, slot: Callable):
        """Disconnect a slot from this signal."""
        if slot in self._slots:
            self._slots.remove(slot)

    def emit(self, *args):
        """Emit the signal with arguments."""
        for slot in self._slots:
            if callable(slot):
                slot(*args)


class QtMockFramework:
    """Main Qt mock framework class."""

    def __init__(self):
        self._registry = qt_mock_registry
        self._application = None
        self._initialized = False

    def initialize(self):
        """Initialize the Qt mock framework."""
        if not self._initialized:
            self._create_application()
            self._register_core_mocks()
            self._initialized = True

    def _create_application(self):
        """Create a mock QApplication."""
        self._application = MockQApplication()
        self._registry.register_mock("QApplication", self._application)

    def _register_core_mocks(self):
        """Register core Qt mocks."""
        # Register class mocks
        self._registry.register_mock("QWidget", MockQWidget)
        self._registry.register_mock("QDialog", MockQDialog)
        self._registry.register_mock("QFrame", MockQFrame)
        self._registry.register_mock("QLabel", MockQLabel)
        self._registry.register_mock("QPushButton", MockQPushButton)
        self._registry.register_mock("QComboBox", MockQComboBox)
        self._registry.register_mock("QSize", MockQSize)
        self._registry.register_mock("QRect", MockQRect)
        self._registry.register_mock("QSizePolicy", MockQSizePolicy)
        self._registry.register_mock("Signal", MockSignal)

    def get_application(self):
        """Get the mock QApplication instance."""
        return self._application

    def reset(self):
        """Reset the framework state."""
        self._registry.reset_all_mocks()

    def cleanup(self):
        """Clean up the framework."""
        self._registry.clear_all_mocks()
        self._initialized = False


class MockQApplication(MockQObject):
    """Mock implementation of QApplication."""

    def __init__(self):
        super().__init__()
        self._instance = self
        self._active_window = None
        self._windows = []
        self._quit_called = False
        self._about_to_quit_signal = MockSignal()

    @classmethod
    def instance(cls):
        """Get the application instance."""
        return cls._instance if hasattr(cls, "_instance") else None

    def quit(self):
        """Quit the application."""
        self._quit_called = True
        self._about_to_quit_signal.emit()

    def closeAllWindows(self):
        """Close all windows."""
        for window in self._windows:
            if hasattr(window, "close"):
                window.close()

    def processEvents(self):
        """Process pending events."""
        pass  # Mock implementation

    def exec(self) -> int:
        """Execute the application event loop."""
        return 0  # Mock implementation

    def setActiveWindow(self, window):
        """Set the active window."""
        self._active_window = window

    def activeWindow(self):
        """Get the active window."""
        return self._active_window


# Global framework instance
qt_mock_framework = QtMockFramework()
