import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
import sys
import os
import tempfile
import shutil
import json

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from helpmesign.core.app import HelpMeSignApp
from helpmesign.utils.resource_manager import ResourceManager


class TestAppIntegration(unittest.TestCase):
    """Integration tests for HelpMeSign application"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create actual resource directories
        os.makedirs('resources/images', exist_ok=True)
        os.makedirs('resources/data', exist_ok=True)
        
        # Create a test config file
        self.test_config = {
            "app_name": "TestHelpMeSign",
            "version": "1.0.0",
            "window_size": {"width": 800, "height": 600},
            "theme": {"primary_color": "#3498db"}
        }
        
        with open('resources/data/config.json', 'w') as f:
            json.dump(self.test_config, f)
    
    def create_mock_root(self):
        """Helper method to create a mock root window with all required attributes"""
        root = MagicMock(spec=tk.Tk)
        root.winfo_screenwidth.return_value = 1920
        root.winfo_screenheight.return_value = 1080
        root.winfo_width.return_value = 800
        root.winfo_height.return_value = 600
        root.tk = MagicMock()  # Add tk attribute
        root.children = {}  # Add children attribute
        return root
    
    def create_app_with_mocks(self, root=None):
        """Helper method to create app with all necessary mocks"""
        if root is None:
            root = self.create_mock_root()
        
        # Mock PhotoImage for icon
        mock_icon = MagicMock()
        with patch('tkinter.PhotoImage', return_value=mock_icon):
            with patch('tkinter.StringVar') as mock_string_var:
                mock_var = MagicMock()
                mock_var.set = MagicMock()
                mock_var.get = MagicMock(return_value="Ready")
                mock_string_var.return_value = mock_var
                
                app = HelpMeSignApp(root)
                return app, root
    
    def tearDown(self):
        """Clean up after each test method"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_resource_manager_with_real_files(self):
        """Test ResourceManager with actual file system"""
        # Happy path - real file system integration
        rm = ResourceManager()
        
        # Test config loading
        config = rm.load_config()
        self.assertEqual(config, self.test_config)
        
        # Test path generation
        image_path = rm.get_image_path('test.png')
        # The path will be absolute in the test environment, so check if it ends with the expected relative path
        self.assertTrue(image_path.endswith('resources/images/test.png'))
        
        # Test resource existence
        self.assertTrue(rm.resource_exists('data', 'config.json'))
        self.assertFalse(rm.resource_exists('image', 'nonexistent.png'))
    
    def test_app_with_real_resource_manager(self):
        """Test HelpMeSignApp with real ResourceManager"""
        # Integration test - app with real resource manager
        root = MagicMock(spec=tk.Tk)
        root.winfo_screenwidth.return_value = 1920
        root.winfo_screenheight.return_value = 1080
        root.winfo_width.return_value = 800
        root.winfo_height.return_value = 600
        root.tk = MagicMock()  # Add tk attribute
        root.children = {}  # Add children attribute
        
        # Mock PhotoImage for icon
        mock_icon = MagicMock()
        with patch('tkinter.PhotoImage', return_value=mock_icon):
            with patch('tkinter.StringVar') as mock_string_var:
                mock_var = MagicMock()
                mock_var.set = MagicMock()
                mock_var.get = MagicMock(return_value="Ready")
                mock_string_var.return_value = mock_var
                
                app = HelpMeSignApp(root)
            
                    # Verify app loaded config from real resource manager
        self.assertEqual(app.config, self.test_config)
        
        # Verify window size from config (accounting for center_window)
        geometry_calls = root.geometry.call_args_list
        self.assertTrue(any("800x600" in str(call) for call in geometry_calls))
    
    def test_config_save_and_load_integration(self):
        """Test config save and load integration"""
        # Integration test - save and load cycle
        rm = ResourceManager()
        
        # Save new config
        new_config = {"test_setting": "test_value"}
        success = rm.save_config(new_config)
        self.assertTrue(success)
        
        # Load config back
        loaded_config = rm.load_config()
        self.assertEqual(loaded_config, new_config)
    
    def test_app_with_missing_resources(self):
        """Test app behavior with missing resources"""
        # Negative case - missing resources
        # Remove config file
        os.remove('resources/data/config.json')
        
        app, root = self.create_app_with_mocks()
        
        # Should use default config when file is missing
        self.assertEqual(app.config, {})
        
        # Should use default window size (accounting for center_window)
        geometry_calls = root.geometry.call_args_list
        self.assertTrue(any("1024x1024" in str(call) for call in geometry_calls))
    
    def test_app_with_corrupted_config(self):
        """Test app behavior with corrupted config file"""
        # Error case - corrupted config
        # Write invalid JSON
        with open('resources/data/config.json', 'w') as f:
            f.write('{ invalid json content')
        
        app, root = self.create_app_with_mocks()
        
        # Should use default config when JSON is invalid
        self.assertEqual(app.config, {})
        
        # Should use default window size (accounting for center_window)
        geometry_calls = root.geometry.call_args_list
        self.assertTrue(any("1024x1024" in str(call) for call in geometry_calls))
    
    def test_resource_manager_directory_creation(self):
        """Test ResourceManager creates directories when they don't exist"""
        # Happy path - automatic directory creation
        # Remove directories
        shutil.rmtree('resources', ignore_errors=True)
        
        # Create new ResourceManager (should create directories)
        rm = ResourceManager()
        
        # Verify directories were created
        self.assertTrue(rm.resources_dir.exists())
        self.assertTrue(rm.images_dir.exists())
        self.assertTrue(rm.data_dir.exists())
    
    def test_app_with_icon_file(self):
        """Test app with actual icon file"""
        # Integration test - real icon file
        # Create a simple test icon file
        with open('resources/images/icon.png', 'w') as f:
            f.write('fake png content')
        
        # Mock PhotoImage to return a mock icon
        mock_icon = MagicMock()
        with patch('tkinter.PhotoImage', return_value=mock_icon):
            app, root = self.create_app_with_mocks()
            
            # Verify icon was set - use ANY to match any mock object
            from unittest.mock import ANY
            root.iconphoto.assert_called_with(True, ANY)
            # Check that app_icon was set (don't compare specific mock objects)
            self.assertTrue(hasattr(app.main_window, 'app_icon'))
    
    def test_app_without_icon_file(self):
        """Test app behavior when icon file is missing"""
        # Negative case - missing icon file
        app, root = self.create_app_with_mocks()
        
        # Should not set icon when file doesn't exist
        root.iconphoto.assert_not_called()
        self.assertFalse(hasattr(app.main_window, 'app_icon'))


if __name__ == '__main__':
    unittest.main() 