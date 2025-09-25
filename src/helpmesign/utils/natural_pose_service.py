"""
Natural Pose Service

This service provides the natural pose data for the character.
The natural pose is a hands-down relaxed stance.
"""

from typing import Any, Dict


class NaturalPoseService:
    """Service to manage natural pose data for character."""

    def __init__(self):
        """Initialize the natural pose service."""
        self._initialize()

    def _initialize(self):
        """Initialize the service if not already done."""
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self._natural_pose_data = self._create_natural_pose_data()

    def _create_natural_pose_data(self) -> Dict[str, Dict[str, Any]]:
        """Create the natural pose data for the character (natural human stance)."""
        return {
            "mixamorig:Hips": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:Spine": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:Head": {"hpr": [0.0, 19.2, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:Neck": {"hpr": [0.0, 23.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftShoulder": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightShoulder": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            # Arms hanging naturally at sides with slight bend
            "mixamorig:LeftArm": {"hpr": [0.0, 81.4, -30.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightArm": {"hpr": [0.0, 77.1, 21.4], "pos": [0.0, 0.0, 0.0]},
            # Forearms slightly bent for natural arm position
            "mixamorig:LeftForeArm": {"hpr": [0.0, 4.3, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightForeArm": {"hpr": [0.0, 8.6, 0.0], "pos": [0.0, 0.0, 0.0]},
            # Hands relaxed, palms facing body
            "mixamorig:LeftHand": {"hpr": [12.9, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightHand": {"hpr": [-8.6, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            # Thumb joints (all 3)
            "mixamorig:LeftHandThumb1": {
                "hpr": [0.0, 20.0, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:LeftHandThumb2": {
                "hpr": [0.0, 15.0, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:LeftHandThumb3": {
                "hpr": [0.0, 10.0, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:RightHandThumb1": {
                "hpr": [0.0, 10.3, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:RightHandThumb2": {
                "hpr": [0.0, 8.0, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:RightHandThumb3": {
                "hpr": [0.0, 5.0, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            # Index finger joints (all 3)
            "mixamorig:LeftHandIndex1": {
                "hpr": [0.0, 12.9, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:LeftHandIndex2": {
                "hpr": [0.0, 10.0, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:LeftHandIndex3": {
                "hpr": [0.0, 8.0, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:RightHandIndex1": {
                "hpr": [0.0, 8.6, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:RightHandIndex2": {
                "hpr": [0.0, 6.5, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:RightHandIndex3": {
                "hpr": [0.0, 4.5, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            # Middle finger joints (all 3)
            "mixamorig:LeftHandMiddle1": {
                "hpr": [0.0, 15.6, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:LeftHandMiddle2": {
                "hpr": [0.0, 12.0, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:LeftHandMiddle3": {
                "hpr": [0.0, 9.0, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:RightHandMiddle1": {
                "hpr": [0.0, 14.5, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:RightHandMiddle2": {
                "hpr": [0.0, 11.0, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:RightHandMiddle3": {
                "hpr": [0.0, 8.0, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            # Ring finger joints (all 3)
            "mixamorig:LeftHandRing1": {
                "hpr": [0.0, 12.9, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:LeftHandRing2": {
                "hpr": [0.0, 10.0, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:LeftHandRing3": {
                "hpr": [0.0, 7.5, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:RightHandRing1": {
                "hpr": [0.0, 12.9, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:RightHandRing2": {
                "hpr": [0.0, 10.0, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:RightHandRing3": {
                "hpr": [0.0, 7.5, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            # Pinky finger joints (all 3)
            "mixamorig:LeftHandPinky1": {
                "hpr": [0.0, 17.1, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:LeftHandPinky2": {
                "hpr": [0.0, 13.0, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:LeftHandPinky3": {
                "hpr": [0.0, 10.0, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:RightHandPinky1": {
                "hpr": [0.0, 4.3, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:RightHandPinky2": {
                "hpr": [0.0, 3.0, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:RightHandPinky3": {
                "hpr": [0.0, 2.0, 0.0],
                "pos": [0.0, 0.0, 0.0],
            },
            "mixamorig:LeftUpLeg": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightUpLeg": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:LeftFoot": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
            "mixamorig:RightFoot": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0]},
        }

    def get_natural_pose_data(self) -> Dict[str, Dict[str, Any]]:
        """Get the natural pose data in mixamorig format."""
        return self._natural_pose_data.copy()

    def get_all_body_parts_pose(self) -> Dict[str, Dict[str, Any]]:
        """Get pose data for all body parts using internal GLB viewer naming."""
        # Mapping from GLB viewer internal names to mixamorig names
        body_part_mapping = {
            "hips": "mixamorig:Hips",
            "spine": "mixamorig:Spine",
            "head": "mixamorig:Head",
            "neck": "mixamorig:Neck",
            "left_shoulder": "mixamorig:LeftShoulder",
            "right_shoulder": "mixamorig:RightShoulder",
            "left_arm": "mixamorig:LeftArm",
            "right_arm": "mixamorig:RightArm",
            "left_forearm": "mixamorig:LeftForeArm",
            "right_forearm": "mixamorig:RightForeArm",
            "left_hand": "mixamorig:LeftHand",
            "right_hand": "mixamorig:RightHand",
            # Individual finger joints (all 3 per finger)
            "left_fingers_thumb_base": "mixamorig:LeftHandThumb1",
            "right_fingers_thumb_base": "mixamorig:RightHandThumb1",
            "left_fingers_thumb_middle": "mixamorig:LeftHandThumb2",
            "right_fingers_thumb_middle": "mixamorig:RightHandThumb2",
            "left_fingers_thumb_tip": "mixamorig:LeftHandThumb3",
            "right_fingers_thumb_tip": "mixamorig:RightHandThumb3",
            "left_fingers_index_base": "mixamorig:LeftHandIndex1",
            "right_fingers_index_base": "mixamorig:RightHandIndex1",
            "left_fingers_index_middle": "mixamorig:LeftHandIndex2",
            "right_fingers_index_middle": "mixamorig:RightHandIndex2",
            "left_fingers_index_tip": "mixamorig:LeftHandIndex3",
            "right_fingers_index_tip": "mixamorig:RightHandIndex3",
            "left_fingers_middle_base": "mixamorig:LeftHandMiddle1",
            "right_fingers_middle_base": "mixamorig:RightHandMiddle1",
            "left_fingers_middle_middle": "mixamorig:LeftHandMiddle2",
            "right_fingers_middle_middle": "mixamorig:RightHandMiddle2",
            "left_fingers_middle_tip": "mixamorig:LeftHandMiddle3",
            "right_fingers_middle_tip": "mixamorig:RightHandMiddle3",
            "left_fingers_ring_base": "mixamorig:LeftHandRing1",
            "right_fingers_ring_base": "mixamorig:RightHandRing1",
            "left_fingers_ring_middle": "mixamorig:LeftHandRing2",
            "right_fingers_ring_middle": "mixamorig:RightHandRing2",
            "left_fingers_ring_tip": "mixamorig:LeftHandRing3",
            "right_fingers_ring_tip": "mixamorig:RightHandRing3",
            "left_fingers_pinky_base": "mixamorig:LeftHandPinky1",
            "right_fingers_pinky_base": "mixamorig:RightHandPinky1",
            "left_fingers_pinky_middle": "mixamorig:LeftHandPinky2",
            "right_fingers_pinky_middle": "mixamorig:RightHandPinky2",
            "left_fingers_pinky_tip": "mixamorig:LeftHandPinky3",
            "right_fingers_pinky_tip": "mixamorig:RightHandPinky3",
            "left_leg": "mixamorig:LeftUpLeg",
            "right_leg": "mixamorig:RightUpLeg",
            "left_foot": "mixamorig:LeftFoot",
            "right_foot": "mixamorig:RightFoot",
        }

        pose_data = {}
        for body_part, mixamorig_name in body_part_mapping.items():
            if mixamorig_name in self._natural_pose_data:
                data = self._natural_pose_data[mixamorig_name]
                pose_data[body_part] = {
                    "hpr": data["hpr"].copy(),
                    "xyz": data[
                        "pos"
                    ].copy(),  # Using 'xyz' for GLB viewer compatibility
                }
            else:
                # Return default values if not found
                pose_data[body_part] = {"hpr": [0.0, 0.0, 0.0], "xyz": [0.0, 0.0, 0.0]}

        return pose_data

    def get_pose_for_body_part(self, body_part: str) -> Dict[str, Any]:
        """Get pose data for a specific body part using internal GLB viewer naming."""
        all_poses = self.get_all_body_parts_pose()
        return all_poses.get(
            body_part, {"hpr": [0.0, 0.0, 0.0], "xyz": [0.0, 0.0, 0.0]}
        )
