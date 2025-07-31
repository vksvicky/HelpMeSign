#!/usr/bin/env python3
"""Test script for settings dialog"""

import tkinter as tk
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from helpmesign.ui.settings_dialog import show_settings_dialog

def test_settings():
    """Test the settings dialog"""
    root = tk.Tk()
    root.title("Settings Dialog Test")
    root.geometry("400x300")
    
    def on_mode_change(mode):
        print(f"Mode changed to: {mode}")
    
    def open_settings():
        show_settings_dialog(root, on_mode_change)
    
    # Add a button to open settings
    btn = tk.Button(root, text="Open Settings", command=open_settings)
    btn.pack(expand=True)
    
    label = tk.Label(root, text="Click the button to test the settings dialog.\nCheck that:\n1. No menu appears\n2. OK button is visible and works")
    label.pack(expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    test_settings() 