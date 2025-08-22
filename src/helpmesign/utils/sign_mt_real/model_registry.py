"""
Model Registry - Following sign.mt patterns

This manages model registration and loading following their ModelRegistry
"""

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .asset_manager import AssetManager


@dataclass
class ModelInfo:
    """Model information following sign.mt patterns"""

    name: str
    path: str
    size: int
    estimated_compressed_size: int
    model_type: str = "prod"


class ModelRegistry:
    """
    Model Registry following sign.mt patterns

    From their ModelRegistry interface - manages bergamot models
    """

    def __init__(self, asset_manager: AssetManager):
        self.logger = logging.getLogger(__name__)
        self.asset_manager = asset_manager
        self._loaded_models: Dict[str, Dict[str, ModelInfo]] = {}

    def create_model_registry(self, model_path: str) -> Dict[str, ModelInfo]:
        """
        Create model registry following sign.mt patterns

        From their createModelRegistry method
        """
        try:
            model_registry = {}
            model_files = self.asset_manager.get_directory(model_path)

            for filename, file_path in model_files.items():
                # Extract file type from extension
                file_type = filename.split(".")[0] if "." in filename else filename

                # Get file stats
                stats = self.asset_manager.stat(file_path)
                size = stats.get("size", 0)

                model_info = ModelInfo(
                    name=file_path,
                    path=file_path,
                    size=size,
                    estimated_compressed_size=size,  # Placeholder
                    model_type="prod",
                )

                model_registry[file_type] = model_info

            self.logger.info(
                f"Created model registry for {model_path}: {len(model_registry)} files"
            )
            return model_registry

        except Exception as e:
            self.logger.error(f"Error creating model registry for {model_path}: {e}")
            return {}

    def load_model(self, model_name: str, model_registry: Dict[str, ModelInfo]) -> bool:
        """
        Load model into registry following sign.mt patterns
        """
        try:
            self._loaded_models[model_name] = model_registry
            self.logger.info(
                f"Loaded model {model_name} with {len(model_registry)} files"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error loading model {model_name}: {e}")
            return False

    def get_model(self, model_name: str) -> Optional[Dict[str, ModelInfo]]:
        """
        Get loaded model following sign.mt patterns
        """
        return self._loaded_models.get(model_name)

    def is_model_loaded(self, model_name: str) -> bool:
        """
        Check if model is loaded following sign.mt patterns
        """
        return model_name in self._loaded_models

    def list_loaded_models(self) -> List[str]:
        """
        List loaded models following sign.mt patterns
        """
        return list(self._loaded_models.keys())

    def unload_model(self, model_name: str) -> bool:
        """
        Unload model following sign.mt patterns
        """
        try:
            if model_name in self._loaded_models:
                del self._loaded_models[model_name]
                self.logger.info(f"Unloaded model {model_name}")
                return True
            return False

        except Exception as e:
            self.logger.error(f"Error unloading model {model_name}: {e}")
            return False

    def get_model_info(self, model_name: str, file_type: str) -> Optional[ModelInfo]:
        """
        Get specific model file info following sign.mt patterns
        """
        try:
            model = self._loaded_models.get(model_name)
            if model:
                return model.get(file_type)
            return None

        except Exception as e:
            self.logger.error(
                f"Error getting model info for {model_name}/{file_type}: {e}"
            )
            return None
