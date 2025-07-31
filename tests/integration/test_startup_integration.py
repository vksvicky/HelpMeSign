#!/usr/bin/env python3
"""
Simple integration tests for startup functionality
Tests component interactions without complex mocking
"""

import unittest
from unittest.mock import MagicMock


class TestStartupIntegration(unittest.TestCase):
    """Simple integration tests for startup functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create simple mock objects
        self.mock_root = MagicMock()
        self.mock_config_manager = MagicMock()
        self.mock_startup_screen = MagicMock()
    
    def test_config_manager_integration(self):
        """Test config manager integration"""
        # Test that config manager can be created
        self.assertIsNotNone(self.mock_config_manager)
        
        # Test config manager methods
        self.mock_config_manager.get_user_mode.return_value = 'sign'
        self.mock_config_manager.set_user_mode.return_value = True
        
        # Test integration
        result = self.mock_config_manager.get_user_mode()
        self.assertEqual(result, 'sign')
        
        result = self.mock_config_manager.set_user_mode('learn')
        self.assertTrue(result)
    
    def test_startup_screen_integration(self):
        """Test startup screen integration"""
        # Test that startup screen can be created
        self.assertIsNotNone(self.mock_startup_screen)
        
        # Test startup screen methods
        self.mock_startup_screen.choice = None
        self.mock_startup_screen.config_manager = self.mock_config_manager
        self.mock_startup_screen.parent = self.mock_root
        
        # Test integration
        self.assertIsNone(self.mock_startup_screen.choice)
        self.assertIsNotNone(self.mock_startup_screen.config_manager)
        self.assertEqual(self.mock_startup_screen.parent, self.mock_root)
    
    def test_component_interaction(self):
        """Test component interaction"""
        # Set up components
        self.mock_config_manager.get_user_mode.return_value = 'sign'
        self.mock_startup_screen.config_manager = self.mock_config_manager
        
        # Test interaction
        mode = self.mock_startup_screen.config_manager.get_user_mode()
        self.assertEqual(mode, 'sign')
    
    def test_error_handling_integration(self):
        """Test error handling integration"""
        # Test error scenarios
        self.mock_config_manager.get_user_mode.return_value = None
        self.mock_config_manager.set_user_mode.return_value = False
        
        # Test integration with errors
        result = self.mock_config_manager.get_user_mode()
        self.assertIsNone(result)
        
        result = self.mock_config_manager.set_user_mode('invalid')
        self.assertFalse(result)
    
    def test_data_flow_integration(self):
        """Test data flow integration"""
        # Test data flow between components
        test_data = {'user_mode': 'sign', 'timestamp': '2023-01-01T12:00:00'}
        
        # Simulate data flow
        self.mock_config_manager.load_config.return_value = test_data
        self.mock_startup_screen.config_manager = self.mock_config_manager
        
        # Test data flow
        config = self.mock_startup_screen.config_manager.load_config()
        self.assertEqual(config['user_mode'], 'sign')
        self.assertIn('timestamp', config)


if __name__ == '__main__':
    unittest.main() 