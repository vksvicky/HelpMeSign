"""
Sign Language Pose Editor - Aligned with sign.mt Architecture
Real-time 3D character pose management for sign language applications.
"""

import json
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import QObject, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Panda3D typing fallback
try:
    from panda3d.core import VBase4
except ImportError:

    class VBase4:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass


class PoseType(Enum):
    """Sign language pose types following sign.mt conventions."""

    NEUTRAL = "neutral"
    T_POSE = "t_pose"
    SIGNING = "signing"
    EXPRESSION = "expression"
    CUSTOM = "custom"


@dataclass
class JointPose:
    """Represents a joint's pose in 3D space."""

    joint_name: str
    heading: float = 0.0
    pitch: float = 0.0
    roll: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "joint_name": self.joint_name,
            "hpr": [self.heading, self.pitch, self.roll],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JointPose":
        return cls(
            joint_name=data["joint_name"],
            heading=data["hpr"][0],
            pitch=data["hpr"][1],
            roll=data["hpr"][2],
        )


class PoseManager(QObject):
    """Manages sign language poses following sign.mt patterns."""

    pose_changed = Signal(str, JointPose)
    pose_reset = Signal()

    def __init__(self):
        super().__init__()
        self._poses: Dict[str, JointPose] = {}
        self._neutral_pose = self._create_neutral_pose()
        self._initialize_poses()

    def _create_neutral_pose(self) -> Dict[str, JointPose]:
        """Create neutral pose using the actual character's natural pose values."""
        print("DEBUG: Creating neutral pose with hardcoded natural pose values")

        # Use the hardcoded natural pose values we discovered
        natural_pose_data = {
            "mixamorig:Hips": {"hpr": [0.0, -90.0, 0.0], "pos": [-0.0, 104.3, 1.6]},
            "mixamorig:Spine": {"hpr": [0.0, 0.0, 0.0], "pos": [-0.0, 0.0, 10.2]},
            "mixamorig:Spine1": {"hpr": [0.0, -0.0, 0.0], "pos": [-0.0, -0.0, 10.0]},
            "mixamorig:Spine2": {"hpr": [0.0, 0.0, 0.0], "pos": [-0.0, 0.0, 9.3]},
            "mixamorig:Neck": {"hpr": [-0.0, 0.0, -0.0], "pos": [0.0, 0.0, 16.9]},
            "mixamorig:Head": {"hpr": [0.0, -0.0, 0.0], "pos": [-0.0, -2.8, 9.3]},
            "mixamorig:RightShoulder": {
                "hpr": [150.0, 90.0, 100.0],
                "pos": [-4.6, 0.8, 11.2],
            },
            "mixamorig:RightArm": {"hpr": [0.0, 90.0, 30.0], "pos": [0.0, -0.0, 10.8]},
            "mixamorig:RightForeArm": {
                "hpr": [-20.0, 0.0, 0.0],
                "pos": [-0.0, 0.0, 27.8],
            },
            "mixamorig:RightHand": {"hpr": [0.0, 0.0, 0.0], "pos": [0.0, -0.0, 28.3]},
            "mixamorig:LeftShoulder": {
                "hpr": [-150.0, 80.0, -100.0],
                "pos": [4.6, 0.8, 11.2],
            },
            "mixamorig:LeftArm": {"hpr": [0.0, 80.0, -30.0], "pos": [-0.0, -0.0, 10.8]},
            "mixamorig:LeftForeArm": {
                "hpr": [20.0, 0.0, 0.0],
                "pos": [-0.0, 0.0, 27.8],
            },
            "mixamorig:LeftHand": {"hpr": [-0.0, 0.0, 0.0], "pos": [0.0, -0.0, 28.3]},
        }

        # Convert the natural pose values to JointPose objects
        neutral_poses = {}
        for joint_name, pose_data in natural_pose_data.items():
            hpr = pose_data["hpr"]
            neutral_poses[joint_name] = JointPose(
                joint_name, float(hpr[0]), float(hpr[1]), float(hpr[2])
            )
            print(
                f"DEBUG: Created JointPose for {joint_name}: H={hpr[0]}, P={hpr[1]}, R={hpr[2]}"
            )

        print(
            f"Created neutral pose with {len(neutral_poses)} joints using hardcoded natural pose values"
        )
        print(f"Neutral pose joints: {list(neutral_poses.keys())}")
        return neutral_poses

    def _initialize_poses(self) -> None:
        """Initialize poses with neutral values."""
        self._poses = {name: pose for name, pose in self._neutral_pose.items()}
        print(f"Initialized poses with {len(self._poses)} joints")

    def get_pose(self, joint_name: str) -> Optional[JointPose]:
        """Get pose for a specific joint."""
        return self._poses.get(joint_name)

    def set_pose(self, joint_name: str, pose: JointPose):
        """Set pose for a specific joint."""
        self._poses[joint_name] = pose
        self.pose_changed.emit(joint_name, pose)

    def reset_to_neutral(self):
        """Reset all poses to neutral position."""
        self._poses = {name: pose for name, pose in self._neutral_pose.items()}
        self.pose_reset.emit()

    def get_all_poses(self) -> Dict[str, JointPose]:
        """Get all current poses."""
        return self._poses.copy()

    def export_poses(self) -> str:
        """Export poses as JSON string."""
        poses_dict = {name: pose.to_dict() for name, pose in self._poses.items()}
        return json.dumps(poses_dict, indent=2)

    def import_poses(self, poses_json: str):
        """Import poses from JSON string."""
        try:
            poses_dict = json.loads(poses_json)
            for joint_name, pose_data in poses_dict.items():
                pose = JointPose.from_dict(pose_data)
                self._poses[joint_name] = pose
        except Exception as e:
            print(f"Error importing poses: {e}")


class PoseSlider(QWidget):
    """Individual pose slider component."""

    value_changed = Signal(str, float)

    def __init__(self, axis: str, min_val: float = -180.0, max_val: float = 180.0):
        super().__init__()
        self.axis = axis
        self.setup_ui(min_val, max_val)

    def setup_ui(self, min_val: float, max_val: float):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)

        # Label
        label = QLabel(f"{self.axis}:")
        label.setMinimumWidth(40)
        layout.addWidget(label)

        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(int(min_val * 10), int(max_val * 10))
        self.slider.setValue(0)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(45 * 10)
        layout.addWidget(self.slider)

        # SpinBox
        self.spinbox = QSpinBox()
        self.spinbox.setRange(int(min_val), int(max_val))
        self.spinbox.setValue(0)
        self.spinbox.setSuffix("°")
        self.spinbox.setMinimumWidth(70)
        layout.addWidget(self.spinbox)

        # Connect signals
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.spinbox.valueChanged.connect(self._on_spinbox_changed)

    def _on_slider_changed(self, value: int):
        float_value = value / 10.0
        self.spinbox.setValue(int(float_value))
        self.value_changed.emit(self.axis, float_value)

    def _on_spinbox_changed(self, value: int):
        self.slider.setValue(int(value * 10))
        self.value_changed.emit(self.axis, float(value))

    def get_value(self) -> float:
        return self.spinbox.value()

    def set_value(self, value: float):
        self.spinbox.setValue(int(value))
        self.slider.setValue(int(value * 10))


class JointEditor(QWidget):
    """Editor for a single joint's pose."""

    pose_changed = Signal(str, JointPose)
    editor_closed = Signal(str)  # Signal emitted when editor is closed

    def __init__(self, joint_name: str, pose_manager: PoseManager):
        super().__init__()
        self.joint_name = joint_name
        self.pose_manager = pose_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # Joint name header with close button
        header_layout = QHBoxLayout()

        header = QLabel(self.joint_name)
        header.setFont(QFont("Arial", 10, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(header)

        # Close button for this joint editor
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """
        )
        close_btn.clicked.connect(self.close_joint_editor)
        header_layout.addWidget(close_btn)

        layout.addLayout(header_layout)

        # Pose sliders
        self.h_slider = PoseSlider("H", -180, 180)
        self.p_slider = PoseSlider("P", -180, 180)
        self.r_slider = PoseSlider("R", -180, 180)

        layout.addWidget(self.h_slider)
        layout.addWidget(self.p_slider)
        layout.addWidget(self.r_slider)

        # Connect signals
        self.h_slider.value_changed.connect(self._on_h_changed)
        self.p_slider.value_changed.connect(self._on_p_changed)
        self.r_slider.value_changed.connect(self._on_r_changed)

        # Reset button
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_pose)
        layout.addWidget(reset_btn)

        # Load current pose (without triggering signals)
        self._load_pose_silently()

    def _on_h_changed(self, axis: str, value: float):
        self._update_pose()

    def _on_p_changed(self, axis: str, value: float):
        self._update_pose()

    def _on_r_changed(self, axis: str, value: float):
        self._update_pose()

    def _update_pose(self):
        pose = JointPose(
            self.joint_name,
            self.h_slider.get_value(),
            self.p_slider.get_value(),
            self.r_slider.get_value(),
        )
        self.pose_manager.set_pose(self.joint_name, pose)
        self.pose_changed.emit(self.joint_name, pose)

    def _load_pose_silently(self):
        """Load current pose from pose manager without triggering signals."""
        pose = self.pose_manager.get_pose(self.joint_name)
        if pose:
            # Temporarily disconnect signals to prevent infinite loop
            try:
                self.h_slider.value_changed.disconnect()
                self.p_slider.value_changed.disconnect()
                self.r_slider.value_changed.disconnect()
            except:
                pass

            self.h_slider.set_value(pose.heading)
            self.p_slider.set_value(pose.pitch)
            self.r_slider.set_value(pose.roll)

            # Reconnect signals
            try:
                self.h_slider.value_changed.connect(self._on_h_changed)
                self.p_slider.value_changed.connect(self._on_p_changed)
                self.r_slider.value_changed.connect(self._on_r_changed)
            except:
                pass

    def load_current_pose(self):
        """Load current pose from pose manager."""
        pose = self.pose_manager.get_pose(self.joint_name)
        if pose:
            self.h_slider.set_value(pose.heading)
            self.p_slider.set_value(pose.pitch)
            self.r_slider.set_value(pose.roll)

    def reset_pose(self):
        """Reset this joint to neutral pose."""
        neutral_pose = self.pose_manager._neutral_pose.get(self.joint_name)
        if neutral_pose:
            self.h_slider.set_value(neutral_pose.heading)
            self.p_slider.set_value(neutral_pose.pitch)
            self.r_slider.set_value(neutral_pose.roll)
            self._update_pose()

    def close_joint_editor(self):
        """Close this joint editor."""
        # Emit signal to notify parent
        self.editor_closed.emit(self.joint_name)
        self.setParent(None)
        self.deleteLater()


class SignLanguagePoseEditor(QWidget):
    """Main sign language pose editor following sign.mt architecture."""

    def __init__(self, animate_panel=None, parent=None):
        super().__init__(parent)
        self.animate_panel = animate_panel
        self.pose_manager = PoseManager()
        self.joint_editors: Dict[str, JointEditor] = {}
        self._available_joints_cache = []  # Cache for available joints

        # Set window properties for proper cleanup
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)

        self.setup_ui()
        self.setup_connections()

        # Connect to parent's close event if parent exists
        if parent:
            parent.destroyed.connect(self.close)

    def closeEvent(self, event):
        """Handle window close event."""
        print("HPR Editor closing...")
        # Clean up any resources if needed
        self.joint_editors.clear()
        self._available_joints_cache.clear()
        event.accept()

    def setup_ui(self) -> None:
        self.setWindowTitle("Sign Language Pose Editor - sign.mt Style")
        self.setMinimumSize(1000, 800)
        self.resize(1000, 800)

        layout = QVBoxLayout(self)

        # Header with close button
        header_layout = QHBoxLayout()

        header = QLabel("Sign Language Pose Editor")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(header)

        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """
        )
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)

        layout.addLayout(header_layout)

        # Instructions
        instructions = QLabel(
            "Real-time 3D character pose management for sign language applications.\n"
            "H=Heading (left/right), P=Pitch (forward/back), R=Roll (side tilt)"
        )
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left panel - Joint editors
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel - Controls and info
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setSizes([600, 400])

    def create_left_panel(self) -> QWidget:
        """Create the left panel with joint editors."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Joint selection
        joint_group = QGroupBox("Joint Selection")
        joint_layout = QHBoxLayout(joint_group)

        self.joint_combo = QComboBox()

        # Add all joints that are available in the neutral pose
        joint_list = [
            "mixamorig:Hips",
            "mixamorig:Spine",
            "mixamorig:Spine1",
            "mixamorig:Spine2",
            "mixamorig:Spine3",
            "mixamorig:Neck",
            "mixamorig:Head",
            "mixamorig:RightShoulder",
            "mixamorig:LeftShoulder",
            "mixamorig:RightArm",
            "mixamorig:LeftArm",
            "mixamorig:RightForeArm",
            "mixamorig:LeftForeArm",
            "mixamorig:RightHand",
            "mixamorig:LeftHand",
            # Right Hand Fingers
            "mixamorig:RightHandIndex1",
            "mixamorig:RightHandIndex2",
            "mixamorig:RightHandIndex3",
            "mixamorig:RightHandIndex4",
            "mixamorig:RightHandMiddle1",
            "mixamorig:RightHandMiddle2",
            "mixamorig:RightHandMiddle3",
            "mixamorig:RightHandMiddle4",
            "mixamorig:RightHandRing1",
            "mixamorig:RightHandRing2",
            "mixamorig:RightHandRing3",
            "mixamorig:RightHandRing4",
            "mixamorig:RightHandPinky1",
            "mixamorig:RightHandPinky2",
            "mixamorig:RightHandPinky3",
            "mixamorig:RightHandPinky4",
            "mixamorig:RightHandThumb1",
            "mixamorig:RightHandThumb2",
            "mixamorig:RightHandThumb3",
            "mixamorig:RightHandThumb4",
            # Left Hand Fingers
            "mixamorig:LeftHandIndex1",
            "mixamorig:LeftHandIndex2",
            "mixamorig:LeftHandIndex3",
            "mixamorig:LeftHandIndex4",
            "mixamorig:LeftHandMiddle1",
            "mixamorig:LeftHandMiddle2",
            "mixamorig:LeftHandMiddle3",
            "mixamorig:LeftHandMiddle4",
            "mixamorig:LeftHandRing1",
            "mixamorig:LeftHandRing2",
            "mixamorig:LeftHandRing3",
            "mixamorig:LeftHandRing4",
            "mixamorig:LeftHandPinky1",
            "mixamorig:LeftHandPinky2",
            "mixamorig:LeftHandPinky3",
            "mixamorig:LeftHandPinky4",
            "mixamorig:LeftHandThumb1",
            "mixamorig:LeftHandThumb2",
            "mixamorig:LeftHandThumb3",
            "mixamorig:LeftHandThumb4",
            # Legs
            "mixamorig:RightUpLeg",
            "mixamorig:LeftUpLeg",
            "mixamorig:RightLeg",
            "mixamorig:LeftLeg",
            "mixamorig:RightFoot",
            "mixamorig:LeftFoot",
            "mixamorig:RightToeBase",
            "mixamorig:LeftToeBase",
        ]
        # Add joints to combo box immediately
        self.joint_combo.addItems(joint_list)
        # Set default selection to first item
        if joint_list:
            self.joint_combo.setCurrentIndex(0)
        # Connect the signal as fallback (will be reconnected with valid joints)
        self.joint_combo.currentTextChanged.connect(self.on_joint_selected)

        joint_layout.addWidget(QLabel("Joint:"))
        joint_layout.addWidget(self.joint_combo)
        layout.addWidget(joint_group)

        # Color testing section
        color_group = QGroupBox("Color Testing for Visibility")
        color_layout = QVBoxLayout(color_group)

        # Color selection dropdown
        self.color_combo = QComboBox()
        color_list = [
            "Default (Light Brown)",
            "Enhanced Visibility",
            "High Contrast Blue",
            "High Contrast Green",
            "High Contrast Red",
            "High Contrast Yellow",
            "High Contrast Orange",
            "High Contrast Purple",
            "High Contrast Cyan",
            "High Contrast Magenta",
            "Blue",
            "Green",
            "Red",
            "Yellow",
            "Purple",
            "Orange",
            "White",
            "Black",
        ]
        self.color_combo.addItems(color_list)
        self.color_combo.currentTextChanged.connect(self.change_character_color)

        color_layout.addWidget(QLabel("Character Color:"))
        color_layout.addWidget(self.color_combo)

        # Quick test button
        test_color_btn = QPushButton("Cycle High Contrast Colors")
        test_color_btn.clicked.connect(self.cycle_high_contrast_colors)
        color_layout.addWidget(test_color_btn)

        # Joint highlighting buttons
        highlight_all_btn = QPushButton("Highlight Joints in Black")
        highlight_all_btn.clicked.connect(self.highlight_joints_with_colors)
        color_layout.addWidget(highlight_all_btn)

        # Simple test button
        simple_test_btn = QPushButton("Test Color Change")
        simple_test_btn.clicked.connect(self.test_simple_color_change)
        color_layout.addWidget(simple_test_btn)

        # Debug joints button
        debug_joints_btn = QPushButton("Debug Available Joints")
        debug_joints_btn.clicked.connect(self.debug_available_joints)
        color_layout.addWidget(debug_joints_btn)

        # Debug all joints in model button
        debug_all_joints_btn = QPushButton("Debug All Joints in Model")
        debug_all_joints_btn.clicked.connect(self.debug_all_joints_in_model_ui)
        color_layout.addWidget(debug_all_joints_btn)

        highlight_hands_btn = QPushButton("Highlight Hands Only")
        highlight_hands_btn.clicked.connect(self.highlight_hands_only)
        color_layout.addWidget(highlight_hands_btn)

        # Alternative visibility approaches
        enhance_lighting_btn = QPushButton("Enhance Lighting")
        enhance_lighting_btn.clicked.connect(self.enhance_lighting_for_hands)
        color_layout.addWidget(enhance_lighting_btn)

        wireframe_btn = QPushButton("Toggle Wireframe")
        wireframe_btn.clicked.connect(self.toggle_wireframe_mode)
        color_layout.addWidget(wireframe_btn)

        outline_btn = QPushButton("Add Hand Outlines")
        outline_btn.clicked.connect(self.add_hand_outlines)
        color_layout.addWidget(outline_btn)

        remove_highlight_btn = QPushButton("Reset All Effects")
        remove_highlight_btn.clicked.connect(self.reset_all_visibility_effects)
        color_layout.addWidget(remove_highlight_btn)

        layout.addWidget(color_group)

        # Joint editors container
        scroll_area = QScrollArea()
        self.joint_editors_container = QWidget()
        self.joint_editors_layout = QVBoxLayout(self.joint_editors_container)
        scroll_area.setWidget(self.joint_editors_container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(500)
        layout.addWidget(scroll_area)

        return panel

    def create_right_panel(self) -> QWidget:
        """Create the right panel with controls and info."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Pose controls
        controls_group = QGroupBox("Pose Controls")
        controls_layout = QVBoxLayout(controls_group)

        # Quick actions
        actions_layout = QHBoxLayout()

        self.reset_all_btn = QPushButton("Reset All")
        self.reset_all_btn.clicked.connect(self.reset_all_poses)
        actions_layout.addWidget(self.reset_all_btn)

        self.apply_btn = QPushButton("Apply to Character")
        self.apply_btn.clicked.connect(self.apply_to_character)
        actions_layout.addWidget(self.apply_btn)

        controls_layout.addLayout(actions_layout)

        # Export/Import
        export_layout = QHBoxLayout()

        self.export_btn = QPushButton("Export Poses")
        self.export_btn.clicked.connect(self.export_poses)
        export_layout.addWidget(self.export_btn)

        self.import_btn = QPushButton("Import Poses")
        self.import_btn.clicked.connect(self.import_poses)
        export_layout.addWidget(self.import_btn)

        controls_layout.addLayout(export_layout)

        # Pose Validation Section
        validation_group = QGroupBox("Pose Validation")
        validation_layout = QVBoxLayout(validation_group)

        # Language and letter selection for validation
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["ASL", "BSL", "ISL", "Auslan", "LSF", "DGS"])
        self.lang_combo.setCurrentText("ASL")
        lang_layout.addWidget(self.lang_combo)

        lang_layout.addWidget(QLabel("Letter:"))
        self.letter_combo = QComboBox()
        # Add alphabet letters
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            self.letter_combo.addItem(letter)
        self.letter_combo.setCurrentText("A")
        lang_layout.addWidget(self.letter_combo)

        validation_layout.addLayout(lang_layout)

        # Validation buttons
        validation_btn_layout = QHBoxLayout()

        self.validate_pose_btn = QPushButton("Validate Current Pose")
        self.validate_pose_btn.clicked.connect(self.validate_current_pose)
        validation_btn_layout.addWidget(self.validate_pose_btn)

        self.load_reference_btn = QPushButton("Load Reference")
        self.load_reference_btn.clicked.connect(self.load_reference_pose)
        validation_btn_layout.addWidget(self.load_reference_btn)

        validation_layout.addLayout(validation_btn_layout)

        # Validation results
        self.validation_results = QTextEdit()
        self.validation_results.setMaximumHeight(150)
        self.validation_results.setPlaceholderText(
            "Validation results will appear here..."
        )
        validation_layout.addWidget(self.validation_results)

        # Add groups to layout
        controls_layout.addLayout(export_layout)


        layout.addWidget(controls_group)
        layout.addWidget(validation_group)

        # Pose information
        info_group = QGroupBox("Pose Information")
        info_layout = QVBoxLayout(info_group)

        self.pose_display = QTextEdit()
        self.pose_display.setMaximumHeight(300)
        self.pose_display.setReadOnly(True)
        info_layout.addWidget(self.pose_display)

        layout.addWidget(info_group)

        # Character color (if needed)
        color_group = QGroupBox("Character Appearance")
        color_layout = QHBoxLayout(color_group)

        color_layout.addWidget(QLabel("Color:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(
            [
                "Default (Light Brown)",
                "Blue",
                "Green",
                "Red",
                "Yellow",
                "Purple",
                "Orange",
                "White",
                "Black",
            ]
        )
        self.color_combo.currentTextChanged.connect(self.change_character_color)
        color_layout.addWidget(self.color_combo)

        layout.addWidget(color_group)

        # Spacer
        layout.addStretch()

        return panel

    def setup_connections(self):
        """Setup signal connections."""
        self.pose_manager.pose_changed.connect(self.on_pose_changed)
        self.pose_manager.pose_reset.connect(self.on_pose_reset)

    def showEvent(self, event):
        """Handle show event - capture current character pose when editor opens."""
        super().showEvent(event)
        # Always refresh the joint list when opening to ensure we get all available joints
        self._available_joints_cache.clear()  # Clear cache to force refresh
        self.update_joint_combo_box()  # Update combo box with available joints first
        self.load_current_character_values()  # Capture current pose instead of loading zeros
        self.update_pose_display()

    def load_current_character_values(self):
        """Load natural pose values into the pose manager."""
        try:
            # Load the natural pose values from the pose manager
            print("DEBUG: Loading natural pose values into HPR editor")

            # First, clear any existing pose/animation on the character
            if (
                self.animate_panel
                and hasattr(self.animate_panel, "_actor")
                and self.animate_panel._actor
            ):
                print("DEBUG: Clearing existing pose/animation on character")
                try:
                    # Stop any active animations
                    self.animate_panel._actor.stop()
                    # Don't apply T-pose animation - we'll create hands-down pose via individual joints
                    self.animate_panel._actor.update()
                    print(
                        "DEBUG: Cleared animations, will create hands-down pose via individual joints"
                    )
                except Exception as e:
                    print(f"DEBUG: Error clearing/applying pose: {e}")

            # Get the natural pose values from the pose manager
            natural_poses = self.pose_manager.get_all_poses()
            print(f"DEBUG: Loaded {len(natural_poses)} natural pose values")

            # Debug: Print some sample values
            for joint_name, pose in list(natural_poses.items())[:3]:
                print(
                    f"DEBUG: {joint_name}: H={pose.heading}, P={pose.pitch}, R={pose.roll}"
                )

            # Auto-populate joints list with natural pose joints
            available_joints = list(natural_poses.keys())
            self.auto_populate_joints_list(available_joints)

            # Update existing joint editors to show the natural pose values
            # Temporarily disconnect signals to prevent infinite loop
            for joint_name, editor in self.joint_editors.items():
                try:
                    # Disconnect the pose_changed signal temporarily
                    editor.pose_changed.disconnect()
                    editor.load_current_pose()
                    # Reconnect the signal
                    editor.pose_changed.connect(self.on_pose_changed)
                    print(
                        f"DEBUG: Updated editor for {joint_name} with natural pose values"
                    )
                except Exception as e:
                    print(f"DEBUG: Error updating editor for {joint_name}: {e}")
                    # Make sure to reconnect even if there's an error
                    try:
                        editor.pose_changed.connect(self.on_pose_changed)
                    except:
                        pass

            # Apply all the pose values to the character
            self.apply_all_poses_to_character()

            # Update the pose display
            self.update_pose_display()

            print(
                f"Successfully loaded natural pose values for {len(natural_poses)} joints"
            )

        except Exception as e:
            print(f"Error loading natural pose values: {e}")
            import traceback

            traceback.print_exc()

    def auto_populate_joints_list(self, available_joints):
        """Automatically populate the joints list with captured joints."""
        try:
            print(f"Auto-populating joints list with {len(available_joints)} joints")

            # Create joint editors for all captured joints
            for joint_name in available_joints:
                if joint_name not in self.joint_editors:
                    print(f"Creating editor for captured joint: {joint_name}")
                    editor = JointEditor(joint_name, self.pose_manager)
                    self.joint_editors[joint_name] = editor
                    self.joint_editors_layout.addWidget(editor)
                    editor.pose_changed.connect(self.on_pose_changed)
                    editor.editor_closed.connect(self.on_joint_editor_closed)
                    print(f"Created editor for {joint_name}")
                else:
                    print(f"Editor already exists for {joint_name}")

            print(f"Joints list populated with {len(self.joint_editors)} joint editors")

        except Exception as e:
            print(f"Error auto-populating joints list: {e}")

    def load_current_pose_from_service(self):
        """Load the current pose from pose_data_service into the pose manager."""
        try:
            # Import and get the pose from pose_data_service
            from ...utils.pose_data_service import PoseDataService

            pose_service = PoseDataService()
            current_pose_data = pose_service.get_neutral_pose()

            # Temporarily disconnect pose_changed signal to prevent applying to character
            self.pose_manager.pose_changed.disconnect()

            # Convert the pose data to JointPose objects
            for joint_name, hpr_values in current_pose_data.joints.items():
                if len(hpr_values) >= 3:
                    h, p, r = hpr_values[0], hpr_values[1], hpr_values[2]
                    joint_pose = JointPose(joint_name, h, p, r)
                    self.pose_manager.set_pose(joint_name, joint_pose)

            # Reconnect the signal
            self.pose_manager.pose_changed.connect(self.on_pose_changed)

            print(
                f"Loaded current pose from pose_data_service for {len(current_pose_data.joints)} joints"
            )

        except Exception as e:
            print(f"Error loading pose from service: {e}")
            # Make sure to reconnect signal even if there's an error
            try:
                self.pose_manager.pose_changed.connect(self.on_pose_changed)
            except:
                pass

    def capture_current_pose_as_neutral(self, actor, available_joints):
        """Capture the current character pose and use it as the neutral pose."""
        try:
            # Get current pose values from the character
            current_pose = {}
            for joint_name in available_joints:
                joint = actor.controlJoint(None, "modelRoot", joint_name)
                if joint is not None:
                    h, p, r = joint.getHpr()
                    current_pose[joint_name] = JointPose(joint_name, h, p, r)
                    print(f"Captured {joint_name}: H={h:.1f}° P={p:.1f}° R={r:.1f}°")

            # Update the pose manager with current values
            for joint_name, pose in current_pose.items():
                self.pose_manager.set_pose(joint_name, pose)

            print(f"Captured current pose for {len(current_pose)} joints")

        except Exception as e:
            print(f"Error capturing current pose: {e}")

    def get_available_joints(self, actor) -> list:
        """Get list of joints that are actually available in the character."""
        # Return cached result if available
        if self._available_joints_cache:
            return self._available_joints_cache

        available_joints = []
        failed_joints = []

        try:
            # First, run debug to see what joints are actually in the model
            all_model_joints = self.debug_all_joints_in_model(actor)

            # Test each joint in our neutral pose to see if it exists
            for joint_name in self.pose_manager._neutral_pose.keys():
                try:
                    joint = actor.controlJoint(None, "modelRoot", joint_name)
                    if joint is not None:
                        available_joints.append(joint_name)
                        print(f"✓ Found joint: {joint_name}")
                    else:
                        failed_joints.append(f"{joint_name} (returned None)")
                        print(f"✗ Joint not found: {joint_name} (returned None)")
                except Exception as e:
                    # Track failed joints for debugging
                    failed_joints.append(f"{joint_name} (error: {str(e)[:50]})")
                    print(f"✗ Joint error: {joint_name} - {str(e)[:50]}")

            # If we found joints in the model that aren't in our neutral pose, add them
            for model_joint in all_model_joints:
                if model_joint not in available_joints and model_joint.startswith(
                    "mixamorig:"
                ):
                    # Try to add this joint to our pose manager
                    try:
                        joint = actor.controlJoint(None, "modelRoot", model_joint)
                        if joint is not None:
                            available_joints.append(model_joint)
                            # Add to pose manager if not already there
                            if model_joint not in self.pose_manager._poses:
                                self.pose_manager._poses[model_joint] = JointPose(
                                    model_joint, 0.0, 0.0, 0.0
                                )
                            print(f"✓ Added missing joint: {model_joint}")
                    except Exception as e:
                        print(f"✗ Could not add joint {model_joint}: {e}")

            # Cache the result
            self._available_joints_cache = available_joints
            print(f"Detected {len(available_joints)} available joints")
            print(f"Available joints: {available_joints}")
            print(f"Failed joints ({len(failed_joints)}): {failed_joints}")
            return available_joints

        except Exception as e:
            print(f"Error getting available joints: {e}")
            return []

    def refresh_joint_list(self):
        """Force refresh the joint list by clearing cache."""
        print("Refreshing joint list...")
        self._available_joints_cache.clear()
        self.update_joint_combo_box()

    def debug_all_joints_in_model(self, actor):
        """Debug method to find all possible joints in the model using different approaches."""
        print("=== DEBUG: Finding all joints in model ===")

        all_found_joints = set()

        # Method 1: Try to find joints by searching the model hierarchy
        try:
            if (
                hasattr(self.animate_panel, "_model_np")
                and self.animate_panel._model_np
            ):
                model_np = self.animate_panel._model_np

                # Search for all nodes that might be joints
                all_nodes = model_np.findAllMatches("**")
                print(f"Found {all_nodes.getNumPaths()} total nodes in model")

                for i in range(all_nodes.getNumPaths()):
                    node = all_nodes.getPath(i)
                    node_name = node.getName()

                    # Look for nodes that might be joints
                    if any(
                        keyword in node_name.lower()
                        for keyword in ["joint", "bone", "mixamorig"]
                    ):
                        all_found_joints.add(node_name)
                        print(f"  Found potential joint: {node_name}")

        except Exception as e:
            print(f"Error in method 1: {e}")

        # Method 2: Try common joint name patterns
        try:
            common_joint_patterns = [
                "mixamorig:*",
                "**/mixamorig:*",
                "**/*Hand*",
                "**/*Arm*",
                "**/*Shoulder*",
                "**/*Head*",
                "**/*Neck*",
                "**/*Hip*",
                "**/*Leg*",
                "**/*Foot*",
            ]

            if (
                hasattr(self.animate_panel, "_model_np")
                and self.animate_panel._model_np
            ):
                model_np = self.animate_panel._model_np

                for pattern in common_joint_patterns:
                    try:
                        nodes = model_np.findAllMatches(pattern)
                        print(f"Pattern '{pattern}': {nodes.getNumPaths()} nodes")
                        for j in range(nodes.getNumPaths()):
                            node = nodes.getPath(j)
                            all_found_joints.add(node.getName())
                    except Exception as e:
                        print(f"Pattern '{pattern}' failed: {e}")

        except Exception as e:
            print(f"Error in method 2: {e}")

        # Method 3: Try to use actor.getJoints() if available
        try:
            if hasattr(actor, "getJoints"):
                joints = actor.getJoints()
                print(f"actor.getJoints() returned: {joints}")
                if joints:
                    for joint in joints:
                        all_found_joints.add(str(joint))
        except Exception as e:
            print(f"actor.getJoints() failed: {e}")

        print(f"=== Total unique joints found: {len(all_found_joints)} ===")
        for joint in sorted(all_found_joints):
            print(f"  - {joint}")

        return list(all_found_joints)

    def update_joint_combo_box(self):
        """Update the joint combo box to only show available joints."""
        if not self.animate_panel or not hasattr(self.animate_panel, "_actor"):
            return

        try:
            actor = self.animate_panel._actor
            if actor is None:
                return

            # Get available joints
            available_joints = self.get_available_joints(actor)

            # Clear and repopulate the combo box with valid joint names
            self.joint_combo.clear()
            valid_joints = [
                joint for joint in available_joints if joint and joint.strip()
            ]
            self.joint_combo.addItems(valid_joints)

            # Always connect the signal (disconnect first to avoid duplicates)
            try:
                self.joint_combo.currentTextChanged.disconnect()
            except:
                pass
            self.joint_combo.currentTextChanged.connect(self.on_joint_selected)

            print(f"Updated joint combo box with {len(valid_joints)} valid joints")

        except Exception as e:
            print(f"Error updating joint combo box: {e}")

    def on_joint_selected(self, joint_name: str):
        """Handle joint selection."""
        print(f"Joint selected: {joint_name}")

        # Validate joint name
        if not joint_name or joint_name.strip() == "":
            print("Invalid joint name, skipping")
            return

        if joint_name not in self.joint_editors:
            print(f"Creating editor for joint: {joint_name}")
            editor = JointEditor(joint_name, self.pose_manager)
            self.joint_editors[joint_name] = editor
            self.joint_editors_layout.addWidget(editor)
            editor.pose_changed.connect(self.on_pose_changed)
            editor.editor_closed.connect(self.on_joint_editor_closed)
            print(f"Created editor for {joint_name}")
        else:
            print(f"Editor already exists for {joint_name}")

    def on_joint_editor_closed(self, joint_name: str):
        """Handle joint editor being closed."""
        print(f"Joint editor closed for: {joint_name}")
        if joint_name in self.joint_editors:
            del self.joint_editors[joint_name]
            print(f"Removed {joint_name} from joint_editors dictionary")
        self.update_pose_display()

    def on_pose_changed(self, joint_name: str, pose: JointPose):
        """Handle pose changes."""
        # Only apply changes for available joints
        if joint_name in self._available_joints_cache:
            self.apply_pose_to_character(joint_name, pose)
        self.update_pose_display()

    def on_pose_reset(self):
        """Handle pose reset."""
        for editor in self.joint_editors.values():
            editor.load_current_pose()
        self.update_pose_display()

    def reset_all_poses(self):
        """Reset all poses to default natural pose."""
        print("DEBUG: Resetting all poses to default natural pose")
        
        try:
            # First, clear any existing pose/animation on the character
            if self.animate_panel and hasattr(self.animate_panel, "_actor") and self.animate_panel._actor:
                print("DEBUG: Clearing existing pose/animation on character")
                try:
                    # Stop any active animations
                    self.animate_panel._actor.stop()
                    # Don't apply T-pose animation - we'll create hands-down pose via individual joints
                    self.animate_panel._actor.update()
                    print("DEBUG: Cleared animations, will create hands-down pose via individual joints")
                except Exception as e:
                    print(f"DEBUG: Error clearing/applying pose: {e}")
            
            # Reset the pose manager to neutral pose - this is the key fix!
            self.pose_manager.reset_to_neutral()
            
            # Get the natural pose values from the pose manager
            natural_poses = self.pose_manager.get_all_poses()
            print(f"DEBUG: Loaded {len(natural_poses)} natural pose values")
            
            # Debug: Print some sample values
            for joint_name, pose in list(natural_poses.items())[:3]:
                print(f"DEBUG: {joint_name}: H={pose.heading}, P={pose.pitch}, R={pose.roll}")
            
            # Auto-populate joints list with natural pose joints
            available_joints = list(natural_poses.keys())
            self.auto_populate_joints_list(available_joints)

            # Update existing joint editors to show the natural pose values
            # Temporarily disconnect signals to prevent infinite loop
            for joint_name, editor in self.joint_editors.items():
                try:
                    # Disconnect the pose_changed signal temporarily
                    editor.pose_changed.disconnect()
                    editor.load_current_pose()
                    # Reconnect the signal
                    editor.pose_changed.connect(self.on_pose_changed)
                    print(f"DEBUG: Updated editor for {joint_name} with natural pose values")
                except Exception as e:
                    print(f"DEBUG: Error updating editor for {joint_name}: {e}")
                    # Make sure to reconnect even if there's an error
                    try:
                        editor.pose_changed.connect(self.on_pose_changed)
                    except:
                        pass

            # Apply all the pose values to the character
            self.apply_all_poses_to_character()

            # Update the pose display
            self.update_pose_display()

            print(f"Successfully reset to natural pose values for {len(natural_poses)} joints")

        except Exception as e:
            print(f"Error resetting to natural pose: {e}")
            import traceback
            traceback.print_exc()

    def apply_to_character(self):
        """Apply all poses to the character."""
        poses = self.pose_manager.get_all_poses()
        print(f"Applying {len(poses)} poses to character")
        # Apply all poses regardless of cache status
        for joint_name, pose in poses.items():
            self.apply_pose_to_character(joint_name, pose)

    def apply_pose_to_character(self, joint_name: str, pose: JointPose):
        """Apply a single pose to the character."""
        if not self.animate_panel or not hasattr(self.animate_panel, "_actor"):
            print(f"No animate panel or actor available for {joint_name}")
            return

        try:
            actor = self.animate_panel._actor
            if actor is None:
                print(f"No actor available for {joint_name}")
                return

            # Try to apply the pose regardless of cache status
            joint = actor.controlJoint(None, "modelRoot", joint_name)
            if joint is not None:
                joint.setHpr(pose.heading, pose.pitch, pose.roll)
                actor.update()
                print(
                    f"Applied pose to {joint_name}: H={pose.heading}° P={pose.pitch}° R={pose.roll}°"
                )

                # Debug: Check what the joint's actual values are after setting
                actual_h, actual_p, actual_r = joint.getHpr()
                print(
                    f"DEBUG: After setting {joint_name}, actual values are: H={actual_h:.1f}° P={actual_p:.1f}° R={actual_r:.1f}°"
                )
            else:
                print(f"Joint {joint_name} not found on actor")

        except Exception as e:
            print(f"Error applying pose to {joint_name}: {e}")

    def apply_all_poses_to_character(self):
        """Apply all pose values from the pose manager to the character."""
        if not self.animate_panel or not hasattr(self.animate_panel, "_actor"):
            print("No animate panel or actor available for applying poses")
            return

        try:
            actor = self.animate_panel._actor
            if actor is None:
                print("No actor available for applying poses")
                return

            print(
                "DEBUG: Applying all pose values to character to create hands-down pose"
            )

            # Get all poses from the pose manager
            all_poses = self.pose_manager.get_all_poses()

            # Apply each pose to the character
            for joint_name, pose in all_poses.items():
                try:
                    joint = actor.controlJoint(None, "modelRoot", joint_name)
                    if joint is not None:
                        joint.setHpr(pose.heading, pose.pitch, pose.roll)
                        print(
                            f"DEBUG: Applied {joint_name}: H={pose.heading}° P={pose.pitch}° R={pose.roll}°"
                        )
                    else:
                        print(f"DEBUG: Joint {joint_name} not found on actor")
                except Exception as e:
                    print(f"DEBUG: Error applying pose to {joint_name}: {e}")

            # Update the actor to reflect all changes
            actor.update()
            print("DEBUG: Successfully applied all pose values to character")

        except Exception as e:
            print(f"Error applying all poses to character: {e}")

    def update_pose_display(self):
        """Update the pose information display."""
        poses = self.pose_manager.get_all_poses()
        text = "Current Poses:\n\n"

        # Get available joints from cache
        available_joints = self._available_joints_cache

        # Show only joints that have editors (are being actively edited)
        active_joints = list(self.joint_editors.keys())

        if active_joints:
            # Show active joints first
            text += "=== Active Joint Editors ===\n\n"
            for joint_name in active_joints:
                if joint_name in poses:
                    pose = poses[joint_name]
                    text += f"{joint_name}:\n"
                    text += f"  H: {pose.heading:6.1f}°\n"
                    text += f"  P: {pose.pitch:6.1f}°\n"
                    text += f"  R: {pose.roll:6.1f}°\n\n"

        # Show only available joints
        text += f"=== Available Joints ({len(available_joints)}) ===\n\n"
        for joint_name, pose in poses.items():
            if joint_name in available_joints:
                text += f"{joint_name}:\n"
                text += f"  H: {pose.heading:6.1f}°\n"
                text += f"  P: {pose.pitch:6.1f}°\n"
                text += f"  R: {pose.roll:6.1f}°\n\n"

        self.pose_display.setText(text)

    def validate_current_pose(self):
        """Validate the current pose against the reference pose for the selected language and letter."""
        try:
            language = self.lang_combo.currentText()
            letter = self.letter_combo.currentText()

            # Get current pose from the pose manager
            current_poses = self.pose_manager.get_all_poses()

            # Load reference pose data
            reference_poses = self._load_reference_pose_data(language, letter)

            if not reference_poses:
                self.validation_results.setText(
                    f"No reference pose found for {language} {letter}"
                )
                return

            # Compare poses
            results = []
            results.append(f"=== Pose Validation: {language} {letter} ===\n")

            total_error = 0
            joint_count = 0

            for joint_name, reference_pose in reference_poses.items():
                if joint_name in current_poses:
                    current_pose = current_poses[joint_name]

                    # Calculate differences
                    h_diff = abs(current_pose.heading - reference_pose[0])
                    p_diff = abs(current_pose.pitch - reference_pose[1])
                    r_diff = abs(current_pose.roll - reference_pose[2])

                    joint_error = (h_diff + p_diff + r_diff) / 3
                    total_error += joint_error
                    joint_count += 1

                    if joint_error > 5:  # Threshold for significant difference
                        results.append(f"❌ {joint_name}: Error {joint_error:.1f}°")
                        results.append(
                            f"   Current: H={current_pose.heading:.1f}° P={current_pose.pitch:.1f}° R={current_pose.roll:.1f}°"
                        )
                        results.append(
                            f"   Reference: H={reference_pose[0]:.1f}° P={reference_pose[1]:.1f}° R={reference_pose[2]:.1f}°"
                        )
                    else:
                        results.append(
                            f"✅ {joint_name}: Good ({joint_error:.1f}° error)"
                        )

            if joint_count > 0:
                avg_error = total_error / joint_count
                results.append(f"\n=== Summary ===")
                results.append(f"Average Error: {avg_error:.1f}°")
                if avg_error < 5:
                    results.append("🎉 Pose is very close to reference!")
                elif avg_error < 10:
                    results.append("👍 Pose is reasonably close to reference")
                else:
                    results.append("⚠️ Pose needs adjustment")

            self.validation_results.setText("\n".join(results))

            # Apply current poses to character so user can see the current state
            self.apply_to_character()

        except Exception as e:
            self.validation_results.setText(f"Error during validation: {str(e)}")

    def load_reference_pose(self):
        """Load the reference pose for the selected language and letter."""
        try:
            language = self.lang_combo.currentText()
            letter = self.letter_combo.currentText()

            reference_poses = self._load_reference_pose_data(language, letter)

            if not reference_poses:
                self.validation_results.setText(
                    f"No reference pose found for {language} {letter}"
                )
                return

            # Apply reference poses to the pose manager
            for joint_name, pose_data in reference_poses.items():
                if len(pose_data) >= 3:
                    pose = JointPose(
                        joint_name=joint_name,
                        heading=pose_data[0],
                        pitch=pose_data[1],
                        roll=pose_data[2],
                    )
                    self.pose_manager.set_pose(joint_name, pose)

            # Update existing joint editors to reflect the new pose data
            for joint_name, editor in self.joint_editors.items():
                editor.load_current_pose()
            self.update_pose_display()

            # Apply to character
            self.apply_to_character()

            self.validation_results.setText(
                f"Loaded reference pose for {language} {letter}"
            )

        except Exception as e:
            self.validation_results.setText(f"Error loading reference pose: {str(e)}")

    def _load_reference_pose_data(
        self, language: str, letter: str
    ) -> Dict[str, List[float]]:
        """Load reference pose data from the sign language files."""
        try:
            import os
            from pathlib import Path

            # Map language names to file names
            lang_map = {
                "ASL": "asl_right_hand.json",
                "BSL": "bsl_right_hand.json",
                "ISL": "isl_right_hand.json",
                "Auslan": "auslan_right_hand.json",
                "LSF": "lsf_right_hand.json",
                "DGS": "dgs_right_hand.json",
            }

            filename = lang_map.get(language, "asl_right_hand.json")

            # Try to find the file
            possible_paths = [
                Path("resources/data/signs") / language.lower() / filename,
                Path("resources/data/signs/asl/asl_right_hand.json"),  # Fallback to ASL
            ]

            for path in possible_paths:
                if path.exists():
                    with open(path, "r") as f:
                        data = json.load(f)

                    if "alphabet" in data and letter in data["alphabet"]:
                        letter_data = data["alphabet"][letter]
                        if "pose" in letter_data:
                            return letter_data["pose"]

            return {}

        except Exception as e:
            print(f"Error loading reference pose data: {e}")
            return {}

    def export_poses(self):
        """Export poses to clipboard."""
        poses_json = self.pose_manager.export_poses()
        QApplication.clipboard().setText(poses_json)
        print("Poses exported to clipboard")

    def import_poses(self):
        """Import poses from clipboard."""
        clipboard_text = QApplication.clipboard().text()
        if clipboard_text:
            self.pose_manager.import_poses(clipboard_text)
            self.on_pose_reset()
            print("Poses imported from clipboard")

    def change_character_color(self, color_name: str):
        """Change character color."""
        if not self.animate_panel or not hasattr(self.animate_panel, "_model_np"):
            return

        try:
            color_map = {
                "Default (Light Brown)": VBase4(0.8, 0.6, 0.4, 1.0),
                "Enhanced Visibility": VBase4(
                    0.9, 0.7, 0.5, 1.0
                ),  # Brighter for better hand visibility
                "High Contrast Blue": VBase4(
                    0.1, 0.3, 0.9, 1.0
                ),  # Deep blue for maximum contrast
                "High Contrast Green": VBase4(
                    0.1, 0.7, 0.2, 1.0
                ),  # Bright green for visibility
                "High Contrast Red": VBase4(
                    0.9, 0.1, 0.1, 1.0
                ),  # Bright red for maximum visibility
                "High Contrast Yellow": VBase4(
                    1.0, 1.0, 0.0, 1.0
                ),  # Pure yellow for high contrast
                "High Contrast Orange": VBase4(
                    1.0, 0.4, 0.0, 1.0
                ),  # Bright orange for visibility
                "High Contrast Purple": VBase4(
                    0.7, 0.1, 0.9, 1.0
                ),  # Bright purple for contrast
                "High Contrast Cyan": VBase4(
                    0.0, 0.9, 0.9, 1.0
                ),  # Bright cyan for visibility
                "High Contrast Magenta": VBase4(
                    0.9, 0.0, 0.9, 1.0
                ),  # Bright magenta for contrast
                "Blue": VBase4(0.2, 0.4, 0.8, 1.0),
                "Green": VBase4(0.2, 0.8, 0.4, 1.0),
                "Red": VBase4(0.8, 0.2, 0.2, 1.0),
                "Yellow": VBase4(0.9, 0.9, 0.2, 1.0),
                "Purple": VBase4(0.6, 0.2, 0.8, 1.0),
                "Orange": VBase4(0.9, 0.5, 0.2, 1.0),
                "White": VBase4(1.0, 1.0, 1.0, 1.0),
                "Black": VBase4(0.1, 0.1, 0.1, 1.0),
            }

            if color_name in color_map:
                model_np = self.animate_panel._model_np
                if model_np is not None:
                    model_np.setColor(color_map[color_name])
                    print(f"Changed character color to: {color_name}")

        except Exception as e:
            print(f"Error changing character color: {e}")

    def cycle_high_contrast_colors(self):
        """Cycle through high contrast colors for testing visibility."""
        high_contrast_colors = [
            "High Contrast Blue",
            "High Contrast Green",
            "High Contrast Red",
            "High Contrast Yellow",
            "High Contrast Orange",
            "High Contrast Purple",
            "High Contrast Cyan",
            "High Contrast Magenta",
        ]

        # Get current color or start with first
        current_color = getattr(self, "_current_test_color", 0)

        # Cycle to next color
        next_color = (current_color + 1) % len(high_contrast_colors)
        self._current_test_color = next_color

        # Apply the color
        color_name = high_contrast_colors[next_color]
        self.change_character_color(color_name)
        print(f"Testing color: {color_name}")

        return color_name

    def highlight_joints_with_colors(self):
        """Highlight only joint geometry, not the entire character."""
        if not self.animate_panel or not hasattr(self.animate_panel, "_model_np"):
            return

        try:
            from panda3d.core import VBase4

            model_np = self.animate_panel._model_np
            if model_np is None:
                print("No model found for highlighting")
                return

            print("=== Joint Highlighting (Targeted Approach) ===")

            # First, restore the character to its original color
            original_color = VBase4(0.1, 0.3, 0.9, 1.0)  # High contrast blue
            model_np.setColor(original_color)
            print("✓ Restored character to original blue color")

            # Try to find and highlight only joint-specific geometry
            self._highlight_joint_geometry_only(model_np)

            # Also create visible joint markers
            self._create_joint_markers(model_np)

        except Exception as e:
            print(f"Error highlighting joints: {e}")

    def _highlight_joint_geometry_only(self, model_np):
        """Highlight only joint geometry without affecting the main character."""
        try:
            from panda3d.core import VBase4

            black_color = VBase4(0.0, 0.0, 0.0, 1.0)  # Black

            print("=== Targeting Joint Geometry Only ===")

            # Method 1: Look for joint-specific geometry nodes
            joint_geometry_patterns = [
                "**/+GeomNode",
                "**/joint*",
                "**/*joint*",
                "**/Joint*",
                "**/*Joint*",
            ]

            total_highlighted = 0

            for pattern in joint_geometry_patterns:
                try:
                    nodes = model_np.findAllMatches(pattern)
                    print(f"Pattern '{pattern}': Found {nodes.getNumPaths()} nodes")

                    for i in range(nodes.getNumPaths()):
                        node = nodes.getPath(i)
                        node_name = node.getName()

                        # Only color nodes that seem to be joint-related
                        if any(
                            keyword in node_name.lower()
                            for keyword in ["joint", "bone", "skeleton"]
                        ):
                            try:
                                node.setColor(black_color)
                                print(f"  ✓ Highlighted joint node: {node_name}")
                                total_highlighted += 1
                            except Exception as e:
                                print(f"  ✗ Could not color {node_name}: {e}")
                        else:
                            print(f"  - Skipped non-joint node: {node_name}")

                except Exception as e:
                    print(f"Pattern '{pattern}' failed: {e}")

            # Method 2: Try to find joint geometry by looking for small geometric objects
            print("\n=== Looking for Small Joint Geometry ===")
            try:
                # Find all geometry nodes and check their size
                geom_nodes = model_np.findAllMatches("**/+GeomNode")
                for i in range(geom_nodes.getNumPaths()):
                    geom_node = geom_nodes.getPath(i)
                    try:
                        # Get the bounding box to check if it's small (likely a joint)
                        bounds = geom_node.getBounds()
                        if bounds:
                            # Handle different bounding types
                            from panda3d.core import BoundingSphere, BoundingBox
                            if isinstance(bounds, BoundingSphere):
                                # For spheres, use radius * 2 as diameter
                                size = bounds.getRadius() * 2
                            elif isinstance(bounds, BoundingBox):
                                # For boxes, calculate size from min/max
                                min_pt = bounds.getMin()
                                max_pt = bounds.getMax()
                                size = max_pt - min_pt
                            else:
                                # Fallback: try getSize() if available
                                try:
                                    size = bounds.getSize()
                                except AttributeError:
                                    # If no getSize method, skip this geometry
                                    continue
                            
                            # Check if geometry is small (likely a joint)
                            if hasattr(size, 'length'):
                                # Vector size
                                if size.length() < 0.1:  # Small threshold
                                    geom_node.setColor(black_color)
                                    print(
                                        f"  ✓ Highlighted small geometry (likely joint): {geom_node.getName()}"
                                    )
                                    total_highlighted += 1
                            else:
                                # Scalar size (radius)
                                if size < 0.1:  # Small threshold
                                    geom_node.setColor(black_color)
                                    print(
                                        f"  ✓ Highlighted small geometry (likely joint): {geom_node.getName()}"
                                    )
                                    total_highlighted += 1
                    except Exception as e:
                        print(f"  ✗ Could not check size of {geom_node.getName()}: {e}")

            except Exception as e:
                print(f"Small geometry detection failed: {e}")

            # Method 3: Try to find joint geometry by looking for specific joint names in geometry
            print("\n=== Looking for Named Joint Geometry ===")
            joint_names = [
                "Head",
                "Neck",
                "Shoulder",
                "Arm",
                "ForeArm",
                "Hand",
                "Index",
                "Middle",
                "Ring",
                "Pinky",
                "Thumb",
                "Hip",
                "Leg",
                "Foot",
            ]

            for joint_name in joint_names:
                try:
                    # Look for geometry nodes with joint names
                    joint_geoms = model_np.findAllMatches(f"**/*{joint_name}*+GeomNode")
                    for j in range(joint_geoms.getNumPaths()):
                        joint_geom = joint_geoms.getPath(j)
                        try:
                            joint_geom.setColor(black_color)
                            print(
                                f"  ✓ Highlighted {joint_name} geometry: {joint_geom.getName()}"
                            )
                            total_highlighted += 1
                        except Exception as e:
                            print(f"  ✗ Could not color {joint_name} geometry: {e}")
                except Exception as e:
                    print(f"  ✗ Error finding {joint_name} geometry: {e}")

            print(
                f"\n=== Summary: Highlighted {total_highlighted} joint geometry nodes ==="
            )

        except Exception as e:
            print(f"Joint geometry highlighting failed: {e}")

    def _create_joint_markers(self, model_np):
        """Create visible joint markers at actual joint positions."""
        try:
            from panda3d.core import CardMaker, VBase4, Vec3

            print("=== Creating Joint Markers at Actual Joint Positions ===")

            # List of joint names to find in the model
            joint_names = [
                "mixamorig:Head",
                "mixamorig:Neck",
                "mixamorig:RightShoulder",
                "mixamorig:LeftShoulder",
                "mixamorig:RightArm",
                "mixamorig:LeftArm",
                "mixamorig:RightForeArm",
                "mixamorig:LeftForeArm",
                "mixamorig:RightHand",
                "mixamorig:LeftHand",
                # Right hand fingers
                "mixamorig:RightHandIndex1",
                "mixamorig:RightHandIndex2",
                "mixamorig:RightHandIndex3",
                "mixamorig:RightHandIndex4",
                "mixamorig:RightHandMiddle1",
                "mixamorig:RightHandMiddle2",
                "mixamorig:RightHandMiddle3",
                "mixamorig:RightHandMiddle4",
                "mixamorig:RightHandRing1",
                "mixamorig:RightHandRing2",
                "mixamorig:RightHandRing3",
                "mixamorig:RightHandRing4",
                "mixamorig:RightHandPinky1",
                "mixamorig:RightHandPinky2",
                "mixamorig:RightHandPinky3",
                "mixamorig:RightHandPinky4",
                "mixamorig:RightHandThumb1",
                "mixamorig:RightHandThumb2",
                "mixamorig:RightHandThumb3",
                "mixamorig:RightHandThumb4",
                # Left hand fingers
                "mixamorig:LeftHandIndex1",
                "mixamorig:LeftHandIndex2",
                "mixamorig:LeftHandIndex3",
                "mixamorig:LeftHandIndex4",
                "mixamorig:LeftHandMiddle1",
                "mixamorig:LeftHandMiddle2",
                "mixamorig:LeftHandMiddle3",
                "mixamorig:LeftHandMiddle4",
                "mixamorig:LeftHandRing1",
                "mixamorig:LeftHandRing2",
                "mixamorig:LeftHandRing3",
                "mixamorig:LeftHandRing4",
                "mixamorig:LeftHandPinky1",
                "mixamorig:LeftHandPinky2",
                "mixamorig:LeftHandPinky3",
                "mixamorig:LeftHandPinky4",
                "mixamorig:LeftHandThumb1",
                "mixamorig:LeftHandThumb2",
                "mixamorig:LeftHandThumb3",
                "mixamorig:LeftHandThumb4",
                # Legs
                "mixamorig:Hips",
                "mixamorig:RightUpLeg",
                "mixamorig:LeftUpLeg",
                "mixamorig:RightLeg",
                "mixamorig:LeftLeg",
                "mixamorig:RightFoot",
                "mixamorig:LeftFoot",
            ]

            # Create a card maker for joint markers
            card_maker = CardMaker("joint_marker")
            card_maker.setFrame(-0.03, 0.03, -0.03, 0.03)  # Smaller square

            markers_created = 0

            for joint_name in joint_names:
                try:
                    # Find the actual joint node in the model
                    joint_node = model_np.find(f"**/{joint_name}")
                    if joint_node and not joint_node.isEmpty():
                        # Get the actual world position of the joint
                        joint_pos = joint_node.getPos(model_np)

                        # Create a marker node at the joint position
                        marker_node = model_np.attachNewNode(
                            f"joint_marker_{joint_name}"
                        )
                        marker_node.setPos(joint_pos)

                        # Create the card geometry
                        card_node = marker_node.attachNewNode(card_maker.generate())
                        card_node.setColor(VBase4(0.0, 0.0, 0.0, 1.0))  # Black
                        card_node.setBillboardAxis()  # Always face the camera

                        # Make it slightly transparent
                        card_node.setTransparency(1)
                        card_node.setAlphaScale(0.9)

                        print(
                            f"  ✓ Created marker for {joint_name} at actual position {joint_pos}"
                        )
                        markers_created += 1
                    else:
                        print(f"  ✗ Could not find joint {joint_name}")

                except Exception as e:
                    print(f"  ✗ Could not create marker for {joint_name}: {e}")

            print(
                f"=== Created {markers_created} joint markers at actual joint positions ==="
            )

        except Exception as e:
            print(f"Joint marker creation failed: {e}")

    def test_simple_color_change(self):
        """Test if basic color changes work on the character"""
        try:
            if not self.animate_panel or not hasattr(self.animate_panel, "_model_np"):
                print("No model found for color test")
                return

            model_np = self.animate_panel._model_np
            if model_np is None:
                print("Model node path not available")
                return

            from panda3d.core import VBase4

            # Try to change the entire character to a bright color
            bright_red = VBase4(1.0, 0.0, 0.0, 1.0)  # Bright red
            model_np.setColor(bright_red)
            print("✓ Set entire character to bright red")

            # Also try to find and color all geometry nodes
            geom_nodes = model_np.findAllMatches("**/+GeomNode")
            print(f"Found {geom_nodes.getNumPaths()} geometry nodes")

            for i in range(geom_nodes.getNumPaths()):
                geom_node = geom_nodes.getPath(i)
                try:
                    geom_node.setColor(bright_red)
                    print(f"✓ Colored geometry node {i} bright red")
                except Exception as e:
                    print(f"✗ Could not color geometry node {i}: {e}")

            print("Simple color change test completed")

        except Exception as e:
            print(f"Error in simple color test: {e}")

    def debug_available_joints(self):
        """Debug method to show all available joints in the model."""
        try:
            if not self.animate_panel or not hasattr(self.animate_panel, "_model_np"):
                print("No model found for joint debugging")
                return

            model_np = self.animate_panel._model_np
            if model_np is None:
                print("Model node path not available")
                return

            print("=== DEBUG: Available Joints in Model ===")

            # Find all nodes that might be joints
            all_nodes = model_np.findAllMatches("**")
            joint_nodes = []

            for i in range(all_nodes.getNumPaths()):
                node = all_nodes.getPath(i)
                node_name = node.getName()

                # Look for nodes that might be joints
                if any(
                    keyword in node_name.lower()
                    for keyword in ["joint", "bone", "mixamorig"]
                ):
                    joint_nodes.append((node_name, node.getPos(model_np)))

            print(f"Found {len(joint_nodes)} potential joint nodes:")
            for joint_name, position in joint_nodes:
                print(f"  - {joint_name}: {position}")

            # Also try to find nodes by common joint patterns
            print("\n=== Looking for specific joint patterns ===")
            patterns = [
                "**/mixamorig:*",
                "**/*Head*",
                "**/*Shoulder*",
                "**/*Arm*",
                "**/*Hand*",
                "**/*Hip*",
                "**/*Leg*",
                "**/*Foot*",
            ]

            for pattern in patterns:
                try:
                    nodes = model_np.findAllMatches(pattern)
                    if nodes.getNumPaths() > 0:
                        print(f"Pattern '{pattern}': {nodes.getNumPaths()} nodes found")
                        for j in range(min(5, nodes.getNumPaths())):  # Show first 5
                            node = nodes.getPath(j)
                            print(f"  - {node.getName()}: {node.getPos(model_np)}")
                except Exception as e:
                    print(f"Pattern '{pattern}' failed: {e}")

        except Exception as e:
            print(f"Error in joint debugging: {e}")

    def debug_all_joints_in_model_ui(self):
        """UI method to debug all joints in the model."""
        try:
            if not self.animate_panel or not hasattr(self.animate_panel, "_actor"):
                print("No animate panel or actor available for joint debugging")
                return

            actor = self.animate_panel._actor
            if actor is None:
                print("No actor available for joint debugging")
                return

            # Run the debug function
            all_joints = self.debug_all_joints_in_model(actor)

            # Clear the cache and refresh the joint list
            self._available_joints_cache.clear()
            self.update_joint_combo_box()

            print(f"Debug completed. Found {len(all_joints)} total joints in model.")

        except Exception as e:
            print(f"Error in joint debugging UI: {e}")

    def _try_joint_coloring_approach_1(self, model_np):
        """Approach 1: Highlight joints in black for better visibility"""
        try:
            from panda3d.core import VBase4

            # Use black color for all joints for maximum contrast
            black_color = VBase4(0.0, 0.0, 0.0, 1.0)  # Black

            joint_names = [
                "mixamorig:Head",
                "mixamorig:Neck",
                "mixamorig:RightShoulder",
                "mixamorig:LeftShoulder",
                "mixamorig:RightArm",
                "mixamorig:LeftArm",
                "mixamorig:RightForeArm",
                "mixamorig:LeftForeArm",
                "mixamorig:RightHand",
                "mixamorig:LeftHand",
                "mixamorig:RightHandIndex1",
                "mixamorig:RightHandIndex2",
                "mixamorig:RightHandIndex3",
                "mixamorig:RightHandMiddle1",
                "mixamorig:RightHandMiddle2",
                "mixamorig:RightHandMiddle3",
                "mixamorig:RightHandRing1",
                "mixamorig:RightHandRing2",
                "mixamorig:RightHandRing3",
                "mixamorig:RightHandPinky1",
                "mixamorig:RightHandPinky2",
                "mixamorig:RightHandPinky3",
                "mixamorig:RightHandThumb1",
                "mixamorig:RightHandThumb2",
                "mixamorig:RightHandThumb3",
            ]

            print("=== Approach 1: Highlighting joints in black ===")
            highlighted_count = 0

            for joint_name in joint_names:
                try:
                    joint_node = model_np.find(f"**/{joint_name}")
                    if joint_node and not joint_node.isEmpty():
                        joint_node.setColor(black_color)
                        print(f"✓ Highlighted {joint_name} in black")
                        highlighted_count += 1
                    else:
                        print(f"✗ Could not find {joint_name}")
                except Exception as e:
                    print(f"✗ Error with {joint_name}: {e}")

            print(f"Successfully highlighted {highlighted_count} joints in black")

        except Exception as e:
            print(f"Approach 1 failed: {e}")

    def _try_joint_coloring_approach_2(self, model_np):
        """Approach 2: Try to find joints by partial name matching"""
        try:
            from panda3d.core import VBase4

            print("=== Approach 2: Partial name matching ===")

            black_color = VBase4(0.0, 0.0, 0.0, 1.0)  # Black

            # Try to find any node containing "Hand" in the name
            hand_nodes = model_np.findAllMatches("**/*Hand*")
            print(f"Found {hand_nodes.getNumPaths()} hand-related nodes")
            for i in range(hand_nodes.getNumPaths()):
                node = hand_nodes.getPath(i)
                print(f"  Hand node {i}: {node.getName()}")
                try:
                    node.setColor(black_color)  # Black
                    print(f"  ✓ Colored {node.getName()} black")
                except Exception as e:
                    print(f"  ✗ Could not color {node.getName()}: {e}")

            # Try to find any node containing "Arm" in the name
            arm_nodes = model_np.findAllMatches("**/*Arm*")
            print(f"Found {arm_nodes.getNumPaths()} arm-related nodes")
            for i in range(arm_nodes.getNumPaths()):
                node = arm_nodes.getPath(i)
                print(f"  Arm node {i}: {node.getName()}")
                try:
                    node.setColor(black_color)  # Black
                    print(f"  ✓ Colored {node.getName()} black")
                except Exception as e:
                    print(f"  ✗ Could not color {node.getName()}: {e}")

            # Try to find any node containing "Shoulder" in the name
            shoulder_nodes = model_np.findAllMatches("**/*Shoulder*")
            print(f"Found {shoulder_nodes.getNumPaths()} shoulder-related nodes")
            for i in range(shoulder_nodes.getNumPaths()):
                node = shoulder_nodes.getPath(i)
                print(f"  Shoulder node {i}: {node.getName()}")
                try:
                    node.setColor(black_color)  # Black
                    print(f"  ✓ Colored {node.getName()} black")
                except Exception as e:
                    print(f"  ✗ Could not color {node.getName()}: {e}")

        except Exception as e:
            print(f"Approach 2 failed: {e}")

    def _try_joint_coloring_approach_3(self, model_np):
        """Approach 3: Try to color all children recursively"""
        try:
            from panda3d.core import VBase4

            print("=== Approach 3: Recursive coloring ===")

            def color_children_recursive(node, depth=0, max_depth=3):
                if depth > max_depth:
                    return

                indent = "  " * depth
                print(f"{indent}Node: {node.getName()}")

                try:
                    # Color this node black for maximum contrast
                    black_color = VBase4(0.0, 0.0, 0.0, 1.0)  # Black
                    node.setColor(black_color)
                    print(f"{indent}✓ Colored black")
                except Exception as e:
                    print(f"{indent}✗ Could not color: {e}")

                # Recursively color children
                for child in node.getChildren():
                    color_children_recursive(child, depth + 1, max_depth)

            color_children_recursive(model_np)

        except Exception as e:
            print(f"Approach 3 failed: {e}")

    def _try_geometry_coloring_approach(self, model_np):
        """Approach 4: Color actual geometry nodes for visible effect"""
        try:
            from panda3d.core import VBase4

            print("=== Approach 4: Geometry coloring for visible effect ===")

            # Find all geometry nodes in the model
            geom_nodes = model_np.findAllMatches("**/+GeomNode")
            print(f"Found {geom_nodes.getNumPaths()} geometry nodes")

            # Color all geometry nodes black for maximum contrast
            black_color = VBase4(0.0, 0.0, 0.0, 1.0)  # Black

            for i in range(geom_nodes.getNumPaths()):
                geom_node = geom_nodes.getPath(i)
                try:
                    geom_node.setColor(black_color)
                    print(f"✓ Colored geometry node {i} black")
                except Exception as e:
                    print(f"✗ Could not color geometry node {i}: {e}")

            # Also try to color the entire model with a pattern
            print("=== Attempting full model color pattern ===")
            try:
                # Set the main model to a base color
                model_np.setColor(VBase4(0.8, 0.8, 0.8, 1.0))  # Light gray base
                print("✓ Set base model color to light gray")

                # Try to find and color specific body parts in black
                body_parts = {
                    "Head": VBase4(0.0, 0.0, 0.0, 1.0),  # Black
                    "Torso": VBase4(0.0, 0.0, 0.0, 1.0),  # Black
                    "Arm": VBase4(0.0, 0.0, 0.0, 1.0),  # Black
                    "Hand": VBase4(0.0, 0.0, 0.0, 1.0),  # Black
                    "Leg": VBase4(0.0, 0.0, 0.0, 1.0),  # Black
                }

                for part_name, color in body_parts.items():
                    part_nodes = model_np.findAllMatches(f"**/*{part_name}*")
                    for j in range(part_nodes.getNumPaths()):
                        part_node = part_nodes.getPath(j)
                        try:
                            part_node.setColor(color)
                            print(f"✓ Colored {part_name} part with {color}")
                        except Exception as e:
                            print(f"✗ Could not color {part_name} part: {e}")

            except Exception as e:
                print(f"✗ Full model coloring failed: {e}")

        except Exception as e:
            print(f"Approach 4 failed: {e}")

    def remove_joint_highlighting(self):
        """Remove joint highlighting and restore default colors."""
        # Use the comprehensive reset function
        self.reset_all_visibility_effects()

    def highlight_hands_only(self):
        """Highlight only the hands with special colors for maximum visibility."""
        if not self.animate_panel or not hasattr(self.animate_panel, "_model_np"):
            return

        try:
            from panda3d.core import VBase4

            # Special colors for hands and fingers
            hand_colors = {
                "mixamorig:RightHand": VBase4(1.0, 1.0, 0.0, 1.0),  # Bright Yellow
                "mixamorig:LeftHand": VBase4(0.0, 1.0, 1.0, 1.0),  # Bright Cyan
                # Right hand fingers - Bright red shades for maximum visibility
                "mixamorig:RightHandIndex1": VBase4(1.0, 0.0, 0.0, 1.0),
                "mixamorig:RightHandIndex2": VBase4(1.0, 0.1, 0.0, 1.0),
                "mixamorig:RightHandIndex3": VBase4(1.0, 0.2, 0.0, 1.0),
                "mixamorig:RightHandIndex4": VBase4(1.0, 0.3, 0.0, 1.0),
                "mixamorig:RightHandMiddle1": VBase4(1.0, 0.0, 0.1, 1.0),
                "mixamorig:RightHandMiddle2": VBase4(1.0, 0.0, 0.2, 1.0),
                "mixamorig:RightHandMiddle3": VBase4(1.0, 0.0, 0.3, 1.0),
                "mixamorig:RightHandMiddle4": VBase4(1.0, 0.0, 0.4, 1.0),
                "mixamorig:RightHandRing1": VBase4(1.0, 0.1, 0.0, 1.0),
                "mixamorig:RightHandRing2": VBase4(1.0, 0.2, 0.0, 1.0),
                "mixamorig:RightHandRing3": VBase4(1.0, 0.3, 0.0, 1.0),
                "mixamorig:RightHandRing4": VBase4(1.0, 0.4, 0.0, 1.0),
                "mixamorig:RightHandPinky1": VBase4(0.9, 0.0, 0.0, 1.0),
                "mixamorig:RightHandPinky2": VBase4(0.9, 0.1, 0.0, 1.0),
                "mixamorig:RightHandPinky3": VBase4(0.9, 0.2, 0.0, 1.0),
                "mixamorig:RightHandPinky4": VBase4(0.9, 0.3, 0.0, 1.0),
                "mixamorig:RightHandThumb1": VBase4(
                    1.0, 1.0, 0.0, 1.0
                ),  # Bright yellow for thumb
                "mixamorig:RightHandThumb2": VBase4(1.0, 1.0, 0.1, 1.0),
                "mixamorig:RightHandThumb3": VBase4(1.0, 1.0, 0.2, 1.0),
                "mixamorig:RightHandThumb4": VBase4(1.0, 1.0, 0.3, 1.0),
                # Left hand fingers - Bright green shades for maximum visibility
                "mixamorig:LeftHandIndex1": VBase4(0.0, 1.0, 0.0, 1.0),
                "mixamorig:LeftHandIndex2": VBase4(0.0, 1.0, 0.1, 1.0),
                "mixamorig:LeftHandIndex3": VBase4(0.0, 1.0, 0.2, 1.0),
                "mixamorig:LeftHandIndex4": VBase4(0.0, 1.0, 0.3, 1.0),
                "mixamorig:LeftHandMiddle1": VBase4(0.0, 0.9, 0.0, 1.0),
                "mixamorig:LeftHandMiddle2": VBase4(0.0, 0.9, 0.1, 1.0),
                "mixamorig:LeftHandMiddle3": VBase4(0.0, 0.9, 0.2, 1.0),
                "mixamorig:LeftHandMiddle4": VBase4(0.0, 0.9, 0.3, 1.0),
                "mixamorig:LeftHandRing1": VBase4(0.0, 0.8, 0.0, 1.0),
                "mixamorig:LeftHandRing2": VBase4(0.0, 0.8, 0.1, 1.0),
                "mixamorig:LeftHandRing3": VBase4(0.0, 0.8, 0.2, 1.0),
                "mixamorig:LeftHandRing4": VBase4(0.0, 0.8, 0.3, 1.0),
                "mixamorig:LeftHandPinky1": VBase4(0.0, 0.7, 0.0, 1.0),
                "mixamorig:LeftHandPinky2": VBase4(0.0, 0.7, 0.1, 1.0),
                "mixamorig:LeftHandPinky3": VBase4(0.0, 0.7, 0.2, 1.0),
                "mixamorig:LeftHandPinky4": VBase4(0.0, 0.7, 0.3, 1.0),
                "mixamorig:LeftHandThumb1": VBase4(
                    0.0, 1.0, 1.0, 1.0
                ),  # Bright cyan for thumb
                "mixamorig:LeftHandThumb2": VBase4(0.0, 1.0, 0.9, 1.0),
                "mixamorig:LeftHandThumb3": VBase4(0.0, 1.0, 0.8, 1.0),
                "mixamorig:LeftHandThumb4": VBase4(0.0, 1.0, 0.7, 1.0),
            }

            model_np = self.animate_panel._model_np
            if model_np is not None:
                # First restore default blue for all joints
                model_np.setColor(VBase4(0.1, 0.3, 0.9, 1.0))

                # Then highlight only hands and fingers
                for joint_name, color in hand_colors.items():
                    try:
                        joint_node = model_np.find(f"**/{joint_name}")
                        if joint_node and not joint_node.isEmpty():
                            joint_node.setColor(color)
                            print(f"Highlighted hand joint {joint_name}")
                    except Exception as e:
                        print(f"Could not highlight hand joint {joint_name}: {e}")

                print("Hand highlighting applied successfully")

        except Exception as e:
            print(f"Error highlighting hands: {e}")

    def enhance_lighting_for_hands(self):
        """Enhance lighting specifically for hand visibility."""
        try:
            if not self.animate_panel or not hasattr(
                self.animate_panel, "_model_manager"
            ):
                print("No model manager found for lighting enhancement")
                return

            model_manager = self.animate_panel._model_manager
            if not model_manager:
                print("Model manager not available")
                return

            # Add additional spotlights focused on the hands
            from panda3d.core import Spotlight, VBase4, Vec3

            # Create a spotlight for the right hand
            right_hand_light = Spotlight("right_hand_light")
            right_hand_light.setColor(VBase4(1.0, 1.0, 1.0, 1.0))
            right_hand_light.setSpecularColor(VBase4(1.0, 1.0, 1.0, 1.0))
            right_hand_light.setAttenuation(Vec3(1.0, 0.0, 0.0))
            right_hand_light.setExponent(10.0)
            right_hand_light.setShadowCaster(True)

            # Position the light to illuminate the right hand area
            light_np = model_manager.parent_panel.render.attachNewNode(right_hand_light)
            light_np.setPos(0.5, 2.0, 1.5)  # Position to illuminate right hand
            light_np.lookAt(0.3, 0.0, 1.0)  # Point towards right hand area

            # Store reference for later removal
            if not hasattr(self, "_enhanced_lights"):
                self._enhanced_lights = []
            self._enhanced_lights.append(light_np)

            print("Enhanced lighting for hands applied")

        except Exception as e:
            print(f"Error enhancing lighting: {e}")

    def toggle_wireframe_mode(self):
        """Toggle wireframe mode for better hand structure visibility."""
        try:
            if not self.animate_panel or not hasattr(self.animate_panel, "_model_np"):
                print("No model found for wireframe toggle")
                return

            model_np = self.animate_panel._model_np
            if model_np is None:
                print("Model node path not available")
                return

            # Toggle wireframe mode
            if not hasattr(self, "_wireframe_enabled"):
                self._wireframe_enabled = False

            self._wireframe_enabled = not self._wireframe_enabled

            if self._wireframe_enabled:
                model_np.setRenderModeWireframe()
                print("Wireframe mode enabled")
            else:
                model_np.setRenderModeFilled()
                print("Wireframe mode disabled")

        except Exception as e:
            print(f"Error toggling wireframe: {e}")

    def add_hand_outlines(self):
        """Add outlines to hands for better visibility."""
        try:
            if not self.animate_panel or not hasattr(self.animate_panel, "_model_np"):
                print("No model found for outline addition")
                return

            model_np = self.animate_panel._model_np
            if model_np is None:
                print("Model node path not available")
                return

            # Try to find hand nodes and add outlines
            hand_nodes = model_np.findAllMatches("**/*Hand*")
            print(f"Found {hand_nodes.getNumPaths()} hand nodes for outlining")

            for i in range(hand_nodes.getNumPaths()):
                hand_node = hand_nodes.getPath(i)
                try:
                    # Create a duplicate for outline effect
                    outline_node = hand_node.copyTo(model_np)
                    outline_node.setColor(0.0, 0.0, 0.0, 1.0)  # Black outline
                    outline_node.setRenderModeWireframe()
                    outline_node.setScale(1.02)  # Slightly larger for outline effect
                    outline_node.setDepthWrite(False)
                    outline_node.setDepthTest(False)

                    # Store reference for later removal
                    if not hasattr(self, "_outline_nodes"):
                        self._outline_nodes = []
                    self._outline_nodes.append(outline_node)

                    print(f"Added outline to {hand_node.getName()}")
                except Exception as e:
                    print(f"Could not add outline to {hand_node.getName()}: {e}")

            print("Hand outlines added")

        except Exception as e:
            print(f"Error adding hand outlines: {e}")

    def reset_all_visibility_effects(self):
        """Reset all visibility effects and restore default appearance."""
        try:
            if not self.animate_panel or not hasattr(self.animate_panel, "_model_np"):
                print("No model found for reset")
                return

            model_np = self.animate_panel._model_np
            if model_np is None:
                print("Model node path not available")
                return

            # Reset wireframe mode
            if hasattr(self, "_wireframe_enabled") and self._wireframe_enabled:
                model_np.setRenderModeFilled()
                self._wireframe_enabled = False
                print("Wireframe mode disabled")

            # Remove enhanced lights
            if hasattr(self, "_enhanced_lights"):
                for light_np in self._enhanced_lights:
                    try:
                        light_np.removeNode()
                    except Exception as e:
                        print(f"Error removing light: {e}")
                self._enhanced_lights = []
                print("Enhanced lights removed")

            # Remove outline nodes
            if hasattr(self, "_outline_nodes"):
                for outline_node in self._outline_nodes:
                    try:
                        outline_node.removeNode()
                    except Exception as e:
                        print(f"Error removing outline: {e}")
                self._outline_nodes = []
                print("Hand outlines removed")

            # Remove joint markers
            joint_markers = model_np.findAllMatches("**/joint_marker_*")
            for i in range(joint_markers.getNumPaths()):
                try:
                    joint_markers.getPath(i).removeNode()
                except:
                    pass
            print("Joint markers removed")

            # Restore default blue color
            from panda3d.core import VBase4

            default_color = VBase4(0.1, 0.3, 0.9, 1.0)
            model_np.setColor(default_color)

            print("All visibility effects reset")

        except Exception as e:
            print(f"Error resetting visibility effects: {e}")


# Legacy compatibility - keep the old class name for existing code
HPRInteractiveEditor = SignLanguagePoseEditor
