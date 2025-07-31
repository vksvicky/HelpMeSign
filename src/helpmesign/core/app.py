import tkinter as tk
import sys
from datetime import datetime
from typing import Dict, Any, Optional

from ..utils.resource_manager import ResourceManager
from ..utils.logger import get_logger, setup_logging, log_function_entry, log_function_exit, log_exception
from ..ui.components import MainWindow, StatusBar
from .startup import show_startup_screen, get_user_mode, set_user_mode


class HelpMeSignApp:
    """Main application class for HelpMeSign"""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the HelpMeSign application
        
        Args:
            root: Tkinter root window
        """
        log_function_entry(get_logger(), "HelpMeSignApp.__init__", root=root)
        
        self.root = root
        self.resource_manager = ResourceManager()
        
        # Load configuration
        self.config = self.resource_manager.load_config()
        
        # Set up logging
        self.logger = setup_logging(self.config)
        self.logger.info("Initializing HelpMeSign application")
        
        # Initialize user mode
        self.user_mode = None
        
        # Create main window
        self.main_window = MainWindow(root, title="HelpMeSign")
        self.logger.debug("Main window created")
        
        # Create status bar
        self.status_bar = StatusBar(root)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.logger.debug("Status bar created")
        
        # Set up application
        self.setup_application()
        self.setup_event_handlers()
        
        # Show startup screen if no user mode is set
        self.check_user_mode()
        
        log_function_exit(get_logger(), "HelpMeSignApp.__init__")
    
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
        
        # Bind text processing shortcuts
        self.main_window.text_input_frame.bind_shortcuts(self.process_text, self.clear_text)
        
        # Bind window close event
        self.main_window.bind_close_event(self.on_closing)
        
        # Bind menu events
        self.main_window.change_mode = self.change_user_mode
        self.main_window.set_mode = self.set_user_mode_from_menu
        self.main_window.on_settings_mode_change = self.set_user_mode_from_menu
    
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
    
    def check_user_mode(self) -> None:
        """Check user mode and show startup screen if needed"""
        log_function_entry(self.logger, "check_user_mode")
        
        try:
            # Try to get existing user mode
            self.user_mode = get_user_mode()
            self.logger.debug(f"Retrieved user mode: {self.user_mode}")
            
            # If no user mode is set, show startup screen
            if not self.user_mode:
                self.logger.info("No user mode found, showing startup screen")
                self.show_startup_screen()
            else:
                # Update status with current mode
                mode_name = "Sign & Translate" if self.user_mode == "sign" else "Learn Sign Language"
                self.status_bar.set_status(f"Current Mode: {mode_name}")
                self.logger.info(f"User mode set to: {mode_name}")
        except (Exception, ValueError) as e:
            # Handle first-time run or any config errors gracefully
            # Don't print error for first-time runs
            if "Configuration file has been tampered with" not in str(e):
                self.logger.warning(f"Config error: {e}")
            self.user_mode = None
            self.logger.info("Showing startup screen due to config error")
            self.show_startup_screen()
        
        log_function_exit(self.logger, "check_user_mode")
    
    def show_startup_screen(self) -> None:
        """Show the startup screen to get user choice"""
        log_function_entry(self.logger, "show_startup_screen")
        
        # Don't hide main window - just show startup screen on top
        self.logger.debug("Main window remains visible")
        
        # Show startup screen
        self.logger.info("Showing startup screen")
        choice = show_startup_screen(self.root)
        self.logger.debug(f"Startup screen returned choice: {choice}")
        
        # Main window is already visible
        self.logger.debug("Main window already visible")
        
        if choice:
            self.user_mode = choice
            mode_name = "Sign & Translate" if choice == "sign" else "Learn Sign Language"
            self.status_bar.set_status(f"Current Mode: {mode_name}")
            self.logger.info(f"User selected: {mode_name}")
            
            # Update UI based on mode
            self.update_ui_for_mode(choice)
        else:
            # User cancelled, use default mode
            self.user_mode = "sign"
            self.status_bar.set_status("Current Mode: Sign & Translate (Default)")
            self.logger.info("User cancelled, using default mode: Sign & Translate")
            self.update_ui_for_mode("sign")
        
        log_function_exit(self.logger, "show_startup_screen")
    
    def update_ui_for_mode(self, mode: str) -> None:
        """Update UI based on selected mode"""
        if mode == "sign":
            # Sign & Translate mode UI updates
            self.main_window.set_title("HelpMeSign - Sign & Translate")
            self.logger.info("UI updated for Sign & Translate mode")
            # Add sign-specific UI elements here
        elif mode == "learn":
            # Learn Sign Language mode UI updates
            self.main_window.set_title("HelpMeSign - Learn Sign Language")
            self.logger.info("UI updated for Learn Sign Language mode")
            # Add learn-specific UI elements here
    
    def change_user_mode(self) -> None:
        """Allow user to change their mode via menu"""
        self.show_startup_screen()
    
    def set_user_mode_from_menu(self, mode: str) -> None:
        """Set user mode from menu selection"""
        if mode in ['sign', 'learn']:
            self.user_mode = mode
            set_user_mode(mode)  # Save to secure config
            self.update_ui_for_mode(mode)
            
            # Update status
            mode_name = "Sign & Translate" if mode == "sign" else "Learn Sign Language"
            self.status_bar.set_status(f"Current Mode: {mode_name}")
            
            # Show confirmation
            import tkinter.messagebox as messagebox
            messagebox.showinfo(
                "Mode Changed",
                f"Switched to {mode_name}!\n\n"
                "Your preference has been saved securely."
            )
    
    def get_user_mode(self) -> Optional[str]:
        """Get current user mode"""
        return self.user_mode
    
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