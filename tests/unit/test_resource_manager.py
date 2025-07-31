import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
import tempfile
import shutil
from pathlib import Path
import sys

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from helpmesign.utils.resource_manager import ResourceManager


class TestResourceManager(unittest.TestCase):
    """Test cases for ResourceManager class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create a fresh ResourceManager instance for each test
        self.resource_manager = ResourceManager()
    
    def tearDown(self):
        """Clean up after each test method"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_init_creates_directories(self):
        """Test that ResourceManager creates necessary directories on initialization"""
        # Happy path - directories should be created
        self.assertTrue(self.resource_manager.resources_dir.exists())
        self.assertTrue(self.resource_manager.images_dir.exists())
        self.assertTrue(self.resource_manager.data_dir.exists())
    
    def test_get_image_path(self):
        """Test get_image_path method"""
        # Happy path - should return correct path
        expected_path = str(self.resource_manager.images_dir / 'test.png')
        actual_path = self.resource_manager.get_image_path('test.png')
        self.assertEqual(actual_path, expected_path)
        
        # Boundary case - empty filename
        empty_path = self.resource_manager.get_image_path('')
        self.assertEqual(empty_path, str(self.resource_manager.images_dir / ''))
        
        # Boundary case - filename with spaces
        space_path = self.resource_manager.get_image_path('test file.png')
        self.assertEqual(space_path, str(self.resource_manager.images_dir / 'test file.png'))
    
    def test_get_data_path(self):
        """Test get_data_path method"""
        # Happy path - should return correct path
        expected_path = str(self.resource_manager.data_dir / 'config.json')
        actual_path = self.resource_manager.get_data_path('config.json')
        self.assertEqual(actual_path, expected_path)
        
        # Boundary case - nested path
        nested_path = self.resource_manager.get_data_path('subfolder/file.txt')
        self.assertEqual(nested_path, str(self.resource_manager.data_dir / 'subfolder/file.txt'))
    
    def test_load_config_success(self):
        """Test successful config loading"""
        # Happy path - valid JSON config
        test_config = {
            "app_name": "TestApp",
            "version": "1.0.0",
            "window_size": {"width": 800, "height": 600}
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(test_config))):
            with patch('pathlib.Path.exists', return_value=True):
                result = self.resource_manager.load_config()
                self.assertEqual(result, test_config)
    
    def test_load_config_file_not_found(self):
        """Test config loading when file doesn't exist"""
        # Negative case - file not found
        with patch('pathlib.Path.exists', return_value=False):
            result = self.resource_manager.load_config()
            self.assertEqual(result, {})
    
    def test_load_config_invalid_json(self):
        """Test config loading with invalid JSON"""
        # Error case - invalid JSON
        invalid_json = "{ invalid json content"
        
        with patch('builtins.open', mock_open(read_data=invalid_json)):
            with patch('pathlib.Path.exists', return_value=True):
                result = self.resource_manager.load_config()
                self.assertEqual(result, {})
    
    def test_load_config_permission_error(self):
        """Test config loading with permission error"""
        # Exception case - permission denied
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with patch('pathlib.Path.exists', return_value=True):
                result = self.resource_manager.load_config()
                self.assertEqual(result, {})
    
    def test_save_config_success(self):
        """Test successful config saving"""
        # Happy path - valid config data
        test_config = {"setting": "value"}
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.dump') as mock_json_dump:
                result = self.resource_manager.save_config(test_config)
                self.assertTrue(result)
                mock_json_dump.assert_called_once_with(test_config, mock_file(), indent=4, ensure_ascii=False)
    
    def test_save_config_io_error(self):
        """Test config saving with IO error"""
        # Exception case - IO error
        test_config = {"setting": "value"}
        
        with patch('builtins.open', side_effect=IOError("Disk full")):
            result = self.resource_manager.save_config(test_config)
            self.assertFalse(result)
    
    def test_list_images_empty_directory(self):
        """Test listing images in empty directory"""
        # Boundary case - empty directory
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.iterdir', return_value=[]):
                result = self.resource_manager.list_images()
                self.assertEqual(result, [])
    
    def test_list_images_with_files(self):
        """Test listing images with actual files"""
        # Happy path - directory with files
        # Create mock files with proper name attributes
        mock_icon = MagicMock()
        mock_icon.name = 'icon.png'
        mock_icon.is_file.return_value = True
        
        mock_background = MagicMock()
        mock_background.name = 'background.jpg'
        mock_background.is_file.return_value = True
        
        mock_subfolder = MagicMock()
        mock_subfolder.name = 'subfolder'
        mock_subfolder.is_file.return_value = False  # Directory
        
        mock_files = [mock_icon, mock_background, mock_subfolder]
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.iterdir', return_value=mock_files):
                result = self.resource_manager.list_images()
                # The result should be the actual file names, not mock objects
                expected = ['icon.png', 'background.jpg']
                self.assertEqual(result, expected)
    
    def test_list_images_directory_not_exists(self):
        """Test listing images when directory doesn't exist"""
        # Negative case - directory doesn't exist
        with patch('pathlib.Path.exists', return_value=False):
            result = self.resource_manager.list_images()
            self.assertEqual(result, [])
    
    def test_list_data_files(self):
        """Test listing data files"""
        # Happy path - data files exist
        # Create mock files with proper name attributes
        mock_config = MagicMock()
        mock_config.name = 'config.json'
        mock_config.is_file.return_value = True
        
        mock_data = MagicMock()
        mock_data.name = 'data.txt'
        mock_data.is_file.return_value = True
        
        mock_files = [mock_config, mock_data]
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.iterdir', return_value=mock_files):
                result = self.resource_manager.list_data_files()
                # The result should be the actual file names, not mock objects
                expected = ['config.json', 'data.txt']
                self.assertEqual(result, expected)
    
    def test_resource_exists_image_true(self):
        """Test resource_exists for existing image"""
        # Happy path - image exists
        with patch('pathlib.Path.exists', return_value=True):
            result = self.resource_manager.resource_exists('image', 'icon.png')
            self.assertTrue(result)
    
    def test_resource_exists_image_false(self):
        """Test resource_exists for non-existing image"""
        # Negative case - image doesn't exist
        with patch('pathlib.Path.exists', return_value=False):
            result = self.resource_manager.resource_exists('image', 'nonexistent.png')
            self.assertFalse(result)
    
    def test_resource_exists_data_true(self):
        """Test resource_exists for existing data file"""
        # Happy path - data file exists
        with patch('pathlib.Path.exists', return_value=True):
            result = self.resource_manager.resource_exists('data', 'config.json')
            self.assertTrue(result)
    
    def test_resource_exists_invalid_type(self):
        """Test resource_exists with invalid resource type"""
        # Error case - invalid resource type
        result = self.resource_manager.resource_exists('invalid', 'file.txt')
        self.assertFalse(result)
    
    def test_resource_exists_none_filename(self):
        """Test resource_exists with None filename"""
        # Boundary case - None filename
        result = self.resource_manager.resource_exists('image', None)
        self.assertFalse(result)
    
    def test_resource_exists_empty_filename(self):
        """Test resource_exists with empty filename"""
        # Boundary case - empty filename
        result = self.resource_manager.resource_exists('image', '')
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main() 