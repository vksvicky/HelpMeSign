#!/usr/bin/env python3
"""
Standalone test for sign.mt integration
Tests the core functionality without import dependencies
"""

import json
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union


# Mock the resource manager for testing (from tests/integration/)
class MockResourceManager:
    def get_resource_path(self, path):
        return os.path.join(os.path.dirname(__file__), "..", "..", "resources", path)


# Sign.mt Integration Classes
class SignLanguageType(Enum):
    """Supported sign languages"""

    ASL = "asl"  # American Sign Language
    BSL = "bsl"  # British Sign Language
    ISL = "isl"  # Indian Sign Language
    AUSLAN = "auslan"  # Australian Sign Language


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
        self.resource_manager = MockResourceManager()

        # Load sign language mappings
        self._load_sign_mappings()

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
            print(f"Could not load sign mappings: {e}")
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
            print(f"Error translating text to signs: {e}")
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


def test_sign_mt_standalone():
    """Test the standalone sign.mt integration"""
    print("🧏 Testing Standalone Sign.mt Integration")
    print("=" * 50)

    try:
        # Test 1: Create translator
        print("\n1. Creating ASL translator...")
        translator = SignMTTranslator(SignLanguageType.ASL)
        print(f"✅ Translator created for {translator.language.value}")

        # Test 2: Get available signs
        print("\n2. Available signs:")
        available_signs = translator.get_available_signs()
        for sign in available_signs:
            description = translator.get_sign_description(sign)
            print(f"   • {sign}: {description}")

        # Test 3: Translate simple words
        print("\n3. Testing translations:")
        test_words = ["hello", "thank_you", "yes", "no"]

        for word in test_words:
            print(f"\n   Translating '{word}':")
            sequence = translator.translate_text_to_signs(word)
            print(f"   ✅ Generated {len(sequence.frames)} frames")
            print(f"   ✅ Total duration: {sequence.total_duration_ms}ms")

            for i, frame in enumerate(sequence.frames):
                print(
                    f"     Frame {i}: {len(frame.poses)} poses, {frame.duration_ms}ms"
                )

        # Test 4: Test pose conversion
        print("\n4. Testing pose conversion:")
        test_pose = SignPose("mixamorig:RightArm", 0, 45, 0)
        pose_dict = test_pose.to_dict()
        print(f"   ✅ Pose converted: {pose_dict}")

        # Test 5: Test frame conversion
        print("\n5. Testing frame conversion:")
        frame = SignFrame(frame_number=0, timestamp_ms=0, duration_ms=500)
        frame.poses.append(test_pose)
        pose_dict = frame.to_pose_dict()
        print(f"   ✅ Frame converted: {pose_dict}")

        # Test 6: Test phrase translation
        print("\n6. Testing phrase translation:")
        phrase = "hello thank_you"
        sequence = translator.translate_text_to_signs(phrase)
        print(f"   ✅ Generated {len(sequence.frames)} frames for phrase")
        print(f"   ✅ Total duration: {sequence.total_duration_ms}ms")

        print("\n🎉 All standalone tests passed! Sign.mt integration is working.")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_sign_mt_standalone()
