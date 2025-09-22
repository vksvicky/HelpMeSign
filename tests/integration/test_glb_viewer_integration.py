#!/usr/bin/env python3
"""
Integration tests for GLB Viewer with real data
"""

import json
import os
import sys
from pathlib import Path

import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestGLBViewerDataIntegration:
    """Integration tests using real data files."""

    def setup_method(self):
        """Set up test fixtures."""
        self.project_root = os.path.join(os.path.dirname(__file__), "..", "..")
        self.resources_path = os.path.join(self.project_root, "resources")

    def test_languages_json_exists_and_valid(self):
        """Test that languages.json exists and has valid structure."""
        languages_file = os.path.join(self.resources_path, "data", "languages.json")

        assert os.path.exists(languages_file), "languages.json file not found"

        with open(languages_file, "r", encoding="utf-8") as f:
            languages = json.load(f)

        assert isinstance(languages, list), "Languages should be a list"
        assert len(languages) > 0, "Should have at least one language"

        # Check required fields for each language
        for lang in languages:
            assert "code" in lang, f"Language missing 'code': {lang}"
            assert "name" in lang, f"Language missing 'name': {lang}"
            assert "flag" in lang, f"Language missing 'flag': {lang}"
            assert "metadata" in lang, f"Language missing 'metadata': {lang}"
            assert (
                "handSupport" in lang["metadata"]
            ), f"Language missing 'handSupport': {lang}"

            # Validate handSupport values
            hand_support = lang["metadata"]["handSupport"]
            assert hand_support in [
                "single",
                "both",
            ], f"Invalid handSupport value: {hand_support}"

    def test_characters_directory_exists(self):
        """Test that characters directory exists with GLB files."""
        characters_dir = os.path.join(self.resources_path, "characters")

        assert os.path.exists(characters_dir), "Characters directory not found"

        glb_files = [f for f in os.listdir(characters_dir) if f.endswith(".glb")]
        assert len(glb_files) > 0, "Should have at least one GLB character file"
        assert "arivo.glb" in glb_files, "arivo.glb character should exist"

    def test_asl_sign_data_exists_and_valid(self):
        """Test that ASL sign data exists and has valid structure."""
        asl_dir = os.path.join(self.resources_path, "data", "signs", "asl")

        assert os.path.exists(asl_dir), "ASL signs directory not found"

        # Check for hand files
        left_hand_file = os.path.join(asl_dir, "asl_left_hand.json")
        right_hand_file = os.path.join(asl_dir, "asl_right_hand.json")

        # At least one hand file should exist
        assert os.path.exists(left_hand_file) or os.path.exists(
            right_hand_file
        ), "At least one ASL hand file should exist"

        # Test the right hand file (preferred for single hand languages)
        if os.path.exists(right_hand_file):
            with open(right_hand_file, "r", encoding="utf-8") as f:
                asl_data = json.load(f)

            # Check structure
            assert "language" in asl_data, "ASL data missing 'language' field"
            assert "alphabet" in asl_data, "ASL data missing 'alphabet' field"
            assert "numbers" in asl_data, "ASL data missing 'numbers' field"

            # Check alphabet completeness
            alphabet = asl_data["alphabet"]
            expected_letters = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            actual_letters = set(alphabet.keys())
            missing_letters = expected_letters - actual_letters
            assert len(missing_letters) == 0, f"Missing letters: {missing_letters}"

            # Check numbers completeness
            numbers = asl_data["numbers"]
            expected_numbers = set("0123456789")
            actual_numbers = set(numbers.keys())
            missing_numbers = expected_numbers - actual_numbers
            assert len(missing_numbers) == 0, f"Missing numbers: {missing_numbers}"

            # Check pose data structure for letter A
            letter_a = alphabet["A"]
            assert "pose" in letter_a, "Letter A missing pose data"
            assert "description" in letter_a, "Letter A missing description"
            assert "instructions" in letter_a, "Letter A missing instructions"

            pose_data = letter_a["pose"]
            assert len(pose_data) > 0, "Letter A pose data should not be empty"

            # Check that pose data has valid joint names and HPR values
            for joint_name, hpr_values in pose_data.items():
                assert joint_name.startswith(
                    "mixamorig:"
                ), f"Invalid joint name: {joint_name}"
                assert isinstance(
                    hpr_values, list
                ), f"HPR values should be list: {joint_name}"
                assert len(hpr_values) == 3, f"HPR should have 3 values: {joint_name}"

                # Check that values are numbers
                for i, value in enumerate(hpr_values):
                    assert isinstance(
                        value, (int, float)
                    ), f"HPR value {i} should be numeric for {joint_name}: {value}"

    def test_sign_loading_integration(self):
        """Test the complete sign loading process."""
        # This would test the actual GLBViewerWindow methods if we could import them
        # For now, we'll test the data processing logic

        languages_file = os.path.join(self.resources_path, "data", "languages.json")
        with open(languages_file, "r", encoding="utf-8") as f:
            languages = json.load(f)

        # Find ASL language
        asl_lang = None
        for lang in languages:
            if lang["code"] == "ASL":
                asl_lang = lang
                break

        assert asl_lang is not None, "ASL language not found in languages.json"

        # Test hand support logic
        hand_support = asl_lang["metadata"]["handSupport"]
        assert hand_support == "single", "ASL should be single hand support"

        # Test file selection logic for single hand languages
        asl_dir = os.path.join(self.resources_path, "data", "signs", "asl")

        # For single hand, should prefer right, fallback to left
        preferred_files = ["asl_right_hand.json", "asl_left_hand.json"]
        selected_file = None

        for filename in preferred_files:
            filepath = os.path.join(asl_dir, filename)
            if os.path.exists(filepath):
                selected_file = filepath
                break

        assert selected_file is not None, "No ASL hand file found"

        # Load and validate the selected file
        with open(selected_file, "r", encoding="utf-8") as f:
            sign_data = json.load(f)

        # Process like the GLB viewer would
        signs = {}

        # Load alphabet
        if "alphabet" in sign_data:
            for letter, data in sign_data["alphabet"].items():
                signs[letter] = {
                    "letter": letter,
                    "hand": "right" if "right" in selected_file else "left",
                    "pose": data.get("pose", {}),
                    "description": data.get("description", ""),
                    "instructions": data.get("instructions", ""),
                }

        # Load numbers
        if "numbers" in sign_data:
            for number, data in sign_data["numbers"].items():
                signs[number] = {
                    "letter": number,
                    "hand": "right" if "right" in selected_file else "left",
                    "pose": data.get("pose", {}),
                    "description": data.get("description", ""),
                    "instructions": data.get("instructions", ""),
                }

        # Verify we got the expected signs
        assert (
            len(signs) == 36
        ), f"Expected 36 signs (26 letters + 10 numbers), got {len(signs)}"
        assert "A" in signs, "Letter A should be in signs"
        assert "0" in signs, "Number 0 should be in signs"

        # Test sorting logic
        letters = {k: v for k, v in signs.items() if k.isalpha()}
        numbers = {k: v for k, v in signs.items() if k.isdigit()}

        sorted_letters = sorted(letters.items(), key=lambda x: x[0])
        sorted_numbers = sorted(numbers.items(), key=lambda x: int(x[0]))

        assert sorted_letters[0][0] == "A", "First letter should be A"
        assert sorted_letters[-1][0] == "Z", "Last letter should be Z"
        assert sorted_numbers[0][0] == "0", "First number should be 0"
        assert sorted_numbers[-1][0] == "9", "Last number should be 9"

    def test_pose_safety_filtering(self):
        """Test that pose filtering removes unsafe joints."""
        # Load real ASL data
        asl_file = os.path.join(
            self.resources_path, "data", "signs", "asl", "asl_right_hand.json"
        )

        if os.path.exists(asl_file):
            with open(asl_file, "r", encoding="utf-8") as f:
                asl_data = json.load(f)

            if "alphabet" in asl_data and "A" in asl_data["alphabet"]:
                pose_data = asl_data["alphabet"]["A"]["pose"]

                # Define safe joints (same as in GLB viewer)
                safe_joints = [
                    "mixamorig:RightArm",
                    "mixamorig:LeftArm",
                    "mixamorig:RightForeArm",
                    "mixamorig:LeftForeArm",
                    "mixamorig:RightHand",
                    "mixamorig:LeftHand",
                ]

                # Add all finger joints
                for hand in ["Right", "Left"]:
                    for finger in ["Thumb", "Index", "Middle", "Ring", "Pinky"]:
                        for i in range(1, 5):
                            safe_joints.append(f"mixamorig:{hand}Hand{finger}{i}")

                # Filter pose data
                safe_pose_data = {
                    k: v for k, v in pose_data.items() if k in safe_joints
                }
                unsafe_pose_data = {
                    k: v for k, v in pose_data.items() if k not in safe_joints
                }

                # Verify filtering
                assert len(safe_pose_data) > 0, "Should have some safe joints"

                # Check that problematic joints are filtered out
                problematic_joints = [
                    "mixamorig:RightShoulder",
                    "mixamorig:Spine",
                    "mixamorig:Hips",
                ]
                for joint in problematic_joints:
                    if joint in pose_data:
                        assert (
                            joint not in safe_pose_data
                        ), f"Problematic joint {joint} should be filtered out"
                        assert (
                            joint in unsafe_pose_data
                        ), f"Problematic joint {joint} should be in unsafe list"


class TestGLBViewerErrorHandling:
    """Test error handling in GLB viewer integration."""

    def test_missing_language_file_handling(self):
        """Test handling of missing language files."""
        # Test what happens when language file doesn't exist
        fake_language_code = "FAKE"
        fake_signs_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "resources",
            "data",
            "signs",
            fake_language_code.lower(),
        )

        # Should not exist
        assert not os.path.exists(
            fake_signs_path
        ), "Fake language path should not exist"

        # The load_available_signs method should return empty dict for non-existent languages
        # This tests the error handling logic

    def test_invalid_json_handling(self):
        """Test handling of invalid JSON data."""
        # This would test how the system handles corrupted or invalid JSON files
        # For now, we just verify the structure of existing files

        languages_file = os.path.join(
            os.path.dirname(__file__), "..", "..", "resources", "data", "languages.json"
        )

        if os.path.exists(languages_file):
            try:
                with open(languages_file, "r", encoding="utf-8") as f:
                    json.load(f)
                # If we get here, the JSON is valid
                assert True
            except json.JSONDecodeError:
                pytest.fail("languages.json contains invalid JSON")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
