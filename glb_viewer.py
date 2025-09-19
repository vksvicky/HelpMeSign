#!/usr/bin/env python3
"""
GLB Viewer with PySide6 UI and Offscreen Panda3D Rendering
Based on the proven approach used in the main HelpMeSign app
"""

import sys
import os
from pathlib import Path
from typing import Optional, Any

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QImage, QPixmap
    from PySide6.QtWidgets import (
        QApplication,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QSlider,
        QVBoxLayout,
        QWidget,
        QGroupBox,
        QGridLayout,
    )
except ImportError as e:
    print(f"Error importing PySide6: {e}")
    print("Please install PySide6: pip install PySide6")
    sys.exit(1)

try:
    from direct.showbase.ShowBase import ShowBase
    from direct.actor.Actor import Actor
    from panda3d.core import (
        AmbientLight, 
        DirectionalLight,
        Vec3, 
        Vec4,
        loadPrcFileData,
        Filename,
        VBase4,
        PNMImage
    )
except ImportError as e:
    print(f"Error importing Panda3D modules: {e}")
    print("Please ensure Panda3D is installed: pip install panda3d")
    sys.exit(1)

try:
    from pygltflib import GLTF2
    import numpy as np
    GLTF_AVAILABLE = True
except ImportError as e:
    print(f"Warning: pygltflib not available: {e}")
    print("Install with: pip install pygltflib")
    GLTF_AVAILABLE = False


def build_joint_hierarchy(glb_path):
    """Extract joint hierarchy from GLB file using pygltflib."""
    if not GLTF_AVAILABLE:
        return None, None
        
    try:
        gltf = GLTF2().load(glb_path)
        
        if not gltf.skins:
            return None, None
        
        # Build joint hierarchy
        joint_hierarchy = {}
        
        for skin in gltf.skins:
            root_joints = []
            
            for joint_idx in skin.joints:
                node = gltf.nodes[joint_idx]
                
                joint_data = {
                    'index': joint_idx,
                    'name': node.name or f"Joint_{joint_idx}",
                    'translation': node.translation or [0, 0, 0],
                    'rotation': node.rotation or [0, 0, 0, 1],
                    'scale': node.scale or [1, 1, 1],
                    'children': [],
                    'parent': None
                }
                
                joint_hierarchy[joint_idx] = joint_data
            
            # Build parent-child relationships
            for joint_idx in skin.joints:
                node = gltf.nodes[joint_idx]
                if node.children:
                    for child_idx in node.children:
                        if child_idx in joint_hierarchy:
                            joint_hierarchy[child_idx]['parent'] = joint_idx
                            joint_hierarchy[joint_idx]['children'].append(child_idx)
            
            # Find root joints (joints without parents)
            root_joints = [idx for idx, joint in joint_hierarchy.items() 
                          if joint['parent'] is None]
        
        return joint_hierarchy, root_joints
    except Exception as e:
        print(f"Error extracting joint hierarchy: {e}")
        return None, None


def print_joint_hierarchy(joint_hierarchy, root_joints, level=0):
    """Print the joint hierarchy in a tree format."""
    for root in root_joints:
        joint = joint_hierarchy[root]
        indent = "  " * level
        print(f"{indent}{joint['name']} (index: {joint['index']})")
        
        if joint['children']:
            print_joint_hierarchy(joint_hierarchy, joint['children'], level + 1)


class GLBViewerWindow(QMainWindow):
    """Main window with PySide6 UI and embedded Panda3D rendering."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GLB Viewer - Arivo Character")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 600)
        
        # Initialize Panda3D offscreen
        self.panda_ready = False
        self.showbase = None
        self.character = None
        self.camera = None
        self.ambient_light_node = None
        
        # Initialize control variables with default values
        defaults = self.get_default_values()
        self.camera_scale = defaults['camera_scale']
        self.camera_distance = defaults['camera_distance']
        self.camera_x_rot = defaults['camera_x_rot']
        self.camera_y_rot = defaults['camera_y_rot']
        self.camera_z_rot = defaults['camera_z_rot']
        self.ambient_light = defaults['ambient_light']
        self.character_x = defaults['character_x']
        self.character_y = defaults['character_y']
        self.character_z = defaults['character_z']
        
        # Initialize body part controls (HPR = Heading, Pitch, Roll; XYZ = Position)
        self.body_parts = {}
        body_part_names = [
            'neck', 'spine',  # Single joints (hips removed due to persistent issues)
            'left_shoulder', 'right_shoulder',
            'left_arm', 'right_arm', 'left_hand', 'right_hand',
            'left_fingers_thumb', 'right_fingers_thumb', 
            'left_fingers_index', 'right_fingers_index',
            'left_fingers_middle', 'right_fingers_middle', 
            'left_fingers_ring', 'right_fingers_ring',
            'left_fingers_pinky', 'right_fingers_pinky', 
            'left_leg', 'right_leg', 'left_foot', 'right_foot'
        ]
        
        for part in body_part_names:
            self.body_parts[part] = {
                'hpr': [0.0, 0.0, 0.0],  # Heading, Pitch, Roll
                'xyz': [0.0, 0.0, 0.0]   # X, Y, Z position
            }
        
        # Create UI
        self.create_ui()
        
        # Initialize Panda3D
        self.init_panda3d()
        
        # Start render timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.render_frame)
        self.timer.start(33)  # ~30 FPS (same as learn module)
        
    def get_default_values(self):
        """Get the default values for all controls."""
        return {
            'camera_scale': 7.0,  # Back to working scale
            'camera_distance': 9.0,  # Back to working distance
            'camera_x_rot': 0.0,
            'camera_y_rot': 1.0,  # Back to working rotation
            'camera_z_rot': 0.0,
            'ambient_light': 0.3,
            'character_x': 0.0,
            'character_y': 3.0,  # Back to working position
            'character_z': -5.0  # Back to working position
        }
        
    def create_ui(self):
        """Create the PySide6 UI with native system fonts."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left panel - 3D viewer
        self.create_viewer_panel(main_layout)
        
        # Right panel - Controls
        self.create_control_panel(main_layout)
        
    def create_viewer_panel(self, parent_layout):
        """Create the 3D viewer panel."""
        viewer_widget = QWidget()
        viewer_widget.setFixedWidth(700)
        viewer_layout = QVBoxLayout(viewer_widget)
        
        # 3D display label
        self.display_label = QLabel("Loading 3D character...")
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.display_label.setStyleSheet("""
            QLabel {
                border: 2px solid #ccc;
                border-radius: 8px;
                background-color: transparent;
                min-height: 100%;
            }
        """)
        viewer_layout.addWidget(self.display_label)
        
        parent_layout.addWidget(viewer_widget)
        
    def create_control_panel(self, parent_layout):
        """Create the control panel with native system fonts."""
        control_widget = QWidget()
        control_widget.setFixedWidth(400)  # Compact control panel
        control_layout = QVBoxLayout(control_widget)
        
        # Title and Export button row
        title_row = QHBoxLayout()
        
        title_label = QLabel("Camera Controls")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
            }
        """)
        title_row.addWidget(title_label)
        title_row.addStretch()  # Push export button to the right
        
        # Export button
        export_button = QPushButton("Export Values")
        export_button.clicked.connect(self.export_values)
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        title_row.addWidget(export_button)
        
        control_layout.addLayout(title_row)
        
        # Create control group
        control_group = QGroupBox("Camera Settings")
        control_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        group_layout = QGridLayout(control_group)
        
        # Create sliders with native system fonts
        self.create_slider_control(group_layout, "Scale", 0, 0.1, 20.0, self.camera_scale, self.update_camera_scale)
        self.create_slider_control(group_layout, "Distance", 1, 2.0, 15.0, self.camera_distance, self.update_camera_distance)
        
        # Character position controls
        self.create_slider_control(group_layout, "Pos-X", 2, -5.0, 5.0, self.character_x, self.update_character_x)
        self.create_slider_control(group_layout, "Pos-Y", 3, -5.0, 5.0, self.character_y, self.update_character_y)
        self.create_slider_control(group_layout, "Pos-Z", 4, -5.0, 5.0, self.character_z, self.update_character_z)
        
        # Camera rotation controls
        self.create_slider_control(group_layout, "X-Rot", 5, -180.0, 180.0, self.camera_x_rot, self.update_camera_x_rot)
        self.create_slider_control(group_layout, "Y-Rot", 6, -180.0, 180.0, self.camera_y_rot, self.update_camera_y_rot)
        self.create_slider_control(group_layout, "Z-Rot", 7, -180.0, 180.0, self.camera_z_rot, self.update_camera_z_rot)
        self.create_slider_control(group_layout, "Ambient", 8, 0.0, 1.0, self.ambient_light, self.update_ambient_light)
        
        # Reset button
        reset_button = QPushButton("Reset All")
        reset_button.clicked.connect(self.reset_all_controls)
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        group_layout.addWidget(reset_button, 9, 0, 1, 3)  # Span across 3 columns
        
        control_layout.addWidget(control_group)
        
        # Body Parts Control Table
        self.create_body_parts_table(control_layout)
        
        control_layout.addStretch()
        
        parent_layout.addWidget(control_widget)
        
    def create_slider_control(self, layout, label_text, row, min_val, max_val, initial_value, callback):
        """Create a slider control with native system fonts."""
        # Label
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 12px; color: #555;")
        layout.addWidget(label, row, 0)
        
        # Slider
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(int(min_val * 100))
        slider.setMaximum(int(max_val * 100))
        slider.setValue(int(initial_value * 100))
        slider.valueChanged.connect(lambda v: callback(v / 100.0))
        layout.addWidget(slider, row, 1)
        
        # Value label
        value_label = QLabel(f"{initial_value:.1f}")
        value_label.setStyleSheet("font-size: 11px; color: #666; min-width: 40px;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(value_label, row, 2)
        
        # Store references for reset function
        slider_name = label_text.lower().replace('-', '_').replace(' ', '_') + '_slider'
        value_name = label_text.lower().replace('-', '_').replace(' ', '_') + '_value'
        setattr(self, slider_name, slider)
        setattr(self, value_name, value_label)
        
    def create_body_parts_table(self, parent_layout):
        """Create the body parts control table with HPR and XYZ controls in top-down layout."""
        # Create control group with consistent styling
        body_group = QGroupBox("Body Parts Control")
        body_group.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                color: #333;
                border: 2px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Create scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setMaximumHeight(400)  # Limit height to make it scrollable
        
        # Create content widget for the scroll area
        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setSpacing(10)
        
        # Body parts list with clear descriptions (hips removed due to persistent issues)
        body_parts = [
            ("Neck", "Head and neck movement"),
            ("Spine", "Spinal column movement"),
            ("Shoulder", "Shoulder joint rotation"),
            ("Arm", "Upper arm rotation"),
            ("Hand", "Hand and wrist movement"),
            ("Fingers (Thumb)", "Thumb finger control"),
            ("Fingers (Index)", "Index finger control"),
            ("Fingers (Middle)", "Middle finger control"),
            ("Fingers (Ring)", "Ring finger control"),
            ("Fingers (Pinky)", "Pinky finger control"),
            ("Leg", "Upper leg and thigh movement"),
            ("Foot", "Foot and ankle movement")
        ]
        
        # Create controls for each body part in top-down layout
        for part_name, description in body_parts:
            # Create a group for this body part
            part_group = QGroupBox(f"{part_name} - {description}")
            part_group.setStyleSheet("""
                QGroupBox {
                    font-size: 11px;
                    font-weight: bold;
                    color: #444;
                    border: 1px solid #ddd;
                    border-radius: 3px;
                    margin-top: 5px;
                    padding-top: 8px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 8px;
                    padding: 0 3px 0 3px;
                }
            """)
            
            part_layout = QVBoxLayout(part_group)
            part_layout.setSpacing(5)
            
            # Create controls based on body part type
            if part_name in ["Neck", "Spine"]:
                # Single joint controls (no left/right)
                single_controls = self.create_hpr_xyz_controls_with_labels(
                    part_name.lower().replace(' ', '_').replace('(', '').replace(')', ''), 
                    part_name
                )
                part_layout.addWidget(single_controls)
            else:
                # Left and right controls side by side
                controls_layout = QHBoxLayout()
                
                # Left side controls
                left_controls = self.create_hpr_xyz_controls_with_labels(
                    f"left_{part_name.lower().replace(' ', '_').replace('(', '').replace(')', '')}", 
                    f"Left {part_name}"
                )
                # Right side controls  
                right_controls = self.create_hpr_xyz_controls_with_labels(
                    f"right_{part_name.lower().replace(' ', '_').replace('(', '').replace(')', '')}", 
                    f"Right {part_name}"
                )
                
                controls_layout.addWidget(left_controls)
                controls_layout.addWidget(right_controls)
                
                part_layout.addLayout(controls_layout)
            main_layout.addWidget(part_group)
        
        # Set the content widget as the scroll area's widget
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to the group
        group_layout_main = QVBoxLayout(body_group)
        group_layout_main.addWidget(scroll_area)
        
        parent_layout.addWidget(body_group)
        
        
    def create_hpr_xyz_controls_with_labels(self, part_name, display_name):
        """Create HPR and XYZ controls for a body part with clear labels."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Title and reset button row
        title_layout = QHBoxLayout()
        
        # Title for this side
        title_label = QLabel(display_name)
        title_label.setStyleSheet("font-size: 10px; color: #333; font-weight: bold; background-color: #f8f8f8; padding: 2px; border: 1px solid #ddd;")
        title_layout.addWidget(title_label)
        
        # Small reset button (no text, just an icon/symbol)
        reset_button = QPushButton("↻")
        reset_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                color: #666;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
                min-width: 20px;
                max-width: 20px;
                min-height: 18px;
                max-height: 18px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #999;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        reset_button.setToolTip(f"Reset {display_name} to default values")
        reset_button.clicked.connect(lambda: self.reset_body_part(part_name))
        title_layout.addWidget(reset_button)
        
        layout.addLayout(title_layout)
        
        # HPR Controls with individual labels
        hpr_label = QLabel("Rotation (HPR)")
        hpr_label.setStyleSheet("font-size: 9px; color: #666; font-weight: bold;")
        layout.addWidget(hpr_label)
        
        hpr_layout = QVBoxLayout()
        for i, axis in enumerate(['H', 'P', 'R']):
            # Create horizontal layout for label and slider
            control_layout = QHBoxLayout()
            
            # Axis label
            axis_label = QLabel(f"{axis}:")
            axis_label.setStyleSheet("font-size: 9px; color: #555; min-width: 15px;")
            axis_label.setFixedWidth(15)
            control_layout.addWidget(axis_label)
            
            # Slider
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(-1800)  # -180.0 * 10
            slider.setMaximum(1800)   # 180.0 * 10
            slider.setValue(0)
            slider.setFixedHeight(18)
            
            # Value label
            value_label = QLabel("0.0")
            value_label.setStyleSheet("font-size: 8px; color: #777; min-width: 30px;")
            value_label.setFixedWidth(30)
            
            # Connect to update function
            def make_update_func(p=part_name, idx=i, val_label=value_label):
                def update_func(v):
                    val = v / 10.0
                    val_label.setText(f"{val:.1f}")
                    self.update_body_part(p, 'hpr', idx, val)
                return update_func
            
            slider.valueChanged.connect(make_update_func())
            
            # Store reference
            slider_name = f"{part_name}_hpr_{axis.lower()}_slider"
            setattr(self, slider_name, slider)
            
            control_layout.addWidget(slider)
            control_layout.addWidget(value_label)
            hpr_layout.addLayout(control_layout)
        
        layout.addLayout(hpr_layout)
        
        # XYZ Controls with individual labels
        xyz_label = QLabel("Position (XYZ)")
        xyz_label.setStyleSheet("font-size: 9px; color: #666; font-weight: bold;")
        layout.addWidget(xyz_label)
        
        xyz_layout = QVBoxLayout()
        for i, axis in enumerate(['X', 'Y', 'Z']):
            # Create horizontal layout for label and slider
            control_layout = QHBoxLayout()
            
            # Axis label
            axis_label = QLabel(f"{axis}:")
            axis_label.setStyleSheet("font-size: 9px; color: #555; min-width: 15px;")
            axis_label.setFixedWidth(15)
            control_layout.addWidget(axis_label)
            
            # Slider
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(-1800)  # -180.0 * 10
            slider.setMaximum(1800)   # 180.0 * 10
            slider.setValue(0)
            slider.setFixedHeight(18)
            
            # Value label
            value_label = QLabel("0.0")
            value_label.setStyleSheet("font-size: 8px; color: #777; min-width: 30px;")
            value_label.setFixedWidth(30)
            
            # Connect to update function
            def make_update_func(p=part_name, idx=i, val_label=value_label):
                def update_func(v):
                    val = v / 10.0
                    val_label.setText(f"{val:.1f}")
                    self.update_body_part(p, 'xyz', idx, val)
                return update_func
            
            slider.valueChanged.connect(make_update_func())
            
            # Store reference
            slider_name = f"{part_name}_xyz_{axis.lower()}_slider"
            setattr(self, slider_name, slider)
            
            control_layout.addWidget(slider)
            control_layout.addWidget(value_label)
            xyz_layout.addLayout(control_layout)
        
        layout.addLayout(xyz_layout)
        
        return widget
    
    def reset_body_part(self, part_name):
        """Reset a specific body part to its default values."""
        if part_name not in self.body_parts:
            return
            
        try:
            # Reset the body part values to zero
            self.body_parts[part_name]['hpr'] = [0.0, 0.0, 0.0]
            self.body_parts[part_name]['xyz'] = [0.0, 0.0, 0.0]
            
            # Reset all sliders to zero
            for axis in ['h', 'p', 'r']:
                slider_name = f"{part_name}_hpr_{axis}_slider"
                if hasattr(self, slider_name):
                    getattr(self, slider_name).setValue(0)
            
            for axis in ['x', 'y', 'z']:
                slider_name = f"{part_name}_xyz_{axis}_slider"
                if hasattr(self, slider_name):
                    getattr(self, slider_name).setValue(0)
            
            # Reset the joint to its original position if we have it stored
            gltf_joint_name = self.get_gltf_joint_name(part_name)
            if gltf_joint_name and hasattr(self, 'original_joint_positions'):
                original_data = self.original_joint_positions.get(gltf_joint_name)
                if original_data:
                    try:
                        joint = self.character.controlJoint(None, "modelRoot", gltf_joint_name)
                        if joint and not joint.isEmpty():
                            joint.setHpr(original_data['hpr'])
                            joint.setPos(original_data['pos'])
                            self.character.update()
                    except Exception as e:
                        print(f"Could not reset joint {gltf_joint_name}: {e}")
                        
        except Exception as e:
            print(f"Error resetting body part {part_name}: {e}")
        
    def update_body_part(self, part_name, control_type, axis_index, value):
        """Update a body part's HPR or XYZ value and apply it to the character."""
        if part_name in self.body_parts:
            self.body_parts[part_name][control_type][axis_index] = value
            
            # Apply the transformation to the character
            self.apply_body_part_transform(part_name, control_type, axis_index, value)    
    def apply_body_part_transform(self, part_name, control_type, axis_index, value):
        """Apply the body part transformation using controlJoint method like hand_pose_editor."""
        if not self.character:
            return
            
        try:
            # Get the GLTF joint name for this body part
            gltf_joint_name = self.get_gltf_joint_name(part_name)
            if not gltf_joint_name:
                return
            
            # Use controlJoint method like hand_pose_editor does
            joint = self.character.controlJoint(None, "modelRoot", gltf_joint_name)
            if not joint or joint.isEmpty():
                return
            
            # Get current values
            hpr_values = self.body_parts[part_name]['hpr']
            xyz_values = self.body_parts[part_name]['xyz']
            
            # Apply transformations to the joint
            
            # Apply HPR transformation
            joint.setHpr(hpr_values[0], hpr_values[1], hpr_values[2])
            
            # Apply XYZ transformation (relative to original position)
            original_pos = self.get_original_joint_position(gltf_joint_name)
            if original_pos:
                joint.setPos(
                    original_pos[0] + xyz_values[0],
                    original_pos[1] + xyz_values[1], 
                    original_pos[2] + xyz_values[2]
                )
            
            # Update the character (important for Panda3D)
            self.character.update()
                
        except Exception as e:
            print(f"Error applying transform to {part_name}: {e}")
            import traceback
            traceback.print_exc()
    
    def apply_bone_transform(self, part_name, hpr_values, xyz_values):
        """Try to apply bone-specific transformations."""
        try:
            # Look for bone nodes in the character
            bone_node = self.find_bone_node(part_name)
            if bone_node:
                # Apply transformation to the specific bone
                bone_node.setHpr(hpr_values[0], hpr_values[1], hpr_values[2])
                original_pos = self.get_original_joint_position(part_name)
                if original_pos:
                    bone_node.setPos(
                        original_pos[0] + xyz_values[0],
                        original_pos[1] + xyz_values[1], 
                        original_pos[2] + xyz_values[2]
                    )
                return True
        except Exception as e:
            pass
        
        return False
    
    def find_bone_node(self, part_name):
        """Find a bone node for the specified body part."""
        # Try to find bone nodes with names related to the body part
        bone_patterns = {
            'neck': ['neck', 'head'],
            'spine': ['spine', 'back', 'torso'],
            'left_shoulder': ['left', 'shoulder', 'l_shoulder'],
            'right_shoulder': ['right', 'shoulder', 'r_shoulder'],
            'left_arm': ['left', 'arm', 'l_arm'],
            'right_arm': ['right', 'arm', 'r_arm'],
            'left_hand': ['left', 'hand', 'l_hand'],
            'right_hand': ['right', 'hand', 'r_hand'],
            'left_leg': ['left', 'leg', 'thigh', 'l_leg'],
            'right_leg': ['right', 'leg', 'thigh', 'r_leg'],
            'left_foot': ['left', 'foot', 'l_foot'],
            'right_foot': ['right', 'foot', 'r_foot']
        }
        
        patterns = bone_patterns.get(part_name, [])
        
        # Search for nodes matching the patterns
        def search_for_bone(node, depth=0, max_depth=10):
            if depth > max_depth:
                return None
                
            node_name = node.getName().lower()
            for pattern in patterns:
                if pattern in node_name:
                    return node
            
            # Search children
            for child in node.getChildren():
                result = search_for_bone(child, depth + 1, max_depth)
                if result:
                    return result
            
            return None
        
        return search_for_bone(self.character)
    
    def apply_differentiated_transform(self, part_name, hpr_values, xyz_values):
        """Apply differentiated transformations to create the illusion of individual control."""
        # Get the base node (Beta_Joints or Armature)
        base_node = self.character.find("**/Beta_Joints")
        if not base_node or base_node.isEmpty():
            base_node = self.character.find("**/Armature")
        
        if not base_node or base_node.isEmpty():
            return
        
        # Create different transformation patterns for different body parts
        # This simulates individual control by applying different scaling/offset patterns
        transform_multipliers = {
            'neck': (0.3, 0.3, 0.3, 0.0, 0.0, 0.0),      # Reduced transformation
            'spine': (0.5, 0.5, 0.5, 0.0, 0.0, 0.0),     # Medium transformation
            'left_shoulder': (0.4, 0.4, 0.4, -0.1, 0.0, 0.0),  # Left side offset
            'right_shoulder': (0.4, 0.4, 0.4, 0.1, 0.0, 0.0),   # Right side offset
            'left_arm': (0.6, 0.6, 0.6, -0.2, 0.0, 0.0),       # Left arm pattern
            'right_arm': (0.6, 0.6, 0.6, 0.2, 0.0, 0.0),       # Right arm pattern
            'left_hand': (0.8, 0.8, 0.8, -0.3, 0.0, 0.0),      # Left hand pattern
            'right_hand': (0.8, 0.8, 0.8, 0.3, 0.0, 0.0),      # Right h    and pattern
            'left_leg': (0.7, 0.7, 0.7, -0.1, 0.0, -0.1),      # Left leg pattern
            'right_leg': (0.7, 0.7, 0.7, 0.1, 0.0, -0.1),      # Right leg pattern
            'left_foot': (0.9, 0.9, 0.9, -0.2, 0.0, -0.2),     # Left foot pattern
            'right_foot': (0.9, 0.9, 0.9, 0.2, 0.0, -0.2),     # Right foot pattern
        }
        
        # Get the transformation pattern for this body part
        pattern = transform_multipliers.get(part_name, (0.5, 0.5, 0.5, 0.0, 0.0, 0.0))
        hpr_mult, xyz_mult, _, x_offset, y_offset, z_offset = pattern
        
        # Apply the differentiated transformation
        base_node.setHpr(
            hpr_values[0] * hpr_mult,
            hpr_values[1] * hpr_mult, 
            hpr_values[2] * hpr_mult
        )
        
        # Apply position with offset
        original_pos = self.get_original_joint_position(part_name)
        if original_pos:
            base_node.setPos(
                original_pos[0] + (xyz_values[0] * xyz_mult) + x_offset,
                original_pos[1] + (xyz_values[1] * xyz_mult) + y_offset,
                original_pos[2] + (xyz_values[2] * xyz_mult) + z_offset
            )
        
    
    def get_joint_name_from_part(self, part_name):
        """Convert part name to joint name using discovered joints."""
        # Only use joints that actually exist in the Panda3D scene
        # Based on discovery, only these nodes exist: Armature, Beta_Joints, Beta_Surface
        joint_mapping = {
            'neck': 'Beta_Joints',  
            'spine': 'Beta_Joints',
            'left_shoulder': 'Beta_Joints',
            'right_shoulder': 'Beta_Joints',
            'left_arm': 'Beta_Joints',
            'right_arm': 'Beta_Joints',
            'left_hand': 'Beta_Joints',
            'right_hand': 'Beta_Joints',
            'left_fingers_thumb': 'Beta_Joints',
            'right_fingers_thumb': 'Beta_Joints',
            'left_fingers_index': 'Beta_Joints',
            'right_fingers_index': 'Beta_Joints',
            'left_fingers_middle': 'Beta_Joints',
            'right_fingers_middle': 'Beta_Joints',
            'left_fingers_ring': 'Beta_Joints',
            'right_fingers_ring': 'Beta_Joints',
            'left_fingers_pinky': 'Beta_Joints',
            'right_fingers_pinky': 'Beta_Joints',
            'left_leg': 'Beta_Joints',
            'right_leg': 'Beta_Joints',
            'left_foot': 'Beta_Joints',
            'right_foot': 'Beta_Joints'
        }
        
        # Try the original mapping first
        joint_name = joint_mapping.get(part_name)
        if joint_name and hasattr(self, 'discovered_joints') and joint_name in self.discovered_joints:
            return joint_name
        
        # If not found, try to find a similar joint
        if hasattr(self, 'discovered_joints'):
            similar_joint = self.find_similar_joint(part_name)
            if similar_joint:
                return similar_joint.getName()
        
        return joint_name
    
    def find_alternative_joint(self, part_name):
        """Try to find alternative joint names if the primary one doesn't exist."""
        alternatives = {
            'neck': ['Beta_Joints', 'Armature'],
            'spine': ['Beta_Joints', 'Armature'],
            'left_shoulder': ['Beta_Joints', 'Armature'],
            'right_shoulder': ['Beta_Joints', 'Armature'],
            'left_arm': ['Beta_Joints', 'Armature'],
            'right_arm': ['Beta_Joints', 'Armature'],
            'left_hand': ['Beta_Joints', 'Armature'],
            'right_hand': ['Beta_Joints', 'Armature'],
            'left_fingers_thumb': ['Beta_Joints', 'Armature'],
            'right_fingers_thumb': ['Beta_Joints', 'Armature'],
            'left_fingers_index': ['Beta_Joints', 'Armature'],
            'right_fingers_index': ['Beta_Joints', 'Armature'],
            'left_fingers_middle': ['Beta_Joints', 'Armature'],
            'right_fingers_middle': ['Beta_Joints', 'Armature'],
            'left_fingers_ring': ['Beta_Joints', 'Armature'],
            'right_fingers_ring': ['Beta_Joints', 'Armature'],
            'left_fingers_pinky': ['Beta_Joints', 'Armature'],
            'right_fingers_pinky': ['Beta_Joints', 'Armature'],
            'left_leg': ['Beta_Joints', 'Armature'],
            'right_leg': ['Beta_Joints', 'Armature'],
            'left_foot': ['Beta_Joints', 'Armature'],
            'right_foot': ['Beta_Joints', 'Armature']
        }
        
        if part_name in alternatives:
            for alt_name in alternatives[part_name]:
                joint = self.character.find(f"**/{alt_name}")
                if joint and not joint.isEmpty():
                    return joint
        return None
    
    def find_child_joint_for_body_part(self, parent_joint, part_name):
        """Find a child joint that corresponds to the specific body part."""
        if not parent_joint:
            return None
            
        # Look for child joints that might correspond to the body part
        for i in range(parent_joint.getNumChildren()):
            child = parent_joint.getChild(i)
            child_name = child.getName().lower()
            
            # Map body part names to potential child joint names
            if 'left_arm' in part_name and ('arm' in child_name or 'shoulder' in child_name):
                return child
            elif 'right_arm' in part_name and ('arm' in child_name or 'shoulder' in child_name):
                return child
            elif 'left_hand' in part_name and 'hand' in child_name:
                return child
            elif 'right_hand' in part_name and 'hand' in child_name:
                return child
            elif 'left_leg' in part_name and ('leg' in child_name or 'thigh' in child_name):
                return child
            elif 'right_leg' in part_name and ('leg' in child_name or 'thigh' in child_name):
                return child
            elif 'left_foot' in part_name and 'foot' in child_name:
                return child
            elif 'right_foot' in part_name and 'foot' in child_name:
                return child
        
        # If no specific child found, return the first child (if any)
        if parent_joint.getNumChildren() > 0:
            return parent_joint.getChild(0)
        
        return None
    
    def get_gltf_joint_name(self, part_name):
        """Get the GLTF joint name for a body part."""
        gltf_mapping = {
            'neck': 'mixamorig:Neck',
            'spine': 'mixamorig:Spine',
            'left_shoulder': 'mixamorig:LeftShoulder',
            'right_shoulder': 'mixamorig:RightShoulder',
            'left_arm': 'mixamorig:LeftArm',
            'right_arm': 'mixamorig:RightArm',
            'left_hand': 'mixamorig:LeftHand',
            'right_hand': 'mixamorig:RightHand',
            'left_fingers_thumb': 'mixamorig:LeftHandThumb1',
            'right_fingers_thumb': 'mixamorig:RightHandThumb1',
            'left_fingers_index': 'mixamorig:LeftHandIndex1',
            'right_fingers_index': 'mixamorig:RightHandIndex1',
            'left_fingers_middle': 'mixamorig:LeftHandMiddle1',
            'right_fingers_middle': 'mixamorig:RightHandMiddle1',
            'left_fingers_ring': 'mixamorig:LeftHandRing1',
            'right_fingers_ring': 'mixamorig:RightHandRing1',
            'left_fingers_pinky': 'mixamorig:LeftHandPinky1',
            'right_fingers_pinky': 'mixamorig:RightHandPinky1',
            'left_leg': 'mixamorig:LeftUpLeg',
            'right_leg': 'mixamorig:RightUpLeg',
            'left_foot': 'mixamorig:LeftFoot',
            'right_foot': 'mixamorig:RightFoot'
        }
        return gltf_mapping.get(part_name)
    
    def find_joint_by_index(self, joint_index):
        """Find a Panda3D joint node by its GLTF index using skeleton system."""
        if not self.character:
            return None
            
        # Try to access the skeleton system
        try:
            # Look for skeleton nodes in the character
            skeleton = self.character.find("**/+Character")
            if skeleton and not skeleton.isEmpty():
                # Try to get the joint by index from the skeleton
                joint = skeleton.get_joint(joint_index)
                if joint:
                    return joint
            
            # Alternative: try to find skeleton in Armature or Beta_Joints
            for skeleton_name in ["Armature", "Beta_Joints"]:
                skeleton_node = self.character.find(f"**/{skeleton_name}")
                if skeleton_node and not skeleton_node.isEmpty():
                    # Try to get joint by index
                    joint = skeleton_node.get_joint(joint_index)
                    if joint:
                        return joint
                        
        except Exception as e:
            print(f"DEBUG: Skeleton access failed: {e}")
        
        # Fallback: try to find by name patterns
        joint_names_to_try = [
            f"Joint_{joint_index}",
            f"Bone_{joint_index}",
            f"mixamorig:Joint_{joint_index}",
            f"mixamorig:Bone_{joint_index}"
        ]
        
        for joint_name in joint_names_to_try:
            joint = self.character.find(f"**/{joint_name}")
            if joint and not joint.isEmpty():
                return joint
        
        return None
    
    def get_original_joint_position(self, joint_name):
        """Get the original position of a joint (for XYZ transformations)."""
        # Store original positions when the character is first loaded
        if not hasattr(self, 'original_joint_positions'):
            self.original_joint_positions = {}
            
        if joint_name not in self.original_joint_positions:
            # Try to get the joint using controlJoint method
            try:
                joint = self.character.controlJoint(None, "modelRoot", joint_name)
                if joint and not joint.isEmpty():
                    pos = joint.getPos()
                    self.original_joint_positions[joint_name] = {
                        'hpr': joint.getHpr(),
                        'pos': pos
                    }
                else:
                    return None
            except:
                return None
                
        # Return the position from the stored data
        joint_data = self.original_joint_positions.get(joint_name)
        if joint_data and 'pos' in joint_data:
            return joint_data['pos']
        return None
        
    def init_panda3d(self):
        """Initialize Panda3D in offscreen mode."""
        try:
            # Configure Panda3D for offscreen rendering (same as learn module)
            loadPrcFileData("", "window-type offscreen")
            loadPrcFileData("", "sync-video 0")
            loadPrcFileData("", "framebuffer-srgb true")
            loadPrcFileData("", "framebuffer-alpha true")  # Enable alpha for transparent background
            loadPrcFileData("", "gl-check-errors false")
            loadPrcFileData("", "notify-level-glgsg fatal")
            loadPrcFileData("", "notify-level-display fatal")
            loadPrcFileData("", "win-size 800 800")
            loadPrcFileData("", "framebuffer-multisample 1")
            
            # Initialize ShowBase
            self.showbase = ShowBase()
            
            # Set up scene
            self.setup_scene()
            
            # Set up render texture (same as learn module)
            self.color_tex = None
            try:
                from panda3d.core import GraphicsOutput, Texture
                
                tex = Texture()
                self.showbase.win.addRenderTexture(tex, GraphicsOutput.RTMCopyRam)
                self.color_tex = tex
                print("Render texture created successfully")
            except Exception as e:
                print(f"Failed to create render texture: {e}")
                self.color_tex = None
            
            # Load character
            glb_path = os.path.join(os.path.dirname(__file__), "resources", "characters", "arivo.glb")
            self.load_glb(glb_path)
            
            self.panda_ready = True
            
        except Exception as e:
            print(f"Error initializing Panda3D: {e}")
            
    def setup_scene(self):
        """Set up the Panda3D scene."""
        self.showbase.setBackgroundColor(0, 0, 0, 0)  # Transparent background
        
        # Set up lighting
        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor(VBase4(0.5, 0.5, 0.5, 1))  # Brighter ambient
        self.ambient_light_node = self.showbase.render.attachNewNode(ambient_light)
        self.showbase.render.setLight(self.ambient_light_node)
        
        directional_light = DirectionalLight('directional_light')
        directional_light.setColor(VBase4(1.0, 1.0, 1.0, 1))  # Brighter directional
        directional_light.setDirection(Vec3(-1, -1, -1))
        directional_light_node = self.showbase.render.attachNewNode(directional_light)
        self.showbase.render.setLight(directional_light_node)
        
        # Set up camera
        self.camera = self.showbase.camera
        self.camera.setPos(0, -8, 1)  # Lower camera to see full character height
        self.camera.lookAt(0, 0, 1)   # Look at character center height
        
        # Set camera lens for better view
        lens = self.showbase.camLens
        lens.setFov(60)  # Moderate field of view to see full character
        
        
    def load_glb(self, glb_path):
        """Load a GLB file."""
        try:
            if not os.path.exists(glb_path):
                print(f"GLB file not found: {glb_path}")
                return
                
            # Load as Actor instead of regular model to enable controlJoint
            self.character = Actor(glb_path)
            
            if not self.character:
                print(f"Failed to load GLB file: {glb_path}")
                return
                
            self.character.setPos(self.character_x, self.character_y, self.character_z)
            self.character.setHpr(0, 0, 0)  # Keep original orientation
            self.character.setScale(3.0)    # Start at scale 3
            self.character.reparentTo(self.showbase.render)
            
            # Initialize original joint positions for body part controls
            self.initialize_joint_positions()
            
            # Apply natural pose if available
            self.apply_natural_pose()
            
        except Exception as e:
            print(f"Error loading GLB file: {e}")
    
    def initialize_joint_positions(self):
        """Initialize and store original joint positions for all body part joints."""
        if not self.character:
            return
            
        self.original_joint_positions = {}
        
        # First, discover all available joints in the character
        self.discover_joints()
        
        # Store original positions for all body part joints
        body_part_names = [
            'neck', 'spine', 'left_shoulder', 'right_shoulder',
            'left_arm', 'right_arm', 'left_hand', 'right_hand',
            'left_fingers_thumb', 'right_fingers_thumb', 'left_fingers_index', 'right_fingers_index',
            'left_fingers_middle', 'right_fingers_middle', 'left_fingers_ring', 'right_fingers_ring',
            'left_fingers_pinky', 'right_fingers_pinky', 'left_leg', 'right_leg', 'left_foot', 'right_foot'
        ]
        
        for part_name in body_part_names:
            gltf_joint_name = self.get_gltf_joint_name(part_name)
            if gltf_joint_name:
                try:
                    # Get the joint using controlJoint method
                    joint = self.character.controlJoint(None, "modelRoot", gltf_joint_name)
                    if joint and not joint.isEmpty():
                        # Store original HPR and position
                        original_hpr = joint.getHpr()
                        original_pos = joint.getPos()
                        self.original_joint_positions[gltf_joint_name] = {
                            'hpr': original_hpr,
                            'pos': original_pos
                        }
                        print(f"Initialized joint position for {gltf_joint_name}: HPR={original_hpr}, POS={original_pos}")
                except Exception as e:
                    print(f"Could not initialize position for {gltf_joint_name}: {e}")
    
    def discover_joints(self):
        """Discover all joints in the character model using GLTF extraction."""
        if not self.character:
            return
            
        
        # Try GLTF-based joint extraction first
        glb_path = os.path.join(os.path.dirname(__file__), "resources", "characters", "arivo.glb")
        joint_hierarchy, root_joints = build_joint_hierarchy(glb_path)
        
        if joint_hierarchy and root_joints:
            
            # Store the GLTF joint data
            self.gltf_joint_hierarchy = joint_hierarchy
            self.gltf_root_joints = root_joints
            
            # Explore the skeleton system
            self.explore_skeleton_system()
            
            # Extract joint names for compatibility
            self.discovered_joints = [joint['name'] for joint in joint_hierarchy.values()]
            
            # Create a mapping from GLTF joint names to Panda3D nodes
            self.gltf_to_panda_mapping = {}
            for joint_name in self.discovered_joints:
                # Try to find the joint in Panda3D
                panda_node = self.character.find(f"**/{joint_name}")
                if panda_node and not panda_node.isEmpty():
                    self.gltf_to_panda_mapping[joint_name] = panda_node
                    print(f"Found Panda3D node for GLTF joint: {joint_name}")
                else:
                    # Try without the mixamorig: prefix
                    simple_name = joint_name.replace('mixamorig:', '')
                    panda_node = self.character.find(f"**/{simple_name}")
                    if panda_node and not panda_node.isEmpty():
                        self.gltf_to_panda_mapping[joint_name] = panda_node
                    else:
                        print(f"Could not find Panda3D node for GLTF joint: {joint_name}")
            
            
            
        else:
            # Fallback to original Panda3D traversal
            self.discovered_joints = []
            
            def traverse_node(node, depth=0, max_depth=10):
                if depth > max_depth:
                    return
                    
                indent = "  " * depth
                node_name = node.getName()
                if node_name and node_name != "Scene":
                    self.discovered_joints.append(node_name)
                    print(f"{indent}{node_name}")
                
                # Continue traversing deeper
                for child in node.getChildren():
                    traverse_node(child, depth + 1, max_depth)
            
            # Traverse much deeper to find individual joints
            traverse_node(self.character, max_depth=15)
    
    def explore_skeleton_system(self):
        """Explore the Panda3D skeleton system to find available joints."""
        
        try:
            # Look for Character nodes (skeleton containers)
            character_nodes = []
            def find_characters(node, depth=0, max_depth=5):
                if depth > max_depth:
                    return
                if node.hasPythonTag('Character'):
                    character_nodes.append(node)
                for child in node.getChildren():
                    find_characters(child, depth + 1, max_depth)
            
            find_characters(self.character)
            
            # Explore each character node
            for i, char_node in enumerate(character_nodes):
                try:
                    # Try to get joint count
                    joint_count = char_node.getNumJoints()
                    
                    # Try to list some joints
                    for j in range(min(joint_count, 10)):  # Show first 10 joints
                        try:
                            joint = char_node.get_joint(j)                            
                        except:
                            pass
                            
                except Exception as e:
                    print(f"  Error accessing character: {e}")
            
            # Also check Armature and Beta_Joints for skeleton properties
            for skeleton_name in ["Armature", "Beta_Joints"]:
                skeleton_node = self.character.find(f"**/{skeleton_name}")
                if skeleton_node and not skeleton_node.isEmpty():
                    print(f"\nExploring {skeleton_name}:")
                    try:
                        # Check if it has joint-related methods
                        if hasattr(skeleton_node, 'getNumJoints'):
                            joint_count = skeleton_node.getNumJoints()
                            
                            # Try to access some joints
                            for j in range(min(joint_count, 5)):
                                try:
                                    joint = skeleton_node.get_joint(j)                                    
                                except:
                                    pass
                    except Exception as e:
                        print(f"  Error accessing {skeleton_name}: {e}")
                        
        except Exception as e:
            print(f"Error exploring skeleton system: {e}")
        
    
    def find_similar_joint(self, target_name):
        """Find a joint with a similar name to the target."""
        if not hasattr(self, 'discovered_joints'):
            return None
            
        target_lower = target_name.lower()
        
        # Look for exact matches first
        for joint_name in self.discovered_joints:
            if joint_name.lower() == target_lower:
                return self.character.find(f"**/{joint_name}")
        
        # Look for partial matches
        for joint_name in self.discovered_joints:
            joint_lower = joint_name.lower()
            if (target_lower in joint_lower or joint_lower in target_lower):
                return self.character.find(f"**/{joint_name}")
        
        # Look for common patterns
        patterns = {
            'shoulder': ['shoulder', 'arm', 'clavicle'],
            'arm': ['arm', 'forearm', 'elbow'],
            'hand': ['hand', 'wrist'],
            'thumb': ['thumb'],
            'index': ['index'],
            'middle': ['middle'],
            'ring': ['ring'],
            'pinky': ['pinky', 'little'],
            'leg': ['leg', 'thigh', 'femur'],
            'hip': ['hip', 'pelvis']
        }
        
        for pattern, keywords in patterns.items():
            if pattern in target_lower:
                for joint_name in self.discovered_joints:
                    joint_lower = joint_name.lower()
                    for keyword in keywords:
                        if keyword in joint_lower:
                            return self.character.find(f"**/{joint_name}")
        
        return None
            
    def apply_natural_pose(self):
        """Apply a natural pose to the character."""
        try:
            from helpmesign.utils.natural_pose_service import NaturalPoseService
            
            pose_service = NaturalPoseService()
            if hasattr(pose_service, 'get_natural_pose'):
                natural_pose = pose_service.get_natural_pose()
                
                if natural_pose and self.character:
                    for joint_name, pose_data in natural_pose.items():
                        joint_node = self.character.find(f"**/{joint_name}")
                        if not joint_node.isEmpty():
                            if 'rotation' in pose_data:
                                rotation = pose_data['rotation']
                                joint_node.setHpr(rotation['x'], rotation['y'], rotation['z'])
                            
                            if 'position' in pose_data:
                                position = pose_data['position']
                                joint_node.setPos(position['x'], position['y'], position['z'])
                                
        except ImportError:
            pass
        except Exception as e:
            print(f"Error applying natural pose: {e}")
            
    def render_frame(self):
        """Render a frame from Panda3D and display it (same as learn module)."""
        if not self.panda_ready or not self.showbase:
            return
            
        try:
            # Step Panda3D
            self.showbase.taskMgr.step()
            
            # Use render texture first (same as learn module)
            image_updated = False
            if self.color_tex is not None:
                try:
                    tex = self.color_tex
                    if tex.hasRamImage():
                        data = tex.getRamImageAs("RGBA")
                        width = tex.getXSize()
                        height = tex.getYSize()
                        stride = width * 4
                        import warnings
                        
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore", DeprecationWarning)
                            img = QImage(
                                bytes(data), width, height, stride, QImage.Format_RGBA8888
                            ).mirrored(False, True)
                        
                        # Scale to full display size
                        display_size = self.display_label.size()
                        display_img = img.scaled(
                            display_size.width(), display_size.height(),
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        
                        # Display in label
                        self.display_label.setPixmap(QPixmap.fromImage(display_img))
                        image_updated = True
                except Exception as e:
                    print(f"Error with render texture: {e}")
                    image_updated = False
            
            # Fallback: screenshot method
            if not image_updated:
                try:
                    pimg = PNMImage()
                    ok = self.showbase.win.getScreenshot(pimg)
                    if ok:
                        width = pimg.getXSize()
                        height = pimg.getYSize()
                        
                        # Convert PNMImage to QImage
                        img = QImage(width, height, QImage.Format_RGBA8888)
                        
                        # Fill the QImage with PNMImage data
                        for y in range(height):
                            for x in range(width):
                                r, g, b = pimg.getXelVal(x, y)
                                r = max(0, min(255, int(r * 255)))
                                g = max(0, min(255, int(g * 255))) 
                                b = max(0, min(255, int(b * 255)))
                                a = 255
                                img.setPixel(x, y, (a << 24) | (r << 16) | (g << 8) | b)
                        
                        img = img.mirrored(False, True)
                        
                        # Scale to full display size
                        display_size = self.display_label.size()
                        display_img = img.scaled(
                            display_size.width(), display_size.height(),
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        
                        # Display in label
                        self.display_label.setPixmap(QPixmap.fromImage(display_img))
                except Exception as e:
                    print(f"Error with screenshot fallback: {e}")
                
        except Exception as e:
            print(f"Error rendering frame: {e}")
            
    def update_camera_scale(self, value):
        """Update camera scale."""
        self.camera_scale = value
        if self.character:
            # Keep character at current position
            self.character.setPos(self.character_x, self.character_y, self.character_z)
            self.character.setScale(value)
            # Keep camera at a fixed distance - don't move it based on scale
            # The character will get larger/smaller but stay in frame
            self.camera.setPos(0, -8, 1)
        self.scale_value.setText(f"{value:.1f}")
        
    def update_camera_distance(self, value):
        """Update camera distance."""
        self.camera_distance = value
        if self.camera:
            # Simple distance control - just move camera closer/further
            # Base distance of 8, with slider range 2-15, so offset from 6 (middle)
            adjusted_distance = 8 + (value - 6)  # Offset from default distance of 6
            self.camera.setPos(0, -adjusted_distance, 1)
        self.distance_value.setText(f"{value:.1f}")
        
    def update_character_x(self, value):
        """Update character X position."""
        self.character_x = value
        if self.character:
            self.character.setPos(value, self.character_y, self.character_z)
        self.pos_x_value.setText(f"{value:.1f}")
        
    def update_character_y(self, value):
        """Update character Y position."""
        self.character_y = value
        if self.character:
            self.character.setPos(self.character_x, value, self.character_z)
        self.pos_y_value.setText(f"{value:.1f}")
        
    def update_character_z(self, value):
        """Update character Z position."""
        self.character_z = value
        if self.character:
            self.character.setPos(self.character_x, self.character_y, value)
        self.pos_z_value.setText(f"{value:.1f}")
        
    def update_camera_x_rot(self, value):
        """Update camera X rotation."""
        self.camera_x_rot = value
        if self.camera:
            self.camera.setHpr(self.camera_x_rot, self.camera_y_rot, self.camera_z_rot)
        self.x_rot_value.setText(f"{value:.1f}")
        
    def update_camera_y_rot(self, value):
        """Update camera Y rotation."""
        self.camera_y_rot = value
        if self.camera:
            self.camera.setHpr(self.camera_x_rot, self.camera_y_rot, self.camera_z_rot)
        self.y_rot_value.setText(f"{value:.1f}")
        
    def update_camera_z_rot(self, value):
        """Update camera Z rotation."""
        self.camera_z_rot = value
        if self.camera:
            self.camera.setHpr(self.camera_x_rot, self.camera_y_rot, self.camera_z_rot)
        self.z_rot_value.setText(f"{value:.1f}")
        
    def update_ambient_light(self, value):
        """Update ambient light."""
        self.ambient_light = value
        if self.ambient_light_node:
            # Get the light from the node and update its color
            light = self.ambient_light_node.node()
            if light:
                light.setColor(VBase4(value, value, value, 1))
        self.ambient_value.setText(f"{value:.1f}")
        
    def reset_all_controls(self):
        """Reset all controls to their default values."""
        try:
            # Get default values
            defaults = self.get_default_values()
            
            # Reset all control variables
            self.camera_scale = defaults['camera_scale']
            self.camera_distance = defaults['camera_distance']
            self.camera_x_rot = defaults['camera_x_rot']
            self.camera_y_rot = defaults['camera_y_rot']
            self.camera_z_rot = defaults['camera_z_rot']
            self.ambient_light = defaults['ambient_light']
            self.character_x = defaults['character_x']
            self.character_y = defaults['character_y']
            self.character_z = defaults['character_z']
            
            # Update sliders (with error handling)
            slider_names = ['scale', 'distance', 'x_rot', 'y_rot', 'z_rot', 'ambient', 'pos_x', 'pos_y', 'pos_z']
            slider_values = [self.camera_scale, self.camera_distance, self.camera_x_rot, self.camera_y_rot, 
                           self.camera_z_rot, self.ambient_light, self.character_x, self.character_y, self.character_z]
            
            for name, value in zip(slider_names, slider_values):
                slider_attr = f"{name}_slider"
                value_attr = f"{name}_value"
                if hasattr(self, slider_attr):
                    getattr(self, slider_attr).setValue(int(value * 100))
                if hasattr(self, value_attr):
                    getattr(self, value_attr).setText(f"{value:.1f}")
            
            # Reset all body part controls to zero
            for part_name in self.body_parts:
                self.body_parts[part_name]['hpr'] = [0.0, 0.0, 0.0]
                self.body_parts[part_name]['xyz'] = [0.0, 0.0, 0.0]
            
            # Reset all body part sliders to zero
            for part_name in self.body_parts:
                # Reset HPR sliders
                for axis in ['h', 'p', 'r']:
                    slider_attr = f"{part_name}_hpr_{axis}_slider"
                    if hasattr(self, slider_attr):
                        getattr(self, slider_attr).setValue(0)
                
                # Reset XYZ sliders
                for axis in ['x', 'y', 'z']:
                    slider_attr = f"{part_name}_xyz_{axis}_slider"
                    if hasattr(self, slider_attr):
                        getattr(self, slider_attr).setValue(0)
            
            # Reset all joints to their original positions and rotations
            if self.character and hasattr(self, 'original_joint_positions'):
                for joint_name, original_data in self.original_joint_positions.items():
                    try:
                        joint = self.character.controlJoint(None, "modelRoot", joint_name)
                        if joint and not joint.isEmpty():
                            # Restore original HPR and position
                            joint.setHpr(original_data['hpr'])
                            joint.setPos(original_data['pos'])
                            print(f"Reset joint {joint_name} to original position")
                    except Exception as e:
                        print(f"Could not reset joint {joint_name}: {e}")
                
                # Update the character after all joint resets
                self.character.update()
            
            # Apply changes to 3D scene
            if self.character:
                self.character.setPos(self.character_x, self.character_y, self.character_z)
                self.character.setScale(self.camera_scale)
                
            if self.camera:
                self.camera.setPos(0, -8, 1)
                self.camera.setHpr(self.camera_x_rot, self.camera_y_rot, self.camera_z_rot)
                
            if self.ambient_light_node:
                light = self.ambient_light_node.node()
                if light:
                    light.setColor(VBase4(self.ambient_light, self.ambient_light, self.ambient_light, 1))
                    
        except Exception as e:
            print(f"Error in reset function: {e}")
            
    def export_values(self):
        """Export current control values to clipboard and console."""
        try:
            # Get current values
            current_values = {
                'camera_scale': self.camera_scale,
                'camera_distance': self.camera_distance,
                'camera_x_rot': self.camera_x_rot,
                'camera_y_rot': self.camera_y_rot,
                'camera_z_rot': self.camera_z_rot,
                'ambient_light': self.ambient_light,
                'character_x': self.character_x,
                'character_y': self.character_y,
                'character_z': self.character_z,
                'body_parts': self.body_parts
            }
            
            # Create formatted string for export
            export_text = "def get_default_values(self):\n"
            export_text += '    """Get the default values for all controls."""\n'
            export_text += "    return {\n"
            
            # Export basic controls
            for key, value in current_values.items():
                if key != 'body_parts':
                    export_text += f"        '{key}': {value},\n"
            
            # Export body parts
            export_text += "        'body_parts': {\n"
            for part_name, part_data in current_values['body_parts'].items():
                export_text += f"            '{part_name}': {{\n"
                export_text += f"                'hpr': {part_data['hpr']},\n"
                export_text += f"                'xyz': {part_data['xyz']}\n"
                export_text += f"            }},\n"
            export_text += "        }\n"
            export_text += "    }"
            
            # Print to console
            print("\n" + "="*50)
            print("EXPORTED CONTROL VALUES:")
            print("="*50)
            print(export_text)
            print("="*50)
            print("Copy the above code to replace your get_default_values() function")
            print("="*50 + "\n")
            
            # Copy to clipboard
            try:
                from PySide6.QtGui import QGuiApplication
                clipboard = QGuiApplication.clipboard()
                clipboard.setText(export_text)
                print("✅ Values copied to clipboard!")
            except Exception as e:
                print(f"⚠️  Could not copy to clipboard: {e}")
                
        except Exception as e:
            print(f"Error exporting values: {e}")


def main():
    """Main function."""
    app = QApplication(sys.argv)
    
    # Set application style for native look
    app.setStyle('Fusion')
    
    window = GLBViewerWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
