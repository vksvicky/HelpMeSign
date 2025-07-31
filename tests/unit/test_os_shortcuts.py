#!/usr/bin/env python3
"""
Test script to demonstrate OS-specific keyboard shortcuts
"""

import platform
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from helpmesign.ui.components import get_os_shortcuts

def test_os_detection():
    """Test OS detection and shortcut generation"""
    print("=== OS-Specific Keyboard Shortcuts Test ===\n")
    
    # Get current OS
    system = platform.system()
    print(f"Current OS: {system}")
    
    # Get shortcuts
    shortcuts = get_os_shortcuts()
    print(f"Detected shortcuts: {shortcuts}")
    
    print("\n=== Menu Examples ===")
    if system == "Darwin":  # macOS
        print("macOS Menu Display:")
        print(f"  Settings...    {shortcuts['cmd']},")
        print(f"  Quit HelpMeSign {shortcuts['cmd']}Q")
        print(f"  Clear All      {shortcuts['cmd']}K")
        print(f"  Close Window   {shortcuts['cmd']}W")
        print(f"  HelpMeSign Help {shortcuts['cmd']}{shortcuts['question']}")
    else:  # Windows/Linux
        print("Windows/Linux Menu Display:")
        print(f"  Settings...    {shortcuts['cmd']}+,")
        print(f"  Quit HelpMeSign {shortcuts['cmd']}+Q")
        print(f"  Clear All      {shortcuts['cmd']}+K")
        print(f"  Close Window   {shortcuts['cmd']}+W")
        print(f"  HelpMeSign Help {shortcuts['cmd']}+{shortcuts['question']}")
    
    print("\n=== Help Dialog Example ===")
    if system == "Darwin":
        print("macOS Help Text:")
        print(f"• {shortcuts['cmd']}, - Open Settings")
        print(f"• {shortcuts['cmd']}K - Clear All")
        print(f"• {shortcuts['cmd']}W - Close Window")
        print(f"• {shortcuts['cmd']}Q - Quit Application")
        print(f"• {shortcuts['cmd']}{shortcuts['question']} - Show Help")
        print(f"• {shortcuts['cmd']}{shortcuts['enter']} - Process Text")
        print(f"• {shortcuts['cmd']}{shortcuts['shift']}K - Clear Text Input")
    else:
        print("Windows/Linux Help Text:")
        print(f"• {shortcuts['cmd']}+, - Open Settings")
        print(f"• {shortcuts['cmd']}+K - Clear All")
        print(f"• {shortcuts['cmd']}+W - Close Window")
        print(f"• {shortcuts['cmd']}+Q - Quit Application")
        print(f"• {shortcuts['cmd']}+{shortcuts['question']} - Show Help")
        print(f"• {shortcuts['cmd']}+{shortcuts['enter']} - Process Text")
        print(f"• {shortcuts['cmd']}+{shortcuts['shift']}+K - Clear Text Input")
    
    print("\n=== Cross-Platform Build Test ===")
    print("When you build the app for different platforms:")
    print("• macOS app (.app): Will show ⌘ symbols")
    print("• Windows exe (.exe): Will show Ctrl symbols")
    print("• Linux executable: Will show Ctrl symbols")
    print("\nThe actual keyboard bindings work on all platforms!")

if __name__ == "__main__":
    test_os_detection() 