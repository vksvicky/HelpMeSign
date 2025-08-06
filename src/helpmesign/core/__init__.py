# Core functionality module

# Expose submodules to make them importable
# This allows tests to import from src.helpmesign.core.app, etc.
__all__ = ["app", "startup"]

# Make submodules available for import
# This is needed for tests that import from src.helpmesign.core.app, etc.
try:
    from . import app
except ImportError:
    pass

try:
    from . import startup
except ImportError:
    pass
