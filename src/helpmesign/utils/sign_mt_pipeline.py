#!/usr/bin/env python3
"""
Sign.mt Compatible Pipeline
Follows the Text → SignWriting → Pose Sequence architecture
"""

import json
import os
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

from .resource_manager import ResourceManager


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

        # SignWriting dictionary (word -> symbols)
        self.signwriting_dictionary = self._load_signwriting_dictionary()

        # Pose templates (symbol -> pose data)
        self.pose_templates = self._load_pose_templates()

        # Neutral pose
        self.neutral_pose = self._get_neutral_pose()

    def _load_signwriting_dictionary(self) -> Dict[str, List[SignWritingSymbol]]:
        """Load SignWriting dictionary for text-to-symbol conversion"""
        dictionary = {}

        # ASL SignWriting mappings (following sign.mt approach)
        dictionary["WELCOME"] = [
            SignWritingSymbol("S10000", HandSide.BOTH, 1000, "Welcome sign")
        ]

        dictionary["TO"] = [SignWritingSymbol("S20500", HandSide.RIGHT, 500, "To sign")]

        dictionary["HELP"] = [
            SignWritingSymbol("S30000", HandSide.BOTH, 800, "Help sign")
        ]

        dictionary["ME"] = [SignWritingSymbol("S40000", HandSide.RIGHT, 600, "Me sign")]

        dictionary["SIGN"] = [
            SignWritingSymbol("S50000", HandSide.BOTH, 1000, "Sign language")
        ]

        dictionary["HELPMESIGN"] = [
            SignWritingSymbol("S10000", HandSide.BOTH, 800, "Help"),
            SignWritingSymbol("S50000", HandSide.BOTH, 800, "Sign"),
        ]

        return dictionary

    def _load_pose_templates(self) -> Dict[str, Dict[str, List[float]]]:
        """Load pose templates for SignWriting symbols"""
        templates: Dict[str, Dict[str, List[float]]] = {}

        # S10000 - Welcome sign (open hands, arms forward)
        templates["S10000"] = {
            "mixamorig:RightArm": [0, 90, 0],
            "mixamorig:LeftArm": [0, 90, 0],
            "mixamorig:RightForeArm": [0, 0, 0],
            "mixamorig:LeftForeArm": [0, 0, 0],
            "mixamorig:RightHand": [0, 0, 0],
            "mixamorig:LeftHand": [0, 0, 0],
            # Fingers extended
            "mixamorig:RightHandIndex1": [0, 0, 0],
            "mixamorig:RightHandIndex2": [0, 0, 0],
            "mixamorig:RightHandIndex3": [0, 0, 0],
            "mixamorig:RightHandMiddle1": [0, 0, 0],
            "mixamorig:RightHandMiddle2": [0, 0, 0],
            "mixamorig:RightHandMiddle3": [0, 0, 0],
            "mixamorig:RightHandRing1": [0, 0, 0],
            "mixamorig:RightHandRing2": [0, 0, 0],
            "mixamorig:RightHandRing3": [0, 0, 0],
            "mixamorig:RightHandPinky1": [0, 0, 0],
            "mixamorig:RightHandPinky2": [0, 0, 0],
            "mixamorig:RightHandPinky3": [0, 0, 0],
            "mixamorig:LeftHandIndex1": [0, 0, 0],
            "mixamorig:LeftHandIndex2": [0, 0, 0],
            "mixamorig:LeftHandIndex3": [0, 0, 0],
            "mixamorig:LeftHandMiddle1": [0, 0, 0],
            "mixamorig:LeftHandMiddle2": [0, 0, 0],
            "mixamorig:LeftHandMiddle3": [0, 0, 0],
            "mixamorig:LeftHandRing1": [0, 0, 0],
            "mixamorig:LeftHandRing2": [0, 0, 0],
            "mixamorig:LeftHandRing3": [0, 0, 0],
            "mixamorig:LeftHandPinky1": [0, 0, 0],
            "mixamorig:LeftHandPinky2": [0, 0, 0],
            "mixamorig:LeftHandPinky3": [0, 0, 0],
        }

        # S20500 - Pointing sign (index finger extended)
        templates["S20500"] = {
            "mixamorig:RightArm": [0, 90, 0],
            "mixamorig:LeftArm": [0, 0, 0],  # Left arm down
            "mixamorig:RightForeArm": [0, 0, 0],
            "mixamorig:LeftForeArm": [0, 0, 0],
            "mixamorig:RightHand": [0, 0, 0],
            "mixamorig:LeftHand": [0, 0, 0],
            # Right hand - index pointing, others closed
            "mixamorig:RightHandIndex1": [0, 0, 0],
            "mixamorig:RightHandIndex2": [0, 0, 0],
            "mixamorig:RightHandIndex3": [0, 0, 0],
            "mixamorig:RightHandMiddle1": [0, -45, 0],
            "mixamorig:RightHandMiddle2": [0, -45, 0],
            "mixamorig:RightHandMiddle3": [0, -45, 0],
            "mixamorig:RightHandRing1": [0, -45, 0],
            "mixamorig:RightHandRing2": [0, -45, 0],
            "mixamorig:RightHandRing3": [0, -45, 0],
            "mixamorig:RightHandPinky1": [0, -45, 0],
            "mixamorig:RightHandPinky2": [0, -45, 0],
            "mixamorig:RightHandPinky3": [0, -45, 0],
            # Left hand - neutral
            "mixamorig:LeftHandIndex1": [0, -10, 0],
            "mixamorig:LeftHandIndex2": [0, -10, 0],
            "mixamorig:LeftHandIndex3": [0, -10, 0],
            "mixamorig:LeftHandMiddle1": [0, -10, 0],
            "mixamorig:LeftHandMiddle2": [0, -10, 0],
            "mixamorig:LeftHandMiddle3": [0, -10, 0],
            "mixamorig:LeftHandRing1": [0, -10, 0],
            "mixamorig:LeftHandRing2": [0, -10, 0],
            "mixamorig:LeftHandRing3": [0, -10, 0],
            "mixamorig:LeftHandPinky1": [0, -10, 0],
            "mixamorig:LeftHandPinky2": [0, -10, 0],
            "mixamorig:LeftHandPinky3": [0, -10, 0],
        }

        # S30000 - Help sign (open hands, palms up)
        templates["S30000"] = {
            "mixamorig:RightArm": [0, 90, 0],
            "mixamorig:LeftArm": [0, 90, 0],
            "mixamorig:RightForeArm": [0, 0, 0],
            "mixamorig:LeftForeArm": [0, 0, 0],
            "mixamorig:RightHand": [0, 0, 90],  # Palm up
            "mixamorig:LeftHand": [0, 0, 90],  # Palm up
            # Fingers extended
            "mixamorig:RightHandIndex1": [0, 0, 0],
            "mixamorig:RightHandIndex2": [0, 0, 0],
            "mixamorig:RightHandIndex3": [0, 0, 0],
            "mixamorig:RightHandMiddle1": [0, 0, 0],
            "mixamorig:RightHandMiddle2": [0, 0, 0],
            "mixamorig:RightHandMiddle3": [0, 0, 0],
            "mixamorig:RightHandRing1": [0, 0, 0],
            "mixamorig:RightHandRing2": [0, 0, 0],
            "mixamorig:RightHandRing3": [0, 0, 0],
            "mixamorig:RightHandPinky1": [0, 0, 0],
            "mixamorig:RightHandPinky2": [0, 0, 0],
            "mixamorig:RightHandPinky3": [0, 0, 0],
            "mixamorig:LeftHandIndex1": [0, 0, 0],
            "mixamorig:LeftHandIndex2": [0, 0, 0],
            "mixamorig:LeftHandIndex3": [0, 0, 0],
            "mixamorig:LeftHandMiddle1": [0, 0, 0],
            "mixamorig:LeftHandMiddle2": [0, 0, 0],
            "mixamorig:LeftHandMiddle3": [0, 0, 0],
            "mixamorig:LeftHandRing1": [0, 0, 0],
            "mixamorig:LeftHandRing2": [0, 0, 0],
            "mixamorig:LeftHandRing3": [0, 0, 0],
            "mixamorig:LeftHandPinky1": [0, 0, 0],
            "mixamorig:LeftHandPinky2": [0, 0, 0],
            "mixamorig:LeftHandPinky3": [0, 0, 0],
        }

        # S40000 - Me sign (point to chest)
        templates["S40000"] = {
            "mixamorig:RightArm": [0, 45, 0],  # Arm pointing to chest
            "mixamorig:LeftArm": [0, 0, 0],
            "mixamorig:RightForeArm": [0, 0, 0],
            "mixamorig:LeftForeArm": [0, 0, 0],
            "mixamorig:RightHand": [0, 0, 0],
            "mixamorig:LeftHand": [0, 0, 0],
            # Index pointing
            "mixamorig:RightHandIndex1": [0, 0, 0],
            "mixamorig:RightHandIndex2": [0, 0, 0],
            "mixamorig:RightHandIndex3": [0, 0, 0],
            "mixamorig:RightHandMiddle1": [0, -45, 0],
            "mixamorig:RightHandMiddle2": [0, -45, 0],
            "mixamorig:RightHandMiddle3": [0, -45, 0],
            "mixamorig:RightHandRing1": [0, -45, 0],
            "mixamorig:RightHandRing2": [0, -45, 0],
            "mixamorig:RightHandRing3": [0, -45, 0],
            "mixamorig:RightHandPinky1": [0, -45, 0],
            "mixamorig:RightHandPinky2": [0, -45, 0],
            "mixamorig:RightHandPinky3": [0, -45, 0],
            # Left hand neutral
            "mixamorig:LeftHandIndex1": [0, -10, 0],
            "mixamorig:LeftHandIndex2": [0, -10, 0],
            "mixamorig:LeftHandIndex3": [0, -10, 0],
            "mixamorig:LeftHandMiddle1": [0, -10, 0],
            "mixamorig:LeftHandMiddle2": [0, -10, 0],
            "mixamorig:LeftHandMiddle3": [0, -10, 0],
            "mixamorig:LeftHandRing1": [0, -10, 0],
            "mixamorig:LeftHandRing2": [0, -10, 0],
            "mixamorig:LeftHandRing3": [0, -10, 0],
            "mixamorig:LeftHandPinky1": [0, -10, 0],
            "mixamorig:LeftHandPinky2": [0, -10, 0],
            "mixamorig:LeftHandPinky3": [0, -10, 0],
        }

        # S50000 - Sign language (V hand)
        templates["S50000"] = {
            "mixamorig:RightArm": [0, 90, 0],
            "mixamorig:LeftArm": [0, 90, 0],
            "mixamorig:RightForeArm": [0, 0, 0],
            "mixamorig:LeftForeArm": [0, 0, 0],
            "mixamorig:RightHand": [0, 0, 0],
            "mixamorig:LeftHand": [0, 0, 0],
            # V hand - index and middle extended
            "mixamorig:RightHandIndex1": [0, 0, 0],
            "mixamorig:RightHandIndex2": [0, 0, 0],
            "mixamorig:RightHandIndex3": [0, 0, 0],
            "mixamorig:RightHandMiddle1": [0, 0, 0],
            "mixamorig:RightHandMiddle2": [0, 0, 0],
            "mixamorig:RightHandMiddle3": [0, 0, 0],
            "mixamorig:RightHandRing1": [0, -45, 0],
            "mixamorig:RightHandRing2": [0, -45, 0],
            "mixamorig:RightHandRing3": [0, -45, 0],
            "mixamorig:RightHandPinky1": [0, -45, 0],
            "mixamorig:RightHandPinky2": [0, -45, 0],
            "mixamorig:RightHandPinky3": [0, -45, 0],
            "mixamorig:LeftHandIndex1": [0, 0, 0],
            "mixamorig:LeftHandIndex2": [0, 0, 0],
            "mixamorig:LeftHandIndex3": [0, 0, 0],
            "mixamorig:LeftHandMiddle1": [0, 0, 0],
            "mixamorig:LeftHandMiddle2": [0, 0, 0],
            "mixamorig:LeftHandMiddle3": [0, 0, 0],
            "mixamorig:LeftHandRing1": [0, -45, 0],
            "mixamorig:LeftHandRing2": [0, -45, 0],
            "mixamorig:LeftHandRing3": [0, -45, 0],
            "mixamorig:LeftHandPinky1": [0, -45, 0],
            "mixamorig:LeftHandPinky2": [0, -45, 0],
            "mixamorig:LeftHandPinky3": [0, -45, 0],
        }

        return templates

    def _get_neutral_pose(self) -> Dict[str, List[float]]:
        """Get neutral pose with arms at sides"""
        return {
            "mixamorig:RightArm": [0, 0, 0],
            "mixamorig:LeftArm": [0, 0, 0],
            "mixamorig:RightForeArm": [0, 0, 0],
            "mixamorig:LeftForeArm": [0, 0, 0],
            "mixamorig:RightHand": [0, 0, 0],
            "mixamorig:LeftHand": [0, 0, 0],
            # Fingers slightly curved
            "mixamorig:RightHandIndex1": [0, -10, 0],
            "mixamorig:RightHandIndex2": [0, -10, 0],
            "mixamorig:RightHandIndex3": [0, -10, 0],
            "mixamorig:RightHandMiddle1": [0, -10, 0],
            "mixamorig:RightHandMiddle2": [0, -10, 0],
            "mixamorig:RightHandMiddle3": [0, -10, 0],
            "mixamorig:RightHandRing1": [0, -10, 0],
            "mixamorig:RightHandRing2": [0, -10, 0],
            "mixamorig:RightHandRing3": [0, -10, 0],
            "mixamorig:RightHandPinky1": [0, -10, 0],
            "mixamorig:RightHandPinky2": [0, -10, 0],
            "mixamorig:RightHandPinky3": [0, -10, 0],
            "mixamorig:LeftHandIndex1": [0, -10, 0],
            "mixamorig:LeftHandIndex2": [0, -10, 0],
            "mixamorig:LeftHandIndex3": [0, -10, 0],
            "mixamorig:LeftHandMiddle1": [0, -10, 0],
            "mixamorig:LeftHandMiddle2": [0, -10, 0],
            "mixamorig:LeftHandMiddle3": [0, -10, 0],
            "mixamorig:LeftHandRing1": [0, -10, 0],
            "mixamorig:LeftHandRing2": [0, -10, 0],
            "mixamorig:LeftHandRing3": [0, -10, 0],
            "mixamorig:LeftHandPinky1": [0, -10, 0],
            "mixamorig:LeftHandPinky2": [0, -10, 0],
            "mixamorig:LeftHandPinky3": [0, -10, 0],
        }

    def text_to_pose_sequence(self, text: str) -> PoseSequence:
        """Main pipeline: Text → SignWriting → Pose Sequence"""
        # Step 1: Normalize text
        normalized_text = self._normalize_text(text)

        # Step 2: Convert to SignWriting symbols
        symbols = self._text_to_signwriting(normalized_text)

        # Step 3: Convert symbols to pose sequence
        pose_sequence = self._signwriting_to_pose_sequence(symbols)

        return pose_sequence

    def _normalize_text(self, text: str) -> str:
        """Normalize input text"""
        return text.strip().upper()

    def _text_to_signwriting(self, text: str) -> List[SignWritingSymbol]:
        """Convert text to SignWriting symbols"""
        words = text.split()
        symbols = []

        for word in words:
            if word in self.signwriting_dictionary:
                symbols.extend(self.signwriting_dictionary[word])
            else:
                # Fallback: spell out unknown words
                for letter in word:
                    if letter in self.signwriting_dictionary:
                        symbols.extend(self.signwriting_dictionary[letter])

        return symbols

    def _signwriting_to_pose_sequence(
        self, symbols: List[SignWritingSymbol]
    ) -> PoseSequence:
        """Convert SignWriting symbols to pose sequence"""
        frames: List[PoseFrame] = []
        current_time = 0
        fps = 30

        for symbol in symbols:
            # Get pose for this symbol
            pose = self._get_pose_for_symbol(symbol)

            # Calculate frames for this symbol
            frame_count = int((symbol.duration_ms / 1000.0) * fps)

            for i in range(frame_count):
                frame = PoseFrame(
                    frame_number=len(frames), pose=pose, timestamp_ms=current_time
                )
                frames.append(frame)
                current_time += int(1000 / fps)

        return PoseSequence(frames=frames, total_duration_ms=current_time, fps=fps)

    # Public wrappers to avoid accessing private methods in callers
    def text_to_signwriting(self, text: str) -> List[SignWritingSymbol]:
        return self._text_to_signwriting(self._normalize_text(text))

    def signwriting_to_pose_sequence(
        self, symbols: List[SignWritingSymbol]
    ) -> PoseSequence:
        return self._signwriting_to_pose_sequence(symbols)

    def _get_pose_for_symbol(self, symbol: SignWritingSymbol) -> Dict[str, List[float]]:
        """Get pose data for a SignWriting symbol"""
        if symbol.code in self.pose_templates:
            base_pose = self.pose_templates[symbol.code].copy()

            # Apply hand-side specific modifications
            if symbol.hand_side == HandSide.LEFT:
                # Mirror right hand poses to left hand
                base_pose = self._mirror_pose_to_left(base_pose)
            elif symbol.hand_side == HandSide.RIGHT:
                # Keep right hand only, set left to neutral
                base_pose = self._set_left_hand_neutral(base_pose)

            return base_pose

        # Fallback to neutral pose
        return self.neutral_pose.copy()

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
        """Get neutral pose"""
        return self.neutral_pose.copy()

    def set_language(self, language: str):
        """Set the current sign language"""
        # For now, we only have ASL mappings
        # In the future, this would load different SignWriting dictionaries
        self.current_language = language if language == "ASL" else self.default_language
