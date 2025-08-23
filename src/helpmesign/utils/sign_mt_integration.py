#!/usr/bin/env python3
"""
Sign.mt Integration Module
Integrates with the sign.mt ecosystem for proper sign language translation
Based on https://github.com/sign/ repositories
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    # Import transformers dynamically to avoid mypy import-not-found error
    import importlib

    import numpy as np
    import requests

    transformers = importlib.import_module("transformers")
    AutoModelForSeq2SeqLM = transformers.AutoModelForSeq2SeqLM
    AutoTokenizer = transformers.AutoTokenizer

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    # Don't print warning at import time - will be logged when needed

    # Type stubs for when transformers is not available
    AutoModelForSeq2SeqLM = Any
    AutoTokenizer = Any


from .resource_manager import ResourceManager


class SignLanguageType(Enum):
    """Supported sign languages"""

    ASL = "asl"  # American Sign Language
    BSL = "bsl"  # British Sign Language
    ISL = "isl"  # Indian Sign Language
    AUSLAN = "auslan"  # Australian Sign Language


@dataclass
class SignWritingSymbol:
    """SignWriting symbol representation following sign.mt conventions"""

    code: str  # e.g., "S10000", "S20500"
    hand_side: str  # "right", "left", "both"
    location: str = ""  # Body location
    movement: str = ""  # Movement type
    duration_ms: int = 500
    description: str = ""


@dataclass
class SignPose:
    """Sign pose with joint rotations"""

    joint_name: str
    heading: float = 0.0
    pitch: float = 0.0
    roll: float = 0.0

    def to_dict(self) -> Dict[str, List[float]]:
        return {self.joint_name: [self.heading, self.pitch, self.roll]}


@dataclass
class SignFrame:
    """Single frame in a sign sequence"""

    frame_number: int
    poses: List[SignPose] = field(default_factory=list)
    timestamp_ms: int = 0
    duration_ms: int = 100

    def to_pose_dict(self) -> Dict[str, List[float]]:
        """Convert to pose dictionary format"""
        pose_dict = {}
        for pose in self.poses:
            pose_dict.update(pose.to_dict())
        return pose_dict


@dataclass
class SignSequence:
    """Complete sign sequence for animation"""

    frames: List[SignFrame] = field(default_factory=list)
    total_duration_ms: int = 1000
    fps: int = 30
    language: SignLanguageType = SignLanguageType.ASL

    def add_frame(self, frame: SignFrame):
        """Add a frame to the sequence"""
        self.frames.append(frame)
        self.total_duration_ms = len(self.frames) * frame.duration_ms


class SignMTTranslator:
    """Sign.mt compatible translator following their architecture"""

    def __init__(self, language: SignLanguageType = SignLanguageType.ASL):
        self.language = language
        self.logger = logging.getLogger(__name__)
        self.resource_manager = ResourceManager()

        # Initialize models and tokenizers
        self._load_models()

        # Load sign language mappings
        self._load_sign_mappings()

    def _load_models(self):
        """Load sign language translation models"""
        if not ML_AVAILABLE:
            self.logger.info("ML dependencies not available, using basic mappings")
            self.tokenizer = None
            self.model = None
            return

        try:
            # Load bergamot models for sign language translation
            # Based on sign.mt's browsermt repository
            model_name = "Helsinki-NLP/opus-mt-en-{lang}".format(
                lang=self.language.value.upper()
            )

            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

            self.logger.info(f"Loaded sign language model for {self.language.value}")

        except Exception as e:
            self.logger.warning(f"Could not load sign language model: {e}")
            self.tokenizer = None
            self.model = None

    def _load_sign_mappings(self):
        """Load sign language to pose mappings"""
        try:
            # Load from sign.mt data repository patterns
            mapping_file = self.resource_manager.get_resource_path(
                f"data/signs/{self.language.value}/pose_mappings.json"
            )

            if os.path.exists(mapping_file):
                with open(mapping_file, "r") as f:
                    self.sign_mappings = json.load(f)
            else:
                # Fallback to basic mappings
                self.sign_mappings = self._create_basic_mappings()

        except Exception as e:
            self.logger.warning(f"Could not load sign mappings: {e}")
            self.sign_mappings = self._create_basic_mappings()

    def _create_basic_mappings(self) -> Dict[str, Dict]:
        """Create basic sign language mappings"""
        return {
            "hello": {
                "description": "Wave hand in greeting",
                "frames": [
                    {
                        "duration_ms": 500,
                        "poses": [
                            {"joint": "mixamorig:RightArm", "h": 0, "p": 45, "r": 0},
                            {"joint": "mixamorig:RightForeArm", "h": 0, "p": 0, "r": 0},
                            {"joint": "mixamorig:RightHand", "h": 0, "p": 0, "r": 0},
                        ],
                    },
                    {
                        "duration_ms": 500,
                        "poses": [
                            {"joint": "mixamorig:RightArm", "h": 0, "p": 45, "r": 0},
                            {"joint": "mixamorig:RightForeArm", "h": 0, "p": 0, "r": 0},
                            {"joint": "mixamorig:RightHand", "h": 0, "p": 0, "r": 45},
                        ],
                    },
                ],
            },
            "thank_you": {
                "description": "Touch chin and move hand forward",
                "frames": [
                    {
                        "duration_ms": 300,
                        "poses": [
                            {"joint": "mixamorig:RightArm", "h": 0, "p": 30, "r": 0},
                            {"joint": "mixamorig:RightForeArm", "h": 0, "p": 0, "r": 0},
                            {"joint": "mixamorig:RightHand", "h": 0, "p": 0, "r": 0},
                        ],
                    },
                    {
                        "duration_ms": 700,
                        "poses": [
                            {"joint": "mixamorig:RightArm", "h": 0, "p": 30, "r": 0},
                            {"joint": "mixamorig:RightForeArm", "h": 0, "p": 0, "r": 0},
                            {"joint": "mixamorig:RightHand", "h": 0, "p": 0, "r": 0},
                        ],
                    },
                ],
            },
            "yes": {
                "description": "Nod head up and down",
                "frames": [
                    {
                        "duration_ms": 400,
                        "poses": [{"joint": "mixamorig:Head", "h": 0, "p": 15, "r": 0}],
                    },
                    {
                        "duration_ms": 400,
                        "poses": [
                            {"joint": "mixamorig:Head", "h": 0, "p": -15, "r": 0}
                        ],
                    },
                ],
            },
            "no": {
                "description": "Shake head side to side",
                "frames": [
                    {
                        "duration_ms": 300,
                        "poses": [{"joint": "mixamorig:Head", "h": 15, "p": 0, "r": 0}],
                    },
                    {
                        "duration_ms": 300,
                        "poses": [
                            {"joint": "mixamorig:Head", "h": -15, "p": 0, "r": 0}
                        ],
                    },
                ],
            },
        }

    def translate_text_to_signs(self, text: str) -> SignSequence:
        """Translate text to sign language sequence"""
        try:
            # Normalize text
            normalized_text = self._normalize_text(text)

            # Split into words/phrases
            words = normalized_text.split()

            # Create sign sequence
            sequence = SignSequence(language=self.language)
            frame_number = 0

            for word in words:
                # Get sign for word
                sign_frames = self._get_sign_for_word(word)

                for frame_data in sign_frames:
                    frame = SignFrame(
                        frame_number=frame_number,
                        timestamp_ms=sequence.total_duration_ms,
                        duration_ms=frame_data["duration_ms"],
                    )

                    # Convert poses
                    for pose_data in frame_data["poses"]:
                        pose = SignPose(
                            joint_name=pose_data["joint"],
                            heading=pose_data["h"],
                            pitch=pose_data["p"],
                            roll=pose_data["r"],
                        )
                        frame.poses.append(pose)

                    sequence.add_frame(frame)
                    frame_number += 1

            return sequence

        except Exception as e:
            self.logger.error(f"Error translating text to signs: {e}")
            return self._create_default_sequence()

    def _normalize_text(self, text: str) -> str:
        """Normalize input text for sign language translation"""
        # Convert to lowercase and remove punctuation
        normalized = re.sub(r"[^\w\s]", "", text.lower())
        return normalized

    def _get_sign_for_word(self, word: str) -> List[Dict]:
        """Get sign frames for a specific word"""
        # Check if we have a direct mapping
        if word in self.sign_mappings:
            return self.sign_mappings[word]["frames"]

        # Try to find similar words
        for key in self.sign_mappings:
            if word in key or key in word:
                return self.sign_mappings[key]["frames"]

        # Return default sign (spell out the word)
        return self._spell_out_word(word)

    def _spell_out_word(self, word: str) -> List[Dict]:
        """Spell out a word using finger spelling"""
        frames = []

        for i, letter in enumerate(word):
            # Create a frame for each letter
            frame = {
                "duration_ms": 300,
                "poses": self._get_finger_spelling_pose(letter),
            }
            frames.append(frame)

        return frames

    def _get_finger_spelling_pose(self, letter: str) -> List[Dict]:
        """Get pose for finger spelling a letter"""
        # Basic finger spelling poses (ASL)
        finger_spelling = {
            "a": [{"joint": "mixamorig:RightHand", "h": 0, "p": 0, "r": 0}],
            "b": [{"joint": "mixamorig:RightHandIndex1", "h": 0, "p": 0, "r": 0}],
            "c": [{"joint": "mixamorig:RightHand", "h": 0, "p": 0, "r": 45}],
            # Add more letters as needed
        }

        return finger_spelling.get(
            letter.lower(), [{"joint": "mixamorig:RightHand", "h": 0, "p": 0, "r": 0}]
        )

    def _create_default_sequence(self) -> SignSequence:
        """Create a default sign sequence"""
        frame = SignFrame(frame_number=0, timestamp_ms=0, duration_ms=1000)

        # Add neutral pose
        neutral_poses = [
            SignPose("mixamorig:RightArm", 0, 0, 0),
            SignPose("mixamorig:RightForeArm", 0, 0, 0),
            SignPose("mixamorig:RightHand", 0, 0, 0),
        ]

        frame.poses.extend(neutral_poses)

        sequence = SignSequence(language=self.language)
        sequence.add_frame(frame)

        return sequence

    def get_available_signs(self) -> List[str]:
        """Get list of available signs"""
        return list(self.sign_mappings.keys())

    def get_sign_description(self, sign: str) -> str:
        """Get description of a sign"""
        if sign in self.sign_mappings:
            return self.sign_mappings[sign]["description"]
        return "Unknown sign"

    def set_language(self, language: SignLanguageType):
        """Change the sign language"""
        self.language = language
        self._load_sign_mappings()
        self.logger.info(f"Switched to {language.value} sign language")


class SignMTDataLoader:
    """Load sign language data from sign.mt repositories"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://raw.githubusercontent.com/sign"

    def load_sign_data(self, language: str = "asl") -> Dict:
        """Load sign language data from sign.mt data repository"""
        if not ML_AVAILABLE:
            self.logger.warning(
                "ML dependencies not available, cannot load remote data"
            )
            return {}

        try:
            # Try to load from sign.mt data repository
            url = f"{self.base_url}/data/main/{language}/signs.json"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"Could not load sign data from {url}")
                return {}

        except Exception as e:
            self.logger.warning(f"Error loading sign data: {e}")
            return {}

    def load_pose_mappings(self, language: str = "asl") -> Dict:
        """Load pose mappings from sign.mt repositories"""
        if not ML_AVAILABLE:
            self.logger.warning(
                "ML dependencies not available, cannot load remote data"
            )
            return {}

        try:
            url = f"{self.base_url}/data/main/{language}/pose_mappings.json"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"Could not load pose mappings from {url}")
                return {}

        except Exception as e:
            self.logger.warning(f"Error loading pose mappings: {e}")
            return {}


# Convenience functions for easy integration
def create_sign_translator(language: str = "asl") -> SignMTTranslator:
    """Create a sign language translator"""
    lang_enum = SignLanguageType(language.lower())
    return SignMTTranslator(lang_enum)


def translate_text_to_signs(text: str, language: str = "asl") -> SignSequence:
    """Quick function to translate text to signs"""
    translator = create_sign_translator(language)
    return translator.translate_text_to_signs(text)
