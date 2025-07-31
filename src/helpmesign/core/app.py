import tkinter as tk
import sys
from datetime import datetime
from typing import Dict, Any, Optional

from ..utils.resource_manager import ResourceManager
from ..ui.components import MainWindow, StatusBar


class HelpMeSignApp:
    """Main application class for HelpMeSign"""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the HelpMeSign application
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.resource_manager = ResourceManager()
        
        # Load configuration
        self.config = self.resource_manager.load_config()
        
        # Create main window
        self.main_window = MainWindow(root, title="HelpMeSign")
        
        # Create status bar
        self.status_bar = StatusBar(root)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Set up application
        self.setup_application()
        self.setup_event_handlers()
    
    def setup_application(self) -> None:
        """Set up the application configuration and appearance"""
        # Set app icon if available
        self.set_app_icon()
        
        # Set window size from config or default
        window_width = self.config.get('window_size', {}).get('width', 1024)
        window_height = self.config.get('window_size', {}).get('height', 1024)
        self.main_window.set_window_size(window_width, window_height)
        self.main_window.set_resizable(False)
        
        # Center the window
        self.main_window.center_window()
        
        # Focus on input field
        self.main_window.text_input_frame.focus_input()
    
    def setup_event_handlers(self) -> None:
        """Set up event handlers for UI components"""
        # Bind text processing events
        self.main_window.text_input_frame.bind_process(self.process_text)
        self.main_window.text_input_frame.bind_clear(self.clear_text)
        self.main_window.text_input_frame.bind_enter_key(self.process_text)
        
        # Bind window close event
        self.main_window.bind_close_event(self.on_closing)
    
    def set_app_icon(self) -> None:
        """Set the application icon if available"""
        try:
            icon_path = self.resource_manager.get_image_path('icon.png')
            if self.resource_manager.resource_exists('image', 'icon.png'):
                self.main_window.set_icon(icon_path)
                print("App icon loaded successfully")
        except Exception as e:
            print(f"Could not load app icon: {e}")
    
    def process_text(self) -> None:
        """Process the entered text"""
        text = self.main_window.text_input_frame.get_text().strip()
        
        if text:
            # Add timestamp and process the text
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            processed_text = f"[{timestamp}] Processed: {text}\n"
            
            # Add to output
            self.main_window.output_frame.add_text(processed_text)
            
            # Clear input
            self.main_window.text_input_frame.clear_text()
            
            # Update status
            self.status_bar.set_status(f"Processed: {text}")
        else:
            self.status_bar.set_status("Please enter some text")
    
    def clear_text(self) -> None:
        """Clear the output text area"""
        self.main_window.output_frame.clear_text()
        self.main_window.text_input_frame.clear_text()
        self.status_bar.set_status("Cleared")
        self.main_window.text_input_frame.focus_input()
    
    def on_closing(self) -> None:
        """Handle application closing"""
        self.root.destroy()
        sys.exit()
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration"""
        return self.config.copy()
    
    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """Save configuration"""
        success = self.resource_manager.save_config(config_data)
        if success:
            self.config = config_data
        return success
    
    def get_resource_info(self) -> Dict[str, Any]:
        """Get information about available resources"""
        return self.resource_manager.get_resource_info()
    
    def run(self) -> None:
        """Start the application main loop"""
        self.root.mainloop()


def create_app() -> HelpMeSignApp:
    """Factory function to create the application"""
    root = tk.Tk()
    return HelpMeSignApp(root)


def main():
    """Main entry point for the application"""
    app = create_app()
    app.run()


if __name__ == "__main__":
    main() 