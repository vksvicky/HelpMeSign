"""
HelpMeSign - A Python GUI application for text processing and management
"""

__version__ = "1.0.0"
__author__ = "HelpMeSign Team"
__description__ = "A simple Python GUI application built with PySide6"

# Try to import PySide6-dependent modules, but handle missing dependencies gracefully
try:
    from .core.app import HelpMeSignApp

    __all__ = ["HelpMeSignApp"]
except ImportError:
    # In CI environments or when PySide6 is not available, don't import GUI components
    __all__ = []
