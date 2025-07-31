import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Any
import platform
from ..utils.font_manager import (
    get_title_font, get_heading_font, get_body_font, get_label_font, 
    get_button_font, get_input_font, get_menu_font, get_small_font
)


def get_os_shortcuts():
    """Get OS-specific keyboard shortcut symbols"""
    system = platform.system().lower()
    print(f"Platform system: {system}")
    if system == "darwin":  # macOS
        return {
            "cmd": "⌘",
            "shift": "⇧",
            "enter": "⏎",
            "question": "?"
        }
    else:  # Windows/Linux
        return {
            "cmd": "Ctrl",
            "shift": "Shift",
            "enter": "Enter",
            "question": "?"
        }


class TextInputFrame(ttk.Frame):
    """Frame containing text input and processing controls"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the text input UI components"""
        # Input label and field
        label = ttk.Label(self, text="Enter text:", font=get_label_font())
        label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.text_input = ttk.Entry(self, width=50, font=get_input_font())
        self.text_input.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.process_button = ttk.Button(button_frame, text="Process", style="Roboto.TButton")
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear", style="Roboto.TButton")
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        self.columnconfigure(1, weight=1)
    
    def get_text(self) -> str:
        """Get the current text from the input field"""
        return self.text_input.get()
    
    def set_text(self, text: str) -> None:
        """Set text in the input field"""
        self.text_input.delete(0, tk.END)
        self.text_input.insert(0, text)
    
    def clear_text(self) -> None:
        """Clear the input field"""
        self.text_input.delete(0, tk.END)
    
    def focus_input(self) -> None:
        """Focus on the input field"""
        self.text_input.focus()
    
    def bind_process(self, callback: Callable) -> None:
        """Bind process button to callback"""
        self.process_button.configure(command=callback)
    
    def bind_clear(self, callback: Callable) -> None:
        """Bind clear button to callback"""
        self.clear_button.configure(command=callback)
    
    def bind_enter_key(self, callback: Callable) -> None:
        """Bind Enter key to callback"""
        self.text_input.bind('<Return>', lambda event: callback())
    
    def bind_shortcuts(self, process_callback: Callable, clear_callback: Callable) -> None:
        """Bind keyboard shortcuts for text processing"""
        # Process text shortcut (Cmd+Enter)
        self.text_input.bind('<Command-Return>', lambda event: process_callback())
        self.text_input.bind('<Control-Return>', lambda event: process_callback())  # Windows/Linux
        
        # Clear text shortcut (Cmd+Shift+K)
        self.text_input.bind('<Command-Shift-K>', lambda event: clear_callback())
        self.text_input.bind('<Control-Shift-K>', lambda event: clear_callback())  # Windows/Linux


class OutputFrame(ttk.Frame):
    """Frame containing output display area"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the output UI components"""
        # Output label
        label = ttk.Label(self, text="Output:", font=get_label_font())
        label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Text widget for output
        self.output_text = tk.Text(self, height=20, width=60, wrap=tk.WORD, font=get_body_font())
        self.output_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.output_text.yview)
        scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
    
    def add_text(self, text: str) -> None:
        """Add text to the output area"""
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
    
    def clear_text(self) -> None:
        """Clear the output area"""
        self.output_text.delete(1.0, tk.END)
    
    def get_text(self) -> str:
        """Get all text from the output area"""
        return self.output_text.get(1.0, tk.END)
    
    def set_text(self, text: str) -> None:
        """Set text in the output area"""
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, text)


class StatusBar(ttk.Frame):
    """Status bar component"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the status bar UI"""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status_label = ttk.Label(
            self, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            font=get_small_font()
        )
        status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.columnconfigure(0, weight=1)
    
    def set_status(self, message: str) -> None:
        """Set the status message"""
        self.status_var.set(message)
    
    def get_status(self) -> str:
        """Get the current status message"""
        return self.status_var.get()


class MainWindow:
    """Main application window"""
    
    def __init__(self, root: tk.Tk, title: str = "HelpMeSign"):
        self.root = root
        self.root.title(title)
        
        # Create menu bar
        self.create_menu()
        
        # Set up main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # Create title
        title_label = ttk.Label(self.main_frame, text=title, font=get_title_font())
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Create UI components
        self.text_input_frame = TextInputFrame(self.main_frame)
        self.text_input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.output_frame = OutputFrame(self.main_frame)
        self.output_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Configure main frame grid weights
        self.main_frame.rowconfigure(2, weight=1)
    
    def set_window_size(self, width: int, height: int) -> None:
        """Set the window size"""
        self.root.geometry(f"{width}x{height}")
    
    def set_resizable(self, resizable: bool) -> None:
        """Set whether the window is resizable"""
        self.root.resizable(resizable, resizable)
    
    def center_window(self) -> None:
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def set_icon(self, icon_path: str) -> None:
        """Set the window icon"""
        try:
            icon = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, icon)
            # Keep a reference to prevent garbage collection
            self.app_icon = icon
        except Exception as e:
            print(f"Could not load app icon: {e}")
    
    def create_menu(self) -> None:
        """Create the application menu bar"""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # Get OS-specific shortcuts
        shortcuts = get_os_shortcuts()
        print(f"Creating menu with shortcuts: {shortcuts}")
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
        
        # HelpMeSign menu (replaces Python menu)
        self.app_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="HelpMeSign", menu=self.app_menu)
        self.app_menu.add_command(label="About HelpMeSign", command=self.show_about)
        self.app_menu.add_separator()
        
        # Create menu items with proper accelerator format
        # Use a more explicit approach for macOS
        if platform.system() == "Darwin":
            # macOS - use proper Unicode symbols with space
            self.app_menu.add_command(label="Settings...", command=self.show_settings, accelerator="⌘, ")
            self.app_menu.add_separator()
            self.app_menu.add_command(label="Quit HelpMeSign", command=self.root.quit, accelerator="⌘Q ")
        else:
            # Windows/Linux - use standard format
            self.app_menu.add_command(label="Settings...", command=self.show_settings, accelerator="Ctrl+,")
            self.app_menu.add_separator()
            self.app_menu.add_command(label="Quit HelpMeSign", command=self.root.quit, accelerator="Ctrl+Q")
        
        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        if platform.system() == "Darwin":
            self.file_menu.add_command(label="Clear All", command=self.clear_all, accelerator="⌘K ")
            self.file_menu.add_separator()
            self.file_menu.add_command(label="Close Window", command=self.root.withdraw, accelerator="⌘W ")
        else:
            self.file_menu.add_command(label="Clear All", command=self.clear_all, accelerator="Ctrl+K")
            self.file_menu.add_separator()
            self.file_menu.add_command(label="Close Window", command=self.root.withdraw, accelerator="Ctrl+W")
        
        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        
        if platform.system() == "Darwin":
            self.help_menu.add_command(label="HelpMeSign Help", command=self.show_help, accelerator="⌘? ")
        else:
            self.help_menu.add_command(label="HelpMeSign Help", command=self.show_help, accelerator="F1")
    
    def clear_all(self) -> None:
        """Clear all text areas"""
        if hasattr(self, 'text_input_frame'):
            self.text_input_frame.clear_text()
        if hasattr(self, 'output_frame'):
            self.output_frame.clear_text()
    
    def change_mode(self) -> None:
        """Change user mode - now handled in settings"""
        self.show_settings()
    
    def set_mode(self, mode: str) -> None:
        """Set user mode - now handled in settings"""
        # This will be implemented in the settings dialog
        pass
    
    def show_about(self) -> None:
        """Show about dialog"""
        import tkinter.messagebox as messagebox
        messagebox.showinfo(
            "About HelpMeSign",
            "HelpMeSign v1.0.0\n\n"
            "An application for Sign Language translation and learning.\n\n"
            "Features:\n"
            "• Sign & Translate: Convert text to sign language\n"
            "• Learn Sign Language: Educational content and symbols\n"
            "• Secure configuration management\n"
            "• Cross-platform support"
        )
    
    def show_settings(self) -> None:
        """Show settings dialog"""
        try:
            from .settings_dialog import show_settings_dialog
            show_settings_dialog(self.root, self.on_settings_mode_change)
        except ImportError:
            # Fallback to simple dialog if settings module not available
            import tkinter.messagebox as messagebox
            messagebox.showinfo(
                "Settings",
                "Settings window will be implemented here.\n\n"
                "This will include:\n"
                "• Mode selection (Sign & Translate / Learn Sign Language)\n"
                "• Application preferences\n"
                "• Display options\n"
                "• Language settings"
            )
    
    def on_settings_mode_change(self, mode: str) -> None:
        """Handle mode change from settings dialog"""
        # This will be overridden by the main app
        if hasattr(self, 'set_mode'):
            self.set_mode(mode)
    
    def show_help(self) -> None:
        """Show help dialog"""
        import tkinter.messagebox as messagebox
        
        # Get OS-specific shortcuts
        shortcuts = get_os_shortcuts()
        system = platform.system()
        
        if system == "Darwin":  # macOS
            shortcuts_text = f"""Keyboard Shortcuts:

• {shortcuts['cmd']}, - Open Settings
• {shortcuts['cmd']}K - Clear All
• {shortcuts['cmd']}W - Close Window
• {shortcuts['cmd']}Q - Quit Application
• {shortcuts['cmd']}{shortcuts['question']} - Show Help
• {shortcuts['cmd']}{shortcuts['enter']} - Process Text
• {shortcuts['cmd']}{shortcuts['shift']}K - Clear Text Input
• {shortcuts['enter']} - Process Text"""
        else:  # Windows/Linux
            shortcuts_text = f"""Keyboard Shortcuts:

• {shortcuts['cmd']}+, - Open Settings
• {shortcuts['cmd']}+K - Clear All
• {shortcuts['cmd']}+W - Close Window
• {shortcuts['cmd']}+Q - Quit Application
• {shortcuts['cmd']}+{shortcuts['question']} - Show Help
• {shortcuts['cmd']}+{shortcuts['enter']} - Process Text
• {shortcuts['cmd']}+{shortcuts['shift']}+K - Clear Text Input
• {shortcuts['enter']} - Process Text"""
        
        messagebox.showinfo(
            "HelpMeSign Help",
            f"HelpMeSign - Sign Language Application\n\n"
            f"How to use:\n\n"
            f"1. Choose your mode:\n"
            f"   • Sign & Translate: Convert text to sign language\n"
            f"   • Learn Sign Language: Learn symbols and words\n\n"
            f"2. Use the text input to enter words or phrases\n\n"
            f"3. View the sign language translations or learning content\n\n"
            f"4. Change modes anytime via Settings menu\n\n"
            f"{shortcuts_text}"
        )
    
    def set_title(self, title: str) -> None:
        """Set the window title"""
        self.root.title(title)
    
    def bind_close_event(self, callback: Callable) -> None:
        """Bind window close event to callback"""
        self.root.protocol("WM_DELETE_WINDOW", callback)
    
    def bind_shortcuts(self) -> None:
        """Bind keyboard shortcuts for the application"""
        # Settings shortcut (Cmd+,)
        self.root.bind('<Command-comma>', lambda e: self.show_settings())
        self.root.bind('<Control-comma>', lambda e: self.show_settings())  # Windows/Linux
        
        # Quit shortcut (Cmd+Q)
        self.root.bind('<Command-q>', lambda e: self.root.quit())
        self.root.bind('<Control-q>', lambda e: self.root.quit())  # Windows/Linux
        
        # Clear All shortcut (Cmd+K)
        self.root.bind('<Command-k>', lambda e: self.clear_all())
        self.root.bind('<Control-k>', lambda e: self.clear_all())  # Windows/Linux
        
        # Close Window shortcut (Cmd+W)
        self.root.bind('<Command-w>', lambda e: self.root.withdraw())
        self.root.bind('<Control-w>', lambda e: self.root.withdraw())  # Windows/Linux
        
        # Help shortcut (Cmd+?)
        self.root.bind('<Command-question>', lambda e: self.show_help())
        self.root.bind('<F1>', lambda e: self.show_help())  # Alternative for Windows/Linux 