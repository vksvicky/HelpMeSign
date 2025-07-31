#!/usr/bin/env python3
"""
Test app without hiding main window
"""

import sys
import os
import tkinter as tk

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_app_no_hide():
    """Test the app without hiding the main window"""
    print("🧪 Testing app without hiding main window...")
    
    try:
        from helpmesign.core.app import HelpMeSignApp
        
        # Create root window
        root = tk.Tk()
        print("✅ Root window created")
        
        # Create app
        app = HelpMeSignApp(root)
        print("✅ App created")
        
        # Don't hide the main window, just show startup screen
        app.logger.info("Showing startup screen without hiding main window")
        
        # Show startup screen directly
        choice = app.show_startup_screen()
        print(f"✅ Startup screen returned: {choice}")
        
        # Run the app
        print("🔄 Running app...")
        app.run()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_app_no_hide() 