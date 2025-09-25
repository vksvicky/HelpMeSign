#!/usr/bin/env python3
"""
GLB Viewer with PySide6 UI and Offscreen Panda3D Rendering
Based on the proven approach used in the main HelpMeSign app
"""

import json
import os
import sys
from multiprocessing import parent_process
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the project root to the Python path
# Current file is in src/helpmesign/modes/learn/glb_viewer.py
# Need to go up 4 levels: learn -> modes -> helpmesign -> src -> project_root
current_dir = os.path.dirname(__file__)  # src/helpmesign/modes/learn/
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
)  # project root
sys.path.insert(0, os.path.join(project_root, "src"))

# Make project_root available globally for resource access
globals()["project_root"] = project_root

try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QImage, QPixmap
    from PySide6.QtWidgets import (
        QApplication,
        QComboBox,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QSlider,
        QVBoxLayout,
        QWidget,
    )
except ImportError as e:
    print(f"Error importing PySide6: {e}")
    print("Please install PySide6: pip install PySide6")
    sys.exit(1)

try:
    from direct.actor.Actor import Actor
    from direct.showbase.ShowBase import ShowBase
    from panda3d.core import (
        AmbientLight,
        DirectionalLight,
        PNMImage,
        VBase4,
        Vec3,
        loadPrcFileData,
    )
except ImportError as e:
    print(f"Error importing Panda3D modules: {e}")
    print("Please ensure Panda3D is installed: pip install panda3d")
    sys.exit(1)

try:
    from pygltflib import GLTF2

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
                    "index": joint_idx,
                    "name": node.name or f"Joint_{joint_idx}",
                    "translation": node.translation or [0, 0, 0],
                    "rotation": node.rotation or [0, 0, 0, 1],
                    "scale": node.scale or [1, 1, 1],
                    "children": [],
                    "parent": None,
                }

                joint_hierarchy[joint_idx] = joint_data

            # Build parent-child relationships
            for joint_idx in skin.joints:
                node = gltf.nodes[joint_idx]
                if node.children:
                    for child_idx in node.children:
                        if child_idx in joint_hierarchy:
                            joint_hierarchy[child_idx]["parent"] = joint_idx
                            joint_hierarchy[joint_idx]["children"].append(child_idx)

            # Find root joints (joints without parents)
            root_joints = [
                idx for idx, joint in joint_hierarchy.items() if joint["parent"] is None
            ]

        return joint_hierarchy, root_joints
    except Exception as e:
        print(f"Error extracting joint hierarchy: {e}")
        return None, None


class GLBViewerWindow(QMainWindow):
    """Main window with PySide6 UI and embedded Panda3D rendering."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GLB Viewer - Arivo Character")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 600)

        # Initialize Panda3D offscreen
        self.panda_ready = False
        self.showbase: Optional[Any] = None
        self.character: Optional[Any] = None
        self.camera: Optional[Any] = None
        self.ambient_light_node: Optional[Any] = None

        # Initialize control variables with default values
        defaults = self.get_default_values()
        self.camera_scale = defaults["camera_scale"]
        self.camera_distance = defaults["camera_distance"]
        self.camera_x_rot = defaults["camera_x_rot"]
        self.camera_y_rot = defaults["camera_y_rot"]
        self.camera_z_rot = defaults["camera_z_rot"]
        self.ambient_light = defaults["ambient_light"]
        self.character_x = defaults["character_x"]
        self.character_y = defaults["character_y"]
        self.character_z = defaults["character_z"]

        # Load language and sign data
        self.available_languages = self.load_available_languages()
        self.current_language = "ASL"  # Default language
        self.available_signs = self.load_available_signs(self.current_language)

        # Initialize universal pose generator (will be updated when language changes)
        self.pose_generator = None
        self._initialize_pose_generator()

        # Initialize body part controls (HPR = Heading, Pitch, Roll; XYZ = Position)
        self.body_parts = {}
        self.body_part_names = [
            "neck",
            "spine",  # Single joints (hips removed due to persistent issues)
            "left_shoulder",
            "right_shoulder",
            "left_arm",
            "right_arm",
            "left_forearm",
            "right_forearm",
            "left_hand",
            "right_hand",
            "left_fingers_thumb",
            "right_fingers_thumb",
            "left_fingers_index",
            "right_fingers_index",
            "left_fingers_middle",
            "right_fingers_middle",
            "left_fingers_ring",
            "right_fingers_ring",
            "left_fingers_pinky",
            "right_fingers_pinky",
            "left_leg",
            "right_leg",
            "left_foot",
            "right_foot",
        ]

        # Get natural pose data from service
        from helpmesign.utils.natural_pose_service import NaturalPoseService

        pose_service = NaturalPoseService()
        natural_pose_data = pose_service.get_all_body_parts_pose()

        for part in self.body_part_names:
            # Use natural pose values if available, otherwise default to zero
            if part in natural_pose_data:
                self.body_parts[part] = {
                    "hpr": natural_pose_data[part]["hpr"].copy(),
                    "xyz": natural_pose_data[part]["xyz"].copy(),
                }
            else:
                self.body_parts[part] = {
                    "hpr": [0.0, 0.0, 0.0],  # Heading, Pitch, Roll
                    "xyz": [0.0, 0.0, 0.0],  # X, Y, Z position
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
        # Import NaturalPoseService to get body parts data
        from helpmesign.utils.natural_pose_service import (
            NaturalPoseService,
        )

        pose_service = NaturalPoseService()
        body_parts_data = pose_service.get_all_body_parts_pose()

        return {
            "camera_scale": 6.5,
            "camera_distance": 9.0,
            "camera_x_rot": 0.0,
            "camera_y_rot": 27.7,
            "camera_z_rot": 0.0,
            "ambient_light": 0.3,
            "character_x": 2.1,
            "character_y": -3.2,
            "character_z": -5.0,
            "body_parts": body_parts_data,
        }

    def load_available_languages(self) -> List[Dict[str, Any]]:
        """Load available sign languages from languages.json."""
        try:
            languages_path = os.path.join(
                project_root, "resources", "data", "languages.json"
            )
            with open(languages_path, "r", encoding="utf-8") as f:
                languages = json.load(f)
            return languages  # type: ignore[no-any-return]
        except Exception as e:
            print(f"Error loading languages: {e}")
            return []

    def load_available_signs(self, language_code: str) -> Dict[str, Dict]:
        """Load available signs for a given language based on its hand support."""
        try:
            signs_path = os.path.join(
                project_root, "resources", "data", "signs", language_code.lower()
            )
            signs: Dict[str, Dict[str, Any]] = {}

            if not os.path.exists(signs_path):
                return signs

            # Get language metadata to determine hand support
            language_info = self.get_language_info(language_code)
            hand_support = (
                language_info.get("handSupport", "single")
                if language_info
                else "single"
            )

            if hand_support == "both":
                # For languages that support both hands, look for single combined file
                # e.g., bsl_hand.json
                combined_file = os.path.join(
                    signs_path, f"{language_code.lower()}_hand.json"
                )
                if os.path.exists(combined_file):
                    self._load_hand_data(combined_file, "both", signs)
                else:
                    print(
                        f"Combined hand file not found for {language_code}: {combined_file}"
                    )
            else:
                # For single hand languages, look for separate left/right files
                # e.g., asl_left_hand.json, asl_right_hand.json
                # Prefer right hand, fallback to left
                for hand in ["right", "left"]:
                    hand_file = os.path.join(
                        signs_path, f"{language_code.lower()}_{hand}_hand.json"
                    )
                    if os.path.exists(hand_file):
                        self._load_hand_data(hand_file, hand, signs)
                        break  # Only load one hand for single hand languages

            return signs
        except Exception as e:
            print(f"Error loading signs for {language_code}: {e}")
            return {}

    def _initialize_pose_generator(self):
        """Initialize pose generator with appropriate config for current language."""
        try:

            from .instruction_to_pose_generator import (
                UniversalInstructionToPoseGenerator,
            )

            # Get language code from current language
            language_code = self.current_language.lower()
            config_path = os.path.join(
                project_root,
                "resources",
                "data",
                "pose_generation",
                f"{language_code}_config.json",
            )

            if os.path.exists(config_path):
                self.pose_generator = UniversalInstructionToPoseGenerator(config_path)
                print(f"✅ Pose generator initialized with {language_code} config")
            else:
                # Fall back to universal config
                self.pose_generator = UniversalInstructionToPoseGenerator()
                print(
                    f"⚠️ No specific config for {language_code}, using universal config"
                )

        except Exception as e:
            print(f"⚠️ Could not initialize pose generator: {e}")
            self.pose_generator = None

    def get_language_info(self, language_code: str) -> Dict[str, Any]:
        """Get language information from the available languages."""
        for lang in self.available_languages:
            if lang.get("code") == language_code:
                return lang.get("metadata", {})  # type: ignore[no-any-return]
        return {}

    def _load_hand_data(self, hand_file: str, hand: str, signs: Dict):
        """Helper method to load sign data from a hand file."""
        with open(hand_file, "r", encoding="utf-8") as f:
            hand_data = json.load(f)

            # Load alphabet letters
            if "alphabet" in hand_data:
                for letter, data in hand_data["alphabet"].items():
                    sign_key = letter  # Default: just use the letter/number

                    signs[sign_key] = {
                        "letter": letter,
                        "hand": hand,
                        "description": data.get("description", ""),
                        "instructions": data.get("instructions", ""),
                        "svg": data.get("svg", ""),
                    }

            # Load numbers
            if "numbers" in hand_data:
                for number, data in hand_data["numbers"].items():
                    sign_key = number  # Default: just use the letter/number

                    signs[sign_key] = {
                        "letter": number,
                        "hand": hand,
                        "description": data.get("description", ""),
                        "instructions": data.get("instructions", ""),
                        "svg": data.get("svg", ""),
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
        self.display_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.display_label.setStyleSheet(
            """
            QLabel {
                border: 2px solid #ccc;
                border-radius: 8px;
                background-color: transparent;
                min-height: 100%;
            }
        """
        )
        viewer_layout.addWidget(self.display_label)

        parent_layout.addWidget(viewer_widget)

    def create_control_panel(self, parent_layout):
        """Create the control panel with native system fonts."""
        control_widget = QWidget()
        control_widget.setFixedWidth(400)  # Compact control panel
        control_layout = QVBoxLayout(control_widget)

        # Title and Export button row
        title_row = QHBoxLayout()

        title_label = QLabel("GLB Viewer Controls")
        title_label.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
            }
        """
        )
        title_row.addWidget(title_label)
        title_row.addStretch()  # Push buttons to the right

        # Mirror to Left Hand button
        self.mirror_button = QPushButton("🪞 Mirror to Left")
        self.mirror_button.setToolTip(
            "Clone current right hand pose to left hand and update body controls"
        )
        self.mirror_button.clicked.connect(self.mirror_to_left_hand)
        self.mirror_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
                margin-right: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """
        )
        title_row.addWidget(self.mirror_button)

        # Export button
        export_button = QPushButton("Export Values")
        export_button.clicked.connect(self.export_values)
        export_button.setStyleSheet(
            """
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
        """
        )
        title_row.addWidget(export_button)

        control_layout.addLayout(title_row)

        # Add sign language selection controls
        self.create_selection_controls(control_layout)

        # Create control group
        control_group = QGroupBox("Camera Settings")
        control_group.setStyleSheet(
            """
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
        """
        )

        group_layout = QGridLayout(control_group)

        # Create sliders with native system fonts
        self.create_slider_control(
            group_layout,
            "Scale",
            0,
            0.1,
            20.0,
            self.camera_scale,
            self.update_camera_scale,
        )
        self.create_slider_control(
            group_layout,
            "Distance",
            1,
            2.0,
            15.0,
            self.camera_distance,
            self.update_camera_distance,
        )

        # Character position controls
        self.create_slider_control(
            group_layout,
            "Pos-X",
            2,
            -5.0,
            5.0,
            self.character_x,
            self.update_character_x,
        )
        self.create_slider_control(
            group_layout,
            "Pos-Y",
            3,
            -5.0,
            5.0,
            self.character_y,
            self.update_character_y,
        )
        self.create_slider_control(
            group_layout,
            "Pos-Z",
            4,
            -5.0,
            5.0,
            self.character_z,
            self.update_character_z,
        )

        # Camera rotation controls
        self.create_slider_control(
            group_layout,
            "X-Rot",
            5,
            -180.0,
            180.0,
            self.camera_x_rot,
            self.update_camera_x_rot,
        )
        self.create_slider_control(
            group_layout,
            "Y-Rot",
            6,
            -180.0,
            180.0,
            self.camera_y_rot,
            self.update_camera_y_rot,
        )
        self.create_slider_control(
            group_layout,
            "Z-Rot",
            7,
            -180.0,
            180.0,
            self.camera_z_rot,
            self.update_camera_z_rot,
        )
        self.create_slider_control(
            group_layout,
            "Ambient",
            8,
            0.0,
            1.0,
            self.ambient_light,
            self.update_ambient_light,
        )

        # Reset button
        # Character Tilt Control
        tilt_label = QLabel("Character Tilt:")
        group_layout.addWidget(tilt_label, 9, 0)

        self.character_tilt_slider = QSlider(Qt.Orientation.Horizontal)
        self.character_tilt_slider.setMinimum(-45)  # Tilt backward
        self.character_tilt_slider.setMaximum(45)  # Tilt forward
        self.character_tilt_slider.setValue(0)  # Neutral
        self.character_tilt_slider.valueChanged.connect(self.update_character_tilt)
        group_layout.addWidget(self.character_tilt_slider, 9, 1)

        self.character_tilt_value = QLabel("0.0")
        self.character_tilt_value.setMinimumWidth(40)
        group_layout.addWidget(self.character_tilt_value, 9, 2)

        # Hand/Finger Outline Control
        outline_label = QLabel("Hand Outline:")
        group_layout.addWidget(outline_label, 10, 0)

        self.outline_intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.outline_intensity_slider.setMinimum(0)  # No outline
        self.outline_intensity_slider.setMaximum(100)  # Maximum outline
        self.outline_intensity_slider.setValue(30)  # Default outline
        self.outline_intensity_slider.valueChanged.connect(self.update_hand_outline)
        group_layout.addWidget(self.outline_intensity_slider, 10, 1)

        self.outline_value = QLabel("30")
        self.outline_value.setMinimumWidth(40)
        group_layout.addWidget(self.outline_value, 10, 2)

        reset_button = QPushButton("Reset All")
        reset_button.clicked.connect(self.reset_all_controls)
        reset_button.setStyleSheet(
            """
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
        """
        )
        group_layout.addWidget(reset_button, 11, 0, 1, 3)  # Span across 3 columns

        control_layout.addWidget(control_group)

        # Body Parts Control Table
        self.create_body_parts_table(control_layout)

        control_layout.addStretch()

        parent_layout.addWidget(control_widget)

    def create_selection_controls(self, parent_layout):
        """Create sign language, character, and sign selection dropdowns."""
        selection_group = QGroupBox("Sign Language Selection")
        selection_group.setStyleSheet(
            """
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
        """
        )

        selection_layout = QVBoxLayout(selection_group)

        # Language selection
        lang_layout = QHBoxLayout()
        lang_label = QLabel("Language:")
        lang_label.setStyleSheet("font-size: 12px; color: #555; min-width: 70px;")
        lang_layout.addWidget(lang_label)

        self.language_combo = QComboBox()
        self.language_combo.setStyleSheet(
            """
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
                font-size: 11px;
            }
        """
        )
        for lang in self.available_languages:
            display_name = f"{lang['flag']} {lang['name']} ({lang['code']})"
            self.language_combo.addItem(display_name, lang["code"])

        # Set default selection
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == self.current_language:
                self.language_combo.setCurrentIndex(i)
                break

        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        lang_layout.addWidget(self.language_combo)
        selection_layout.addLayout(lang_layout)

        # Sign selection
        sign_layout = QHBoxLayout()
        sign_label = QLabel("Sign:")
        sign_label.setStyleSheet("font-size: 12px; color: #555; min-width: 70px;")
        sign_layout.addWidget(sign_label)

        self.sign_combo = QComboBox()
        self.sign_combo.setStyleSheet(
            """
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
                font-size: 11px;
            }
        """
        )
        self.populate_signs_combo()
        self.sign_combo.currentTextChanged.connect(self.on_sign_changed)
        sign_layout.addWidget(self.sign_combo)
        selection_layout.addLayout(sign_layout)

        # Buttons layout
        buttons_layout = QHBoxLayout()

        # Apply Sign button
        apply_button = QPushButton("Apply Sign")
        apply_button.clicked.connect(self.apply_selected_sign)
        apply_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """
        )
        buttons_layout.addWidget(apply_button)

        # Test Joint Control button
        test_button = QPushButton("Test Joint")
        test_button.clicked.connect(self.test_basic_joint_control)
        test_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #EF6C00;
            }
        """
        )
        buttons_layout.addWidget(test_button)

        # Debug Nodes button
        debug_button = QPushButton("Debug Nodes")
        debug_button.clicked.connect(self.debug_character_nodes)
        debug_button.setStyleSheet(
            """
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
            QPushButton:pressed {
                background-color: #4A148C;
            }
        """
        )
        buttons_layout.addWidget(debug_button)

        selection_layout.addLayout(buttons_layout)

        parent_layout.addWidget(selection_group)

    def create_slider_control(
        self, layout, label_text, row, min_val, max_val, initial_value, callback
    ):
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
        slider_name = label_text.lower().replace("-", "_").replace(" ", "_") + "_slider"
        value_name = label_text.lower().replace("-", "_").replace(" ", "_") + "_value"
        setattr(self, slider_name, slider)
        setattr(self, value_name, value_label)

    def create_body_parts_table(self, parent_layout):
        """Create the body parts control table with HPR and XYZ controls in top-down layout."""
        # Create control group with consistent styling
        body_group = QGroupBox("Body Parts Control")
        body_group.setStyleSheet(
            """
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
        """
        )

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
            ("ForeArm", "Forearm rotation"),
            ("Hand", "Hand and wrist movement"),
            ("Fingers (Thumb)", "Thumb finger control"),
            ("Fingers (Index)", "Index finger control"),
            ("Fingers (Middle)", "Middle finger control"),
            ("Fingers (Ring)", "Ring finger control"),
            ("Fingers (Pinky)", "Pinky finger control"),
            ("Leg", "Upper leg and thigh movement"),
            ("Foot", "Foot and ankle movement"),
        ]

        # Create controls for each body part in top-down layout
        for part_name, description in body_parts:
            # Create a group for this body part
            part_group = QGroupBox(f"{part_name} - {description}")
            part_group.setStyleSheet(
                """
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
            """
            )

            part_layout = QVBoxLayout(part_group)
            part_layout.setSpacing(5)

            # Create controls based on body part type
            if part_name in ["Neck", "Spine"]:
                # Single joint controls (no left/right)
                single_controls = self.create_hpr_xyz_controls_with_labels(
                    part_name.lower()
                    .replace(" ", "_")
                    .replace("(", "")
                    .replace(")", ""),
                    part_name,
                )
                part_layout.addWidget(single_controls)
            else:
                # Left and right controls side by side
                controls_layout = QHBoxLayout()

                # Left side controls
                left_controls = self.create_hpr_xyz_controls_with_labels(
                    f"left_{part_name.lower().replace(' ', '_').replace('(', '').replace(')', '')}",
                    f"Left {part_name}",
                )
                # Right side controls
                right_controls = self.create_hpr_xyz_controls_with_labels(
                    f"right_{part_name.lower().replace(' ', '_').replace('(', '').replace(')', '')}",
                    f"Right {part_name}",
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
        title_label.setStyleSheet(
            "font-size: 10px; color: #333; font-weight: bold; background-color: #f8f8f8; padding: 2px; border: 1px solid #ddd;"
        )
        title_layout.addWidget(title_label)

        # Small reset button (no text, just an icon/symbol)
        reset_button = QPushButton("↻")
        reset_button.setStyleSheet(
            """
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
        """
        )
        reset_button.setToolTip(f"Reset {display_name} to default values")
        reset_button.clicked.connect(lambda: self.reset_body_part(part_name))
        title_layout.addWidget(reset_button)

        layout.addLayout(title_layout)

        # HPR Controls with individual labels
        hpr_label = QLabel("Rotation (HPR)")
        hpr_label.setStyleSheet("font-size: 9px; color: #666; font-weight: bold;")
        layout.addWidget(hpr_label)

        hpr_layout = QVBoxLayout()
        for i, axis in enumerate(["H", "P", "R"]):
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
            slider.setMaximum(1800)  # 180.0 * 10

            # Set initial value from natural pose data
            initial_value = 0
            if part_name in self.body_parts:
                initial_value = int(self.body_parts[part_name]["hpr"][i] * 10)
            slider.setValue(initial_value)
            slider.setFixedHeight(18)

            # Value label
            value_label = QLabel(f"{initial_value / 10.0:.1f}")
            value_label.setStyleSheet("font-size: 8px; color: #777; min-width: 30px;")
            value_label.setFixedWidth(30)

            # Connect to update function
            def make_update_func(p=part_name, idx=i, val_label=value_label):
                def update_func(v):
                    val = v / 10.0
                    val_label.setText(f"{val:.1f}")
                    self.update_body_part(p, "hpr", idx, val)

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
        for i, axis in enumerate(["X", "Y", "Z"]):
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
            slider.setMaximum(1800)  # 180.0 * 10

            # Set initial value from natural pose data
            initial_value = 0
            if part_name in self.body_parts:
                initial_value = int(self.body_parts[part_name]["xyz"][i] * 10)
            slider.setValue(initial_value)
            slider.setFixedHeight(18)

            # Value label
            value_label = QLabel(f"{initial_value / 10.0:.1f}")
            value_label.setStyleSheet("font-size: 8px; color: #777; min-width: 30px;")
            value_label.setFixedWidth(30)

            # Connect to update function
            def make_update_func(p=part_name, idx=i, val_label=value_label):
                def update_func(v):
                    val = v / 10.0
                    val_label.setText(f"{val:.1f}")
                    self.update_body_part(p, "xyz", idx, val)

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
        """Reset a specific body part to its natural pose values."""
        if part_name not in self.body_parts:
            return

        try:
            # Get natural pose values from service
            from helpmesign.utils.natural_pose_service import (
                NaturalPoseService,
            )

            pose_service = NaturalPoseService()
            natural_pose_data = pose_service.get_all_body_parts_pose()

            # Reset to natural pose values if available, otherwise zero
            if part_name in natural_pose_data:
                self.body_parts[part_name]["hpr"] = natural_pose_data[part_name][
                    "hpr"
                ].copy()
                self.body_parts[part_name]["xyz"] = natural_pose_data[part_name][
                    "xyz"
                ].copy()
            else:
                self.body_parts[part_name]["hpr"] = [0.0, 0.0, 0.0]
                self.body_parts[part_name]["xyz"] = [0.0, 0.0, 0.0]

            # Reset all sliders to natural pose values
            for i, axis in enumerate(["h", "p", "r"]):
                slider_name = f"{part_name}_hpr_{axis}_slider"
                if hasattr(self, slider_name):
                    value = int(
                        self.body_parts[part_name]["hpr"][i] * 10
                    )  # Convert to slider scale
                    getattr(self, slider_name).setValue(value)

            for i, axis in enumerate(["x", "y", "z"]):
                slider_name = f"{part_name}_xyz_{axis}_slider"
                if hasattr(self, slider_name):
                    value = int(
                        self.body_parts[part_name]["xyz"][i] * 10
                    )  # Convert to slider scale
                    getattr(self, slider_name).setValue(value)

            # Apply the natural pose values to the joint
            gltf_joint_name = self.get_gltf_joint_name(part_name)
            if gltf_joint_name and self.character:
                try:
                    joint = self.character.controlJoint(
                        None, "modelRoot", gltf_joint_name
                    )
                    if joint and not joint.isEmpty():
                        # Apply the natural pose HPR values
                        hpr_values = self.body_parts[part_name]["hpr"]
                        joint.setHpr(hpr_values[0], hpr_values[1], hpr_values[2])

                        # Apply XYZ values relative to original position
                        original_pos = self.get_original_joint_position(gltf_joint_name)
                        if original_pos:
                            xyz_values = self.body_parts[part_name]["xyz"]
                            joint.setPos(
                                original_pos[0] + xyz_values[0],
                                original_pos[1] + xyz_values[1],
                                original_pos[2] + xyz_values[2],
                            )

                        self.character.update()
                        print(
                            f"Reset {part_name} to natural pose: HPR={hpr_values}, XYZ={xyz_values}"
                        )
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
            hpr_values = self.body_parts[part_name]["hpr"]
            xyz_values = self.body_parts[part_name]["xyz"]

            # Apply transformations to the joint

            # Apply HPR transformation
            joint.setHpr(hpr_values[0], hpr_values[1], hpr_values[2])

            # Apply XYZ transformation (relative to original position)
            original_pos = self.get_original_joint_position(gltf_joint_name)
            if original_pos:
                joint.setPos(
                    original_pos[0] + xyz_values[0],
                    original_pos[1] + xyz_values[1],
                    original_pos[2] + xyz_values[2],
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
                        original_pos[2] + xyz_values[2],
                    )
                return True
        except Exception as e:
            pass

        return False

    def find_bone_node(self, part_name):
        """Find a bone node for the specified body part."""
        # Try to find bone nodes with names related to the body part
        bone_patterns = {
            "neck": ["neck", "head"],
            "spine": ["spine", "back", "torso"],
            "left_shoulder": ["left", "shoulder", "l_shoulder"],
            "right_shoulder": ["right", "shoulder", "r_shoulder"],
            "left_arm": ["left", "arm", "l_arm"],
            "right_arm": ["right", "arm", "r_arm"],
            "left_hand": ["left", "hand", "l_hand"],
            "right_hand": ["right", "hand", "r_hand"],
            "left_leg": ["left", "leg", "thigh", "l_leg"],
            "right_leg": ["right", "leg", "thigh", "r_leg"],
            "left_foot": ["left", "foot", "l_foot"],
            "right_foot": ["right", "foot", "r_foot"],
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

    def get_joint_name_from_part(self, part_name):
        """Convert part name to joint name using discovered joints."""
        # Only use joints that actually exist in the Panda3D scene
        # Based on discovery, only these nodes exist: Armature, Beta_Joints, Beta_Surface
        joint_mapping = {
            "neck": "Beta_Joints",
            "spine": "Beta_Joints",
            "left_shoulder": "Beta_Joints",
            "right_shoulder": "Beta_Joints",
            "left_arm": "Beta_Joints",
            "right_arm": "Beta_Joints",
            "left_hand": "Beta_Joints",
            "right_hand": "Beta_Joints",
            "left_fingers_thumb": "Beta_Joints",
            "right_fingers_thumb": "Beta_Joints",
            "left_fingers_index": "Beta_Joints",
            "right_fingers_index": "Beta_Joints",
            "left_fingers_middle": "Beta_Joints",
            "right_fingers_middle": "Beta_Joints",
            "left_fingers_ring": "Beta_Joints",
            "right_fingers_ring": "Beta_Joints",
            "left_fingers_pinky": "Beta_Joints",
            "right_fingers_pinky": "Beta_Joints",
            "left_leg": "Beta_Joints",
            "right_leg": "Beta_Joints",
            "left_foot": "Beta_Joints",
            "right_foot": "Beta_Joints",
        }

        # Try the original mapping first
        joint_name = joint_mapping.get(part_name)
        if (
            joint_name
            and hasattr(self, "discovered_joints")
            and joint_name in self.discovered_joints
        ):
            return joint_name

        # If not found, try to find a similar joint
        if hasattr(self, "discovered_joints"):
            similar_joint = self.find_similar_joint(part_name)
            if similar_joint:
                return similar_joint.getName()

        return joint_name

    def find_alternative_joint(self, part_name):
        """Try to find alternative joint names if the primary one doesn't exist."""
        alternatives = {
            "neck": ["Beta_Joints", "Armature"],
            "spine": ["Beta_Joints", "Armature"],
            "left_shoulder": ["Beta_Joints", "Armature"],
            "right_shoulder": ["Beta_Joints", "Armature"],
            "left_arm": ["Beta_Joints", "Armature"],
            "right_arm": ["Beta_Joints", "Armature"],
            "left_hand": ["Beta_Joints", "Armature"],
            "right_hand": ["Beta_Joints", "Armature"],
            "left_fingers_thumb": ["Beta_Joints", "Armature"],
            "right_fingers_thumb": ["Beta_Joints", "Armature"],
            "left_fingers_index": ["Beta_Joints", "Armature"],
            "right_fingers_index": ["Beta_Joints", "Armature"],
            "left_fingers_middle": ["Beta_Joints", "Armature"],
            "right_fingers_middle": ["Beta_Joints", "Armature"],
            "left_fingers_ring": ["Beta_Joints", "Armature"],
            "right_fingers_ring": ["Beta_Joints", "Armature"],
            "left_fingers_pinky": ["Beta_Joints", "Armature"],
            "right_fingers_pinky": ["Beta_Joints", "Armature"],
            "left_leg": ["Beta_Joints", "Armature"],
            "right_leg": ["Beta_Joints", "Armature"],
            "left_foot": ["Beta_Joints", "Armature"],
            "right_foot": ["Beta_Joints", "Armature"],
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
            if "left_arm" in part_name and (
                "arm" in child_name or "shoulder" in child_name
            ):
                return child
            elif "right_arm" in part_name and (
                "arm" in child_name or "shoulder" in child_name
            ):
                return child
            elif "left_hand" in part_name and "hand" in child_name:
                return child
            elif "right_hand" in part_name and "hand" in child_name:
                return child
            elif "left_leg" in part_name and (
                "leg" in child_name or "thigh" in child_name
            ):
                return child
            elif "right_leg" in part_name and (
                "leg" in child_name or "thigh" in child_name
            ):
                return child
            elif "left_foot" in part_name and "foot" in child_name:
                return child
            elif "right_foot" in part_name and "foot" in child_name:
                return child

        # If no specific child found, return the first child (if any)
        if parent_joint.getNumChildren() > 0:
            return parent_joint.getChild(0)

        return None

    def get_gltf_joint_name(self, part_name):
        """Get the GLTF joint name for a body part."""
        gltf_mapping = {
            "neck": "mixamorig:Neck",
            "spine": "mixamorig:Spine",
            "left_shoulder": "mixamorig:LeftShoulder",
            "right_shoulder": "mixamorig:RightShoulder",
            "left_arm": "mixamorig:LeftArm",
            "right_arm": "mixamorig:RightArm",
            "left_forearm": "mixamorig:LeftForeArm",
            "right_forearm": "mixamorig:RightForeArm",
            "left_hand": "mixamorig:LeftHand",
            "right_hand": "mixamorig:RightHand",
            "left_fingers_thumb": "mixamorig:LeftHandThumb1",
            "right_fingers_thumb": "mixamorig:RightHandThumb1",
            "left_fingers_index": "mixamorig:LeftHandIndex1",
            "right_fingers_index": "mixamorig:RightHandIndex1",
            "left_fingers_middle": "mixamorig:LeftHandMiddle1",
            "right_fingers_middle": "mixamorig:RightHandMiddle1",
            "left_fingers_ring": "mixamorig:LeftHandRing1",
            "right_fingers_ring": "mixamorig:RightHandRing1",
            "left_fingers_pinky": "mixamorig:LeftHandPinky1",
            "right_fingers_pinky": "mixamorig:RightHandPinky1",
            "left_leg": "mixamorig:LeftUpLeg",
            "right_leg": "mixamorig:RightUpLeg",
            "left_foot": "mixamorig:LeftFoot",
            "right_foot": "mixamorig:RightFoot",
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
            f"mixamorig:Bone_{joint_index}",
        ]

        for joint_name in joint_names_to_try:
            if self.character is None:
                return None
            joint = self.character.find(f"**/{joint_name}")
            if joint and not joint.isEmpty():
                return joint

        return None

    def get_original_joint_position(self, joint_name):
        """Get the original position of a joint (for XYZ transformations)."""
        # Store original positions when the character is first loaded
        if not hasattr(self, "original_joint_positions"):
            self.original_joint_positions = {}

        if joint_name not in self.original_joint_positions:
            # Try to get the joint using controlJoint method
            try:
                joint = self.character.controlJoint(None, "modelRoot", joint_name)
                if joint and not joint.isEmpty():
                    pos = joint.getPos()
                    self.original_joint_positions[joint_name] = {
                        "hpr": joint.getHpr(),
                        "pos": pos,
                    }
                else:
                    return None
            except:
                return None

        # Return the position from the stored data
        joint_data = self.original_joint_positions.get(joint_name)
        if joint_data and "pos" in joint_data:
            return joint_data["pos"]
        return None

    def init_panda3d(self):
        """Initialize Panda3D in offscreen mode."""
        try:
            # Configure Panda3D for offscreen rendering (same as learn module)
            loadPrcFileData("", "window-type offscreen")
            loadPrcFileData("", "sync-video 0")
            loadPrcFileData("", "framebuffer-srgb true")
            loadPrcFileData(
                "", "framebuffer-alpha true"
            )  # Enable alpha for transparent background
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
            glb_path = os.path.join(
                project_root, "resources", "characters", "arivo.glb"
            )
            self.load_glb(glb_path)

            self.panda_ready = True

        except Exception as e:
            print(f"Error initializing Panda3D: {e}")

    def setup_scene(self):
        """Set up the Panda3D scene."""
        self.showbase.setBackgroundColor(0, 0, 0, 0)  # Transparent background

        # Set up lighting
        ambient_light = AmbientLight("ambient_light")
        ambient_light.setColor(
            VBase4(self.ambient_light, self.ambient_light, self.ambient_light, 1)
        )  # Use default ambient light value
        self.ambient_light_node = self.showbase.render.attachNewNode(ambient_light)
        self.showbase.render.setLight(self.ambient_light_node)

        directional_light = DirectionalLight("directional_light")
        directional_light.setColor(VBase4(1.0, 1.0, 1.0, 1))  # Brighter directional
        directional_light.setDirection(Vec3(-1, -1, -1))
        directional_light_node = self.showbase.render.attachNewNode(directional_light)
        self.showbase.render.setLight(directional_light_node)

        # Set up camera with default values
        self.camera = self.showbase.camera
        # Apply default camera values
        self.camera.setPos(0, -self.camera_distance, 1)
        self.camera.setHpr(self.camera_x_rot, self.camera_y_rot, self.camera_z_rot)
        self.camera.lookAt(0, 0, 1)  # Look at character center height

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
            self.character.setScale(self.camera_scale)  # Use default scale
            self.character.reparentTo(self.showbase.render)

            # Apply camera settings after character is loaded
            if self.camera:
                self.camera.setPos(0, -self.camera_distance, 1)
                self.camera.setHpr(
                    self.camera_x_rot, self.camera_y_rot, self.camera_z_rot
                )

            # Initialize original joint positions for body part controls
            self.initialize_joint_positions()

            # Apply natural pose if available
            # self.apply_natural_pose()

        except Exception as e:
            print(f"Error loading GLB file: {e}")

    def initialize_joint_positions(self):
        """Initialize and store original joint positions for all body part joints."""
        if not self.character:
            return

        self.original_joint_positions: Dict[str, Dict[str, Any]] = {}

        # First, discover all available joints in the character
        # self.discover_joints()

        # Get natural pose data
        from helpmesign.utils.natural_pose_service import (
            NaturalPoseService,
        )

        pose_service = NaturalPoseService()
        natural_pose = pose_service.get_natural_pose_data()

        for part_name in self.body_part_names:
            gltf_joint_name = self.get_gltf_joint_name(part_name)
            if gltf_joint_name:
                try:
                    # Get the joint using controlJoint method
                    joint = self.character.controlJoint(
                        None, "modelRoot", gltf_joint_name
                    )
                    if joint and not joint.isEmpty():
                        # Store original HPR and position
                        original_hpr = joint.getHpr()
                        original_pos = joint.getPos()
                        self.original_joint_positions[gltf_joint_name] = {
                            "hpr": original_hpr,
                            "pos": original_pos,
                        }

                        # Apply natural pose using slider values from self.body_parts
                        # Find the corresponding body part for this joint
                        body_part_name = None
                        for part_name, part_gltf_name in [
                            ("neck", "mixamorig:Neck"),
                            ("spine", "mixamorig:Spine"),
                            # ('left_shoulder', 'mixamorig:LeftShoulder'),
                            # ('right_shoulder', 'mixamorig:RightShoulder'),
                            ("left_arm", "mixamorig:LeftArm"),
                            ("right_arm", "mixamorig:RightArm"),
                            ("left_forearm", "mixamorig:LeftForeArm"),
                            ("right_forearm", "mixamorig:RightForeArm"),
                            ("left_hand", "mixamorig:LeftHand"),
                            ("right_hand", "mixamorig:RightHand"),
                            ("left_fingers_thumb", "mixamorig:LeftHandThumb1"),
                            ("right_fingers_thumb", "mixamorig:RightHandThumb1"),
                            ("left_fingers_index", "mixamorig:LeftHandIndex1"),
                            ("right_fingers_index", "mixamorig:RightHandIndex1"),
                            ("left_fingers_middle", "mixamorig:LeftHandMiddle1"),
                            ("right_fingers_middle", "mixamorig:RightHandMiddle1"),
                            ("left_fingers_ring", "mixamorig:LeftHandRing1"),
                            ("right_fingers_ring", "mixamorig:RightHandRing1"),
                            ("left_fingers_pinky", "mixamorig:LeftHandPinky1"),
                            ("right_fingers_pinky", "mixamorig:RightHandPinky1"),
                            # ('left_leg', 'mixamorig:LeftUpLeg'),
                            # ('right_leg', 'mixamorig:RightUpLeg'),
                            ("left_foot", "mixamorig:LeftFoot"),
                            ("right_foot", "mixamorig:RightFoot"),
                        ]:
                            if gltf_joint_name == part_gltf_name:
                                body_part_name = part_name
                                break

                        # Apply slider values if we found a matching body part
                        if body_part_name and body_part_name in self.body_parts:
                            body_part_data = self.body_parts[body_part_name]
                            hpr = body_part_data["hpr"]
                            xyz = body_part_data["xyz"]

                            # Apply HPR values
                            joint.setHpr(hpr[0], hpr[1], hpr[2])

                            # Apply XYZ values relative to original position
                            original_pos = self.original_joint_positions[
                                gltf_joint_name
                            ]["pos"]
                            joint.setPos(
                                original_pos[0] + xyz[0],
                                original_pos[1] + xyz[1],
                                original_pos[2] + xyz[2],
                            )

                except Exception as e:
                    print(f"Could not initialize position for {gltf_joint_name}: {e}")

        # Update the character after applying all natural poses
        self.character.update()
        print("Natural pose applied during initialization")

    def discover_joints(self):
        """Discover all joints in the character model using GLTF extraction."""
        if not self.character:
            return

        # Try GLTF-based joint extraction first
        glb_path = os.path.join(
            os.path.dirname(__file__), "resources", "characters", "arivo.glb"
        )
        joint_hierarchy, root_joints = build_joint_hierarchy(glb_path)

        if joint_hierarchy and root_joints:

            # Store the GLTF joint data
            self.gltf_joint_hierarchy = joint_hierarchy
            self.gltf_root_joints = root_joints

            # Explore the skeleton system
            self.explore_skeleton_system()

            # Extract joint names for compatibility
            self.discovered_joints = [
                joint["name"] for joint in joint_hierarchy.values()
            ]

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
                    simple_name = joint_name.replace("mixamorig:", "")
                    panda_node = self.character.find(f"**/{simple_name}")
                    if panda_node and not panda_node.isEmpty():
                        self.gltf_to_panda_mapping[joint_name] = panda_node
                    else:
                        print(
                            f"Could not find Panda3D node for GLTF joint: {joint_name}"
                        )
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
                if node.hasPythonTag("Character"):
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
                        if hasattr(skeleton_node, "getNumJoints"):
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
        if not hasattr(self, "discovered_joints"):
            return None

        target_lower = target_name.lower()

        # Look for exact matches first
        for joint_name in self.discovered_joints:
            if joint_name.lower() == target_lower:
                return self.character.find(f"**/{joint_name}")

        # Look for partial matches
        for joint_name in self.discovered_joints:
            joint_lower = joint_name.lower()
            if target_lower in joint_lower or joint_lower in target_lower:
                return self.character.find(f"**/{joint_name}")

        # Look for common patterns
        patterns = {
            "shoulder": ["shoulder", "arm", "clavicle"],
            "arm": ["arm", "forearm", "elbow"],
            "hand": ["hand", "wrist"],
            "thumb": ["thumb"],
            "index": ["index"],
            "middle": ["middle"],
            "ring": ["ring"],
            "pinky": ["pinky", "little"],
            "leg": ["leg", "thigh", "femur"],
            "hip": ["hip", "pelvis"],
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
        parent_process
        # if not self.character:
        #     return

        # try:
        #     # Set neck pose directly - very small value to avoid distortion
        #     neck_joint = self.character.controlJoint(None, "modelRoot", "mixamorig:Neck")
        #     if neck_joint and not neck_joint.isEmpty():
        #         # Set a small neck pitch (4 degrees instead of 40)
        #         neck_joint.setHpr(0, 40, 0)

        #     from helpmesign.utils.natural_pose_service import NaturalPoseService
        #     pose_service = NaturalPoseService()
        #     natural_pose = pose_service.get_natural_pose_data()

        #     if not natural_pose:
        #         print("No natural pose data available")
        #         return

        #     for joint_name, pose_data in natural_pose.items():
        #         print("Debug: ", joint_name, pose_data);
        #         joint = self.character.controlJoint(None, "modelRoot", joint_name)
        #         if joint and not joint.isEmpty():
        #             print("Debug: ", joint_name, pose_data['hpr'][0], pose_data['hpr'][1], pose_data['hpr'][2]);
        #             # joint.setHpr(pose_data['hpr'][0], pose_data['hpr'][1], pose_data['hpr'][2])
        #     #     joint = self.character.controlJoint(None, "modelRoot", joint_name)
        #     #     if joint and not joint.isEmpty():
        #     #         # print("Debug: ", joint.setHpr(pose_data['hpr'][0], pose_data['hpr'][1], pose_data['hpr'][2]));
        #     #         print("Debug: ", joint_name, pose_data['hpr'][0], pose_data['hpr'][1], pose_data['hpr'][2]);
        #     #         joint.setHpr(pose_data['hpr'][0], pose_data['hpr'][1], pose_data['hpr'][2])

        #     self.character.update()
        # except Exception as e:
        #     print(f"Error setting neck pose: {e}")

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
                                bytes(data),
                                width,
                                height,
                                stride,
                                QImage.Format_RGBA8888,
                            ).mirrored(False, True)

                        # Scale to full display size
                        display_size = self.display_label.size()
                        display_img = img.scaled(
                            display_size.width(),
                            display_size.height(),
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation,
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
                            display_size.width(),
                            display_size.height(),
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation,
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
            # Keep camera at current distance setting
            self.camera.setPos(0, -self.camera_distance, 1)
        self.scale_value.setText(f"{value:.1f}")

    def update_camera_distance(self, value):
        """Update camera distance."""
        self.camera_distance = value
        if self.camera:
            # Simple distance control - just move camera closer/further
            self.camera.setPos(0, -value, 1)
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
            self.camera_scale = defaults["camera_scale"]
            self.camera_distance = defaults["camera_distance"]
            self.camera_x_rot = defaults["camera_x_rot"]
            self.camera_y_rot = defaults["camera_y_rot"]
            self.camera_z_rot = defaults["camera_z_rot"]
            self.ambient_light = defaults["ambient_light"]
            self.character_x = defaults["character_x"]
            self.character_y = defaults["character_y"]
            self.character_z = defaults["character_z"]

            # Reset new controls
            if hasattr(self, "character_tilt_slider"):
                self.character_tilt_slider.setValue(0)
            if hasattr(self, "outline_intensity_slider"):
                self.outline_intensity_slider.setValue(30)

            # Update sliders (with error handling)
            slider_names = [
                "scale",
                "distance",
                "x_rot",
                "y_rot",
                "z_rot",
                "ambient",
                "pos_x",
                "pos_y",
                "pos_z",
            ]
            slider_values = [
                self.camera_scale,
                self.camera_distance,
                self.camera_x_rot,
                self.camera_y_rot,
                self.camera_z_rot,
                self.ambient_light,
                self.character_x,
                self.character_y,
                self.character_z,
            ]

            for name, value in zip(slider_names, slider_values):
                slider_attr = f"{name}_slider"
                value_attr = f"{name}_value"
                if hasattr(self, slider_attr):
                    getattr(self, slider_attr).setValue(int(value * 100))
                if hasattr(self, value_attr):
                    getattr(self, value_attr).setText(f"{value:.1f}")

            # Reset all body part controls to natural pose values
            natural_pose_data = defaults["body_parts"]
            for part_name in self.body_parts:
                if part_name in natural_pose_data:
                    self.body_parts[part_name]["hpr"] = natural_pose_data[part_name][
                        "hpr"
                    ].copy()
                    self.body_parts[part_name]["xyz"] = natural_pose_data[part_name][
                        "xyz"
                    ].copy()
                else:
                    self.body_parts[part_name]["hpr"] = [0.0, 0.0, 0.0]
                    self.body_parts[part_name]["xyz"] = [0.0, 0.0, 0.0]

            # Reset all body part sliders to natural pose values
            for part_name in self.body_parts:
                # Reset HPR sliders to natural pose values
                for i, axis in enumerate(["h", "p", "r"]):
                    slider_attr = f"{part_name}_hpr_{axis}_slider"
                    if hasattr(self, slider_attr):
                        value = int(
                            self.body_parts[part_name]["hpr"][i] * 10
                        )  # Convert to slider scale
                        getattr(self, slider_attr).setValue(value)

                # Reset XYZ sliders to natural pose values
                for i, axis in enumerate(["x", "y", "z"]):
                    slider_attr = f"{part_name}_xyz_{axis}_slider"
                    if hasattr(self, slider_attr):
                        value = int(
                            self.body_parts[part_name]["xyz"][i] * 10
                        )  # Convert to slider scale
                        getattr(self, slider_attr).setValue(value)

            # Reset all joints to their original positions and rotations
            if self.character and hasattr(self, "original_joint_positions"):
                for joint_name, original_data in self.original_joint_positions.items():
                    try:
                        joint = self.character.controlJoint(
                            None, "modelRoot", joint_name
                        )
                        if joint and not joint.isEmpty():
                            # Restore original HPR and position
                            joint.setHpr(original_data["hpr"])
                            joint.setPos(original_data["pos"])
                            print(f"Reset joint {joint_name} to original position")
                    except Exception as e:
                        print(f"Could not reset joint {joint_name}: {e}")

                # Update the character after all joint resets
                self.character.update()

            # Apply changes to 3D scene
            if self.character:
                self.character.setPos(
                    self.character_x, self.character_y, self.character_z
                )
                self.character.setScale(self.camera_scale)

            if self.camera:
                self.camera.setPos(0, -self.camera_distance, 1)
                self.camera.setHpr(
                    self.camera_x_rot, self.camera_y_rot, self.camera_z_rot
                )

            if self.ambient_light_node:
                light = self.ambient_light_node.node()
                if light:
                    light.setColor(
                        VBase4(
                            self.ambient_light,
                            self.ambient_light,
                            self.ambient_light,
                            1,
                        )
                    )

        except Exception as e:
            print(f"Error in reset function: {e}")

    def export_values(self):
        """Export current control values including both right and left hand data to clipboard and console."""
        try:
            # Separate right hand and left hand data for clarity
            right_hand_parts = {}
            left_hand_parts = {}
            other_parts = {}

            for part_name, part_data in self.body_parts.items():
                if "Right" in part_name and any(
                    hand_part in part_name
                    for hand_part in [
                        "Arm",
                        "Hand",
                        "Thumb",
                        "Index",
                        "Middle",
                        "Ring",
                        "Pinky",
                    ]
                ):
                    right_hand_parts[part_name] = part_data
                elif "Left" in part_name and any(
                    hand_part in part_name
                    for hand_part in [
                        "Arm",
                        "Hand",
                        "Thumb",
                        "Index",
                        "Middle",
                        "Ring",
                        "Pinky",
                    ]
                ):
                    left_hand_parts[part_name] = part_data
                else:
                    other_parts[part_name] = part_data

            # Get current values
            current_values = {
                "camera_scale": self.camera_scale,
                "camera_distance": self.camera_distance,
                "camera_x_rot": self.camera_x_rot,
                "camera_y_rot": self.camera_y_rot,
                "camera_z_rot": self.camera_z_rot,
                "ambient_light": self.ambient_light,
                "character_x": self.character_x,
                "character_y": self.character_y,
                "character_z": self.character_z,
                "character_tilt": (
                    getattr(self, "character_tilt_slider", {}).value()
                    if hasattr(self, "character_tilt_slider")
                    else 0
                ),
                "hand_outline": (
                    getattr(self, "outline_intensity_slider", {}).value()
                    if hasattr(self, "outline_intensity_slider")
                    else 30
                ),
                "right_hand_parts": right_hand_parts,
                "left_hand_parts": left_hand_parts,
                "other_body_parts": other_parts,
                "all_body_parts": self.body_parts,  # Keep original format for compatibility
            }

            # Create formatted string for export
            export_text = "def get_default_values(self):\n"
            export_text += '    """Get the default values for all controls."""\n'
            export_text += "    return {\n"

            # Export basic controls
            for key, value in current_values.items():
                if key != "body_parts":
                    export_text += f"        '{key}': {value},\n"

            # Export body parts
            export_text += "        'body_parts': {\n"
            for part_name, part_data in current_values["body_parts"].items():
                export_text += f"            '{part_name}': {{\n"
                export_text += f"                'hpr': {part_data['hpr']},\n"
                export_text += f"                'xyz': {part_data['xyz']}\n"
                export_text += f"            }},\n"
            export_text += "        }\n"
            export_text += "    }"

            # Print to console
            print("\n" + "=" * 50)
            print("EXPORTED CONTROL VALUES:")
            print("=" * 50)
            print(export_text)
            print("=" * 50)
            print("Copy the above code to replace your get_default_values() function")
            print("=" * 50 + "\n")

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

    def populate_signs_combo(self):
        """Populate the signs combo box with available signs for the current language."""
        self.sign_combo.clear()
        self.sign_combo.addItem("-- Select a Sign --", None)

        # Separate letters and numbers for better sorting
        letters = {k: v for k, v in self.available_signs.items() if k.isalpha()}
        numbers = {k: v for k, v in self.available_signs.items() if k.isdigit()}

        # Sort letters alphabetically and numbers numerically
        sorted_letters = sorted(letters.items(), key=lambda x: x[0])
        sorted_numbers = sorted(numbers.items(), key=lambda x: int(x[0]))

        # Add numbers first (0-9), then letters (A-Z)
        for number, sign_data in sorted_numbers:
            self.sign_combo.addItem(number, sign_data)

        for letter, sign_data in sorted_letters:
            self.sign_combo.addItem(letter, sign_data)

    def on_language_changed(self):
        """Handle language selection change."""
        current_data = self.language_combo.currentData()
        if current_data:
            self.current_language = current_data
            self.available_signs = self.load_available_signs(self.current_language)
            self.populate_signs_combo()

            # Reinitialize pose generator for the new language
            self._initialize_pose_generator()

            print(f"Language changed to: {self.current_language}")

    def on_sign_changed(self):
        """Handle sign selection change."""
        current_data = self.sign_combo.currentData()
        if current_data:
            # Update description or show instructions
            instructions = current_data.get("instructions", "")
            description = current_data.get("description", "")
            if instructions or description:
                print(f"Sign: {current_data.get('letter', 'Unknown')}")
                if description:
                    print(f"Description: {description}")
                if instructions:
                    print(f"Instructions: {instructions}")

    def apply_selected_sign(self):
        """Apply the selected sign pose to the character using universal pose generator."""
        current_data = self.sign_combo.currentData()
        if not current_data or not self.character:
            print("❌ No sign selected or character not loaded")
            return

        # Get instruction from sign data
        instruction = current_data.get("instructions", "")
        if not instruction:
            print("❌ No instructions available for selected sign")
            return

        # Generate pose from instruction using universal generator
        if not self.pose_generator:
            print("❌ Pose generator not available")
            return

        print(f"🎭 Generating pose from instruction: {instruction}")
        pose_data = self.pose_generator.generate_universal_pose(
            instruction, hand="right"
        )

        if not pose_data:
            print("❌ Could not generate pose from instruction")
            return

        print(
            f"🎭 Applying sign: {current_data.get('letter', 'Unknown')} ({current_data.get('hand', 'unknown')} hand)"
        )
        print(f"📝 Pose has {len(pose_data)} joint definitions")

        # Debug: Check if character is loaded properly
        if self.character:
            print(f"✅ Character loaded: {type(self.character)}")
        else:
            print("❌ Character is None!")
            return

        # First, reset to natural pose to ensure we start from a clean state
        print("🔄 Resetting to natural pose first...")
        self.reset_to_natural_pose_for_sign()

        # Apply pose to character joints (SAFE MODE - skip problematic joints)
        applied_count = 0
        not_found_count = 0
        error_count = 0
        skipped_count = 0

        # Define safe joints (arms, hands, fingers only - skip shoulders, legs, spine)
        safe_joints = [
            "mixamorig:RightArm",
            "mixamorig:LeftArm",
            "mixamorig:RightForeArm",
            "mixamorig:LeftForeArm",
            "mixamorig:RightHand",
            "mixamorig:LeftHand",
            # All finger joints
            "mixamorig:RightHandThumb1",
            "mixamorig:RightHandThumb2",
            "mixamorig:RightHandThumb3",
            "mixamorig:RightHandThumb4",
            "mixamorig:LeftHandThumb1",
            "mixamorig:LeftHandThumb2",
            "mixamorig:LeftHandThumb3",
            "mixamorig:LeftHandThumb4",
            "mixamorig:RightHandIndex1",
            "mixamorig:RightHandIndex2",
            "mixamorig:RightHandIndex3",
            "mixamorig:RightHandIndex4",
            "mixamorig:LeftHandIndex1",
            "mixamorig:LeftHandIndex2",
            "mixamorig:LeftHandIndex3",
            "mixamorig:LeftHandIndex4",
            "mixamorig:RightHandMiddle1",
            "mixamorig:RightHandMiddle2",
            "mixamorig:RightHandMiddle3",
            "mixamorig:RightHandMiddle4",
            "mixamorig:LeftHandMiddle1",
            "mixamorig:LeftHandMiddle2",
            "mixamorig:LeftHandMiddle3",
            "mixamorig:LeftHandMiddle4",
            "mixamorig:RightHandRing1",
            "mixamorig:RightHandRing2",
            "mixamorig:RightHandRing3",
            "mixamorig:RightHandRing4",
            "mixamorig:LeftHandRing1",
            "mixamorig:LeftHandRing2",
            "mixamorig:LeftHandRing3",
            "mixamorig:LeftHandRing4",
            "mixamorig:RightHandPinky1",
            "mixamorig:RightHandPinky2",
            "mixamorig:RightHandPinky3",
            "mixamorig:RightHandPinky4",
            "mixamorig:LeftHandPinky1",
            "mixamorig:LeftHandPinky2",
            "mixamorig:LeftHandPinky3",
            "mixamorig:LeftHandPinky4",
        ]

        # Debug: Show all joints that the pose generator created
        print(f"🔍 DEBUG: Pose generator created {len(pose_data)} joints:")
        for joint_name in pose_data.keys():
            print(f"  - {joint_name}")

        print(f"🔍 DEBUG: Checking against safe joints filter...")

        for joint_name, hpr_values in pose_data.items():
            # Skip problematic joints that cause major distortions
            if joint_name not in safe_joints:
                print(
                    f"⚠️ SKIPPED {joint_name}: Not in safe joints list (POTENTIAL BUG SOURCE)"
                )
                # Check if this is a problematic joint type
                if any(
                    problem in joint_name.lower()
                    for problem in ["shoulder", "leg", "spine", "hip", "neck", "head"]
                ):
                    print(
                        f"🚨 ALERT: {joint_name} is a problematic joint type that should not be generated!"
                    )
                skipped_count += 1
                continue

            try:
                # Use controlJoint method like the body part controls
                joint = self.character.controlJoint(None, "modelRoot", joint_name)
                if joint and not joint.isEmpty():
                    # Apply HPR values (assuming pose data is in [H, P, R] format)
                    if isinstance(hpr_values, list) and len(hpr_values) >= 3:
                        # Store original values for comparison
                        original_hpr = joint.getHpr()
                        joint.setHpr(hpr_values[0], hpr_values[1], hpr_values[2])
                        new_hpr = joint.getHpr()
                        applied_count += 1
                        print(
                            f"✅ {joint_name}: {hpr_values} (was: {[round(x, 1) for x in original_hpr]}, now: {[round(x, 1) for x in new_hpr]})"
                        )

                        # Update UI sliders to reflect the applied pose
                        self.update_ui_for_applied_joint(joint_name, hpr_values)
                    else:
                        print(f"❌ Invalid pose data for {joint_name}: {hpr_values}")
                        error_count += 1
                else:
                    print(f"❌ Joint not found: {joint_name}")
                    not_found_count += 1
            except Exception as e:
                print(f"❌ Error applying pose to {joint_name}: {e}")
                error_count += 1

        # Summary
        print(f"\n📊 Pose Application Results:")
        print(f"  ✅ Applied: {applied_count}")
        print(f"  ⚠️ Skipped: {skipped_count} (problematic joints)")
        print(f"  ❌ Not found: {not_found_count}")
        print(f"  ❌ Errors: {error_count}")
        print(
            f"  📈 Safe joints success rate: {applied_count / (len(pose_data) - skipped_count) * 100:.1f}%"
            if (len(pose_data) - skipped_count) > 0
            else "  📈 No safe joints to apply"
        )

        if applied_count > 0:
            # Update the character
            self.character.update()
            print(f"🔄 Character updated with {applied_count} joint changes")

            # Adjust camera to better see the sign (rotate around character)
            if self.camera:
                # Rotate camera to see the character from the front-right angle
                self.camera.setPos(
                    2, -self.camera_distance, 1
                )  # Move slightly to the right
                self.camera.lookAt(0, 0, 1)  # Look at character center
                print("📷 Adjusted camera to better view the sign")

            # Force a render update
            if hasattr(self, "render_frame"):
                self.render_frame()
                print("🎬 Forced render update")
        else:
            print("❌ No joints were successfully updated - character pose unchanged")

    def reset_to_natural_pose_for_sign(self):
        """Reset character to natural pose before applying a sign (SAFE JOINTS ONLY)."""
        try:
            # Get natural pose data
            from helpmesign.utils.natural_pose_service import (
                NaturalPoseService,
            )

            pose_service = NaturalPoseService()
            natural_pose_data = pose_service.get_all_body_parts_pose()

            # ONLY reset safe body parts (arms, hands, fingers - NO shoulders, legs, spine)
            safe_body_parts = [
                "right_arm",
                "left_arm",
                "right_forearm",
                "left_forearm",
                "right_hand",
                "left_hand",
                # Add finger parts if they exist in natural_pose_data
                "right_thumb",
                "left_thumb",
                "right_index_finger",
                "left_index_finger",
                "right_middle_finger",
                "left_middle_finger",
                "right_ring_finger",
                "left_ring_finger",
                "right_pinky_finger",
                "left_pinky_finger",
            ]

            reset_count = 0
            print("🔄 Resetting SAFE joints only (no shoulders/legs/spine)...")
            for part_name in safe_body_parts:
                gltf_joint_name = self.get_gltf_joint_name(part_name)
                if gltf_joint_name and part_name in natural_pose_data:
                    try:
                        joint = self.character.controlJoint(
                            None, "modelRoot", gltf_joint_name
                        )
                        if joint and not joint.isEmpty():
                            hpr_values = natural_pose_data[part_name]["hpr"]
                            joint.setHpr(hpr_values[0], hpr_values[1], hpr_values[2])
                            reset_count += 1
                            print(f"  ✅ Reset {part_name} -> {gltf_joint_name}")
                        else:
                            print(
                                f"  ❌ Joint not found: {part_name} -> {gltf_joint_name}"
                            )
                    except Exception as e:
                        print(f"❌ Error resetting {gltf_joint_name}: {e}")
                else:
                    print(f"  ⚠️ No natural pose data for: {part_name}")

            if reset_count > 0:
                self.character.update()
                print(f"✅ Reset {reset_count} SAFE joints to natural pose")
            else:
                print("❌ No joints were reset")

        except Exception as e:
            print(f"❌ Error during natural pose reset: {e}")

    def test_basic_joint_control(self):
        """Test basic joint control to verify the system is working."""
        print("🧪 Testing basic joint control...")

        if not self.character:
            print("❌ No character loaded")
            return False

        # Test with multiple joints to make changes more visible
        test_joints = {
            "mixamorig:RightArm": [45, 0, 0],  # Raise right arm
            "mixamorig:RightForeArm": [0, 45, 0],  # Bend elbow
            "mixamorig:RightHand": [0, 0, 45],  # Rotate hand
        }

        print("🎭 Applying dramatic test pose...")
        applied_joints = []

        for joint_name, test_hpr in test_joints.items():
            try:
                joint = self.character.controlJoint(None, "modelRoot", joint_name)
                if joint and not joint.isEmpty():
                    # Store original values
                    original_hpr = joint.getHpr()
                    applied_joints.append((joint, original_hpr))

                    # Apply dramatic test change
                    joint.setHpr(test_hpr[0], test_hpr[1], test_hpr[2])
                    print(
                        f"✅ {joint_name}: {test_hpr} (was: {[round(x, 1) for x in original_hpr]})"
                    )
                else:
                    print(f"❌ Joint {joint_name} not found or empty")

            except Exception as e:
                print(f"❌ Error testing joint {joint_name}: {e}")

        if applied_joints:
            # Update character
            self.character.update()

            # Adjust camera for better view
            if self.camera:
                self.camera.setPos(
                    3, -self.camera_distance, 2
                )  # Move to see the right arm
                self.camera.lookAt(0, 0, 1)
                print("📷 Adjusted camera to see test pose")

            # Force render
            if hasattr(self, "render_frame"):
                self.render_frame()

            print(f"🎬 Applied dramatic test pose to {len(applied_joints)} joints")
            print("⏰ Pose will be restored in 3 seconds...")

            # Wait a moment then restore (using a simple loop instead of timer for testing)
            import time

            time.sleep(3)

            # Restore original values
            for joint, original_hpr in applied_joints:
                joint.setHpr(original_hpr[0], original_hpr[1], original_hpr[2])

            self.character.update()
            if hasattr(self, "render_frame"):
                self.render_frame()

            print("✅ Restored original pose")
            return True
        else:
            print("❌ No joints were successfully tested")
            return False

    def update_ui_for_applied_joint(self, joint_name: str, hpr_values: List[float]):
        """Update UI body parts data when a joint is modified by pose application."""
        # Map joint names to body part names and update the internal data
        joint_to_bodypart_map = {
            "mixamorig:RightArm": "Right Arm",
            "mixamorig:LeftArm": "Left Arm",
            "mixamorig:RightForeArm": "Right Forearm",
            "mixamorig:LeftForeArm": "Left Forearm",
            "mixamorig:RightHand": "Right Hand",
            "mixamorig:LeftHand": "Left Hand",
            "mixamorig:RightHandThumb1": "Right Thumb",
            "mixamorig:RightHandThumb2": "Right Thumb",
            "mixamorig:RightHandThumb3": "Right Thumb",
            "mixamorig:RightHandIndex1": "Right Index Finger",
            "mixamorig:RightHandIndex2": "Right Index Finger",
            "mixamorig:RightHandIndex3": "Right Index Finger",
            "mixamorig:RightHandMiddle1": "Right Middle Finger",
            "mixamorig:RightHandMiddle2": "Right Middle Finger",
            "mixamorig:RightHandMiddle3": "Right Middle Finger",
            "mixamorig:RightHandRing1": "Right Ring Finger",
            "mixamorig:RightHandRing2": "Right Ring Finger",
            "mixamorig:RightHandRing3": "Right Ring Finger",
            "mixamorig:RightHandPinky1": "Right Pinky Finger",
            "mixamorig:RightHandPinky2": "Right Pinky Finger",
            "mixamorig:RightHandPinky3": "Right Pinky Finger",
        }

        body_part_name = joint_to_bodypart_map.get(joint_name)
        if body_part_name and body_part_name in self.body_parts:
            # Update the internal body parts data
            self.body_parts[body_part_name]["hpr"] = hpr_values.copy()
            print(f"🔄 Updated UI data for {body_part_name}: HPR = {hpr_values}")

            # Force refresh the UI to show the new values
            # The sliders will show the updated values when you expand that section
        else:
            print(f"🔍 No UI mapping found for joint: {joint_name}")

    def update_character_tilt(self, value):
        """Update character tilt forward/backward."""
        tilt_degrees = float(value)
        self.character_tilt_value.setText(f"{tilt_degrees}")

        if self.character and hasattr(self, "showbase"):
            try:
                # Apply tilt to the character root node
                # Positive values tilt forward, negative values tilt backward
                self.character.setHpr(0, tilt_degrees, 0)  # Pitch rotation

                # Update the character
                self.character.update()

                # Force render update
                if hasattr(self, "render_frame"):
                    self.render_frame()

                print(f"🎭 Character tilted: {tilt_degrees}°")

            except Exception as e:
                print(f"❌ Error tilting character: {e}")

    def mirror_to_left_hand(self):
        """Clone current right hand pose to left hand and update body controls."""
        print("🪞 Mirroring right hand pose to left hand...")

        # Mapping of right hand body parts to left hand equivalents
        right_to_left_mapping = {
            "Right Arm": "Left Arm",
            "Right Forearm": "Left Forearm",
            "Right Hand": "Left Hand",
            "Right Thumb": "Left Thumb",
            "Right Index Finger": "Left Index Finger",
            "Right Middle Finger": "Left Middle Finger",
            "Right Ring Finger": "Left Ring Finger",
            "Right Pinky Finger": "Left Pinky Finger",
        }

        cloned_count = 0

        # Clone right hand values to left hand in body_parts data
        for right_part, left_part in right_to_left_mapping.items():
            if right_part in self.body_parts and left_part in self.body_parts:
                # Copy HPR and XYZ values from right to left
                right_data = self.body_parts[right_part]
                self.body_parts[left_part]["hpr"] = right_data["hpr"].copy()
                self.body_parts[left_part]["xyz"] = right_data["xyz"].copy()

                # Apply the cloned pose to the character's left side joints
                left_joint_name = self.get_gltf_joint_name(
                    left_part.lower().replace(" ", "_")
                )
                if left_joint_name and self.character:
                    try:
                        joint = self.character.controlJoint(
                            None, "modelRoot", left_joint_name
                        )
                        if joint and not joint.isEmpty():
                            hpr = right_data["hpr"]
                            xyz = right_data["xyz"]
                            joint.setHpr(hpr[0], hpr[1], hpr[2])
                            joint.setPos(xyz[0], xyz[1], xyz[2])
                            cloned_count += 1
                            print(
                                f"  ✅ Cloned {right_part} → {left_part}: HPR={hpr}, XYZ={xyz}"
                            )
                    except Exception as e:
                        print(f"  ❌ Error cloning {right_part} to {left_part}: {e}")

        # Update the character
        if cloned_count > 0 and self.character:
            self.character.update()
            if hasattr(self, "render_frame"):
                self.render_frame()
            print(
                f"✅ Successfully cloned {cloned_count} right hand joints to left hand"
            )

            # Refresh the UI to show updated values
            self.refresh_body_parts_ui()
        else:
            print("❌ No joints were cloned")

    def refresh_body_parts_ui(self):
        """Refresh the body parts UI to show updated values."""
        # This will cause the sliders to show the new values when sections are expanded
        # The UI automatically reads from self.body_parts when creating sliders
        print("🔄 Body parts UI data updated - expand sections to see new values")

    def debug_character_nodes(self):
        """Debug method to list all available nodes in the character model."""
        if not self.character:
            print("❌ No character loaded")
            return

        print("🔍 DEBUG: Listing all character nodes...")

        # Get all nodes in the character
        all_nodes = self.character.findAllMatches("**")
        print(f"📊 Total nodes found: {all_nodes.getNumPaths()}")

        hand_related = []
        finger_related = []
        other_nodes = []

        for i in range(
            min(all_nodes.getNumPaths(), 50)
        ):  # Limit to first 50 for readability
            node = all_nodes.getPath(i)
            node_name = node.getName()

            if any(
                hand_part in node_name
                for hand_part in [
                    "Hand",
                    "Finger",
                    "Thumb",
                    "Index",
                    "Middle",
                    "Ring",
                    "Pinky",
                ]
            ):
                if "Hand" in node_name:
                    hand_related.append(node_name)
                else:
                    finger_related.append(node_name)
            else:
                other_nodes.append(node_name)

        print(f"\n🖐️ Hand-related nodes ({len(hand_related)}):")
        for name in hand_related[:10]:  # Show first 10
            print(f"  - {name}")

        print(f"\n👆 Finger-related nodes ({len(finger_related)}):")
        for name in finger_related[:10]:  # Show first 10
            print(f"  - {name}")

        print(f"\n🤖 Other nodes ({len(other_nodes)}) - showing first 10:")
        for name in other_nodes[:10]:
            print(f"  - {name}")

        # Test the current hand outline patterns
        print(f"\n🧪 Testing current hand outline patterns:")
        patterns = ["*RightHand*", "*LeftHand*", "*RightHandThumb*", "*RightHandIndex*"]
        for pattern in patterns:
            matches = self.character.findAllMatches(f"**/{pattern}")
            print(f"  Pattern '{pattern}': {matches.getNumPaths()} matches")
            for j in range(min(matches.getNumPaths(), 3)):
                match_node = matches.getPath(j)
                print(f"    - {match_node.getName()}")

    def update_hand_outline(self, value):
        """Update hand and finger outline visibility using transparency and material effects."""
        outline_intensity = float(value)
        self.outline_value.setText(f"{int(outline_intensity)}")

        if hasattr(self, "showbase") and self.showbase and self.character:
            try:
                # Clear any previous hand highlighting
                if hasattr(self, "_highlighted_nodes"):
                    for node in self._highlighted_nodes:
                        if node and not node.isEmpty():
                            node.clearColorScale()
                            node.clearTransparency()
                            node.clearRenderMode()

                self._highlighted_nodes = []

                if outline_intensity > 0:
                    # Try to find ALL nodes with geometry first
                    all_nodes = self.character.findAllMatches("**")
                    all_geometry_nodes = []

                    print("🔍 Scanning all nodes for geometry...")
                    for i in range(all_nodes.getNumPaths()):
                        node = all_nodes.getPath(i)
                        node_name = node.getName()

                        # Check if this node has geometry
                        if hasattr(node, "getNumGeoms") and node.getNumGeoms() > 0:
                            all_geometry_nodes.append((node, node_name))
                            print(
                                f"🎯 Found geometry node: {node_name} ({node.getNumGeoms()} geoms)"
                            )

                    print(f"📊 Total geometry nodes found: {len(all_geometry_nodes)}")

                    # Now try to find hand-related geometry by looking at the mesh names
                    hand_geometry_nodes = []
                    for node, node_name in all_geometry_nodes:
                        # Look for hand/finger related geometry
                        if any(
                            hand_part in node_name.lower()
                            for hand_part in [
                                "hand",
                                "finger",
                                "thumb",
                                "index",
                                "middle",
                                "ring",
                                "pinky",
                                "arm",
                            ]
                        ):
                            hand_geometry_nodes.append(node)
                            print(f"🖐️ Hand geometry found: {node_name}")

                    if hand_geometry_nodes:
                        self._highlighted_nodes = hand_geometry_nodes
                        applied_count = 0

                        # Use very aggressive color changes to make it obvious
                        for node in hand_geometry_nodes:
                            try:
                                # Bright red color to make it very obvious
                                node.setColorScale(3.0, 0.2, 0.2, 1.0)
                                applied_count += 1
                                print(f"✅ Applied bright red to {node.getName()}")
                            except Exception as e:
                                print(
                                    f"❌ Failed to apply color to {node.getName()}: {e}"
                                )

                        print(
                            f"🎨 Applied bright red to {applied_count}/{len(hand_geometry_nodes)} hand geometry nodes"
                        )
                    else:
                        print(
                            "❌ No hand geometry nodes found, trying to highlight ALL geometry"
                        )
                        # If no hand-specific geometry found, highlight ALL geometry to see what we have
                        if all_geometry_nodes:
                            self._highlighted_nodes = [
                                node for node, name in all_geometry_nodes
                            ]
                            applied_count = 0

                            for node, node_name in all_geometry_nodes:
                                try:
                                    # Bright green color to see all geometry
                                    node.setColorScale(0.2, 3.0, 0.2, 1.0)
                                    applied_count += 1
                                    print(
                                        f"✅ Applied bright green to ALL geometry: {node_name}"
                                    )
                                except Exception as e:
                                    print(
                                        f"❌ Failed to apply color to {node_name}: {e}"
                                    )

                            print(
                                f"🎨 Applied bright green to {applied_count}/{len(all_geometry_nodes)} ALL geometry nodes"
                            )
                        else:
                            print("❌ No geometry nodes found at all!")
                            # Try lighting-based approach to highlight hands
                            print("🔄 Trying lighting-based hand highlighting...")
                            try:
                                # Create a spotlight that follows the character's hands
                                if not hasattr(self, "hand_spotlight"):
                                    from panda3d.core import (
                                        PerspectiveLens,
                                        Spotlight,
                                        VBase4,
                                    )

                                    # Create a spotlight
                                    self.hand_spotlight = Spotlight("hand_spotlight")
                                    self.hand_spotlight.setColor(
                                        VBase4(1, 1, 0.5, 1)
                                    )  # Yellowish light

                                    # Set up the lens
                                    lens = PerspectiveLens()
                                    lens.setFov(30)  # Narrow beam
                                    self.hand_spotlight.setLens(lens)

                                    # Add the light to the scene
                                    light_node = self.showbase.render.attachNewNode(
                                        self.hand_spotlight
                                    )
                                    light_node.setPos(
                                        self.character.getPos() + (0, 0, 2)
                                    )  # Above character
                                    light_node.lookAt(
                                        self.character
                                    )  # Point at character

                                    print("✅ Created hand spotlight")

                                # Adjust spotlight intensity based on outline intensity
                                intensity = outline_intensity / 100.0
                                if intensity > 0:
                                    # Position spotlight to focus on hands
                                    hand_pos = self.character.getPos() + (
                                        0.5,
                                        0,
                                        1.5,
                                    )  # Approximate hand position
                                    light_node = self.hand_spotlight.getParent()
                                    light_node.setPos(hand_pos)
                                    light_node.lookAt(
                                        self.character.getPos() + (0, 0, 1)
                                    )

                                    # Adjust light color and intensity
                                    from panda3d.core import VBase4

                                    r = 1.0 + intensity * 2.0  # 1.0-3.0 (bright yellow)
                                    g = 1.0 + intensity * 1.5  # 1.0-2.5
                                    b = 0.5 + intensity * 0.5  # 0.5-1.0
                                    self.hand_spotlight.setColor(VBase4(r, g, b, 1))

                                    print(
                                        f"✅ Adjusted spotlight intensity: {intensity:.2f}"
                                    )
                                else:
                                    # Turn off spotlight
                                    if hasattr(self, "hand_spotlight"):
                                        self.hand_spotlight.getParent().detachNode()
                                        print("✅ Turned off hand spotlight")

                                self._highlighted_nodes = [self.character]

                            except Exception as e:
                                print(f"❌ Lighting approach failed: {e}")

                                # Try material-based approach
                                print("🔄 Trying material-based approach...")
                                try:
                                    # Try to modify the character's material properties
                                    if hasattr(self.character, "setMaterial"):
                                        from panda3d.core import Material

                                        material = Material()
                                        material.setShininess(100.0)  # Make it shiny
                                        material.setSpecular(
                                            VBase4(1, 1, 0.5, 1)
                                        )  # Yellowish specular
                                        self.character.setMaterial(material)
                                        print("✅ Applied shiny material to character")
                                    else:
                                        print(
                                            "❌ Character doesn't support material modification"
                                        )

                                except Exception as e2:
                                    print(f"❌ Material approach failed: {e2}")
                                    # Final fallback
                                    self._try_fallback_hand_highlighting(
                                        outline_intensity
                                    )

                # Force render update
                if hasattr(self, "render_frame"):
                    self.render_frame()

                effect_desc = (
                    "none"
                    if outline_intensity == 0
                    else f"{'transparent' if outline_intensity <= 50 else 'bright'}"
                )
                print(
                    f"🖐️ Hand outline: {outline_intensity}% ({effect_desc} effect on {len(getattr(self, '_highlighted_nodes', []))} nodes)"
                )

            except Exception as e:
                print(f"❌ Error updating hand outline: {e}")
                import traceback

                traceback.print_exc()

    def _try_fallback_hand_highlighting(self, outline_intensity):
        """Fallback method using the original approach."""
        print("🔄 Trying fallback hand highlighting method...")

        # Find all hand and finger related nodes
        hand_finger_patterns = [
            "*RightHand*",
            "*LeftHand*",
            "*RightHandThumb*",
            "*LeftHandThumb*",
            "*RightHandIndex*",
            "*LeftHandIndex*",
            "*RightHandMiddle*",
            "*LeftHandMiddle*",
            "*RightHandRing*",
            "*LeftHandRing*",
            "*RightHandPinky*",
            "*LeftHandPinky*",
            "*RightArm*",
            "*LeftArm*",
            "*RightForeArm*",
            "*LeftForeArm*",
        ]

        nodes_found = 0
        for pattern in hand_finger_patterns:
            nodes = self.character.findAllMatches(f"**/{pattern}")
            for i in range(nodes.getNumPaths()):
                node = nodes.getPath(i)
                if node and not node.isEmpty():
                    self._highlighted_nodes.append(node)
                    nodes_found += 1

        print(f"🔍 Fallback: Found {nodes_found} hand/finger nodes")

        if nodes_found > 0:
            # Try a very aggressive color change
            for node in self._highlighted_nodes:
                try:
                    # Bright red color to make it obvious
                    node.setColorScale(3.0, 0.5, 0.5, 1.0)
                except Exception as e:
                    print(f"❌ Fallback failed for {node.getName()}: {e}")

    def apply_pose_data(self, pose_data, description="Custom Pose"):
        """Apply pose data directly (used for mirroring and other operations)."""
        if not self.character or not pose_data:
            print("❌ No character or pose data available")
            return

        print(f"🎭 Applying {description}...")

        # Reset to natural pose first
        self.reset_to_natural_pose_for_sign()

        # Apply the pose data (reuse the same logic as apply_selected_sign)
        applied_count = 0
        safe_joints = [
            "mixamorig:RightArm",
            "mixamorig:LeftArm",
            "mixamorig:RightForeArm",
            "mixamorig:LeftForeArm",
            "mixamorig:RightHand",
            "mixamorig:LeftHand",
            # All finger joints
            "mixamorig:RightHandThumb1",
            "mixamorig:RightHandThumb2",
            "mixamorig:RightHandThumb3",
            "mixamorig:LeftHandThumb1",
            "mixamorig:LeftHandThumb2",
            "mixamorig:LeftHandThumb3",
            "mixamorig:RightHandIndex1",
            "mixamorig:RightHandIndex2",
            "mixamorig:RightHandIndex3",
            "mixamorig:LeftHandIndex1",
            "mixamorig:LeftHandIndex2",
            "mixamorig:LeftHandIndex3",
            "mixamorig:RightHandMiddle1",
            "mixamorig:RightHandMiddle2",
            "mixamorig:RightHandMiddle3",
            "mixamorig:LeftHandMiddle1",
            "mixamorig:LeftHandMiddle2",
            "mixamorig:LeftHandMiddle3",
            "mixamorig:RightHandRing1",
            "mixamorig:RightHandRing2",
            "mixamorig:RightHandRing3",
            "mixamorig:LeftHandRing1",
            "mixamorig:LeftHandRing2",
            "mixamorig:LeftHandRing3",
            "mixamorig:RightHandPinky1",
            "mixamorig:RightHandPinky2",
            "mixamorig:RightHandPinky3",
            "mixamorig:LeftHandPinky1",
            "mixamorig:LeftHandPinky2",
            "mixamorig:LeftHandPinky3",
        ]

        for joint_name, hpr_values in pose_data.items():
            if joint_name in safe_joints:
                try:
                    joint = self.character.controlJoint(None, "modelRoot", joint_name)
                    if joint and not joint.isEmpty():
                        if isinstance(hpr_values, list) and len(hpr_values) >= 3:
                            joint.setHpr(hpr_values[0], hpr_values[1], hpr_values[2])
                            applied_count += 1
                except Exception as e:
                    print(f"❌ Error applying {joint_name}: {e}")

        if applied_count > 0:
            self.character.update()
            if hasattr(self, "render_frame"):
                self.render_frame()
            print(f"✅ Applied {description} with {applied_count} joint changes")


def main():
    """Main function."""
    app = QApplication(sys.argv)

    # Set application style for native look
    app.setStyle("Fusion")

    window = GLBViewerWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
