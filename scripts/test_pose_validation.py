#!/usr/bin/env python3
"""
Test script for pose validation system
Demonstrates how to use the pose validation panel
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt

from helpmesign.modes.learn.pose_validation_panel import PoseValidationPanel


class TestPoseValidationWindow(QMainWindow):
    """Test window for pose validation system"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pose Validation Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Pose Validation System Test")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel("""
        This test demonstrates the pose validation system:
        
        1. Click "Open Pose Validation Panel" to open the validation interface
        2. Select a letter (e.g., 'A') and hand preference (right/left)
        3. Click "Load Current Pose" to load the pose data
        4. Click "Open HPR Editor" to visually inspect and correct the pose
        5. Make corrections in the HPR editor
        6. Click "Save Corrections" to save the corrected pose
        7. Click "Export Corrections" to export validation results
        
        The system will validate poses against human anatomical constraints
        and allow you to visually correct them using the HPR editor.
        """)
        instructions.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                font-size: 12px;
                color: #495057;
            }
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Open pose validation button
        self.open_validation_btn = QPushButton("Open Pose Validation Panel")
        self.open_validation_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        self.open_validation_btn.clicked.connect(self.open_pose_validation)
        layout.addWidget(self.open_validation_btn)
        
        # Status label
        self.status_label = QLabel("Ready to test pose validation")
        self.status_label.setStyleSheet("color: #6c757d; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # Pose validation panel
        self.pose_validation_panel = None
        
    def open_pose_validation(self):
        """Open the pose validation panel"""
        try:
            if not self.pose_validation_panel:
                self.pose_validation_panel = PoseValidationPanel()
                # Connect signal to handle pose corrections
                self.pose_validation_panel.pose_corrected.connect(self.on_pose_corrected)
            
            self.pose_validation_panel.show()
            self.pose_validation_panel.raise_()
            self.pose_validation_panel.activateWindow()
            
            self.status_label.setText("Pose Validation Panel opened")
            
        except Exception as e:
            self.status_label.setText(f"Error opening pose validation panel: {e}")
            print(f"Error: {e}")
    
    def on_pose_corrected(self, letter: str, corrected_pose: dict):
        """Handle pose corrections"""
        self.status_label.setText(f"Pose corrected for letter {letter}")
        print(f"Pose corrected for letter {letter}: {corrected_pose}")


def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Create and show test window
    window = TestPoseValidationWindow()
    window.show()
    
    print("Pose Validation Test Window opened")
    print("Click 'Open Pose Validation Panel' to start testing")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
