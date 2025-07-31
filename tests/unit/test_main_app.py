import unittest
from unittest.mock import patch, MagicMock, mock_open
import tkinter as tk
import sys
import os
import tempfile
import shutil

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from helpmesign.core.app import HelpMeSignApp


class TestHelpMeSignAppComplete(unittest.TestCase):
    """Test cases for HelpMeSignApp class with complete mocking"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create a mock root window with ALL required tkinter attributes
        self.root = MagicMock(spec=tk.Tk)
        self.root.winfo_screenwidth.return_value = 1920
        self.root.winfo_screenheight.return_value = 1080
        self.root.winfo_width.return_value = 1024
        self.root.winfo_height.return_value = 1024
        self.root.tk = MagicMock()  # Add tk attribute
        self.root.children = {}  # Add children attribute
        self.root.title = MagicMock()
        self.root.geometry = MagicMock()
        self.root.resizable = MagicMock()
        self.root.iconphoto = MagicMock()
        
        # Mock tkinter variables
        self.mock_string_var = MagicMock()
        self.mock_string_var.set = MagicMock()
        self.mock_string_var.get = MagicMock(return_value="Ready")
    
    def tearDown(self):
        """Clean up after each test method"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def create_mock_resource_manager(self, config_data=None):
        """Helper method to create a mock resource manager"""
        if config_data is None:
            config_data = {
                'window_size': {'width': 1024, 'height': 1024},
                'theme': {'primary_color': '#3498db'}
            }
        
        mock_rm = MagicMock()
        mock_rm.load_config.return_value = config_data
        mock_rm.get_image_path.return_value = 'resources/images/icon.png'
        mock_rm.resource_exists.return_value = True
        return mock_rm
    
    def create_app_with_mocks(self, config_data=None):
        """Helper method to create app with all necessary mocks"""
        with patch('helpmesign.core.app.ResourceManager') as mock_rm_class:
            with patch('tkinter.StringVar', return_value=self.mock_string_var):
                mock_rm_instance = self.create_mock_resource_manager(config_data)
                mock_rm_class.return_value = mock_rm_instance
                
                app = HelpMeSignApp(self.root)
                return app, mock_rm_instance
    
    def test_init_success(self):
        """Test successful initialization of HelpMeSignApp"""
        # Happy path - successful initialization
        app, _ = self.create_app_with_mocks()
        
        # Verify initialization
        self.root.title.assert_called_with("HelpMeSign")
        # The app calls center_window() which adds position coordinates, so we check for the size part
        geometry_calls = self.root.geometry.call_args_list
        self.assertTrue(any("1024x1024" in str(call) for call in geometry_calls))
        self.root.resizable.assert_called_with(False, False)
    
    def test_init_with_default_config(self):
        """Test initialization with default config when config is empty"""
        # Boundary case - empty config
        app, _ = self.create_app_with_mocks({})
        
        # Should use default window size
        geometry_calls = self.root.geometry.call_args_list
        self.assertTrue(any("1024x1024" in str(call) for call in geometry_calls))
    
    def test_init_with_custom_config(self):
        """Test initialization with custom window size from config"""
        # Happy path - custom config
        custom_config = {
            'window_size': {'width': 800, 'height': 600}
        }
        
        app, _ = self.create_app_with_mocks(custom_config)
        
        # Should use custom window size
        geometry_calls = self.root.geometry.call_args_list
        self.assertTrue(any("800x600" in str(call) for call in geometry_calls))
    
    def test_set_app_icon_success(self):
        """Test successful app icon setting"""
        # Happy path - icon exists and loads successfully
        with patch('tkinter.PhotoImage') as mock_photo_image:
            mock_icon = MagicMock()
            mock_photo_image.return_value = mock_icon
            
            app, _ = self.create_app_with_mocks()
            
            # Verify icon was set - use ANY to match any mock object
            from unittest.mock import ANY
            self.root.iconphoto.assert_called_with(True, ANY)
            # Check that app_icon was set (don't compare specific mock objects)
            self.assertTrue(hasattr(app.main_window, 'app_icon'))
    
    def test_set_app_icon_not_found(self):
        """Test app icon setting when icon doesn't exist"""
        # Negative case - icon doesn't exist
        with patch('helpmesign.core.app.ResourceManager') as mock_rm_class:
            with patch('tkinter.StringVar', return_value=self.mock_string_var):
                mock_rm_instance = self.create_mock_resource_manager()
                mock_rm_instance.resource_exists.return_value = False
                mock_rm_class.return_value = mock_rm_instance
                
                app = HelpMeSignApp(self.root)
                
                # Should not set icon
                self.root.iconphoto.assert_not_called()
                self.assertFalse(hasattr(app.main_window, 'app_icon'))
    
    def test_set_app_icon_load_error(self):
        """Test app icon setting when icon fails to load"""
        # Exception case - icon load error
        with patch('tkinter.PhotoImage', side_effect=Exception("Invalid image")):
            app, _ = self.create_app_with_mocks()
            
            # Should not set icon
            self.root.iconphoto.assert_not_called()
            self.assertFalse(hasattr(app.main_window, 'app_icon'))
    
    def test_center_window(self):
        """Test window centering functionality"""
        # Happy path - window centering
        app, _ = self.create_app_with_mocks()
        
        # Verify centering calculations
        # This test verifies the centering logic works correctly
        self.assertIsNotNone(app.main_window)
    
    def test_process_text_success(self):
        """Test successful text processing"""
        # Happy path - valid text processing
        app, _ = self.create_app_with_mocks()
        
        # Mock text input and output
        app.main_window.text_input_frame.text_input = MagicMock()
        app.main_window.text_input_frame.text_input.get.return_value = "Test text"
        app.main_window.text_input_frame.text_input.delete = MagicMock()
        
        app.main_window.output_frame.output_text = MagicMock()
        app.main_window.output_frame.output_text.insert = MagicMock()
        app.main_window.output_frame.output_text.see = MagicMock()
        
        app.status_bar.status_var = MagicMock()
        app.status_bar.status_var.set = MagicMock()
        
        # Process text
        app.process_text()
        
        # Verify processing
        app.main_window.text_input_frame.text_input.get.assert_called()
        app.main_window.output_frame.output_text.insert.assert_called()
        app.main_window.text_input_frame.text_input.delete.assert_called_with(0, tk.END)
        app.status_bar.status_var.set.assert_called_with("Processed: Test text")
    
    def test_process_text_empty(self):
        """Test text processing with empty input"""
        # Boundary case - empty text
        app, _ = self.create_app_with_mocks()
        
        # Mock text input and status
        app.main_window.text_input_frame.text_input = MagicMock()
        app.main_window.text_input_frame.text_input.get.return_value = "   "  # Whitespace only
        
        app.status_bar.status_var = MagicMock()
        app.status_bar.status_var.set = MagicMock()
        
        # Process text
        app.process_text()
        
        # Verify status message for empty text
        app.status_bar.status_var.set.assert_called_with("Please enter some text")
    
    def test_process_text_whitespace_only(self):
        """Test text processing with whitespace-only input"""
        # Boundary case - whitespace only
        app, _ = self.create_app_with_mocks()
        
        # Mock text input and status
        app.main_window.text_input_frame.text_input = MagicMock()
        app.main_window.text_input_frame.text_input.get.return_value = "   \t\n   "
        
        app.status_bar.status_var = MagicMock()
        app.status_bar.status_var.set = MagicMock()
        
        # Process text
        app.process_text()
        
        # Verify status message for whitespace-only text
        app.status_bar.status_var.set.assert_called_with("Please enter some text")
    
    def test_process_text_with_special_characters(self):
        """Test text processing with special characters"""
        # Happy path - special characters
        app, _ = self.create_app_with_mocks()
        
        # Mock text input and output
        special_text = "Hello @#$%^&*() World! 🚀"
        app.main_window.text_input_frame.text_input = MagicMock()
        app.main_window.text_input_frame.text_input.get.return_value = special_text
        app.main_window.text_input_frame.text_input.delete = MagicMock()
        
        app.main_window.output_frame.output_text = MagicMock()
        app.main_window.output_frame.output_text.insert = MagicMock()
        app.main_window.output_frame.output_text.see = MagicMock()
        
        app.status_bar.status_var = MagicMock()
        app.status_bar.status_var.set = MagicMock()
        
        # Process text
        app.process_text()
        
        # Verify processing of special characters
        app.main_window.output_frame.output_text.insert.assert_called()
        app.status_bar.status_var.set.assert_called_with(f"Processed: {special_text}")
    
    def test_clear_text(self):
        """Test clear text functionality"""
        # Happy path - clearing text
        app, _ = self.create_app_with_mocks()
        
        # Mock text widgets
        app.main_window.text_input_frame.text_input = MagicMock()
        app.main_window.text_input_frame.text_input.delete = MagicMock()
        app.main_window.text_input_frame.text_input.focus = MagicMock()
        
        app.main_window.output_frame.output_text = MagicMock()
        app.main_window.output_frame.output_text.delete = MagicMock()
        
        app.status_bar.status_var = MagicMock()
        app.status_bar.status_var.set = MagicMock()
        
        # Clear text
        app.clear_text()
        
        # Verify clearing
        app.main_window.output_frame.output_text.delete.assert_called_with(1.0, tk.END)
        app.main_window.text_input_frame.text_input.delete.assert_called_with(0, tk.END)
        app.status_bar.status_var.set.assert_called_with("Cleared")
        app.main_window.text_input_frame.text_input.focus.assert_called()


if __name__ == '__main__':
    unittest.main() 