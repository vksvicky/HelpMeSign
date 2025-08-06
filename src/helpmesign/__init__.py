"""
HelpMeSign - A Python GUI application for text processing and management
"""

from typing import List

__version__ = "1.0.0"
__author__ = "HelpMeSign Team"
__description__ = "A simple Python GUI application built with PySide6"

# Expose submodules to make them importable
# This allows tests to import from src.helpmesign.core and src.helpmesign.utils
__all__: List[str] = ["core", "utils", "ui", "modes", "services"]


def get_app():
    """Get the HelpMeSignApp class if PySide6 is available"""
    try:
        from .core.app import HelpMeSignApp

        return HelpMeSignApp
    except ImportError:
        return None


# Make submodules available for import
# This is needed for tests that import from src.helpmesign.core, etc.
try:
    from . import core
except ImportError:
    pass

try:
    from . import utils
except ImportError:
    pass

try:
    from . import ui
except ImportError:
    pass

try:
    from . import modes
except ImportError:
    pass

try:
    from . import services
except ImportError:
    pass
