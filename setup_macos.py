#!/usr/bin/env python3
"""
Setup script for py2app
"""

from setuptools import setup

APP = ['main_prod.py']
DATA_FILES = [
    ('resources', [
        'resources/data/config.json',
        'resources/data/sample_data.txt',
        'resources/images/icon.png',
        'resources/fonts/Roboto-Regular.ttf',
        'resources/fonts/Roboto-Bold.ttf',
        'resources/fonts/Roboto-Light.ttf',
        'resources/fonts/Roboto-Medium.ttf',
        'resources/fonts/Roboto-Thin.ttf'
    ])
]

OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'resources/images/icon.png',
    'plist': {
        'CFBundleName': 'HelpMeSign',
        'CFBundleDisplayName': 'HelpMeSign',
        'CFBundleIdentifier': 'com.helpmesign.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
    },
    'packages': ['PySide6', 'helpmesign'],
    'includes': ['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets'],
    'excludes': ['tkinter', 'test', 'distutils'],
    'optimize': 2,
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
