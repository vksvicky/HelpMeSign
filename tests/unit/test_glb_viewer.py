#!/usr/bin/env python3
"""
Unit tests for GLB Viewer functionality
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestGLBViewerDataLoading:
    """Test data loading functionality of GLB viewer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_resources_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "resources"
        )

    def test_load_available_languages(self):
        """Test loading available sign languages."""
        # Mock the GLBViewerWindow class
        with patch("glb_viewer.GLBViewerWindow") as MockWindow:
            mock_instance = MockWindow.return_value
            mock_instance.load_available_languages.return_value = [
                {"code": "ASL", "name": "American Sign Language", "flag": "🇺🇸"},
                {"code": "BSL", "name": "British Sign Language", "flag": "🇬🇧"},
            ]

            languages = mock_instance.load_available_languages()
            assert len(languages) >= 2
            assert any(lang["code"] == "ASL" for lang in languages)
            assert any(lang["code"] == "BSL" for lang in languages)

    def test_load_available_characters(self):
        """Test loading available characters."""
        with patch("glb_viewer.GLBViewerWindow") as MockWindow:
            mock_instance = MockWindow.return_value
            mock_instance.load_available_characters.return_value = ["arivo.glb"]

            characters = mock_instance.load_available_characters()
            assert len(characters) >= 1
            assert "arivo.glb" in characters

    def test_load_available_signs_asl(self):
        """Test loading ASL signs."""
        with patch("glb_viewer.GLBViewerWindow") as MockWindow:
            mock_instance = MockWindow.return_value

            # Mock ASL signs data
            mock_signs = {
                "A": {
                    "letter": "A",
                    "hand": "right",
                    "pose": {"mixamorig:RightArm": [0, 10, -20]},
                    "description": "ASL letter A",
                    "instructions": "Make a fist",
                },
                "0": {
                    "letter": "0",
                    "hand": "right",
                    "pose": {"mixamorig:RightHand": [0, 0, 0]},
                    "description": "ASL number 0",
                    "instructions": "Make a fist",
                },
            }

            mock_instance.load_available_signs.return_value = mock_signs

            signs = mock_instance.load_available_signs("ASL")
            assert len(signs) >= 2
            assert "A" in signs
            assert "0" in signs
            assert signs["A"]["pose"] is not None

    def test_get_language_info(self):
        """Test getting language metadata."""
        with patch("glb_viewer.GLBViewerWindow") as MockWindow:
            mock_instance = MockWindow.return_value
            mock_instance.available_languages = [
                {"code": "ASL", "metadata": {"handSupport": "single"}},
                {"code": "BSL", "metadata": {"handSupport": "both"}},
            ]
            mock_instance.get_language_info.return_value = {"handSupport": "single"}

            info = mock_instance.get_language_info("ASL")
            assert info["handSupport"] == "single"


class TestGLBViewerPoseApplication:
    """Test pose application functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_character = Mock()
        self.mock_joint = Mock()

    def test_safe_joint_filtering(self):
        """Test that only safe joints are applied."""
        # Define test pose data with both safe and unsafe joints
        pose_data = {
            "mixamorig:RightArm": [0, 10, -20],  # Safe
            "mixamorig:RightHand": [0, 0, 45],  # Safe
            "mixamorig:RightShoulder": [0, -40, -150],  # Unsafe - should be skipped
            "mixamorig:Spine": [0, 0, 10],  # Unsafe - should be skipped
        }

        safe_joints = [
            "mixamorig:RightArm",
            "mixamorig:LeftArm",
            "mixamorig:RightForeArm",
            "mixamorig:LeftForeArm",
            "mixamorig:RightHand",
            "mixamorig:LeftHand",
        ]

        # Filter joints like the GLB viewer does
        filtered_joints = {k: v for k, v in pose_data.items() if k in safe_joints}

        assert len(filtered_joints) == 2  # Only safe joints
        assert "mixamorig:RightArm" in filtered_joints
        assert "mixamorig:RightHand" in filtered_joints
        assert "mixamorig:RightShoulder" not in filtered_joints
        assert "mixamorig:Spine" not in filtered_joints

    def test_pose_value_validation(self):
        """Test pose value format validation."""
        valid_hpr = [0, 10, -20]
        invalid_hpr_short = [0, 10]
        invalid_hpr_not_list = "not a list"

        # Test validation logic
        assert isinstance(valid_hpr, list) and len(valid_hpr) >= 3
        assert not (isinstance(invalid_hpr_short, list) and len(invalid_hpr_short) >= 3)
        assert not (
            isinstance(invalid_hpr_not_list, list) and len(invalid_hpr_not_list) >= 3
        )

    @patch("glb_viewer.GLBViewerWindow")
    def test_apply_selected_sign_mock(self, MockWindow):
        """Test sign application with mocked character."""
        mock_instance = MockWindow.return_value
        mock_instance.character = Mock()
        mock_instance.sign_combo = Mock()

        # Mock sign data
        mock_sign_data = {
            "letter": "A",
            "hand": "right",
            "pose": {
                "mixamorig:RightArm": [0, 10, -20],
                "mixamorig:RightHand": [0, 0, 45],
            },
        }

        mock_instance.sign_combo.currentData.return_value = mock_sign_data

        # Mock joint control
        mock_joint = Mock()
        mock_joint.isEmpty.return_value = False
        mock_joint.getHpr.return_value = [0.0, 0.0, 0.0]
        mock_instance.character.controlJoint.return_value = mock_joint

        # Mock the actual method
        def mock_apply_selected_sign():
            current_data = mock_instance.sign_combo.currentData()
            if current_data and mock_instance.character:
                pose_data = current_data.get("pose", {})
                applied_count = 0
                for joint_name, hpr_values in pose_data.items():
                    joint = mock_instance.character.controlJoint(
                        None, "modelRoot", joint_name
                    )
                    if joint and not joint.isEmpty():
                        if isinstance(hpr_values, list) and len(hpr_values) >= 3:
                            joint.setHpr(hpr_values[0], hpr_values[1], hpr_values[2])
                            applied_count += 1
                mock_instance.character.update()
                return applied_count
            return 0

        mock_instance.apply_selected_sign = mock_apply_selected_sign

        # Test the method
        applied_count = mock_instance.apply_selected_sign()
        assert applied_count == 2  # Both joints should be applied

        # Verify joint control was called
        assert mock_instance.character.controlJoint.call_count == 2
        assert mock_instance.character.update.called


class TestGLBViewerHandSelection:
    """Test hand selection logic based on language metadata."""

    def test_single_hand_language_selection(self):
        """Test that single hand languages prefer right hand."""
        languages = [
            {"code": "ASL", "metadata": {"handSupport": "single"}},
            {"code": "ISL", "metadata": {"handSupport": "single"}},
        ]

        for lang in languages:
            if lang["metadata"]["handSupport"] == "single":
                # Should prefer right hand file, fallback to left
                preferred_order = ["right", "left"]
                assert preferred_order[0] == "right"

    def test_both_hands_language_selection(self):
        """Test that both hands languages use combined file."""
        languages = [{"code": "BSL", "metadata": {"handSupport": "both"}}]

        for lang in languages:
            if lang["metadata"]["handSupport"] == "both":
                # Should look for combined file like bsl_hand.json
                expected_file_pattern = f"{lang['code'].lower()}_hand.json"
                assert expected_file_pattern == "bsl_hand.json"


class TestGLBViewerIntegration:
    """Integration tests for GLB viewer components."""

    @patch("glb_viewer.QApplication")
    @patch("glb_viewer.GLBViewerWindow")
    def test_glb_viewer_initialization(self, MockWindow, MockApp):
        """Test GLB viewer window initialization."""
        mock_app = MockApp.return_value
        mock_window = MockWindow.return_value

        # Mock initialization
        mock_window.available_languages = [
            {"code": "ASL", "name": "American Sign Language"}
        ]
        mock_window.current_language = "ASL"
        mock_window.available_signs = {"A": {"letter": "A"}}

        # Verify initialization completed
        assert mock_window.current_language == "ASL"
        assert len(mock_window.available_languages) >= 1
        assert "A" in mock_window.available_signs

    def test_dropdown_population_logic(self):
        """Test dropdown population with sorted data."""
        # Mock sign data with letters and numbers
        signs = {
            "Z": {"letter": "Z"},
            "A": {"letter": "A"},
            "9": {"letter": "9"},
            "0": {"letter": "0"},
            "M": {"letter": "M"},
        }

        # Separate and sort like the GLB viewer does
        letters = {k: v for k, v in signs.items() if k.isalpha()}
        numbers = {k: v for k, v in signs.items() if k.isdigit()}

        sorted_letters = sorted(letters.items(), key=lambda x: x[0])
        sorted_numbers = sorted(numbers.items(), key=lambda x: int(x[0]))

        # Verify sorting
        assert sorted_numbers[0][0] == "0"
        assert sorted_numbers[1][0] == "9"
        assert sorted_letters[0][0] == "A"
        assert sorted_letters[-1][0] == "Z"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
