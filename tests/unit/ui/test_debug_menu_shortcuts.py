#!/usr/bin/env python3
"""Unit tests for OS-specific keyboard shortcuts"""

import platform
from unittest.mock import patch


def get_os_shortcuts():
    """Get OS-specific keyboard shortcut symbols"""
    system = platform.system().lower()
    if system == "darwin":  # macOS
        return {"cmd": "⌘", "shift": "⇧", "enter": "⏎", "question": "?"}
    else:  # Windows/Linux
        return {"cmd": "Ctrl", "shift": "Shift", "enter": "Enter", "question": "?"}


class TestOSShortcuts:
    """Test OS-specific keyboard shortcut functionality"""

    def test_get_os_shortcuts_darwin(self):
        """Test macOS shortcut symbols"""
        with patch("platform.system", return_value="Darwin"):
            shortcuts = get_os_shortcuts()
            assert shortcuts["cmd"] == "⌘"
            assert shortcuts["shift"] == "⇧"
            assert shortcuts["enter"] == "⏎"
            assert shortcuts["question"] == "?"

    def test_get_os_shortcuts_windows(self):
        """Test Windows shortcut symbols"""
        with patch("platform.system", return_value="Windows"):
            shortcuts = get_os_shortcuts()
            assert shortcuts["cmd"] == "Ctrl"
            assert shortcuts["shift"] == "Shift"
            assert shortcuts["enter"] == "Enter"
            assert shortcuts["question"] == "?"

    def test_get_os_shortcuts_linux(self):
        """Test Linux shortcut symbols"""
        with patch("platform.system", return_value="Linux"):
            shortcuts = get_os_shortcuts()
            assert shortcuts["cmd"] == "Ctrl"
            assert shortcuts["shift"] == "Shift"
            assert shortcuts["enter"] == "Enter"
            assert shortcuts["question"] == "?"

    def test_shortcuts_structure(self):
        """Test that shortcuts dictionary has expected keys"""
        shortcuts = get_os_shortcuts()
        expected_keys = {"cmd", "shift", "enter", "question"}
        assert set(shortcuts.keys()) == expected_keys

    def test_shortcuts_not_empty(self):
        """Test that shortcuts dictionary is not empty"""
        shortcuts = get_os_shortcuts()
        assert len(shortcuts) > 0
        for key, value in shortcuts.items():
            assert isinstance(value, str)
            assert len(value) > 0
