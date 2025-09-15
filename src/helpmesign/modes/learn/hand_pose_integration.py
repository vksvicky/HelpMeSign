#!/usr/bin/env python3
"""
Integration module for Hand Pose Editor
Provides easy access to the specialized hand pose editor
"""

import logging
from typing import Optional

from PySide6.QtCore import Qt

from .hand_pose_editor import HandPoseEditor

logger = logging.getLogger(__name__)


class HandPoseEditorLauncher:
    """Launcher for the Hand Pose Editor"""

    def __init__(self, parent=None):
        self.parent = parent
        self.editor_instance: Optional[HandPoseEditor] = None

    def open_hand_pose_editor(self):
        """Open the Hand Pose Editor"""
        try:
            if self.editor_instance is None or not self.editor_instance.isVisible():
                self.editor_instance = HandPoseEditor(self.parent)
                self.editor_instance.show()
                logger.info("Hand Pose Editor opened")
            else:
                self.editor_instance.raise_()
                self.editor_instance.activateWindow()
                logger.info("Hand Pose Editor brought to front")

        except Exception as e:
            logger.error(f"Error opening Hand Pose Editor: {e}")

    def close_hand_pose_editor(self):
        """Close the Hand Pose Editor"""
        if self.editor_instance and self.editor_instance.isVisible():
            self.editor_instance.close()
            logger.info("Hand Pose Editor closed")


def create_hand_pose_editor_button(parent_widget, launcher: HandPoseEditorLauncher):
    """Create a button to open the Hand Pose Editor"""
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QPushButton

        button = QPushButton("🖐️ Open Hand Pose Editor")
        button.setToolTip("Open specialized editor for hand, finger, and arm poses")
        button.clicked.connect(launcher.open_hand_pose_editor)

        # Style the button
        button.setStyleSheet(
            """
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
            QPushButton:pressed {
                background-color: #7d3c98;
            }
        """
        )

        return button

    except ImportError:
        logger.warning("PySide6 not available for button creation")
        return None


# Convenience function for quick access
def open_hand_pose_editor(main_window):
    """Quick function to open the Hand Pose Editor"""
    try:
        # Get the animate_panel from the main window
        animate_panel = None
        if hasattr(main_window, "learn_mode"):
            learn_mode = main_window.learn_mode
            logger.info(f"Learn mode found: {learn_mode}")
            logger.info(f"Learn mode attributes: {dir(learn_mode)}")

            if hasattr(learn_mode, "animate_gesture_panel"):
                animate_panel = learn_mode.animate_gesture_panel
                logger.info(f"Found animate_gesture_panel: {animate_panel}")
            else:
                logger.warning("No animate_gesture_panel found in learn_mode")
        else:
            logger.warning("No learn_mode found in main_window")

        # Create the Hand Pose Editor with proper parameters
        logger.info("Creating Hand Pose Editor...")
        editor = HandPoseEditor(animate_panel, main_window)

        # Set window properties
        editor.setWindowTitle("Hand Pose Editor - HelpMeSign")
        editor.setMinimumSize(1200, 800)

        # Show the window - same approach as HPR Editor
        logger.info("Showing Hand Pose Editor window...")
        editor.show()
        editor.raise_()
        editor.activateWindow()

        logger.info("Hand Pose Editor opened successfully")
        return editor

    except Exception as e:
        logger.error(f"Error opening Hand Pose Editor: {e}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        return None
