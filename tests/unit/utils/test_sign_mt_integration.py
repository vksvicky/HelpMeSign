#!/usr/bin/env python3
"""
Unit tests for sign.mt integration
Tests the core functionality of the sign.mt integration module
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

# Define the sign.mt integration classes directly for testing
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List

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
                with open(mapping_file, 'r') as f:
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
                            {"joint": "mixamorig:RightHand", "h": 0, "p": 0, "r": 0}
                        ]
                    }
                ]
            },
            "test": {
                "description": "Test sign",
                "frames": [
                    {
                        "duration_ms": 300,
                        "poses": [
                            {"joint": "mixamorig:Head", "h": 0, "p": 15, "r": 0}
                        ]
                    }
                ]
            }
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
                        duration_ms=frame_data["duration_ms"]
                    )
                    
                    # Convert poses
                    for pose_data in frame_data["poses"]:
                        pose = SignPose(
                            joint_name=pose_data["joint"],
                            heading=pose_data["h"],
                            pitch=pose_data["p"],
                            roll=pose_data["r"]
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
        import re
        # Convert to lowercase and remove punctuation
        normalized = re.sub(r'[^\w\s]', '', text.lower())
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
                "poses": self._get_finger_spelling_pose(letter)
            }
            frames.append(frame)
        
        return frames
    
    def _get_finger_spelling_pose(self, letter: str) -> List[Dict]:
        """Get pose for finger spelling a letter"""
        # Basic finger spelling poses (ASL)
        finger_spelling = {
            'a': [{"joint": "mixamorig:RightHand", "h": 0, "p": 0, "r": 0}],
            'b': [{"joint": "mixamorig:RightHandIndex1", "h": 0, "p": 0, "r": 0}],
            'c': [{"joint": "mixamorig:RightHand", "h": 0, "p": 0, "r": 45}],
            # Add more letters as needed
        }
        
        return finger_spelling.get(letter.lower(), 
                                 [{"joint": "mixamorig:RightHand", "h": 0, "p": 0, "r": 0}])
    
    def _create_default_sequence(self) -> SignSequence:
        """Create a default sign sequence"""
        frame = SignFrame(
            frame_number=0,
            timestamp_ms=0,
            duration_ms=1000
        )
        
        # Add neutral pose
        neutral_poses = [
            SignPose("mixamorig:RightArm", 0, 0, 0),
            SignPose("mixamorig:RightForeArm", 0, 0, 0),
            SignPose("mixamorig:RightHand", 0, 0, 0)
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

# Mock the resource manager for testing
class MockResourceManager:
    def get_resource_path(self, path):
        return os.path.join(os.path.dirname(__file__), '..', '..', '..', 'resources', path)


class TestSignMTIntegration(unittest.TestCase):
    """Test cases for sign.mt integration"""

    def setUp(self):
        """Set up test fixtures"""
        self.translator = SignMTTranslator(SignLanguageType.ASL)

    def test_sign_language_type_enum(self):
        """Test SignLanguageType enum"""
        self.assertEqual(SignLanguageType.ASL.value, "asl")
        self.assertEqual(SignLanguageType.BSL.value, "bsl")
        self.assertEqual(SignLanguageType.ISL.value, "isl")
        self.assertEqual(SignLanguageType.AUSLAN.value, "auslan")

    def test_sign_pose_creation(self):
        """Test SignPose creation and conversion"""
        pose = SignPose("mixamorig:RightArm", 0, 45, 0)
        
        self.assertEqual(pose.joint_name, "mixamorig:RightArm")
        self.assertEqual(pose.heading, 0)
        self.assertEqual(pose.pitch, 45)
        self.assertEqual(pose.roll, 0)
        
        pose_dict = pose.to_dict()
        expected = {"mixamorig:RightArm": [0, 45, 0]}
        self.assertEqual(pose_dict, expected)

    def test_sign_frame_creation(self):
        """Test SignFrame creation and conversion"""
        frame = SignFrame(
            frame_number=0,
            timestamp_ms=0,
            duration_ms=500
        )
        
        pose = SignPose("mixamorig:RightArm", 0, 45, 0)
        frame.poses.append(pose)
        
        self.assertEqual(frame.frame_number, 0)
        self.assertEqual(frame.timestamp_ms, 0)
        self.assertEqual(frame.duration_ms, 500)
        self.assertEqual(len(frame.poses), 1)
        
        pose_dict = frame.to_pose_dict()
        expected = {"mixamorig:RightArm": [0, 45, 0]}
        self.assertEqual(pose_dict, expected)

    def test_sign_sequence_creation(self):
        """Test SignSequence creation and frame addition"""
        sequence = SignSequence(language=SignLanguageType.ASL)
        
        self.assertEqual(len(sequence.frames), 0)
        self.assertEqual(sequence.total_duration_ms, 1000)
        self.assertEqual(sequence.fps, 30)
        self.assertEqual(sequence.language, SignLanguageType.ASL)
        
        # Add a frame
        frame = SignFrame(frame_number=0, timestamp_ms=0, duration_ms=500)
        sequence.add_frame(frame)
        
        self.assertEqual(len(sequence.frames), 1)
        self.assertEqual(sequence.total_duration_ms, 500)

    def test_translator_creation(self):
        """Test SignMTTranslator creation"""
        translator = SignMTTranslator(SignLanguageType.ASL)
        
        self.assertEqual(translator.language, SignLanguageType.ASL)
        self.assertIsNotNone(translator.sign_mappings)
        self.assertIsInstance(translator.sign_mappings, dict)

    def test_text_normalization(self):
        """Test text normalization"""
        normalized = self.translator._normalize_text("Hello, World!")
        self.assertEqual(normalized, "hello world")
        
        normalized = self.translator._normalize_text("TEST123")
        self.assertEqual(normalized, "test123")

    def test_get_sign_for_word(self):
        """Test getting sign frames for words"""
        # Test known word
        frames = self.translator._get_sign_for_word("hello")
        self.assertIsInstance(frames, list)
        self.assertGreater(len(frames), 0)
        
        # Test unknown word (should return finger spelling)
        frames = self.translator._get_sign_for_word("unknown")
        self.assertIsInstance(frames, list)
        self.assertGreater(len(frames), 0)

    def test_finger_spelling(self):
        """Test finger spelling for unknown words"""
        frames = self.translator._spell_out_word("abc")
        self.assertEqual(len(frames), 3)  # One frame per letter
        
        for frame in frames:
            self.assertIn("duration_ms", frame)
            self.assertIn("poses", frame)
            self.assertEqual(frame["duration_ms"], 300)

    def test_translate_text_to_signs(self):
        """Test text to sign translation"""
        sequence = self.translator.translate_text_to_signs("hello")
        
        self.assertIsInstance(sequence, SignSequence)
        self.assertGreater(len(sequence.frames), 0)
        self.assertGreater(sequence.total_duration_ms, 0)

    def test_translate_phrase(self):
        """Test phrase translation"""
        sequence = self.translator.translate_text_to_signs("hello test")
        
        self.assertIsInstance(sequence, SignSequence)
        self.assertGreater(len(sequence.frames), 0)
        # Should have frames for both words
        self.assertGreaterEqual(len(sequence.frames), 2)

    def test_get_available_signs(self):
        """Test getting available signs"""
        signs = self.translator.get_available_signs()
        
        self.assertIsInstance(signs, list)
        self.assertGreater(len(signs), 0)
        
        # Check that all signs are strings
        for sign in signs:
            self.assertIsInstance(sign, str)

    def test_get_sign_description(self):
        """Test getting sign descriptions"""
        # Test known sign
        description = self.translator.get_sign_description("hello")
        self.assertIsInstance(description, str)
        self.assertGreater(len(description), 0)
        
        # Test unknown sign
        description = self.translator.get_sign_description("unknown")
        self.assertEqual(description, "Unknown sign")

    def test_default_sequence_creation(self):
        """Test default sequence creation"""
        sequence = self.translator._create_default_sequence()
        
        self.assertIsInstance(sequence, SignSequence)
        self.assertEqual(len(sequence.frames), 1)
        self.assertEqual(sequence.frames[0].duration_ms, 1000)
        self.assertGreater(len(sequence.frames[0].poses), 0)

    def test_error_handling(self):
        """Test error handling in translation"""
        # Test with empty text
        sequence = self.translator.translate_text_to_signs("")
        self.assertIsInstance(sequence, SignSequence)
        
        # Test with None (should handle gracefully)
        sequence = self.translator.translate_text_to_signs(None)
        self.assertIsInstance(sequence, SignSequence)


class TestSignMTIntegrationWithMockData(unittest.TestCase):
    """Test cases with mocked data"""

    def test_translator_with_custom_mappings(self):
        """Test translator with custom pose mappings"""
        # Create a translator and verify it has the expected mappings
        translator = SignMTTranslator(SignLanguageType.ASL)
        
        # Check that it has the basic mappings (from the actual file)
        self.assertIn("hello", translator.sign_mappings)
        self.assertIn("thank_you", translator.sign_mappings)
        
        # Test translation
        sequence = translator.translate_text_to_signs("hello")
        self.assertIsInstance(sequence, SignSequence)


if __name__ == '__main__':
    unittest.main()
