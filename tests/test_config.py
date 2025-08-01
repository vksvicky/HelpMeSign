"""
Test configuration and utilities for HelpMeSign tests
"""

import os
import shutil
import tempfile
from pathlib import Path

# Test configuration
TEST_CONFIG = {
    "temp_dir_prefix": "helpmesign_test_",
    "test_timeout": 30,  # seconds
    "max_test_retries": 3,
    "coverage_threshold": 80.0,  # minimum coverage percentage
}

# Test data
TEST_DATA = {
    "valid_config": {
        "app_name": "TestHelpMeSign",
        "version": "1.0.0",
        "window_size": {"width": 800, "height": 600},
        "theme": {"primary_color": "#3498db"},
    },
    "invalid_config": {"invalid_key": "invalid_value"},
    "sample_texts": [
        "Hello World",
        "Test with spaces",
        "Special chars: @#$%^&*()",
        "Unicode: émojis 🎉",
        "",  # Empty string
        "   ",  # Whitespace only
        "Very long text " * 100,  # Long text
    ],
}


class TestEnvironment:
    """Test environment setup and teardown utilities"""

    def __init__(self):
        self.test_dir = None
        self.original_cwd = None

    def setup(self):
        """Set up test environment"""
        self.original_cwd = os.getcwd()
        self.test_dir = tempfile.mkdtemp(prefix=TEST_CONFIG["temp_dir_prefix"])
        os.chdir(self.test_dir)

        # Create resource directories
        os.makedirs("resources/images", exist_ok=True)
        os.makedirs("resources/data", exist_ok=True)

        return self.test_dir

    def teardown(self):
        """Clean up test environment"""
        if self.original_cwd:
            os.chdir(self.original_cwd)
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def create_test_file(self, path, content=""):
        """Create a test file with given content"""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)
        return str(file_path)

    def create_test_config(self, config_data=None):
        """Create a test config file"""
        if config_data is None:
            config_data = TEST_DATA["valid_config"]

        import json

        config_path = "resources/data/config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=4)
        return config_path


def get_test_resource_path(resource_type, filename):
    """Get path for test resources"""
    base_path = Path(__file__).parent
    return str(base_path / resource_type / filename)


def assert_file_exists(file_path):
    """Assert that a file exists"""
    assert os.path.exists(file_path), f"File does not exist: {file_path}"


def assert_file_content(file_path, expected_content):
    """Assert file content matches expected content"""
    with open(file_path, "r") as f:
        actual_content = f.read()
    assert actual_content == expected_content, f"File content mismatch in {file_path}"


def create_mock_tkinter_root():
    """Create a mock tkinter root window for testing"""
    import tkinter as tk
    from unittest.mock import MagicMock

    mock_root = MagicMock(spec=tk.Tk)
    mock_root.winfo_screenwidth.return_value = 1920
    mock_root.winfo_screenheight.return_value = 1080
    mock_root.winfo_width.return_value = 1024
    mock_root.winfo_height.return_value = 1024

    return mock_root


# Test categories for organization
TEST_CATEGORIES = {
    "unit": "Unit tests for individual components",
    "integration": "Integration tests for component interaction",
    "mocks": "Mock-based tests for various scenarios",
    "performance": "Performance and stress tests",
    "ui": "User interface tests",
    "api": "API and external service tests",
}

# Test tags for filtering
TEST_TAGS = {
    "happy_path": "Tests normal operation",
    "error_handling": "Tests error conditions",
    "boundary": "Tests boundary conditions",
    "performance": "Tests performance characteristics",
    "security": "Tests security aspects",
    "accessibility": "Tests accessibility features",
}
