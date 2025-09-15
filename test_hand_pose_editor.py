#!/usr/bin/env python3
"""
Test script for the Hand Pose Editor
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from PySide6.QtWidgets import QApplication
    from src.helpmesign.modes.learn.hand_pose_editor import HandPoseEditor
    
    def main():
        app = QApplication(sys.argv)
        
        # Create the hand pose editor
        editor = HandPoseEditor()
        editor.show()
        
        print("Hand Pose Editor launched successfully!")
        print("Features:")
        print("- 6x zoom view (hip and above only)")
        print("- Reference image display")
        print("- Hand, finger, and arm joint controls")
        print("- Quick pose presets (Fist, Open, Point)")
        print("- Real-time pose editing")
        print("- Language and letter selection")
        
        sys.exit(app.exec())
        
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure PySide6 is installed: pip install PySide6")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
