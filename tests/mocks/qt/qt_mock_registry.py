"""
Qt Mock Registry

Central registry for managing all Qt mocks and their states.
Provides mock verification, state management, and debugging tools.
"""

import threading
from typing import Any, Callable, Dict, Optional
from unittest.mock import MagicMock, Mock


class QtMockRegistry:
    """Central registry for Qt mocks and their states."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._mocks: Dict[str, Any] = {}
            self._mock_states: Dict[str, Dict[str, Any]] = {}
            self._verification_callbacks: Dict[str, Callable] = {}
            self._initialized = True

    def register_mock(
        self, name: str, mock: Any, state: Optional[Dict[str, Any]] = None
    ):
        """Register a Qt mock with optional initial state."""
        self._mocks[name] = mock
        self._mock_states[name] = state or {}

    def get_mock(self, name: str) -> Optional[Any]:
        """Get a registered mock by name."""
        return self._mocks.get(name)

    def get_mock_state(self, name: str) -> Dict[str, Any]:
        """Get the current state of a mock."""
        return self._mock_states.get(name, {})

    def update_mock_state(self, name: str, state_updates: Dict[str, Any]):
        """Update the state of a registered mock."""
        if name in self._mock_states:
            self._mock_states[name].update(state_updates)

    def register_verification_callback(self, name: str, callback: Callable):
        """Register a verification callback for a mock."""
        self._verification_callbacks[name] = callback

    def verify_mock(self, name: str, *args, **kwargs) -> bool:
        """Verify a mock using its registered callback."""
        if name in self._verification_callbacks:
            return self._verification_callbacks[name](*args, **kwargs)
        return True

    def reset_all_mocks(self):
        """Reset all registered mocks to their initial state."""
        for name, mock in self._mocks.items():
            if hasattr(mock, "reset_mock"):
                mock.reset_mock()
            if name in self._mock_states:
                # Restore initial state
                initial_state = self._mock_states[name]
                for attr, value in initial_state.items():
                    if hasattr(mock, attr):
                        setattr(mock, attr, value)

    def clear_all_mocks(self):
        """Clear all registered mocks."""
        self._mocks.clear()
        self._mock_states.clear()
        self._verification_callbacks.clear()

    def get_all_mocks(self) -> Dict[str, Any]:
        """Get all registered mocks."""
        return self._mocks.copy()

    def debug_mock(self, name: str) -> Dict[str, Any]:
        """Get debug information for a mock."""
        mock = self.get_mock(name)
        if mock is None:
            return {"error": f"Mock '{name}' not found"}

        debug_info = {
            "name": name,
            "type": type(mock).__name__,
            "state": self.get_mock_state(name),
            "call_count": getattr(mock, "call_count", 0),
            "call_args_list": getattr(mock, "call_args_list", []),
            "method_calls": getattr(mock, "method_calls", []),
        }

        return debug_info


# Global registry instance
qt_mock_registry = QtMockRegistry()
