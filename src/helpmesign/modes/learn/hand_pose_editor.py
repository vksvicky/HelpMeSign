#!/usr/bin/env python3
"""
Specialized Hand Pose Editor for HelpMeSign
Focused on hand, finger, and arm poses with zoomed view and image reference
"""

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Camera and Character Position Control Constants
POSITION_INCREMENT = 0.01  # Change this value to adjust slider precision
CAMERA_X_RANGE = (-2000, 2000)  # -20 to 20 in 0.01 increments
CAMERA_Y_RANGE = (-3000, 0)  # -30 to 0 in 0.01 increments
CAMERA_Z_RANGE = (-1000, 1000)  # -10 to 10 in 0.01 increments
CHAR_X_RANGE = (-500, 500)  # -5 to 5 in 0.01 increments
CHAR_Y_RANGE = (-500, 500)  # -5 to 5 in 0.01 increments
CHAR_Z_RANGE = (-500, 500)  # -5 to 5 in 0.01 increments

try:
    from PySide6.QtCore import QObject, Qt, QTimer, Signal
    from PySide6.QtGui import QFont, QPixmap
    from PySide6.QtWidgets import (
        QComboBox,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QSlider,
        QSpinBox,
        QSplitter,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    print("PySide6 not available")


from src.helpmesign.modes.learn.hpr_editor import JointPose, PoseManager


@dataclass
class HandJointPose:
    """Hand-specific joint pose data"""

    joint_name: str
    heading: float
    pitch: float
    roll: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HandJointPose":
        return cls(
            joint_name=data["joint_name"],
            heading=data["hpr"][0],
            pitch=data["hpr"][1],
            roll=data["hpr"][2],
        )


class HandPoseEditor(QWidget):
    """Specialized editor for hand, finger, and arm poses with zoomed view"""

    def __init__(self, animate_panel: Any, main_window: Any, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("helpmesign")
        self.animate_panel = animate_panel
        self.main_window = main_window
        self.pose_manager = PoseManager()
        self.joint_editors: Dict[str, "HandJointEditor"] = {}
        self.current_language = "ASL"
        self.current_letter = "A"
        self.reference_image_path = None
        self.original_pose_stored = False

        # Check if PySide6 is available
        if not PYSIDE6_AVAILABLE:
            self.logger.error(
                "PySide6 not available! Hand Pose Editor cannot function properly."
            )
            raise RuntimeError("PySide6 is required for Hand Pose Editor to function")

        # Set window properties for proper cleanup - same as HPR Editor
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)

        try:
            self.setup_ui()
            self.load_hand_joints()

            # No need to store original pose since we're using a separate 3D view
            self.setup_connections()
        except Exception as e:
            self.logger.error(f"HandPoseEditor: Error during initialization: {e}")
            import traceback

            self.logger.error(f"HandPoseEditor: Traceback: {traceback.format_exc()}")
            raise

    def closeEvent(self, event):
        """Handle window close event - clean up resources and restore main window"""
        try:
            self.logger.info("Hand Pose Editor closing - cleaning up resources")

            # Restore the main window's character visibility
            if (
                hasattr(self.animate_panel, "_model_np")
                and self.animate_panel._model_np
            ):
                self.animate_panel._model_np.show()
                self.logger.info("Restored main window character visibility")

            # Restore the main window's 3D panel visibility
            if hasattr(self.animate_panel, "_display"):
                self.animate_panel._display.show()
                self.logger.info("Restored main window 3D panel visibility")

            # Restore the main window's natural pose
            self._restore_main_window_natural_pose()

            # No need to clean up 3D view since we're reusing the main window's view
            self.logger.info(
                "Hand Pose Editor using main window's 3D view - no cleanup needed"
            )

            # Clean up resources
            self.joint_editors.clear()
            self.pose_manager = None

            # Clear references
            self.animate_panel = None
            self.main_window = None

            self.logger.info("Hand Pose Editor closed successfully")
            event.accept()

        except Exception as e:
            self.logger.error(f"Error during Hand Pose Editor close: {e}")
            event.accept()  # Still accept the close event

    def _restore_main_window_pose(self):
        """Restore the main window's character to its original pose"""
        try:
            self.logger.info("Starting pose restoration...")
            if not hasattr(self, "animate_panel") or not self.animate_panel:
                self.logger.warning("No animate_panel available for pose restoration")
                return

            if hasattr(self.animate_panel, "_actor") and self.animate_panel._actor:
                self.logger.info("Actor found, checking for stored original pose...")
                applied_poses = 0

                # If we have stored the original pose, restore it
                if hasattr(self, "original_pose") and self.original_pose:
                    self.logger.info(
                        f"Found stored original pose with {len(self.original_pose)} joints, restoring..."
                    )
                    for joint_name, pose_data in self.original_pose.items():
                        try:
                            # Get the joint using controlJoint method
                            joint = self.animate_panel._actor.controlJoint(
                                None, "modelRoot", joint_name
                            )
                            if joint is not None and not joint.isEmpty():
                                # Apply the original pose values
                                joint.setHpr(
                                    pose_data["heading"],
                                    pose_data["pitch"],
                                    pose_data["roll"],
                                )
                                applied_poses += 1
                                # Debug: Log the first few joint values being restored
                                if joint_name in [
                                    "mixamorig:RightShoulder",
                                    "mixamorig:RightHand",
                                    "mixamorig:RightHandThumb1",
                                ]:
                                    self.logger.info(
                                        f"Restored {joint_name}: H={pose_data['heading']:.1f}, P={pose_data['pitch']:.1f}, R={pose_data['roll']:.1f}"
                                    )
                            else:
                                self.logger.debug(
                                    f"Joint {joint_name} not found for restoration"
                                )
                        except Exception as e:
                            self.logger.debug(
                                f"Could not restore original pose for joint {joint_name}: {e}"
                            )

                    # Update the actor to make changes visible
                    self.animate_panel._actor.update()
                    self.logger.info(
                        f"Restored original pose to main window character with {applied_poses} joints"
                    )
                else:
                    self.logger.warning(
                        "No stored original pose found, trying natural pose fallback..."
                    )
                    # Fallback to natural pose if original pose wasn't stored
                    try:
                        from src.helpmesign.utils.natural_pose_service import (
                            NaturalPoseService,
                        )

                        natural_pose_service = NaturalPoseService()
                        natural_poses = natural_pose_service.get_natural_poses()
                    except ImportError:
                        self.logger.warning(
                            "Natural pose service not available, skipping pose restoration"
                        )
                        return

                    for joint_name, pose_data in natural_poses.items():
                        try:
                            # Get the joint using controlJoint method
                            joint = self.animate_panel._actor.controlJoint(
                                None, "modelRoot", joint_name
                            )
                            if joint is not None and not joint.isEmpty():
                                # Apply the natural pose values
                                joint.setHpr(
                                    pose_data["heading"],
                                    pose_data["pitch"],
                                    pose_data["roll"],
                                )
                                applied_poses += 1
                            else:
                                self.logger.debug(
                                    f"Joint {joint_name} not found for natural pose restoration"
                                )
                        except Exception as e:
                            self.logger.debug(
                                f"Could not restore natural pose for joint {joint_name}: {e}"
                            )

                    # Update the actor to make changes visible
                    self.animate_panel._actor.update()
                    self.logger.info(
                        f"Restored natural pose to main window character with {applied_poses} joints"
                    )
            else:
                self.logger.warning("Cannot restore pose - actor not available")

        except Exception as e:
            self.logger.error(f"Error restoring main window pose: {e}")

    def _store_original_pose(self):
        """Store the original pose of the main window character"""
        try:
            self.logger.info("Starting to store original pose...")
            if not hasattr(self, "animate_panel") or not self.animate_panel:
                self.logger.warning("No animate_panel available for pose storage")
                return

            if hasattr(self.animate_panel, "_actor") and self.animate_panel._actor:
                self.logger.info(
                    "Actor found, storing original pose for hand joints..."
                )
                # Store the current pose of the main window character
                self.original_pose = {}

                # Get all joints and store their current HPR values
                for joint_name in self.hand_joints:
                    try:
                        # Get the joint using controlJoint method
                        joint = self.animate_panel._actor.controlJoint(
                            None, "modelRoot", joint_name
                        )
                        if joint is not None and not joint.isEmpty():
                            # Get current HPR values
                            hpr = joint.getHpr()
                            self.original_pose[joint_name] = {
                                "heading": hpr[0],
                                "pitch": hpr[1],
                                "roll": hpr[2],
                            }
                            # Debug: Log the first few joint values
                            if joint_name in [
                                "mixamorig:RightShoulder",
                                "mixamorig:RightHand",
                                "mixamorig:RightHandThumb1",
                            ]:
                                self.logger.info(
                                    f"Stored {joint_name}: H={hpr[0]:.1f}, P={hpr[1]:.1f}, R={hpr[2]:.1f}"
                                )
                        else:
                            self.logger.debug(
                                f"Joint {joint_name} not found or not controllable"
                            )
                    except Exception as e:
                        self.logger.debug(
                            f"Could not store original pose for joint {joint_name}: {e}"
                        )

                self.original_pose_stored = True
                self.logger.info(
                    f"Stored original pose for {len(self.original_pose)} joints"
                )
            else:
                self.logger.warning("Cannot store original pose - actor not available")

        except Exception as e:
            self.logger.error(f"Error storing original pose: {e}")

    def setup_ui(self):
        """Set up the specialized hand pose editor UI"""
        self.setWindowTitle("Hand Pose Editor - HelpMeSign")
        self.setMinimumSize(1400, 900)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Header with title and controls
        header_layout = QHBoxLayout()

        title = QLabel("🖐️ Hand Pose Editor")
        title.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
        """
        )
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Language and letter selection
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["ASL", "BSL", "ISL", "Auslan", "LSF", "DGS"])
        self.lang_combo.setCurrentText("ASL")
        header_layout.addWidget(QLabel("Language:"))
        header_layout.addWidget(self.lang_combo)

        self.letter_combo = QComboBox()
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
            self.letter_combo.addItem(letter)
        self.letter_combo.setCurrentText("A")
        header_layout.addWidget(QLabel("Letter:"))
        header_layout.addWidget(self.letter_combo)

        # Refresh button
        self.refresh_btn = QPushButton("🔄 Reload Data")
        self.refresh_btn.clicked.connect(self.reload_pose_data)
        self.refresh_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        header_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(header_layout)

        # Main splitter - 3D view on left, controls on right
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)

        # Left panel - 3D view with zoom
        left_panel = self.create_3d_view_panel()
        main_splitter.addWidget(left_panel)

        # Right panel - Controls and reference image
        right_panel = self.create_controls_panel()
        main_splitter.addWidget(right_panel)

        # Set splitter proportions (60% for 3D view, 40% for controls)
        main_splitter.setSizes([840, 560])

    def create_3d_view_panel(self) -> QWidget:
        """Create the 3D view panel with zoomed character"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 3D view group
        view_group = QGroupBox("3D Hand View (6x Zoom - Hip & Above)")
        view_layout = QVBoxLayout(view_group)

        # Use the main window's 3D view for the Hand Pose Editor
        # This ensures we only have one character and one 3D view
        animate_panel_valid = False
        try:
            # Reuse the main window's AnimateGesturePanel
            self.editor_3d_view = self.animate_panel
            animate_panel_valid = True
            self.logger.info("Using main window's 3D view for Hand Pose Editor")

            # Apply neutral pose to the character for editing
            from PySide6.QtCore import QTimer

            def sync_pose_after_load():
                try:
                    if (
                        hasattr(self.editor_3d_view, "_actor")
                        and self.editor_3d_view._actor
                    ):
                        # Apply neutral pose to the character
                        self._apply_neutral_pose_to_editor()

                        self.logger.info(
                            "Successfully applied neutral pose for Hand Pose Editor"
                        )
                    else:
                        self.logger.warning(
                            "Character actor not available for pose sync"
                        )
                except Exception as e:
                    self.logger.error(f"Error syncing pose after load: {e}")

            # Use QTimer to ensure the 3D view is fully initialized
            QTimer.singleShot(1000, sync_pose_after_load)

            view_layout.addWidget(self.editor_3d_view)
            self.logger.info("Added main window's 3D view to Hand Pose Editor")

        except Exception as e:
            self.logger.warning(f"Could not use main window's 3D view: {e}")
            animate_panel_valid = False

        # Fallback placeholder if no 3D view available
        if not animate_panel_valid:
            # Fallback placeholder if no 3D view available
            self.view_placeholder = QLabel(
                "3D Character View\n(6x Zoom - Hip & Above Only)\n\n3D View not available"
            )
            self.view_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.view_placeholder.setStyleSheet(
                """
                QLabel {
                    background-color: #2c3e50;
                    color: white;
                    border: 2px solid #34495e;
                    border-radius: 8px;
                    padding: 40px;
                    font-size: 16px;
                    font-weight: bold;
                }
            """
            )
            self.view_placeholder.setMinimumHeight(400)
            view_layout.addWidget(self.view_placeholder)

        # Camera controls section (moved from right panel)
        camera_group = QGroupBox("Camera Controls")
        camera_layout = QVBoxLayout(camera_group)

        # Camera position controls
        camera_pos_layout = QHBoxLayout()

        # Camera X position
        camera_x_layout = QVBoxLayout()
        camera_x_layout.addWidget(QLabel("Camera X"))
        self.camera_x_slider = QSlider(Qt.Orientation.Horizontal)
        self.camera_x_slider.setRange(*CAMERA_X_RANGE)
        self.camera_x_slider.setSingleStep(1)  # Each step = 0.01 units
        self.camera_x_slider.setPageStep(
            1
        )  # Page step = 0.01 units (prevents 0.10 jumps)
        self.camera_x_slider.setValue(
            0
        )  # Will be updated when original position is stored
        self.camera_x_slider.valueChanged.connect(self.update_camera_position)
        camera_x_layout.addWidget(self.camera_x_slider)
        self.camera_x_label = QLabel("0.00")
        camera_x_layout.addWidget(self.camera_x_label)
        camera_pos_layout.addLayout(camera_x_layout)

        # Camera Y position
        camera_y_layout = QVBoxLayout()
        camera_y_layout.addWidget(QLabel("Camera Y"))
        self.camera_y_slider = QSlider(Qt.Orientation.Horizontal)
        self.camera_y_slider.setRange(*CAMERA_Y_RANGE)
        self.camera_y_slider.setSingleStep(1)  # Each step = 0.01 units
        self.camera_y_slider.setPageStep(
            1
        )  # Page step = 0.01 units (prevents 0.10 jumps)
        self.camera_y_slider.setValue(
            0
        )  # Will be updated when original position is stored
        self.camera_y_slider.valueChanged.connect(self.update_camera_position)
        camera_y_layout.addWidget(self.camera_y_slider)
        self.camera_y_label = QLabel("0.00")
        camera_y_layout.addWidget(self.camera_y_label)
        camera_pos_layout.addLayout(camera_y_layout)

        # Camera Z position
        camera_z_layout = QVBoxLayout()
        camera_z_layout.addWidget(QLabel("Camera Z"))
        self.camera_z_slider = QSlider(Qt.Orientation.Horizontal)
        self.camera_z_slider.setRange(*CAMERA_Z_RANGE)
        self.camera_z_slider.setSingleStep(1)  # Each step = 0.01 units
        self.camera_z_slider.setPageStep(
            1
        )  # Page step = 0.01 units (prevents 0.10 jumps)
        self.camera_z_slider.setValue(
            0
        )  # Will be updated when original position is stored
        self.camera_z_slider.valueChanged.connect(self.update_camera_position)
        camera_z_layout.addWidget(self.camera_z_slider)
        self.camera_z_label = QLabel("0.00")
        camera_z_layout.addWidget(self.camera_z_label)
        camera_pos_layout.addLayout(camera_z_layout)

        camera_layout.addLayout(camera_pos_layout)

        # Character position controls
        char_pos_layout = QHBoxLayout()

        # Character X position
        char_x_layout = QVBoxLayout()
        char_x_layout.addWidget(QLabel("Character X"))
        self.char_x_slider = QSlider(Qt.Orientation.Horizontal)
        self.char_x_slider.setRange(*CHAR_X_RANGE)
        self.char_x_slider.setSingleStep(1)  # Each step = 0.01 units
        self.char_x_slider.setPageStep(
            1
        )  # Page step = 0.01 units (prevents 0.10 jumps)
        self.char_x_slider.setValue(
            0
        )  # Will be updated when original position is stored
        self.char_x_slider.valueChanged.connect(self.update_character_position)
        char_x_layout.addWidget(self.char_x_slider)
        self.char_x_label = QLabel("0.00")
        char_x_layout.addWidget(self.char_x_label)
        char_pos_layout.addLayout(char_x_layout)

        # Character Y position
        char_y_layout = QVBoxLayout()
        char_y_layout.addWidget(QLabel("Character Y"))
        self.char_y_slider = QSlider(Qt.Orientation.Horizontal)
        self.char_y_slider.setRange(*CHAR_Y_RANGE)
        self.char_y_slider.setSingleStep(1)  # Each step = 0.01 units
        self.char_y_slider.setPageStep(
            1
        )  # Page step = 0.01 units (prevents 0.10 jumps)
        self.char_y_slider.setValue(
            0
        )  # Will be updated when original position is stored
        self.char_y_slider.valueChanged.connect(self.update_character_position)
        char_y_layout.addWidget(self.char_y_slider)
        self.char_y_label = QLabel("0.00")
        char_y_layout.addWidget(self.char_y_label)
        char_pos_layout.addLayout(char_y_layout)

        # Character Z position
        char_z_layout = QVBoxLayout()
        char_z_layout.addWidget(QLabel("Character Z"))
        self.char_z_slider = QSlider(Qt.Orientation.Horizontal)
        self.char_z_slider.setRange(*CHAR_Z_RANGE)
        self.char_z_slider.setSingleStep(1)  # Each step = 0.01 units
        self.char_z_slider.setPageStep(
            1
        )  # Page step = 0.01 units (prevents 0.10 jumps)
        self.char_z_slider.setValue(
            0
        )  # Will be updated when original position is stored
        self.char_z_slider.valueChanged.connect(self.update_character_position)
        char_z_layout.addWidget(self.char_z_slider)
        self.char_z_label = QLabel("0.00")
        char_z_layout.addWidget(self.char_z_label)
        char_pos_layout.addLayout(char_z_layout)

        camera_layout.addLayout(char_pos_layout)

        # Reset buttons
        reset_buttons_layout = QHBoxLayout()
        self.reset_camera_btn = QPushButton("Reset Camera")
        self.reset_camera_btn.clicked.connect(self.reset_camera_position)
        reset_buttons_layout.addWidget(self.reset_camera_btn)

        self.reset_character_btn = QPushButton("Reset Character")
        self.reset_character_btn.clicked.connect(self.reset_character_orientation)
        reset_buttons_layout.addWidget(self.reset_character_btn)

        camera_layout.addLayout(reset_buttons_layout)

        view_layout.addWidget(camera_group)
        layout.addWidget(view_group)

        return panel

    def create_controls_panel(self) -> QWidget:
        """Create the controls panel with joint editors and reference image"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Removed reference image section - using dropdown selection instead

        # Hand joints section
        joints_group = QGroupBox("Hand & Finger Joints")
        joints_layout = QVBoxLayout(joints_group)

        # Create scrollable area for joint editors
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(200)  # Ensure minimum height
        scroll_area.setMaximumHeight(400)

        self.joints_container = QWidget()
        self.joints_layout = QVBoxLayout(self.joints_container)
        scroll_area.setWidget(self.joints_container)

        print(f"Created joints container with layout: {self.joints_layout}")
        print(f"Scroll area widget: {scroll_area.widget()}")

        joints_layout.addWidget(scroll_area)
        layout.addWidget(joints_group)

        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_group)

        # Hand presets
        presets_layout = QHBoxLayout()

        self.fist_btn = QPushButton("Make Fist")
        self.fist_btn.clicked.connect(self.apply_fist_pose)
        presets_layout.addWidget(self.fist_btn)

        self.open_btn = QPushButton("Open Hand")
        self.open_btn.clicked.connect(self.apply_open_pose)
        presets_layout.addWidget(self.open_btn)

        self.point_btn = QPushButton("Point")
        self.point_btn.clicked.connect(self.apply_point_pose)
        presets_layout.addWidget(self.point_btn)

        actions_layout.addLayout(presets_layout)

        # Apply and reset buttons
        apply_layout = QHBoxLayout()

        self.apply_btn = QPushButton("Apply to Character")
        self.apply_btn.clicked.connect(self.apply_to_character)
        self.apply_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """
        )
        apply_layout.addWidget(self.apply_btn)

        self.reset_btn = QPushButton("Reset Pose")
        self.reset_btn.clicked.connect(self.reset_pose)
        self.reset_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """
        )
        apply_layout.addWidget(self.reset_btn)

        actions_layout.addLayout(apply_layout)

        # Mirror and Export buttons
        mirror_export_layout = QVBoxLayout()

        # Mirror button
        mirror_layout = QHBoxLayout()
        self.mirror_btn = QPushButton("Mirror to Left Hand")
        self.mirror_btn.clicked.connect(self.mirror_to_left_hand)
        self.mirror_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """
        )
        mirror_layout.addWidget(self.mirror_btn)
        mirror_export_layout.addLayout(mirror_layout)

        # Export buttons
        export_layout = QHBoxLayout()

        self.export_right_btn = QPushButton("Export Right Hand")
        self.export_right_btn.clicked.connect(lambda: self.export_pose_to_json("right"))
        self.export_right_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        export_layout.addWidget(self.export_right_btn)

        self.export_left_btn = QPushButton("Export Left Hand")
        self.export_left_btn.clicked.connect(lambda: self.export_pose_to_json("left"))
        self.export_left_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """
        )
        export_layout.addWidget(self.export_left_btn)

        mirror_export_layout.addLayout(export_layout)
        actions_layout.addLayout(mirror_export_layout)
        layout.addWidget(actions_group)

        return panel

    def load_hand_joints(self):
        """Load hand, finger, and arm joints"""
        # Define hand-specific joints
        self.hand_joints = [
            # Arm joints
            "mixamorig:RightShoulder",
            "mixamorig:RightArm",
            "mixamorig:RightForeArm",
            "mixamorig:RightHand",
            # Thumb joints
            "mixamorig:RightHandThumb1",
            "mixamorig:RightHandThumb2",
            "mixamorig:RightHandThumb3",
            "mixamorig:RightHandThumb4",
            # Index finger joints
            "mixamorig:RightHandIndex1",
            "mixamorig:RightHandIndex2",
            "mixamorig:RightHandIndex3",
            "mixamorig:RightHandIndex4",
            # Middle finger joints
            "mixamorig:RightHandMiddle1",
            "mixamorig:RightHandMiddle2",
            "mixamorig:RightHandMiddle3",
            "mixamorig:RightHandMiddle4",
            # Ring finger joints
            "mixamorig:RightHandRing1",
            "mixamorig:RightHandRing2",
            "mixamorig:RightHandRing3",
            "mixamorig:RightHandRing4",
            # Pinky finger joints
            "mixamorig:RightHandPinky1",
            "mixamorig:RightHandPinky2",
            "mixamorig:RightHandPinky3",
            "mixamorig:RightHandPinky4",
        ]

        # Create joint editors
        print(f"Creating {len(self.hand_joints)} joint editors...")
        for joint_name in self.hand_joints:
            try:
                editor = HandJointEditor(joint_name, self)
                self.joint_editors[joint_name] = editor
                self.joints_layout.addWidget(editor)
                print(f"✓ Created editor for {joint_name}")
                print(f"  Editor size: {editor.size()}")
                print(f"  Editor visible: {editor.isVisible()}")
                print(f"  Layout count after adding: {self.joints_layout.count()}")
            except Exception as e:
                print(f"✗ Failed to create editor for {joint_name}: {e}")
                import traceback

                traceback.print_exc()

        print(f"Total joint editors created: {len(self.joint_editors)}")
        print(f"Joints layout children: {self.joints_layout.count()}")

    def setup_connections(self):
        """Set up signal connections"""
        self.lang_combo.currentTextChanged.connect(self.on_language_changed)
        self.letter_combo.currentTextChanged.connect(self.on_letter_changed)

        # Connect pose change signals from joint editors
        for editor in self.joint_editors.values():
            if hasattr(editor, "pose_changed"):
                editor.pose_changed.connect(self._on_pose_changed)

    def _on_pose_changed(self, joint_name: str, pose: JointPose):
        """Handle pose changes from joint editors"""
        self.logger.info(
            f"HandPoseEditor: Pose changed for {joint_name}: H={pose.heading}, P={pose.pitch}, R={pose.roll}"
        )
        self.pose_manager.set_pose(joint_name, pose)

        # Apply the change to the 3D character
        self.apply_to_character()

    # Removed load_reference_image method - no longer needed

    # Removed reference image related methods - no longer needed

    def on_language_changed(self, language: str):
        """Handle language selection change"""
        self.current_language = language
        self.reload_pose_data()

    def on_letter_changed(self, letter: str):
        """Handle letter selection change"""
        self.current_letter = letter
        self.reload_pose_data()

    def reload_pose_data(self):
        """Reload pose data from JSON file"""
        self.logger.info("HandPoseEditor: Reload pose data button clicked!")
        try:
            # Load pose data from JSON
            pose_data = self.load_pose_from_json()
            if pose_data:
                # Apply to joint editors
                for joint_name, pose_values in pose_data.items():
                    if joint_name in self.joint_editors:
                        editor = self.joint_editors[joint_name]
                        editor.set_pose_values(pose_values)

                self.logger.info(
                    f"Reloaded pose data for {self.current_language} {self.current_letter}"
                )
            else:
                self.logger.warning("No pose data found")

        except Exception as e:
            self.logger.error(f"Error reloading pose data: {e}")

    def load_pose_from_json(self) -> Dict[str, List[float]]:
        """Load pose data from JSON file"""
        try:
            # Map language to file
            lang_map = {
                "ASL": "asl_right_hand.json",
                "BSL": "bsl_right_hand.json",
                "ISL": "isl_right_hand.json",
                "Auslan": "auslan_right_hand.json",
                "LSF": "lsf_right_hand.json",
                "DGS": "dgs_right_hand.json",
            }

            filename = lang_map.get(self.current_language, "asl_right_hand.json")
            file_path = Path("resources/data/signs/asl") / filename

            if file_path.exists():
                with open(file_path, "r") as f:
                    data = json.load(f)

                if "alphabet" in data and self.current_letter in data["alphabet"]:
                    letter_data = data["alphabet"][self.current_letter]
                    if "pose" in letter_data:
                        return letter_data["pose"]

        except Exception as e:
            self.logger.error(f"Error loading pose from JSON: {e}")

        return {}

    def apply_fist_pose(self):
        """Apply fist pose to all fingers"""
        self.logger.info("HandPoseEditor: Make Fist button clicked!")
        fist_values = {
            # Realistic fist - much more natural angles
            "thumb1": [0, 5, 0],
            "thumb2": [0, 30, 0],
            "thumb3": [0, 45, 0],
            "thumb4": [0, 25, 0],
            "index1": [0, 0, 0],
            "index2": [0, 60, 0],
            "index3": [0, 70, 0],
            "index4": [0, 30, 0],
            "middle1": [0, 0, 0],
            "middle2": [0, 60, 0],
            "middle3": [0, 70, 0],
            "middle4": [0, 30, 0],
            "ring1": [0, 5, 0],
            "ring2": [0, 60, 0],
            "ring3": [0, 70, 0],
            "ring4": [0, 30, 0],
            "pinky1": [0, 0, 0],
            "pinky2": [0, 60, 0],
            "pinky3": [0, 70, 0],
            "pinky4": [0, 30, 0],
        }

        for joint_type, values in fist_values.items():
            joint_name = f"mixamorig:RightHand{joint_type.capitalize()}"
            if joint_name in self.joint_editors:
                self.joint_editors[joint_name].set_pose_values(values)

    def apply_open_pose(self):
        """Apply open hand pose"""
        open_values = {
            "thumb1": [0, 25, 0],
            "thumb2": [0, 0, 0],
            "thumb3": [0, 0, 0],
            "thumb4": [0, 0, 0],
            "index1": [0, 10, 0],
            "index2": [0, 0, 0],
            "index3": [0, 0, 0],
            "index4": [0, 0, 0],
            "middle1": [0, 0, 0],
            "middle2": [0, 0, 0],
            "middle3": [0, 0, 0],
            "middle4": [0, 0, 0],
            "ring1": [0, 30, 0],
            "ring2": [0, 0, 0],
            "ring3": [0, 0, 0],
            "ring4": [0, 0, 0],
            "pinky1": [0, 0, 0],
            "pinky2": [0, 0, 0],
            "pinky3": [0, 0, 0],
            "pinky4": [0, 0, 0],
        }

        for joint_type, values in open_values.items():
            joint_name = f"mixamorig:RightHand{joint_type.capitalize()}"
            if joint_name in self.joint_editors:
                self.joint_editors[joint_name].set_pose_values(values)

    def apply_point_pose(self):
        """Apply pointing pose (index finger extended)"""
        point_values = {
            "thumb1": [0, 25, 0],
            "thumb2": [0, 45, 0],
            "thumb3": [0, 60, 0],
            "thumb4": [0, 30, 0],
            "index1": [0, 10, 0],
            "index2": [0, 0, 0],
            "index3": [0, 0, 0],
            "index4": [0, 0, 0],
            "middle1": [0, 0, 0],
            "middle2": [0, 90, 0],
            "middle3": [0, 90, 0],
            "middle4": [0, 45, 0],
            "ring1": [0, 30, 0],
            "ring2": [0, 90, 0],
            "ring3": [0, 90, 0],
            "ring4": [0, 45, 0],
            "pinky1": [0, 0, 0],
            "pinky2": [0, 90, 0],
            "pinky3": [0, 90, 0],
            "pinky4": [0, 45, 0],
        }

        for joint_type, values in point_values.items():
            joint_name = f"mixamorig:RightHand{joint_type.capitalize()}"
            if joint_name in self.joint_editors:
                self.joint_editors[joint_name].set_pose_values(values)

    def reset_pose(self):
        """Reset pose to neutral"""
        self.logger.info("HandPoseEditor: Reset Pose button clicked!")
        for editor in self.joint_editors.values():
            editor.reset_to_neutral()

    def reset_3d_view(self):
        """Reset 3D view to default"""
        self.logger.info("Reset 3D view")

    def zoom_in(self):
        """Zoom in on 3D view"""
        self.logger.info("Zoom in")

    def zoom_out(self):
        """Zoom out on 3D view"""
        self.logger.info("Zoom out")

    def setup_zoomed_view(self):
        """Setup the 6x zoomed view focused on hip and above"""
        self.logger.info("=== setup_zoomed_view called ===")

        if not self.animate_panel:
            self.logger.warning("No animate_panel available for zoomed view")
            return

        try:
            self.logger.info("Setting up 6x zoomed view for hands and head")

            # Store the original camera and character positions for reset
            # NOTE: This method is deprecated - positions are now captured in capture_original_positions()
            # which uses the editor's own 3D view, not the main window
            self.logger.info(
                "setup_zoomed_view is deprecated - using capture_original_positions instead"
            )

            # Apply initial pose to show current state
            self.apply_to_character()

            self.logger.info("6x zoomed view setup completed")

        except Exception as e:
            self.logger.error(f"Error setting up zoomed view: {e}")

    def apply_to_character(self):
        """Apply current pose to the main window character"""
        # Apply to the main window character
        if (
            hasattr(self, "editor_3d_view")
            and self.editor_3d_view
            and hasattr(self.editor_3d_view, "_actor")
            and self.editor_3d_view._actor
        ):
            self._apply_poses_to_actor(self.editor_3d_view._actor, "main_window")

    def _improve_character_appearance(self):
        """Improve the character's appearance in the editor"""
        try:
            if (
                not hasattr(self.editor_3d_view, "_actor")
                or not self.editor_3d_view._actor
            ):
                return

            actor = self.editor_3d_view._actor

            # Apply enhanced visibility color for better hand gesture visibility
            self.logger.info(
                "Applying enhanced visibility color for better hand gesture visibility"
            )

            # Method 1: Color all geometry nodes with more vibrant colors
            self.logger.info("=== Method 1: Coloring all geometry nodes ===")
            all_geom_nodes = actor.findAllMatches("**/+GeomNode")
            colored_count = 0

            for geom_node in all_geom_nodes:
                try:
                    # Set a more vibrant, warmer skin tone
                    geom_node.setColor(
                        1.0, 0.9, 0.8, 1.0
                    )  # Warmer, more vibrant skin tone
                    colored_count += 1
                except Exception as e:
                    self.logger.debug(f"Could not color geom node: {e}")

            self.logger.info(f"=== Total colored geometry: {colored_count} ===")

            # Method 2: Color specific body parts for better visibility
            self.logger.info("=== Method 2: Coloring specific body parts ===")
            body_parts = [
                "mixamorig:Head",
                "mixamorig:LeftShoulder",
                "mixamorig:RightShoulder",
                "mixamorig:Hips",
                "mixamorig:LeftHand",
                "mixamorig:RightHand",
            ]

            for part_name in body_parts:
                try:
                    part_node = actor.find("**/" + part_name)
                    if part_node:
                        part_node.setColor(
                            1.0, 0.9, 0.8, 1.0
                        )  # Warmer, more vibrant skin tone
                        self.logger.info(f"  ✓ Colored {part_name} part: {part_name}")
                except Exception as e:
                    self.logger.debug(f"Could not color {part_name}: {e}")

            # Improve lighting - use the same approach as the main window
            try:
                # Get the render node from the editor's 3D view
                render_node = None
                if (
                    hasattr(self.editor_3d_view, "_render")
                    and self.editor_3d_view._render
                ):
                    render_node = self.editor_3d_view._render
                elif (
                    hasattr(self.editor_3d_view, "render")
                    and self.editor_3d_view.render
                ):
                    render_node = self.editor_3d_view.render
                elif (
                    hasattr(self.editor_3d_view, "_display")
                    and self.editor_3d_view._display
                ):
                    render_node = self.editor_3d_view._display

                if render_node:
                    # Clear existing lights
                    render_node.clearLight()

                    # Create ambient light
                    from panda3d.core import AmbientLight

                    ambient_light = AmbientLight("ambient_light")
                    ambient_light.setColor((0.4, 0.4, 0.4, 1.0))
                    ambient_light_np = render_node.attachNewNode(ambient_light)
                    render_node.setLight(ambient_light_np)

                    # Create directional light
                    from panda3d.core import DirectionalLight

                    directional_light = DirectionalLight("directional_light")
                    directional_light.setColor((0.8, 0.8, 0.8, 1.0))
                    directional_light_np = render_node.attachNewNode(directional_light)
                    directional_light_np.setHpr(45, -30, 0)
                    render_node.setLight(directional_light_np)

                    # Create additional fill light
                    fill_light = DirectionalLight("fill_light")
                    fill_light.setColor((0.3, 0.3, 0.4, 1.0))
                    fill_light_np = render_node.attachNewNode(fill_light)
                    fill_light_np.setHpr(-45, -20, 0)
                    render_node.setLight(fill_light_np)

                    self.logger.info("Applied improved lighting to editor character")
                else:
                    self.logger.warning("Could not find render node for lighting")

            except Exception as e:
                self.logger.debug(f"Could not improve lighting: {e}")

            self.logger.info("Character appearance improved successfully")

        except Exception as e:
            self.logger.error(f"Error improving character appearance: {e}")

    def _setup_independent_pose_control(self):
        """Setup independent pose control for the Hand Pose Editor"""
        try:
            # Store the original pose of the main window's character
            self._store_original_main_window_pose()

            # Apply neutral pose to the main window's character for editing
            self._apply_neutral_pose_to_main_window()

            self.logger.info(
                "Setup independent pose control - main window character ready for editing"
            )

        except Exception as e:
            self.logger.error(f"Error setting up independent pose control: {e}")

    def _store_original_main_window_pose(self):
        """Store the original pose of the main window's character"""
        try:
            if (
                not hasattr(self.animate_panel, "_actor")
                or not self.animate_panel._actor
            ):
                self.logger.warning("Main window actor not available for pose storage")
                return

            self.original_main_window_pose = {}

            for joint_name in self.hand_joints:
                try:
                    joint = self.animate_panel._actor.controlJoint(
                        None, "modelRoot", joint_name
                    )
                    if joint:
                        hpr = joint.getHpr()
                        self.original_main_window_pose[joint_name] = {
                            "heading": hpr[0],
                            "pitch": hpr[1],
                            "roll": hpr[2],
                        }
                        self.logger.debug(
                            f"Stored original pose for {joint_name}: H={hpr[0]:.1f}, P={hpr[1]:.1f}, R={hpr[2]:.1f}"
                        )
                except Exception as e:
                    self.logger.debug(
                        f"Could not store original pose for joint {joint_name}: {e}"
                    )

            self.logger.info(
                f"Stored original pose for {len(self.original_main_window_pose)} hand joints"
            )

        except Exception as e:
            self.logger.error(f"Error storing original main window pose: {e}")

    def _apply_neutral_pose_to_main_window(self):
        """Apply neutral pose to the main window's character for editing"""
        try:
            if (
                not hasattr(self.animate_panel, "_actor")
                or not self.animate_panel._actor
            ):
                self.logger.warning("Main window actor not available for neutral pose")
                return

            neutral_poses = 0
            for joint_name in self.hand_joints:
                try:
                    joint = self.animate_panel._actor.controlJoint(
                        None, "modelRoot", joint_name
                    )
                    if joint:
                        # Apply neutral pose (0, 0, 0) for all hand joints
                        joint.setHpr(0.0, 0.0, 0.0)
                        neutral_poses += 1

                        # Also update the pose manager
                        pose = JointPose(joint_name, 0.0, 0.0, 0.0)
                        self.pose_manager.set_pose(joint_name, pose)

                except Exception as e:
                    self.logger.debug(
                        f"Could not apply neutral pose to joint {joint_name}: {e}"
                    )

            # Update the actor to render changes
            self.animate_panel._actor.update()
            self.logger.info(
                f"Applied neutral pose to {neutral_poses} hand joints in main window"
            )

        except Exception as e:
            self.logger.error(f"Error applying neutral pose to main window: {e}")

    def _restore_original_main_window_pose(self):
        """Restore the original pose of the main window's character"""
        try:
            if (
                not hasattr(self, "original_main_window_pose")
                or not self.original_main_window_pose
            ):
                self.logger.warning("No original pose stored to restore")
                return

            if (
                not hasattr(self.animate_panel, "_actor")
                or not self.animate_panel._actor
            ):
                self.logger.warning(
                    "Main window actor not available for pose restoration"
                )
                return

            restored_count = 0
            for joint_name, pose_data in self.original_main_window_pose.items():
                try:
                    joint = self.animate_panel._actor.controlJoint(
                        None, "modelRoot", joint_name
                    )
                    if joint:
                        joint.setHpr(
                            pose_data["heading"], pose_data["pitch"], pose_data["roll"]
                        )
                        restored_count += 1
                        self.logger.debug(
                            f"Restored original pose for {joint_name}: H={pose_data['heading']:.1f}, P={pose_data['pitch']:.1f}, R={pose_data['roll']:.1f}"
                        )
                except Exception as e:
                    self.logger.debug(
                        f"Could not restore original pose for joint {joint_name}: {e}"
                    )

            # Update the actor to render changes
            self.animate_panel._actor.update()
            self.logger.info(
                f"Restored original pose for {restored_count} hand joints in main window"
            )

        except Exception as e:
            self.logger.error(f"Error restoring original main window pose: {e}")

    def _restore_main_window_natural_pose(self):
        """Restore the main window's character to its natural pose when Hand Pose Editor closes"""
        try:
            if not hasattr(self, "animate_panel") or not self.animate_panel:
                self.logger.warning(
                    "No animate_panel available for restoring natural pose"
                )
                return

            if (
                not hasattr(self.animate_panel, "_actor")
                or not self.animate_panel._actor
            ):
                self.logger.warning(
                    "Main window actor not available for restoring natural pose"
                )
                return

            # Apply natural pose to the main window's character
            restored_count = 0
            for joint_name in self.hand_joints:
                try:
                    joint = self.animate_panel._actor.controlJoint(
                        None, "modelRoot", joint_name
                    )
                    if joint:
                        # Apply natural pose (0, 0, 0) for all hand joints
                        joint.setHpr(0.0, 0.0, 0.0)
                        restored_count += 1
                except Exception as e:
                    self.logger.error(
                        f"Error restoring natural pose to joint {joint_name}: {e}"
                    )

            # Update the actor to render the changes
            self.animate_panel._actor.update()

            self.logger.info(
                f"Restored natural pose for {restored_count} hand joints in main window"
            )

        except Exception as e:
            self.logger.error(f"Error restoring main window natural pose: {e}")

    def _apply_neutral_pose_to_editor(self):
        """Apply neutral T-pose to main window character for editing"""
        try:
            if (
                not hasattr(self.editor_3d_view, "_actor")
                or not self.editor_3d_view._actor
            ):
                self.logger.warning("Character actor not available for neutral pose")
                return

            # Apply neutral pose to the main window character
            neutral_poses = 0
            for joint_name in self.hand_joints:
                try:
                    joint = self.editor_3d_view._actor.controlJoint(
                        None, "modelRoot", joint_name
                    )
                    if joint:
                        # Apply neutral pose (0, 0, 0) for all hand joints
                        joint.setHpr(0.0, 0.0, 0.0)
                        neutral_poses += 1

                        # Also update the pose manager
                        pose = JointPose(joint_name, 0.0, 0.0, 0.0)
                        self.pose_manager.set_pose(joint_name, pose)

                except Exception as e:
                    self.logger.debug(
                        f"Could not apply neutral pose to joint {joint_name}: {e}"
                    )

            # Update the actor to render changes
            self.animate_panel._actor.update()
            self.logger.info(
                f"Applied neutral pose to {neutral_poses} hand joints in main window character"
            )

        except Exception as e:
            self.logger.error(f"Error applying neutral pose to editor: {e}")

        # def _copy_pose_to_editor(self):
        #     """DEPRECATED: Hand Pose Editor should be independent from main window"""
        #     return  # Disabled - Hand Pose Editor should be independent
        #             "mixamorig:RightShoulder",
        #             "mixamorig:RightArm",
        #             "mixamorig:RightForeArm",
        #             "mixamorig:RightHand",
        #             "mixamorig:RightHandThumb1",
        #             "mixamorig:RightHandThumb2",
        #             "mixamorig:RightHandThumb3",
        #             "mixamorig:RightHandThumb4",
        #             "mixamorig:RightHandIndex1",
        #             "mixamorig:RightHandIndex2",
        #             "mixamorig:RightHandIndex3",
        #             "mixamorig:RightHandIndex4",
        #             "mixamorig:RightHandMiddle1",
        #             "mixamorig:RightHandMiddle2",
        #             "mixamorig:RightHandMiddle3",
        #             "mixamorig:RightHandMiddle4",
        #             "mixamorig:RightHandRing1",
        #             "mixamorig:RightHandRing2",
        #             "mixamorig:RightHandRing3",
        #             "mixamorig:RightHandRing4",
        #             "mixamorig:RightHandPinky1",
        #             "mixamorig:RightHandPinky2",
        #             "mixamorig:RightHandPinky3",
        #             "mixamorig:RightHandPinky4",
        #             "mixamorig:LeftShoulder",
        #             "mixamorig:LeftArm",
        #             "mixamorig:LeftForeArm",
        #             "mixamorig:LeftHand",
        #             "mixamorig:LeftHandThumb1",
        #             "mixamorig:LeftHandThumb2",
        #             "mixamorig:LeftHandThumb3",
        #             "mixamorig:LeftHandThumb4",
        #             "mixamorig:LeftHandIndex1",
        #             "mixamorig:LeftHandIndex2",
        #             "mixamorig:LeftHandIndex3",
        #             "mixamorig:LeftHandIndex4",
        #             "mixamorig:LeftHandMiddle1",
        #             "mixamorig:LeftHandMiddle2",
        #             "mixamorig:LeftHandMiddle3",
        #             "mixamorig:LeftHandMiddle4",
        #             "mixamorig:LeftHandRing1",
        #             "mixamorig:LeftHandRing2",
        #             "mixamorig:LeftHandRing3",
        #             "mixamorig:LeftHandRing4",
        #             "mixamorig:LeftHandPinky1",
        #             "mixamorig:LeftHandPinky2",
        #             "mixamorig:LeftHandPinky3",
        #             "mixamorig:LeftHandPinky4",
        #         ]

        #         copied_count = 0
        #         for joint_name in all_joints:
        #             try:
        #                 # Get joint from main window
        #                 main_joint = self.animate_panel._actor.controlJoint(
        #                     None, "modelRoot", joint_name
        #                 )
        #                 if main_joint:
        #                     # Get current HPR from main window
        #                     hpr = main_joint.getHpr()

        #                     # Apply to editor's joint
        #                     editor_joint = self.editor_3d_view._actor.controlJoint(
        #                         None, "modelRoot", joint_name
        #                     )
        #                     if editor_joint:
        #                         editor_joint.setHpr(hpr)
        #                         copied_count += 1

        #                         # Also update the pose manager for hand joints
        #                         if joint_name in self.hand_joints:
        #                             from src.helpmesign.modes.learn.hpr_editor import (
        #                                 JointPose,
        #                             )

        #                             pose = JointPose(
        #                                 joint_name=joint_name,
        #                                 heading=hpr[0],
        #                                 pitch=hpr[1],
        #                                 roll=hpr[2],
        #                             )
        #                             self.pose_manager.set_pose(joint_name, pose)

        #             except Exception as e:
        #                 self.logger.debug(
        #                     f"Could not copy pose for joint {joint_name}: {e}"
        #                 )

        #         self.editor_3d_view._actor.update()
        #         self.logger.info(
        #             f"Copied {copied_count} joint poses from main window to Hand Pose Editor"
        #         )

        #     except Exception as e:
        #         self.logger.error(f"Error copying pose to editor: {e}")

        # def _apply_current_pose_to_editor(self):
        #     """Apply the current pose from pose manager to the editor's character"""
        #     try:
        #         if (
        #             not hasattr(self.editor_3d_view, "_actor")
        #             or not self.editor_3d_view._actor
        #         ):
        #             return

        #         # Get all current poses from the pose manager
        #         all_poses = self.pose_manager.get_all_poses()

        #         if not all_poses:
        #             # If no poses in manager, apply neutral pose
        #             self._apply_neutral_pose_to_editor()
        #             return

        #         # Apply each pose to the editor's actor
        #         applied_count = 0
        #         for joint_name, pose in all_poses.items():
        #             try:
        #                 joint = self.editor_3d_view._actor.controlJoint(
        #                     None, "modelRoot", joint_name
        #                 )
        #                 if joint:
        #                     joint.setHpr(pose.heading, pose.pitch, pose.roll)
        #                     applied_count += 1
        #             except Exception as e:
        #                 self.logger.debug(
        #                     f"Could not apply pose for joint {joint_name}: {e}"
        #                 )

        #         self.editor_3d_view._actor.update()
        #         self.logger.info(
        #             f"Applied {applied_count} poses from pose manager to editor character"
        #         )

        #     except Exception as e:
        #         self.logger.error(f"Error applying current pose to editor: {e}")

        # def _apply_neutral_pose_to_editor(self):
        """Apply neutral pose to the editor's character"""
        try:
            if (
                not hasattr(self.editor_3d_view, "_actor")
                or not self.editor_3d_view._actor
            ):
                return

            # Apply natural pose using the natural pose service
            from src.helpmesign.utils.natural_pose_service import NaturalPoseService

            natural_pose_service = NaturalPoseService()
            natural_pose_data = natural_pose_service.get_natural_pose_data()

            applied_count = 0
            for joint_name, pose_data in natural_pose_data.items():
                try:
                    joint = self.editor_3d_view._actor.controlJoint(
                        None, "modelRoot", joint_name
                    )
                    if joint:
                        hpr = pose_data["hpr"]
                        joint.setHpr(hpr[0], hpr[1], hpr[2])
                        applied_count += 1
                except Exception as e:
                    self.logger.debug(
                        f"Could not apply neutral pose for joint {joint_name}: {e}"
                    )

            self.editor_3d_view._actor.update()
            self.logger.info(
                f"Applied neutral pose with {applied_count} joints to editor character"
            )

        except Exception as e:
            self.logger.error(f"Error applying neutral pose to editor: {e}")

    def _apply_poses_to_actor(self, actor, location="unknown"):
        """Apply poses to a specific actor"""
        try:
            if actor is None:
                self.logger.warning(f"No actor available for {location}")
                return

            # Apply poses for hand-related joints only
            hand_joints = [
                "mixamorig:RightShoulder",
                "mixamorig:RightArm",
                "mixamorig:RightForeArm",
                "mixamorig:RightHand",
                "mixamorig:RightHandThumb1",
                "mixamorig:RightHandThumb2",
                "mixamorig:RightHandThumb3",
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
                "mixamorig:LeftShoulder",
                "mixamorig:LeftArm",
                "mixamorig:LeftForeArm",
                "mixamorig:LeftHand",
                "mixamorig:LeftHandThumb1",
                "mixamorig:LeftHandThumb2",
                "mixamorig:LeftHandThumb3",
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
            ]

            applied_count = 0
            for joint_name in hand_joints:
                pose = self.pose_manager.get_pose(joint_name)
                if pose:
                    joint = actor.controlJoint(None, "modelRoot", joint_name)
                    if joint is not None:
                        joint.setHpr(pose.heading, pose.pitch, pose.roll)
                        applied_count += 1

            actor.update()
            self.logger.debug(f"Applied {applied_count} hand poses to {location}")

        except Exception as e:
            self.logger.error(f"Error applying poses to {location}: {e}")

    def mirror_to_left_hand(self):
        """Mirror right hand pose to left hand"""
        try:
            # Define right to left hand joint mapping
            right_to_left_mapping = {
                "mixamorig:RightShoulder": "mixamorig:LeftShoulder",
                "mixamorig:RightArm": "mixamorig:LeftArm",
                "mixamorig:RightForeArm": "mixamorig:LeftForeArm",
                "mixamorig:RightHand": "mixamorig:LeftHand",
                "mixamorig:RightHandThumb1": "mixamorig:LeftHandThumb1",
                "mixamorig:RightHandThumb2": "mixamorig:LeftHandThumb2",
                "mixamorig:RightHandThumb3": "mixamorig:LeftHandThumb3",
                "mixamorig:RightHandIndex1": "mixamorig:LeftHandIndex1",
                "mixamorig:RightHandIndex2": "mixamorig:LeftHandIndex2",
                "mixamorig:RightHandIndex3": "mixamorig:LeftHandIndex3",
                "mixamorig:RightHandMiddle1": "mixamorig:LeftHandMiddle1",
                "mixamorig:RightHandMiddle2": "mixamorig:LeftHandMiddle2",
                "mixamorig:RightHandMiddle3": "mixamorig:LeftHandMiddle3",
                "mixamorig:RightHandRing1": "mixamorig:LeftHandRing1",
                "mixamorig:RightHandRing2": "mixamorig:LeftHandRing2",
                "mixamorig:RightHandRing3": "mixamorig:LeftHandRing3",
                "mixamorig:RightHandPinky1": "mixamorig:LeftHandPinky1",
                "mixamorig:RightHandPinky2": "mixamorig:LeftHandPinky2",
                "mixamorig:RightHandPinky3": "mixamorig:LeftHandPinky3",
            }

            # Get all current poses
            all_poses = self.pose_manager.get_all_poses()
            mirrored_count = 0

            # Mirror each right hand joint to left hand
            for right_joint, left_joint in right_to_left_mapping.items():
                if right_joint in all_poses:
                    right_pose = all_poses[right_joint]

                    # Mirror the pose (flip heading for left/right symmetry)
                    mirrored_pose = JointPose(
                        joint_name=left_joint,
                        heading=-right_pose.heading,  # Flip heading for mirroring
                        pitch=right_pose.pitch,  # Keep pitch the same
                        roll=-right_pose.roll,  # Flip roll for mirroring
                    )

                    # Set the mirrored pose
                    self.pose_manager.set_pose(left_joint, mirrored_pose)
                    mirrored_count += 1

                    # Update the joint editor if it exists
                    if left_joint in self.joint_editors:
                        editor = self.joint_editors[left_joint]
                        editor.set_pose(mirrored_pose)

            # Apply the mirrored poses to the character
            self.apply_to_character()

            self.logger.info(
                f"Mirrored {mirrored_count} joints from right to left hand"
            )

            from PySide6.QtWidgets import QMessageBox

            QMessageBox.information(
                self,
                "Mirror Complete",
                f"Successfully mirrored {mirrored_count} joints from right hand to left hand.\n\nNote: Heading and roll values are flipped for proper left/right symmetry.",
            )

        except Exception as e:
            self.logger.error(f"Error mirroring pose: {e}")
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.critical(
                self, "Mirror Error", f"Failed to mirror pose:\n{str(e)}"
            )

    def export_pose_to_json(self, hand="both"):
        """Export current pose to JSON file"""
        try:
            import json
            from datetime import datetime

            from PySide6.QtWidgets import QFileDialog, QMessageBox

            # Get all poses from the pose manager
            all_poses = self.pose_manager.get_all_poses()

            if not all_poses:
                QMessageBox.warning(
                    self,
                    "No Pose Data",
                    "No pose data to export. Please adjust some joints first.",
                )
                return

            # Filter poses based on hand selection
            filtered_poses = {}
            if hand == "right":
                # Only right hand joints
                for joint_name, pose in all_poses.items():
                    if "Right" in joint_name:
                        filtered_poses[joint_name] = pose
            elif hand == "left":
                # Only left hand joints
                for joint_name, pose in all_poses.items():
                    if "Left" in joint_name:
                        filtered_poses[joint_name] = pose
            else:
                # Both hands (default)
                filtered_poses = all_poses

            if not filtered_poses:
                QMessageBox.warning(
                    self,
                    "No Hand Data",
                    f"No {hand} hand pose data to export. Please adjust some joints first.",
                )
                return

            # Create export data structure
            hand_description = (
                f"{hand.capitalize()} hand" if hand != "both" else "Both hands"
            )
            export_data = {
                "metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "language": self.current_language,
                    "letter": self.current_letter,
                    "hand": hand,
                    "total_joints": len(filtered_poses),
                    "description": f"{hand_description} pose for {self.current_language} letter {self.current_letter}",
                },
                "pose": {},
            }

            # Convert poses to the expected format
            for joint_name, pose in filtered_poses.items():
                export_data["pose"][joint_name] = [pose.heading, pose.pitch, pose.roll]

            # Ask user for save location
            filename = (
                f"{self.current_language}_{self.current_letter}_{hand}_hand_pose.json"
            )
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                f"Export {hand.capitalize()} Hand Pose to JSON",
                filename,
                "JSON Files (*.json);;All Files (*)",
            )

            if file_path:
                # Write to file
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

                self.logger.info(f"Exported {hand} hand pose to: {file_path}")
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"{hand.capitalize()} hand pose exported successfully to:\n{file_path}\n\nJoints exported: {len(filtered_poses)}",
                )
            else:
                self.logger.info("Export cancelled by user")

        except Exception as e:
            self.logger.error(f"Error exporting pose: {e}")
            QMessageBox.critical(
                self, "Export Error", f"Failed to export pose:\n{str(e)}"
            )

    def update_camera_position(self):
        """Update camera position based on slider values - works on editor's camera"""
        # Update the editor's own camera
        if (
            not hasattr(self, "editor_3d_view")
            or not self.editor_3d_view
            or not hasattr(self.editor_3d_view, "_camera")
        ):
            return

        try:
            camera = self.editor_3d_view._camera
            # Convert slider values to position increments
            x = self.camera_x_slider.value() * POSITION_INCREMENT
            y = self.camera_y_slider.value() * POSITION_INCREMENT
            z = self.camera_z_slider.value() * POSITION_INCREMENT

            camera.setPos(x, y, z)

            # Update labels with decimal values
            self.camera_x_label.setText(f"{x:.2f}")
            self.camera_y_label.setText(f"{y:.2f}")
            self.camera_z_label.setText(f"{z:.2f}")

            self.logger.info(
                f"Updated editor camera position: ({x:.2f}, {y:.2f}, {z:.2f})"
            )

        except Exception as e:
            self.logger.error(f"Error updating editor camera position: {e}")

    def update_character_position(self):
        """Update character position based on slider values - works on editor's character"""
        # Update the editor's own character
        if (
            not hasattr(self, "editor_3d_view")
            or not self.editor_3d_view
            or not hasattr(self.editor_3d_view, "_model_np")
        ):
            return

        try:
            model_np = self.editor_3d_view._model_np
            # Convert slider values to position increments
            x = self.char_x_slider.value() * POSITION_INCREMENT
            y = self.char_y_slider.value() * POSITION_INCREMENT
            z = self.char_z_slider.value() * POSITION_INCREMENT

            model_np.setPos(x, y, z)

            # Update labels with decimal values
            self.char_x_label.setText(f"{x:.2f}")
            self.char_y_label.setText(f"{y:.2f}")
            self.char_z_label.setText(f"{z:.2f}")

            self.logger.info(
                f"Updated editor character position: ({x:.2f}, {y:.2f}, {z:.2f})"
            )

        except Exception as e:
            self.logger.error(f"Error updating editor character position: {e}")

    def reset_camera_position(self):
        """Reset camera and character to original positions - works on editor 3D view only"""
        try:
            # Check if we have stored original positions
            if hasattr(self, "original_camera_pos") and hasattr(
                self, "original_character_pos"
            ):
                self.logger.info(f"Resetting editor to original positions:")
                self.logger.info(f"  Original camera: {self.original_camera_pos}")
                self.logger.info(f"  Original character: {self.original_character_pos}")

                # Apply the exact original positions directly to editor's 3D view
                if (
                    hasattr(self, "editor_3d_view")
                    and self.editor_3d_view
                    and hasattr(self.editor_3d_view, "_camera")
                    and self.editor_3d_view._camera
                ):
                    camera = self.editor_3d_view._camera
                    camera.setPos(
                        self.original_camera_pos.x,
                        self.original_camera_pos.y,
                        self.original_camera_pos.z,
                    )
                    self.logger.info(
                        f"Set editor camera to exact original position: {self.original_camera_pos}"
                    )

                if (
                    hasattr(self, "editor_3d_view")
                    and self.editor_3d_view
                    and hasattr(self.editor_3d_view, "_model_np")
                    and self.editor_3d_view._model_np
                ):
                    model_np = self.editor_3d_view._model_np
                    model_np.setPos(
                        self.original_character_pos.x,
                        self.original_character_pos.y,
                        self.original_character_pos.z,
                    )
                    self.logger.info(
                        f"Set editor character to exact original position: {self.original_character_pos}"
                    )

                # Update sliders to match the exact positions (convert to position increments)
                self.camera_x_slider.setValue(
                    int(round(self.original_camera_pos.x / POSITION_INCREMENT))
                )
                self.camera_y_slider.setValue(
                    int(round(self.original_camera_pos.y / POSITION_INCREMENT))
                )
                self.camera_z_slider.setValue(
                    int(round(self.original_camera_pos.z / POSITION_INCREMENT))
                )

                self.char_x_slider.setValue(
                    int(round(self.original_character_pos.x / POSITION_INCREMENT))
                )
                self.char_y_slider.setValue(
                    int(round(self.original_character_pos.y / POSITION_INCREMENT))
                )
                self.char_z_slider.setValue(
                    int(round(self.original_character_pos.z / POSITION_INCREMENT))
                )

                # Update the labels with decimal values
                self.camera_x_label.setText(f"{self.original_camera_pos.x:.2f}")
                self.camera_y_label.setText(f"{self.original_camera_pos.y:.2f}")
                self.camera_z_label.setText(f"{self.original_camera_pos.z:.2f}")

                self.char_x_label.setText(f"{self.original_character_pos.x:.2f}")
                self.char_y_label.setText(f"{self.original_character_pos.y:.2f}")
                self.char_z_label.setText(f"{self.original_character_pos.z:.2f}")

                self.logger.info(
                    "Reset editor camera and character positions to exact original values"
                )
            else:
                self.logger.warning("No original positions stored, cannot reset")

        except Exception as e:
            self.logger.error(f"Error resetting editor camera position: {e}")

    def reset_character_orientation(self):
        """Reset character to neutral orientation and position - works on editor character"""
        try:
            if (
                not hasattr(self, "editor_3d_view")
                or not self.editor_3d_view
                or not hasattr(self.editor_3d_view, "_model_np")
                or not self.editor_3d_view._model_np
            ):
                self.logger.warning("Editor character model not available for reset")
                return

            model_np = self.editor_3d_view._model_np

            # Reset character to neutral position and orientation
            model_np.setPos(0, 0, 0)
            model_np.setHpr(0, 0, 0)  # Reset heading, pitch, roll to 0
            model_np.setScale(1, 1, 1)  # Reset scale to 1:1:1

            # Reset character sliders to center
            self.char_x_slider.setValue(0)
            self.char_y_slider.setValue(0)
            self.char_z_slider.setValue(0)

            # Update labels
            self.char_x_label.setText("0.00")
            self.char_y_label.setText("0.00")
            self.char_z_label.setText("0.00")

            # Reset character to neutral pose if actor is available
            if hasattr(self.editor_3d_view, "_actor") and self.editor_3d_view._actor:
                try:
                    # Stop any animations
                    self.editor_3d_view._actor.stop()

                    # Apply neutral pose
                    from src.helpmesign.utils.natural_pose_service import (
                        NaturalPoseService,
                    )

                    natural_pose_service = NaturalPoseService()
                    natural_pose_data = natural_pose_service.get_natural_pose_data()

                    # Apply natural pose to each joint
                    for joint_name, pose_data in natural_pose_data.items():
                        try:
                            joint = self.editor_3d_view._actor.controlJoint(
                                None, "modelRoot", joint_name
                            )
                            if joint:
                                hpr = pose_data["hpr"]
                                joint.setHpr(hpr[0], hpr[1], hpr[2])
                        except Exception as joint_error:
                            self.logger.debug(
                                f"Could not reset joint {joint_name}: {joint_error}"
                            )

                    self.editor_3d_view._actor.update()
                    self.logger.info(
                        "Reset editor character to neutral pose and orientation"
                    )

                except Exception as pose_error:
                    self.logger.warning(
                        f"Could not reset editor character pose: {pose_error}"
                    )

            self.logger.info(
                "Editor character orientation and position reset successfully"
            )

        except Exception as e:
            self.logger.error(f"Error resetting editor character orientation: {e}")

    def showEvent(self, event):
        """Called when the window is shown - capture original positions after model is loaded"""
        super().showEvent(event)
        # Use a timer to delay capturing positions until after the model is fully loaded
        QTimer.singleShot(1000, self.capture_original_positions)

    def capture_original_positions(self):
        """Capture the original camera and character positions from editor's 3D view"""
        try:
            # Capture positions from the editor's own 3D view
            if not hasattr(self, "editor_3d_view") or not self.editor_3d_view:
                self.logger.warning(
                    "No editor_3d_view available for capturing positions"
                )
                return

            # Store the original camera and character positions for reset
            if hasattr(self.editor_3d_view, "_camera") and self.editor_3d_view._camera:
                camera = self.editor_3d_view._camera
                self.original_camera_pos = camera.getPos()
                self.logger.info(
                    f"Captured original editor camera position: {self.original_camera_pos}"
                )

                if (
                    hasattr(self.editor_3d_view, "_model_np")
                    and self.editor_3d_view._model_np
                ):
                    model_np = self.editor_3d_view._model_np
                    self.original_character_pos = model_np.getPos()
                    self.logger.info(
                        f"Captured original editor character position: {self.original_character_pos}"
                    )

                    # Update the slider values to match the original positions (convert to position increments)
                    self.camera_x_slider.setValue(
                        int(round(self.original_camera_pos.x / POSITION_INCREMENT))
                    )
                    self.camera_y_slider.setValue(
                        int(round(self.original_camera_pos.y / POSITION_INCREMENT))
                    )
                    self.camera_z_slider.setValue(
                        int(round(self.original_camera_pos.z / POSITION_INCREMENT))
                    )

                    self.char_x_slider.setValue(
                        int(round(self.original_character_pos.x / POSITION_INCREMENT))
                    )
                    self.char_y_slider.setValue(
                        int(round(self.original_character_pos.y / POSITION_INCREMENT))
                    )
                    self.char_z_slider.setValue(
                        int(round(self.original_character_pos.z / POSITION_INCREMENT))
                    )

                    # Update the labels with decimal values
                    self.camera_x_label.setText(f"{self.original_camera_pos.x:.2f}")
                    self.camera_y_label.setText(f"{self.original_camera_pos.y:.2f}")
                    self.camera_z_label.setText(f"{self.original_camera_pos.z:.2f}")

                    self.char_x_label.setText(f"{self.original_character_pos.x:.2f}")
                    self.char_y_label.setText(f"{self.original_character_pos.y:.2f}")
                    self.char_z_label.setText(f"{self.original_character_pos.z:.2f}")

                    self.logger.info(
                        "Updated sliders to match captured original editor positions"
                    )
                else:
                    self.logger.warning(
                        "Editor model node not available for capturing positions"
                    )
            else:
                self.logger.warning(
                    "Editor camera not available for capturing positions"
                )

        except Exception as e:
            self.logger.error(f"Error capturing original editor positions: {e}")


class HandJointEditor(QWidget):
    """Individual joint editor for hand joints"""

    # Define signals
    pose_changed = Signal(str, object)  # joint_name, pose

    def __init__(self, joint_name: str, parent=None):
        super().__init__(parent)
        self.joint_name = joint_name
        self.logger = logging.getLogger("helpmesign")
        print(f"HandJointEditor: Creating editor for joint: {joint_name}")
        try:
            self.setup_ui()
            print(f"✓ HandJointEditor setup completed for {joint_name}")
        except Exception as e:
            print(f"✗ HandJointEditor setup failed for {joint_name}: {e}")
            import traceback

            traceback.print_exc()
            raise

    def setup_ui(self):
        """Set up the joint editor UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)

        # Joint name label
        name_label = QLabel(self.get_display_name())
        name_label.setMinimumWidth(120)
        name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(name_label)

        # H, P, R sliders and spinboxes
        self.h_slider_group = self.create_slider_group("H", -180, 180)
        self.p_slider_group = self.create_slider_group("P", -180, 180)
        self.r_slider_group = self.create_slider_group("R", -180, 180)

        layout.addWidget(self.h_slider_group)
        layout.addWidget(self.p_slider_group)
        layout.addWidget(self.r_slider_group)

    def create_slider_group(self, label: str, min_val: int, max_val: int) -> QWidget:
        """Create a slider group with label, slider, and spinbox"""
        group = QWidget()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(2, 0, 2, 0)

        # Label
        label_widget = QLabel(label)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_widget.setStyleSheet("font-weight: bold; color: #7f8c8d;")
        layout.addWidget(label_widget)

        # Slider
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val * 10, max_val * 10)
        slider.setValue(0)
        slider.valueChanged.connect(self.on_slider_changed)
        self.logger.info(
            f"HandJointEditor: Connected slider {label} to on_slider_changed"
        )
        layout.addWidget(slider)

        # Spinbox
        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(0)
        spinbox.valueChanged.connect(self.on_spinbox_changed)
        self.logger.info(
            f"HandJointEditor: Connected spinbox {label} to on_spinbox_changed"
        )
        layout.addWidget(spinbox)

        # Store references
        setattr(self, f"{label.lower()}_slider", slider)
        setattr(self, f"{label.lower()}_spinbox", spinbox)

        return group

    def on_slider_changed(self, value):
        """Handle slider value change"""
        self.logger.info(f"HandJointEditor: Slider changed to value: {value}")
        # Convert slider value back to actual value
        actual_value = value / 10.0
        # Update corresponding spinbox
        if hasattr(self, "h_slider") and hasattr(self, "h_spinbox"):
            if self.sender() == self.h_slider:
                self.h_spinbox.setValue(int(actual_value))
        if hasattr(self, "p_slider") and hasattr(self, "p_spinbox"):
            if self.sender() == self.p_slider:
                self.p_spinbox.setValue(int(actual_value))
        if hasattr(self, "r_slider") and hasattr(self, "r_spinbox"):
            if self.sender() == self.r_slider:
                self.r_spinbox.setValue(int(actual_value))

        self.emit_pose_changed()

    def on_spinbox_changed(self, value):
        """Handle spinbox value change"""
        self.logger.info(f"HandJointEditor: Spinbox changed to value: {value}")
        # Update corresponding slider
        if hasattr(self, "h_slider") and hasattr(self, "h_spinbox"):
            if self.sender() == self.h_spinbox:
                self.h_slider.setValue(value * 10)
        if hasattr(self, "p_slider") and hasattr(self, "p_spinbox"):
            if self.sender() == self.p_spinbox:
                self.p_slider.setValue(value * 10)
        if hasattr(self, "r_slider") and hasattr(self, "r_spinbox"):
            if self.sender() == self.r_spinbox:
                self.r_slider.setValue(value * 10)

        self.logger.info(f"HandJointEditor: About to emit pose changed from spinbox")
        self.emit_pose_changed()

    def emit_pose_changed(self):
        """Emit pose changed signal"""
        self.logger.info(
            f"HandJointEditor: emit_pose_changed called for {self.joint_name}"
        )
        try:
            from src.helpmesign.modes.learn.hpr_editor import JointPose

            pose = JointPose(
                joint_name=self.joint_name,
                heading=self.h_spinbox.value() if hasattr(self, "h_spinbox") else 0,
                pitch=self.p_spinbox.value() if hasattr(self, "p_spinbox") else 0,
                roll=self.r_spinbox.value() if hasattr(self, "r_spinbox") else 0,
            )
            self.logger.info(
                f"HandJointEditor: Emitting pose changed for {self.joint_name}: H={pose.heading}, P={pose.pitch}, R={pose.roll}"
            )
            self.pose_changed.emit(self.joint_name, pose)
        except Exception as e:
            self.logger.error(f"Error emitting pose changed: {e}")
            import traceback

            self.logger.error(f"Traceback: {traceback.format_exc()}")

    def get_display_name(self) -> str:
        """Get display name for joint"""
        name_map = {
            "mixamorig:RightShoulder": "Right Shoulder",
            "mixamorig:RightArm": "Right Arm",
            "mixamorig:RightForeArm": "Right Forearm",
            "mixamorig:RightHand": "Right Hand",
            "mixamorig:RightHandThumb1": "Thumb 1",
            "mixamorig:RightHandThumb2": "Thumb 2",
            "mixamorig:RightHandThumb3": "Thumb 3",
            "mixamorig:RightHandThumb4": "Thumb 4",
            "mixamorig:RightHandIndex1": "Index 1",
            "mixamorig:RightHandIndex2": "Index 2",
            "mixamorig:RightHandIndex3": "Index 3",
            "mixamorig:RightHandIndex4": "Index 4",
            "mixamorig:RightHandMiddle1": "Middle 1",
            "mixamorig:RightHandMiddle2": "Middle 2",
            "mixamorig:RightHandMiddle3": "Middle 3",
            "mixamorig:RightHandMiddle4": "Middle 4",
            "mixamorig:RightHandRing1": "Ring 1",
            "mixamorig:RightHandRing2": "Ring 2",
            "mixamorig:RightHandRing3": "Ring 3",
            "mixamorig:RightHandRing4": "Ring 4",
            "mixamorig:RightHandPinky1": "Pinky 1",
            "mixamorig:RightHandPinky2": "Pinky 2",
            "mixamorig:RightHandPinky3": "Pinky 3",
            "mixamorig:RightHandPinky4": "Pinky 4",
        }
        return name_map.get(self.joint_name, self.joint_name)

    def set_pose_values(self, values: List[float]):
        """Set pose values from list [h, p, r]"""
        if len(values) >= 3:
            if hasattr(self, "h_spinbox"):
                self.h_spinbox.setValue(int(values[0]))
            if hasattr(self, "p_spinbox"):
                self.p_spinbox.setValue(int(values[1]))
            if hasattr(self, "r_spinbox"):
                self.r_spinbox.setValue(int(values[2]))

    def get_pose_values(self) -> List[float]:
        """Get current pose values as [h, p, r]"""
        h_val = self.h_spinbox.value() if hasattr(self, "h_spinbox") else 0
        p_val = self.p_spinbox.value() if hasattr(self, "p_spinbox") else 0
        r_val = self.r_spinbox.value() if hasattr(self, "r_spinbox") else 0
        return [h_val, p_val, r_val]

    def reset_to_neutral(self):
        """Reset to neutral pose"""
        self.h_spinbox.setValue(0)
        self.p_spinbox.setValue(0)
        self.r_spinbox.setValue(0)


if __name__ == "__main__":
    # Test the editor
    if PYSIDE6_AVAILABLE:
        import sys

        from PySide6.QtWidgets import QApplication

        app = QApplication(sys.argv)
        # This is a test section - would need proper arguments in real usage
        # editor = HandPoseEditor(animate_panel=None, main_window=None)
        # editor.show()
        sys.exit(app.exec())
    else:
        print("PySide6 not available for testing")
