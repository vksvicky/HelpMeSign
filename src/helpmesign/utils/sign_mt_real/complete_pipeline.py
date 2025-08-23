"""
Complete Sign.mt Pipeline - Following sign.mt patterns

This implements the complete sign.mt architecture as local modules
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..pose_types import PoseFrame, PoseSequence
from .asset_manager import AssetManager
from .bergamot_translator import BergamotTranslator
from .model_registry import ModelRegistry
from .pose_data_service import PoseData, PoseDataService
from .signwriting_service import SignWritingService


@dataclass
class LanguagePair:
    """Language pair following sign.mt patterns"""

    spoken: str
    signed: str


class CompleteSignMTPipeline:
    """
    Complete Sign.mt Pipeline following their exact architecture

    This integrates all the sign.mt modules into a complete pipeline
    """

    def __init__(self, language: str = "ASL"):
        self.logger = logging.getLogger(__name__)
        self.language = language

        # Initialize all modules following sign.mt patterns
        self.asset_manager = AssetManager()
        self.model_registry = ModelRegistry(self.asset_manager)
        self.bergamot_translator = BergamotTranslator(
            self.asset_manager, self.model_registry
        )
        self.signwriting_service = SignWritingService(self.bergamot_translator)
        self.pose_data_service = PoseDataService(self.asset_manager)

        # Language mappings following sign.mt patterns
        self.language_mappings = {
            "ASL": LanguagePair(spoken="en", signed="ase"),
            "BSL": LanguagePair(spoken="en", signed="bfi"),
            "GSG": LanguagePair(spoken="de", signed="gsg"),
            "SGG": LanguagePair(spoken="de", signed="sgg"),
        }

        # Load lexicon for current language
        self._load_language_resources()

    def _load_language_resources(self):
        """Load language resources following sign.mt patterns"""
        try:
            # Load lexicon for current language
            if self.language in self.language_mappings:
                language_pair = self.language_mappings[self.language]
                self.pose_data_service.load_lexicon(language_pair.signed)

            self.logger.info(f"Loaded resources for language: {self.language}")

        except Exception as e:
            self.logger.error(f"Error loading language resources: {e}")

    def set_language(self, language: str):
        """Set language following sign.mt patterns"""
        self.language = language
        self._load_language_resources()

    async def text_to_pose_sequence(self, text: str) -> PoseSequence:
        """
        Complete pipeline: Text → SignWriting → Pose Sequence

        Following sign.mt patterns exactly
        """
        try:
            self.logger.info(f"Starting pipeline for text: '{text}'")

            # Get language pair
            if self.language not in self.language_mappings:
                raise Exception(f"Unsupported language: {self.language}")

            language_pair = self.language_mappings[self.language]

            # Step 1: Preprocess text
            preprocessed_text = self.signwriting_service.preprocess_spoken_text(text)

            # Step 2: Split into sentences (following their pattern)
            sentences = [preprocessed_text]  # Simple sentence splitting for now

            # Step 3: Translate to SignWriting
            signwriting_response = (
                await self.signwriting_service.translate_spoken_to_signwriting(
                    preprocessed_text,
                    sentences,
                    language_pair.spoken,
                    language_pair.signed,
                )
            )

            if not signwriting_response.text:
                self.logger.warning(
                    "No SignWriting generated, falling back to fingerspelling"
                )
                return self._fallback_to_fingerspelling(text)

            self.logger.info(f"Generated SignWriting: {signwriting_response.text}")

            # Step 4: Convert SignWriting to pose sequence
            pose_sequence = self._signwriting_to_pose_sequence(
                signwriting_response.text, language_pair.signed
            )

            self.logger.info(
                f"Generated pose sequence: {len(pose_sequence.frames)} frames"
            )
            return pose_sequence

        except Exception as e:
            self.logger.error(f"Pipeline error: {e}")
            return self._fallback_to_fingerspelling(text)

    def _signwriting_to_pose_sequence(
        self, signwriting: str, signed_language: str
    ) -> PoseSequence:
        """
        Convert SignWriting to pose sequence following sign.mt patterns
        """
        try:
            frames: List[PoseFrame] = []
            current_time_ms = 0

            # Parse SignWriting into individual symbols
            # SignWriting format: S5000M1000 (hand shape + movement)
            signs = []
            i = 0
            while i < len(signwriting):
                if signwriting[i] == "S":
                    # Find the end of the hand shape number
                    j = i + 1
                    while j < len(signwriting) and signwriting[j].isdigit():
                        j += 1
                    hand_shape = signwriting[i:j]
                    signs.append(hand_shape)
                    i = j
                elif signwriting[i] == "M":
                    # Find the end of the movement number
                    j = i + 1
                    while j < len(signwriting) and signwriting[j].isdigit():
                        j += 1
                    movement = signwriting[i:j]
                    signs.append(movement)
                    i = j
                else:
                    i += 1

            for i, sign in enumerate(signs):
                # Get pose for this sign
                pose_data = self.pose_data_service.get_pose_from_signwriting(
                    sign, signed_language
                )

                if pose_data:
                    # Skip disruptive neutral poses in the middle of phrases
                    metadata = pose_data.metadata or {}
                    is_neutral_return = metadata.get("sign_type") == "neutral_return"
                    is_middle_of_phrase = i > 0 and i < len(signs) - 1

                    if is_neutral_return and is_middle_of_phrase:
                        self.logger.info(
                            f"Skipping disruptive neutral pose {sign} in middle of phrase"
                        )
                        continue

                    # Create multiple frames for this pose to make animation longer and smoother
                    num_frames = max(
                        3, pose_data.duration_ms // 500
                    )  # At least 3 frames, more for longer poses
                    frame_duration = pose_data.duration_ms // num_frames

                    for frame_idx in range(num_frames):
                        frame = PoseFrame(
                            frame_number=len(frames),
                            pose=pose_data.joints,
                            timestamp_ms=current_time_ms,
                        )
                        frames.append(frame)
                        current_time_ms += frame_duration
                else:
                    # Create neutral pose frame if no pose found
                    neutral_pose = self.pose_data_service.get_neutral_pose()
                    frame = PoseFrame(
                        frame_number=i,
                        pose=neutral_pose.joints,
                        timestamp_ms=current_time_ms,
                    )
                    frames.append(frame)
                    current_time_ms += 1000  # Longer duration for better visibility

            # Add final neutral pose
            if frames:
                neutral_pose = self.pose_data_service.get_neutral_pose()
                final_frame = PoseFrame(
                    frame_number=len(frames),
                    pose=neutral_pose.joints,
                    timestamp_ms=current_time_ms,
                )
                frames.append(final_frame)
                current_time_ms += 1000  # Longer duration for better visibility

            return PoseSequence(
                frames=frames,
                total_duration_ms=current_time_ms,
                fps=15,  # Slower FPS for better visibility
            )

        except Exception as e:
            self.logger.error(f"Error converting SignWriting to pose sequence: {e}")
            return PoseSequence(frames=[], total_duration_ms=0)

    def _fallback_to_fingerspelling(self, text: str) -> PoseSequence:
        """
        Fallback to fingerspelling following sign.mt patterns
        """
        try:
            frames: List[PoseFrame] = []
            current_time_ms = 0

            # Convert text to lowercase and split into characters
            characters = list(text.lower())

            for i, char in enumerate(characters):
                # Generate pose for each character
                pose_data = self._generate_fingerspelling_pose(char)

                frame = PoseFrame(
                    frame_number=i, pose=pose_data.joints, timestamp_ms=current_time_ms
                )
                frames.append(frame)

                current_time_ms += pose_data.duration_ms

            # Add final neutral pose
            if frames:
                neutral_pose = self.pose_data_service.get_neutral_pose()
                final_frame = PoseFrame(
                    frame_number=len(frames),
                    pose=neutral_pose.joints,
                    timestamp_ms=current_time_ms,
                )
                frames.append(final_frame)
                current_time_ms += 1000  # Longer duration for better visibility

            return PoseSequence(
                frames=frames,
                total_duration_ms=current_time_ms,
                fps=15,  # Slower FPS for better visibility
            )

        except Exception as e:
            self.logger.error(f"Error in fingerspelling fallback: {e}")
            return PoseSequence(frames=[], total_duration_ms=0)

    def _generate_fingerspelling_pose(self, char: str) -> PoseData:
        """
        Generate fingerspelling pose following sign.mt patterns
        """
        # This would use their actual fingerspelling mappings
        # For now, use simple hand shapes based on character type

        if char.isalpha():
            # Letter - use hand shape based on character
            if char in ["a", "e", "i", "o", "u"]:
                # Vowels - open hand
                joints = {
                    "mixamorig:RightArm": [0.0, -15.0, 0.0],
                    "mixamorig:RightForeArm": [0.0, 0.0, 0.0],
                    "mixamorig:RightHand": [0.0, 0.0, 0.0],
                    "mixamorig:RightHandIndex1": [0.0, 0.0, 0.0],
                    "mixamorig:RightHandIndex2": [0.0, 0.0, 0.0],
                    "mixamorig:RightHandIndex3": [0.0, 0.0, 0.0],
                    "mixamorig:RightHandMiddle1": [0.0, 0.0, 0.0],
                    "mixamorig:RightHandMiddle2": [0.0, 0.0, 0.0],
                    "mixamorig:RightHandMiddle3": [0.0, 0.0, 0.0],
                    "mixamorig:RightHandRing1": [0.0, 0.0, 0.0],
                    "mixamorig:RightHandRing2": [0.0, 0.0, 0.0],
                    "mixamorig:RightHandRing3": [0.0, 0.0, 0.0],
                    "mixamorig:RightHandPinky1": [0.0, 0.0, 0.0],
                    "mixamorig:RightHandPinky2": [0.0, 0.0, 0.0],
                    "mixamorig:RightHandPinky3": [0.0, 0.0, 0.0],
                }
            else:
                # Consonants - closed hand
                joints = {
                    "mixamorig:RightArm": [0.0, -15.0, 0.0],
                    "mixamorig:RightForeArm": [0.0, 0.0, 0.0],
                    "mixamorig:RightHand": [0.0, 0.0, 0.0],
                    "mixamorig:RightHandIndex1": [0.0, -30.0, 0.0],
                    "mixamorig:RightHandIndex2": [0.0, -30.0, 0.0],
                    "mixamorig:RightHandIndex3": [0.0, -30.0, 0.0],
                    "mixamorig:RightHandMiddle1": [0.0, -30.0, 0.0],
                    "mixamorig:RightHandMiddle2": [0.0, -30.0, 0.0],
                    "mixamorig:RightHandMiddle3": [0.0, -30.0, 0.0],
                    "mixamorig:RightHandRing1": [0.0, -30.0, 0.0],
                    "mixamorig:RightHandRing2": [0.0, -30.0, 0.0],
                    "mixamorig:RightHandRing3": [0.0, -30.0, 0.0],
                    "mixamorig:RightHandPinky1": [0.0, -30.0, 0.0],
                    "mixamorig:RightHandPinky2": [0.0, -30.0, 0.0],
                    "mixamorig:RightHandPinky3": [0.0, -30.0, 0.0],
                }
        else:
            # Non-letter - neutral pose
            joints = {
                "mixamorig:RightArm": [0.0, -15.0, 0.0],
                "mixamorig:RightForeArm": [0.0, 0.0, 0.0],
                "mixamorig:RightHand": [0.0, 0.0, 0.0],
                "mixamorig:RightHandIndex1": [0.0, 0.0, 0.0],
                "mixamorig:RightHandIndex2": [0.0, 0.0, 0.0],
                "mixamorig:RightHandIndex3": [0.0, 0.0, 0.0],
                "mixamorig:RightHandMiddle1": [0.0, 0.0, 0.0],
                "mixamorig:RightHandMiddle2": [0.0, 0.0, 0.0],
                "mixamorig:RightHandMiddle3": [0.0, 0.0, 0.0],
                "mixamorig:RightHandRing1": [0.0, 0.0, 0.0],
                "mixamorig:RightHandRing2": [0.0, 0.0, 0.0],
                "mixamorig:RightHandRing3": [0.0, 0.0, 0.0],
                "mixamorig:RightHandPinky1": [0.0, 0.0, 0.0],
                "mixamorig:RightHandPinky2": [0.0, 0.0, 0.0],
                "mixamorig:RightHandPinky3": [0.0, 0.0, 0.0],
            }

        return PoseData(joints=joints, duration_ms=500)  # 500ms per character

    def get_neutral_pose(self) -> Dict[str, List[float]]:
        """Get neutral pose following sign.mt patterns"""
        neutral_pose = self.pose_data_service.get_neutral_pose()
        return neutral_pose.joints
