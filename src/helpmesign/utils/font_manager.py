"""
Font Manager for HelpMeSign Application
Handles loading and managing Roboto fonts across the application
"""

import os
import tkinter as tk
from tkinter import font
from typing import Optional, Dict, Any
import platform


class FontManager:
    """Manages application fonts"""
    
    def __init__(self):
        self.fonts_loaded = False
        self.font_families = {}
        self._load_fonts()
    
    def _load_fonts(self) -> None:
        """Load Roboto fonts from resources"""
        try:
            # Get the path to the fonts directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            fonts_dir = os.path.join(project_root, "resources", "fonts")
            
            # Roboto font files
            font_files = {
                "Roboto": "Roboto-Regular.ttf",
                "Roboto-Bold": "Roboto-Bold.ttf",
                "Roboto-Light": "Roboto-Light.ttf",
                "Roboto-Medium": "Roboto-Medium.ttf"
            }
            
            # Try to load fonts if they exist
            for font_name, filename in font_files.items():
                font_path = os.path.join(fonts_dir, filename)
                if os.path.exists(font_path):
                    try:
                        # Load the font using tkinter
                        tk.font.families()  # Initialize font system
                        self.font_families[font_name] = font_path
                    except Exception as e:
                        print(f"Warning: Could not load font {font_name}: {e}")
            
            if self.font_families:
                self.fonts_loaded = True
                print(f"Loaded {len(self.font_families)} Roboto fonts")
            else:
                print("No Roboto fonts found, using system fonts")
                
        except Exception as e:
            print(f"Error loading fonts: {e}")
    
    def get_font(self, family: str = "Roboto", size: int = 10, weight: str = "normal", slant: str = "roman") -> tuple:
        """Get a font tuple for tkinter widgets"""
        if not self.fonts_loaded:
            # Fallback to system fonts
            if family == "Roboto":
                family = "Arial" if platform.system() == "Windows" else "Helvetica"
        
        return (family, size, weight, slant)
    
    def get_title_font(self) -> tuple:
        """Get font for titles"""
        return self.get_font("Roboto-Bold" if self.fonts_loaded else "Arial", 20, "bold")
    
    def get_heading_font(self) -> tuple:
        """Get font for headings"""
        return self.get_font("Roboto-Medium" if self.fonts_loaded else "Arial", 16, "bold")
    
    def get_subheading_font(self) -> tuple:
        """Get font for subheadings"""
        return self.get_font("Roboto-Medium" if self.fonts_loaded else "Arial", 14, "bold")
    
    def get_body_font(self) -> tuple:
        """Get font for body text"""
        return self.get_font("Roboto", 12, "normal")
    
    def get_small_font(self) -> tuple:
        """Get font for small text"""
        return self.get_font("Roboto", 10, "normal")
    
    def get_button_font(self) -> tuple:
        """Get font for buttons"""
        return self.get_font("Roboto-Medium" if self.fonts_loaded else "Arial", 11, "bold")
    
    def get_label_font(self) -> tuple:
        """Get font for labels"""
        return self.get_font("Roboto", 11, "normal")
    
    def get_input_font(self) -> tuple:
        """Get font for input fields"""
        return self.get_font("Roboto", 11, "normal")
    
    def get_menu_font(self) -> tuple:
        """Get font for menu items"""
        return self.get_font("Roboto", 12, "normal")


# Global font manager instance
_font_manager = None

def get_font_manager() -> FontManager:
    """Get the global font manager instance"""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
    return _font_manager

def get_font(family: str = "Roboto", size: int = 10, weight: str = "normal", slant: str = "roman") -> tuple:
    """Get a font tuple"""
    return get_font_manager().get_font(family, size, weight, slant)

def get_title_font() -> tuple:
    """Get title font"""
    return get_font_manager().get_title_font()

def get_heading_font() -> tuple:
    """Get heading font"""
    return get_font_manager().get_heading_font()

def get_subheading_font() -> tuple:
    """Get subheading font"""
    return get_font_manager().get_subheading_font()

def get_body_font() -> tuple:
    """Get body font"""
    return get_font_manager().get_body_font()

def get_small_font() -> tuple:
    """Get small font"""
    return get_font_manager().get_small_font()

def get_button_font() -> tuple:
    """Get button font"""
    return get_font_manager().get_button_font()

def get_label_font() -> tuple:
    """Get label font"""
    return get_font_manager().get_label_font()

def get_input_font() -> tuple:
    """Get input font"""
    return get_font_manager().get_input_font()

def get_menu_font() -> tuple:
    """Get menu font"""
    return get_font_manager().get_menu_font() 