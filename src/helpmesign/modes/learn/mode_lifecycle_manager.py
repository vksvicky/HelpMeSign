"""
Mode Lifecycle Manager for Learn Mode
Handles mode activation, deactivation, and lifecycle management
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from ...core.startup import get_all_settings, save_all_settings
from ...utils.language_manager import get_text


class LearnModeLifecycleManager:
    """Manages mode lifecycle, activation, and deactivation for Learn Mode"""

    def __init__(self, learn_mode):
        self.learn_mode = learn_mode

    def activate(self) -> None:
        """Activate the learning mode"""
        try:
            # Set the mode in the main window
            self.learn_mode.main_window.set_mode("learn")
            self.learn_mode.main_window.set_status("Learning mode activated")

            # Add the learning widget to the main window's content area
            if (
                hasattr(self.learn_mode, "learning_widget")
                and self.learn_mode.learning_widget
            ):
                if hasattr(self.learn_mode.main_window, "content_area"):
                    content_area = self.learn_mode.main_window.content_area
                    content_area.addWidget(self.learn_mode.learning_widget)
                    content_area.setCurrentWidget(self.learn_mode.learning_widget)
                elif hasattr(self.learn_mode.main_window, "set_central_widget"):
                    main_window = self.learn_mode.main_window
                    main_window.set_central_widget(self.learn_mode.learning_widget)
                elif hasattr(self.learn_mode.main_window, "set_content_widget"):
                    main_window = self.learn_mode.main_window
                    main_window.set_content_widget(self.learn_mode.learning_widget)

            # Load saved language selection
            self.learn_mode.load_saved_language_selection()

            # Update character buttons
            self.learn_mode.update_character_buttons()

            # Update hand preference visibility and status bar
            self.learn_mode._restore_hand_preference_visual_state()

            # Ensure status bar is updated with current language and hand preference
            if hasattr(self.learn_mode.main_window, "status_bar"):
                self.learn_mode.main_window.status_bar.update_learning_mode_status()
                self.learn_mode.logger.debug("Status bar updated after mode activation")

            # Set up behavior and signal connections
            self.setup_behavior()

            # Start welcome animation timer
            self._start_welcome_animation_timer()

            # Initialize 3D character loading
            self._initialize_3d_character()

            # Update UI
            self.learn_mode.update_ui()

        except Exception as e:
            self.learn_mode.logger.error(f"Error activating learning mode: {e}")

    def deactivate(self) -> None:
        """Deactivate the learning mode"""
        try:
            # Stop any active timers
            if (
                hasattr(self.learn_mode, "welcome_timer")
                and self.learn_mode.welcome_timer
            ):
                self.learn_mode.welcome_timer.stop()

            # Remove the learning widget from content area
            if (
                hasattr(self.learn_mode, "learning_widget")
                and self.learn_mode.learning_widget
                and hasattr(self.learn_mode.main_window, "content_area")
            ):
                content_area = self.learn_mode.main_window.content_area
                content_area.removeWidget(self.learn_mode.learning_widget)

            # Clear content
            self.learn_mode.clear_content()

            # Remove event filters
            if hasattr(self.learn_mode, "eventFilter"):
                try:
                    # Remove event filter from any widgets that might have it
                    if (
                        hasattr(self.learn_mode, "learning_widget")
                        and self.learn_mode.learning_widget
                    ):
                        self.learn_mode.learning_widget.removeEventFilter(
                            self.learn_mode
                        )
                except Exception:
                    pass

            # Update status
            if hasattr(self.learn_mode.main_window, "set_status"):
                self.learn_mode.main_window.set_status("Learning mode deactivated")

        except Exception as e:
            self.learn_mode.logger.error(f"Error deactivating learning mode: {e}")

    def _start_welcome_animation_timer(self) -> None:
        """Start the welcome animation timer"""
        try:
            # Create a timer for welcome animation
            if not hasattr(self.learn_mode, "welcome_timer"):
                from PySide6.QtCore import QTimer

                self.learn_mode.welcome_timer = QTimer()
                self.learn_mode.welcome_timer.timeout.connect(self._on_welcome_timer)

            # Start the timer with a delay
            self.learn_mode.welcome_timer.start(1000)  # 1 second delay

        except Exception as e:
            self.learn_mode.logger.error(f"Error starting welcome animation timer: {e}")

    def _on_welcome_timer(self) -> None:
        """Handle welcome timer timeout"""
        try:
            # Stop the timer
            if hasattr(self.learn_mode, "welcome_timer"):
                self.learn_mode.welcome_timer.stop()

            # Get current language and hand preference from global settings
            current_language = getattr(self.learn_mode, "current_language", None)
            hand_preference = getattr(self.learn_mode, "current_hand_preference", None)

            # Validate that we have the required settings
            if not current_language:
                self.learn_mode.logger.error("No language available in global settings")
                return
            if not hand_preference:
                self.learn_mode.logger.error(
                    "No hand preference available in global settings"
                )
                return

            # Start welcome animation
            welcome_text = get_text("ui.welcome.learning_mode")
            self._start_welcome_animation(
                welcome_text, current_language, hand_preference
            )

            # Ensure status bar is updated with current language and hand preference
            # This runs after a delay, so the UI should be fully ready
            if hasattr(self.learn_mode.main_window, "status_bar"):
                # Add a small additional delay to ensure UI is fully ready
                from PySide6.QtCore import QTimer

                # Store timer as instance variable to prevent garbage collection
                if not hasattr(self, "_delayed_status_timer"):
                    self._delayed_status_timer = QTimer()
                    self._delayed_status_timer.setSingleShot(True)
                    self._delayed_status_timer.timeout.connect(
                        self._delayed_status_bar_update
                    )

                self._delayed_status_timer.start(500)  # 500ms additional delay
                self.learn_mode.logger.debug(
                    f"Status bar update scheduled in welcome timer for {current_language} - {hand_preference} hand"
                )

        except Exception as e:
            self.learn_mode.logger.error(f"Error in welcome timer: {e}")

    def _delayed_status_bar_update(self) -> None:
        """Delayed status bar update that checks current content before updating"""
        try:
            self.learn_mode.logger.debug("Delayed status bar update method called")

            if hasattr(self.learn_mode.main_window, "status_bar"):
                status_bar = self.learn_mode.main_window.status_bar

                # Check if status bar already has the correct content
                current_text = status_bar.status_label.text()

                # Get current language and hand preference from learn_mode
                current_language = getattr(self.learn_mode, "current_language", "ASL")
                current_hand_preference = getattr(
                    self.learn_mode, "current_hand_preference", "right"
                )

                # Format hand preference for display
                hand_display = "Left" if current_hand_preference == "left" else "Right"

                expected_text = f"Mode: {get_text('modes.learn.name')} | {current_language} - {hand_display} Hand"

                self.learn_mode.logger.debug(
                    f"Current status bar text: '{current_text}'"
                )
                self.learn_mode.logger.debug(f"Expected text: '{expected_text}'")

                if current_text == expected_text:
                    self.learn_mode.logger.debug(
                        "Status bar already has correct content, skipping update"
                    )
                    return

                # Only update if content is different or blank
                if current_text != expected_text:
                    self.learn_mode.logger.debug(
                        f"Updating status bar from '{current_text}' to '{expected_text}'"
                    )
                    status_bar.update_learning_mode_status()
                else:
                    self.learn_mode.logger.debug(
                        "Status bar content is correct, no update needed"
                    )
            else:
                self.learn_mode.logger.debug("No status bar found in main window")

        except Exception as e:
            self.learn_mode.logger.error(f"Error in delayed status bar update: {e}")

    def _start_welcome_animation(self, welcome: str, lang: str, hand: str) -> None:
        """Start the welcome animation"""
        try:
            # This would typically trigger a welcome animation
            # For now, just log the welcome message
            self.learn_mode.logger.info(
                f"Welcome to {lang} learning mode ({hand} hand)"
            )

            # Show hand preference in status bar instead of generic welcome message
            if hasattr(self.learn_mode.main_window, "set_status"):
                hand_message = f"Hand preference set to {hand}"
                self.learn_mode.logger.debug(
                    f"Setting hand preference status: '{hand_message}'"
                )
                self.learn_mode.main_window.set_status(hand_message)
            else:
                self.learn_mode.logger.debug(
                    "No set_status method available for hand preference display"
                )

        except Exception as e:
            self.learn_mode.logger.error(f"Error starting welcome animation: {e}")

    def _set_hand_preference(self, hand_preference: str) -> None:
        """Set the hand preference"""
        try:
            # Validate hand preference
            if hand_preference not in ["left", "right", "both"]:
                self.learn_mode.logger.warning(
                    f"Invalid hand preference: {hand_preference}"
                )
                return

            self.learn_mode.logger.info(
                f"Setting hand preference to: {hand_preference}"
            )
            # Update local state
            self.learn_mode.current_hand_preference = hand_preference

            # Update UI to reflect the change
            lang_manager = self.learn_mode.sign_language_manager
            lang_manager._update_hand_icon_visibility_from_pref()

            # Update character buttons
            self.learn_mode.update_character_buttons()

            # Save to configuration
            self._save_hand_preference_to_config(hand_preference)

            # Update status with hand preference change message
            if hasattr(self.learn_mode.main_window, "set_status"):
                if hand_preference == "both":
                    hand_message = "Hand preference set to both hands"
                else:
                    hand_message = f"Hand preference set to {hand_preference}"
                self.learn_mode.main_window.set_status(hand_message)

            # Schedule status bar update after a delay to show the temporary message
            from PySide6.QtCore import QTimer

            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self._restore_status_bar_display())
            timer.start(3000)  # 3 seconds delay

        except Exception as e:
            self.learn_mode.logger.error(f"Error setting hand preference: {e}")

    def _save_hand_preference_to_config(self, hand_preference: str) -> None:
        """Save hand preference to configuration"""
        try:
            # Get current settings
            current_settings = get_all_settings()

            # Update hand preference
            current_settings["hand_preference"] = hand_preference

            # Save settings
            if save_all_settings(current_settings):
                self.learn_mode.logger.info(
                    f"Hand preference saved to config: {hand_preference}"
                )
            else:
                self.learn_mode.logger.error("Failed to save hand preference to config")

        except Exception as e:
            self.learn_mode.logger.error(f"Error saving hand preference: {e}")

    def _on_hand_preference_changed(self, hand_preference: str) -> None:
        """Handle hand preference change"""
        try:
            # Set the new hand preference
            self._set_hand_preference(hand_preference)

            # Update the current character display if one is selected
            if (
                hasattr(self.learn_mode, "current_character")
                and self.learn_mode.current_character
            ):
                char_type = getattr(self.learn_mode, "current_char_type", "letter")
                self.learn_mode.update_sign_display(
                    self.learn_mode.current_character, char_type
                )

        except Exception as e:
            self.learn_mode.logger.error(f"Error handling hand preference change: {e}")

    def change_sign_language(self, language: str) -> None:
        """Change the sign language"""
        try:
            # Update current language
            self.learn_mode.current_language = language

            # Update character buttons
            self.learn_mode.update_character_buttons()

            # Update hand preference visual state and status bar for the new language
            self._restore_hand_preference_visual_state()

            # Status bar will be updated by _restore_hand_preference_visual_state() to show proper hand preference format
            self.learn_mode.logger.debug(
                f"Language changed to {language}, status bar updated via hand preference restoration"
            )

        except Exception as e:
            self.learn_mode.logger.error(f"Error changing sign language: {e}")

    def _on_external_language_selected(self, code: str) -> None:
        """Handle external language selection"""
        try:
            self.learn_mode.logger.info(
                f"External language selection received for code: {code}"
            )

            # Get the full language data from the language code
            from ...utils.language_loader import get_all_languages

            languages = get_all_languages()
            language_data = None

            self.learn_mode.logger.info(f"Found {len(languages)} languages in total")

            for lang in languages:
                if lang.get("code") == code:
                    language_data = lang
                    self.learn_mode.logger.info(
                        f"Found language data for {code}: {lang.get('name')}"
                    )
                    break

            if language_data:
                # Call the language manager's on_language_selected with full data
                self.learn_mode.logger.info(f"Calling language manager for {code}")
                self.learn_mode.sign_language_manager.on_language_selected(
                    language_data
                )
                self.learn_mode.logger.info(
                    f"Language changed to {code} via external selection"
                )
            else:
                self.learn_mode.logger.warning(
                    f"Language data not found for code: {code}"
                )

        except Exception as e:
            self.learn_mode.logger.error(
                f"Error handling external language selection: {e}"
            )

    def _restore_hand_preference_visual_state(self) -> None:
        """Restore the visual state of hand preference buttons and update status bar"""
        try:
            # Get current hand preference
            current_pref = getattr(self.learn_mode, "current_hand_preference", "right")

            # Update button states
            if hasattr(self.learn_mode, "right_hand_btn"):
                is_right_selected = current_pref == "right"
                self.learn_mode.right_hand_btn.setProperty(
                    "selected", is_right_selected
                )
                self.learn_mode.right_hand_btn.style().unpolish(
                    self.learn_mode.right_hand_btn
                )
                self.learn_mode.right_hand_btn.style().polish(
                    self.learn_mode.right_hand_btn
                )

            if hasattr(self.learn_mode, "left_hand_btn"):
                is_left_selected = current_pref == "left"
                self.learn_mode.left_hand_btn.setProperty("selected", is_left_selected)
                self.learn_mode.left_hand_btn.style().unpolish(
                    self.learn_mode.left_hand_btn
                )
                self.learn_mode.left_hand_btn.style().polish(
                    self.learn_mode.left_hand_btn
                )

            # Update status bar to show current hand preference
            if hasattr(self.learn_mode.main_window, "status_bar"):
                self.learn_mode.main_window.status_bar.update_learning_mode_status()
                self.learn_mode.logger.debug(
                    f"Status bar updated with hand preference: {current_pref}"
                )

        except Exception as e:
            self.learn_mode.logger.error(
                f"Error restoring hand preference visual state: {e}"
            )

    def _initialize_3d_character(self) -> None:
        """Initialize 3D character loading"""
        try:
            # Check if animate panel exists
            if (
                hasattr(self.learn_mode, "animate_gesture_panel")
                and self.learn_mode.animate_gesture_panel
            ):
                # Get the default character model path
                from ...utils.resource_manager import ResourceManager

                resource_manager = ResourceManager()
                model_path = resource_manager.get_model_path("arivo.glb")

                # Load the 3D character
                panel = self.learn_mode.animate_gesture_panel
                panel.load_character(model_path)

                self.learn_mode.logger.info(
                    f"3D character loading initialized with model: " f"{model_path}"
                )
            else:
                self.learn_mode.logger.warning(
                    "Animate gesture panel not found, " "cannot initialize 3D character"
                )

        except Exception as e:
            self.learn_mode.logger.error(f"Error initializing 3D character: {e}")

    def _force_layout_stability(self) -> None:
        """Force layout stability by updating the layout"""
        try:
            # Force layout update
            if (
                hasattr(self.learn_mode, "learning_widget")
                and self.learn_mode.learning_widget
            ):
                self.learn_mode.learning_widget.updateGeometry()
                self.learn_mode.learning_widget.update()

        except Exception as e:
            self.learn_mode.logger.error(f"Error forcing layout stability: {e}")

    def setup_behavior(self) -> None:
        """Set up behavior and event handlers"""
        try:
            # Set up hand preference button handlers
            if hasattr(self.learn_mode, "right_hand_btn"):
                self.learn_mode.right_hand_btn.clicked.connect(
                    lambda: self._on_hand_preference_changed("right")
                )

            if hasattr(self.learn_mode, "left_hand_btn"):
                self.learn_mode.left_hand_btn.clicked.connect(
                    lambda: self._on_hand_preference_changed("left")
                )

            # Set up category button handler
            if hasattr(self.learn_mode, "category_button"):
                self.learn_mode.category_button.clicked.connect(
                    self.learn_mode.sign_language_manager.show_category_menu
                )

            # Set up search handler
            if hasattr(self.learn_mode, "search_input"):
                self.learn_mode.search_input.textChanged.connect(
                    self.learn_mode.sign_language_manager.on_search_changed
                )

            # Set up text-to-sign play button handler
            if hasattr(self.learn_mode, "text_to_sign_play_btn"):
                btn = self.learn_mode.text_to_sign_play_btn
                btn.clicked.connect(
                    self.learn_mode.ui_behavior_manager.on_text_to_sign_play
                )

            # Set up clear button handler
            if hasattr(self.learn_mode, "clear_button"):
                btn = self.learn_mode.clear_button
                btn.clicked.connect(
                    self.learn_mode.ui_behavior_manager._on_clear_sign_clicked
                )

            # Set up HPR editor button handler
            # Set up HPR Editor button handler
            # Note: Connection is already set up in ui_components.py to avoid duplication
            # if hasattr(self.learn_mode, "hpr_editor_btn"):
            #     btn = self.learn_mode.hpr_editor_btn
            #     btn.clicked.connect(self.learn_mode.ui_behavior_manager.open_hpr_editor)

            # Set up Hand Pose Editor button handler
            # Note: Connection is already set up in ui_components.py to avoid duplication
            # if hasattr(self.learn_mode, "hand_pose_editor_btn"):
            #     btn = self.learn_mode.hand_pose_editor_btn
            #     btn.clicked.connect(self.learn_mode.open_hand_pose_editor)

            # Set up pose validation button handler
            if hasattr(self.learn_mode, "pose_validation_btn"):
                btn = self.learn_mode.pose_validation_btn
                btn.clicked.connect(
                    self.learn_mode.ui_behavior_manager.open_pose_validation
                )

            # Set up learn and clear request handlers
            if hasattr(self.learn_mode.main_window, "process_requested"):
                main_window = self.learn_mode.main_window
                main_window.process_requested.connect(
                    self.learn_mode._on_learn_requested
                )

            if hasattr(self.learn_mode.main_window, "clear_requested"):
                main_window = self.learn_mode.main_window
                main_window.clear_requested.connect(self.learn_mode._on_clear_requested)

            # Set up external language selection handler
            if hasattr(self.learn_mode.main_window, "language_selected"):
                main_window = self.learn_mode.main_window
                main_window.language_selected.connect(
                    self._on_external_language_selected
                )

            # Set up hand preference update handler
            if hasattr(self.learn_mode.main_window, "update_hand_preference"):
                main_window = self.learn_mode.main_window
                main_window.update_hand_preference.connect(
                    self.learn_mode._on_hand_preference_changed
                )

            # Set up event filter
            if (
                hasattr(self.learn_mode, "learning_widget")
                and self.learn_mode.learning_widget
            ):
                widget = self.learn_mode.learning_widget
                widget.installEventFilter(self.learn_mode.event_filter)

        except Exception as e:
            self.learn_mode.logger.error(f"Error setting up behavior: {e}")

    def _restore_status_bar_display(self) -> None:
        """Restore the normal status bar display after showing temporary messages"""
        try:
            # Update status bar to show normal mode display
            if hasattr(self.learn_mode.main_window, "status_bar"):
                self.learn_mode.main_window.status_bar.update_learning_mode_status()
                self.learn_mode.logger.debug("Status bar restored to normal display")
        except Exception as e:
            self.learn_mode.logger.error(f"Error restoring status bar display: {e}")
