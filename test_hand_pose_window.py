#!/usr/bin/env python3
"""
Test script to verify Hand Pose Editor window display
"""

import sys
import logging
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_window_display():
    """Test basic window display functionality"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create a simple test window
    window = QWidget()
    window.setWindowTitle("Test Hand Pose Editor Window")
    window.setMinimumSize(800, 600)
    
    # Create layout
    layout = QVBoxLayout()
    
    # Add a label
    label = QLabel("Hand Pose Editor Test Window")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 20px;")
    layout.addWidget(label)
    
    # Add a button
    button = QPushButton("Test Button")
    button.setStyleSheet("""
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
    layout.addWidget(button)
    
    window.setLayout(layout)
    
    # Show the window
    logger.info("Showing test window...")
    window.show()
    window.raise_()
    window.activateWindow()
    
    # Force visibility
    window.setVisible(True)
    window.setFocus()
    
    # Log window properties
    logger.info(f"Window visible: {window.isVisible()}")
    logger.info(f"Window size: {window.size()}")
    logger.info(f"Window position: {window.pos()}")
    logger.info(f"Window state: {window.windowState()}")
    
    logger.info("Test window should now be visible")
    
    # Keep the window open for a few seconds
    import time
    time.sleep(3)
    
    return window

if __name__ == "__main__":
    try:
        logger.info("Starting Hand Pose Editor window test...")
        window = test_window_display()
        logger.info("Test completed successfully")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
