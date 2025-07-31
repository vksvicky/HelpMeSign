"""
Build scripts for HelpMeSign application
"""

__version__ = "1.0.0"
__author__ = "HelpMeSign Team"

# Available build scripts
BUILD_SCRIPTS = {
    'macos': 'build_macos_app.py',
    'windows': 'build_windows_exe.py',
    'all': 'build_all.py'
} 