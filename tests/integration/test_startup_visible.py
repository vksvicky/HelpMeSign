#!/usr/bin/env python3
"""
Test script to verify startup screen visibility
"""

import sys
import os
import tkinter as tk

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_startup_visibility():
    """Test if the startup screen is visible"""
    print("🧪 Testing startup screen visibility...")
    
    try:
        from helpmesign.core.startup import StartupScreen
        
        # Create a root window
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        print("✅ Root window created and hidden")
        
        # Create startup screen
        startup = StartupScreen(root)
        print("✅ Startup screen created")
        
        # Show the startup screen
        print("🔄 Showing startup screen...")
        choice = startup.show()
        print(f"✅ Startup screen returned choice: {choice}")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_startup_visibility() 