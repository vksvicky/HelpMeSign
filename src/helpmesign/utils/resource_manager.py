"""
Resource Manager for HelpMeSign Application
Handles loading and managing application resources (config, images, etc.)
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .logger import get_logger


class ResourceManager:
    """Manages application resources"""

    def __init__(self):
        self.logger = get_logger("helpmesign.resources")
        self.base_path = self._get_base_path()
        self.logger.debug(
            f"Resource manager initialized with base path: {self.base_path}"
        )

    def _get_base_path(self) -> Path:
        """Get the base path for resources"""
        # Try to find the project root
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent
        return project_root

    def get_resource_path(self, resource_type: str, filename: str) -> Path:
        """Get the full path to a resource file"""
        resource_dir = self.base_path / "resources" / resource_type
        return resource_dir / filename

    def resource_exists(self, resource_type: str, filename: str) -> bool:
        """Check if a resource file exists"""
        resource_path = self.get_resource_path(resource_type, filename)
        exists = resource_path.exists()
        self.logger.debug(f"Resource {resource_type}/{filename} exists: {exists}")
        return exists

    def get_image_path(self, filename: str) -> str:
        """Get the path to an image file"""
        return str(self.get_resource_path("images", filename))

    def get_data_path(self, filename: str) -> str:
        """Get the path to a data file"""
        return str(self.get_resource_path("data", filename))

    def get_model_path(self, filename: str) -> str:
        """Get the path to a model file (3D characters, animations)."""
        return str(self.get_resource_path("characters", filename))

    def load_config(self) -> Dict[str, Any]:
        """Load the application configuration"""
        config_path = self.get_data_path("config.json")
        self.logger.debug(f"Loading config from: {config_path}")

        try:
            if not os.path.exists(config_path):
                self.logger.warning(f"Config file not found: {config_path}")
                return self._get_default_config()

            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.logger.info("Configuration loaded successfully")
                return config

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file: {config_path}")
            return self._get_default_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return self._get_default_config()

    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        config_path = self.get_data_path("config.json")
        self.logger.debug(f"Saving config to: {config_path}")

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

            self.logger.info("Configuration saved successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        self.logger.info("Using default configuration")
        return {
            "app_name": "HelpMeSign",
            "version": "1.0.0",
            "window_size": {"width": 1024, "height": 1024},
            "dev_window_size": {"width": 1200, "height": 800},
            "logging": {"level": "INFO", "dev_level": "DEBUG", "file_enabled": True},
        }

    def get_resource_info(self) -> Dict[str, Any]:
        """Get information about available resources"""
        info: Dict[str, Any] = {"base_path": str(self.base_path), "resources": {}}

        resources_dir = self.base_path / "resources"
        if resources_dir.exists():
            for resource_type in ["images", "data", "fonts"]:
                type_dir = resources_dir / resource_type
                if type_dir.exists():
                    files: List[str] = [
                        f.name for f in type_dir.iterdir() if f.is_file()
                    ]
                    info["resources"][resource_type] = files
                else:
                    info["resources"][resource_type] = []
        else:
            info["resources"] = {"images": [], "data": [], "fonts": []}

        self.logger.debug(f"Resource info: {info}")
        return info
