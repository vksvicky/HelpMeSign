#!/usr/bin/env python3
"""
Global pytest configuration and fixtures
Ensures proper test isolation and prevents tests from modifying real user data
"""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def isolate_user_config():
    """
    Automatically isolate all tests from the real user configuration
    This fixture runs for ALL tests to prevent any accidental modification of real user data
    """
    # Create a temporary directory for test config files
    temp_dir = tempfile.mkdtemp(prefix="helpmesign_test_")
    temp_config_dir = Path(temp_dir) / ".helpmesign"
    temp_config_dir.mkdir(parents=True, exist_ok=True)

    # Mock the home directory to use our temp directory
    with patch("pathlib.Path.home") as mock_home:
        mock_home.return_value = Path(temp_dir)

        # Also mock os.path.expanduser to be safe
        with patch("os.path.expanduser") as mock_expanduser:
            mock_expanduser.side_effect = lambda path: str(
                Path(temp_dir) / path.lstrip("~/")
            )

            try:
                yield temp_config_dir
            finally:
                # Clean up temp files and directory
                try:
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception as e:
                    # Log but don't fail the test
                    print(f"Warning: Could not clean up temp directory {temp_dir}: {e}")


@pytest.fixture
def mock_secure_config():
    """
    Fixture that provides a fully mocked SecureConfigManager
    Use this for tests that need to control configuration behavior precisely
    """
    from unittest.mock import MagicMock

    mock_manager = MagicMock()
    mock_manager.load_config.return_value = {
        "user_mode": "Learn Sign Language",
        "theme": "Light",
        "font_size": 12,
        "hand_preference": "right",
        "selected_language": "ASL",
    }
    mock_manager.save_config.return_value = True
    mock_manager.get_user_mode.return_value = "Learn Sign Language"
    mock_manager.get_theme.return_value = "Light"
    mock_manager.get_font_size.return_value = 12
    mock_manager.get_hand_preference.return_value = "right"
    mock_manager.get_all_settings.return_value = {
        "user_mode": "Learn Sign Language",
        "theme": "Light",
        "font_size": 12,
        "hand_preference": "right",
        "selected_language": "ASL",
    }

    with patch("src.helpmesign.core.startup.SecureConfigManager") as mock_class:
        mock_class.return_value = mock_manager
        yield mock_manager


@pytest.fixture
def isolated_config_manager(isolate_user_config):
    """
    Fixture that provides a real SecureConfigManager instance but isolated to a temp directory
    Use this for integration tests that need real config file operations
    """
    from src.helpmesign.core.startup import SecureConfigManager

    # The isolate_user_config fixture will already have set up the temp directory
    # So we can just create a real instance and it will use the temp directory
    manager = SecureConfigManager()
    return manager


# Ensure tests don't accidentally import and use real functions without mocking
def pytest_runtest_setup(item):
    """
    Hook that runs before each test to add additional safety checks
    """
    # Add environment variable to indicate we're in test mode
    os.environ["HELPMESIGN_TEST_MODE"] = "true"


def pytest_runtest_teardown(item):
    """
    Hook that runs after each test to clean up
    """
    # Remove test mode indicator
    if "HELPMESIGN_TEST_MODE" in os.environ:
        del os.environ["HELPMESIGN_TEST_MODE"]
