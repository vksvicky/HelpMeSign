"""
Learn Sign Language mode implementation
Provides educational content and learning tools for sign language
"""

from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout

from ...utils.language_manager import get_text
from ..base_mode import BaseMode


class LearnMode(BaseMode):
    """Learn Sign Language mode - educational content and learning tools"""

    def __init__(self, main_window, environment: str = "dev"):
        super().__init__(main_window, environment)
        self.learning_progress: Dict[str, Dict[str, Any]] = {}
        self.lesson_history: List[Dict[str, Any]] = []
        self.current_lesson = None

    def get_mode_name(self) -> str:
        """Get the display name for this mode"""
        return get_text("modes.learn.name")

    def get_mode_description(self) -> str:
        """Get a description of what this mode does"""
        return get_text("modes.learn.description")

    def setup_ui(self) -> None:
        """Set up the mode-specific UI components"""
        # This mode will have additional UI components for learning
        # For now, it uses the existing main window UI
        pass

    def setup_behavior(self) -> None:
        """Set up mode-specific behavior and event handlers"""
        # Connect to main window signals for learning functionality
        if hasattr(self.main_window, "process_requested"):
            self.main_window.process_requested.connect(self._on_learn_requested)

        if hasattr(self.main_window, "clear_requested"):
            self.main_window.clear_requested.connect(self._on_clear_requested)

    def process_text(self, text: str) -> str:
        """Process input text and provide learning information"""
        if not text.strip():
            return get_text("ui.output.empty_message")

        # Provide educational content about the input text
        output = self.get_sign_language_info(text)

        # Track learning progress
        self.learning_progress[text.lower()] = {
            "searched_count": self.learning_progress.get(text.lower(), {}).get(
                "searched_count", 0
            )
            + 1,
            "last_searched": "now",  # Could use actual timestamp
        }

        return output

    def get_sign_language_info(self, text: str) -> str:
        """Get educational information about sign language for the given text"""
        words = text.lower().split()
        educational_content = []

        for word in words:
            # Provide educational content for each word
            if word in ["hello", "hi"]:
                educational_content.append(
                    "👋 HELLO/HI:\n"
                    "• Hand gesture: Wave your hand\n"
                    "• Cultural note: This is one of the most universal signs\n"
                    "• Tip: Make eye contact while signing"
                )
            elif word in ["thank", "thanks", "thank_you"]:
                educational_content.append(
                    "🙏 THANK YOU:\n"
                    "• Hand gesture: Hand to chin, then forward\n"
                    "• Cultural note: Shows respect and gratitude\n"
                    "• Tip: The movement should be smooth and deliberate"
                )
            elif word == "yes":
                educational_content.append(
                    "👍 YES:\n"
                    "• Hand gesture: Nod head and make a fist\n"
                    "• Cultural note: Combines facial expression with hand gesture\n"
                    "• Tip: The head nod is as important as the hand gesture"
                )
            elif word == "no":
                educational_content.append(
                    "👎 NO:\n"
                    "• Hand gesture: Shake head and point index finger\n"
                    "• Cultural note: Clear and direct communication\n"
                    "• Tip: Facial expression should match the meaning"
                )
            elif word == "please":
                educational_content.append(
                    "🤲 PLEASE:\n"
                    "• Hand gesture: Flat hand, palm up, circular motion\n"
                    "• Cultural note: Shows politeness and request\n"
                    "• Tip: The circular motion should be gentle"
                )
            elif word == "sorry":
                educational_content.append(
                    "🤝 SORRY:\n"
                    "• Hand gesture: Fist over heart, circular motion\n"
                    "• Cultural note: Shows genuine apology and remorse\n"
                    "• Tip: The heart placement emphasizes sincerity"
                )
            else:
                # For unknown words, provide spelling information
                spelled_word = " ".join(word.upper())
                educational_content.append(
                    f"🤟 SPELLING: {spelled_word}\n"
                    "• Use finger spelling for this word\n"
                    "• Each letter has a specific hand position\n"
                    "• Practice spelling slowly and clearly"
                )

        return "\n\n".join(educational_content)

    def _on_learn_requested(self) -> None:
        """Handle learn button click"""
        try:
            input_text = self.main_window.get_text_input()
            output_text = self.process_text(input_text)
            self.main_window.set_text_output(output_text)

            # Update status
            status_message = f"{get_text('ui.status.learning_prefix')}{input_text}{get_text('ui.status.learning_suffix')}"
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
        # Update input placeholder text for learning mode
        if hasattr(self.main_window, "text_input_frame"):
            if hasattr(self.main_window.text_input_frame, "text_input"):
                self.main_window.text_input_frame.text_input.setPlaceholderText(
                    "Enter a word to learn its sign language..."
                )

    def clear_content(self) -> None:
        """Clear all content in this mode"""
        self.main_window.set_text_input("")
        self.main_window.set_text_output("")
        # Don't clear learning progress - that should persist

    def get_settings(self) -> Dict[str, Any]:
        """Get mode-specific settings"""
        return {
            "learning_progress_count": len(self.learning_progress),
            "lesson_history_count": len(self.lesson_history),
            "mode": "learn",
        }

    def apply_settings(self, settings: Dict[str, Any]) -> None:
        """Apply mode-specific settings"""
        # Could implement settings like:
        # - Learning difficulty level
        # - Preferred learning style (visual, text, etc.)
        # - Progress tracking preferences
        pass

    def get_learning_progress(self) -> Dict[str, Any]:
        """Get current learning progress"""
        return self.learning_progress.copy()

    def get_lesson_suggestions(self) -> List[str]:
        """Get suggested lessons based on learning progress"""
        # Could implement AI-based suggestions
        return ["Basic Greetings", "Common Phrases", "Numbers", "Colors"]
