#!/usr/bin/env python3
"""
Pose data service for HelpMeSign
Converts sign names to actual pose data for 3D character animation
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class PoseData:
    """Pose data for a single frame"""

    joints: Dict[str, List[float]]
    metadata: Optional[Dict] = None


class PoseDataService:
    """
    Service for managing pose data and converting sign names to poses
    """

    def __init__(self, data_path: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.data_path = data_path or Path("resources/data")
        self.pose_mappings: Dict = {}
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the pose data service"""
        if self._initialized:
            return

        self.logger.info("Initializing pose data service")

        # Load pose mappings
        self._load_pose_mappings()

        self._initialized = True
        self.logger.info("Pose data service initialized")

    def _load_pose_mappings(self) -> None:
        """Load pose mappings from data files"""
        try:
            # Load existing pose data if available
            pose_file = self.data_path / "poses/pose_mappings.json"
            if pose_file.exists():
                with open(pose_file, "r") as f:
                    self.pose_mappings = json.load(f)
                self.logger.info(f"Loaded {len(self.pose_mappings)} pose mappings")
            else:
                self.logger.info("No pose mappings found, using default poses")
                self._create_default_poses()

        except Exception as e:
            self.logger.error(f"Error loading pose mappings: {e}")
            self._create_default_poses()

    def _create_default_poses(self) -> None:
        """Create default pose mappings"""
        self.pose_mappings = {
            # Neutral pose
            "neutral": {
                "joints": {
                    "mixamorig:Head": [0, 0, 0],
                    "mixamorig:Neck": [0, 0, 0],
                    "mixamorig:RightShoulder": [0, 0, 0],
                    "mixamorig:LeftShoulder": [0, 0, 0],
                    "mixamorig:RightArm": [0, 0, 0],
                    "mixamorig:LeftArm": [0, 0, 0],
                    "mixamorig:RightForeArm": [0, 0, 0],
                    "mixamorig:LeftForeArm": [0, 0, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                    "mixamorig:LeftHand": [0, 0, 0],
                }
            },
            # Greeting poses
            "greeting_open_hand": {
                "joints": {
                    "mixamorig:Head": [0, 0, 0],
                    "mixamorig:Neck": [0, 0, 0],
                    "mixamorig:RightShoulder": [0, 0, 0],
                    "mixamorig:LeftShoulder": [0, 0, 0],
                    "mixamorig:RightArm": [0, 0, 0],
                    "mixamorig:LeftArm": [0, 0, 0],
                    "mixamorig:RightForeArm": [0, 0, 0],
                    "mixamorig:LeftForeArm": [0, 0, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                    "mixamorig:LeftHand": [0, 0, 0],
                }
            },
            # Gratitude poses
            "gratitude_hand_to_chin": {
                "joints": {
                    "mixamorig:Head": [0, 0, 0],
                    "mixamorig:Neck": [0, 0, 0],
                    "mixamorig:RightShoulder": [0, 0, 0],
                    "mixamorig:LeftShoulder": [0, 0, 0],
                    "mixamorig:RightArm": [0, 0, 0],
                    "mixamorig:LeftArm": [0, 0, 0],
                    "mixamorig:RightForeArm": [0, 0, 0],
                    "mixamorig:LeftForeArm": [0, 0, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                    "mixamorig:LeftHand": [0, 0, 0],
                }
            },
            # Farewell poses
            "farewell_wave": {
                "joints": {
                    "mixamorig:Head": [0, 0, 0],
                    "mixamorig:Neck": [0, 0, 0],
                    "mixamorig:RightShoulder": [0, 0, 0],
                    "mixamorig:LeftShoulder": [0, 0, 0],
                    "mixamorig:RightArm": [0, 0, 0],
                    "mixamorig:LeftArm": [0, 0, 0],
                    "mixamorig:RightForeArm": [0, 0, 0],
                    "mixamorig:LeftForeArm": [0, 0, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                    "mixamorig:LeftHand": [0, 0, 0],
                }
            },
            # Request poses
            "request_palm_up": {
                "joints": {
                    "mixamorig:Head": [0, 0, 0],
                    "mixamorig:Neck": [0, 0, 0],
                    "mixamorig:RightShoulder": [0, 0, 0],
                    "mixamorig:LeftShoulder": [0, 0, 0],
                    "mixamorig:RightArm": [0, 0, 0],
                    "mixamorig:LeftArm": [0, 0, 0],
                    "mixamorig:RightForeArm": [0, 0, 0],
                    "mixamorig:LeftForeArm": [0, 0, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                    "mixamorig:LeftHand": [0, 0, 0],
                }
            },
        }

    def get_pose(self, pose_name: str) -> Optional[PoseData]:
        """
        Get pose data for a given pose name

        Args:
            pose_name: Name of the pose to retrieve

        Returns:
            PoseData object or None if not found
        """
        if not self._initialized:
            self.initialize()

        if pose_name in self.pose_mappings:
            pose_data = self.pose_mappings[pose_name]
            return PoseData(
                joints=pose_data.get("joints", {}), metadata=pose_data.get("metadata")
            )

        self.logger.warning(f"Pose '{pose_name}' not found, using neutral pose")
        return self.get_pose("neutral")

    def get_pose_sequence(self, sign_name: str) -> List[PoseData]:
        """
        Get a sequence of poses for a sign

        Args:
            sign_name: Name of the sign

        Returns:
            List of PoseData objects
        """
        if not self._initialized:
            self.initialize()

        # Define pose sequences for different signs
        pose_sequences = {
            "greeting_open_hand": ["neutral", "greeting_open_hand", "neutral"],
            "gratitude_hand_to_chin": ["neutral", "gratitude_hand_to_chin", "neutral"],
            "farewell_wave": ["neutral", "farewell_wave", "neutral"],
            "request_palm_up": ["neutral", "request_palm_up", "neutral"],
        }

        # Get the sequence for this sign
        sequence_names = pose_sequences.get(sign_name, ["neutral"])

        # Convert to PoseData objects
        poses = []
        for pose_name in sequence_names:
            pose = self.get_pose(pose_name)
            if pose:
                poses.append(pose)

        return poses

    def get_neutral_pose(self) -> PoseData:
        """Get the neutral pose"""
        return self.get_pose("neutral") or PoseData(joints={})

    def save_pose_mappings(self) -> None:
        """Save pose mappings to file"""
        try:
            pose_dir = self.data_path / "poses"
            pose_dir.mkdir(parents=True, exist_ok=True)

            pose_file = pose_dir / "pose_mappings.json"
            with open(pose_file, "w") as f:
                json.dump(self.pose_mappings, f, indent=2)

            self.logger.info(f"Saved pose mappings to {pose_file}")

        except Exception as e:
            self.logger.error(f"Error saving pose mappings: {e}")


# Test function
def test_pose_data_service():
    """Test the pose data service"""
    service = PoseDataService()
    service.initialize()

    test_poses = [
        "neutral",
        "greeting_open_hand",
        "gratitude_hand_to_chin",
        "farewell_wave",
    ]

    print("Testing pose data service:")
    print("=" * 50)

    for pose_name in test_poses:
        pose = service.get_pose(pose_name)
        if pose:
            print(f"Pose '{pose_name}': {len(pose.joints)} joints")
        else:
            print(f"Pose '{pose_name}': Not found")

    print()

    # Test pose sequences
    test_signs = ["greeting_open_hand", "gratitude_hand_to_chin"]

    for sign_name in test_signs:
        sequence = service.get_pose_sequence(sign_name)
        print(f"Sign '{sign_name}': {len(sequence)} poses")

    print()


if __name__ == "__main__":
    test_pose_data_service()
