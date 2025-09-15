#!/usr/bin/env python3
"""
Simplified test of Hand Pose Editor
"""

import sys
import logging
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleHandPoseEditor(QWidget):
    """Simplified Hand Pose Editor for testing"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI"""
        self.setWindowTitle("Simple Hand Pose Editor - HelpMeSign")
        self.setMinimumSize(1200, 800)
        
        # Create main layout
        main_layout = QHBoxLayout()
        
        # Left panel - 3D view placeholder
        left_panel = QWidget()
        left_panel.setStyleSheet("background-color: #2c3e50; border: 2px solid #34495e;")
        left_layout = QVBoxLayout()
        
        view_label = QLabel("3D Character View\n(6x Zoom - Hip & Above Only)")
        view_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        view_label.setStyleSheet("""
            QLabel {
                background-color: #2c3e50;
                color: white;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 20px;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        left_layout.addWidget(view_label)
        left_panel.setLayout(left_layout)
        
        # Right panel - controls
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: #ecf0f1; border: 2px solid #bdc3c7;")
        right_layout = QVBoxLayout()
        
        controls_label = QLabel("Hand Pose Controls")
        controls_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_label.setStyleSheet("""
            QLabel {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        right_layout.addWidget(controls_label)
        
        # Add some test controls
        test_button = QPushButton("Test Button")
        test_button.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        right_layout.addWidget(test_button)
        
        right_panel.setLayout(right_layout)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 2)  # 2/3 width
        main_layout.addWidget(right_panel, 1)  # 1/3 width
        
        self.setLayout(main_layout)
        
        self.logger.info("Simple Hand Pose Editor UI setup completed")

def test_simple_hand_pose_editor():
    """Test the simplified Hand Pose Editor"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    logger.info("Creating Simple Hand Pose Editor...")
    editor = SimpleHandPoseEditor()
    
    logger.info("Showing Simple Hand Pose Editor...")
    editor.show()
    editor.raise_()
    editor.activateWindow()
    editor.setVisible(True)
    editor.setFocus()
    
    # Log window properties
    logger.info(f"Window visible: {editor.isVisible()}")
    logger.info(f"Window size: {editor.size()}")
    logger.info(f"Window position: {editor.pos()}")
    logger.info(f"Window state: {editor.windowState()}")
    
    logger.info("Simple Hand Pose Editor should now be visible")
    
    # Keep the window open for a few seconds
    import time
    time.sleep(5)
    
    return editor

if __name__ == "__main__":
    try:
        logger.info("Starting Simple Hand Pose Editor test...")
        editor = test_simple_hand_pose_editor()
        logger.info("Test completed successfully")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
