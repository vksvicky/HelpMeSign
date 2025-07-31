#!/usr/bin/env python3
"""
Test script to run the app with logging enabled
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_app_with_logging():
    """Test the app with logging enabled"""
    print("🧪 Testing app with logging...")
    
    try:
        from helpmesign.core.app import HelpMeSignApp
        import tkinter as tk
        
        # Create root window
        root = tk.Tk()
        print("✅ Root window created")
        
        # Create app (this will set up logging)
        app = HelpMeSignApp(root)
        print("✅ App created with logging")
        
        # Set user mode directly to skip startup screen for now
        app.user_mode = "sign"
        app.logger.info("User mode set to 'sign' for testing")
        
        # Update UI
        app.update_ui_for_mode("sign")
        app.logger.info("UI updated for sign mode")
        
        # Show the window
        root.deiconify()
        app.logger.info("Main window shown")
        
        # Run the app
        print("🔄 Running app with logging...")
        app.logger.info("Starting application main loop")
        app.run()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_app_with_logging() 