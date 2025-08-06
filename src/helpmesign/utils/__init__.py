# Utilities module

# Expose submodules to make them importable
# This allows tests to import from src.helpmesign.utils.*, etc.
__all__ = [
    "language_manager",
    "language_loader",
    "theme_manager",
    "font_manager",
    "system_monitor",
    "resource_manager",
    "logger",
]

# Make submodules available for import
# This is needed for tests that import from src.helpmesign.utils.*, etc.
try:
    from . import language_manager
except ImportError:
    pass

try:
    from . import language_loader
except ImportError:
    pass

try:
    from . import theme_manager
except ImportError:
    pass

try:
    from . import font_manager
except ImportError:
    pass

try:
    from . import system_monitor
except ImportError:
    pass

try:
    from . import resource_manager
except ImportError:
    pass

try:
    from . import logger
except ImportError:
    pass
