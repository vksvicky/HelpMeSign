#!/usr/bin/env python3
"""
Unit tests for the instruction parser system
Tests natural language instruction parsing and pose generation
"""

import json
import sys
from pathlib import Path

# Add the instruction parser directly to avoid full app imports
sys.path.insert(
    0,
    str(
        Path(__file__).parent.parent.parent.parent
        / "src"
        / "helpmesign"
        / "modes"
        / "learn"
    ),
)

from instruction_parser import InstructionParser


class TestInstructionParser:
    """Test cases for the instruction parser"""

    def __init__(self):
        self.parser = InstructionParser("asl")
        self.test_results = []

    def run_test(self, test_name, test_func):
        """Run a single test and record results"""
        try:
            test_func()
            self.test_results.append(f"✅ {test_name}")
            print(f"✅ {test_name}")
        except Exception as e:
            self.test_results.append(f"❌ {test_name}: {e}")
            print(f"❌ {test_name}: {e}")

    def test_parser_initialization(self):
        """Test that parser initializes correctly"""
        assert self.parser.language_code == "asl"
        assert self.parser.lexicon is not None
        assert self.parser.handshape_presets is not None
        assert self.parser.location_presets is not None
        assert self.parser.natural_pose is not None

    def test_instruction_parsing_basic(self):
        """Test basic instruction parsing"""
        instruction = "Raise your right arm with elbow bent, make a fist with thumb extended to the side"
        dsl = self.parser.parse_instruction(instruction)

        assert dsl["hand"] == "dominant"
        assert dsl["handshape"] == "fist"
        assert dsl["location"] == "elbow"
        assert dsl["orientation"] == "palm_in"
        assert dsl["contact"] == "none"
        assert dsl["movement"]["type"] == "none"
        assert dsl["angles"]["elbow"] == 45
        assert dsl["timing"]["hold_ms"] == 600

    def test_instruction_parsing_flat_hand(self):
        """Test parsing flat hand instruction"""
        instruction = "Hold your right hand flat with all fingers together and extended"
        dsl = self.parser.parse_instruction(instruction)

        assert dsl["hand"] == "dominant"
        assert dsl["handshape"] == "flat"
        assert dsl["location"] == "neutral_space"
        assert dsl["orientation"] == "palm_in"

    def test_instruction_parsing_curved_hand(self):
        """Test parsing curved hand instruction"""
        instruction = "Curve your right hand fingers and thumb to form a C shape"
        dsl = self.parser.parse_instruction(instruction)

        assert dsl["hand"] == "dominant"
        assert dsl["handshape"] == "c_shape"
        assert dsl["location"] == "neutral_space"

    def test_instruction_parsing_pointing(self):
        """Test parsing pointing instruction"""
        instruction = "Extend only your index finger on your right hand"
        dsl = self.parser.parse_instruction(instruction)

        assert dsl["hand"] == "dominant"
        assert dsl["handshape"] == "point"
        assert dsl["location"] == "neutral_space"

    def test_instruction_parsing_touch(self):
        """Test parsing touch instruction"""
        instruction = "Touch your forehead with your index finger"
        dsl = self.parser.parse_instruction(instruction)

        assert dsl["hand"] == "dominant"
        assert dsl["handshape"] == "point"
        assert dsl["location"] == "forehead"
        assert dsl["contact"] == "touch"

    def test_pose_generation_from_instruction(self):
        """Test pose generation from natural language instruction"""
        instruction = "Raise your right arm with elbow bent, make a fist with thumb extended to the side"
        pose = self.parser.generate_pose_from_instruction(instruction)

        assert len(pose) > 0
        assert "mixamorig:RightArm" in pose
        assert "mixamorig:RightForeArm" in pose
        assert "mixamorig:RightHand" in pose

        # Check that elbow angle is applied
        assert pose["mixamorig:RightForeArm"] == [0.0, 45, 0.0]

    def test_pose_generation_from_dsl(self):
        """Test pose generation from DSL structure"""
        dsl = {
            "hand": "dominant",
            "handshape": "fist",
            "location": "neutral_space",
            "orientation": "palm_in",
            "contact": "none",
            "movement": {"type": "none"},
            "angles": {"elbow": 45},
            "timing": {"hold_ms": 600},
        }

        pose = self.parser.generate_pose_from_dsl(dsl)

        assert len(pose) > 0
        assert "mixamorig:RightHand" in pose
        assert "mixamorig:RightForeArm" in pose

        # Check that elbow angle is applied
        assert pose["mixamorig:RightForeArm"] == [0.0, 45, 0.0]

    def test_sign_data_loading(self):
        """Test loading sign data from unified file"""
        sign_data = self.parser.get_sign_data("A")

        assert sign_data is not None
        assert "description" in sign_data
        assert "instructions" in sign_data
        assert "svg" in sign_data
        assert "dsl" in sign_data

    def test_pose_generation_from_sign(self):
        """Test pose generation from sign symbol"""
        pose = self.parser.generate_pose_from_sign("A")

        assert len(pose) > 0
        assert "mixamorig:RightHand" in pose
        assert "mixamorig:RightForeArm" in pose

    def test_handshape_presets_loading(self):
        """Test that handshape presets are loaded from universal config"""
        assert "fist" in self.parser.handshape_presets
        assert "flat" in self.parser.handshape_presets
        assert "curved" in self.parser.handshape_presets
        assert "c_shape" in self.parser.handshape_presets
        assert "point" in self.parser.handshape_presets

        # Check that fist preset has correct structure
        fist_preset = self.parser.handshape_presets["fist"]
        assert "mixamorig:RightHand" in fist_preset
        assert "mixamorig:LeftHand" in fist_preset
        assert "mixamorig:RightHandIndex1" in fist_preset

    def test_location_presets_loading(self):
        """Test that location presets are loaded from universal config"""
        assert "neutral_space" in self.parser.location_presets
        assert "forehead" in self.parser.location_presets
        assert "chin" in self.parser.location_presets
        assert "chest" in self.parser.location_presets

        # Check that neutral_space preset has correct structure
        neutral_preset = self.parser.location_presets["neutral_space"]
        assert "mixamorig:RightArm" in neutral_preset
        assert "mixamorig:LeftArm" in neutral_preset

    def test_natural_pose_loading(self):
        """Test that natural pose is loaded from universal config"""
        assert len(self.parser.natural_pose) > 0
        assert "mixamorig:RightHand" in self.parser.natural_pose
        assert "mixamorig:LeftHand" in self.parser.natural_pose
        assert "mixamorig:RightArm" in self.parser.natural_pose
        assert "mixamorig:LeftArm" in self.parser.natural_pose

    def test_lexicon_loading(self):
        """Test that lexicon is loaded from unified file"""
        assert self.parser.lexicon is not None
        assert "handshapes" in self.parser.lexicon
        assert "locations" in self.parser.lexicon
        assert "orientations" in self.parser.lexicon
        assert "actions" in self.parser.lexicon

    def test_tokenization(self):
        """Test instruction tokenization"""
        tokens = self.parser._tokenize("Raise your right arm with elbow bent")
        expected = ["Raise", "your", "right", "arm", "with", "elbow", "bent"]
        assert tokens == expected

    def test_hand_extraction(self):
        """Test hand information extraction"""
        assert self.parser._extract_hand(["right"]) == "dominant"
        assert self.parser._extract_hand(["left"]) == "non_dominant"
        assert self.parser._extract_hand(["both"]) == "both"
        assert (
            self.parser._extract_hand(["some", "other", "words"]) == "dominant"
        )  # default

    def test_contact_extraction(self):
        """Test contact information extraction"""
        assert self.parser._extract_contact(["touch"]) == "touch"
        assert self.parser._extract_contact(["hover"]) == "hover"
        assert self.parser._extract_contact(["grasp"]) == "grasp"
        assert (
            self.parser._extract_contact(["some", "other", "words"]) == "none"
        )  # default

    def test_movement_extraction(self):
        """Test movement information extraction"""
        movement = self.parser._extract_movement(["move", "up"])
        assert movement["type"] == "line"
        assert movement["direction"] == "up"

        movement = self.parser._extract_movement(["draw", "down"])
        assert movement["type"] == "line"
        assert movement["direction"] == "down"

        movement = self.parser._extract_movement(["some", "other", "words"])
        assert movement["type"] == "none"

    def test_angle_extraction(self):
        """Test angle information extraction"""
        angles = self.parser._extract_angles(["elbow", "bent"])
        assert angles["elbow"] == 45

        angles = self.parser._extract_angles(["elbow", "straight"])
        assert angles["elbow"] == 0

        angles = self.parser._extract_angles(["shoulder", "raised"])
        assert angles["shoulder"] == -30

        angles = self.parser._extract_angles(["some", "other", "words"])
        assert angles == {}

    def test_full_instruction_to_pose_pipeline(self):
        """Test the complete pipeline from instruction to pose"""
        test_cases = [
            {
                "instruction": "Raise your right arm with elbow bent, make a fist with thumb extended to the side",
                "expected_handshape": "fist",
                "expected_angles": {"elbow": 45},
            },
            {
                "instruction": "Hold your right hand flat with all fingers together and extended",
                "expected_handshape": "flat",
                "expected_angles": {},
            },
            {
                "instruction": "Curve your right hand fingers and thumb to form a C shape",
                "expected_handshape": "c_shape",
                "expected_angles": {},
            },
            {
                "instruction": "Extend only your index finger on your right hand",
                "expected_handshape": "point",
                "expected_angles": {},
            },
            {
                "instruction": "Touch your forehead with your index finger",
                "expected_handshape": "point",
                "expected_location": "forehead",
                "expected_contact": "touch",
                "expected_angles": {},
            },
        ]

        for test_case in test_cases:
            instruction = test_case["instruction"]

            # Parse instruction to DSL
            dsl = self.parser.parse_instruction(instruction)

            # Verify DSL structure
            assert dsl["hand"] == "dominant"
            assert dsl["handshape"] == test_case["expected_handshape"]

            if "expected_location" in test_case:
                assert dsl["location"] == test_case["expected_location"]

            if "expected_contact" in test_case:
                assert dsl["contact"] == test_case["expected_contact"]

            if "expected_angles" in test_case:
                assert dsl["angles"] == test_case["expected_angles"]

            # Generate pose from DSL
            pose = self.parser.generate_pose_from_dsl(dsl)

            # Verify pose has expected joints
            assert len(pose) > 0
            assert "mixamorig:RightHand" in pose
            assert "mixamorig:RightForeArm" in pose

            # Verify angle overrides are applied
            if test_case["expected_angles"]:
                for joint, angle in test_case["expected_angles"].items():
                    if joint == "elbow":
                        assert pose["mixamorig:RightForeArm"] == [0.0, angle, 0.0]
                    elif joint == "shoulder":
                        assert pose["mixamorig:RightArm"] == [0.0, angle, 0.0]

    def test_sign_symbol_to_pose_pipeline(self):
        """Test the complete pipeline from sign symbol to pose"""
        test_symbols = ["A", "B", "C", "1", "2"]

        for symbol in test_symbols:
            # Get sign data
            sign_data = self.parser.get_sign_data(symbol)
            assert sign_data is not None, f"No sign data found for symbol: {symbol}"

            # Verify sign data structure
            assert "description" in sign_data
            assert "instructions" in sign_data
            assert "svg" in sign_data

            # Generate pose from sign
            pose = self.parser.generate_pose_from_sign(symbol)
            assert len(pose) > 0, f"No pose generated for symbol: {symbol}"

            # Verify pose has expected joints
            assert "mixamorig:RightHand" in pose
            assert "mixamorig:RightForeArm" in pose

    def run_all_tests(self):
        """Run all tests"""
        print("=== Instruction Parser Tests ===\n")

        # Basic functionality tests
        self.run_test("Parser Initialization", self.test_parser_initialization)
        self.run_test("Basic Instruction Parsing", self.test_instruction_parsing_basic)
        self.run_test("Flat Hand Parsing", self.test_instruction_parsing_flat_hand)
        self.run_test("Curved Hand Parsing", self.test_instruction_parsing_curved_hand)
        self.run_test("Pointing Parsing", self.test_instruction_parsing_pointing)
        self.run_test("Touch Parsing", self.test_instruction_parsing_touch)

        # Pose generation tests
        self.run_test(
            "Pose Generation from Instruction",
            self.test_pose_generation_from_instruction,
        )
        self.run_test("Pose Generation from DSL", self.test_pose_generation_from_dsl)
        self.run_test("Sign Data Loading", self.test_sign_data_loading)
        self.run_test("Pose Generation from Sign", self.test_pose_generation_from_sign)

        # Configuration loading tests
        self.run_test("Handshape Presets Loading", self.test_handshape_presets_loading)
        self.run_test("Location Presets Loading", self.test_location_presets_loading)
        self.run_test("Natural Pose Loading", self.test_natural_pose_loading)
        self.run_test("Lexicon Loading", self.test_lexicon_loading)

        # Utility function tests
        self.run_test("Tokenization", self.test_tokenization)
        self.run_test("Hand Extraction", self.test_hand_extraction)
        self.run_test("Contact Extraction", self.test_contact_extraction)
        self.run_test("Movement Extraction", self.test_movement_extraction)
        self.run_test("Angle Extraction", self.test_angle_extraction)

        # Integration tests
        self.run_test(
            "Full Instruction to Pose Pipeline",
            self.test_full_instruction_to_pose_pipeline,
        )
        self.run_test(
            "Sign Symbol to Pose Pipeline", self.test_sign_symbol_to_pose_pipeline
        )

        # Summary
        print("\n=== Test Summary ===")
        passed = sum(1 for result in self.test_results if result.startswith("✅"))
        total = len(self.test_results)
        print(f"Passed: {passed}/{total}")

        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("❌ Some tests failed!")
            for result in self.test_results:
                if result.startswith("❌"):
                    print(f"  {result}")


if __name__ == "__main__":
    # Run tests if executed directly
    test_suite = TestInstructionParser()
    test_suite.run_all_tests()
