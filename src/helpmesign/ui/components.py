import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Any


class TextInputFrame(ttk.Frame):
    """Frame containing text input and processing controls"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the text input UI components"""
        # Input label and field
        ttk.Label(self, text="Enter text:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.text_input = ttk.Entry(self, width=50)
        self.text_input.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.process_button = ttk.Button(button_frame, text="Process")
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear")
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


class OutputFrame(ttk.Frame):
    """Frame containing output display area"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the output UI components"""
        # Output label
        ttk.Label(self, text="Output:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Text widget for output
        self.output_text = tk.Text(self, height=20, width=60, wrap=tk.WORD)
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
            anchor=tk.W
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
        
        # Set up main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # Create title
        title_label = ttk.Label(self.main_frame, text=title, font=("Arial", 24, "bold"))
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
    
    def bind_close_event(self, callback: Callable) -> None:
        """Bind window close event to callback"""
        self.root.protocol("WM_DELETE_WINDOW", callback) 