#!/usr/bin/env python3
"""
Sign.mt Compatible Pipeline
Follows the Text → SignWriting → Pose Sequence architecture
Integrates with https://github.com/sign/ ecosystem
"""

import json
import os
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

from .resource_manager import ResourceManager
from .sign_mt_real.asset_manager import AssetManager
from .sign_mt_real.pose_data_service import PoseDataService
from .sign_mt_integration import SignMTTranslator, SignLanguageType, SignSequence


class HandSide(Enum):
    """Which hand to use for signing"""

    RIGHT = "right"
    LEFT = "left"
    BOTH = "both"


@dataclass
class SignWritingSymbol:
    """SignWriting symbol representation"""

    code: str  # e.g., "S10000", "S20500"
    hand_side: HandSide
    duration_ms: int
    description: str = ""


@dataclass
class PoseFrame:
    """Single frame in a pose sequence"""

    frame_number: int
    pose: Dict[str, List[float]]  # joint_name -> [h, p, r]
    timestamp_ms: int


@dataclass
class PoseSequence:
    """Complete pose sequence for animation"""

    frames: List[PoseFrame]
    total_duration_ms: int
    fps: int = 30


class SignMTPipeline:
    """Sign.mt compatible text-to-pose pipeline"""

    def __init__(self, default_language: str = "ASL"):
        self.default_language = default_language
        self.current_language = default_language
        self.resource_manager = ResourceManager()

        # Initialize pose data service for neutral pose
        asset_manager = AssetManager()
        self.pose_data_service = PoseDataService(asset_manager)

        # Neutral pose from pose_data_service
        self.neutral_pose = self.pose_data_service.get_neutral_pose().joints
        
        # Initialize sign.mt translator
        self.sign_translator = SignMTTranslator(SignLanguageType.ASL)

    def _normalize_text(self, text: str) -> str:
        """Normalize input text"""
        return text.strip().upper()

    def _mirror_pose_to_left(
        self, pose: Dict[str, List[float]]
    ) -> Dict[str, List[float]]:
        """Mirror right hand poses to left hand"""
        mirrored = pose.copy()

        # Mirror arm positions
        if "mixamorig:RightArm" in pose:
            right_arm = pose["mixamorig:RightArm"]
            mirrored["mixamorig:LeftArm"] = [-right_arm[0], right_arm[1], -right_arm[2]]

        # Mirror forearm positions
        if "mixamorig:RightForeArm" in pose:
            right_forearm = pose["mixamorig:RightForeArm"]
            mirrored["mixamorig:LeftForeArm"] = [
                -right_forearm[0],
                right_forearm[1],
                -right_forearm[2],
            ]

        # Mirror hand positions
        if "mixamorig:RightHand" in pose:
            right_hand = pose["mixamorig:RightHand"]
            mirrored["mixamorig:LeftHand"] = [
                -right_hand[0],
                right_hand[1],
                -right_hand[2],
            ]

        # Mirror finger positions
        finger_mappings = [
            ("RightHandIndex", "LeftHandIndex"),
            ("RightHandMiddle", "LeftHandMiddle"),
            ("RightHandRing", "LeftHandRing"),
            ("RightHandPinky", "LeftHandPinky"),
            ("RightHandThumb", "LeftHandThumb"),
        ]

        for right_prefix, left_prefix in finger_mappings:
            for i in range(1, 4):  # 3 joints per finger
                right_joint = f"mixamorig:{right_prefix}{i}"
                left_joint = f"mixamorig:{left_prefix}{i}"

                if right_joint in pose:
                    right_values = pose[right_joint]
                    mirrored[left_joint] = [
                        -right_values[0],
                        right_values[1],
                        -right_values[2],
                    ]

        return mirrored

    def _set_left_hand_neutral(
        self, pose: Dict[str, List[float]]
    ) -> Dict[str, List[float]]:
        """Set left hand to neutral position"""
        neutral = self.neutral_pose

        # Set left hand joints to neutral
        left_joints = [
            "mixamorig:LeftArm",
            "mixamorig:LeftForeArm",
            "mixamorig:LeftHand",
            "mixamorig:LeftHandIndex1",
            "mixamorig:LeftHandIndex2",
            "mixamorig:LeftHandIndex3",
            "mixamorig:LeftHandMiddle1",
            "mixamorig:LeftHandMiddle2",
            "mixamorig:LeftHandMiddle3",
            "mixamorig:LeftHandRing1",
            "mixamorig:LeftHandRing2",
            "mixamorig:LeftHandRing3",
            "mixamorig:LeftHandPinky1",
            "mixamorig:LeftHandPinky2",
            "mixamorig:LeftHandPinky3",
            "mixamorig:LeftHandThumb1",
            "mixamorig:LeftHandThumb2",
            "mixamorig:LeftHandThumb3",
        ]

        for joint in left_joints:
            if joint in neutral:
                pose[joint] = neutral[joint]

        return pose

    def get_neutral_pose(self) -> Dict[str, List[float]]:
        """Get neutral pose from pose_data_service"""
        return self.pose_data_service.get_neutral_pose().joints

    def set_language(self, language: str):
        """Set the current sign language"""
        try:
            # Convert string to SignLanguageType enum
            lang_enum = SignLanguageType(language.lower())
            self.current_language = language
            self.sign_translator.set_language(lang_enum)
        except ValueError:
            # Fallback to ASL if language not supported
            self.current_language = self.default_language
            self.sign_translator.set_language(SignLanguageType.ASL)

    def text_to_pose_sequence(self, text: str) -> Optional[PoseSequence]:
        """Convert text to pose sequence using sign.mt integration"""
        try:
            # Use sign.mt translator to convert text to sign sequence
            sign_sequence = self.sign_translator.translate_text_to_signs(text)
            
            # Convert SignSequence to PoseSequence format
            frames = []
            for sign_frame in sign_sequence.frames:
                pose_frame = PoseFrame(
                    frame_number=sign_frame.frame_number,
                    pose=sign_frame.to_pose_dict(),
                    timestamp_ms=sign_frame.timestamp_ms
                )
                frames.append(pose_frame)
            
            return PoseSequence(
                frames=frames,
                total_duration_ms=sign_sequence.total_duration_ms,
                fps=30
            )
        except Exception as e:
            print(f"Error in text_to_pose_sequence: {e}")
            return None

    def text_to_signwriting(self, text: str) -> List[str]:
        """Convert text to SignWriting symbols"""
        try:
            # Placeholder implementation
            # In the real implementation, this would use a translation model
            return ["S5000"]  # Default hand shape
        except Exception as e:
            print(f"Error in text_to_signwriting: {e}")
            return []

    def signwriting_to_pose_sequence(self, signwriting: str) -> Optional[PoseSequence]:
        """Convert SignWriting to pose sequence"""
        try:
            # Placeholder implementation
            neutral_pose = self.get_neutral_pose()

            frame = PoseFrame(frame_number=0, pose=neutral_pose, timestamp_ms=0)

            return PoseSequence(frames=[frame], total_duration_ms=1000, fps=30)
        except Exception as e:
            print(f"Error in signwriting_to_pose_sequence: {e}")
            return None

    def _get_pose_for_symbol(self, symbol: str) -> Optional[Dict[str, List[float]]]:
        """Get pose for a SignWriting symbol"""
        try:
            # Placeholder implementation
            return self.get_neutral_pose()
        except Exception as e:
            print(f"Error in _get_pose_for_symbol: {e}")
            return None
