#!/usr/bin/env python3
"""Debug script to test menu accelerators"""

import platform
import tkinter as tk
from tkinter import ttk


def get_os_shortcuts():
    """Get OS-specific keyboard shortcut symbols"""
    system = platform.system().lower()
    print(f"Detected system: {system}")
    if system == "darwin":  # macOS
        return {"cmd": "⌘", "shift": "⇧", "enter": "⏎", "question": "?"}
    else:  # Windows/Linux
        return {"cmd": "Ctrl", "shift": "Shift", "enter": "Enter", "question": "?"}


def test_menu():
    root = tk.Tk()
    root.title("Menu Accelerator Test")
    root.geometry("400x300")

    # Get shortcuts
    shortcuts = get_os_shortcuts()
    print(f"Shortcuts: {shortcuts}")

    # Create menu bar
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    # Test menu
    test_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Test", menu=test_menu)

    # Add menu items with accelerators
    test_menu.add_command(
        label="Settings",
        command=lambda: print("Settings clicked"),
        accelerator=f"{shortcuts['cmd']},",
    )
    test_menu.add_command(
        label="Quit", command=root.quit, accelerator=f"{shortcuts['cmd']}Q"
    )

    # Also test with hardcoded values
    test_menu.add_separator()
    test_menu.add_command(
        label="Test 1", command=lambda: print("Test 1 clicked"), accelerator="⌘K"
    )
    test_menu.add_command(
        label="Test 2", command=lambda: print("Test 2 clicked"), accelerator="Ctrl+W"
    )

    print("Menu created. Check if accelerators are visible.")
    root.mainloop()


if __name__ == "__main__":
    test_menu()
