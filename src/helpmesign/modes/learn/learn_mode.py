"""
Learn Sign Language mode implementation
Provides character selection and sign display layout
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout
    from PySide6.QtGui import QFont

from ...utils.language_manager import get_text
from ..base_mode import BaseMode


class LearnMode(BaseMode):
    """Learn Sign Language mode - character selection and sign display"""

    def __init__(self, main_window, environment: str = "dev"):
        # Initialize font attributes before calling parent __init__
        # Get current font size and family once and store them
        from src.helpmesign.utils.theme_manager import get_font_family, get_font_size

        self.current_font_size = get_font_size()
        self.current_font_family = get_font_family()

        # Initialize character tracking variables
        self.current_character: Optional[str] = None
        self.current_char_type: Optional[str] = None

        # Initialize learning progress tracking
        self.learning_progress: Dict[str, Dict[str, Any]] = {}
        self.lesson_history: List[Dict[str, Any]] = []
        self.current_lesson: Optional[Dict[str, Any]] = None

        # Now call parent __init__ which will call setup_ui()
        super().__init__(main_window, environment)

    def get_mode_name(self) -> str:
        """Get the display name for this mode"""
        return get_text("modes.learn.name")

    def get_mode_description(self) -> str:
        """Get a description of what this mode does"""
        return get_text("modes.learn.description")

    def setup_ui(self) -> None:
        """Set up the mode-specific UI components"""
        # Skip UI creation in test environments or when main_window is a mock
        if hasattr(self.main_window, "_is_mock") or not hasattr(
            self.main_window, "content_area"
        ):
            return

        # Create a custom layout for learning mode
        self.create_learning_layout()

    def create_learning_layout(self) -> None:
        """Create the learning mode layout with alphabet selection and sign display"""
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFont
        from PySide6.QtWidgets import (
            QButtonGroup,
            QFrame,
            QGridLayout,
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QPushButton,
            QRadioButton,
            QVBoxLayout,
            QWidget,
        )

        # Create main learning widget
        self.learning_widget = QWidget()

        # Main horizontal layout
        main_layout = QHBoxLayout(self.learning_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Left panel - Sign display
        left_panel = self.create_sign_display_panel()
        left_panel.setFixedWidth(400)
        main_layout.addWidget(left_panel, 2)  # 2 parts width

        # Right panel - Alphabet/Number selection
        right_panel = self.create_selection_panel()
        right_panel.setFixedWidth(700)
        main_layout.addWidget(right_panel, 1)  # 1 part width

        # Store references for later use
        self.left_panel = left_panel
        self.right_panel = right_panel

    def create_selection_panel(self):
        """Create the left panel for alphabet/number selection"""
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFont
        from PySide6.QtWidgets import (
            QFrame,
            QGridLayout,
            QLabel,
            QPushButton,
            QVBoxLayout,
        )

        # Create panel frame
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.Box)
        panel.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 15px;
            }
        """
        )

        layout = QVBoxLayout(panel)
        layout.setSpacing(25)  # More spacing between title and grid

        # Title
        self.selection_title = QLabel("Select Character")
        self.selection_title.setFont(
            QFont(self.current_font_family, self.current_font_size, QFont.Weight.Bold)
        )
        self.selection_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selection_title.setFixedSize(300, 40)  # Fixed size prevents panel resizing
        layout.addWidget(self.selection_title)

        # Fixed grid layout with absolute spacing to prevent layout shifts
        combined_layout = QGridLayout()
        combined_layout.setSpacing(16)  # Fixed spacing between buttons
        combined_layout.setContentsMargins(16, 16, 16, 16)  # Fixed margins
        combined_layout.setRowStretch(0, 0)  # Prevent row stretching
        combined_layout.setColumnStretch(0, 0)  # Prevent column stretching

        # Create all buttons in a single dictionary
        self.alphabet_buttons = {}
        self.number_buttons = {}

        # ASL characters - English alphabet and numbers
        all_characters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + list("0123456789")

        # Improved layout: 6 columns, 48px buttons, better spacing
        max_columns = 6
        button_size = 48

        row, col = 0, 0
        for char in all_characters:
            btn = QPushButton(char)
            btn.setFixedSize(button_size, button_size)
            btn.setMinimumSize(button_size, button_size)
            btn.setMaximumSize(button_size, button_size)
            btn.setFont(
                QFont(
                    self.current_font_family, self.current_font_size, QFont.Weight.Bold
                )
            )
            btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #007bff;
                    border: 1px solid #0056b3;
                    border-radius: 6px;
                    color: white;
                    font-weight: bold;
                }
                QPushButton[selected="true"] {
                    background-color: #0056b3;
                    border: 1px solid #0056b3;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                    border-color: #004085;
                }
                QPushButton:pressed {
                    background-color: #004085;
                }
            """
            )

            # Connect to appropriate handler based on character type
            if char.isalpha():
                btn.clicked.connect(
                    lambda checked, c=char: self.on_alphabet_selected(c)
                )
                self.alphabet_buttons[char] = btn
            else:
                btn.clicked.connect(lambda checked, c=char: self.on_number_selected(c))
                self.number_buttons[char] = btn

            combined_layout.addWidget(btn, row, col)

            col += 1
            if col >= max_columns:
                col = 0
                row += 1

        # Add the grid layout to the main layout with no stretching
        layout.addLayout(combined_layout)
        layout.addStretch(1)  # Add stretch to prevent grid from expanding

        return panel

    def create_sign_display_panel(self):
        """Create the right panel for sign display"""
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFont
        from PySide6.QtWidgets import (
            QButtonGroup,
            QFrame,
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QPushButton,
            QRadioButton,
            QVBoxLayout,
        )

        # Create panel frame
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.Box)
        panel.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 15px;
            }
        """
        )

        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        # Title
        self.sign_title = QLabel("Select a letter or number")
        self.sign_title.setFont(
            QFont(self.current_font_family, self.current_font_size, QFont.Weight.Bold)
        )
        self.sign_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sign_title.setFixedSize(300, 40)  # Fixed size prevents panel resizing
        layout.addWidget(self.sign_title)

        # Sign display area
        self.sign_display_label = QLabel()
        self.sign_display_label.setMinimumSize(300, 300)
        self.sign_display_label.setStyleSheet(
            """
            QLabel {
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 10px;
                color: #6c757d;
            }
        """
        )
        self.sign_display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sign_display_label.setText("Sign will appear here")
        layout.addWidget(self.sign_display_label)

        # Hand preference section
        hand_group = QGroupBox("Hand Preference")
        hand_group.setFont(
            QFont(
                self.current_font_family, self.current_font_size - 2, QFont.Weight.Bold
            )
        )
        hand_layout = QHBoxLayout(hand_group)

        self.hand_button_group = QButtonGroup()

        self.right_hand_radio = QRadioButton("Right Hand")
        self.right_hand_radio.setChecked(True)
        self.right_hand_radio.toggled.connect(self.on_hand_preference_changed)
        self.hand_button_group.addButton(self.right_hand_radio)
        hand_layout.addWidget(self.right_hand_radio)

        self.left_hand_radio = QRadioButton("Left Hand")
        self.left_hand_radio.toggled.connect(self.on_hand_preference_changed)
        self.hand_button_group.addButton(self.left_hand_radio)
        hand_layout.addWidget(self.left_hand_radio)

        layout.addWidget(hand_group)

        # Description area
        self.sign_description = QLabel(
            "Choose a letter or number from the left panel to see its sign language representation."
        )
        self.sign_description.setWordWrap(True)
        self.sign_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sign_description.setFixedSize(
            300, 80
        )  # Fixed size prevents panel resizing
        self.sign_description.setStyleSheet(
            """
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
                color: #495057;
            }
        """
        )
        layout.addWidget(self.sign_description)

        return panel

    def on_alphabet_selected(self, letter: str) -> None:
        """Handle alphabet letter selection"""
        # Update button styling
        self.update_button_selection(letter, self.alphabet_buttons)

        # Update sign display
        self.update_sign_display(letter, "letter")

        # Update title
        self.sign_title.setText(f"Sign for '{letter}'")

    def on_number_selected(self, number: str) -> None:
        """Handle number selection"""
        # Update button styling
        self.update_button_selection(number, self.number_buttons)

        # Update sign display
        self.update_sign_display(number, "number")

        # Update title
        self.sign_title.setText(f"Sign for '{number}'")

    def update_button_selection(self, selected: str, button_dict: dict) -> None:
        """Update button styling to show selection using property, not stylesheet"""
        # Reset ALL buttons (both alphabet and number) to unselected
        for btn in self.alphabet_buttons.values():
            btn.setProperty("selected", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        for btn in self.number_buttons.values():
            btn.setProperty("selected", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        # Highlight selected button
        if selected in button_dict:
            button_dict[selected].setProperty("selected", True)
            button_dict[selected].style().unpolish(button_dict[selected])
            button_dict[selected].style().polish(button_dict[selected])

    def update_sign_display(self, character: str, char_type: str) -> None:
        """Update the sign display area"""
        # Safety check - ensure sign display label exists
        if not hasattr(self, "sign_display_label") or self.sign_display_label is None:
            return

        # Store current character and type for hand preference changes
        self.current_character = character
        self.current_char_type = char_type

        hand_preference = "right" if self.right_hand_radio.isChecked() else "left"

        # Simple placeholder text
        sign_info = f"ASL sign for {char_type} '{character}' ({hand_preference} hand)"

        # Update display
        self.sign_display_label.setText(
            f"ASL Sign for '{character}'\n({hand_preference} hand)"
        )
        self.sign_description.setText(sign_info)

    def on_hand_preference_changed(self) -> None:
        """Handle hand preference change"""
        # Update the current sign display with new hand preference
        if (
            hasattr(self, "current_character")
            and hasattr(self, "current_char_type")
            and self.current_character is not None
            and self.current_char_type is not None
        ):
            self.update_sign_display(self.current_character, self.current_char_type)

    def setup_behavior(self) -> None:
        """Set up mode-specific behavior and event handlers"""
        # Connect hand preference radio buttons to their handler
        if hasattr(self, "right_hand_radio") and hasattr(self, "left_hand_radio"):
            self.right_hand_radio.toggled.connect(self.on_hand_preference_changed)
            self.left_hand_radio.toggled.connect(self.on_hand_preference_changed)

        # Connect to main window signals if they exist
        if hasattr(self.main_window, "clear_requested"):
            self.main_window.clear_requested.connect(self._on_clear_requested)

        if hasattr(self.main_window, "process_requested"):
            self.main_window.process_requested.connect(self._on_learn_requested)

    def process_text(self, text: str) -> str:
        """Process input text according to mode-specific logic"""
        if not text.strip():
            return get_text("ui.output.empty_message")

        # Convert text to sign language for learning
        result = self.get_sign_language_info(text)

        # Track learning progress
        self._update_learning_progress(text)

        return result

    def get_sign_language_info(self, text: str) -> str:
        """Get detailed sign language information for a word or phrase"""
        text_lower = text.lower().strip()
        words = text_lower.split()

        if len(words) == 1:
            # Single word processing
            word = words[0]
            return self._get_single_word_info(word)
        else:
            # Multiple words - process each word
            results = []
            for word in words:
                word_info = self._get_single_word_info(word)
                results.append(word_info)
            return "\n\n".join(results)

    def _get_single_word_info(self, word: str) -> str:
        """Get sign language information for a single word"""
        # Basic sign language conversion with detailed information
        if word in ["hello", "hi"]:
            return "👋 HELLO/HI:\n• Hand gesture: Wave your hand\n• Cultural note: Universal greeting\n• Tip: Make eye contact while signing"
        elif word in ["thank", "thanks", "thank_you"]:
            return "🙏 THANK YOU:\n• Hand gesture: Hand to chin, then forward\n• Cultural note: Shows respect and gratitude\n• Tip: Use facial expression to convey sincerity"
        elif word == "yes":
            return "👍 YES:\n• Hand gesture: Nod head and make a fist\n• Cultural note: Affirmative response\n• Tip: Combine with head nod for emphasis"
        elif word == "no":
            return "👎 NO:\n• Hand gesture: Shake head and point index finger\n• Cultural note: Negative response\n• Tip: Use clear facial expression"
        elif word == "please":
            return "🤲 PLEASE:\n• Hand gesture: Flat hand, palm up, circular motion\n• Cultural note: Polite request\n• Tip: Make the motion smooth and gentle"
        elif word == "sorry":
            return "🤝 SORRY:\n• Hand gesture: Fist over heart, circular motion\n• Cultural note: Apology gesture\n• Tip: Show genuine remorse in expression"
        else:
            # For unknown words, spell them out
            spelled_word = " ".join(word.upper())
            return f"🤟 SPELLING: {spelled_word}\n• Use finger spelling for this word\n• Each letter has a specific hand position\n• Practice spelling slowly and clearly"

    def _update_learning_progress(self, text: str) -> None:
        """Update learning progress for a word or phrase"""
        text_lower = text.lower().strip()

        # For very long text, track the entire text as one entry
        if len(text_lower) > 1000:
            if text_lower not in self.learning_progress:
                self.learning_progress[text_lower] = {"searched_count": 0}
            self.learning_progress[text_lower]["searched_count"] += 1
        else:
            # For normal text, track individual words only
            words = text_lower.split()
            for word in words:
                if word not in self.learning_progress:
                    self.learning_progress[word] = {"searched_count": 0}
                self.learning_progress[word]["searched_count"] += 1

        # Limit progress tracking to prevent memory issues
        if len(self.learning_progress) > 100:
            # Remove oldest entries
            oldest_key = next(iter(self.learning_progress))
            del self.learning_progress[oldest_key]

    def _on_learn_requested(self) -> None:
        """Handle learn button click in learning mode"""
        try:
            input_text = self.main_window.get_text_input()
            if input_text and input_text.strip():
                output_text = self.process_text(input_text)
                self.main_window.set_text_output(output_text)

                # Update status
                status_message = f"Learned sign for: {input_text}"
                self.main_window.set_status(status_message)
            else:
                self.main_window.set_text_output("")
                self.main_window.set_status("Please enter text to learn")
        except Exception as e:
            self.main_window.set_text_output("")
            self.main_window.set_status("Error occurred")

    def _on_clear_requested(self) -> None:
        """Handle clear button click in learning mode"""
        # Clear text input if main window has the method
        if hasattr(self.main_window, "set_text_input"):
            self.main_window.set_text_input("")

        # Clear text output if main window has the method
        if hasattr(self.main_window, "set_text_output"):
            self.main_window.set_text_output("")

        # Update status if main window has the method
        if hasattr(self.main_window, "set_status"):
            self.main_window.set_status("Content cleared")

        # Reset the sign display to default state
        if hasattr(self, "sign_display_label"):
            self.sign_display_label.setText("Sign will appear here")

        if hasattr(self, "sign_title"):
            self.sign_title.setText("Select a letter or number")

        if hasattr(self, "sign_description"):
            self.sign_description.setText(
                "Choose a letter or number from the left panel to see its sign language representation."
            )

        # Clear any button selections
        if hasattr(self, "alphabet_buttons"):
            self.update_button_selection("", self.alphabet_buttons)
        if hasattr(self, "number_buttons"):
            self.update_button_selection("", self.number_buttons)

    def update_ui(self) -> None:
        """Update the UI to reflect the current mode"""
        # Update fonts to match current font size setting
        self.update_fonts()

    def update_fonts(self) -> None:
        """Update fonts following the defined process:
        Only update fonts in currently visible window, never update button fonts
        """
        from src.helpmesign.utils.theme_manager import get_font_family, get_font_size

        try:
            # Only update fonts if this mode is currently visible
            if (
                not hasattr(self, "learning_widget")
                or not self.learning_widget.isVisible()
            ):
                return

            # Update stored font size and family
            self.current_font_size = get_font_size()
            self.current_font_family = get_font_family()

            # Update title fonts - consistent with other modes
            if hasattr(self, "sign_title"):
                self.sign_title.setFont(
                    QFont(
                        self.current_font_family,
                        self.current_font_size,
                        QFont.Weight.Bold,
                    )
                )

            if hasattr(self, "selection_title"):
                self.selection_title.setFont(
                    QFont(
                        self.current_font_family,
                        self.current_font_size,
                        QFont.Weight.Bold,
                    )
                )

            # CRITICAL: DO NOT update button fonts at all - this causes layout shifts
            # The buttons are created with fixed size and font, and must remain unchanged
            # Any font updates will cause Qt to recalculate sizes and break the layout

            # Update hand preference group font - smaller for UI elements
            if hasattr(self, "hand_button_group"):
                for btn in self.hand_button_group.buttons():
                    btn.setFont(
                        QFont(
                            self.current_font_family,
                            self.current_font_size - 2,
                            QFont.Weight.Normal,
                        )
                    )

            # Update description text font
            if hasattr(self, "sign_description"):
                self.sign_description.setFont(
                    QFont(
                        self.current_font_family,
                        self.current_font_size - 3,
                        QFont.Weight.Normal,
                    )
                )

        except Exception as e:
            # Fallback to default font sizes if theme manager is not available
            pass

    def clear_content(self) -> None:
        """Clear all content in this mode"""
        # Clear text input if main window has the method
        if hasattr(self.main_window, "set_text_input"):
            self.main_window.set_text_input("")

        # Clear text output if main window has the method
        if hasattr(self.main_window, "set_text_output"):
            self.main_window.set_text_output("")

        # Reset the sign display to default state
        if hasattr(self, "sign_display_label"):
            self.sign_display_label.setText("Sign will appear here")

        if hasattr(self, "sign_title"):
            self.sign_title.setText("Select a letter or number")

        if hasattr(self, "sign_description"):
            self.sign_description.setText(
                "Choose a letter or number from the left panel to see its sign language representation."
            )

        # Clear any button selections
        if hasattr(self, "alphabet_buttons"):
            self.update_button_selection("", self.alphabet_buttons)
        if hasattr(self, "number_buttons"):
            self.update_button_selection("", self.number_buttons)

        # Reset current character tracking
        if hasattr(self, "current_character"):
            self.current_character = None
        if hasattr(self, "current_char_type"):
            self.current_char_type = None

    def get_settings(self) -> Dict[str, Any]:
        """Get mode-specific settings"""
        return {
            "mode": "learn",
            "learning_progress_count": len(self.learning_progress),
            "lesson_history_count": len(self.lesson_history),
            "current_lesson": self.current_lesson is not None,
        }

    def get_learning_progress(self) -> Dict[str, Dict[str, Any]]:
        """Get a copy of the learning progress"""
        return self.learning_progress.copy()

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
            if word not in self.learning_progress:
                suggestions.append(f"Learn '{word}' - Basic greeting/response")

        # Suggest words that have been learned less than 3 times
        for word, progress in self.learning_progress.items():
            if progress.get("searched_count", 0) < 3:
                suggestions.append(f"Practice '{word}' - Review needed")

        return suggestions[:5]  # Limit to 5 suggestions

    def activate(self) -> None:
        """Activate this mode - called when switching to this mode"""
        # Skip UI operations if in test mode or missing UI elements
        if hasattr(self.main_window, "_is_mock") or not hasattr(
            self, "learning_widget"
        ):
            self.main_window.set_mode(self.mode_name)
            return

        # Add the learning widget to the content area if not already present
        if self.main_window.content_area.indexOf(self.learning_widget) == -1:
            self.main_window.content_area.addWidget(self.learning_widget)

        # Switch to learning content
        self.main_window.content_area.setCurrentWidget(self.learning_widget)

        # Update UI for learning mode
        self.update_ui()

        self.main_window.set_mode(self.mode_name)

        # Force a layout update after a short delay to ensure all font updates are complete
        from PySide6.QtCore import QTimer

        QTimer.singleShot(100, self._force_layout_stability)

    def deactivate(self) -> None:
        """Deactivate this mode - called when switching away from this mode"""
        # Switch back to default content
        self.main_window.content_area.setCurrentWidget(self.main_window.default_content)

    def _force_layout_stability(self) -> None:
        """Force the layout to remain stable after all font updates are complete"""
        try:
            # Re-apply fixed sizes to all buttons to ensure they stay the correct size
            if hasattr(self, "alphabet_buttons"):
                for btn in self.alphabet_buttons.values():
                    btn.setFixedSize(48, 48)
                    btn.setMinimumSize(48, 48)
                    btn.setMaximumSize(48, 48)

            if hasattr(self, "number_buttons"):
                for btn in self.number_buttons.values():
                    btn.setFixedSize(48, 48)
                    btn.setMinimumSize(48, 48)
                    btn.setMaximumSize(48, 48)

            # Force the layout to update
            if hasattr(self, "learning_widget"):
                self.learning_widget.updateGeometry()
                self.learning_widget.update()
        except Exception as e:
            # Silently ignore any errors
            pass
