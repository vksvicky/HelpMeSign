#!/usr/bin/env python3
"""
Very simple startup screen test
"""

import tkinter as tk
from tkinter import ttk, messagebox


def create_simple_startup():
    """Create a simple startup screen"""
    print("Creating simple startup screen...")

    # Create root window
    root = tk.Tk()
    root.withdraw()  # Hide root

    # Create startup window
    startup = tk.Toplevel(root)
    startup.title("Welcome to HelpMeSign")
    startup.geometry("400x300")
    startup.resizable(False, False)

    # Center the window
    startup.update_idletasks()
    width = startup.winfo_width()
    height = startup.winfo_height()
    x = (startup.winfo_screenwidth() // 2) - (width // 2)
    y = (startup.winfo_screenheight() // 2) - (height // 2)
    startup.geometry(f"{width}x{height}+{x}+{y}")

    # Make it modal and bring to front
    startup.transient(root)
    startup.grab_set()
    startup.focus_set()
    startup.lift()
    startup.attributes("-topmost", True)

    # Add some content
    label = ttk.Label(
        startup, text="Welcome to HelpMeSign!\n\nChoose your mode:", font=("Arial", 14)
    )
    label.pack(pady=20)

    def choose_sign():
        messagebox.showinfo("Choice", "You chose Sign Mode!")
        startup.destroy()
        root.destroy()

    def choose_learn():
        messagebox.showinfo("Choice", "You chose Learn Mode!")
        startup.destroy()
        root.destroy()

    button_frame = ttk.Frame(startup)
    button_frame.pack(pady=20)

    sign_btn = ttk.Button(button_frame, text="Sign Mode", command=choose_sign)
    sign_btn.pack(side=tk.LEFT, padx=10)

    learn_btn = ttk.Button(button_frame, text="Learn Mode", command=choose_learn)
    learn_btn.pack(side=tk.LEFT, padx=10)

    # Remove topmost after a short delay
    startup.after(100, lambda: startup.attributes("-topmost", False))

    print("Startup screen created and should be visible")
    print("Click one of the buttons to test...")

    # Wait for window to close
    startup.wait_window()
    root.destroy()


if __name__ == "__main__":
    create_simple_startup()
