#!/usr/bin/env python3
"""
Direct test of Hand Pose Editor creation
"""

import sys
import logging
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_hand_pose_editor_direct():
    """Test direct creation of Hand Pose Editor"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        logger.info("Importing Hand Pose Editor...")
        from helpmesign.modes.learn.hand_pose_editor import HandPoseEditor
        
        logger.info("Creating Hand Pose Editor...")
        editor = HandPoseEditor(None, None)  # No animate_panel, no main_window
        
        logger.info("Setting window properties...")
        editor.setWindowTitle("Test Hand Pose Editor - HelpMeSign")
        editor.setMinimumSize(1200, 800)
        
        logger.info("Showing Hand Pose Editor...")
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
        
        logger.info("Hand Pose Editor should now be visible")
        
        # Keep the window open for a few seconds
        import time
        time.sleep(5)
        
        return editor
        
    except Exception as e:
        logger.error(f"Error creating Hand Pose Editor: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    try:
        logger.info("Starting direct Hand Pose Editor test...")
        editor = test_hand_pose_editor_direct()
        if editor:
            logger.info("Test completed successfully")
        else:
            logger.error("Test failed - editor not created")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
