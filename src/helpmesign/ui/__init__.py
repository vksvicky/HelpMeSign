# User interface module

# Expose submodules to make them importable
# This allows tests to import from src.helpmesign.ui.components, etc.
__all__ = ["components", "settings_dialog"]

# Make submodules available for import
# This is needed for tests that import from src.helpmesign.ui.components, etc.
try:
    from . import components
except ImportError:
    pass

try:
    from . import settings_dialog
except ImportError:
    pass
