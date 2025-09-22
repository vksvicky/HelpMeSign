"""
Learn Sign Language mode implementation
Provides character selection and sign display layout
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from PySide6.QtCore import QEvent, QObject

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget, QLabel
    from .animate_panel import AnimateGesturePanel

from ...utils.language_manager import get_text
from ...utils.sign_language_loader import get_sign_language_loader
from ..base_mode import BaseMode
from .character_manager import LearnModeCharacterManager
from .gesture_manager import LearnModeGestureManager
from .learning_progress import LearnModeLearningProgress
from .mode_lifecycle_manager import LearnModeLifecycleManager
from .sign_language_manager import LearnModeSignLanguageManager
from .ui_behavior_manager import LearnModeUIBehaviorManager

# Import refactored modules
from .ui_components import LearnModeUIComponents


class LearnModeEventFilter(QObject):
    """Event filter for LearnMode to handle widget events"""

    def __init__(self, learn_mode):
        super().__init__()
        self.learn_mode = learn_mode

    def eventFilter(self, obj, event):
        """Filter events for the learn mode"""
        if event.type() == QEvent.Type.Resize:
            # Handle resize events if needed
            pass
        return super().eventFilter(obj, event)


class LearnMode(BaseMode):
    """Learn Sign Language mode - character selection and sign display"""

    def __init__(self, main_window):
        # Initialize logger
        import logging

        self.logger = logging.getLogger(__name__)

        # Optional legacy title label retained for type-safety (may be unused)
        self.sign_title: Optional["QLabel"] = None

        # Hand pose editor instance

        # Initialize character tracking variables
        self.current_character: Optional[str] = None
        self.current_char_type: Optional[str] = None

        # Initialize learning progress tracking
        self.learning_progress: Dict[str, Dict[str, Any]] = {}
        self.lesson_history: List[Dict[str, Any]] = []
        self.current_lesson: Optional[Dict[str, Any]] = None

        # Initialize sign language loader
        self.sign_loader = get_sign_language_loader()

        # Load global settings once at initialization
        self._load_global_settings()

        self.current_category = "all"  # Track current category

        # Initialize animate panel (will be set up in setup_ui)
        self.animate_gesture_panel: Optional["AnimateGesturePanel"] = None

        # Initialize learning widget (will be set up in setup_ui)
        self.learning_widget: Optional["QWidget"] = None

        # Initialize UI layout components
        self.language_list_layout: Optional["QWidget"] = None
        self.category_text_label: Optional["QLabel"] = None

        # Initialize language selection tracking
        self.selected_language: Optional[Dict[str, Any]] = None

        # Initialize event filter
        self.event_filter = LearnModeEventFilter(self)

        # Initialize manager instances BEFORE calling parent __init__
        self.ui_components = LearnModeUIComponents(self)
        self.sign_language_manager = LearnModeSignLanguageManager(self)
        self.character_manager = LearnModeCharacterManager(self)
        self.gesture_manager = LearnModeGestureManager(self)
        self.learning_progress_manager = LearnModeLearningProgress(self)
        self.ui_behavior_manager = LearnModeUIBehaviorManager(self)
        self.mode_lifecycle_manager = LearnModeLifecycleManager(self)
        # Initialize theme and font information directly
        self._initialize_theme_and_font_info(main_window)

        # Now call parent __init__ which will call setup_ui()
        super().__init__(main_window)

    def get_mode_description(self) -> str:
        """Get mode description"""
        return "Learn sign language with interactive lessons and practice"

    def get_mode_name(self) -> str:
        """Get the display name for this mode"""
        return get_text("modes.learn.name")

    def _load_global_settings(self) -> None:
        """Load global settings once at initialization"""
        try:
            from ...core.startup import get_all_settings

            # Load settings from configuration (this is the only time we read from config)
            settings = get_all_settings()

            # Set global settings that will be used throughout the session
            self.current_language = settings.get("selected_language")
            self.current_hand_preference = settings.get("hand_preference")

            self.logger.info(
                f"Global settings loaded: language={self.current_language}, hand_preference={self.current_hand_preference}"
            )

        except Exception as e:
            self.logger.error(f"Failed to load global settings: {e}")
            # Set defaults if loading fails
            self.current_language = None
            self.current_hand_preference = None

    def _initialize_theme_and_font_info(self, main_window) -> None:
        """Initialize theme and font information from main window or config"""
        try:
            # Try to get theme and font info from main window first
            if hasattr(main_window, "theme") and hasattr(main_window, "font_size"):
                self.current_theme = main_window.theme
                self.current_font_size = main_window.font_size
                self.logger.debug(
                    f"Using theme and font from main window: {self.current_theme}, {self.current_font_size}"
                )
            else:
                # Fallback to config
                from ...core.startup import get_all_settings

                settings = get_all_settings()
                self.current_theme = settings.get("theme", "Light")
                self.current_font_size = settings.get("font_size", 16)
                self.logger.debug(
                    f"Using theme and font from config: {self.current_theme}, {self.current_font_size}"
                )

            # Get effective theme (handle System theme)
            self.effective_theme = self._get_effective_theme_from_theme(
                self.current_theme
            )

            # Get font family from theme manager
            from ...utils.theme_manager import get_font_family

            self.current_font_family = get_font_family()

        except Exception as e:
            self.logger.error(f"Error initializing theme and font info: {e}")
            # Fallback to system theme instead of hardcoded Light
            try:
                from ...core.startup import get_theme

                fallback_theme = get_theme()
            except Exception:
                fallback_theme = "Light"
            self.current_theme = fallback_theme
            self.effective_theme = fallback_theme
            self.current_font_size = 16
            self.current_font_family = "Roboto"

    def _get_effective_theme_from_theme(self, theme: str) -> str:
        """Get effective theme (Dark/Light) from theme name"""
        if theme == "System":
            # Detect system theme
            try:
                from ...utils.theme_manager import get_theme_manager

                theme_manager = get_theme_manager()
                current_theme = theme_manager.get_current_theme()

                if current_theme.startswith("System ("):
                    if "Dark" in current_theme:
                        return "Dark"
                    else:
                        return "Light"
                else:
                    return "Light"  # Fallback
            except Exception:
                return "Light"  # Fallback
        elif theme == "Dark":
            return "Dark"
        else:
            # Instead of hardcoded Light, get from system
            try:
                from ...core.startup import get_theme

                return get_theme()
            except Exception:
                return "Light"  # Final fallback

    def setup_ui(self) -> None:
        """Set up the mode-specific UI components"""
        # Create the main layout
        self.ui_components.create_learning_layout()

        # Set up behavior and event handlers
        self.mode_lifecycle_manager.setup_behavior()

        # Set initial placeholder text using the behavior manager
        if hasattr(self, "ui_behavior_manager"):
            self.ui_behavior_manager._set_placeholder_text()
            self.logger.debug("Initial placeholder text set via behavior manager")
        else:
            self.logger.warning("ui_behavior_manager not available during setup_ui")

    def setup_behavior(self) -> None:
        """Set up behavior and event handlers"""
        self.mode_lifecycle_manager.setup_behavior()

    def update_character_buttons(self):
        """Update the character buttons based on the selected language
        and hand preference"""
        self.character_manager.update_character_buttons()

    def populate_language_list(self, category: str):
        """Populate the language list based on category using grid layout"""
        self.sign_language_manager.populate_language_list(category)

        # Recalculate the grid layout based on current width
        self.sign_language_manager._recalculate_grid_layout()

    # Add missing methods as delegations to managers
    def on_alphabet_selected(self, letter: str) -> None:
        """Handle alphabet letter selection"""
        self.character_manager.on_alphabet_selected(letter)

    def on_number_selected(self, number: str) -> None:
        """Handle number selection"""
        self.character_manager.on_number_selected(number)

    def update_button_selection(self, selected: str, button_dict: dict) -> None:
        """Update button styling to show selection using property,
        not stylesheet"""
        self.character_manager.update_button_selection(selected, button_dict)

    def _update_hand_icon_visibility_from_pref(self) -> None:
        """Show/hide hand icons solely based on saved hand preference"""
        self.sign_language_manager._update_hand_icon_visibility_from_pref()

    def save_language_selection(self, language_code: str) -> None:
        """Save the selected language to user configuration"""
        self.sign_language_manager.save_language_selection(language_code)

    def load_saved_language_selection(self) -> None:
        """Load the saved language selection from configuration"""
        self.sign_language_manager.load_saved_language_selection()

    def select_language_by_code(self, language_code: str) -> None:
        """Select a language by its code"""
        self.sign_language_manager.select_language_by_code(language_code)

    def on_search_changed(self, text: str):
        """Handle search text changes"""
        self.sign_language_manager.on_search_changed(text)

    def populate_search_results(self, languages: list):
        """Populate language list with search results using grid layout"""
        self.sign_language_manager.populate_search_results(languages)

    def show_category_menu(self):
        """Show the category selection menu"""
        self.sign_language_manager.show_category_menu()

    def on_category_selected(self, category: str):
        """Handle category selection from menu"""
        self.sign_language_manager.on_category_selected(category)

    def on_category_changed(self, category_text: str):
        """Handle category selection changes"""
        self.sign_language_manager.on_category_changed(category_text)

    def on_language_selected(self, language: dict):
        """Handle language selection"""
        self.sign_language_manager.on_language_selected(language)

    def change_sign_language(self, language: str) -> None:
        """Change the sign language"""
        self.mode_lifecycle_manager.change_sign_language(language)

    def update_sign_display(self, character: str, char_type: str) -> None:
        """Update the sign display area with actual SVG signs"""
        self.ui_behavior_manager.update_sign_display(character, char_type)

    def process_text(self, text: str) -> str:
        """Process input text according to mode-specific logic"""
        return self.ui_behavior_manager.process_text(text)

    def open_hpr_editor(self) -> None:
        """Open the HPR editor"""
        self.ui_behavior_manager.open_hpr_editor()

    def open_pose_validation(self) -> None:
        """Open the pose validation panel"""
        self.ui_behavior_manager.open_pose_validation()

    def open_hand_pose_editor(self) -> None:
        """Open the GLB Viewer (replacing the old Hand Pose Editor)"""
        try:
            import os
            import subprocess
            import sys

            # Get the path to the GLB viewer (now in the same directory)
            current_dir = os.path.dirname(__file__)
            glb_viewer_path = os.path.join(current_dir, "glb_viewer.py")

            if not os.path.exists(glb_viewer_path):
                raise FileNotFoundError(f"GLB viewer not found at {glb_viewer_path}")

            # Get project root for working directory (GLB viewer needs access to resources)
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            )

            # Launch the GLB viewer in a separate process
            subprocess.Popen(
                [sys.executable, glb_viewer_path],
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.logger.info("GLB Viewer launched successfully")
            if hasattr(self.main_window, "set_status"):
                self.main_window.set_status("GLB Viewer opened")

        except Exception as e:
            self.logger.error(f"Error opening GLB Viewer: {e}")
            if hasattr(self.main_window, "set_status"):
                self.main_window.set_status(f"Error opening GLB Viewer: {e}")

    def _show_placeholder_message(self) -> None:
        """Show placeholder message"""
        self.ui_behavior_manager._show_placeholder_message()

    def _set_hand_preference(self, hand_preference: str) -> None:
        """Set the hand preference and update the UI"""
        self.mode_lifecycle_manager._set_hand_preference(hand_preference)

    def _on_hand_preference_changed(self, hand_preference: str) -> None:
        """Handle hand preference change"""
        self.mode_lifecycle_manager._on_hand_preference_changed(hand_preference)

    def on_text_to_sign_play(self) -> None:
        """Handle text-to-sign play button click"""
        self.ui_behavior_manager.on_text_to_sign_play()

    def get_sign_language_info(self, text: str) -> str:
        """Get detailed sign language information for a word or phrase"""
        return self.ui_behavior_manager.get_sign_language_info(text)

    def _get_single_word_info(self, word: str) -> str:
        """Get sign language information for a single word"""
        return self.ui_behavior_manager._get_single_word_info(word)

    def _update_learning_progress(self, text: str) -> None:
        """Update learning progress for a word or phrase"""
        self.learning_progress_manager._update_learning_progress(text)

    def _on_learn_requested(self) -> None:
        """Handle learn button click in learning mode"""
        self.learning_progress_manager._on_learn_requested()

    def _on_clear_requested(self) -> None:
        """Handle clear button click in learning mode"""
        self.learning_progress_manager._on_clear_requested()

    def update_ui(self) -> None:
        """Update the UI to reflect the current mode"""
        self.ui_behavior_manager.update_ui()

    def update_fonts(self) -> None:
        """Update fonts - not needed as fonts are set during
        initialization"""
        self.ui_behavior_manager.update_fonts()

    def clear_content(self) -> None:
        """Clear all content in this mode"""
        self.ui_behavior_manager.clear_content()

    def get_settings(self) -> Dict[str, Any]:
        """Get mode-specific settings"""
        return self.learning_progress_manager.get_settings()

    def get_learning_progress(self) -> Dict[str, Dict[str, Any]]:
        """Get a copy of the learning progress"""
        return self.learning_progress_manager.get_learning_progress()

    def get_lesson_suggestions(self) -> List[str]:
        """Get lesson suggestions based on learning progress"""
        return self.learning_progress_manager.get_lesson_suggestions()

    def activate(self) -> None:
        """Activate the learning mode"""
        self.mode_lifecycle_manager.activate()

    def deactivate(self) -> None:
        """Deactivate the learning mode"""
        self.mode_lifecycle_manager.deactivate()

    def _restore_hand_preference_visual_state(self) -> None:
        """Restore the visual state of hand preference buttons"""
        self.mode_lifecycle_manager._restore_hand_preference_visual_state()

    def _force_layout_stability(self) -> None:
        """Force layout stability by updating the layout"""
        try:
            # Force layout update if learning widget exists
            if hasattr(self, "learning_widget") and self.learning_widget:
                self.learning_widget.updateGeometry()
                self.learning_widget.update()
        except Exception as e:
            self.logger.error(f"Error forcing layout stability: {e}")
