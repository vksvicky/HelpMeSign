"""
Natural Pose Service - Centralized source of truth for character natural pose values.
Provides consistent natural pose data across all components.
"""

from typing import Dict, Any


class NaturalPoseService:
    """Service providing centralized natural pose values for the character."""
    
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self._natural_pose_data = self._create_natural_pose_data()
    
    def _create_natural_pose_data(self) -> Dict[str, Dict[str, Any]]:
        """Create the natural pose data for the character (hands-down pose)."""
        return {
            "mixamorig:Hips": {"hpr": [-90.4, -85.3, -87.6], "pos": [-0.0, 104.3, 1.6]},
            "mixamorig:Spine": {"hpr": [0.5, -8.0, -1.7], "pos": [-0.0, 0.0, 10.2]},
            "mixamorig:Spine1": {"hpr": [0.0, -0.0, 0.0], "pos": [-0.0, -0.0, 10.0]},
            "mixamorig:Spine2": {"hpr": [0.0, 0.0, 0.0], "pos": [-0.0, 0.0, 9.3]},
            "mixamorig:Neck": {"hpr": [0.3, -10.4, 0.4], "pos": [0.0, 0.0, 16.9]},
            "mixamorig:Head": {"hpr": [1.1, 4.3, 4.4], "pos": [-0.0, -2.8, 9.3]},
            "mixamorig:RightShoulder": {
                "hpr": [128.7, 76.7, 132.1],
                "pos": [-4.6, 0.8, 11.2],
            },
            "mixamorig:RightArm": {"hpr": [-56.0, 39.8, 52.3], "pos": [0.0, -0.0, 10.8]},
            "mixamorig:RightForeArm": {
                "hpr": [0.0, 0.0, 0.0],
                "pos": [-0.0, 0.0, 27.8],
            },
            "mixamorig:RightHand": {"hpr": [33.6, -19.6, 16.1], "pos": [0.0, -0.0, 28.3]},
            # Right hand fingers - natural relaxed position (straight, slightly spread)
            "mixamorig:RightHandThumb1": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHandThumb2": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHandThumb3": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHandThumb4": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHandIndex1": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHandIndex2": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHandIndex3": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHandIndex4": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHandMiddle1": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHandMiddle2": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHandMiddle3": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHandMiddle4": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHandRing1": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHandRing2": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHandRing3": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHandRing4": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHandPinky1": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHandPinky2": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHandPinky3": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHandPinky4": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftShoulder": {
                "hpr": [-123.9, 74.1, -139.7],
                "pos": [4.6, 0.8, 11.2],
            },
            "mixamorig:LeftArm": {"hpr": [48.6, 44.4, -52.1], "pos": [-0.0, -0.0, 10.8]},
            "mixamorig:LeftForeArm": {
                "hpr": [0.0, 0.0, 0.0],
                "pos": [-0.0, 0.0, 27.8],
            },
            "mixamorig:LeftHand": {"hpr": [-20.6, -8.6, -17.5], "pos": [0.0, -0.0, 28.3]},
            # Left hand fingers - natural relaxed position (straight, slightly spread)
            "mixamorig:LeftHandThumb1": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftHandThumb2": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftHandThumb3": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftHandThumb4": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftHandIndex1": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftHandIndex2": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftHandIndex3": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftHandIndex4": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftHandMiddle1": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftHandMiddle2": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftHandMiddle3": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftHandMiddle4": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftHandRing1": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftHandRing2": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftHandRing3": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftHandRing4": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftHandPinky1": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftHandPinky2": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftHandPinky3": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftHandPinky4": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
        }
    
    def get_natural_pose_data(self) -> Dict[str, Dict[str, Any]]:
        """Get the natural pose data."""
        return self._natural_pose_data.copy()
    
    def get_natural_pose_hpr(self, joint_name: str) -> tuple[float, float, float]:
        """Get the natural HPR values for a specific joint."""
        if joint_name in self._natural_pose_data:
            hpr = self._natural_pose_data[joint_name]["hpr"]
            return (float(hpr[0]), float(hpr[1]), float(hpr[2]))
        return (0.0, 0.0, 0.0)
    
    def get_natural_pose_pos(self, joint_name: str) -> tuple[float, float, float]:
        """Get the natural position values for a specific joint."""
        if joint_name in self._natural_pose_data:
            pos = self._natural_pose_data[joint_name]["pos"]
            return (float(pos[0]), float(pos[1]), float(pos[2]))
        return (0.0, 0.0, 0.0)
    
    def has_joint(self, joint_name: str) -> bool:
        """Check if a joint exists in the natural pose data."""
        return joint_name in self._natural_pose_data


# Global instance for easy access
_natural_pose_service = None


def get_natural_pose_service() -> NaturalPoseService:
    """Get the global natural pose service instance."""
    global _natural_pose_service
    if _natural_pose_service is None:
        _natural_pose_service = NaturalPoseService()
    return _natural_pose_service
