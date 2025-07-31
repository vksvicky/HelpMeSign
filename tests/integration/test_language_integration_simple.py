#!/usr/bin/env python3
"""
Simple integration tests for the language system
Tests integration with PySide6 components without causing segmentation faults
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Try to import PySide6 components, handle missing dependencies gracefully
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    PYSIDE6_AVAILABLE = True
except ImportError:
    # Mock PySide6 components for CI environments
    class QApplication:
        def __init__(self, argv=None):
            self.argv = argv or []
        
        @staticmethod
        def instance():
            return None
    
    class Qt:
        pass
    
    PYSIDE6_AVAILABLE = False

# Import our components
from helpmesign.utils.language_manager import get_text, get_list, get_dict
from helpmesign.ui.components import get_os_shortcuts


class TestLanguageIntegrationSimple(unittest.TestCase):
    """Simple integration tests for language system"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create QApplication if it doesn't exist
        if PYSIDE6_AVAILABLE:
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            else:
                self.app = QApplication.instance()
        else:
            self.app = QApplication()
    
    def test_language_system_integration(self):
        """Test that language system works with PySide6 components"""
        # Test that we can get text without errors
        app_name = get_text("app.name", "HelpMeSign")
        self.assertIsInstance(app_name, str)
        self.assertGreater(len(app_name), 0)
        
        # Test that we can get lists without errors
        tips = get_list("sign_language.learning.tips", ["Default tip"])
        self.assertIsInstance(tips, list)
        self.assertGreater(len(tips), 0)
        
        # Test that we can get dictionaries without errors
        shortcuts = get_dict("os_shortcuts.macos", {"cmd": "⌘"})
        self.assertIsInstance(shortcuts, dict)
        self.assertGreater(len(shortcuts), 0)
    
    def test_os_shortcuts_integration(self):
        """Test OS shortcuts integration"""
        # Test that OS shortcuts work
        shortcuts = get_os_shortcuts()
        self.assertIsInstance(shortcuts, dict)
        
        # Should have basic shortcuts
        self.assertIn("cmd", shortcuts)
        self.assertIn("option", shortcuts)
        self.assertIn("shift", shortcuts)
    
    def test_language_system_with_pyside6(self):
        """Test language system works alongside PySide6"""
        # Test that language functions work when QApplication is running
        if PYSIDE6_AVAILABLE:
            self.assertTrue(QApplication.instance() is not None)
        else:
            # Skip this test if PySide6 is not available
            self.skipTest("PySide6 not available in this environment")
        
        # Get some text
        text = get_text("ui.main_window.title", "Default Title")
        self.assertIsInstance(text, str)
        
        # Get some list data
        list_data = get_list("sign_language.learning.tips", ["Tip 1", "Tip 2"])
        self.assertIsInstance(list_data, list)
        
        # Get some dict data
        dict_data = get_dict("os_shortcuts.windows", {"cmd": "Ctrl"})
        self.assertIsInstance(dict_data, dict)
    
    def test_language_system_error_handling_integration(self):
        """Test language system error handling in integration"""
        # Test with invalid keys
        invalid_text = get_text("invalid.key", "Default Text")
        self.assertEqual(invalid_text, "Default Text")
        
        invalid_list = get_list("invalid.list", ["default"])
        self.assertEqual(invalid_list, ["default"])
        
        invalid_dict = get_dict("invalid.dict", {"default": "value"})
        self.assertEqual(invalid_dict, {"default": "value"})
    
    def test_language_system_performance_integration(self):
        """Test language system performance in integration"""
        # Test multiple calls to ensure no performance issues
        for i in range(100):
            text = get_text("app.name", "HelpMeSign")
            self.assertIsInstance(text, str)
            
            list_data = get_list("sign_language.learning.tips", ["Tip"])
            self.assertIsInstance(list_data, list)
            
            dict_data = get_dict("os_shortcuts.macos", {"cmd": "⌘"})
            self.assertIsInstance(dict_data, dict)


class TestLanguageSystemBoundaryConditionsIntegration(unittest.TestCase):
    """Integration tests for boundary conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create QApplication if it doesn't exist
        if PYSIDE6_AVAILABLE:
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            else:
                self.app = QApplication.instance()
        else:
            self.app = QApplication()
    
    def test_empty_strings_integration(self):
        """Test handling of empty strings in integration"""
        # Test with empty keys
        empty_text = get_text("", "Default")
        self.assertEqual(empty_text, "Default")
        
        # Test with None keys
        none_text = get_text(None, "Default")
        self.assertEqual(none_text, "Default")
    
    def test_unicode_integration(self):
        """Test unicode handling in integration"""
        # Test with unicode text
        unicode_text = get_text("app.name", "HelpMeSign 🎉")
        self.assertIsInstance(unicode_text, str)
        
        # Test with unicode in lists
        unicode_list = get_list("test.list", ["Item 1 🎉", "Item 2 🚀"])
        self.assertIsInstance(unicode_list, list)
        self.assertTrue(all(isinstance(item, str) for item in unicode_list))
    
    def test_large_data_integration(self):
        """Test handling of large data in integration"""
        # Test with large default values
        large_text = get_text("large.key", "A" * 10000)
        self.assertEqual(len(large_text), 10000)
        
        large_list = get_list("large.list", ["A" * 1000] * 100)
        self.assertEqual(len(large_list), 100)
        self.assertEqual(len(large_list[0]), 1000)


if __name__ == '__main__':
    unittest.main() 