"""
Test setup for HelpMeSign tests
Handles PySide6 initialization and language system setup
"""

import sys
import os
from unittest.mock import MagicMock, patch

# Try to import PySide6, but handle missing dependencies gracefully
try:
    from PySide6.QtWidgets import QApplication
    PYSIDE6_AVAILABLE = True
except ImportError as e:
    # Mock QApplication for CI environments where PySide6 is not available
    class QApplication:
        def __init__(self, argv=None):
            self.argv = argv or []
        
        @staticmethod
        def instance():
            return None
        
        def quit(self):
            pass
    
    PYSIDE6_AVAILABLE = False

# Global QApplication instance for tests
_qapp = None

def setup_qapplication():
    """Setup QApplication for tests if not already created"""
    global _qapp
    if _qapp is None:
        # Create QApplication if it doesn't exist
        if PYSIDE6_AVAILABLE and not QApplication.instance():
            _qapp = QApplication(sys.argv)
        else:
            _qapp = QApplication.instance() if PYSIDE6_AVAILABLE else QApplication()
    return _qapp

def teardown_qapplication():
    """Clean up QApplication after tests"""
    global _qapp
    if _qapp:
        _qapp.quit()
        _qapp = None

def mock_language_system():
    """Mock the language system for tests"""
    # Mock language manager to return predictable values
    mock_text = MagicMock(return_value="Test Text")
    mock_list = MagicMock(return_value=["Item 1", "Item 2"])
    mock_dict = MagicMock(return_value={"key": "value"})
    
    with patch('helpmesign.utils.language_manager.get_text', mock_text), \
         patch('helpmesign.utils.language_manager.get_list', mock_list), \
         patch('helpmesign.utils.language_manager.get_dict', mock_dict):
        yield mock_text, mock_list, mock_dict

def mock_font_system():
    """Mock the font system for tests"""
    # Mock font functions to return predictable values
    mock_font = MagicMock(return_value=("Arial", 12, 400, 0))
    
    with patch('helpmesign.utils.font_manager.get_title_font', mock_font), \
         patch('helpmesign.utils.font_manager.get_heading_font', mock_font), \
         patch('helpmesign.utils.font_manager.get_body_font', mock_font), \
         patch('helpmesign.utils.font_manager.get_label_font', mock_font), \
         patch('helpmesign.utils.font_manager.get_button_font', mock_font), \
         patch('helpmesign.utils.font_manager.get_input_font', mock_font), \
         patch('helpmesign.utils.font_manager.get_small_font', mock_font):
        yield mock_font

def mock_resource_system():
    """Mock the resource system for tests"""
    # Mock resource manager
    mock_resource_manager = MagicMock()
    mock_resource_manager.load_config.return_value = {
        "window_size": {"width": 800, "height": 600},
        "dev_window_size": {"width": 1000, "height": 800},
        "theme": "default",
        "logging": {"level": "INFO"}
    }
    mock_resource_manager.get_image_path.return_value = "/fake/path/icon.png"
    mock_resource_manager.resource_exists.return_value = True
    mock_resource_manager.save_config.return_value = True
    
    with patch('helpmesign.utils.resource_manager.ResourceManager', return_value=mock_resource_manager):
        yield mock_resource_manager

def mock_logging_system():
    """Mock the logging system for tests"""
    # Mock logger
    mock_logger = MagicMock()
    mock_logger.info = MagicMock()
    mock_logger.debug = MagicMock()
    mock_logger.warning = MagicMock()
    mock_logger.error = MagicMock()
    
    with patch('helpmesign.utils.logger.get_logger', return_value=mock_logger), \
         patch('helpmesign.utils.logger.setup_logging', return_value=mock_logger):
        yield mock_logger

def create_test_environment():
    """Create a complete test environment with all mocks"""
    # Setup QApplication
    qapp = setup_qapplication()
    
    # Setup all mocks
    language_mocks = mock_language_system()
    font_mocks = mock_font_system()
    resource_mocks = mock_resource_system()
    logging_mocks = mock_logging_system()
    
    return {
        'qapp': qapp,
        'language': language_mocks,
        'font': font_mocks,
        'resource': resource_mocks,
        'logging': logging_mocks
    } 