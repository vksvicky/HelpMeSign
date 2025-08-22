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
    QSpacerItem,
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
        """Create neutral pose using pose data service."""
        # Use the same pose data service as the main pipeline
        from ...utils.sign_mt_real.asset_manager import AssetManager
        from ...utils.sign_mt_real.pose_data_service import PoseDataService

        asset_manager = AssetManager()
        pose_data_service = PoseDataService(asset_manager)
        neutral_pose_data = pose_data_service.get_neutral_pose()

        # Convert PoseData to JointPose format
        neutral_poses = {}
        for joint_name, hpr_values in neutral_pose_data.joints.items():
            if len(hpr_values) >= 3:
                neutral_poses[joint_name] = JointPose(
                    joint_name,
                    float(hpr_values[0]),
                    float(hpr_values[1]),
                    float(hpr_values[2]),
                )

        return neutral_poses

    def _initialize_poses(self):
        """Initialize poses with neutral values."""
        self._poses = {name: pose for name, pose in self._neutral_pose.items()}

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

        # Load current pose
        self.load_current_pose()

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
        self.setParent(None)
        self.deleteLater()


class SignLanguagePoseEditor(QWidget):
    """Main sign language pose editor following sign.mt architecture."""

    def __init__(self, animate_panel=None):
        super().__init__()
        self.animate_panel = animate_panel
        self.pose_manager = PoseManager()
        self.joint_editors: Dict[str, JointEditor] = {}
        self._available_joints_cache = []  # Cache for available joints

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.setWindowTitle("Sign Language Pose Editor - sign.mt Style")
        self.setMinimumSize(1000, 800)
        self.resize(1000, 800)

        layout = QVBoxLayout(self)

        # Header with close button
        header_layout = QHBoxLayout()

        header = QLabel("Sign Language Pose Editor")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
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
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
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
            # Left Hand Fingers
            "mixamorig:LeftHandIndex1",
            "mixamorig:LeftHandIndex2",
            "mixamorig:LeftHandIndex3",
            "mixamorig:LeftHandMiddle1",
            "mixamorig:LeftHandMiddle2",
            "mixamorig:LeftHandMiddle3",
            "mixamorig:LeftHandRing1",
            "mixamorig:LeftHandRing2",
            "mixamorig:LeftHandRing3",
            "mixamorig:LeftHandPinky1",
            "mixamorig:LeftHandPinky2",
            "mixamorig:LeftHandPinky3",
            "mixamorig:LeftHandThumb1",
            "mixamorig:LeftHandThumb2",
            "mixamorig:LeftHandThumb3",
            "mixamorig:RightUpLeg",
            "mixamorig:LeftUpLeg",
            "mixamorig:RightLeg",
            "mixamorig:LeftLeg",
            "mixamorig:RightFoot",
            "mixamorig:LeftFoot",
            "mixamorig:RightToeBase",
            "mixamorig:LeftToeBase",
        ]
        # Connect the signal as fallback (will be reconnected with valid joints)
        self.joint_combo.currentTextChanged.connect(self.on_joint_selected)

        joint_layout.addWidget(QLabel("Joint:"))
        joint_layout.addWidget(self.joint_combo)
        layout.addWidget(joint_group)

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

        # Refresh button
        refresh_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("Capture Current Pose")
        self.refresh_btn.clicked.connect(self.load_current_character_values)
        refresh_layout.addWidget(self.refresh_btn)

        controls_layout.addLayout(refresh_layout)

        layout.addWidget(controls_group)

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
        """Handle show event - load current character values when editor opens."""
        super().showEvent(event)
        # Only detect joints once when opening
        if not self._available_joints_cache:
            self.update_joint_combo_box()  # Update combo box with available joints first
        self.load_current_pose_from_service()
        self.update_pose_display()

    def load_current_character_values(self):
        """Reset editor to neutral pose values (default pose)."""
        if not self.animate_panel or not hasattr(self.animate_panel, "_actor"):
            return

        try:
            actor = self.animate_panel._actor
            if actor is None:
                return

            # Get available joints from the actor
            available_joints = self.get_available_joints(actor)

            # Capture current character pose as neutral pose
            self.capture_current_pose_as_neutral(actor, available_joints)

            # Update existing joint editors to show neutral values
            for joint_name, editor in self.joint_editors.items():
                editor.load_current_pose()

            # Update the pose display
            self.update_pose_display()

            print(
                f"Captured current character pose as neutral pose ({len(available_joints)} available joints)"
            )

        except Exception as e:
            print(f"Error capturing current pose: {e}")

    def load_current_pose_from_service(self):
        """Load the current pose from pose_data_service into the pose manager."""
        try:
            # Import and get the pose from pose_data_service
            from ...utils.sign_mt_real.asset_manager import AssetManager
            from ...utils.sign_mt_real.pose_data_service import PoseDataService

            asset_manager = AssetManager()
            pose_service = PoseDataService(asset_manager)
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

        try:
            # Test each joint in our neutral pose to see if it exists
            for joint_name in self.pose_manager._neutral_pose.keys():
                try:
                    joint = actor.controlJoint(None, "modelRoot", joint_name)
                    if joint is not None:
                        available_joints.append(joint_name)
                except Exception:
                    # Silently skip joints that can't be controlled
                    pass

            # Cache the result
            self._available_joints_cache = available_joints
            print(f"Detected {len(available_joints)} available joints")
            return available_joints

        except Exception as e:
            print(f"Error getting available joints: {e}")
            return []

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
            print(f"Created editor for {joint_name}")
        else:
            print(f"Editor already exists for {joint_name}")

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
        """Reset all poses to neutral."""
        self.pose_manager.reset_to_neutral()
        # Update existing joint editors
        for joint_name, editor in self.joint_editors.items():
            editor.load_current_pose()
        self.update_pose_display()

    def apply_to_character(self):
        """Apply all poses to the character."""
        poses = self.pose_manager.get_all_poses()
        # Only apply poses for available joints
        for joint_name, pose in poses.items():
            if joint_name in self._available_joints_cache:
                self.apply_pose_to_character(joint_name, pose)

    def apply_pose_to_character(self, joint_name: str, pose: JointPose):
        """Apply a single pose to the character."""
        if not self.animate_panel or not hasattr(self.animate_panel, "_actor"):
            return

        # Validate that this joint is available
        if joint_name not in self._available_joints_cache:
            return

        try:
            actor = self.animate_panel._actor
            if actor is None:
                return

            joint = actor.controlJoint(None, "modelRoot", joint_name)
            if joint is not None:
                joint.setHpr(pose.heading, pose.pitch, pose.roll)
                actor.update()

        except Exception as e:
            print(f"Error applying pose to {joint_name}: {e}")

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

    def shutdown(self):
        """Gracefully shutdown the HPR editor."""
        try:
            # Clear all joint editors
            for editor in self.joint_editors.values():
                if editor.parent():
                    editor.setParent(None)
            self.joint_editors.clear()

            # Clear cache
            self._available_joints_cache = []

            # Clear pose manager
            if hasattr(self, "pose_manager"):
                self.pose_manager = None

            print("HPR editor shutdown completed")

        except Exception as e:
            print(f"Error during HPR editor shutdown: {e}")


# Legacy compatibility - keep the old class name for existing code
HPRInteractiveEditor = SignLanguagePoseEditor
