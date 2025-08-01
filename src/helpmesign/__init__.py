"""
HelpMeSign - A Python GUI application for text processing and management
"""

from typing import List

__version__ = "1.0.0"
__author__ = "HelpMeSign Team"
__description__ = "A simple Python GUI application built with PySide6"

# Don't import PySide6-dependent modules at package level
# This prevents import errors in CI environments where GUI libraries are not available
__all__: List[str] = []


def get_app():
    """Get the HelpMeSignApp class if PySide6 is available"""
    try:
        from .core.app import HelpMeSignApp

        return HelpMeSignApp
    except ImportError:
        return None
