#!/usr/bin/env python3
"""
Pose Validation Panel
Integrates with HPR editor to validate and correct sign language poses
"""

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .hpr_editor import JointPose, PoseManager, SignLanguagePoseEditor
from .ui_components import get_button_style


@dataclass
class PoseValidationResult:
    """Result of pose validation"""

    letter: str
    original_pose: Dict[str, List[float]]
    corrected_pose: Dict[str, List[float]]
    corrections_made: List[str]
    validation_notes: str
    is_valid: bool


class PoseValidationPanel(QWidget):
    """Panel for validating and correcting sign language poses using HPR editor"""

    pose_corrected = Signal(str, Dict[str, List[float]])  # letter, corrected_pose

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_panel = parent
        self.current_letter = None
        self.current_pose_data = {}
        self.validation_results = {}

        # HPR Editor integration
        self.hpr_editor = None
        self.pose_manager = None

        self.setup_ui()
        self.load_pose_data()

    def setup_ui(self):
        """Set up the pose validation UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("Sign Language Pose Validation")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Letter selection
        letter_group = QGroupBox("Select Letter to Validate")
        letter_layout = QHBoxLayout(letter_group)

        self.letter_combo = QComboBox()
        self.letter_combo.addItems([chr(i) for i in range(ord("A"), ord("Z") + 1)])
        self.letter_combo.currentTextChanged.connect(self.on_letter_changed)
        letter_layout.addWidget(QLabel("Letter:"))
        letter_layout.addWidget(self.letter_combo)

        # Hand preference
        self.hand_combo = QComboBox()
        self.hand_combo.addItems(["right", "left"])
        self.hand_combo.setCurrentText("right")
        letter_layout.addWidget(QLabel("Hand:"))
        letter_layout.addWidget(self.hand_combo)

        layout.addWidget(letter_group)

        # Pose buttons
        pose_group = QGroupBox("Pose Actions")
        pose_layout = QGridLayout(pose_group)

        # Load pose button
        self.load_pose_btn = QPushButton("Load Current Pose")
        self.load_pose_btn.setStyleSheet(get_button_style())
        self.load_pose_btn.clicked.connect(self.load_current_pose)
        pose_layout.addWidget(self.load_pose_btn, 0, 0)

        # Open HPR Editor button
        self.open_editor_btn = QPushButton("Open HPR Editor")
        self.open_editor_btn.setStyleSheet(get_button_style())
        self.open_editor_btn.clicked.connect(self.open_hpr_editor)
        pose_layout.addWidget(self.open_editor_btn, 0, 1)

        # Validate pose button
        self.validate_pose_btn = QPushButton("Validate Pose")
        self.validate_pose_btn.setStyleSheet(get_button_style())
        self.validate_pose_btn.clicked.connect(self.validate_current_pose)
        pose_layout.addWidget(self.validate_pose_btn, 1, 0)

        # Save corrections button
        self.save_corrections_btn = QPushButton("Save Corrections")
        self.save_corrections_btn.setStyleSheet(get_button_style())
        self.save_corrections_btn.clicked.connect(self.save_corrections)
        pose_layout.addWidget(self.save_corrections_btn, 1, 1)

        # Reset pose button
        self.reset_pose_btn = QPushButton("Reset to Original")
        self.reset_pose_btn.setStyleSheet(get_button_style())
        self.reset_pose_btn.clicked.connect(self.reset_to_original)
        pose_layout.addWidget(self.reset_pose_btn, 2, 0)

        # Export corrections button
        self.export_btn = QPushButton("Export Corrections")
        self.export_btn.setStyleSheet(get_button_style())
        self.export_btn.clicked.connect(self.export_corrections)
        pose_layout.addWidget(self.export_btn, 2, 1)

        layout.addWidget(pose_group)

        # Current pose display
        pose_display_group = QGroupBox("Current Pose Data")
        pose_display_layout = QVBoxLayout(pose_display_group)

        self.pose_display = QTextEdit()
        self.pose_display.setMaximumHeight(150)
        self.pose_display.setReadOnly(True)
        self.pose_display.setStyleSheet(
            """
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
            }
        """
        )
        pose_display_layout.addWidget(self.pose_display)

        layout.addWidget(pose_display_group)

        # Validation results
        results_group = QGroupBox("Validation Results")
        results_layout = QVBoxLayout(results_group)

        self.results_display = QTextEdit()
        self.results_display.setMaximumHeight(200)
        self.results_display.setReadOnly(True)
        self.results_display.setStyleSheet(
            """
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
            }
        """
        )
        results_layout.addWidget(self.results_display)

        layout.addWidget(results_group)

        # Status bar
        self.status_label = QLabel("Ready to validate poses")
        self.status_label.setStyleSheet("color: #6c757d; font-style: italic;")
        layout.addWidget(self.status_label)

    def load_pose_data(self):
        """Load pose data from JSON files"""
        self.pose_data = {}

        # Load ASL right hand data
        asl_right_path = "resources/data/signs/asl/asl_right_hand.json"
        if os.path.exists(asl_right_path):
            try:
                with open(asl_right_path, "r") as f:
                    data = json.load(f)
                    if "alphabet" in data:
                        self.pose_data["ASL_right"] = data["alphabet"]
            except Exception as e:
                print(f"Error loading ASL right hand data: {e}")

        # Load ASL left hand data
        asl_left_path = "resources/data/signs/asl/asl_left_hand.json"
        if os.path.exists(asl_left_path):
            try:
                with open(asl_left_path, "r") as f:
                    data = json.load(f)
                    if "alphabet" in data:
                        self.pose_data["ASL_left"] = data["alphabet"]
            except Exception as e:
                print(f"Error loading ASL left hand data: {e}")

        self.update_status(f"Loaded pose data for {len(self.pose_data)} languages")

    def on_letter_changed(self, letter: str):
        """Handle letter selection change"""
        self.current_letter = letter
        self.update_pose_display()

    def load_current_pose(self):
        """Load the current pose for the selected letter"""
        if not self.current_letter:
            self.update_status("Please select a letter first")
            return

        hand = self.hand_combo.currentText()
        language_key = f"ASL_{hand}"

        if language_key not in self.pose_data:
            self.update_status(f"No pose data found for {language_key}")
            return

        if self.current_letter not in self.pose_data[language_key]:
            self.update_status(f"No pose data found for letter {self.current_letter}")
            return

        letter_data = self.pose_data[language_key][self.current_letter]
        self.current_pose_data = letter_data.get("pose", {})

        # Initialize pose manager if not exists
        if not self.pose_manager:
            self.pose_manager = PoseManager()

        # Load pose into pose manager
        for joint_name, hpr in self.current_pose_data.items():
            if len(hpr) >= 3:
                pose = JointPose(joint_name, hpr[0], hpr[1], hpr[2])
                self.pose_manager.set_pose(joint_name, pose)

        self.update_pose_display()
        self.update_status(f"Loaded pose for {self.current_letter} ({hand} hand)")

    def open_hpr_editor(self):
        """Open the HPR editor for pose correction"""
        if not self.current_pose_data:
            self.update_status("Please load a pose first")
            return

        if not self.hpr_editor:
            self.hpr_editor = SignLanguagePoseEditor(self.parent_panel)
            self.hpr_editor.pose_changed.connect(self.on_pose_changed)

        # Set the pose manager
        self.hpr_editor.pose_manager = self.pose_manager

        # Show the editor
        self.hpr_editor.show()
        self.update_status(
            "HPR Editor opened - make corrections and click 'Save Corrections'"
        )

    def on_pose_changed(self, joint_name: str, pose: JointPose):
        """Handle pose changes from HPR editor"""
        # Update current pose data
        self.current_pose_data[joint_name] = [pose.heading, pose.pitch, pose.roll]
        self.update_pose_display()

    def validate_current_pose(self):
        """Validate the current pose against constraints"""
        if not self.current_pose_data:
            self.update_status("Please load a pose first")
            return

        from ...utils.joint_constraints import joint_validator

        # Validate pose
        constrained_pose = joint_validator.validate_and_constrain_pose(
            self.current_pose_data
        )
        is_valid = joint_validator.is_pose_valid(self.current_pose_data)

        # Check for violations
        violations = []
        for joint_name, original_hpr in self.current_pose_data.items():
            if joint_name in constrained_pose:
                constrained_hpr = constrained_pose[joint_name]
                if original_hpr != constrained_hpr:
                    violations.append(
                        {
                            "joint": joint_name,
                            "original": original_hpr,
                            "constrained": constrained_hpr,
                        }
                    )

        # Create validation result
        result = PoseValidationResult(
            letter=self.current_letter,
            original_pose=self.current_pose_data.copy(),
            corrected_pose=constrained_pose,
            corrections_made=[
                f"{v['joint']}: {v['original']} → {v['constrained']}"
                for v in violations
            ],
            validation_notes=f"Pose is {'VALID' if is_valid else 'INVALID'} - {len(violations)} violations found",
            is_valid=is_valid,
        )

        self.validation_results[self.current_letter] = result
        self.update_results_display(result)

        status_msg = f"Validation complete: {result.validation_notes}"
        self.update_status(status_msg)

    def save_corrections(self):
        """Save corrections to the pose data"""
        if not self.current_pose_data:
            self.update_status("No pose data to save")
            return

        # Get corrected pose from HPR editor if available
        if self.hpr_editor and self.hpr_editor.pose_manager:
            corrected_pose = {}
            for (
                joint_name,
                pose,
            ) in self.hpr_editor.pose_manager.get_all_poses().items():
                corrected_pose[joint_name] = [pose.heading, pose.pitch, pose.roll]

            # Update current pose data
            self.current_pose_data = corrected_pose

            # Save to file
            self.save_pose_to_file(corrected_pose)

            # Emit signal
            self.pose_corrected.emit(self.current_letter, corrected_pose)

            self.update_status(f"Corrections saved for {self.current_letter}")
        else:
            self.update_status("No corrections to save")

    def save_pose_to_file(self, pose_data: Dict[str, List[float]]):
        """Save pose data to the JSON file"""
        hand = self.hand_combo.currentText()
        file_path = f"resources/data/signs/asl/asl_{hand}_hand.json"

        try:
            # Load existing data
            with open(file_path, "r") as f:
                data = json.load(f)

            # Update pose data
            if "alphabet" in data and self.current_letter in data["alphabet"]:
                data["alphabet"][self.current_letter]["pose"] = pose_data

                # Save back to file
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)

                self.update_status(f"Pose saved to {file_path}")
            else:
                self.update_status(
                    f"Could not find {self.current_letter} in {file_path}"
                )

        except Exception as e:
            self.update_status(f"Error saving pose: {e}")

    def reset_to_original(self):
        """Reset pose to original values"""
        if not self.current_letter:
            self.update_status("Please select a letter first")
            return

        hand = self.hand_combo.currentText()
        language_key = f"ASL_{hand}"

        if (
            language_key in self.pose_data
            and self.current_letter in self.pose_data[language_key]
        ):
            letter_data = self.pose_data[language_key][self.current_letter]
            self.current_pose_data = letter_data.get("pose", {})

            # Reset pose manager
            if self.pose_manager:
                for joint_name, hpr in self.current_pose_data.items():
                    if len(hpr) >= 3:
                        pose = JointPose(joint_name, hpr[0], hpr[1], hpr[2])
                        self.pose_manager.set_pose(joint_name, pose)

            # Update HPR editor if open
            if self.hpr_editor:
                self.hpr_editor.pose_manager = self.pose_manager
                self.hpr_editor.update_pose_display()

            self.update_pose_display()
            self.update_status(f"Reset to original pose for {self.current_letter}")
        else:
            self.update_status(f"No original pose found for {self.current_letter}")

    def export_corrections(self):
        """Export corrections to a file"""
        if not self.validation_results:
            self.update_status("No validation results to export")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Corrections", "pose_corrections.json", "JSON Files (*.json)"
        )

        if file_path:
            try:
                # Prepare export data
                export_data = {
                    "corrections": {},
                    "summary": {
                        "total_letters": len(self.validation_results),
                        "valid_poses": sum(
                            1 for r in self.validation_results.values() if r.is_valid
                        ),
                        "invalid_poses": sum(
                            1
                            for r in self.validation_results.values()
                            if not r.is_valid
                        ),
                    },
                }

                for letter, result in self.validation_results.items():
                    export_data["corrections"][letter] = {
                        "original_pose": result.original_pose,
                        "corrected_pose": result.corrected_pose,
                        "corrections_made": result.corrections_made,
                        "validation_notes": result.validation_notes,
                        "is_valid": result.is_valid,
                    }

                # Save to file
                with open(file_path, "w") as f:
                    json.dump(export_data, f, indent=2)

                self.update_status(f"Corrections exported to {file_path}")

            except Exception as e:
                self.update_status(f"Error exporting corrections: {e}")

    def update_pose_display(self):
        """Update the pose display"""
        if not self.current_pose_data:
            self.pose_display.setText("No pose data loaded")
            return

        # Format pose data for display
        pose_text = f"Letter: {self.current_letter}\n"
        pose_text += f"Hand: {self.hand_combo.currentText()}\n"
        pose_text += f"Joints: {len(self.current_pose_data)}\n\n"

        for joint_name, hpr in self.current_pose_data.items():
            pose_text += f"{joint_name}: [{hpr[0]:.1f}, {hpr[1]:.1f}, {hpr[2]:.1f}]\n"

        self.pose_display.setText(pose_text)

    def update_results_display(self, result: PoseValidationResult):
        """Update the validation results display"""
        results_text = f"Validation Results for {result.letter}\n"
        results_text += f"Status: {result.validation_notes}\n\n"

        if result.corrections_made:
            results_text += "Corrections Made:\n"
            for correction in result.corrections_made:
                results_text += f"  • {correction}\n"
        else:
            results_text += "No corrections needed - pose is valid!\n"

        self.results_display.setText(results_text)

    def update_status(self, message: str):
        """Update the status label"""
        self.status_label.setText(message)
        print(f"Pose Validation: {message}")
