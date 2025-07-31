#!/usr/bin/env python3
"""
Settings dialog for HelpMeSign application
Follows macOS design patterns
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from ..utils.font_manager import (
    get_title_font, get_heading_font, get_body_font, get_label_font, 
    get_button_font, get_input_font, get_small_font
)


class SettingsDialog:
    """macOS-style settings dialog"""
    
    def __init__(self, parent, on_mode_change: Optional[Callable] = None):
        print("Initializing SettingsDialog...")
        self.parent = parent
        self.on_mode_change = on_mode_change
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("HelpMeSign Settings")
        self.dialog.geometry("500x500")
        self.dialog.resizable(False, False)
        
        # Completely disable menu creation for this window
        self.dialog.option_add('*Menu.tearOff', False)
        self.dialog.option_add('*tearOff', False)
        # Override the menu method to prevent any menu creation
        def no_menu(*args, **kwargs):
            return None
        # Only set menu attribute if it exists
        if hasattr(self.dialog, 'menu'):
            self.dialog.menu = no_menu
        
        # Make it a proper child window (no menu bar)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Aggressively remove menu bar - multiple approaches
        self.dialog.config(menu=None)
        self.dialog.option_add('*tearOff', False)
        self.dialog.option_add('*Menu.tearOff', False)
        
        # Set window attributes for proper child window behavior
        self.dialog.attributes('-topmost', False)
        self.dialog.focus_force()
        
        # Force remove any menu that might be created
        def remove_menu():
            try:
                self.dialog.config(menu=None)
                # Also try to remove any existing menu
                if hasattr(self.dialog, '_menu'):
                    delattr(self.dialog, '_menu')
            except:
                pass
        
        # Call multiple times to ensure menu is removed
        self.dialog.after(10, remove_menu)
        self.dialog.after(50, remove_menu)
        self.dialog.after(100, remove_menu)
        
        # Add rounded rectangle method to canvas
        self._add_canvas_methods()
        
        # Create UI components
        self.create_widgets()
        
        # Load current settings
        self.load_current_settings()
        
        # Center the window after widgets are created
        self.center_window()
        
        # Make it modal and focused
        self.dialog.focus_set()
        
        print("SettingsDialog initialization complete")
    
    def _add_canvas_methods(self):
        """Add custom methods to canvas for rounded rectangles"""
        def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
            """Create a rounded rectangle on canvas"""
            points = [
                x1 + radius, y1,
                x2 - radius, y1,
                x2, y1,
                x2, y1 + radius,
                x2, y2 - radius,
                x2, y2,
                x2 - radius, y2,
                x1 + radius, y2,
                x1, y2,
                x1, y2 - radius,
                x1, y1 + radius,
                x1, y1
            ]
            return canvas.create_polygon(points, **kwargs, smooth=True)
        
        # Add the method to canvas class
        tk.Canvas.create_rounded_rectangle = create_rounded_rectangle
    
    def center_window(self):
        """Center the settings window"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Create the settings UI"""
        print("Creating settings widgets...")
        
        # Main container
        main_frame = ttk.Frame(self.dialog, padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Settings", 
            font=get_title_font()
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30), sticky=tk.W)
        
        # Mode Selection Section
        mode_frame = ttk.LabelFrame(main_frame, text="Application Mode", padding="20")
        mode_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 25))
        mode_frame.columnconfigure(1, weight=1)
        
        # Mode description
        mode_desc = ttk.Label(
            mode_frame,
            text="Choose your preferred mode:",
            font=get_body_font()
        )
        mode_desc.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=tk.W)
        
        # Modern segmented control container
        toggle_frame = ttk.Frame(mode_frame)
        toggle_frame.grid(row=1, column=0, columnspan=2, pady=15, sticky=(tk.W, tk.E))
        toggle_frame.columnconfigure(0, weight=1)
        
        # Modern segmented control
        self.mode_var = tk.IntVar(value=0)  # 0 = sign, 1 = learn
        self.segmented_canvas = tk.Canvas(
            toggle_frame,
            width=300,
            height=40,
            bg='#f0f0f0',
            highlightthickness=0,
            relief='flat'
        )
        self.segmented_canvas.grid(row=0, column=0, pady=10)
        
        # Create segmented control
        self.create_segmented_control()
        
        # Bind click events
        self.segmented_canvas.bind('<Button-1>', self.on_segmented_click)
        
        # Mode description
        self.mode_desc_label = ttk.Label(
            mode_frame,
            text="Convert text to sign language and learn sign symbols",
            font=get_body_font(),
            foreground="gray",
            wraplength=400
        )
        self.mode_desc_label.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky=tk.W)
        
        # Preferences Section
        prefs_frame = ttk.LabelFrame(main_frame, text="Preferences", padding="20")
        prefs_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 25))
        prefs_frame.columnconfigure(1, weight=1)
        
        # Auto-save preference
        self.auto_save_var = tk.BooleanVar(value=True)
        auto_save_check = ttk.Checkbutton(
            prefs_frame,
            text="Auto-save preferences",
            variable=self.auto_save_var
        )
        auto_save_check.grid(row=0, column=0, pady=8, sticky=tk.W)
        
        # Show status bar preference
        self.show_status_var = tk.BooleanVar(value=True)
        status_check = ttk.Checkbutton(
            prefs_frame,
            text="Show status bar",
            variable=self.show_status_var
        )
        status_check.grid(row=1, column=0, pady=8, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0), sticky=(tk.E, tk.W))
        button_frame.columnconfigure(0, weight=1)
        
        # OK button (primary action) - make it more prominent
        ok_btn = ttk.Button(
            button_frame,
            text="OK",
            command=self.ok,
            style="Roboto.TButton"
        )
        ok_btn.grid(row=0, column=1, padx=(10, 0), sticky=tk.E)
        
        # Focus on OK button for better UX
        ok_btn.focus_set()
        
        # Bind Enter key to OK button
        self.dialog.bind('<Return>', lambda e: self.ok())
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
        
        print("Settings widgets created successfully")
    
    def load_current_settings(self):
        """Load current application settings"""
        # This would load from the actual config
        # For now, we'll use defaults
        # Set initial slider value based on current mode (default to sign mode)
        self.mode_var.set(0)  # 0 = sign mode
    
    def create_segmented_control(self):
        """Create the modern segmented control visual elements"""
        # Clear canvas
        self.segmented_canvas.delete("all")
        
        # Get current state
        current_mode = self.mode_var.get()
        
        # Colors
        business_blue = '#2563eb'  # Professional business blue
        white_color = '#ffffff'
        text_color = '#1f2937'  # Dark gray for text
        
        # Dimensions
        width = 300
        height = 40
        segment_width = width // 2
        
        # Draw background (business blue)
        self.segmented_canvas.create_rounded_rectangle(
            0, 0, width, height,
            radius=20,
            fill=business_blue,
            outline='',
            tags="background"
        )
        
        # Draw white pill (selected segment)
        if current_mode == 0:  # Sign & Translate
            pill_x1 = 2
            pill_x2 = segment_width - 2
        else:  # Learn Sign Language
            pill_x1 = segment_width + 2
            pill_x2 = width - 2
        
        self.segmented_canvas.create_rounded_rectangle(
            pill_x1, 2, pill_x2, height - 2,
            radius=18,
            fill=white_color,
            outline='',
            tags="pill"
        )
        
        # Add text labels with smaller font
        # Sign & Translate text
        sign_text_color = business_blue if current_mode == 0 else white_color
        self.segmented_canvas.create_text(
            segment_width // 2, height // 2,
            text="Sign & Translate",
            fill=sign_text_color,
            font=("Arial", 10, "bold"),  # Custom smaller font
            tags="sign_text"
        )
        
        # Learn Sign Language text
        learn_text_color = business_blue if current_mode == 1 else white_color
        self.segmented_canvas.create_text(
            segment_width + segment_width // 2, height // 2,
            text="Learn Sign Language",
            fill=learn_text_color,
            font=("Arial", 10, "bold"),  # Custom smaller font
            tags="learn_text"
        )
    
    def on_segmented_click(self, event):
        """Handle segmented control click"""
        # Get click position
        x = event.x
        width = 300
        segment_width = width // 2
        
        # Determine which segment was clicked
        if x < segment_width:
            new_mode = 0  # Sign & Translate
        else:
            new_mode = 1  # Learn Sign Language
        
        # Update the mode
        self.mode_var.set(new_mode)
        
        # Update the visual segmented control
        self.create_segmented_control()
        
        # Update description
        if new_mode == 0:
            self.mode_desc_label.config(text="Convert text to sign language and learn sign symbols")
        else:
            self.mode_desc_label.config(text="Learn about sign language symbols and words")
        
        print(f"Segmented control switched to mode: {new_mode}")
    
    def on_slider_change(self, value):
        """Handle slider value change (kept for compatibility)"""
        # This method is no longer used but kept for compatibility
        pass
    
    def get_selected_mode(self):
        """Get the currently selected mode from slider"""
        mode_value = self.mode_var.get()
        return "sign" if mode_value == 0 else "learn"
    
    def ok(self):
        """Apply settings and close"""
        try:
            # Apply the selected mode from slider
            selected_mode = self.get_selected_mode()
            
            # Call the callback if provided
            if self.on_mode_change:
                self.on_mode_change(selected_mode)
            
            # Close the dialog
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to apply settings: {str(e)}"
            )
    
    def show(self):
        """Show the settings dialog"""
        self.dialog.wait_window()
        return self.result


def show_settings_dialog(parent, on_mode_change: Optional[Callable] = None):
    """Show the settings dialog"""
    dialog = SettingsDialog(parent, on_mode_change)
    return dialog.show() 