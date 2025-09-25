#!/usr/bin/env python3
"""
Universal Instruction-to-Pose Generator
Converts natural language instructions into 3D pose data dynamically
Supports multiple sign languages with minimal configuration changes
"""

import json
import os
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .instruction_parser import InstructionParser


class UniversalHandShape(Enum):
    """Universal hand shapes across sign languages"""

    FIST = "fist"
    FLAT = "flat"
    CURVED = "curved"
    POINT = "point"
    OPEN = "open"
    CLOSED = "closed"
    C_SHAPE = "c_shape"
    O_SHAPE = "o_shape"
    L_SHAPE = "l_shape"


class UniversalAction(Enum):
    """Universal actions across sign languages"""

    RAISE = "raise"
    LOWER = "lower"
    HOLD = "hold"
    POINT = "point"
    CURVE = "curve"
    CURL = "curl"
    EXTEND = "extend"
    BEND = "bend"
    TOUCH = "touch"
    MOVE = "move"
    FORM = "form"
    MAKE = "make"
    KEEP = "keep"


class BodyPart(Enum):
    """Universal body parts"""

    ARM = "arm"
    FOREARM = "forearm"
    ELBOW = "elbow"
    HAND = "hand"
    WRIST = "wrist"
    THUMB = "thumb"
    INDEX = "index"
    MIDDLE = "middle"
    RING = "ring"
    PINKY = "pinky"
    FINGERS = "fingers"


@dataclass
class UniversalPoseInstruction:
    """Language-agnostic pose instruction"""

    action: UniversalAction
    body_part: BodyPart
    modifier: Optional[str] = None
    direction: Optional[str] = None
    hand_shape: Optional[UniversalHandShape] = None
    intensity: float = 1.0  # 0.0 to 1.0 for partial movements


class UniversalInstructionToPoseGenerator:
    """Universal pose generator that works across different sign languages"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the universal pose generator

        Args:
            config_path: Path to language-specific configuration file
                        If None, uses default universal configuration
        """
        self.config_path = config_path
        self.language_config = self._load_language_config()

        # Universal pose mappings (work for all sign languages)
        self.universal_hand_shapes = self._init_universal_hand_shapes()
        self.universal_actions = self._init_universal_actions()
        self.joint_mappings = self._init_joint_mappings()

        # Language-specific overrides (if provided)
        self.language_overrides = self.language_config.get("overrides", {})

        # Initialize the new instruction parser
        self.instruction_parser = InstructionParser("asl")

    def _load_language_config(self) -> Dict[str, Any]:
        """Load language-specific configuration"""
        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)

        # Return default universal configuration (legacy format for backward compatibility)
        return {
            "language": "universal",
            "keywords": {
                "actions": {
                    "raise": ["raise", "lift", "up", "elevate"],
                    "lower": ["lower", "down", "drop"],
                    "hold": ["hold", "keep", "maintain", "stay"],
                    "point": ["point", "extend", "straighten"],
                    "curve": ["curve", "bend", "arch"],
                    "curl": ["curl", "close", "fold"],
                    "touch": ["touch", "contact", "meet"],
                    "make": ["make", "form", "create", "shape"],
                },
                "body_parts": {
                    "arm": ["arm", "shoulder"],
                    "elbow": ["elbow"],
                    "hand": ["hand", "wrist"],
                    "fingers": ["fingers", "digits"],
                    "thumb": ["thumb"],
                    "index": ["index", "pointer"],
                    "middle": ["middle"],
                    "ring": ["ring"],
                    "pinky": ["pinky", "little"],
                },
                "hand_shapes": {
                    "fist": ["fist", "closed", "tight"],
                    "flat": ["flat", "open", "straight", "extended"],
                    "curved": ["curved", "bent", "c-shape", "c shape"],
                    "point": ["point", "pointing", "finger up"],
                },
                "modifiers": {
                    "together": ["together", "close", "tight"],
                    "apart": ["apart", "spread", "wide"],
                    "bent": ["bent", "curved", "flexed"],
                    "straight": ["straight", "extended", "flat"],
                },
            },
        }

    def _init_universal_hand_shapes(self) -> Dict[str, Dict[str, Any]]:
        """Universal hand shape mappings that work across sign languages"""
        return {
            "fist": {
                # Real working values from manual pose creation
                "index": {
                    "hpr": [0, 77.1, 0],
                    "xyz": [0, 0, 0],
                },  # Real index finger curl
                "middle": {
                    "hpr": [0, 84.8, 0],
                    "xyz": [0, 0, 0],
                },  # Real middle finger curl
                "ring": {
                    "hpr": [0, 94.3, 0],
                    "xyz": [0, 0, 0],
                },  # Real ring finger curl
                "pinky": {"hpr": [0, 90.0, 0], "xyz": [0, 0, 0]},  # Real pinky curl
                "thumb": {
                    "hpr": [0.0, 2.1, 10.3],
                    "xyz": [0, 0, 0],
                },  # Real thumb position for 'A'
            },
            "flat": {
                # All fingers extended straight
                "index": {"hpr": [0, 0, 0], "xyz": [0, 0, 0]},
                "middle": {"hpr": [0, 0, 0], "xyz": [0, 0, 0]},
                "ring": {"hpr": [0, 0, 0], "xyz": [0, 0, 0]},
                "pinky": {"hpr": [0, 0, 0], "xyz": [0, 0, 0]},
                "thumb": {"hpr": [0, 0, 0], "xyz": [0, 0, 0]},
            },
            "curved": {
                # Fingers slightly curved, forming C shape
                "index": {"hpr": [0, 30, 0], "xyz": [0, 0, 0]},
                "middle": {"hpr": [0, 30, 0], "xyz": [0, 0, 0]},
                "ring": {"hpr": [0, 30, 0], "xyz": [0, 0, 0]},
                "pinky": {"hpr": [0, 30, 0], "xyz": [0, 0, 0]},
                "thumb": {"hpr": [-20, 15, 5], "xyz": [0, 0, 0]},
            },
            "point": {
                # One finger extended, others closed
                "index": {"hpr": [0, 0, 0], "xyz": [0, 0, 0]},  # Extended
                "middle": {
                    "hpr": [0, 45, 0],
                    "xyz": [0, 0, 0],
                },  # Closed (reduced from 90)
                "ring": {
                    "hpr": [0, 45, 0],
                    "xyz": [0, 0, 0],
                },  # Closed (reduced from 90)
                "pinky": {
                    "hpr": [0, 45, 0],
                    "xyz": [0, 0, 0],
                },  # Closed (reduced from 90)
                "thumb": {"hpr": [-20, 15, 5], "xyz": [0, 0, 0]},  # More natural
            },
        }

    def _init_universal_actions(self) -> Dict[str, Dict[str, Any]]:
        """Universal action mappings"""
        return {
            "raise_arm": {
                "arm": {
                    "hpr": [4.3, 90.0, 0.0],
                    "xyz": [0, 0, 0],
                },  # Real working values from manual pose
                # Don't set forearm here - let bend_elbow handle it
            },
            "bend_elbow": {
                "forearm": {
                    "hpr": [77.1, 132.9, 0.0],
                    "xyz": [0, 0, 0],
                },  # Real working elbow bend values
            },
            "arm_to_side": {
                "arm": {"hpr": [0, 0, -90], "xyz": [0, 0, 0]},  # Arm out to side
            },
            "arm_forward": {
                "arm": {"hpr": [0, 45, 0], "xyz": [0, 0, 0]},  # Arm forward
            },
            "hand_up": {
                "hand": {"hpr": [0, -30, 0], "xyz": [0, 0, 0]},  # Wrist bent up
            },
            "hand_flat": {
                "hand": {"hpr": [0, 0, 0], "xyz": [0, 0, 0]},  # Neutral wrist position
            },
            "hand_fist_orientation": {
                "hand": {
                    "hpr": [180.0, 0.0, 0.0],
                    "xyz": [0, 0, 0],
                },  # Hand orientation for fist
            },
        }

    def _init_joint_mappings(self) -> Dict[str, str]:
        """Map universal body parts to actual joint names"""
        return {
            "right_arm": "mixamorig:RightArm",
            "left_arm": "mixamorig:LeftArm",
            "right_forearm": "mixamorig:RightForeArm",
            "left_forearm": "mixamorig:LeftForeArm",
            "right_hand": "mixamorig:RightHand",
            "left_hand": "mixamorig:LeftHand",
            "right_thumb1": "mixamorig:RightHandThumb1",
            "right_thumb2": "mixamorig:RightHandThumb2",
            "right_thumb3": "mixamorig:RightHandThumb3",
            "right_index1": "mixamorig:RightHandIndex1",
            "right_index2": "mixamorig:RightHandIndex2",
            "right_index3": "mixamorig:RightHandIndex3",
            "right_middle1": "mixamorig:RightHandMiddle1",
            "right_middle2": "mixamorig:RightHandMiddle2",
            "right_middle3": "mixamorig:RightHandMiddle3",
            "right_ring1": "mixamorig:RightHandRing1",
            "right_ring2": "mixamorig:RightHandRing2",
            "right_ring3": "mixamorig:RightHandRing3",
            "right_pinky1": "mixamorig:RightHandPinky1",
            "right_pinky2": "mixamorig:RightHandPinky2",
            "right_pinky3": "mixamorig:RightHandPinky3",
            # Left hand mappings (mirror of right)
            "left_thumb1": "mixamorig:LeftHandThumb1",
            "left_thumb2": "mixamorig:LeftHandThumb2",
            "left_thumb3": "mixamorig:LeftHandThumb3",
            "left_index1": "mixamorig:LeftHandIndex1",
            "left_index2": "mixamorig:LeftHandIndex2",
            "left_index3": "mixamorig:LeftHandIndex3",
            "left_middle1": "mixamorig:LeftHandMiddle1",
            "left_middle2": "mixamorig:LeftHandMiddle2",
            "left_middle3": "mixamorig:LeftHandMiddle3",
            "left_ring1": "mixamorig:LeftHandRing1",
            "left_ring2": "mixamorig:LeftHandRing2",
            "left_ring3": "mixamorig:LeftHandRing3",
            "left_pinky1": "mixamorig:LeftHandPinky1",
            "left_pinky2": "mixamorig:LeftHandPinky2",
            "left_pinky3": "mixamorig:LeftHandPinky3",
        }

    def parse_universal_instruction(
        self, instruction: str
    ) -> List[UniversalPoseInstruction]:
        """Parse instruction using language-agnostic keyword matching"""
        instruction = instruction.lower()
        words = re.findall(r"\b\w+\b", instruction)
        parsed_instructions = []

        # Extract actions, body parts, and modifiers using keyword matching
        detected_actions = []
        detected_body_parts = []
        detected_hand_shapes = []
        detected_modifiers = []

        keywords = self.language_config["keywords"]

        # Match actions
        for universal_action in keywords["actions"].keys():
            synonyms = self._get_keyword_synonyms("actions", universal_action)
            if any(word in synonyms for word in words):
                try:
                    detected_actions.append(UniversalAction(universal_action))
                except ValueError:
                    continue

        # Match body parts
        for universal_part in keywords["body_parts"].keys():
            synonyms = self._get_keyword_synonyms("body_parts", universal_part)
            if any(word in synonyms for word in words):
                try:
                    detected_body_parts.append(BodyPart(universal_part))
                except ValueError:
                    continue

        # Match hand shapes
        for universal_shape in keywords["hand_shapes"].keys():
            synonyms = self._get_keyword_synonyms("hand_shapes", universal_shape)
            if any(word in synonyms for word in words):
                try:
                    detected_hand_shapes.append(UniversalHandShape(universal_shape))
                except ValueError:
                    continue

        # Match modifiers
        for modifier in keywords["modifiers"].keys():
            synonyms = self._get_keyword_synonyms("modifiers", modifier)
            if any(word in synonyms for word in words):
                detected_modifiers.append(modifier)

        # Combine detected elements into instructions
        if detected_actions and detected_body_parts:
            for action in detected_actions:
                for body_part in detected_body_parts:
                    hand_shape = (
                        detected_hand_shapes[0] if detected_hand_shapes else None
                    )
                    modifier = detected_modifiers[0] if detected_modifiers else None

                    parsed_instructions.append(
                        UniversalPoseInstruction(
                            action=action,
                            body_part=body_part,
                            hand_shape=hand_shape,
                            modifier=modifier,
                        )
                    )

        return parsed_instructions

    def generate_universal_pose(
        self, instruction: str, hand: str = "right"
    ) -> Dict[str, List[float]]:
        """Generate 3D pose data using universal approach"""
        parsed = self.parse_universal_instruction(instruction)
        pose_data: Dict[str, List[float]] = {}

        for instr in parsed:
            # Apply hand shape mappings
            if (
                instr.hand_shape
                and instr.hand_shape.value in self.universal_hand_shapes
            ):
                shape_mapping = self.universal_hand_shapes[instr.hand_shape.value]
                finger_pose = self._apply_hand_shape(shape_mapping, hand)
                # Extract HPR values from the new HPR+XYZ format
                for joint_name, joint_data in finger_pose.items():
                    if isinstance(joint_data, dict) and "hpr" in joint_data:
                        pose_data[joint_name] = joint_data["hpr"]
                    elif isinstance(joint_data, list):
                        pose_data[joint_name] = joint_data  # Legacy format

            # Apply action-specific poses
            if (
                instr.action == UniversalAction.RAISE
                and instr.body_part == BodyPart.ARM
            ):
                arm_pose = self._apply_arm_action("raise_arm", hand)
                # Extract HPR values from the new HPR+XYZ format
                for joint_name, joint_data in arm_pose.items():
                    if isinstance(joint_data, dict) and "hpr" in joint_data:
                        pose_data[joint_name] = joint_data["hpr"]
                    elif isinstance(joint_data, list):
                        pose_data[joint_name] = joint_data  # Legacy format

            # Handle elbow bending - both "BEND + ELBOW" and "RAISE + ELBOW" (from "elbow bent")
            if (
                instr.action == UniversalAction.BEND
                and instr.body_part == BodyPart.ELBOW
            ) or (
                instr.action == UniversalAction.RAISE
                and instr.body_part == BodyPart.ELBOW
            ):
                elbow_pose = self._apply_arm_action("bend_elbow", hand)
                # Extract HPR values from the new HPR+XYZ format
                for joint_name, joint_data in elbow_pose.items():
                    if isinstance(joint_data, dict) and "hpr" in joint_data:
                        pose_data[joint_name] = joint_data["hpr"]
                    elif isinstance(joint_data, list):
                        pose_data[joint_name] = joint_data  # Legacy format

            if instr.action == UniversalAction.POINT and instr.body_part in [
                BodyPart.INDEX,
                BodyPart.MIDDLE,
                BodyPart.RING,
                BodyPart.PINKY,
            ]:
                # finger_pose: Dict[str, List[float]] = self._apply_single_finger_point(
                #     instr.body_part.value, hand
                # )
                # Extract HPR values from the new HPR+XYZ format
                for joint_name, joint_data in finger_pose.items():
                    if isinstance(joint_data, dict) and "hpr" in joint_data:
                        pose_data[joint_name] = joint_data["hpr"]
                    elif isinstance(joint_data, list):
                        pose_data[joint_name] = joint_data  # Legacy format

        # Apply hand orientation for fist (specific to letter A)
        if any(instr.hand_shape == UniversalHandShape.FIST for instr in parsed):
            hand_pose = self._apply_arm_action("hand_fist_orientation", hand)
            for joint_name, joint_data in hand_pose.items():
                if isinstance(joint_data, dict) and "hpr" in joint_data:
                    pose_data[joint_name] = joint_data["hpr"]
                elif isinstance(joint_data, list):
                    pose_data[joint_name] = joint_data

        return pose_data

    def _apply_hand_shape(
        self, shape_mapping: Dict[str, Any], hand: str
    ) -> Dict[str, Dict[str, List[float]]]:
        """Apply hand shape to specific hand"""
        pose_data: Dict[str, Dict[str, List[float]]] = {}
        hand_prefix = hand.lower()

        for finger, finger_data in shape_mapping.items():
            # Handle new HPR+XYZ format or legacy HPR-only format
            if isinstance(finger_data, dict) and "hpr" in finger_data:
                hpr = finger_data["hpr"]
                xyz = finger_data["xyz"]
            else:
                hpr = finger_data  # Legacy format (just HPR list)
                xyz = [0, 0, 0]  # Default XYZ for legacy format

            if finger == "thumb":
                for i in range(1, 4):  # Thumb has 3 joints
                    joint_key = f"{hand_prefix}_{finger}{i}"
                    if joint_key in self.joint_mappings:
                        pose_data[self.joint_mappings[joint_key]] = {
                            "hpr": hpr,
                            "xyz": xyz,
                        }
            else:
                for i in range(1, 4):  # Other fingers have 3 joints
                    joint_key = f"{hand_prefix}_{finger}{i}"
                    if joint_key in self.joint_mappings:
                        pose_data[self.joint_mappings[joint_key]] = {
                            "hpr": hpr,
                            "xyz": xyz,
                        }

        return pose_data

    def _apply_arm_action(
        self, action_key: str, hand: str
    ) -> Dict[str, Dict[str, List[float]]]:
        """Apply arm/elbow actions"""
        pose_data: Dict[str, Dict[str, List[float]]] = {}
        hand_prefix = hand.lower()

        if action_key in self.universal_actions:
            action_mapping = self.universal_actions[action_key]
            for body_part, part_data in action_mapping.items():
                # Handle new HPR+XYZ format or legacy HPR-only format
                if isinstance(part_data, dict) and "hpr" in part_data:
                    hpr = part_data["hpr"]
                    xyz = part_data["xyz"]
                else:
                    hpr = part_data  # Legacy format (just HPR list)
                    xyz = [0, 0, 0]  # Default XYZ for legacy format

                joint_key = f"{hand_prefix}_{body_part}"
                if joint_key in self.joint_mappings:
                    pose_data[self.joint_mappings[joint_key]] = {"hpr": hpr, "xyz": xyz}

        return pose_data

    def _apply_single_finger_point(
        self, finger: str, hand: str
    ) -> Dict[str, List[float]]:
        """Point a single finger while keeping others closed"""
        pose_data: Dict[str, List[float]] = {}
        hand_prefix = hand.lower()

        fingers = ["index", "middle", "ring", "pinky"]

        for f in fingers:
            hpr = (
                [0.0, 0.0, 0.0] if f == finger else [0.0, 45.0, 0.0]
            )  # Extended vs closed
            for i in range(1, 4):
                joint_key = f"{hand_prefix}_{f}{i}"
                if joint_key in self.joint_mappings:
                    pose_data[self.joint_mappings[joint_key]] = hpr

        return pose_data

    def get_supported_patterns(self) -> List[str]:
        """Return list of supported universal instruction patterns"""
        return [
            "Universal Actions: raise, lower, hold, point, curve, curl, extend, bend, touch, move, form, make, keep",
            "Universal Body Parts: arm, forearm, elbow, hand, wrist, thumb, index, middle, ring, pinky, fingers",
            "Universal Hand Shapes: fist, flat, curved, point, open, closed, c_shape, o_shape, l_shape",
            "Universal Modifiers: together, apart, bent, straight",
            "Example: 'raise your arm and make a fist'",
            "Example: 'point your index finger up'",
            "Example: 'hold your hand flat with fingers together'",
        ]

    def analyze_universal_coverage(self, instructions: List[str]) -> Dict[str, Any]:
        """Analyze instruction coverage using universal approach"""
        coverage: Dict[str, Any] = {
            "parseable": 0,
            "unparseable": 0,
            "total": len(instructions),
            "detected_patterns": {},
        }

        unparseable_instructions = []
        pattern_counts: Dict[str, int] = {}

        for instruction in instructions:
            parsed = self.parse_universal_instruction(instruction)
            if parsed:
                coverage["parseable"] += 1
                # Track patterns
                for instr in parsed:
                    pattern_key = f"{instr.action.value}_{instr.body_part.value}"
                    if instr.hand_shape:
                        pattern_key += f"_{instr.hand_shape.value}"
                    pattern_counts[pattern_key] = pattern_counts.get(pattern_key, 0) + 1
            else:
                coverage["unparseable"] += 1
                unparseable_instructions.append(instruction)

        coverage["unparseable_list"] = unparseable_instructions
        coverage["detected_patterns"] = pattern_counts
        return coverage

    def _get_keyword_synonyms(self, category: str, keyword: str) -> List[str]:
        """Get synonyms for a keyword, handling both old and new config formats"""
        keywords = self.language_config.get("keywords", {}).get(category, {})
        keyword_data = keywords.get(keyword, {})

        # Handle new format with synonyms
        if isinstance(keyword_data, dict) and "synonyms" in keyword_data:
            return keyword_data["synonyms"]
        # Handle old format (direct list)
        elif isinstance(keyword_data, list):
            return keyword_data
        else:
            return []

    def _get_keyword_pose_data(
        self, category: str, keyword: str
    ) -> Dict[str, List[float]]:
        """Get pose data for a keyword, handling both old and new config formats"""
        keywords = self.language_config.get("keywords", {}).get(category, {})
        keyword_data = keywords.get(keyword, {})

        # Handle new format with pose_data
        if isinstance(keyword_data, dict) and "pose_data" in keyword_data:
            return keyword_data["pose_data"]
        else:
            return {}

    def get_symbol_pose_from_signs_file(
        self, symbol: str, signs_file_path: str
    ) -> Dict[str, List[float]]:
        """Get pose data for a specific symbol by generating it from instructions in signs file"""
        try:
            with open(signs_file_path, "r", encoding="utf-8") as f:
                signs_config = json.load(f)

            # Check alphabet first, then numbers
            symbol_data = None
            if symbol.upper() in signs_config.get("alphabet", {}):
                symbol_data = signs_config["alphabet"][symbol.upper()]
            elif symbol.upper() in signs_config.get("numbers", {}):
                symbol_data = signs_config["numbers"][symbol.upper()]

            if symbol_data and "instructions" in symbol_data:
                # Generate pose from instructions using universal config keywords
                instruction_text = symbol_data["instructions"]
                return self.generate_pose_from_instruction(instruction_text)

        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass

        return {}

    def get_symbol_instruction_from_signs_file(
        self, symbol: str, signs_file_path: str
    ) -> str:
        """Get instruction text for a specific symbol from signs file"""
        try:
            with open(signs_file_path, "r", encoding="utf-8") as f:
                signs_config = json.load(f)

            # Check alphabet first, then numbers
            symbol_data = None
            if symbol.upper() in signs_config.get("alphabet", {}):
                symbol_data = signs_config["alphabet"][symbol.upper()]
            elif symbol.upper() in signs_config.get("numbers", {}):
                symbol_data = signs_config["numbers"][symbol.upper()]

            if symbol_data and "instructions" in symbol_data:
                return symbol_data["instructions"]

        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass

        return f"Sign for {symbol}"

    def generate_static_pose_from_keywords(
        self, keywords: List[str]
    ) -> Dict[str, List[float]]:
        """Generate static pose by combining pose data from multiple keywords"""
        # Start with natural pose as base
        natural_pose = self._get_keyword_pose_data("actions", "natural")
        combined_pose = natural_pose.copy() if natural_pose else {}

        for keyword in keywords:
            # Try to find the keyword in each category
            for category in ["actions", "body_parts", "hand_shapes", "modifiers"]:
                category_keywords = self.language_config.get("keywords", {}).get(
                    category, {}
                )

                for key, data in category_keywords.items():
                    synonyms = self._get_keyword_synonyms(category, key)
                    if keyword.lower() in [s.lower() for s in synonyms]:
                        pose_data = self._get_keyword_pose_data(category, key)
                        # Merge pose data (later keywords override earlier ones)
                        combined_pose.update(pose_data)
                        break

        return combined_pose

    def generate_animated_pose_sequence_from_signs_file(
        self, language_string: str, signs_file_path: str, duration_ms: int = 2000
    ) -> List[Dict[str, Any]]:
        """Generate animated pose sequence from a language string using signs file"""
        sequence: List[Dict[str, Any]] = []
        symbols = list(language_string.upper())

        if not symbols:
            return sequence

        # Calculate timing
        frame_duration = duration_ms // len(symbols)

        for i, symbol in enumerate(symbols):
            pose_data = self.get_symbol_pose_from_signs_file(symbol, signs_file_path)
            if pose_data:
                frame = {
                    "frame_number": i,
                    "timestamp_ms": i * frame_duration,
                    "pose": pose_data,
                    "symbol": symbol,
                    "instruction": self.get_symbol_instruction_from_signs_file(
                        symbol, signs_file_path
                    ),
                }
                sequence.append(frame)

        return sequence

    def generate_pose_from_instruction(
        self, instruction: str
    ) -> Dict[str, List[float]]:
        """Generate pose from natural language instruction using keyword matching"""
        # Use the new instruction parser for better accuracy
        try:
            return self.instruction_parser.generate_pose_from_instruction(instruction)
        except Exception:
            # Fallback to original method
            words = instruction.lower().split()
            return self.generate_static_pose_from_keywords(words)

    def get_sign_data_from_unified_file(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get sign data from the unified ASL file"""
        return self.instruction_parser.get_sign_data(symbol)

    def generate_pose_from_sign_symbol(self, symbol: str) -> Dict[str, List[float]]:
        """Generate pose data from a sign symbol using the unified file"""
        return self.instruction_parser.generate_pose_from_sign(symbol)

    def create_language_config_template(
        self, language_code: str, language_name: str
    ) -> Dict[str, Any]:
        """Create a template configuration for a new language"""
        return {
            "language": language_code.upper(),
            "language_name": language_name,
            "keywords": {
                "actions": {
                    "raise": ["raise", "lift", "up", "elevate"],
                    "lower": ["lower", "down", "drop"],
                    "hold": ["hold", "keep", "maintain", "stay"],
                    "point": ["point", "extend", "straighten"],
                    "curve": ["curve", "bend", "arch"],
                    "curl": ["curl", "close", "fold"],
                    "touch": ["touch", "contact", "meet"],
                    "make": ["make", "form", "create", "shape"],
                },
                "body_parts": {
                    "arm": ["arm", "shoulder"],
                    "elbow": ["elbow"],
                    "hand": ["hand", "wrist"],
                    "fingers": ["fingers", "digits"],
                    "thumb": ["thumb"],
                    "index": ["index", "pointer"],
                    "middle": ["middle"],
                    "ring": ["ring"],
                    "pinky": ["pinky", "little"],
                },
                "hand_shapes": {
                    "fist": ["fist", "closed", "tight"],
                    "flat": ["flat", "open", "straight", "extended"],
                    "curved": ["curved", "bent", "c-shape", "c shape"],
                    "point": ["point", "pointing", "finger up"],
                },
                "modifiers": {
                    "together": ["together", "close", "tight"],
                    "apart": ["apart", "spread", "wide"],
                    "bent": ["bent", "curved", "flexed"],
                    "straight": ["straight", "extended", "flat"],
                },
            },
            "overrides": {
                "comment": "Add language-specific pose adjustments here if needed"
            },
        }


def main():
    """Test the universal instruction to pose generator"""
    generator = UniversalInstructionToPoseGenerator()

    # Test with some example instructions
    test_instructions = [
        "Raise your right arm with elbow bent, make a fist with thumb extended to the side",
        "Hold your right hand flat with all fingers together and extended",
        "Point your index finger up with your right hand, keeping other fingers closed",
        "Curve your right hand fingers and thumb to form a C shape",
        "Point your pinky finger up with your right hand, keeping other fingers closed",
    ]

    print("=== UNIVERSAL INSTRUCTION TO POSE GENERATOR TEST ===")
    print(f"Language: {generator.language_config['language']}")
    print()

    for i, instruction in enumerate(test_instructions, 1):
        print(f"{i}. Instruction: {instruction}")

        parsed = generator.parse_universal_instruction(instruction)
        print(f"   Parsed components: {len(parsed)}")
        for comp in parsed:
            hand_shape_str = f" -> {comp.hand_shape.value}" if comp.hand_shape else ""
            modifier_str = f" ({comp.modifier})" if comp.modifier else ""
            print(
                f"   - {comp.action.value} {comp.body_part.value}{hand_shape_str}{modifier_str}"
            )

        pose = generator.generate_universal_pose(instruction)
        print(f"   Generated pose joints: {len(pose)}")
        for joint, hpr in list(pose.items())[:3]:  # Show first 3 joints
            print(f"   - {joint}: {hpr}")
        if len(pose) > 3:
            print(f"   ... and {len(pose) - 3} more joints")
        print()

    # Test coverage analysis
    print("=== COVERAGE ANALYSIS ===")
    coverage = generator.analyze_universal_coverage(test_instructions)
    print(
        f"Parseable: {coverage['parseable']}/{coverage['total']} ({coverage['parseable']/coverage['total']*100:.1f}%)"
    )
    print(f"Detected patterns: {list(coverage['detected_patterns'].keys())}")

    if coverage["unparseable_list"]:
        print(f"Unparseable instructions: {coverage['unparseable_list']}")

    # Show supported patterns
    print("\n=== SUPPORTED PATTERNS ===")
    for pattern in generator.get_supported_patterns():
        print(f"- {pattern}")


def create_language_config_file(
    language_code: str, language_name: str, output_path: str
):
    """Create a new language configuration file"""
    generator = UniversalInstructionToPoseGenerator()
    config = generator.create_language_config_template(language_code, language_name)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"Created language configuration template: {output_path}")
    print("Edit the keywords section to match your language's instruction patterns.")


if __name__ == "__main__":
    main()
