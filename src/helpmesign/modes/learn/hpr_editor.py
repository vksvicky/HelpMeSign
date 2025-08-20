"""
Interactive HPR Editor for 3D Character Joint Positioning
Allows real-time adjustment of Heading, Pitch, and Roll values for character joints.
"""

import sys
from typing import Any, Dict, Optional

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Panda3D typing fallback: define VBase4 with a typed alias so mypy does not require stubs
try:
    from panda3d.core import VBase4 as VBase4
except Exception:

    class VBase4:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass


class HPRSlider(QWidget):
    """Individual HPR slider with label and spinbox."""

    valueChanged = Signal(str, float)

    def __init__(
        self,
        name: str,
        min_val: float = -180.0,
        max_val: float = 180.0,
        default: float = 0.0,
    ):
        super().__init__()
        self.name = name
        self.setup_ui(min_val, max_val, default)

    def setup_ui(self, min_val: float, max_val: float, default: float):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)

        # Label
        label = QLabel(f"{self.name}:")
        label.setMinimumWidth(60)
        layout.addWidget(label)

        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(int(min_val * 10), int(max_val * 10))
        self.slider.setValue(int(default * 10))
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(45 * 10)  # 45 degree ticks
        layout.addWidget(self.slider)

        # SpinBox
        self.spinbox = QSpinBox()
        self.spinbox.setRange(int(min_val), int(max_val))
        self.spinbox.setValue(int(default))
        self.spinbox.setSuffix("°")
        self.spinbox.setMinimumWidth(80)
        layout.addWidget(self.spinbox)

        # Connect signals
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.spinbox.valueChanged.connect(self._on_spinbox_changed)

    def _on_slider_changed(self, value: int):
        float_value = value / 10.0
        self.spinbox.setValue(int(float_value))
        self.valueChanged.emit(self.name, float_value)

    def _on_spinbox_changed(self, value: int):
        self.slider.setValue(int(value * 10))
        self.valueChanged.emit(self.name, float(value))

    def get_value(self) -> float:
        return self.spinbox.value()

    def set_value(self, value: float):
        self.spinbox.setValue(int(value))
        self.slider.setValue(int(value * 10))


class HPRJointEditor(QWidget):
    """Editor for a single joint's HPR values."""

    hprChanged = Signal(str, float, float, float)

    def __init__(self, joint_name: str):
        super().__init__()
        self.joint_name = joint_name
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Joint name header
        header = QLabel(self.joint_name)
        header.setFont(QFont("Arial", 10, QFont.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # HPR sliders
        self.h_slider = HPRSlider("H", -180, 180, 0)
        self.p_slider = HPRSlider("P", -180, 180, 0)
        self.r_slider = HPRSlider("R", -180, 180, 0)

        layout.addWidget(self.h_slider)
        layout.addWidget(self.p_slider)
        layout.addWidget(self.r_slider)

        # Connect signals
        self.h_slider.valueChanged.connect(self._on_h_changed)
        self.p_slider.valueChanged.connect(self._on_p_changed)
        self.r_slider.valueChanged.connect(self._on_r_changed)

        # Reset button
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_values)
        layout.addWidget(reset_btn)

    def _on_h_changed(self, name: str, value: float):
        self.hprChanged.emit(
            self.joint_name, value, self.p_slider.get_value(), self.r_slider.get_value()
        )

    def _on_p_changed(self, name: str, value: float):
        self.hprChanged.emit(
            self.joint_name, self.h_slider.get_value(), value, self.r_slider.get_value()
        )

    def _on_r_changed(self, name: str, value: float):
        self.hprChanged.emit(
            self.joint_name, self.h_slider.get_value(), self.p_slider.get_value(), value
        )

    def get_hpr(self) -> tuple[float, float, float]:
        return (
            self.h_slider.get_value(),
            self.p_slider.get_value(),
            self.r_slider.get_value(),
        )

    def set_hpr(self, h: float, p: float, r: float):
        self.h_slider.set_value(h)
        self.p_slider.set_value(p)
        self.r_slider.set_value(r)

    def reset_values(self):
        self.set_hpr(0, 0, 0)


class HPRInteractiveEditor(QWidget):
    """Main interactive HPR editor window."""

    def __init__(self, animate_panel=None):
        super().__init__()
        self.animate_panel = animate_panel
        self.joint_editors: Dict[str, HPRJointEditor] = {}
        self.setup_ui()

        # Timer for periodic updates - DISABLED to prevent automatic value application
        # self.update_timer = QTimer()
        # self.update_timer.timeout.connect(self.apply_current_values)
        # self.update_timer.start(100)  # Update 10 times per second

    def setup_ui(self):
        self.setWindowTitle("Interactive HPR Editor - Character Joint Positioning")
        self.setMinimumSize(1000, 800)
        self.resize(1000, 800)

        # Clear any existing layout and widgets
        if self.layout():
            QWidget().setLayout(self.layout())

        # Clear any existing joint editors
        for editor in self.joint_editors.values():
            if editor.parent():
                editor.setParent(None)
        self.joint_editors.clear()

        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Interactive HPR Editor")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Instructions
        instructions = QLabel(
            "Adjust the sliders to position the character's joints in real-time.\n"
            "H=Heading (left/right), P=Pitch (forward/back), R=Roll (side tilt)"
        )
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Left panel - Joint editors
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)  # Add spacing between widgets
        left_layout.setContentsMargins(10, 10, 10, 10)  # Add margins

        # Joint selection
        joint_group = QGroupBox("Joint Selection")
        joint_layout = QHBoxLayout(joint_group)
        joint_layout.setContentsMargins(10, 10, 10, 10)

        self.joint_combo = QComboBox()
        self.joint_combo.addItems(
            [
                "mixamorig:RightArm",
                "mixamorig:LeftArm",
                "mixamorig:RightForeArm",
                "mixamorig:LeftForeArm",
                "mixamorig:RightHand",
                "mixamorig:LeftHand",
                "mixamorig:Hips",
                "mixamorig:Spine",
                "mixamorig:Spine1",
                "mixamorig:Spine2",
                "mixamorig:RightUpLeg",
                "mixamorig:LeftUpLeg",
                "mixamorig:RightLeg",
                "mixamorig:LeftLeg",
            ]
        )
        self.joint_combo.currentTextChanged.connect(self.on_joint_selected)
        joint_layout.addWidget(QLabel("Joint:"))
        joint_layout.addWidget(self.joint_combo)

        left_layout.addWidget(joint_group)

        # Body Rotation Controls
        body_group = QGroupBox("Body Rotation & Positioning")
        body_layout = QVBoxLayout(body_group)
        body_layout.setContentsMargins(10, 10, 10, 10)
        body_layout.setSpacing(8)

        # Body rotation presets
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Body Presets:"))

        self.body_preset_combo = QComboBox()
        self.body_preset_combo.addItems(
            [
                "Neutral (T-Pose)",
                "Forward Lean",
                "Backward Lean",
                "Left Turn",
                "Right Turn",
                "Sitting Pose",
                "Signing Pose (Arms Forward)",
                "Custom",
            ]
        )
        self.body_preset_combo.currentTextChanged.connect(self.apply_body_preset)
        preset_layout.addWidget(self.body_preset_combo)

        body_layout.addLayout(preset_layout)

        # Quick body rotation controls
        rotation_layout = QGridLayout()

        # Hips rotation
        rotation_layout.addWidget(QLabel("Hips Rotation:"), 0, 0)
        self.hips_h_slider = QSlider(Qt.Horizontal)
        self.hips_h_slider.setRange(-180, 180)
        self.hips_h_slider.setValue(0)
        self.hips_h_slider.valueChanged.connect(
            lambda v: self.quick_body_rotation("mixamorig:Hips", "H", v)
        )
        rotation_layout.addWidget(self.hips_h_slider, 0, 1)

        # Spine rotation
        rotation_layout.addWidget(QLabel("Spine Rotation:"), 1, 0)
        self.spine_h_slider = QSlider(Qt.Horizontal)
        self.spine_h_slider.setRange(-180, 180)
        self.spine_h_slider.setValue(0)
        self.spine_h_slider.valueChanged.connect(
            lambda v: self.quick_body_rotation("mixamorig:Spine", "H", v)
        )
        rotation_layout.addWidget(self.spine_h_slider, 1, 1)

        # Body lean (pitch)
        rotation_layout.addWidget(QLabel("Body Lean:"), 2, 0)
        self.body_p_slider = QSlider(Qt.Horizontal)
        self.body_p_slider.setRange(-90, 90)
        self.body_p_slider.setValue(0)
        self.body_p_slider.valueChanged.connect(self.body_lean)
        rotation_layout.addWidget(self.body_p_slider, 2, 1)

        body_layout.addLayout(rotation_layout)

        # Body reset button
        body_reset_btn = QPushButton("Reset Body Position")
        body_reset_btn.clicked.connect(self.reset_body_position)
        body_layout.addWidget(body_reset_btn)

        left_layout.addWidget(body_group)

        # Joint editors container with scroll area
        from PySide6.QtWidgets import QScrollArea

        scroll_area = QScrollArea()
        self.joint_editors_container = QWidget()
        self.joint_editors_layout = QVBoxLayout(self.joint_editors_container)
        self.joint_editors_layout.setSpacing(5)
        self.joint_editors_layout.setContentsMargins(5, 5, 5, 5)
        scroll_area.setWidget(self.joint_editors_container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(400)  # Increased height
        scroll_area.setMaximumHeight(500)  # Set maximum height
        left_layout.addWidget(scroll_area)

        # Add a spacer to ensure proper separation
        from PySide6.QtWidgets import QSpacerItem

        spacer = QSpacerItem(20, 20)
        left_layout.addItem(spacer)

        # Control buttons
        button_layout = QHBoxLayout()

        self.apply_btn = QPushButton("Apply All Values")
        self.apply_btn.clicked.connect(self.apply_current_values)
        button_layout.addWidget(self.apply_btn)

        self.reset_all_btn = QPushButton("Reset All")
        self.reset_all_btn.clicked.connect(self.reset_all_values)
        button_layout.addWidget(self.reset_all_btn)

        self.copy_values_btn = QPushButton("Copy Values to Code")
        self.copy_values_btn.clicked.connect(self.copy_values_to_clipboard)
        button_layout.addWidget(self.copy_values_btn)

        # Color control
        color_group = QGroupBox("Character Color")
        color_layout = QHBoxLayout(color_group)
        color_layout.setContentsMargins(10, 10, 10, 10)

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

        left_layout.addWidget(color_group)

        # RGB Color sliders for fine control
        rgb_group = QGroupBox("RGB Color Control")
        rgb_layout = QVBoxLayout(rgb_group)
        rgb_layout.setContentsMargins(10, 10, 10, 10)
        rgb_layout.setSpacing(5)

        # Red slider
        red_layout = QHBoxLayout()
        red_layout.addWidget(QLabel("Red:"))
        self.red_slider = QSlider(Qt.Horizontal)
        self.red_slider.setRange(0, 255)
        self.red_slider.setValue(200)
        self.red_slider.valueChanged.connect(self.update_rgb_color)
        red_layout.addWidget(self.red_slider)
        self.red_label = QLabel("200")
        red_layout.addWidget(self.red_label)
        rgb_layout.addLayout(red_layout)

        # Green slider
        green_layout = QHBoxLayout()
        green_layout.addWidget(QLabel("Green:"))
        self.green_slider = QSlider(Qt.Horizontal)
        self.green_slider.setRange(0, 255)
        self.green_slider.setValue(150)
        self.green_slider.valueChanged.connect(self.update_rgb_color)
        green_layout.addWidget(self.green_slider)
        self.green_label = QLabel("150")
        green_layout.addWidget(self.green_label)
        rgb_layout.addLayout(green_layout)

        # Blue slider
        blue_layout = QHBoxLayout()
        blue_layout.addWidget(QLabel("Blue:"))
        self.blue_slider = QSlider(Qt.Horizontal)
        self.blue_slider.setRange(0, 255)
        self.blue_slider.setValue(100)
        self.blue_slider.valueChanged.connect(self.update_rgb_color)
        blue_layout.addWidget(self.blue_slider)
        self.blue_label = QLabel("100")
        blue_layout.addWidget(self.blue_label)
        rgb_layout.addLayout(blue_layout)

        left_layout.addWidget(rgb_group)

        left_layout.addLayout(button_layout)

        splitter.addWidget(left_panel)

        # Right panel - Log and current values
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Current values display
        values_group = QGroupBox("Current Values")
        values_layout = QVBoxLayout(values_group)

        self.values_display = QTextEdit()
        self.values_display.setMaximumHeight(200)
        self.values_display.setReadOnly(True)
        values_layout.addWidget(self.values_display)

        right_layout.addWidget(values_group)

        # Log display
        log_group = QGroupBox("Application Log")
        log_layout = QVBoxLayout(log_group)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        log_layout.addWidget(self.log_display)

        right_layout.addWidget(log_group)

        splitter.addWidget(right_panel)

        # Set splitter proportions - give more space to left panel
        splitter.setSizes([600, 400])

        # Initialize joint editors
        self.initialize_joint_editors()

    def initialize_joint_editors(self):
        """Create editors for all joints."""

        # Clear any existing joint editors
        for editor in self.joint_editors.values():
            if editor.parent():
                editor.setParent(None)
        self.joint_editors.clear()

        # Clear the joint editors layout
        while self.joint_editors_layout.count():
            child = self.joint_editors_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

        # Create joint editors organized by category
        arm_joints = [
            "mixamorig:RightArm",
            "mixamorig:LeftArm",
            "mixamorig:RightForeArm",
            "mixamorig:LeftForeArm",
            "mixamorig:RightHand",
            "mixamorig:LeftHand",
        ]
        body_joints = [
            "mixamorig:Hips",
            "mixamorig:Spine",
            "mixamorig:Spine1",
            "mixamorig:Spine2",
        ]
        leg_joints = [
            "mixamorig:RightUpLeg",
            "mixamorig:LeftUpLeg",
            "mixamorig:RightLeg",
            "mixamorig:LeftLeg",
        ]

        # Add arm joints section
        arm_group = QGroupBox("Arm & Hand Joints")
        arm_layout = QVBoxLayout(arm_group)
        arm_layout.setContentsMargins(10, 10, 10, 10)
        arm_layout.setSpacing(5)
        for joint_name in arm_joints:
            editor = HPRJointEditor(joint_name)
            editor.hprChanged.connect(self.on_hpr_changed)
            self.joint_editors[joint_name] = editor
            arm_layout.addWidget(editor)
            editor.setVisible(True)

        self.joint_editors_layout.addWidget(arm_group)

        # Add body joints section
        body_joint_group = QGroupBox("Body Joints")
        body_joint_layout = QVBoxLayout(body_joint_group)
        body_joint_layout.setContentsMargins(10, 10, 10, 10)
        body_joint_layout.setSpacing(5)
        for joint_name in body_joints:
            editor = HPRJointEditor(joint_name)
            editor.hprChanged.connect(self.on_hpr_changed)
            self.joint_editors[joint_name] = editor
            body_joint_layout.addWidget(editor)
            editor.setVisible(True)

        self.joint_editors_layout.addWidget(body_joint_group)

        # Add leg joints section
        leg_group = QGroupBox("Leg Joints")
        leg_layout = QVBoxLayout(leg_group)
        leg_layout.setContentsMargins(10, 10, 10, 10)
        leg_layout.setSpacing(5)
        for joint_name in leg_joints:
            editor = HPRJointEditor(joint_name)
            editor.hprChanged.connect(self.on_hpr_changed)
            self.joint_editors[joint_name] = editor
            leg_layout.addWidget(editor)
            editor.setVisible(True)

        self.joint_editors_layout.addWidget(leg_group)

        # Don't set initial values - let the character keep its current pose
        # self.set_initial_values()

        # Force layout update
        self.joint_editors_container.updateGeometry()

    def set_initial_values(self):
        """Set initial HPR values based on current code."""
        initial_values = {
            "mixamorig:RightArm": (100, 90, 0),  # Optimized from HPR editor testing
            "mixamorig:LeftArm": (-100, 90, 0),  # Optimized from HPR editor testing
            "mixamorig:RightForeArm": (0, 0, 0),  # Optimized from HPR editor testing
            "mixamorig:LeftForeArm": (0, 0, 0),  # Optimized from HPR editor testing
            "mixamorig:RightHand": (0, 0, 0),
            "mixamorig:LeftHand": (0, 0, 0),
            "mixamorig:Hips": (0, 0, 0),
            "mixamorig:Spine": (0, 0, 0),
            "mixamorig:Spine1": (0, 0, 0),
            "mixamorig:Spine2": (0, 0, 0),
            "mixamorig:RightUpLeg": (0, 0, 0),
            "mixamorig:LeftUpLeg": (0, 0, 0),
            "mixamorig:RightLeg": (0, 0, 0),
            "mixamorig:LeftLeg": (0, 0, 0),
        }

        for joint_name, (h, p, r) in initial_values.items():
            if joint_name in self.joint_editors:
                self.joint_editors[joint_name].set_hpr(h, p, r)

    def on_joint_selected(self, joint_name: str):
        """Handle joint selection."""
        self.log_message(f"Selected joint: {joint_name}")

    def on_hpr_changed(self, joint_name: str, h: float, p: float, r: float):
        """Handle HPR value changes."""
        self.log_message(f"{joint_name}: H={h:.1f}°, P={p:.1f}°, R={r:.1f}°")
        self.update_values_display()

    def apply_current_values(self):
        """Apply current HPR values to the character."""
        if not self.animate_panel or not hasattr(self.animate_panel, "_actor"):
            return

        try:
            actor = self.animate_panel._actor
            if actor is None:
                return

            for joint_name, editor in self.joint_editors.items():
                h, p, r = editor.get_hpr()
                joint = actor.controlJoint(None, "modelRoot", joint_name)
                if joint is not None:
                    joint.setHpr(h, p, r)

            # Force update
            actor.update()
            self.log_message("Applied all HPR values to character")

        except Exception as e:
            self.log_message(f"Error applying HPR values: {e}")

    def reset_all_values(self):
        """Reset all HPR values to zero."""
        for editor in self.joint_editors.values():
            editor.reset_values()
        self.log_message("Reset all HPR values to zero")

    def copy_values_to_clipboard(self):
        """Copy current HPR values as Python code to clipboard."""
        import json

        values = {}
        for joint_name, editor in self.joint_editors.items():
            h, p, r = editor.get_hpr()
            values[joint_name] = [h, p, r]

        code = f"""# HPR Values for Character Joints
# Generated by Interactive HPR Editor

joint_hpr_values = {json.dumps(values, indent=2)}

# Apply to character:
for joint_name, (h, p, r) in joint_hpr_values.items():
    joint = actor.controlJoint(None, "modelRoot", joint_name)
    if joint is not None:
        joint.setHpr(h, p, r)
actor.update()
"""

        from PySide6.QtWidgets import QApplication

        QApplication.clipboard().setText(code)
        self.log_message("Copied HPR values to clipboard as Python code")

    def update_values_display(self):
        """Update the current values display."""
        text = "Current HPR Values:\n\n"
        for joint_name, editor in self.joint_editors.items():
            h, p, r = editor.get_hpr()
            text += f"{joint_name}:\n"
            text += f"  H: {h:6.1f}°\n"
            text += f"  P: {p:6.1f}°\n"
            text += f"  R: {r:6.1f}°\n\n"

        self.values_display.setText(text)

    def change_character_color(self, color_name: str):
        """Change the character's color."""
        if not self.animate_panel or not hasattr(self.animate_panel, "_model_np"):
            return

        try:
            VBase4

            # Color mapping
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
                color = color_map[color_name]
                model_np = self.animate_panel._model_np
                if model_np is not None:
                    # Apply color to the model
                    model_np.setColor(color)
                    self.log_message(f"Changed character color to: {color_name}")
                else:
                    self.log_message("No model loaded to change color")
            else:
                self.log_message(f"Unknown color: {color_name}")

        except Exception as e:
            self.log_message(f"Error changing character color: {e}")

    def update_rgb_color(self):
        """Update character color using RGB sliders."""
        if not self.animate_panel or not hasattr(self.animate_panel, "_model_np"):
            return

        try:
            VBase4

            # Get RGB values from sliders
            r = self.red_slider.value() / 255.0
            g = self.green_slider.value() / 255.0
            b = self.blue_slider.value() / 255.0

            # Update labels
            self.red_label.setText(str(self.red_slider.value()))
            self.green_label.setText(str(self.green_slider.value()))
            self.blue_label.setText(str(self.blue_slider.value()))

            # Apply color
            color = VBase4(r, g, b, 1.0)
            model_np = self.animate_panel._model_np
            if model_np is not None:
                model_np.setColor(color)
                self.log_message(
                    f"RGB Color: R={self.red_slider.value()}, G={self.green_slider.value()}, B={self.blue_slider.value()}"
                )

        except Exception as e:
            self.log_message(f"Error updating RGB color: {e}")

    def log_message(self, message: str):
        """Add a message to the log display."""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_display.append(f"[{timestamp}] {message}")

        # Keep only last 100 lines
        lines = self.log_display.toPlainText().split("\n")
        if len(lines) > 100:
            self.log_display.setPlainText("\n".join(lines[-100:]))

    def showEvent(self, event):
        """Handle show event."""
        super().showEvent(event)
        self.update_values_display()
        self.log_message("HPR Editor opened - adjust sliders to position character")

    def apply_body_preset(self, preset_name: str):
        """Apply a body rotation preset."""
        if not self.animate_panel or not hasattr(self.animate_panel, "_actor"):
            return

        try:
            actor = self.animate_panel._actor
            if actor is None:
                return

            # Preset configurations
            presets = {
                "Neutral (T-Pose)": {
                    "mixamorig:Hips": [0, 0, 0],
                    "mixamorig:Spine": [0, 0, 0],
                    "mixamorig:Spine1": [0, 0, 0],
                    "mixamorig:Spine2": [0, 0, 0],
                },
                "Forward Lean": {
                    "mixamorig:Hips": [0, -15, 0],
                    "mixamorig:Spine": [0, -10, 0],
                    "mixamorig:Spine1": [0, -5, 0],
                    "mixamorig:Spine2": [0, -5, 0],
                },
                "Backward Lean": {
                    "mixamorig:Hips": [0, 15, 0],
                    "mixamorig:Spine": [0, 10, 0],
                    "mixamorig:Spine1": [0, 5, 0],
                    "mixamorig:Spine2": [0, 5, 0],
                },
                "Left Turn": {
                    "mixamorig:Hips": [-45, 0, 0],
                    "mixamorig:Spine": [-30, 0, 0],
                    "mixamorig:Spine1": [-15, 0, 0],
                    "mixamorig:Spine2": [-5, 0, 0],
                },
                "Right Turn": {
                    "mixamorig:Hips": [45, 0, 0],
                    "mixamorig:Spine": [30, 0, 0],
                    "mixamorig:Spine1": [15, 0, 0],
                    "mixamorig:Spine2": [5, 0, 0],
                },
                "Sitting Pose": {
                    "mixamorig:Hips": [0, -30, 0],
                    "mixamorig:Spine": [0, -20, 0],
                    "mixamorig:Spine1": [0, -10, 0],
                    "mixamorig:Spine2": [0, -5, 0],
                    "mixamorig:RightUpLeg": [0, -45, 0],
                    "mixamorig:LeftUpLeg": [0, -45, 0],
                },
                "Signing Pose (Arms Forward)": {
                    "mixamorig:Hips": [0, -10, 0],
                    "mixamorig:Spine": [0, -5, 0],
                    "mixamorig:Spine1": [0, 0, 0],
                    "mixamorig:Spine2": [0, 5, 0],
                },
            }

            if preset_name in presets:
                preset = presets[preset_name]
                for joint_name, hpr in preset.items():
                    joint = actor.controlJoint(None, "modelRoot", joint_name)
                    if joint is not None:
                        h, p, r = hpr
                        joint.setHpr(h, p, r)

                actor.update()
                self.log_message(f"Applied body preset: {preset_name}")

                # Update sliders to match preset
                if preset_name != "Custom":
                    if "mixamorig:Hips" in preset:
                        h, p, r = preset["mixamorig:Hips"]
                        self.hips_h_slider.setValue(int(h))
                    if "mixamorig:Spine" in preset:
                        h, p, r = preset["mixamorig:Spine"]
                        self.spine_h_slider.setValue(int(h))
                    if "mixamorig:Spine" in preset:
                        h, p, r = preset["mixamorig:Spine"]
                        self.body_p_slider.setValue(int(p))

        except Exception as e:
            self.log_message(f"Error applying body preset: {e}")

    def quick_body_rotation(self, joint_name: str, axis: str, value: float):
        """Quick rotation of body joints."""
        if not self.animate_panel or not hasattr(self.animate_panel, "_actor"):
            return

        try:
            actor = self.animate_panel._actor
            if actor is None:
                return

            joint = actor.controlJoint(None, "modelRoot", joint_name)
            if joint is not None:
                current_h, current_p, current_r = joint.getHpr()

                if axis == "H":
                    joint.setHpr(value, current_p, current_r)
                elif axis == "P":
                    joint.setHpr(current_h, value, current_r)
                elif axis == "R":
                    joint.setHpr(current_h, current_p, value)

                actor.update()
                self.log_message(f"Rotated {joint_name} {axis}-axis to {value}°")

        except Exception as e:
            self.log_message(f"Error rotating {joint_name}: {e}")

    def body_lean(self, value: float):
        """Apply body lean (pitch) to spine joints."""
        if not self.animate_panel or not hasattr(self.animate_panel, "_actor"):
            return

        try:
            actor = self.animate_panel._actor
            if actor is None:
                return

            # Apply lean to spine joints
            spine_joints = ["mixamorig:Spine", "mixamorig:Spine1", "mixamorig:Spine2"]

            for joint_name in spine_joints:
                joint = actor.controlJoint(None, "modelRoot", joint_name)
                if joint is not None:
                    current_h, current_p, current_r = joint.getHpr()
                    # Distribute lean across spine joints
                    lean_factor = 0.3 if joint_name == "mixamorig:Spine" else 0.2
                    new_pitch = value * lean_factor
                    joint.setHpr(current_h, new_pitch, current_r)

            actor.update()
            self.log_message(f"Applied body lean: {value}°")

        except Exception as e:
            self.log_message(f"Error applying body lean: {e}")

    def reset_body_position(self):
        """Reset all body joints to neutral position."""
        if not self.animate_panel or not hasattr(self.animate_panel, "_actor"):
            return

        try:
            actor = self.animate_panel._actor
            if actor is None:
                return

            # Reset body joints
            body_joints = [
                "mixamorig:Hips",
                "mixamorig:Spine",
                "mixamorig:Spine1",
                "mixamorig:Spine2",
                "mixamorig:RightUpLeg",
                "mixamorig:LeftUpLeg",
                "mixamorig:RightLeg",
                "mixamorig:LeftLeg",
            ]

            for joint_name in body_joints:
                joint = actor.controlJoint(None, "modelRoot", joint_name)
                if joint is not None:
                    joint.setHpr(0, 0, 0)

            actor.update()

            # Reset sliders
            self.hips_h_slider.setValue(0)
            self.spine_h_slider.setValue(0)
            self.body_p_slider.setValue(0)

            self.log_message("Reset body position to neutral")

        except Exception as e:
            self.log_message(f"Error resetting body position: {e}")
