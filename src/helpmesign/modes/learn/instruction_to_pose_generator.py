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

    def _load_language_config(self) -> Dict[str, Any]:
        """Load language-specific configuration"""
        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)

        # Return default universal configuration
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

    def _init_universal_hand_shapes(self) -> Dict[str, Dict[str, List[float]]]:
        """Universal hand shape mappings that work across sign languages"""
        return {
            "fist": {
                # All fingers curl into palm, thumb wraps around
                "index": [0, 90, 0],  # Each finger joint curls 90 degrees
                "middle": [0, 90, 0],
                "ring": [0, 90, 0],
                "pinky": [0, 90, 0],
                "thumb": [-45, 30, 10],  # Thumb wraps around
            },
            "flat": {
                # All fingers extended straight
                "index": [0, 0, 0],
                "middle": [0, 0, 0],
                "ring": [0, 0, 0],
                "pinky": [0, 0, 0],
                "thumb": [0, 0, 0],
            },
            "curved": {
                # Fingers slightly curved, forming C shape
                "index": [0, 30, 0],
                "middle": [0, 30, 0],
                "ring": [0, 30, 0],
                "pinky": [0, 30, 0],
                "thumb": [-20, 15, 5],
            },
            "point": {
                # One finger extended, others closed
                "index": [0, 0, 0],  # Extended
                "middle": [0, 90, 0],  # Closed
                "ring": [0, 90, 0],  # Closed
                "pinky": [0, 90, 0],  # Closed
                "thumb": [-20, 30, 10],  # Partially closed
            },
        }

    def _init_universal_actions(self) -> Dict[str, Dict[str, Any]]:
        """Universal action mappings"""
        return {
            "raise_arm": {
                "arm": [0, 45, -30],  # Lift arm up and out
                "forearm": [0, 0, 0],  # Keep forearm neutral
            },
            "bend_elbow": {
                "forearm": [0, 90, 0],  # 90 degree bend at elbow
            },
            "arm_to_side": {
                "arm": [0, 0, -90],  # Arm out to side
            },
            "arm_forward": {
                "arm": [0, 45, 0],  # Arm forward
            },
            "hand_up": {
                "hand": [0, -30, 0],  # Wrist bent up
            },
            "hand_flat": {
                "hand": [0, 0, 0],  # Neutral wrist position
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
        for universal_action, synonyms in keywords["actions"].items():
            if any(word in synonyms for word in words):
                try:
                    detected_actions.append(UniversalAction(universal_action))
                except ValueError:
                    continue

        # Match body parts
        for universal_part, synonyms in keywords["body_parts"].items():
            if any(word in synonyms for word in words):
                try:
                    detected_body_parts.append(BodyPart(universal_part))
                except ValueError:
                    continue

        # Match hand shapes
        for universal_shape, synonyms in keywords["hand_shapes"].items():
            if any(word in synonyms for word in words):
                try:
                    detected_hand_shapes.append(UniversalHandShape(universal_shape))
                except ValueError:
                    continue

        # Match modifiers
        for modifier, synonyms in keywords["modifiers"].items():
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
                pose_data.update(finger_pose)

            # Apply action-specific poses
            if (
                instr.action == UniversalAction.RAISE
                and instr.body_part == BodyPart.ARM
            ):
                arm_pose = self._apply_arm_action("raise_arm", hand)
                pose_data.update(arm_pose)

            if (
                instr.action == UniversalAction.BEND
                and instr.body_part == BodyPart.ELBOW
            ):
                elbow_pose = self._apply_arm_action("bend_elbow", hand)
                pose_data.update(elbow_pose)

            if instr.action == UniversalAction.POINT and instr.body_part in [
                BodyPart.INDEX,
                BodyPart.MIDDLE,
                BodyPart.RING,
                BodyPart.PINKY,
            ]:
                finger_pose = self._apply_single_finger_point(
                    instr.body_part.value, hand
                )
                pose_data.update(finger_pose)

        return pose_data

    def _apply_hand_shape(
        self, shape_mapping: Dict[str, List[float]], hand: str
    ) -> Dict[str, List[float]]:
        """Apply hand shape to specific hand"""
        pose_data: Dict[str, List[float]] = {}
        hand_prefix = hand.lower()

        for finger, hpr in shape_mapping.items():
            if finger == "thumb":
                for i in range(1, 4):  # Thumb has 3 joints
                    joint_key = f"{hand_prefix}_{finger}{i}"
                    if joint_key in self.joint_mappings:
                        pose_data[self.joint_mappings[joint_key]] = hpr
            else:
                for i in range(1, 4):  # Other fingers have 3 joints
                    joint_key = f"{hand_prefix}_{finger}{i}"
                    if joint_key in self.joint_mappings:
                        pose_data[self.joint_mappings[joint_key]] = hpr

        return pose_data

    def _apply_arm_action(self, action_key: str, hand: str) -> Dict[str, List[float]]:
        """Apply arm/elbow actions"""
        pose_data: Dict[str, List[float]] = {}
        hand_prefix = hand.lower()

        if action_key in self.universal_actions:
            action_mapping = self.universal_actions[action_key]
            for body_part, hpr in action_mapping.items():
                joint_key = f"{hand_prefix}_{body_part}"
                if joint_key in self.joint_mappings:
                    pose_data[self.joint_mappings[joint_key]] = hpr

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
                [0.0, 0.0, 0.0] if f == finger else [0.0, 90.0, 0.0]
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
