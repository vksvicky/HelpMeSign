"""
Sign & Translate mode implementation
Converts text input to sign language representations
"""

from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QVBoxLayout, QWidget

from ..base_mode import BaseMode
from ...utils.language_manager import get_text


class SignTranslateMode(BaseMode):
    """Sign & Translate mode - converts text to sign language"""

    def __init__(self, main_window, environment: str = "dev"):
        super().__init__(main_window, environment)
        self.conversion_history = []

    def get_mode_name(self) -> str:
        """Get the display name for this mode"""
        return get_text("modes.sign_translate.name")

    def get_mode_description(self) -> str:
        """Get a description of what this mode does"""
        return get_text("modes.sign_translate.description")

    def setup_ui(self) -> None:
        """Set up the mode-specific UI components"""
        # This mode uses the existing main window UI components
        # No additional UI setup needed for now
        pass

    def setup_behavior(self) -> None:
        """Set up mode-specific behavior and event handlers"""
        # Connect to main window signals for text processing
        if hasattr(self.main_window, "process_requested"):
            self.main_window.process_requested.connect(self._on_process_requested)
        
        if hasattr(self.main_window, "clear_requested"):
            self.main_window.clear_requested.connect(self._on_clear_requested)

    def process_text(self, text: str) -> str:
        """Process input text and convert to sign language"""
        if not text.strip():
            return get_text("ui.output.empty_message")

        # Convert text to sign language representation
        output = self.convert_to_sign_language(text)
        
        # Add to conversion history
        self.conversion_history.append({
            "input": text,
            "output": output,
            "timestamp": "now"  # Could use actual timestamp
        })
        
        return output

    def convert_to_sign_language(self, text: str) -> str:
        """Convert text to sign language representation"""
        # This is the existing conversion logic from the main app
        words = text.lower().split()
        sign_language_words = []

        for word in words:
            # Basic sign language conversion
            if word in ["hello", "hi"]:
                sign_language_words.append("👋 Wave hand")
            elif word in ["thank", "thanks", "thank_you"]:
                sign_language_words.append("🙏 Hand to chin, then forward")
            elif word == "yes":
                sign_language_words.append("👍 Nod head and fist")
            elif word == "no":
                sign_language_words.append("👎 Shake head and index finger")
            elif word == "please":
                sign_language_words.append("🤲 Flat hand, palm up, circular motion")
            elif word == "sorry":
                sign_language_words.append("🤝 Fist over heart, circular motion")
            else:
                # For unknown words, spell them out
                spelled_word = " ".join(word)
                sign_language_words.append(f"🤟 Spell: {spelled_word}")

        return " | ".join(sign_language_words)

    def _on_process_requested(self) -> None:
        """Handle process button click"""
        try:
            input_text = self.main_window.get_text_input()
            output_text = self.process_text(input_text)
            self.main_window.set_text_output(output_text)
            
            # Update status
            status_message = f"{get_text('ui.status.converted_prefix')}{input_text}{get_text('ui.status.converted_suffix')}"
            self.main_window.set_status(status_message)
            
        except Exception as e:
            error_message = f"{get_text('ui.status.error_prefix')}{e}"
            self.main_window.set_text_output(error_message)
            self.main_window.set_status("Error occurred")

    def _on_clear_requested(self) -> None:
        """Handle clear button click"""
        self.main_window.set_text_input("")
        self.main_window.set_text_output("")
        self.main_window.set_status(get_text("ui.status.cleared"))

    def update_ui(self) -> None:
        """Update the UI to reflect the current mode"""
        # Update input placeholder text
        if hasattr(self.main_window, "text_input_frame"):
            if hasattr(self.main_window.text_input_frame, "text_input"):
                self.main_window.text_input_frame.text_input.setPlaceholderText(
                    get_text("ui.text_input.placeholder")
                )

    def clear_content(self) -> None:
        """Clear all content in this mode"""
        self.main_window.set_text_input("")
        self.main_window.set_text_output("")
        self.conversion_history.clear()

    def get_settings(self) -> Dict[str, Any]:
        """Get mode-specific settings"""
        return {
            "conversion_history_count": len(self.conversion_history),
            "mode": "sign_translate"
        }

    def apply_settings(self, settings: Dict[str, Any]) -> None:
        """Apply mode-specific settings"""
        # Could implement settings like:
        # - Conversion history limit
        # - Preferred sign language dialect
        # - Output format preferences
        pass 