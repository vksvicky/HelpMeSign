"""
Learning Progress for Learn Mode
Contains learning progress tracking methods extracted from learn_mode.py
"""

from typing import Any, Dict, List


class LearnModeLearningProgress:
    """Learning progress tracking methods for Learn Mode"""

    def __init__(self, learn_mode):
        self.learn_mode = learn_mode
        self.logger = learn_mode.logger

    def _update_learning_progress(self, text: str) -> None:
        """Update learning progress for a word or phrase"""
        text_lower = text.lower().strip()

        # For very long text, track the entire text as one entry
        if len(text_lower) > 1000:
            if text_lower not in self.learn_mode.learning_progress:
                self.learn_mode.learning_progress[text_lower] = {"searched_count": 0}
            self.learn_mode.learning_progress[text_lower]["searched_count"] += 1
        else:
            # For normal text, track individual words only
            words = text_lower.split()
            for word in words:
                if word not in self.learn_mode.learning_progress:
                    self.learn_mode.learning_progress[word] = {"searched_count": 0}
                self.learn_mode.learning_progress[word]["searched_count"] += 1

        # Limit progress tracking to prevent memory issues
        if len(self.learn_mode.learning_progress) > 100:
            # Remove oldest entries
            oldest_key = next(iter(self.learn_mode.learning_progress))
            del self.learn_mode.learning_progress[oldest_key]

    def _on_learn_requested(self) -> None:
        """Handle learn button click in learning mode"""
        try:
            input_text = self.learn_mode.main_window.get_text_input()
            if input_text and input_text.strip():
                output_text = self.learn_mode.process_text(input_text)
                self.learn_mode.main_window.set_text_output(output_text)

                # Update status
                status_message = f"Learned sign for: {input_text}"
                self.learn_mode.main_window.set_status(status_message)
            else:
                self.learn_mode.main_window.set_text_output("")
                self.learn_mode.main_window.set_status("Please enter text to learn")
        except Exception as e:
            self.learn_mode.main_window.set_text_output("")
            self.learn_mode.main_window.set_status("Error occurred")

    def _on_clear_requested(self) -> None:
        """Handle clear button click in learning mode"""
        # Call the main clear_content method to avoid duplication
        self.learn_mode.clear_content()

    def get_settings(self) -> Dict[str, Any]:
        """Get mode-specific settings"""
        return {
            "mode": "learn",
            "learning_progress_count": len(self.learn_mode.learning_progress),
            "lesson_history_count": len(self.learn_mode.lesson_history),
            "current_lesson": self.learn_mode.current_lesson is not None,
        }

    def get_learning_progress(self) -> Dict[str, Dict[str, Any]]:
        """Get a copy of the learning progress"""
        return self.learn_mode.learning_progress.copy()

    def get_lesson_suggestions(self) -> List[str]:
        """Get lesson suggestions based on learning progress"""
        suggestions = []

        # Add basic lesson categories
        suggestions.append("Basic Greetings")
        suggestions.append("Common Phrases")
        suggestions.append("Numbers")
        suggestions.append("Colors")

        # Suggest common words that haven't been learned yet
        common_words = ["hello", "thanks", "yes", "no", "please", "sorry"]
        for word in common_words:
            if word not in self.learn_mode.learning_progress:
                suggestions.append(f"Learn '{word}' - Basic greeting/response")

        # Suggest words that have been learned less than 3 times
        for word, progress in self.learn_mode.learning_progress.items():
            if progress.get("searched_count", 0) < 3:
                suggestions.append(f"Practice '{word}' - Review needed")

        return suggestions[:5]  # Limit to 5 suggestions
