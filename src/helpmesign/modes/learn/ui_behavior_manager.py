"""
UI Behavior Manager for Learn Mode
Handles UI behavior, text processing, and other UI-related functionality
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget, QLabel
    from PySide6.QtCore import QEvent

from ...core.startup import get_theme
from ...utils.language_manager import get_text
from ...utils.sign_language_loader import get_sign_language_loader


class LearnModeUIBehaviorManager:
    """Manages UI behavior and text processing for Learn Mode"""

    # Consistent styling for placeholder text (font-size will be set dynamically)
    PLACEHOLDER_STYLE = (
        "text-align: center; color: #6b7b8c; font-style: italic; padding: 20px;"
    )

    def __init__(self, learn_mode):
        self.learn_mode = learn_mode
        self.sign_loader = get_sign_language_loader()

    def _set_placeholder_text(self) -> None:
        """Set the placeholder text with consistent styling"""
        try:
            if hasattr(self.learn_mode, "sign_instructions_label"):
                placeholder_text = get_text(
                    "ui.language_selection.sign_will_appear_here"
                )
                # Get font size from configuration
                font_size = self.learn_mode.current_font_size
                # Create complete style with dynamic font size
                complete_style = f"{self.PLACEHOLDER_STYLE} font-size: {font_size}px;"
                html_content = f'<div style="{complete_style}">{placeholder_text}</div>'
                self.learn_mode.sign_instructions_label.setText(html_content)
                self.learn_mode.logger.debug(
                    f"Placeholder text set: '{placeholder_text}' with font size: {font_size}px"
                )
        except Exception as e:
            self.learn_mode.logger.error(f"Error setting placeholder text: {e}")

    def update_ui(self) -> None:
        """Update the UI to reflect the current mode"""
        # No updates needed - theme and font are set during initialization
        pass

    def update_fonts(self) -> None:
        """Update fonts - not needed as fonts are set during initialization"""
        # Fonts are set during component creation with stored theme and font information
        pass

    def clear_content(self) -> None:
        """Clear all content in this mode"""
        # Clear text input if main window has the method
        if hasattr(self.learn_mode.main_window, "set_text_input"):
            self.learn_mode.main_window.set_text_input("")

        # Clear text output if main window has the method
        if hasattr(self.learn_mode.main_window, "set_text_output"):
            self.learn_mode.main_window.set_text_output("")

        # Update status using language configuration
        if hasattr(self.learn_mode.main_window, "set_status"):
            self.learn_mode.main_window.set_status(get_text("ui.status.cleared"))

        # Reset the sign display to default state using language configuration
        if hasattr(self.learn_mode, "sign_display_label"):
            self.learn_mode.sign_display_label.setText(
                get_text("ui.language_selection.sign_will_appear_here")
            )

        # Sign description removed for better space utilization

        # Clear any button selections
        if hasattr(self.learn_mode, "alphabet_buttons"):
            self.learn_mode.character_manager.update_button_selection(
                "", self.learn_mode.alphabet_buttons
            )
        if hasattr(self.learn_mode, "number_buttons"):
            self.learn_mode.character_manager.update_button_selection(
                "", self.learn_mode.number_buttons
            )

        # Reset current character tracking
        if hasattr(self.learn_mode, "current_character"):
            self.learn_mode.current_character = None
        if hasattr(self.learn_mode, "current_char_type"):
            self.learn_mode.current_char_type = None

    def process_text(self, text: str) -> str:
        """Process text input and return sign language information"""
        if not text.strip():
            return get_text("ui.output.empty_message")

        # Convert text to sign language for learning
        result = self.get_sign_language_info(text)

        # Track learning progress
        self.learn_mode._update_learning_progress(text)

        return result

    def get_sign_language_info(self, text: str) -> str:
        """Get sign language information for text"""
        try:
            if not text or not text.strip():
                return "Please enter text to get sign language information"

            text_lower = text.lower().strip()
            words = text_lower.split()

            if len(words) == 1:
                return self._get_single_word_info(words[0])
            else:
                # Multiple words - process each word
                results = []
                for word in words:
                    word_info = self._get_single_word_info(word)
                    results.append(word_info)
                return "\n\n".join(results)

        except Exception as e:
            self.learn_mode.logger.error(f"Error getting sign language info: {e}")
            return f"Error: {e}"

    def update_sign_display(self, character: str, char_type: str) -> None:
        """Update the sign display area with actual SVG signs"""
        from PySide6.QtCore import QByteArray

        # Only update state if the UI is ready (tests expect early return when label missing)
        if hasattr(self.learn_mode, "sign_display_label"):
            self.learn_mode.current_character = character
            self.learn_mode.current_char_type = char_type

        # Safety: allow function to proceed even when SVG widget is absent in tests
        svg_widget_available = (
            hasattr(self.learn_mode, "sign_svg_widget")
            and self.learn_mode.sign_svg_widget is not None
        )

        # Get hand preference from local UI state
        hand_preference = getattr(self.learn_mode, "current_hand_preference", "right")

        # Load the sign data from our JSON files
        svg_data = self.sign_loader.get_sign_svg(
            self.learn_mode.current_language, character, hand_preference
        )
        instructions = self.sign_loader.get_sign_instructions(
            self.learn_mode.current_language, character, hand_preference
        )

        # # Update title
        # if hasattr(self.learn_mode, "sign_title") and self.learn_mode.sign_title is not None:
        #     self.learn_mode.sign_title.setText(f"{hand_preference.title()} Hand Sign")

        if svg_data:
            try:
                # QSvgWidget supports loading from QByteArray
                if svg_widget_available and hasattr(
                    self.learn_mode.sign_svg_widget, "load"
                ):
                    self.learn_mode.sign_svg_widget.load(
                        QByteArray(svg_data.encode("utf-8"))
                    )
                else:
                    # Fallback label shows raw SVG text
                    if (
                        hasattr(self.learn_mode, "sign_svg_widget")
                        and self.learn_mode.sign_svg_widget is not None
                    ):
                        self.learn_mode.sign_svg_widget.setText(svg_data)
                # Show the clear button since a sign is now displayed
                if hasattr(self.learn_mode, "clear_sign_btn"):
                    self.learn_mode.clear_sign_btn.setVisible(True)
            except Exception:
                # As a last resort, show raw SVG string
                try:
                    if (
                        hasattr(self.learn_mode, "sign_svg_widget")
                        and self.learn_mode.sign_svg_widget is not None
                    ):
                        self.learn_mode.sign_svg_widget.setText(svg_data)
                except Exception:
                    pass
        else:
            # Clear SVG view on missing data
            try:
                if svg_widget_available and hasattr(
                    self.learn_mode.sign_svg_widget, "load"
                ):
                    self.learn_mode.sign_svg_widget.load(QByteArray())
                else:
                    if (
                        hasattr(self.learn_mode, "sign_svg_widget")
                        and self.learn_mode.sign_svg_widget is not None
                    ):
                        self.learn_mode.sign_svg_widget.setText(
                            get_text("ui.language_selection.sign_will_appear_here")
                        )
            except Exception:
                pass

        # Update instructions text
        if instructions:
            from ...utils.theme_manager import get_font_family

            # Prefer mode's size but enforce a minimum of 16 for readability
            configured_size = getattr(self.learn_mode, "current_font_size", 16)
            try:
                numeric_size = (
                    int(configured_size) if configured_size is not None else 16
                )
            except Exception:
                numeric_size = 16
            current_size = max(numeric_size, 16)
            current_family = get_font_family()
            # Theme-aware text colors for readability
            current_theme = get_theme()
            text_color = "#2c3e50" if current_theme == "Light" else "#e0e6ed"
            meta_color = "#6b7b8c" if current_theme == "Light" else "#a8b2bd"

            if (
                hasattr(self.learn_mode, "sign_instructions_label")
                and self.learn_mode.sign_instructions_label is not None
            ):
                # Apply explicit font on the QLabel to ensure QSS doesn't override size
                try:
                    from PySide6.QtGui import QFont

                    safe_family = str(current_family) if current_family else "Roboto"
                    self.learn_mode.sign_instructions_label.setFont(
                        QFont(safe_family, int(current_size))
                    )
                    # Also apply a direct styleSheet so QSS cannot downscale the font
                    self.learn_mode.sign_instructions_label.setStyleSheet(
                        f"font-family: {safe_family}; font-size: {current_size}px; color: {text_color};"
                    )
                except Exception:
                    pass

                self.learn_mode.sign_instructions_label.setText(
                    f'<div style="font-family: {current_family}; font-size: {current_size}px; color: {text_color};">'
                    f'<p style="margin: 6px 0; text-align: justify; text-justify: inter-word;">{instructions}</p>'
                    f"<div style=\"margin: 4px 0; font-size: 0.9em; color: {meta_color}; text-align: center;\">Character: '{character}'</div>"
                    f"</div>"
                )
        else:
            if (
                hasattr(self.learn_mode, "sign_instructions_label")
                and self.learn_mode.sign_instructions_label is not None
            ):
                self.learn_mode.sign_instructions_label.setText(
                    f'<div style="font-family: {self.learn_mode.current_font_family}; font-size: {self.learn_mode.current_font_size}px; color: #e74c3c;">'
                    f"<h3>Sign Not Found</h3>"
                    f"<p>No sign data available for '{character}' in {self.learn_mode.current_language}</p>"
                    f"</div>"
                )

        # Backward-compatible label update for tests that rely on a text label
        if (
            hasattr(self.learn_mode, "sign_display_label")
            and self.learn_mode.sign_display_label is not None
        ):
            try:
                label_text = instructions or get_text(
                    "ui.language_selection.sign_will_appear_here"
                )
            except Exception:
                label_text = instructions or f"Character: '{character}'"
            try:
                self.learn_mode.sign_display_label.setText(label_text)
            except Exception:
                pass

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

    def eventFilter(self, obj, event):
        """Event filter for handling special events"""
        try:
            if event.type() == QEvent.MouseButtonPress:
                # Handle mouse press events if needed
                pass
            elif event.type() == QEvent.KeyPress:
                # Handle key press events if needed
                pass
        except Exception as e:
            self.learn_mode.logger.error(f"Error in event filter: {e}")

        # Always return False to let the event continue
        return False

    def _show_text_translation_message(self, text: str) -> None:
        """Show a message about text translation"""
        try:
            if hasattr(self.learn_mode.main_window, "set_status"):
                self.learn_mode.main_window.set_status(f"Processing text: {text}")
        except Exception as e:
            self.learn_mode.logger.error(f"Error showing translation message: {e}")

    def _hide_clear_button(self) -> None:
        """Hide the clear button"""
        try:
            if hasattr(self.learn_mode, "clear_button"):
                self.learn_mode.clear_button.setVisible(False)
        except Exception as e:
            self.learn_mode.logger.error(f"Error hiding clear button: {e}")

    def _show_placeholder_message(self) -> None:
        """Show placeholder message"""
        try:
            if hasattr(self.learn_mode, "sign_svg_widget"):
                placeholder_text = get_text(
                    "ui.language_selection.sign_will_appear_here"
                )
                # Handle different widget types appropriately
                if hasattr(self.learn_mode.sign_svg_widget, "setText"):
                    # QLabel or other text widget
                    self.learn_mode.sign_svg_widget.setText(placeholder_text)
                    self.learn_mode.logger.info(
                        f"Placeholder message set: '{placeholder_text}'"
                    )
                elif hasattr(self.learn_mode.sign_svg_widget, "load"):
                    # QSvgWidget - can't set text, just log it
                    self.learn_mode.logger.debug(
                        f"QSvgWidget placeholder text would be: '{placeholder_text}'"
                    )
                else:
                    # Unknown widget type
                    self.learn_mode.logger.debug("Unknown widget type for placeholder")

                # Ensure the text is visible by setting a visible text color
                if hasattr(self.learn_mode.sign_svg_widget, "setStyleSheet"):
                    current_theme = get_theme()
                    text_color = "#333333" if current_theme == "Light" else "#ffffff"
                    self.learn_mode.sign_svg_widget.setStyleSheet(
                        f"color: {text_color};"
                    )
            else:
                self.learn_mode.logger.warning(
                    "sign_svg_widget not found for placeholder message"
                )
        except Exception as e:
            self.learn_mode.logger.error(f"Error showing placeholder message: {e}")

    def _on_clear_sign_clicked(self) -> None:
        """Handle clear sign button click"""
        try:
            # Clear the sign display (hand gesture)
            if hasattr(self.learn_mode, "sign_svg_widget"):
                # Handle different widget types appropriately
                if hasattr(self.learn_mode.sign_svg_widget, "setText"):
                    # QLabel or other text widget
                    self.learn_mode.sign_svg_widget.setText(
                        get_text("ui.language_selection.sign_will_appear_here")
                    )
                elif hasattr(self.learn_mode.sign_svg_widget, "load"):
                    # QSvgWidget - clear by loading empty content
                    self.learn_mode.sign_svg_widget.load("")
                else:
                    # Unknown widget type - just log it
                    self.learn_mode.logger.debug("Unknown widget type for sign display")

            # Show placeholder message in instructions label since sign_svg_widget is QSvgWidget (doesn't support text)
            self._set_placeholder_text()

            # Hide the close button since there's nothing to clear
            if hasattr(self.learn_mode, "clear_sign_btn"):
                self.learn_mode.clear_sign_btn.setVisible(False)

            # Clear button selections
            if hasattr(self.learn_mode, "alphabet_buttons"):
                self.learn_mode.character_manager.update_button_selection(
                    "", self.learn_mode.alphabet_buttons
                )
            if hasattr(self.learn_mode, "number_buttons"):
                self.learn_mode.character_manager.update_button_selection(
                    "", self.learn_mode.number_buttons
                )

            # Reset current character tracking
            if hasattr(self.learn_mode, "current_character"):
                self.learn_mode.current_character = None
            if hasattr(self.learn_mode, "current_char_type"):
                self.learn_mode.current_char_type = None

            # Update status
            if hasattr(self.learn_mode.main_window, "set_status"):
                self.learn_mode.main_window.set_status("Sign display cleared")

        except Exception as e:
            self.learn_mode.logger.error(f"Error clearing sign: {e}")

    def open_hpr_editor(self) -> None:
        """Open the HPR editor"""
        try:
            from .hpr_editor import SignLanguagePoseEditor

            if (
                not hasattr(self.learn_mode, "hpr_editor")
                or self.learn_mode.hpr_editor is None
            ):
                self.learn_mode.hpr_editor = SignLanguagePoseEditor(
                    self.learn_mode.animate_gesture_panel, self.learn_mode.main_window
                )

            self.learn_mode.hpr_editor.show()
            self.learn_mode.hpr_editor.raise_()
            self.learn_mode.hpr_editor.activateWindow()

            if hasattr(self.learn_mode.main_window, "set_status"):
                self.learn_mode.main_window.set_status("HPR Editor opened")
        except Exception as e:
            self.learn_mode.logger.error(f"Error opening HPR editor: {e}")
            if hasattr(self.learn_mode.main_window, "set_status"):
                self.learn_mode.main_window.set_status(f"Error opening HPR editor: {e}")

    def open_pose_validation(self) -> None:
        """Open the HPR editor with pose validation functionality"""
        try:
            from .hpr_editor import SignLanguagePoseEditor

            # Always create a new instance to avoid "already deleted" errors
            # The old instance will be properly cleaned up by Qt's parent-child relationship
            self.learn_mode.hpr_editor = SignLanguagePoseEditor(
                self.learn_mode.animate_gesture_panel, self.learn_mode.main_window
            )

            self.learn_mode.hpr_editor.show()
            self.learn_mode.hpr_editor.raise_()
            self.learn_mode.hpr_editor.activateWindow()

            if hasattr(self.learn_mode.main_window, "set_status"):
                self.learn_mode.main_window.set_status(
                    "HPR Editor with Pose Validation opened"
                )
        except Exception as e:
            self.learn_mode.logger.error(f"Error opening HPR editor: {e}")
            if hasattr(self.learn_mode.main_window, "set_status"):
                self.learn_mode.main_window.set_status(f"Error opening HPR editor: {e}")

    def on_pose_corrected(
        self, letter: str, corrected_pose: Dict[str, List[float]]
    ) -> None:
        """Handle pose corrections from validation panel"""
        try:
            self.learn_mode.logger.info(f"Pose corrected for letter {letter}")
            if hasattr(self.learn_mode.main_window, "set_status"):
                self.learn_mode.main_window.set_status(
                    f"Pose corrected for letter {letter}"
                )
        except Exception as e:
            self.learn_mode.logger.error(f"Error handling pose correction: {e}")

    def on_text_to_sign_play(self) -> None:
        """Handle text-to-sign play button click"""
        try:
            # Get text from input
            if hasattr(self.learn_mode.main_window, "get_text_input"):
                input_text = self.learn_mode.main_window.get_text_input()
                if input_text and input_text.strip():
                    # Process the text
                    output_text = self.process_text(input_text)

                    # Set output
                    if hasattr(self.learn_mode.main_window, "set_text_output"):
                        self.learn_mode.main_window.set_text_output(output_text)

                    # Update status
                    if hasattr(self.learn_mode.main_window, "set_status"):
                        self.learn_mode.main_window.set_status(
                            f"Processed text: {input_text}"
                        )

                    # Show translation message
                    self._show_text_translation_message(input_text)
                else:
                    # Show placeholder message
                    self._show_placeholder_message()
        except Exception as e:
            self.learn_mode.logger.error(f"Error in text-to-sign play: {e}")
            if hasattr(self.learn_mode.main_window, "set_status"):
                self.learn_mode.main_window.set_status("Error processing text")
