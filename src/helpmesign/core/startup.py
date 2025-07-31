"""
Startup screen module for HelpMeSign
Handles user choice between sign and learn modes
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import hashlib
import hmac
from pathlib import Path
from typing import Optional, Dict, Any


class StartupScreen:
    """Startup screen with user choice functionality"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.choice = None
        self.config_manager = SecureConfigManager()
        
    def show(self) -> Optional[str]:
        """Show startup screen and return user choice"""
        # Create startup window
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Welcome to HelpMeSign")
        self.window.geometry("600x400")
        self.window.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Make it modal
        self.window.transient(self.parent) if self.parent else None
        self.window.grab_set()
        
        # Create UI
        self.create_widgets()
        
        # Load previous choice if exists
        self.load_previous_choice()
        
        # Wait for user choice
        self.window.wait_window()
        
        return self.choice
    
    def center_window(self):
        """Center the startup window"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Create startup screen widgets"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Welcome to HelpMeSign", 
            font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Subtitle
        subtitle_label = ttk.Label(
            main_frame,
            text="Choose your preferred mode to get started:",
            font=("Arial", 12)
        )
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 30))
        
        # Sign mode option
        sign_frame = ttk.LabelFrame(main_frame, text="Sign Mode", padding="15")
        sign_frame.grid(row=2, column=0, padx=(0, 10), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        sign_icon = ttk.Label(sign_frame, text="✍️", font=("Arial", 24))
        sign_icon.grid(row=0, column=0, pady=(0, 10))
        
        sign_title = ttk.Label(sign_frame, text="Document Signing", font=("Arial", 14, "bold"))
        sign_title.grid(row=1, column=0, pady=(0, 5))
        
        sign_desc = ttk.Label(
            sign_frame, 
            text="Sign documents and contracts\nwith digital signatures",
            font=("Arial", 10),
            justify=tk.CENTER
        )
        sign_desc.grid(row=2, column=0, pady=(0, 15))
        
        sign_button = ttk.Button(
            sign_frame,
            text="Choose Sign Mode",
            command=lambda: self.make_choice("sign"),
            style="Accent.TButton"
        )
        sign_button.grid(row=3, column=0, pady=(0, 5))
        
        # Learn mode option
        learn_frame = ttk.LabelFrame(main_frame, text="Learn Mode", padding="15")
        learn_frame.grid(row=2, column=1, padx=(10, 0), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        learn_icon = ttk.Label(learn_frame, text="📚", font=("Arial", 24))
        learn_icon.grid(row=0, column=0, pady=(0, 10))
        
        learn_title = ttk.Label(learn_frame, text="Learning & Education", font=("Arial", 14, "bold"))
        learn_title.grid(row=1, column=0, pady=(0, 5))
        
        learn_desc = ttk.Label(
            learn_frame,
            text="Learn about digital signatures\nand best practices",
            font=("Arial", 10),
            justify=tk.CENTER
        )
        learn_desc.grid(row=2, column=0, pady=(0, 15))
        
        learn_button = ttk.Button(
            learn_frame,
            text="Choose Learn Mode",
            command=lambda: self.make_choice("learn"),
            style="Accent.TButton"
        )
        learn_button.grid(row=3, column=0, pady=(0, 5))
        
        # Info section
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding="10")
        info_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0), sticky=(tk.W, tk.E))
        
        info_text = ttk.Label(
            info_frame,
            text="💡 You can change your choice later via the menu options.\nYour preference will be saved securely for future sessions.",
            font=("Arial", 10),
            justify=tk.CENTER
        )
        info_text.grid(row=0, column=0)
        
        # Configure column weights for equal sizing
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def load_previous_choice(self):
        """Load and display previous user choice if available"""
        try:
            config = self.config_manager.load_config()
            if config and 'user_mode' in config:
                previous_mode = config['user_mode']
                if previous_mode in ['sign', 'learn']:
                    # Highlight the previous choice
                    self.highlight_previous_choice(previous_mode)
        except (Exception, ValueError) as e:
            # Silently handle any loading errors (including tamper detection on first run)
            # This is expected behavior when no config exists yet
            pass
    
    def highlight_previous_choice(self, mode: str):
        """Highlight the previously selected mode"""
        # This could be enhanced with visual indicators
        pass
    
    def make_choice(self, choice: str):
        """Handle user choice"""
        self.choice = choice
        
        # Save choice to secure config
        try:
            config = self.config_manager.load_config() or {}
            config['user_mode'] = choice
            config['last_updated'] = self.get_timestamp()
            self.config_manager.save_config(config)
            
            # Show confirmation
            mode_name = "Sign Mode" if choice == "sign" else "Learn Mode"
            messagebox.showinfo(
                "Choice Saved",
                f"You've selected {mode_name}!\n\n"
                "Your preference has been saved securely.\n"
                "You can change this later via the menu options."
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to save your choice: {str(e)}\n\n"
                "Your choice will not be remembered for future sessions."
            )
        
        # Close startup window
        self.window.destroy()
    
    def get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


class SecureConfigManager:
    """Secure configuration manager for user preferences"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".helpmesign"
        self.config_file = self.config_dir / "user_config.secure"
        self.secret_key = self._get_secret_key()
    
    def _get_secret_key(self) -> bytes:
        """Get or generate secret key for encryption"""
        key_file = self.config_dir / ".secret_key"
        
        if key_file.exists():
            try:
                return key_file.read_bytes()
            except Exception:
                pass
        
        # Generate new secret key
        import secrets
        key = secrets.token_bytes(32)
        
        # Ensure directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Save key with restricted permissions
        try:
            key_file.write_bytes(key)
            key_file.chmod(0o600)  # Owner read/write only
        except Exception:
            # Fallback to a deterministic key if file operations fail
            key = hashlib.sha256(b"HelpMeSign_Default_Key").digest()
        
        return key
    
    def _encrypt_data(self, data: str) -> bytes:
        """Encrypt data using HMAC"""
        return hmac.new(self.secret_key, data.encode('utf-8'), hashlib.sha256).digest()
    
    def _verify_data(self, data: str, signature: bytes) -> bool:
        """Verify data integrity"""
        expected_signature = self._encrypt_data(data)
        return hmac.compare_digest(signature, expected_signature)
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration securely"""
        try:
            # Ensure directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Convert config to JSON
            config_json = json.dumps(config, indent=2, ensure_ascii=False)
            
            # Create signature
            signature = self._encrypt_data(config_json)
            
            # Combine data and signature
            secure_data = {
                'data': config_json,
                'signature': signature.hex(),
                'version': '1.0'
            }
            
            # Save to file with restricted permissions
            with open(self.config_file, 'w') as f:
                json.dump(secure_data, f, indent=2)
            
            # Set restrictive permissions
            self.config_file.chmod(0o600)  # Owner read/write only
            
            return True
            
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def load_config(self) -> Optional[Dict[str, Any]]:
        """Load configuration securely"""
        try:
            if not self.config_file.exists():
                return None
            
            # Read secure data
            with open(self.config_file, 'r') as f:
                secure_data = json.load(f)
            
            # Verify signature
            data = secure_data['data']
            signature = bytes.fromhex(secure_data['signature'])
            
            if not self._verify_data(data, signature):
                raise ValueError("Configuration file has been tampered with")
            
            # Parse config
            config = json.loads(data)
            return config
            
        except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as e:
            # Handle first-time run or corrupted config gracefully
            # Don't print error for first-time runs (file not found)
            if not isinstance(e, FileNotFoundError):
                print(f"Config error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error loading config: {e}")
            return None
    
    def get_user_mode(self) -> Optional[str]:
        """Get current user mode"""
        config = self.load_config()
        return config.get('user_mode') if config else None
    
    def set_user_mode(self, mode: str) -> bool:
        """Set user mode"""
        config = self.load_config() or {}
        config['user_mode'] = mode
        config['last_updated'] = self.get_timestamp()
        return self.save_config(config)
    
    def get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


def show_startup_screen(parent=None) -> Optional[str]:
    """Show startup screen and return user choice"""
    startup = StartupScreen(parent)
    return startup.show()


def get_user_mode() -> Optional[str]:
    """Get current user mode from secure config"""
    try:
        config_manager = SecureConfigManager()
        return config_manager.get_user_mode()
    except (Exception, ValueError) as e:
        # Handle first-time run or any config errors gracefully
        # Don't print error for first-time runs
        if "Configuration file has been tampered with" not in str(e):
            print(f"Config error: {e}")
        return None


def set_user_mode(mode: str) -> bool:
    """Set user mode in secure config"""
    config_manager = SecureConfigManager()
    return config_manager.set_user_mode(mode) 