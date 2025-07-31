import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class ResourceManager:
    """Utility class for managing application resources"""
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize ResourceManager
        
        Args:
            base_path: Base path for resources (defaults to current directory)
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.resources_dir = self.base_path / 'resources'
        self.images_dir = self.resources_dir / 'images'
        self.data_dir = self.resources_dir / 'data'
        
        # Ensure directories exist
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def get_image_path(self, filename: str) -> str:
        """
        Get the full path to an image file
        
        Args:
            filename: Name of the image file
            
        Returns:
            Full path to the image file
        """
        return str(self.images_dir / filename)
    
    def get_data_path(self, filename: str) -> str:
        """
        Get the full path to a data file
        
        Args:
            filename: Name of the data file
            
        Returns:
            Full path to the data file
        """
        return str(self.data_dir / filename)
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from config.json
        
        Returns:
            Configuration dictionary, empty dict if loading fails
        """
        config_path = self.get_data_path('config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file not found: {config_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Invalid JSON in config file: {config_path}")
            return {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """
        Save configuration to config.json
        
        Args:
            config_data: Configuration data to save
            
        Returns:
            True if successful, False otherwise
        """
        config_path = self.get_data_path('config.json')
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def list_images(self) -> List[str]:
        """
        List all image files in the images directory
        
        Returns:
            List of image filenames
        """
        if self.images_dir.exists():
            return [f.name for f in self.images_dir.iterdir() if f.is_file()]
        return []
    
    def list_data_files(self) -> List[str]:
        """
        List all data files in the data directory
        
        Returns:
            List of data filenames
        """
        if self.data_dir.exists():
            return [f.name for f in self.data_dir.iterdir() if f.is_file()]
        return []
    
    def resource_exists(self, resource_type: str, filename: str) -> bool:
        """
        Check if a resource file exists
        
        Args:
            resource_type: Type of resource ('image' or 'data')
            filename: Name of the file
            
        Returns:
            True if resource exists, False otherwise
        """
        if not filename:
            return False
            
        if resource_type == 'image':
            return (self.images_dir / filename).exists()
        elif resource_type == 'data':
            return (self.data_dir / filename).exists()
        return False
    
    def create_resource_directories(self) -> None:
        """Create resource directories if they don't exist"""
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def get_resource_info(self) -> Dict[str, Any]:
        """
        Get information about available resources
        
        Returns:
            Dictionary with resource information
        """
        return {
            'images': self.list_images(),
            'data_files': self.list_data_files(),
            'images_dir': str(self.images_dir),
            'data_dir': str(self.data_dir),
            'resources_dir': str(self.resources_dir)
        } 