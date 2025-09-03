"""
Language Management for Learn Mode
Contains language selection and management methods extracted from learn_mode.py
"""

from typing import Dict, List, Optional

from ...utils.language_manager import get_text
from ...utils.theme_manager import get_theme_style


class LearnModeLanguageManager:
    """Language management methods for Learn Mode"""

    def __init__(self, learn_mode):
        self.learn_mode = learn_mode
        self.logger = learn_mode.logger

    def populate_language_list(self, category: str):
        """Populate the language list based on category using grid layout"""
        # Prevent excessive recalculations
        if hasattr(self.learn_mode, "_populating_languages") and getattr(
            self.learn_mode, "_populating_languages", False
        ):
            return

        self.learn_mode._populating_languages = True

        try:
            # Clear existing items
            for i in reversed(range(self.learn_mode.language_list_layout.count())):
                item = self.learn_mode.language_list_layout.itemAt(i)
                if item and item.widget():
                    item.widget().setParent(None)

            # Get languages for category
            if category == "popular":
                languages = self.learn_mode.categories.get("popular", [])
            elif category == "beginner":
                languages = self.learn_mode.categories.get("beginner", [])
            elif category == "intermediate":
                languages = self.learn_mode.categories.get("intermediate", [])
            elif category == "advanced":
                languages = self.learn_mode.categories.get("advanced", [])
            else:
                languages = self.learn_mode.categories.get("all", [])

            self.learn_mode.filtered_languages = languages
            self.learn_mode.current_category = category
        finally:
            self.learn_mode._populating_languages = False

        # Calculate optimal number of columns based on available width
        # Get actual available width from the scroll area, accounting for scrollbar
        try:
            available_width = (
                self.learn_mode.language_list_area.width()
                if self.learn_mode.language_list_area.width() > 0
                else 600
            )
            # Handle case where width might be a Mock object in tests
            if (
                hasattr(available_width, "_mock_name")
                or str(type(available_width)).find("Mock") != -1
            ):
                available_width = 600  # Default width for tests

            scrollbar_width = 16  # Approximate scrollbar width
            effective_width = available_width - scrollbar_width

            button_width = 70  # Target button width
            spacing = 8  # Grid spacing
            margins = 8  # Total margins

            # Calculate optimal columns: (effective_width - margins) / (button_width + spacing)
            # Allow more columns to better utilize space
            try:
                optimal_columns = max(
                    4, min(8, (effective_width - margins) // (button_width + spacing))
                )
            except (TypeError, AttributeError):
                # Fallback for test environment or when arithmetic fails
                optimal_columns = 4
        except (TypeError, AttributeError):
            # Fallback for test environment or when arithmetic fails
            optimal_columns = 4

        # Create language buttons in a grid layout with optimal columns
        for i, language in enumerate(languages):
            btn = self.create_language_button(language)

            # Preserve checked state for the currently selected language when the grid is rebuilt
            try:
                selected = getattr(self.learn_mode, "selected_language", None)
                if selected and language.get("code") == selected.get("code"):
                    btn.setChecked(True)
            except Exception:
                pass

            row = i // optimal_columns
            col = i % optimal_columns
            self.learn_mode.language_list_layout.addWidget(btn, row, col)

        # Add stretch factors to make buttons expand and fill available space
        for col in range(optimal_columns):
            self.learn_mode.language_list_layout.setColumnStretch(col, 1)

    def _on_language_area_resize(self, event):
        """Handle resize events to recalculate grid layout"""
        # Call the original resize event handler
        from PySide6.QtWidgets import QScrollArea

        QScrollArea.resizeEvent(self.learn_mode.language_list_area, event)

        # Only recalculate if we have languages loaded and the resize is significant
        if (
            hasattr(self.learn_mode, "filtered_languages")
            and self.learn_mode.filtered_languages
        ):
            # Use a timer to debounce rapid resize events
            if not hasattr(self.learn_mode, "_resize_timer"):
                from PySide6.QtCore import QTimer

                # Parent to the scroll area (QObject) for safe destruction on shutdown
                self.learn_mode._resize_timer = QTimer(
                    self.learn_mode.language_list_area
                )
                self.learn_mode._resize_timer.setSingleShot(True)
                self.learn_mode._resize_timer.timeout.connect(
                    self._recalculate_grid_layout
                )

            # Reset the timer to prevent excessive recalculations
            self.learn_mode._resize_timer.start(100)  # 100ms delay

    def _recalculate_grid_layout(self):
        """Recalculate the grid layout based on current width"""
        if hasattr(self.learn_mode, "current_category"):
            self.populate_language_list(self.learn_mode.current_category)

    def create_language_button(self, language: dict):
        """Create a compact button for a language in grid layout"""
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFont
        from PySide6.QtWidgets import QPushButton

        # Get language information
        code = language.get("code", "")
        flag = language.get("flag", "🌐")
        name = language.get("name", "Unknown")
        native_name = language.get("nativeName", "")
        speakers = language.get("metadata", {}).get("speakers", 0)
        difficulty = language.get("metadata", {}).get("difficulty", "Unknown")
        regions = language.get("metadata", {}).get("regions", [])
        writing_systems = language.get("writingSystems", {})

        # Format button text with just flag and code - compact for grid
        button_text = f"{flag} {code}"

        btn = QPushButton(button_text)
        btn.setCheckable(True)
        btn.setProperty("language_code", code)
        btn.setProperty("language_data", language)
        btn.clicked.connect(
            lambda checked: self.learn_mode.on_language_selected(language)
        )

        # Get theme-aware language button styling from theme manager
        language_button_style = get_theme_style("learn_mode_language_button")

        # Replace font-family placeholder with actual font family
        language_button_style = language_button_style.replace(
            'font-family: "Roboto"',
            f'font-family: "{self.learn_mode.current_font_family}"',
        )

        # Flexible styling for grid layout that utilizes available space
        btn.setStyleSheet(language_button_style)

        # Enhanced tooltip with statistics
        tooltip = f"<b>{name}</b><br>"
        if native_name and native_name != name:
            tooltip += f"<b>Native:</b> {native_name}<br>"
        tooltip += f"<b>Code:</b> {code}<br>"
        tooltip += f"<b>Speakers:</b> {speakers:,}<br>"
        tooltip += f"<b>Difficulty:</b> {difficulty}<br>"
        if regions:
            tooltip += f"<b>Regions:</b> {', '.join(regions)}<br>"
        if writing_systems:
            writing_system_keys = list(writing_systems.keys())
            if writing_system_keys:
                tooltip += (
                    f"<b>Writing Systems:</b> {', '.join(writing_system_keys)}<br>"
                )

        btn.setToolTip(tooltip)

        return btn

    def on_language_selected(self, language: dict):
        from PySide6.QtCore import Qt

        """Handle language selection"""
        self.learn_mode.selected_language = language

        # Update button states (if legacy in-panel list exists)
        try:
            if (
                hasattr(self.learn_mode, "language_list_layout")
                and self.learn_mode.language_list_layout is not None
            ):
                for i in range(self.learn_mode.language_list_layout.count()):
                    item = self.learn_mode.language_list_layout.itemAt(i)
                    if item and item.widget():
                        btn = item.widget()
                        if btn.property("language_code") == language.get("code"):
                            btn.setChecked(True)
                        else:
                            btn.setChecked(False)
        except Exception:
            pass

        # Update sign display title to show selected language flag and code (if present)
        flag = language.get("flag", "🌐")
        code = language.get("code", "ASL")
        if self.learn_mode.sign_title is not None:
            try:
                self.learn_mode.sign_title.setText(f"{flag} {code}")
                # Ensure stylesheet does not override center alignment
                self.learn_mode.sign_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            except Exception:
                pass

        # Change the sign language for the sign display
        language_code = language.get("code", "ASL")
        self.learn_mode.change_sign_language(language_code)

        # Language-aware hand control:
        # - If language offers only a two-hand form (e.g., BSL), select 'both' and hide icons
        # - If language offers left/right variants, show icons and ensure a concrete hand is selected
        try:
            hands = []
            if hasattr(self.learn_mode, "sign_loader") and self.learn_mode.sign_loader:
                hands = self.learn_mode.sign_loader.get_available_hands(language_code)
            has_left_or_right = any(h in ("left", "right") for h in hands)
            # Treat missing metadata as a two-hand language by default (e.g., BSL)
            has_both_only = ("both" in hands) or (not hands and not has_left_or_right)

            if has_left_or_right:
                # Show icons
                if hasattr(self.learn_mode, "right_hand_btn"):
                    self.learn_mode.right_hand_btn.setVisible(True)
                if hasattr(self.learn_mode, "left_hand_btn"):
                    self.learn_mode.left_hand_btn.setVisible(True)

                # If previous language set preference to 'both', switch to a concrete hand
                if (
                    getattr(self.learn_mode, "current_hand_preference", "right")
                    == "both"
                ):
                    # Default to right hand
                    self.learn_mode._set_hand_preference("right")
            elif has_both_only:
                # BSL-like languages: default to right hand, but allow both hands for word-based signing
                # Don't change the UI preference to "both"
                if (
                    getattr(self.learn_mode, "current_hand_preference", "right")
                    == "both"
                ):
                    # Reset to right hand if it was set to "both"
                    self.learn_mode._set_hand_preference("right")
            else:
                # Unknown capability info; do not change visibility, but avoid 'both'
                if (
                    getattr(self.learn_mode, "current_hand_preference", "right")
                    == "both"
                ):
                    self.learn_mode._set_hand_preference("right")
        except Exception:
            pass

        # Update icons based on the current in-memory state
        self.learn_mode._update_hand_icon_visibility_from_pref()

        # Save language selection to configuration
        self.save_language_selection(language_code)

        # Update character buttons based on new language
        self.learn_mode.update_character_buttons()

        # If the selected language has no available characters for the current
        # hand preference, reset the sign area to the default placeholder and
        # clear any prior selection state.
        try:
            hand_pref = getattr(self.learn_mode, "current_hand_preference", "right")
            has_alpha = bool(
                self.learn_mode.sign_loader.get_alphabet_signs(language_code, hand_pref)
            )
            has_nums = bool(
                self.learn_mode.sign_loader.get_number_signs(language_code, hand_pref)
            )
            if not has_alpha and not has_nums:
                self.learn_mode.current_character = None
                self.learn_mode.current_char_type = None
                self.learn_mode._show_placeholder_message()
                if hasattr(self.learn_mode, "clear_sign_btn"):
                    self.learn_mode.clear_sign_btn.setVisible(False)
        except Exception:
            pass

        # Re-evaluate hand icon visibility (no extra read; use current state)
        self.learn_mode._update_hand_icon_visibility_from_pref()

    def _update_hand_icon_visibility_from_pref(self) -> None:
        """Show/hide hand icons solely based on saved hand preference.

        Always show individual left/right hand buttons, never show combined "both" button.
        """
        try:
            pref = getattr(self.learn_mode, "current_hand_preference", "right")

            # Always show individual hand buttons
            if hasattr(self.learn_mode, "right_hand_btn"):
                try:
                    self.learn_mode.right_hand_btn.setVisible(True)
                    self.learn_mode.right_hand_btn.setText("🖐️")
                    # Set selected state based on preference
                    is_right_selected = pref == "right"
                    self.learn_mode.right_hand_btn.setProperty(
                        "selected", is_right_selected
                    )
                    self.learn_mode.right_hand_btn.style().unpolish(
                        self.learn_mode.right_hand_btn
                    )
                    self.learn_mode.right_hand_btn.style().polish(
                        self.learn_mode.right_hand_btn
                    )
                except Exception:
                    pass
            if hasattr(self.learn_mode, "left_hand_btn"):
                try:
                    self.learn_mode.left_hand_btn.setVisible(True)
                    self.learn_mode.left_hand_btn.setText("🤚")
                    # Set selected state based on preference
                    is_left_selected = pref == "left"
                    self.learn_mode.left_hand_btn.setProperty(
                        "selected", is_left_selected
                    )
                    self.learn_mode.left_hand_btn.style().unpolish(
                        self.learn_mode.left_hand_btn
                    )
                    self.learn_mode.left_hand_btn.style().polish(
                        self.learn_mode.left_hand_btn
                    )
                except Exception:
                    pass
        except Exception:
            pass

    def save_language_selection(self, language_code: str) -> None:
        """Save the selected language to user configuration"""
        try:
            from ...core.startup import get_all_settings, save_all_settings

            # Get current settings
            current_settings = get_all_settings()

            # Update the language selection
            current_settings["selected_language"] = language_code

            # Save the updated settings
            if save_all_settings(current_settings):
                self.learn_mode.logger.info(
                    f"Language selection saved to config: {language_code}"
                )
            else:
                self.learn_mode.logger.error(
                    "Failed to save language selection to config"
                )

        except Exception as e:
            self.learn_mode.logger.error(f"Error saving language selection: {e}")

    def load_saved_language_selection(self) -> None:
        """Load the saved language selection from configuration"""
        # Prevent multiple calls
        if hasattr(self.learn_mode, "_language_loaded") and getattr(
            self.learn_mode, "_language_loaded", False
        ):
            return

        try:
            from ...core.startup import get_all_settings

            # Get current settings
            current_settings = get_all_settings()

            saved_language = current_settings.get("selected_language", "ASL")
            self.learn_mode.logger.info(
                f"Loaded saved language selection: {saved_language}"
            )

            # Find and select the saved language
            self.select_language_by_code(saved_language)

            self.learn_mode._language_loaded = True

        except Exception as e:
            self.learn_mode.logger.error(f"Error loading saved language selection: {e}")
            # Default to ASL if there's an error
            self.select_language_by_code("ASL")

    def select_language_by_code(self, language_code: str) -> None:
        """Select a language by its code"""
        try:
            # If an in-panel list exists (legacy), try to use it; otherwise skip
            if (
                hasattr(self.learn_mode, "language_list_layout")
                and self.learn_mode.language_list_layout is not None
            ):
                for i in range(self.learn_mode.language_list_layout.count()):
                    item = self.learn_mode.language_list_layout.itemAt(i)
                    if item and item.widget():
                        btn = item.widget()
                        if btn.property("language_code") == language_code:
                            btn.setChecked(True)
                            self.on_language_selected(btn.property("language_data"))
                            return

            # If not found in current list, try to find it in all languages
            from ...utils.language_loader import get_all_languages

            all_languages = get_all_languages()

            for language in all_languages:
                if language.get("code") == language_code:
                    # Update selected_language and apply
                    self.learn_mode.selected_language = language
                    self.on_language_selected(language)
                    # Force refresh for character grid/hand icons
                    try:
                        self.learn_mode.update_character_buttons()
                        self._update_hand_icon_visibility_from_pref()
                    except Exception:
                        pass
                    return

            # If still not found, default to ASL
            self.learn_mode.logger.warning(
                f"Language {language_code} not found, defaulting to ASL"
            )
            for language in all_languages:
                if language.get("code") == "ASL":
                    self.on_language_selected(language)
                    return

        except Exception as e:
            self.learn_mode.logger.error(f"Error selecting language by code: {e}")

    def on_search_changed(self, text: str):
        """Handle search text changes"""
        from ...utils.language_loader import search_languages

        if text.strip():
            # Search in all languages
            search_results = search_languages(text)
            self.populate_search_results(search_results)
        else:
            # Show current category
            self.populate_language_list(self.learn_mode.current_category)

    def populate_search_results(self, languages: list):
        """Populate language list with search results using grid layout"""
        # Clear existing items
        for i in reversed(range(self.learn_mode.language_list_layout.count())):
            item = self.learn_mode.language_list_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        self.learn_mode.filtered_languages = languages

        # Create language buttons for search results in a grid layout (4 columns for better space utilization)
        columns = 4
        for i, language in enumerate(languages):
            btn = self.create_language_button(language)
            row = i // columns
            col = i % columns
            self.learn_mode.language_list_layout.addWidget(btn, row, col)

    def show_category_menu(self):
        """Show the category selection menu"""
        try:
            # Position the menu below the button
            button_rect = self.learn_mode.category_button.rect()
            menu_pos = self.learn_mode.category_button.mapToGlobal(
                button_rect.bottomLeft()
            )
            self.learn_mode.category_menu.popup(menu_pos)
        except Exception as e:
            self.learn_mode.logger.error(f"Error showing category menu: {e}")

    def on_category_selected(self, category: str):
        """Handle category selection from menu"""
        try:
            # Update button text
            category_display_names = {
                "all": get_text("ui.language_selection.category_all"),
                "popular": get_text("ui.language_selection.category_popular"),
                "beginner": get_text("ui.language_selection.category_beginner"),
                "intermediate": get_text("ui.language_selection.category_intermediate"),
                "advanced": get_text("ui.language_selection.category_advanced"),
            }
            display_name = category_display_names.get(
                category, get_text("ui.language_selection.category_all")
            )
            self.learn_mode.category_text_label.setText(display_name)

            # Update current category
            self.learn_mode.current_category = category

            # Populate language list
            self.populate_language_list(category)

        except Exception as e:
            self.learn_mode.logger.error(f"Error handling category selection: {e}")
            self.populate_language_list("all")
