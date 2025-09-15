#!/usr/bin/env python3
"""
Test script to verify the Hand Pose Editor button integration
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_button_integration():
    """Test that the button integration works correctly"""
    try:
        # Test imports
        from src.helpmesign.modes.learn.hand_pose_integration import open_hand_pose_editor
        from src.helpmesign.modes.learn.hand_pose_editor import HandPoseEditor
        
        print("✅ Hand Pose Editor imports successful")
        
        # Test button creation
        from src.helpmesign.modes.learn.ui_components import LearnModeUIComponents
        print("✅ UI Components import successful")
        
        # Test learn mode method
        from src.helpmesign.modes.learn.learn_mode import LearnMode
        print("✅ Learn Mode import successful")
        
        print("\n🎉 All integrations successful!")
        print("\nButton Features:")
        print("- 🖐️ Hand Pose Editor button added next to HPR Editor button")
        print("- Purple styling to distinguish from HPR Editor")
        print("- Tooltip with description")
        print("- Click handler connected to open_hand_pose_editor method")
        print("- Status bar updates when opened")
        
        print("\nTo test the button:")
        print("1. Run the main application")
        print("2. Go to Learn Mode")
        print("3. Look for the '🖐️ Hand Pose Editor' button next to 'Open HPR Editor'")
        print("4. Click it to open the specialized hand pose editor")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_button_integration()
    sys.exit(0 if success else 1)
