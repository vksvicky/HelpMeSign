#!/usr/bin/env python3
"""
Simple test for Hand Pose Editor window display
"""

import sys
import logging
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleHandPoseEditor(QWidget):
    """Simple test version of Hand Pose Editor"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        self.setWindowTitle("Simple Hand Pose Editor Test")
        self.setMinimumSize(800, 600)
        
        # Create a simple layout
        layout = QVBoxLayout(self)
        
        # Add a label
        label = QLabel("🖐️ Hand Pose Editor Test Window")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
            }
        """)
        layout.addWidget(label)
        
        # Add a test button
        button = QPushButton("Test Button - Window is Working!")
        button.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        button.clicked.connect(self.test_button_clicked)
        layout.addWidget(button)
        
        self.logger.info("Simple Hand Pose Editor created successfully")
        
    def test_button_clicked(self):
        """Test button click handler"""
        self.logger.info("Test button clicked! Window is working properly.")
        self.setWindowTitle("Simple Hand Pose Editor Test - Button Clicked!")

def main():
    """Main function to test the simple editor"""
    app = QApplication(sys.argv)
    
    logger.info("Creating simple Hand Pose Editor...")
    editor = SimpleHandPoseEditor()
    
    logger.info("Showing simple Hand Pose Editor...")
    editor.show()
    editor.raise_()
    editor.activateWindow()
    
    logger.info("Simple Hand Pose Editor should now be visible")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
