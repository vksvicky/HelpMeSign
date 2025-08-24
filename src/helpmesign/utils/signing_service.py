#!/usr/bin/env python3
"""
Clean signing service for HelpMeSign
Handles text-to-sign translation without external dependencies
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class SignResponse:
    """Response from signing service"""

    text: str
    confidence: float
    source: str
    pose_sequence: Optional[List[Dict]] = None


@dataclass
class PoseFrame:
    """Single pose frame for animation"""

    time_ms: int
    joints: Dict[str, List[float]]
    metadata: Optional[Dict] = None


@dataclass
class PoseSequence:
    """Complete pose sequence for animation"""

    frames: List[PoseFrame]
    fps: int = 30
    total_duration_ms: int = 0


class SigningService:
    """
    Clean signing service that translates text to sign language poses
    Uses local data and rule-based translation
    """

    def __init__(self, data_path: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.data_path = data_path or Path("resources/data")
        self.sign_data: Dict = {}
        self.word_mappings: Dict = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the signing service"""
        if self._initialized:
            return

        self.logger.info("Initializing signing service")

        # Load local sign language data
        await self._load_local_data()

        # Build word mappings
        self._build_word_mappings()

        self._initialized = True
        self.logger.info("Signing service initialized")

    async def _load_local_data(self) -> None:
        """Load local sign language data"""
        try:
            # Load existing ASL data
            asl_file = self.data_path / "signs/asl/asl_right_hand.json"
            if asl_file.exists():
                with open(asl_file, "r") as f:
                    self.sign_data = json.load(f)
                self.logger.info(f"Loaded {len(self.sign_data)} ASL signs")
            else:
                self.logger.warning("No ASL data found, using basic mappings")
                self.sign_data = {}

        except Exception as e:
            self.logger.error(f"Error loading local data: {e}")
            self.sign_data = {}

    def _build_word_mappings(self) -> None:
        """Build word-to-sign mappings"""
        self.word_mappings = {
            # Basic greetings
            "hello": "greeting_open_hand",
            "hi": "greeting_open_hand",
            "goodbye": "farewell_wave",
            "bye": "farewell_wave",
            # Common words
            "thank": "gratitude_hand_to_chin",
            "thanks": "gratitude_hand_to_chin",
            "please": "request_palm_up",
            "help": "assistance_hands_up",
            "yes": "affirmation_nod",
            "no": "negation_shake",
            # Family
            "mother": "family_mother",
            "father": "family_father",
            "sister": "family_sister",
            "brother": "family_brother",
            # Colors
            "red": "color_red",
            "blue": "color_blue",
            "green": "color_green",
            "yellow": "color_yellow",
            # Numbers
            "one": "number_one",
            "two": "number_two",
            "three": "number_three",
            "four": "number_four",
            "five": "number_five",
        }

    async def translate_text(self, text: str, language: str = "ASL") -> SignResponse:
        """
        Translate text to sign language

        Args:
            text: Input text to translate
            language: Target sign language (default: ASL)

        Returns:
            SignResponse with translation and pose sequence
        """
        if not self._initialized:
            await self.initialize()

        self.logger.info(f"Translating '{text}' to {language}")

        # Clean and normalize text
        clean_text = text.lower().strip()
        words = clean_text.split()

        # Try exact word match first
        if len(words) == 1 and clean_text in self.word_mappings:
            sign_name = self.word_mappings[clean_text]
            pose_sequence = self._generate_pose_sequence(sign_name)
            return SignResponse(
                text=sign_name,
                confidence=0.9,
                source="exact_match",
                pose_sequence=pose_sequence,
            )

        # Try phrase matching
        phrase_result = self._match_phrase(clean_text)
        if phrase_result:
            return phrase_result

        # Fallback to word-by-word translation
        return self._translate_word_by_word(words)

    def _match_phrase(self, text: str) -> Optional[SignResponse]:
        """Match common phrases"""
        phrase_mappings = {
            "thank you": "gratitude_sequence",
            "you're welcome": "welcome_sequence",
            "how are you": "question_how_are_you",
            "i'm fine": "response_i_am_fine",
            "nice to meet you": "greeting_nice_to_meet",
        }

        if text in phrase_mappings:
            sign_name = phrase_mappings[text]
            pose_sequence = self._generate_pose_sequence(sign_name)
            return SignResponse(
                text=sign_name,
                confidence=0.8,
                source="phrase_match",
                pose_sequence=pose_sequence,
            )

        return None

    def _translate_word_by_word(self, words: List[str]) -> SignResponse:
        """Translate text word by word"""
        translations = []
        matched_words = 0

        for word in words:
            if word in self.word_mappings:
                translations.append(self.word_mappings[word])
                matched_words += 1
            else:
                # Use fingerspelling for unknown words
                translations.append(f"fingerspell_{word}")

        confidence = matched_words / len(words) if words else 0.0
        confidence = max(0.3, confidence)  # Minimum confidence

        # Generate pose sequence for the translation
        pose_sequence = self._generate_pose_sequence(" ".join(translations))

        return SignResponse(
            text=" ".join(translations),
            confidence=confidence,
            source="word_by_word",
            pose_sequence=pose_sequence,
        )

    def _generate_pose_sequence(self, sign_name: str) -> List[Dict]:
        """Generate pose sequence for a sign"""
        # This is a simplified pose generation
        # In a real implementation, you'd have detailed pose data

        base_poses = {
            "greeting_open_hand": [
                {"time": 0, "pose": "neutral"},
                {"time": 500, "pose": "greeting_open_hand"},
                {"time": 1000, "pose": "neutral"},
            ],
            "gratitude_hand_to_chin": [
                {"time": 0, "pose": "neutral"},
                {"time": 300, "pose": "gratitude_hand_to_chin"},
                {"time": 800, "pose": "gratitude_hand_to_chin"},
                {"time": 1200, "pose": "neutral"},
            ],
            "farewell_wave": [
                {"time": 0, "pose": "neutral"},
                {"time": 200, "pose": "farewell_wave"},
                {"time": 400, "pose": "farewell_wave"},
                {"time": 600, "pose": "farewell_wave"},
                {"time": 800, "pose": "neutral"},
            ],
            "request_palm_up": [
                {"time": 0, "pose": "neutral"},
                {"time": 400, "pose": "request_palm_up"},
                {"time": 1000, "pose": "neutral"},
            ],
            "gratitude_sequence": [
                {"time": 0, "pose": "neutral"},
                {"time": 300, "pose": "gratitude_hand_to_chin"},
                {"time": 800, "pose": "gratitude_hand_to_chin"},
                {"time": 1200, "pose": "neutral"},
            ],
            "question_how_are_you": [
                {"time": 0, "pose": "neutral"},
                {"time": 400, "pose": "request_palm_up"},
                {"time": 1000, "pose": "neutral"},
            ],
        }

        # Return default pose if not found
        return base_poses.get(
            sign_name,
            [
                {"time": 0, "pose": "neutral"},
                {"time": 500, "pose": "basic_gesture"},
                {"time": 1000, "pose": "neutral"},
            ],
        )

    def get_neutral_pose(self) -> Dict:
        """Get neutral pose for character reset"""
        return {
            "pose": "neutral",
            "joints": {
                "head": [0, 0, 0],
                "neck": [0, 0, 0],
                "shoulder_r": [0, 0, 0],
                "shoulder_l": [0, 0, 0],
                "elbow_r": [0, 0, 0],
                "elbow_l": [0, 0, 0],
                "wrist_r": [0, 0, 0],
                "wrist_l": [0, 0, 0],
                "hand_r": [0, 0, 0],
                "hand_l": [0, 0, 0],
            },
        }


# Convenience function for testing
async def test_signing_service():
    """Test the signing service"""
    service = SigningService()
    await service.initialize()

    test_texts = ["hello", "thank you", "goodbye", "please help me", "how are you"]

    print("Testing signing service:")
    print("=" * 50)

    for text in test_texts:
        result = await service.translate_text(text)
        print(
            f"'{text}' -> '{result.text}' (confidence: {result.confidence:.2f}, source: {result.source})"
        )
        if result.pose_sequence:
            print(f"  Pose sequence: {len(result.pose_sequence)} frames")
        print()


if __name__ == "__main__":
    asyncio.run(test_signing_service())
