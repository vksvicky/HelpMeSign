#!/usr/bin/env python3
"""
Instruction Parser for Sign Language
Converts natural language instructions to structured DSL and then to pose data
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Joint name constants
RIGHT_HAND = "mixamorig:RightHand"
LEFT_HAND = "mixamorig:LeftHand"
RIGHT_HAND_INDEX1 = "mixamorig:RightHandIndex1"
RIGHT_HAND_MIDDLE1 = "mixamorig:RightHandMiddle1"
RIGHT_HAND_RING1 = "mixamorig:RightHandRing1"
RIGHT_HAND_PINKY1 = "mixamorig:RightHandPinky1"
RIGHT_HAND_THUMB1 = "mixamorig:RightHandThumb1"
LEFT_HAND_INDEX1 = "mixamorig:LeftHandIndex1"
LEFT_HAND_MIDDLE1 = "mixamorig:LeftHandMiddle1"
LEFT_HAND_RING1 = "mixamorig:LeftHandRing1"
LEFT_HAND_PINKY1 = "mixamorig:LeftHandPinky1"
LEFT_HAND_THUMB1 = "mixamorig:LeftHandThumb1"
RIGHT_ARM = "mixamorig:RightArm"
LEFT_ARM = "mixamorig:LeftArm"
RIGHT_FOREARM = "mixamorig:RightForeArm"
LEFT_FOREARM = "mixamorig:LeftForeArm"


class InstructionParser:
    """Parses natural language instructions into structured DSL"""

    def __init__(self, language_code: str = "asl"):
        self.language_code = language_code
        self.lexicon = self._load_lexicon()
        self.universal_config = self._load_universal_config()

        # Extract presets from existing universal config structure
        self.handshape_presets = self._extract_handshape_presets()
        self.location_presets = self._extract_location_presets()
        self.natural_pose = self._extract_natural_pose()

    def _load_lexicon(self) -> Dict[str, Any]:
        """Load language-specific lexicon"""
        try:
            signs_file = Path(
                f"resources/data/signs/{self.language_code}/asl_unified.json"
            )
            with open(signs_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("lexicon", {})
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _load_universal_config(self) -> Dict[str, Any]:
        """Load universal configuration"""
        try:
            config_file = Path("resources/data/pose_generation/universal_config.json")
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _extract_handshape_presets(self) -> Dict[str, Dict[str, List[float]]]:
        """Extract handshape presets from universal config"""
        handshapes = {}
        keywords = self.universal_config.get("keywords", {})
        hand_shapes = keywords.get("hand_shapes", {})

        for handshape_name, handshape_data in hand_shapes.items():
            pose_data = handshape_data.get("pose_data", {})
            if pose_data:
                handshapes[handshape_name] = pose_data

        return handshapes

    def _extract_location_presets(self) -> Dict[str, Dict[str, List[float]]]:
        """Extract location presets from universal config body_parts"""
        locations = {}
        keywords = self.universal_config.get("keywords", {})
        body_parts = keywords.get("body_parts", {})

        # Map body parts to location presets
        location_mapping = {
            "neutral_space": ["arm", "forearm", "hand"],
            "forehead": ["arm", "forearm"],
            "chin": ["arm", "forearm"],
            "chest": ["arm", "forearm", "hand"],
        }

        for location_name, body_part_names in location_mapping.items():
            location_pose = {}
            for body_part in body_part_names:
                if body_part in body_parts:
                    pose_data = body_parts[body_part].get("pose_data", {})
                    location_pose.update(pose_data)
            if location_pose:
                locations[location_name] = location_pose

        return locations

    def _extract_natural_pose(self) -> Dict[str, List[float]]:
        """Extract natural pose from universal config"""
        # Look for natural action or create from body parts
        keywords = self.universal_config.get("keywords", {})
        actions = keywords.get("actions", {})

        if "natural" in actions:
            return actions["natural"].get("pose_data", {})

        # Fallback: combine all body parts for natural pose
        natural_pose = {}
        body_parts = keywords.get("body_parts", {})
        for body_part_data in body_parts.values():
            pose_data = body_part_data.get("pose_data", {})
            natural_pose.update(pose_data)

        return natural_pose

    def parse_instruction(self, instruction_text: str) -> Dict[str, Any]:
        """Convert natural language instruction to structured DSL"""
        # Tokenize and normalize
        tokens = self._tokenize(instruction_text.lower())

        # Extract structured information
        dsl = {
            "hand": self._extract_hand(tokens),
            "handshape": self._extract_handshape(tokens),
            "location": self._extract_location(tokens),
            "orientation": self._extract_orientation(tokens),
            "contact": self._extract_contact(tokens),
            "movement": self._extract_movement(tokens),
            "angles": self._extract_angles(tokens),
            "timing": self._extract_timing(tokens),
        }

        return dsl

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize instruction text"""
        # Remove punctuation and split into words
        text = re.sub(r"[^\w\s]", " ", text)
        return text.split()

    def _extract_hand(self, tokens: List[str]) -> str:
        """Extract hand information"""
        if "left" in tokens:
            return "non_dominant"
        elif "right" in tokens:
            return "dominant"
        elif "both" in tokens:
            return "both"
        return "dominant"  # Default

    def _extract_handshape(self, tokens: List[str]) -> str:
        """Extract handshape from tokens"""
        handshapes = self.lexicon.get("handshapes", {})

        # Look for handshape keywords
        for token in tokens:
            if token in handshapes:
                return handshapes[token]

        # Look for multi-word handshapes
        for i in range(len(tokens) - 1):
            phrase = f"{tokens[i]} {tokens[i+1]}"
            if phrase in handshapes:
                return handshapes[phrase]

        return "fist"  # Default

    def _extract_location(self, tokens: List[str]) -> str:
        """Extract location from tokens"""
        locations = self.lexicon.get("locations", {})

        # Look for location keywords
        for token in tokens:
            if token in locations:
                return locations[token]

        # Look for multi-word locations
        for i in range(len(tokens) - 1):
            phrase = f"{tokens[i]} {tokens[i+1]}"
            if phrase in locations:
                return locations[phrase]

        return "neutral_space"  # Default

    def _extract_orientation(self, tokens: List[str]) -> str:
        """Extract orientation from tokens"""
        orientations = self.lexicon.get("orientations", {})

        # Look for orientation keywords
        for token in tokens:
            if token in orientations:
                return orientations[token]

        # Look for multi-word orientations
        for i in range(len(tokens) - 1):
            phrase = f"{tokens[i]} {tokens[i+1]}"
            if phrase in orientations:
                return orientations[phrase]

        return "palm_in"  # Default

    def _extract_contact(self, tokens: List[str]) -> str:
        """Extract contact information"""
        if "touch" in tokens:
            return "touch"
        elif "hover" in tokens:
            return "hover"
        elif "grasp" in tokens:
            return "grasp"
        return "none"

    def _extract_movement(self, tokens: List[str]) -> Dict[str, Any]:
        """Extract movement information"""
        movement = {"type": "none"}

        if "move" in tokens or "draw" in tokens:
            movement["type"] = "line"
            if "up" in tokens:
                movement["direction"] = "up"
            elif "down" in tokens:
                movement["direction"] = "down"
            elif "left" in tokens:
                movement["direction"] = "left"
            elif "right" in tokens:
                movement["direction"] = "right"

        return movement

    def _extract_angles(self, tokens: List[str]) -> Dict[str, Any]:
        """Extract angle information"""
        angles = {}

        if "elbow" in tokens and "bent" in tokens:
            angles["elbow"] = 45
        elif "elbow" in tokens and "straight" in tokens:
            angles["elbow"] = 0

        if "shoulder" in tokens and "raised" in tokens:
            angles["shoulder"] = -30

        return angles

    def _extract_timing(self, tokens: List[str]) -> Dict[str, Any]:
        """Extract timing information"""
        # tokens parameter is kept for future timing extraction logic
        return {"hold_ms": 600}  # Default timing

    def generate_pose_from_dsl(self, dsl: Dict[str, Any]) -> Dict[str, List[float]]:
        """Generate pose data from DSL"""
        pose = self.natural_pose.copy()

        # Apply handshape
        if dsl.get("handshape") and dsl["handshape"] in self.handshape_presets:
            handshape_pose = self.handshape_presets[dsl["handshape"]]
            pose.update(handshape_pose)

        # Apply location
        if dsl.get("location") and dsl["location"] in self.location_presets:
            location_pose = self.location_presets[dsl["location"]]
            pose.update(location_pose)

        # Apply angle overrides
        if dsl.get("angles"):
            for joint, angle in dsl["angles"].items():
                if joint == "elbow":
                    pose[RIGHT_FOREARM] = [0.0, angle, 0.0]
                    pose[LEFT_FOREARM] = [0.0, angle, 0.0]
                elif joint == "shoulder":
                    pose[RIGHT_ARM] = [0.0, angle, 0.0]
                    pose[LEFT_ARM] = [0.0, angle, 0.0]

        return pose

    def generate_pose_from_instruction(
        self, instruction_text: str
    ) -> Dict[str, List[float]]:
        """Generate pose data from natural language instruction"""
        dsl = self.parse_instruction(instruction_text)
        return self.generate_pose_from_dsl(dsl)

    def get_sign_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get sign data for a specific symbol"""
        try:
            signs_file = Path(
                f"resources/data/signs/{self.language_code}/asl_unified.json"
            )
            with open(signs_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Check alphabet first, then numbers
            if symbol.upper() in data.get("alphabet", {}):
                return data["alphabet"][symbol.upper()]
            elif symbol.upper() in data.get("numbers", {}):
                return data["numbers"][symbol.upper()]

        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass

        return None

    def generate_pose_from_sign(self, symbol: str) -> Dict[str, List[float]]:
        """Generate pose data from sign symbol"""
        sign_data = self.get_sign_data(symbol)
        if not sign_data:
            return {}

        # Use DSL if available, otherwise parse instructions
        if "dsl" in sign_data:
            return self.generate_pose_from_dsl(sign_data["dsl"])
        elif "instructions" in sign_data:
            return self.generate_pose_from_instruction(sign_data["instructions"])

        return {}
