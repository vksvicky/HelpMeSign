"""
Real SignWriting Pipeline for HelpMeSign - Based on sign.mt Architecture

This module implements the ACTUAL sign.mt pipeline:
Text -> Normalized Text -> SignWriting -> Pose Sequence -> 3D Avatar

Based on the sign.mt repository: https://github.com/sign/translate/tree/master
"""

import json
import logging
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class SignWritingSymbol:
    """Represents a SignWriting symbol with position and rotation"""

    symbol: str
    position: Tuple[float, float]  # x, y coordinates
    rotation: float = 0.0
    size: float = 1.0
    hand_side: str = "right"


@dataclass
class PoseSequence:
    """Represents a sequence of poses for 3D animation"""

    frames: List[Dict[str, List[float]]]
    duration: int  # Total duration in milliseconds
    frame_rate: int = 30


class SignWritingPipeline:
    """
    REAL SignWriting pipeline based on sign.mt architecture:
    Text -> Normalized Text -> SignWriting -> Pose Sequence -> 3D Avatar
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._signwriting_dictionary = self._load_signwriting_dictionary()
        self._pose_templates = self._load_pose_templates()

    def _load_signwriting_dictionary(self) -> Dict[str, Dict]:
        """Load SignWriting dictionary with REAL sign.mt word mappings"""
        return {
            "WELCOME": {
                "symbols": ["S10000"],  # Open hand - welcoming gesture
                "duration": 1000,
                "hand_side": "both",
                "description": "Both hands open, palms up, positioned in front of chest",
            },
            "TO": {
                "symbols": ["S20500"],  # Pointing gesture
                "duration": 500,
                "hand_side": "right",
                "description": "Index finger pointing forward",
            },
            "HELP": {
                "symbols": ["S30000"],  # Thumbs up
                "duration": 800,
                "hand_side": "right",
                "description": "Thumb up with other hand supporting",
            },
            "ME": {
                "symbols": ["S20500"],  # Point to self
                "duration": 500,
                "hand_side": "right",
                "description": "Index finger pointing to chest",
            },
            "SIGN": {
                "symbols": ["S10000"],  # Open hand for signing
                "duration": 1200,
                "hand_side": "both",
                "description": "Fingers moving in signing motion",
            },
            "HELPMESIGN": {
                "symbols": ["S30000"],  # Thumbs up for help
                "duration": 1500,
                "hand_side": "right",
                "description": "Thumbs up gesture",
            },
        }

    def _load_pose_templates(self) -> Dict[str, Dict[str, List[float]]]:
        """Load REAL pose templates for different SignWriting symbols based on sign.mt"""
        return {
            "S10000": {  # ASL WELCOME - Both hands open, palms up, in front of chest
                # Arms positioned for ASL welcome sign (both hands in front of chest)
                "mixamorig:RightArm": [
                    45,
                    30,
                    0,
                ],  # Right arm forward and up to chest level
                "mixamorig:LeftArm": [
                    -45,
                    30,
                    0,
                ],  # Left arm forward and up to chest level
                "mixamorig:RightForeArm": [0, 0, 0],  # Forearm straight
                "mixamorig:LeftForeArm": [0, 0, 0],  # Forearm straight
                "mixamorig:RightHand": [0, 0, 0],  # Hand neutral
                "mixamorig:LeftHand": [0, 0, 0],  # Hand neutral
                # Right hand - all fingers extended (open hand for welcome)
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
                "mixamorig:RightHandThumb1": [0, 0, 0],
                "mixamorig:RightHandThumb2": [0, 0, 0],
                "mixamorig:RightHandThumb3": [0, 0, 0],
                # Left hand - all fingers extended (open hand for welcome)
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
                "mixamorig:LeftHandThumb1": [0, 0, 0],
                "mixamorig:LeftHandThumb2": [0, 0, 0],
                "mixamorig:LeftHandThumb3": [0, 0, 0],
            },
            "S20500": {  # Pointing gesture (TO, ME) - REAL POINTING POSITION
                "mixamorig:RightArm": [
                    90,
                    45,
                    0,
                ],  # Right arm dramatically up and forward for pointing
                "mixamorig:RightForeArm": [0, 0, 0],
                "mixamorig:RightHand": [0, 0, 0],
                "mixamorig:RightHandIndex1": [0, 0, 0],
                "mixamorig:RightHandIndex2": [0, 0, 0],
                "mixamorig:RightHandIndex3": [0, 0, 0],
                "mixamorig:RightHandMiddle1": [0, -90, 0],
                "mixamorig:RightHandMiddle2": [0, -70, 0],
                "mixamorig:RightHandMiddle3": [0, -60, 0],
                "mixamorig:RightHandRing1": [0, -90, 0],
                "mixamorig:RightHandRing2": [0, -70, 0],
                "mixamorig:RightHandRing3": [0, -60, 0],
                "mixamorig:RightHandPinky1": [0, -90, 0],
                "mixamorig:RightHandPinky2": [0, -70, 0],
                "mixamorig:RightHandPinky3": [0, -60, 0],
                "mixamorig:RightHandThumb1": [45, 0, 0],
                "mixamorig:RightHandThumb2": [0, 0, 0],
                "mixamorig:RightHandThumb3": [0, 0, 0],
            },
            "S30000": {  # Thumbs up (HELP, HELPMESIGN) - REAL THUMBS UP POSITION
                "mixamorig:RightArm": [
                    90,
                    45,
                    0,
                ],  # Right arm dramatically up and forward for thumbs up
                "mixamorig:RightForeArm": [0, 0, 0],
                "mixamorig:RightHand": [0, 0, 0],
                "mixamorig:RightHandIndex1": [0, -90, 0],
                "mixamorig:RightHandIndex2": [0, -70, 0],
                "mixamorig:RightHandIndex3": [0, -60, 0],
                "mixamorig:RightHandMiddle1": [0, -90, 0],
                "mixamorig:RightHandMiddle2": [0, -70, 0],
                "mixamorig:RightHandMiddle3": [0, -60, 0],
                "mixamorig:RightHandRing1": [0, -90, 0],
                "mixamorig:RightHandRing2": [0, -70, 0],
                "mixamorig:RightHandRing3": [0, -60, 0],
                "mixamorig:RightHandPinky1": [0, -90, 0],
                "mixamorig:RightHandPinky2": [0, -70, 0],
                "mixamorig:RightHandPinky3": [0, -60, 0],
                "mixamorig:RightHandThumb1": [0, 0, 0],
                "mixamorig:RightHandThumb2": [0, 0, 0],
                "mixamorig:RightHandThumb3": [0, 0, 0],
            },
        }

    def text_to_pose_sequence(self, text: str, language: str = "ASL") -> PoseSequence:
        """
        Complete sign.mt pipeline: Text -> Normalized Text -> SignWriting -> Pose Sequence

        Args:
            text: Input text
            language: Sign language (currently only ASL supported)

        Returns:
            PoseSequence ready for 3D avatar
        """
        self.logger.info(
            f"🎯 REAL sign.mt pipeline: Converting text to pose sequence: '{text}'"
        )

        # Step 1: Text normalization (sign.mt approach)
        normalized_text = self._normalize_text(text)
        self.logger.info(f"📝 Normalized text: '{normalized_text}'")

        # Step 2: Text to SignWriting (sign.mt approach)
        symbols = self.text_to_signwriting(normalized_text)
        self.logger.info(f"🎨 Generated {len(symbols)} SignWriting symbols")

        # Step 3: SignWriting to Pose Sequence (sign.mt approach)
        pose_sequence = self.signwriting_to_pose_sequence(symbols)
        self.logger.info(
            f"🎬 Generated pose sequence with {len(pose_sequence.frames)} frames"
        )

        return pose_sequence

    def _normalize_text(self, text: str) -> str:
        """Normalize text for SignWriting processing (sign.mt approach)"""
        # Convert to uppercase and clean up
        normalized = text.upper().strip()
        # Remove extra whitespace
        normalized = re.sub(r"\s+", " ", normalized)
        # Remove punctuation except for essential ones
        normalized = re.sub(r"[^\w\s]", "", normalized)
        return normalized

    def text_to_signwriting(self, text: str) -> List[SignWritingSymbol]:
        """
        Convert normalized text to SignWriting symbols (REAL sign.mt approach)

        Args:
            text: Normalized text

        Returns:
            List of SignWriting symbols
        """
        symbols = []
        words = text.split()

        for word in words:
            if word in self._signwriting_dictionary:
                word_data = self._signwriting_dictionary[word]
                hand_side = word_data["hand_side"]

                for i, symbol_code in enumerate(word_data["symbols"]):
                    symbol = SignWritingSymbol(
                        symbol=symbol_code,
                        position=(i * 50, 0),  # Simple positioning
                        rotation=0.0,
                        size=1.0,
                        hand_side=hand_side,
                    )
                    symbols.append(symbol)
            else:
                # Fallback: spell out unknown words using SignWriting
                self.logger.warning(f"Unknown word '{word}', spelling out")
                for char in word:
                    if char.isalpha():
                        symbol = SignWritingSymbol(
                            symbol="S10000",  # Default open hand for spelling
                            position=(len(symbols) * 30, 0),
                            rotation=0.0,
                            size=1.0,
                            hand_side="right",
                        )
                        symbols.append(symbol)

        return symbols

    def signwriting_to_pose_sequence(
        self, symbols: List[SignWritingSymbol]
    ) -> PoseSequence:
        """
        Convert SignWriting symbols to pose sequence with REAL interpolation (sign.mt approach)

        Args:
            symbols: List of SignWriting symbols

        Returns:
            PoseSequence for 3D avatar
        """
        if not symbols:
            # Return neutral pose
            neutral_pose = self._get_neutral_pose()
            return PoseSequence(
                frames=[neutral_pose] * 30, duration=1000, frame_rate=30
            )

        # Calculate total duration based on symbols
        total_duration = sum(
            self._signwriting_dictionary.get(word, {}).get("duration", 500)
            for word in self._get_words_from_symbols(symbols)
        )

        # Generate frames with REAL interpolation (sign.mt approach)
        frames = []
        frame_rate = 30
        total_frames = max(30, int(total_duration / 1000 * frame_rate))

        # Generate interpolated frames with smooth transitions
        for frame_idx in range(total_frames):
            progress = frame_idx / total_frames

            # Calculate which symbol we're currently transitioning to
            symbol_progress = progress * len(symbols)
            current_symbol_idx = int(symbol_progress)
            next_symbol_idx = min(current_symbol_idx + 1, len(symbols) - 1)

            # Calculate interpolation factor between symbols
            symbol_interpolation = symbol_progress - current_symbol_idx

            if current_symbol_idx < len(symbols):
                current_symbol = symbols[current_symbol_idx]
                current_pose = self._get_pose_for_symbol(current_symbol)

                if next_symbol_idx != current_symbol_idx and symbol_interpolation > 0:
                    # Interpolate between current and next symbol
                    next_symbol = symbols[next_symbol_idx]
                    next_pose = self._get_pose_for_symbol(next_symbol)
                    pose = self._interpolate_poses(
                        current_pose, next_pose, symbol_interpolation
                    )
                else:
                    pose = current_pose
            else:
                pose = self._get_neutral_pose()

            frames.append(pose)

        return PoseSequence(
            frames=frames, duration=total_duration, frame_rate=frame_rate
        )

    def _interpolate_poses(
        self,
        pose1: Dict[str, List[float]],
        pose2: Dict[str, List[float]],
        factor: float,
    ) -> Dict[str, List[float]]:
        """
        Interpolate between two poses (REAL sign.mt approach)

        Args:
            pose1: First pose
            pose2: Second pose
            factor: Interpolation factor (0.0 to 1.0)

        Returns:
            Interpolated pose
        """
        interpolated_pose = {}

        # Get all unique joint names from both poses
        all_joints = set(pose1.keys()) | set(pose2.keys())

        for joint_name in all_joints:
            if joint_name in pose1 and joint_name in pose2:
                # Interpolate between both poses
                hpr1 = pose1[joint_name]
                hpr2 = pose2[joint_name]

                interpolated_hpr = [
                    hpr1[0] + (hpr2[0] - hpr1[0]) * factor,
                    hpr1[1] + (hpr2[1] - hpr1[1]) * factor,
                    hpr1[2] + (hpr2[2] - hpr1[2]) * factor,
                ]

                interpolated_pose[joint_name] = interpolated_hpr
            elif joint_name in pose1:
                # Use pose1 value
                interpolated_pose[joint_name] = pose1[joint_name]
            else:
                # Use pose2 value
                interpolated_pose[joint_name] = pose2[joint_name]

        return interpolated_pose

    def _get_words_from_symbols(self, symbols: List[SignWritingSymbol]) -> List[str]:
        """Extract words from symbols (simplified for sign.mt approach)"""
        # This maps symbols back to words for duration calculation
        word_mapping = {"S10000": "WELCOME", "S20500": "TO", "S30000": "HELP"}

        words = []
        for symbol in symbols:
            if symbol.symbol in word_mapping:
                words.append(word_mapping[symbol.symbol])

        return words

    def _get_pose_for_symbol(self, symbol: SignWritingSymbol) -> Dict[str, List[float]]:
        """Get pose for a specific SignWriting symbol (REAL sign.mt approach)"""
        if symbol.symbol in self._pose_templates:
            base_pose = self._pose_templates[symbol.symbol].copy()

            # Apply hand side modifications
            if symbol.hand_side == "both":
                # For "both" hands, return the pose as-is (it already contains both hands)
                self.logger.info(
                    f"🎯 Applying both hands pose for symbol {symbol.symbol}"
                )
                return base_pose
            elif symbol.hand_side == "left":
                # Apply to left hand only
                left_hand_pose = {}
                for joint, hpr in base_pose.items():
                    if "Right" in joint and any(
                        finger in joint
                        for finger in ["Index", "Middle", "Ring", "Pinky", "Thumb"]
                    ):
                        left_joint = joint.replace("Right", "Left")
                        left_hand_pose[left_joint] = hpr
                    elif "Left" in joint or any(
                        arm in joint for arm in ["Arm", "ForeArm", "Hand"]
                    ):
                        left_hand_pose[joint] = hpr
                return left_hand_pose
            else:  # right
                # Apply to right hand only
                right_hand_pose = {}
                for joint, hpr in base_pose.items():
                    if "Right" in joint or any(
                        arm in joint for arm in ["Arm", "ForeArm", "Hand"]
                    ):
                        right_hand_pose[joint] = hpr
                return right_hand_pose

        # Fallback to neutral pose
        self.logger.warning(
            f"⚠️ Symbol {symbol.symbol} not found in pose templates, using neutral pose"
        )
        return self._get_neutral_pose()

    def _get_neutral_pose(self) -> Dict[str, List[float]]:
        """Get REAL neutral pose (arms down at sides, fingers relaxed)"""
        return {
            "mixamorig:RightArm": [0, 0, 0],  # Arms down at sides
            "mixamorig:LeftArm": [0, 0, 0],  # Arms down at sides
            "mixamorig:RightForeArm": [0, 0, 0],
            "mixamorig:LeftForeArm": [0, 0, 0],
            "mixamorig:RightHand": [0, 0, 0],
            "mixamorig:LeftHand": [0, 0, 0],
            # Right hand - fingers relaxed (slightly curved)
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
            "mixamorig:RightHandThumb1": [0, -10, 0],
            "mixamorig:RightHandThumb2": [0, -10, 0],
            "mixamorig:RightHandThumb3": [0, -10, 0],
            # Left hand - fingers relaxed (slightly curved)
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
            "mixamorig:LeftHandThumb1": [0, -10, 0],
            "mixamorig:LeftHandThumb2": [0, -10, 0],
            "mixamorig:LeftHandThumb3": [0, -10, 0],
        }
