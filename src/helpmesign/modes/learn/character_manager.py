"""
Character Management for Learn Mode
Contains character button and selection methods extracted from learn_mode.py
"""

from typing import Dict, Optional

from ...utils.language_manager import get_text
from ...utils.theme_manager import get_theme_style


class LearnModeCharacterManager:
    """Character management methods for Learn Mode"""

    def __init__(self, learn_mode):
        self.learn_mode = learn_mode

    def _get_current_language(self) -> Optional[str]:
        """Get the current language from global settings"""
        # Use the global settings loaded at initialization
        if (
            hasattr(self.learn_mode, "current_language")
            and self.learn_mode.current_language
        ):
            return self.learn_mode.current_language

        # If not available, log error
        self.learn_mode.logger.error("No language available in global settings")
        return None

    def update_character_buttons(self):
        """Update the character buttons based on the selected language and hand preference"""
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QLabel, QPushButton

        from ...utils.sign_language_loader import get_sign_language_loader
        from ...utils.theme_manager import get_theme_manager

        # Prevent excessive updates
        if (
            hasattr(self.learn_mode, "_updating_character_buttons")
            and self.learn_mode._updating_character_buttons
        ):
            return

        self.learn_mode._updating_character_buttons = True

        # Get the selected language and hand preference from global settings
        selected_language = self.learn_mode.current_language
        hand_preference = self.learn_mode.current_hand_preference

        try:
            # Safety check - ensure character layout exists
            if not hasattr(self.learn_mode, "character_layout"):
                self.learn_mode.logger.warning(
                    "Character layout not initialized yet, skipping character button update"
                )
                return

            # Ensure button dictionaries exist
            if not hasattr(self.learn_mode, "alphabet_buttons"):
                self.learn_mode.alphabet_buttons = {}
            if not hasattr(self.learn_mode, "number_buttons"):
                self.learn_mode.number_buttons = {}

            # Safely clear existing buttons without deleteLater() to avoid memory corruption
            for button in self.learn_mode.alphabet_buttons.values():
                if button and button.parent():
                    button.setParent(None)
            for button in self.learn_mode.number_buttons.values():
                if button and button.parent():
                    button.setParent(None)
            self.learn_mode.alphabet_buttons.clear()
            self.learn_mode.number_buttons.clear()

            # Safely clear the layout and delete widgets to avoid leaks/corruption
            while self.learn_mode.character_layout.count():
                child = self.learn_mode.character_layout.takeAt(0)
                w = child.widget()
                if w:
                    try:
                        w.setParent(None)
                        if hasattr(w, "deleteLater"):
                            w.deleteLater()
                    except Exception:
                        pass

            # Validate that we have the required settings
            if not selected_language:
                self.learn_mode.logger.error(
                    "No language configured in global settings"
                )
                return
            if not hand_preference:
                self.learn_mode.logger.error(
                    "No hand preference configured in global settings"
                )
                return

            # Load sign language data dynamically
            sign_loader = get_sign_language_loader()

            # Get alphabet and number signs for the selected language and hand
            alphabet_signs = sign_loader.get_alphabet_signs(
                selected_language, hand_preference
            )
            number_signs = sign_loader.get_number_signs(
                selected_language, hand_preference
            )

            if not alphabet_signs and not number_signs:
                # No sign data available - show error message
                error_label = QLabel(
                    f"Sign language data for {selected_language} is not available.\nPlease contact support@cycleruncode.club for assistance."
                )
                error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                error_label.setStyleSheet(
                    """
                    QLabel {
                        color: #dc3545;
                        font-weight: bold;
                        padding: 20px;
                        background-color: #f8d7da;
                        border: 1px solid #f5c6cb;
                        border-radius: 5px;
                        margin: 10px;
                    }
                """
                )
                self.learn_mode.character_layout.addWidget(error_label, 0, 0)
                return

            # Extract characters from the sign data
            alphabet_chars = list(alphabet_signs.keys())
            number_chars = list(number_signs.keys())
            # If no alphabet loaded (e.g., two-hand language with single dataset),
            # attempt to load without hand distinction
            if (
                not alphabet_chars
                and getattr(self.learn_mode, "current_hand_preference", "right")
                == "both"
            ):
                fallback_alphabet = self.learn_mode.sign_loader.get_alphabet_signs(
                    selected_language, "both"
                )
                alphabet_chars = (
                    list(fallback_alphabet.keys()) if fallback_alphabet else []
                )
                fallback_numbers = self.learn_mode.sign_loader.get_number_signs(
                    selected_language, "both"
                )
                number_chars = (
                    list(fallback_numbers.keys()) if fallback_numbers else number_chars
                )

            # Combine all characters
            all_characters = alphabet_chars + number_chars

            if not all_characters:
                # No characters available - show error message
                error_label = QLabel(
                    f"No characters available for {selected_language}.\nPlease contact support@cycleruncode.club for assistance."
                )
                error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                error_label.setStyleSheet(
                    """
                    QLabel {
                        color: #dc3545;
                        font-weight: bold;
                        padding: 20px;
                        background-color: #f8d7da;
                        border: 1px solid #f5c6cb;
                        border-radius: 5px;
                        margin: 10px;
                    }
                """
                )
                self.learn_mode.character_layout.addWidget(error_label, 0, 0)
                return

            # Improved layout: 6 columns, 48px buttons, better spacing
            max_columns = 6
            button_size = 48

            # Get theme-aware character button styling from theme manager with dynamic font size
            theme_manager = get_theme_manager()
            char_button_style = theme_manager.get_complete_style(
                "learn_mode_character_button", include_font_size=True
            )

            row, col = 0, 0
            for char in all_characters:
                btn = QPushButton(char)
                btn.setFixedSize(button_size, button_size)
                btn.setMinimumSize(button_size, button_size)
                btn.setMaximumSize(button_size, button_size)
                btn.setStyleSheet(char_button_style)

                # Connect to appropriate handler based on character type
                if char in alphabet_chars:
                    btn.clicked.connect(
                        lambda checked, c=char: self.learn_mode.on_alphabet_selected(c)
                    )
                    self.learn_mode.alphabet_buttons[char] = btn
                else:
                    btn.clicked.connect(
                        lambda checked, c=char: self.learn_mode.on_number_selected(c)
                    )
                    self.learn_mode.number_buttons[char] = btn

                # Add the button to the grid for both letters and numbers
                self.learn_mode.character_layout.addWidget(btn, row, col)

                col += 1
                if col >= max_columns:
                    col = 0
                    row += 1

        except Exception as e:
            # Error loading sign data - show error message
            error_label = QLabel(
                f"Error loading sign language data for {selected_language}.\nPlease contact support@cycleruncode.club for assistance.\nError: {str(e)}"
            )
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet(
                """
                QLabel {
                    color: #dc3545;
                    font-weight: bold;
                    padding: 20px;
                    background-color: #f8d7da;
                    border: 1px solid #f5c6cb;
                    border-radius: 5px;
                    margin: 10px;
                }
            """
            )
            self.learn_mode.character_layout.addWidget(error_label, 0, 0)
        finally:
            self.learn_mode._updating_character_buttons = False

    def update_button_selection(self, selected: str, button_dict: dict) -> None:
        """Update button styling to show selection using property, not stylesheet"""
        # Reset ALL buttons (both alphabet and number) to unselected
        for btn in self.learn_mode.alphabet_buttons.values():
            btn.setProperty("selected", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        for btn in self.learn_mode.number_buttons.values():
            btn.setProperty("selected", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        # Highlight selected button
        if selected in button_dict:
            button_dict[selected].setProperty("selected", True)
            button_dict[selected].style().unpolish(button_dict[selected])
            button_dict[selected].style().polish(button_dict[selected])

    def on_alphabet_selected(self, letter: str) -> None:
        """Handle alphabet letter selection"""
        # Update button styling
        self.update_button_selection(letter, self.learn_mode.alphabet_buttons)

        # Update sign display
        self.learn_mode.update_sign_display(letter, "letter")

        # Trigger 3D gesture animation if panel is available
        try:
            if hasattr(self.learn_mode, "animate_gesture_panel"):
                hand = getattr(self.learn_mode, "current_hand_preference", "right")

                # Get gesture data and validate it before playing
                gesture_data = self.learn_mode._get_gesture_data(letter, "letter", hand)
                if gesture_data:
                    validated_gesture = self.learn_mode.validate_gesture_before_play(
                        gesture_data
                    )

                    # Check for violations and log them
                    violations = self.learn_mode.get_gesture_constraint_violations(
                        gesture_data
                    )
                    if violations:
                        self.learn_mode.logger.warning(
                            f"Gesture '{letter}' has {len(violations)} constraint violations"
                        )
                        for violation in violations:
                            self.learn_mode.logger.debug(
                                f"Joint '{violation['joint']}' ({violation['description']}) "
                                f"violates constraints: {violation['original_values']}"
                            )

                    # Play the validated gesture
                    current_language = self._get_current_language()
                    if current_language:
                        self.learn_mode.animate_gesture_panel.set_language(
                            current_language
                        )
                        self.learn_mode.animate_gesture_panel.play_gesture(letter, hand)
                else:
                    # Fallback to direct gesture playing if no data available
                    current_language = self._get_current_language()
                    if current_language:
                        self.learn_mode.animate_gesture_panel.set_language(
                            current_language
                        )
                        self.learn_mode.animate_gesture_panel.play_gesture(letter, hand)
        except Exception as e:
            self.learn_mode.logger.error(
                f"Error playing alphabet gesture '{letter}': {e}"
            )

    def on_number_selected(self, number: str) -> None:
        """Handle number selection"""
        # Update button styling
        self.update_button_selection(number, self.learn_mode.number_buttons)

        # Update sign display
        self.learn_mode.update_sign_display(number, "number")

        # Trigger 3D gesture animation if panel is available
        try:
            if hasattr(self.learn_mode, "animate_gesture_panel"):
                hand = getattr(self.learn_mode, "current_hand_preference", "right")

                # Get gesture data and validate it before playing
                gesture_data = self.learn_mode._get_gesture_data(number, "number", hand)
                if gesture_data:
                    validated_gesture = self.learn_mode.validate_gesture_before_play(
                        gesture_data
                    )

                    # Check for violations and log them
                    violations = self.learn_mode.get_gesture_constraint_violations(
                        gesture_data
                    )
                    if violations:
                        self.learn_mode.logger.warning(
                            f"Gesture '{number}' has {len(violations)} constraint violations"
                        )
                        for violation in violations:
                            self.learn_mode.logger.debug(
                                f"Joint '{violation['joint']}' ({violation['description']}) "
                                f"violates constraints: {violation['original_values']}"
                            )

                    # Play the validated gesture
                    current_language = self._get_current_language()
                    if current_language:
                        self.learn_mode.animate_gesture_panel.set_language(
                            current_language
                        )
                        self.learn_mode.animate_gesture_panel.play_gesture(number, hand)
                else:
                    # Fallback to direct gesture playing if no data available
                    current_language = self._get_current_language()
                    if current_language:
                        self.learn_mode.animate_gesture_panel.set_language(
                            current_language
                        )
                        self.learn_mode.animate_gesture_panel.play_gesture(number, hand)
        except Exception as e:
            self.learn_mode.logger.error(
                f"Error playing number gesture '{number}': {e}"
            )
