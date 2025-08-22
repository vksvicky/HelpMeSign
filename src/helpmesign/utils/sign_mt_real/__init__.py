"""
Real sign.mt Architecture Implementation

This implements the actual sign.mt architecture as local modules:
1. Bergamot Translation Engine
2. SignWriting Translation Service
3. Pose Data from Real Lexicons
4. Model Registry and Asset Management
"""

from .asset_manager import AssetManager
from .bergamot_translator import BergamotTranslator
from .model_registry import ModelRegistry
from .pose_data_service import PoseDataService
from .signwriting_service import SignWritingService

__all__ = [
    "BergamotTranslator",
    "SignWritingService",
    "PoseDataService",
    "ModelRegistry",
    "AssetManager",
]
