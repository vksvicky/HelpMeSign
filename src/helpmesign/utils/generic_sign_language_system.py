#!/usr/bin/env python3
"""
Generic Sign Language System
Supports multiple sign languages with ASL as default
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


class SignType(Enum):
    """Types of signs"""

    HAND_SHAPE = "hand_shape"
    MOVEMENT = "movement"
    LOCATION = "location"
    EXPRESSION = "expression"


@dataclass
class HandPose:
    """Represents a hand pose with finger positions"""

    # Arm position (HPR values)
    arm_h: float = 0.0
    arm_p: float = 0.0
    arm_r: float = 0.0

    # Forearm position
    forearm_h: float = 0.0
    forearm_p: float = 0.0
    forearm_r: float = 0.0

    # Hand position
    hand_h: float = 0.0
    hand_p: float = 0.0
    hand_r: float = 0.0

    # Finger positions (HPR for each finger joint)
    thumb: List[Tuple[float, float, float]] | None = None  # 3 joints
    index: List[Tuple[float, float, float]] | None = None  # 3 joints
    middle: List[Tuple[float, float, float]] | None = None  # 3 joints
    ring: List[Tuple[float, float, float]] | None = None  # 3 joints
    pinky: List[Tuple[float, float, float]] | None = None  # 3 joints

    def __post_init__(self):
        if self.thumb is None:
            self.thumb = [(0.0, 0.0, 0.0)] * 3
        if self.index is None:
            self.index = [(0.0, 0.0, 0.0)] * 3
        if self.middle is None:
            self.middle = [(0.0, 0.0, 0.0)] * 3
        if self.ring is None:
            self.ring = [(0.0, 0.0, 0.0)] * 3
        if self.pinky is None:
            self.pinky = [(0.0, 0.0, 0.0)] * 3


@dataclass
class SignPose:
    """Complete pose for a sign"""

    right_hand: HandPose
    left_hand: HandPose
    duration_ms: int = 1000
    hand_side: HandSide = HandSide.BOTH


@dataclass
class SignTemplate:
    """Template for a sign with multiple poses for animation"""

    poses: List[SignPose]
    description: str = ""
    sign_type: SignType = SignType.HAND_SHAPE


class GenericSignLanguageSystem:
    """Generic system for handling multiple sign languages"""

    def __init__(self, default_language: str = "ASL"):
        self.default_language = default_language
        self.current_language = default_language
        self.resource_manager = ResourceManager()

        # Load pose templates
        self.pose_templates = self._load_pose_templates()

        # Load language mappings
        self.language_mappings = self._load_language_mappings()

        # Neutral pose
        self.neutral_pose = self._get_neutral_pose()

    def _load_pose_templates(self) -> Dict[str, SignTemplate]:
        """Load generic pose templates that work for any language"""
        templates = {}

        # Basic hand shapes
        templates["OPEN_HAND"] = SignTemplate(
            poses=[
                SignPose(
                    right_hand=HandPose(
                        arm_h=0,
                        arm_p=90,
                        arm_r=0,  # Arm forward
                        forearm_h=0,
                        forearm_p=0,
                        forearm_r=0,
                        hand_h=0,
                        hand_p=0,
                        hand_r=0,
                        thumb=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        index=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        middle=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        ring=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        pinky=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                    ),
                    left_hand=HandPose(
                        arm_h=0,
                        arm_p=90,
                        arm_r=0,
                        forearm_h=0,
                        forearm_p=0,
                        forearm_r=0,
                        hand_h=0,
                        hand_p=0,
                        hand_r=0,
                        thumb=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        index=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        middle=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        ring=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        pinky=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                    ),
                    duration_ms=1000,
                    hand_side=HandSide.BOTH,
                )
            ],
            description="Open hand with fingers extended",
            sign_type=SignType.HAND_SHAPE,
        )

        templates["CLOSED_FIST"] = SignTemplate(
            poses=[
                SignPose(
                    right_hand=HandPose(
                        arm_h=0,
                        arm_p=90,
                        arm_r=0,
                        forearm_h=0,
                        forearm_p=0,
                        forearm_r=0,
                        hand_h=0,
                        hand_p=0,
                        hand_r=0,
                        thumb=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        index=[(0, -45, 0), (0, -45, 0), (0, -45, 0)],
                        middle=[(0, -45, 0), (0, -45, 0), (0, -45, 0)],
                        ring=[(0, -45, 0), (0, -45, 0), (0, -45, 0)],
                        pinky=[(0, -45, 0), (0, -45, 0), (0, -45, 0)],
                    ),
                    left_hand=HandPose(
                        arm_h=0,
                        arm_p=90,
                        arm_r=0,
                        forearm_h=0,
                        forearm_p=0,
                        forearm_r=0,
                        hand_h=0,
                        hand_p=0,
                        hand_r=0,
                        thumb=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        index=[(0, -45, 0), (0, -45, 0), (0, -45, 0)],
                        middle=[(0, -45, 0), (0, -45, 0), (0, -45, 0)],
                        ring=[(0, -45, 0), (0, -45, 0), (0, -45, 0)],
                        pinky=[(0, -45, 0), (0, -45, 0), (0, -45, 0)],
                    ),
                    duration_ms=1000,
                    hand_side=HandSide.BOTH,
                )
            ],
            description="Closed fist with fingers curled",
            sign_type=SignType.HAND_SHAPE,
        )

        templates["POINTING_INDEX"] = SignTemplate(
            poses=[
                SignPose(
                    right_hand=HandPose(
                        arm_h=0,
                        arm_p=90,
                        arm_r=0,
                        forearm_h=0,
                        forearm_p=0,
                        forearm_r=0,
                        hand_h=0,
                        hand_p=0,
                        hand_r=0,
                        thumb=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        index=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        middle=[(0, -45, 0), (0, -45, 0), (0, -45, 0)],
                        ring=[(0, -45, 0), (0, -45, 0), (0, -45, 0)],
                        pinky=[(0, -45, 0), (0, -45, 0), (0, -45, 0)],
                    ),
                    left_hand=HandPose(
                        arm_h=0,
                        arm_p=90,
                        arm_r=0,
                        forearm_h=0,
                        forearm_p=0,
                        forearm_r=0,
                        hand_h=0,
                        hand_p=0,
                        hand_r=0,
                        thumb=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        index=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        middle=[(0, -45, 0), (0, -45, 0), (0, -45, 0)],
                        ring=[(0, -45, 0), (0, -45, 0), (0, -45, 0)],
                        pinky=[(0, -45, 0), (0, -45, 0), (0, -45, 0)],
                    ),
                    duration_ms=1000,
                    hand_side=HandSide.BOTH,
                )
            ],
            description="Index finger pointing, others closed",
            sign_type=SignType.HAND_SHAPE,
        )

        templates["V_HAND"] = SignTemplate(
            poses=[
                SignPose(
                    right_hand=HandPose(
                        arm_h=0,
                        arm_p=90,
                        arm_r=0,
                        forearm_h=0,
                        forearm_p=0,
                        forearm_r=0,
                        hand_h=0,
                        hand_p=0,
                        hand_r=0,
                        thumb=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        index=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        middle=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        ring=[(0, -45, 0), (0, -45, 0), (0, -45, 0)],
                        pinky=[(0, -45, 0), (0, -45, 0), (0, -45, 0)],
                    ),
                    left_hand=HandPose(
                        arm_h=0,
                        arm_p=90,
                        arm_r=0,
                        forearm_h=0,
                        forearm_p=0,
                        forearm_r=0,
                        hand_h=0,
                        hand_p=0,
                        hand_r=0,
                        thumb=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        index=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        middle=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                        ring=[(0, -45, 0), (0, -45, 0), (0, -45, 0)],
                        pinky=[(0, -45, 0), (0, -45, 0), (0, -45, 0)],
                    ),
                    duration_ms=1000,
                    hand_side=HandSide.BOTH,
                )
            ],
            description="V hand with index and middle extended",
            sign_type=SignType.HAND_SHAPE,
        )

        return templates

    def _load_language_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load language-specific word to template mappings"""
        mappings = {}

        # ASL mappings (default)
        mappings["ASL"] = {
            "WELCOME": "OPEN_HAND",
            "TO": "POINTING_INDEX",
            "HELP": "OPEN_HAND",
            "ME": "POINTING_INDEX",
            "SIGN": "V_HAND",
            "HELPMESIGN": "OPEN_HAND",
        }

        # BSL mappings (example)
        mappings["BSL"] = {
            "WELCOME": "OPEN_HAND",
            "TO": "POINTING_INDEX",
            "HELP": "OPEN_HAND",
            "ME": "POINTING_INDEX",
            "SIGN": "V_HAND",
            "HELPMESIGN": "OPEN_HAND",
        }

        # Add more languages as needed
        # mappings["AUSLAN"] = {...}
        # mappings["LSF"] = {...}

        return mappings

    def _get_neutral_pose(self) -> SignPose:
        """Get neutral pose with arms at sides"""
        return SignPose(
            right_hand=HandPose(
                arm_h=0,
                arm_p=0,
                arm_r=0,
                forearm_h=0,
                forearm_p=0,
                forearm_r=0,
                hand_h=0,
                hand_p=0,
                hand_r=0,
                thumb=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                index=[(0, -10, 0), (0, -10, 0), (0, -10, 0)],
                middle=[(0, -10, 0), (0, -10, 0), (0, -10, 0)],
                ring=[(0, -10, 0), (0, -10, 0), (0, -10, 0)],
                pinky=[(0, -10, 0), (0, -10, 0), (0, -10, 0)],
            ),
            left_hand=HandPose(
                arm_h=0,
                arm_p=0,
                arm_r=0,
                forearm_h=0,
                forearm_p=0,
                forearm_r=0,
                hand_h=0,
                hand_p=0,
                hand_r=0,
                thumb=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                index=[(0, -10, 0), (0, -10, 0), (0, -10, 0)],
                middle=[(0, -10, 0), (0, -10, 0), (0, -10, 0)],
                ring=[(0, -10, 0), (0, -10, 0), (0, -10, 0)],
                pinky=[(0, -10, 0), (0, -10, 0), (0, -10, 0)],
            ),
            duration_ms=1000,
            hand_side=HandSide.BOTH,
        )

    def set_language(self, language: str):
        """Set the current sign language"""
        if language in self.language_mappings:
            self.current_language = language
        else:
            # Fallback to default
            self.current_language = self.default_language

    def get_sign_for_word(self, word: str) -> Optional[SignTemplate]:
        """Get sign template for a word in current language"""
        word_upper = word.upper()

        # Check current language mappings
        if self.current_language in self.language_mappings:
            language_map = self.language_mappings[self.current_language]
            if word_upper in language_map:
                template_name = language_map[word_upper]
                if template_name in self.pose_templates:
                    return self.pose_templates[template_name]

        # Fallback to default language
        if self.current_language != self.default_language:
            default_map = self.language_mappings[self.default_language]
            if word_upper in default_map:
                template_name = default_map[word_upper]
                if template_name in self.pose_templates:
                    return self.pose_templates[template_name]

        # No sign found
        return None

    def get_neutral_pose(self) -> SignPose:
        """Get neutral pose"""
        return self.neutral_pose

    def add_language_mapping(self, language: str, word: str, template_name: str):
        """Add a new language mapping"""
        if language not in self.language_mappings:
            self.language_mappings[language] = {}

        self.language_mappings[language][word.upper()] = template_name

    def add_pose_template(self, name: str, template: SignTemplate):
        """Add a new pose template"""
        self.pose_templates[name] = template

    def get_available_languages(self) -> List[str]:
        """Get list of available languages"""
        return list(self.language_mappings.keys())

    def get_available_templates(self) -> List[str]:
        """Get list of available pose templates"""
        return list(self.pose_templates.keys())
