"""
Learn Sign Language mode implementation
Provides character selection and sign display layout
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout
    from PySide6.QtGui import QFont

from ...utils.language_manager import get_text
from ...utils.sign_language_loader import get_sign_language_loader
from ...utils.theme_manager import get_theme_style
from ..base_mode import BaseMode


class LearnMode(BaseMode):
    """Learn Sign Language mode - character selection and sign display"""

    def __init__(self, main_window, environment: str = "dev"):
        # Initialize logger
        import logging

        self.logger = logging.getLogger(__name__)

        # Get theme and font information from main window or config
        self._initialize_theme_and_font_info(main_window, environment)

        # Initialize character tracking variables
        self.current_character: Optional[str] = None
        self.current_char_type: Optional[str] = None

        # Initialize learning progress tracking
        self.learning_progress: Dict[str, Dict[str, Any]] = {}
        self.lesson_history: List[Dict[str, Any]] = []
        self.current_lesson: Optional[Dict[str, Any]] = None

        # Initialize sign language loader
        self.sign_loader = get_sign_language_loader()
        self.current_language = "ASL"  # Default to ASL
        self.current_category = "all"  # Track current category

        # Now call parent __init__ which will call setup_ui()
        super().__init__(main_window, environment)

    def _initialize_theme_and_font_info(self, main_window, environment: str) -> None:
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
                from src.helpmesign.core.startup import get_all_settings

                settings = get_all_settings(environment)
                self.current_theme = settings.get("theme", "Light")
                self.current_font_size = settings.get("font_size", 12)
                self.logger.debug(
                    f"Using theme and font from config: {self.current_theme}, {self.current_font_size}"
                )

            # Get effective theme (handle System theme)
            self.effective_theme = self._get_effective_theme_from_theme(
                self.current_theme
            )

            # Get font family from theme manager
            from src.helpmesign.utils.theme_manager import get_font_family

            self.current_font_family = get_font_family()

        except Exception as e:
            self.logger.error(f"Error initializing theme and font info: {e}")
            # Fallback to defaults
            self.current_theme = "Light"
            self.effective_theme = "Light"
            self.current_font_size = 12
            self.current_font_family = "Roboto"

    def _get_effective_theme_from_theme(self, theme: str) -> str:
        """Get effective theme (Dark/Light) from theme name"""
        if theme == "System":
            # Detect system theme
            try:
                from src.helpmesign.utils.theme_manager import get_theme_manager

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
            return "Light"

    def get_mode_name(self) -> str:
        """Get the display name for this mode"""
        return get_text("modes.learn.name")

    def get_mode_description(self) -> str:
        """Get mode description"""
        return "Learn sign language with interactive lessons and practice"

    def setup_ui(self) -> None:
        """Set up the mode-specific UI components"""
        # Create the main layout
        self.create_learning_layout()

        # Set up behavior and event handlers
        self.setup_behavior()

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

        # Main horizontal layout (remove outer padding/borders)
        main_layout = QHBoxLayout(self.learning_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)

        # Left panel - Sign display with language selector
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
            QHBoxLayout,
            QLabel,
            QPushButton,
            QVBoxLayout,
            QWidget,
        )

        from ...utils.theme_manager import get_theme_manager

        # Initialize button dictionaries early to prevent AttributeError
        self.alphabet_buttons = {}
        self.number_buttons = {}

        # Create panel with visible border (card-like)
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.Box)

        # Get theme-aware panel styling from theme manager
        panel_style = get_theme_style("learn_mode_panel")
        panel.setStyleSheet(panel_style)

        layout = QVBoxLayout(panel)
        layout.setSpacing(15)  # Reduced spacing for better layout

        # Hand preference selector - innovative icon-based design
        hand_selector_layout = QHBoxLayout()
        hand_selector_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Add stretch first to push buttons to the right
        hand_selector_layout.addStretch()

        # Hand preference icons
        self.right_hand_btn = QPushButton("🖐️")
        self.left_hand_btn = QPushButton("🤚")

        # Get theme-aware hand button styling from theme manager with dynamic font size
        theme_manager = get_theme_manager()
        hand_button_style = theme_manager.get_complete_style(
            "learn_mode_hand_button", include_font_size=True
        )

        self.right_hand_btn.setStyleSheet(hand_button_style)
        self.left_hand_btn.setStyleSheet(hand_button_style)

        # Set tooltips
        self.right_hand_btn.setToolTip("Right Hand Signs")
        self.left_hand_btn.setToolTip("Left Hand Signs")

        # Load hand preference from config (default to right hand)
        try:
            from src.helpmesign.core.startup import get_hand_preference

            self.current_hand_preference = get_hand_preference()
        except Exception:
            self.current_hand_preference = "right"  # Default fallback

        # Set initial button selection based on loaded preference
        if self.current_hand_preference == "left":
            self.left_hand_btn.setProperty("selected", True)
            self.right_hand_btn.setProperty("selected", False)
        else:
            self.right_hand_btn.setProperty("selected", True)
            self.left_hand_btn.setProperty("selected", False)

        # Force style update to ensure visual state is applied
        self.right_hand_btn.style().unpolish(self.right_hand_btn)
        self.right_hand_btn.style().polish(self.right_hand_btn)
        self.left_hand_btn.style().unpolish(self.left_hand_btn)
        self.left_hand_btn.style().polish(self.left_hand_btn)

        # Force a repaint to ensure visual state is visible
        self.right_hand_btn.update()
        self.left_hand_btn.update()

        # Connect hand preference buttons
        self.right_hand_btn.clicked.connect(lambda: self._set_hand_preference("right"))
        self.left_hand_btn.clicked.connect(lambda: self._set_hand_preference("left"))

        hand_selector_layout.addWidget(self.right_hand_btn)
        hand_selector_layout.addWidget(self.left_hand_btn)

        layout.addLayout(hand_selector_layout)

        # Create a container for character buttons that can be updated dynamically
        self.character_container = QWidget()
        self.character_layout = QGridLayout(self.character_container)
        self.character_layout.setSpacing(16)  # Fixed spacing between buttons
        self.character_layout.setContentsMargins(16, 16, 16, 16)  # Fixed margins
        self.character_layout.setRowStretch(0, 0)  # Prevent row stretching
        self.character_layout.setColumnStretch(0, 0)  # Prevent column stretching

        # Add the character container to the main layout
        layout.addWidget(self.character_container)
        layout.addStretch(1)  # Add stretch to prevent grid from expanding

        # Store the panel for later updates
        self.selection_panel = panel

        return panel

    def update_character_buttons(self):
        """Update the character buttons based on the selected language and hand preference"""
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QLabel, QPushButton

        from ...utils.sign_language_loader import get_sign_language_loader
        from ...utils.theme_manager import get_theme_manager

        # Prevent excessive updates
        if (
            hasattr(self, "_updating_character_buttons")
            and self._updating_character_buttons
        ):
            return

        self._updating_character_buttons = True

        try:
            # Safety check - ensure character layout exists
            if not hasattr(self, "character_layout"):
                self.logger.warning(
                    "Character layout not initialized yet, skipping character button update"
                )
                return

            # Ensure button dictionaries exist
            if not hasattr(self, "alphabet_buttons"):
                self.alphabet_buttons = {}
            if not hasattr(self, "number_buttons"):
                self.number_buttons = {}

            # Safely clear existing buttons without deleteLater() to avoid memory corruption
            for button in self.alphabet_buttons.values():
                if button and button.parent():
                    button.setParent(None)
            for button in self.number_buttons.values():
                if button and button.parent():
                    button.setParent(None)
            self.alphabet_buttons.clear()
            self.number_buttons.clear()

            # Safely clear the layout without deleteLater()
            while self.character_layout.count():
                child = self.character_layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)

            # Get the selected language and hand preference
            selected_language = "ASL"  # Default fallback
            if hasattr(self, "selected_language") and self.selected_language:
                selected_language = self.selected_language.get("code", "ASL")

            hand_preference = self.current_hand_preference

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
                self.character_layout.addWidget(error_label, 0, 0)
                return

            # Extract characters from the sign data
            alphabet_chars = list(alphabet_signs.keys())
            number_chars = list(number_signs.keys())

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
                self.character_layout.addWidget(error_label, 0, 0)
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
                        lambda checked, c=char: self.on_alphabet_selected(c)
                    )
                    self.alphabet_buttons[char] = btn
                else:
                    btn.clicked.connect(
                        lambda checked, c=char: self.on_number_selected(c)
                    )
                    self.number_buttons[char] = btn

                self.character_layout.addWidget(btn, row, col)

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
            self.character_layout.addWidget(error_label, 0, 0)
        finally:
            self._updating_character_buttons = False

    def create_language_selector(self):
        """Create a clean, modern language selection component"""
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFont

        # Create a framed container JUST around the language selection area
        from PySide6.QtWidgets import (
            QComboBox,
            QFrame,
            QGridLayout,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QListWidget,
            QListWidgetItem,
            QMenu,
            QPushButton,
            QScrollArea,
            QVBoxLayout,
            QWidget,
        )

        from ...utils.language_loader import get_all_languages, get_language_categories
        from ...utils.theme_manager import get_theme_manager

        container = QFrame()
        container.setFrameStyle(QFrame.Shape.Box)
        container.setStyleSheet(get_theme_style("learn_mode_panel"))

        layout = QVBoxLayout(container)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # Theme manager will be used for component styles below
        theme_manager = get_theme_manager()

        # Search and filter row
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(12)  # Increased spacing

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(
            get_text("ui.language_selection.search_placeholder")
        )
        self.search_box.textChanged.connect(self.on_search_changed)

        # Get theme-aware search box styling from theme manager
        search_style = theme_manager.get_complete_style(
            "learn_mode_search_box", include_font_size=True
        )

        self.search_box.setStyleSheet(search_style)
        filter_layout.addWidget(self.search_box, 3)  # Takes 3/4 of space

        # Category selector - using QPushButton with custom popup menu
        # Create a container widget for the button with proper layout
        category_container = QWidget()
        category_layout = QHBoxLayout(category_container)
        category_layout.setContentsMargins(0, 0, 0, 0)
        category_layout.setSpacing(0)

        # Create the button with text and arrow in separate layout
        self.category_button = QPushButton()
        self.category_button.setObjectName("categoryButton")
        self.category_button.clicked.connect(self.show_category_menu)

        # Create inner layout for text and arrow
        button_layout = QHBoxLayout(self.category_button)
        button_layout.setContentsMargins(8, 4, 8, 4)
        button_layout.setSpacing(8)

        # Text label
        self.category_text_label = QLabel(
            get_text("ui.language_selection.category_all")
        )
        self.category_text_label.setObjectName("categoryTextLabel")
        button_layout.addWidget(self.category_text_label, 1)  # Takes available space

        # Arrow label
        self.category_arrow_label = QLabel("▼")
        self.category_arrow_label.setObjectName("categoryArrowLabel")
        button_layout.addWidget(self.category_arrow_label, 0)  # Fixed size

        # Add the button to the container
        category_layout.addWidget(self.category_button)

        # Create the popup menu
        self.category_menu = QMenu(self.category_button)

        # Add menu items
        self.category_actions = {}
        categories = [
            (get_text("ui.language_selection.category_all"), "all"),
            (get_text("ui.language_selection.category_popular"), "popular"),
            (get_text("ui.language_selection.category_beginner"), "beginner"),
            (get_text("ui.language_selection.category_intermediate"), "intermediate"),
            (get_text("ui.language_selection.category_advanced"), "advanced"),
        ]

        for display_name, category_value in categories:
            action = self.category_menu.addAction(display_name)
            action.setData(category_value)
            self.category_actions[category_value] = action
            action.triggered.connect(
                lambda checked, cat=category_value: self.on_category_selected(cat)
            )

            # Get theme-aware category button and menu styling from theme manager
        category_button_style = get_theme_style("learn_mode_category_button")
        category_menu_style = get_theme_style("learn_mode_category_menu")

        self.category_button.setStyleSheet(category_button_style)
        self.category_menu.setStyleSheet(category_menu_style)

        filter_layout.addWidget(category_container, 1)  # Takes 1/4 of space

        layout.addLayout(filter_layout)

        # Language grid area - clean and simple (keep content borderless)
        self.language_list_area = QScrollArea()
        self.language_list_area.setWidgetResizable(True)
        self.language_list_area.setMaximumHeight(220)
        # Keep default frame on the outer panel; the scroll area itself remains minimal
        self.language_list_area.setFrameShape(QFrame.Shape.NoFrame)
        # Never show horizontal scrollbar and ensure transparent viewport
        self.language_list_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        try:
            from PySide6.QtGui import QColor, QPalette

            palette = self.language_list_area.viewport().palette()
            palette.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0, 0))
            self.language_list_area.viewport().setPalette(palette)
            self.language_list_area.viewport().setAutoFillBackground(False)
        except Exception:
            pass

        # Connect resize event to recalculate grid layout
        self.language_list_area.resizeEvent = self._on_language_area_resize

        # Get theme-aware scroll area styling from theme manager
        scroll_area_style = get_theme_style("learn_mode_scroll_area")
        self.language_list_area.setStyleSheet(scroll_area_style)

        # Language grid widget (transparent background)
        self.language_list_widget = QWidget()
        self.language_list_widget.setObjectName("languageListWidget")
        self.language_list_widget.setStyleSheet("background: transparent;")
        if hasattr(self.language_list_widget, "setAutoFillBackground"):
            self.language_list_widget.setAutoFillBackground(False)
        self.language_list_layout = QGridLayout(self.language_list_widget)
        self.language_list_layout.setSpacing(
            8
        )  # Increased spacing for better visual separation
        self.language_list_layout.setContentsMargins(
            0, 0, 0, 0
        )  # Remove inner margins to avoid horizontal scroll

        self.language_list_area.setWidget(self.language_list_widget)
        layout.addWidget(self.language_list_area)

        # Initialize language data
        self.languages = get_all_languages()
        self.categories = get_language_categories()
        self.selected_language = None
        self.filtered_languages = []

        # Populate initial language list
        self.populate_language_list("all")

        # Load saved language selection
        self.load_saved_language_selection()

        return container

    def populate_language_list(self, category: str):
        """Populate the language list based on category using grid layout"""
        # Prevent excessive recalculations
        if hasattr(self, "_populating_languages") and getattr(
            self, "_populating_languages", False
        ):
            return

        self._populating_languages = True

        try:
            # Clear existing items
            for i in reversed(range(self.language_list_layout.count())):
                item = self.language_list_layout.itemAt(i)
                if item and item.widget():
                    item.widget().setParent(None)

            # Get languages for category
            if category == "popular":
                languages = self.categories.get("popular", [])
            elif category == "beginner":
                languages = self.categories.get("beginner", [])
            elif category == "intermediate":
                languages = self.categories.get("intermediate", [])
            elif category == "advanced":
                languages = self.categories.get("advanced", [])
            else:
                languages = self.categories.get("all", [])

            self.filtered_languages = languages
            self.current_category = category
        finally:
            self._populating_languages = False

        # Calculate optimal number of columns based on available width
        # Get actual available width from the scroll area, accounting for scrollbar
        available_width = (
            self.language_list_area.width()
            if self.language_list_area.width() > 0
            else 600
        )
        scrollbar_width = 16  # Approximate scrollbar width
        effective_width = available_width - scrollbar_width

        button_width = 70  # Target button width
        spacing = 8  # Grid spacing
        margins = 8  # Total margins

        # Calculate optimal columns: (effective_width - margins) / (button_width + spacing)
        # Allow more columns to better utilize space
        optimal_columns = max(
            4, min(8, (effective_width - margins) // (button_width + spacing))
        )

        # Create language buttons in a grid layout with optimal columns
        for i, language in enumerate(languages):
            btn = self.create_language_button(language)

            # Preserve checked state for the currently selected language when the grid is rebuilt
            try:
                selected = getattr(self, "selected_language", None)
                if selected and language.get("code") == selected.get("code"):
                    btn.setChecked(True)
            except Exception:
                pass

            row = i // optimal_columns
            col = i % optimal_columns
            self.language_list_layout.addWidget(btn, row, col)

        # Add stretch factors to make buttons expand and fill available space
        for col in range(optimal_columns):
            self.language_list_layout.setColumnStretch(col, 1)

    def _on_language_area_resize(self, event):
        """Handle resize events to recalculate grid layout"""
        # Call the original resize event handler
        from PySide6.QtWidgets import QScrollArea

        QScrollArea.resizeEvent(self.language_list_area, event)

        # Only recalculate if we have languages loaded and the resize is significant
        if hasattr(self, "filtered_languages") and self.filtered_languages:
            # Use a timer to debounce rapid resize events
            if not hasattr(self, "_resize_timer"):
                from PySide6.QtCore import QTimer

                self._resize_timer = QTimer()
                self._resize_timer.setSingleShot(True)
                self._resize_timer.timeout.connect(self._recalculate_grid_layout)

            # Reset the timer to prevent excessive recalculations
            self._resize_timer.start(100)  # 100ms delay

    def _recalculate_grid_layout(self):
        """Recalculate the grid layout based on current width"""
        if hasattr(self, "current_category"):
            self.populate_language_list(self.current_category)

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
        btn.clicked.connect(lambda: self.on_language_selected(language))

        # Get theme-aware language button styling from theme manager
        language_button_style = get_theme_style("learn_mode_language_button")

        # Replace font-family placeholder with actual font family
        language_button_style = language_button_style.replace(
            'font-family: "Roboto"', f'font-family: "{self.current_font_family}"'
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
        """Handle language selection"""
        self.selected_language = language

        # Update button states
        for i in range(self.language_list_layout.count()):
            item = self.language_list_layout.itemAt(i)
            if item.widget():
                btn = item.widget()
                if btn.property("language_code") == language.get("code"):
                    btn.setChecked(True)
                else:
                    btn.setChecked(False)

        # Update sign display title to show selected language flag and code
        flag = language.get("flag", "🌐")
        code = language.get("code", "Unknown")
        self.sign_title.setText(f"{flag} {code}")

        # Change the sign language for the sign display
        language_code = language.get("code", "ASL")
        self.change_sign_language(language_code)

        # Save language selection to configuration
        self.save_language_selection(language_code)

        # Update character buttons based on new language
        self.update_character_buttons()

    def save_language_selection(self, language_code: str) -> None:
        """Save the selected language to user configuration"""
        try:
            from ...core.startup import get_all_settings, save_all_settings

            # Get current settings
            current_settings = get_all_settings(self.environment)

            # Update the language selection
            current_settings["selected_language"] = language_code

            # Save the updated settings
            if save_all_settings(current_settings, self.environment):
                self.logger.info(f"Language selection saved to config: {language_code}")
            else:
                self.logger.error("Failed to save language selection to config")

        except Exception as e:
            self.logger.error(f"Error saving language selection: {e}")

    def load_saved_language_selection(self) -> None:
        """Load the saved language selection from configuration"""
        # Prevent multiple calls
        if hasattr(self, "_language_loaded") and getattr(
            self, "_language_loaded", False
        ):
            return

        try:
            from ...core.startup import get_all_settings

            # Get current settings
            current_settings = get_all_settings(self.environment)

            saved_language = current_settings.get("selected_language", "ASL")
            self.logger.info(f"Loaded saved language selection: {saved_language}")

            # Find and select the saved language
            self.select_language_by_code(saved_language)

            self._language_loaded = True

        except Exception as e:
            self.logger.error(f"Error loading saved language selection: {e}")
            # Default to ASL if there's an error
            self.select_language_by_code("ASL")

    def select_language_by_code(self, language_code: str) -> None:
        """Select a language by its code"""
        try:
            # Find the language in the current list
            for i in range(self.language_list_layout.count()):
                item = self.language_list_layout.itemAt(i)
                if item and item.widget():
                    btn = item.widget()
                    if btn.property("language_code") == language_code:
                        # Simulate clicking the button
                        btn.setChecked(True)
                        self.on_language_selected(btn.property("language_data"))
                        return

            # If not found in current list, try to find it in all languages
            from ...utils.language_loader import get_all_languages

            all_languages = get_all_languages()

            for language in all_languages:
                if language.get("code") == language_code:
                    self.on_language_selected(language)
                    return

            # If still not found, default to ASL
            self.logger.warning(
                f"Language {language_code} not found, defaulting to ASL"
            )
            for language in all_languages:
                if language.get("code") == "ASL":
                    self.on_language_selected(language)
                    return

        except Exception as e:
            self.logger.error(f"Error selecting language by code: {e}")

    def on_search_changed(self, text: str):
        """Handle search text changes"""
        from ...utils.language_loader import search_languages

        if text.strip():
            # Search in all languages
            search_results = search_languages(text)
            self.populate_search_results(search_results)
        else:
            # Show current category
            self.populate_language_list(self.current_category)

    def populate_search_results(self, languages: list):
        """Populate language list with search results using grid layout"""
        # Clear existing items
        for i in reversed(range(self.language_list_layout.count())):
            item = self.language_list_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        self.filtered_languages = languages

        # Create language buttons for search results in a grid layout (4 columns for better space utilization)
        columns = 4
        for i, language in enumerate(languages):
            btn = self.create_language_button(language)
            row = i // columns
            col = i % columns
            self.language_list_layout.addWidget(btn, row, col)

    def show_category_menu(self):
        """Show the category selection menu"""
        try:
            # Position the menu below the button
            button_rect = self.category_button.rect()
            menu_pos = self.category_button.mapToGlobal(button_rect.bottomLeft())
            self.category_menu.popup(menu_pos)
        except Exception as e:
            self.logger.error(f"Error showing category menu: {e}")

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
            self.category_text_label.setText(display_name)

            # Update current category
            self.current_category = category

            # Populate language list
            self.populate_language_list(category)

        except Exception as e:
            self.logger.error(f"Error handling category selection: {e}")
            self.populate_language_list("all")

    def on_category_changed(self, category_text: str):
        """Handle category selection changes"""
        # Find the category key
        category_map = {
            get_text("ui.language_selection.category_popular"): "popular",
            get_text("ui.language_selection.category_beginner"): "beginner",
            get_text("ui.language_selection.category_intermediate"): "intermediate",
            get_text("ui.language_selection.category_advanced"): "advanced",
            get_text("ui.language_selection.category_all"): "all",
        }

        category = category_map.get(category_text, "popular")
        self.populate_language_list(category)

    def create_sign_display_panel(self):
        """Create the right panel for sign display with language selector"""
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFont
        from PySide6.QtWidgets import (
            QButtonGroup,
            QComboBox,
            QFrame,
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QPushButton,
            QRadioButton,
            QScrollArea,
            QVBoxLayout,
            QWidget,
        )

        from ...utils.theme_manager import get_theme_manager

        # Create panel with visible border (card-like)
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.Box)

        # Get theme-aware panel styling from theme manager
        panel_style = get_theme_style("learn_mode_panel")
        panel.setStyleSheet(panel_style)

        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        # Sign title
        self.sign_title = QLabel("Sign Language")
        self.sign_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Get theme-aware title styling from theme manager with dynamic font size
        theme_manager = get_theme_manager()
        title_style = theme_manager.get_complete_style(
            "learn_mode_title", include_font_size=True
        )

        self.sign_title.setStyleSheet(title_style)
        layout.addWidget(self.sign_title)

        # Sign display area
        self.sign_display_label = QLabel()
        self.sign_display_label.setMinimumSize(300, 300)

        # Get theme-aware display label styling from theme manager
        display_style = get_theme_style("learn_mode_sign_display")

        self.sign_display_label.setStyleSheet(display_style)
        self.sign_display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sign_display_label.setTextFormat(
            Qt.TextFormat.RichText
        )  # Enable HTML support
        self.sign_display_label.setWordWrap(True)  # Enable word wrapping
        self.sign_display_label.setText(
            get_text("ui.language_selection.sign_will_appear_here")
        )
        layout.addWidget(self.sign_display_label)

        # Hand preference moved to settings window

        # Language selector section
        language_group = self.create_language_selector()
        layout.addWidget(language_group)

        return panel

    def on_alphabet_selected(self, letter: str) -> None:
        """Handle alphabet letter selection"""
        # Update button styling
        self.update_button_selection(letter, self.alphabet_buttons)

        # Update sign display
        self.update_sign_display(letter, "letter")

    def on_number_selected(self, number: str) -> None:
        """Handle number selection"""
        # Update button styling
        self.update_button_selection(number, self.number_buttons)

        # Update sign display
        self.update_sign_display(number, "number")

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
        """Update the sign display area with actual SVG signs"""
        # Safety check - ensure sign display label exists
        if not hasattr(self, "sign_display_label") or self.sign_display_label is None:
            return

        # Store current character and type for hand preference changes
        self.current_character = character
        self.current_char_type = char_type

        # Get hand preference from local UI state
        hand_preference = getattr(self, "current_hand_preference", "right")

        # Load the sign data from our JSON files
        svg_data = self.sign_loader.get_sign_svg(
            self.current_language, character, hand_preference
        )
        instructions = self.sign_loader.get_sign_instructions(
            self.current_language, character, hand_preference
        )

        if svg_data and instructions:
            # Create HTML content with SVG and instructions
            html_content = f"""
            <div style="text-align: center; padding: 20px;">
                <div style="margin-bottom: 20px;">
                    {svg_data}
                </div>
                <div style="font-family: {self.current_font_family}; font-size: {self.current_font_size}px; color: #333;">
                    <h3 style="margin: 10px 0; color: #2c3e50;">{hand_preference.title()} Hand Sign</h3>
                    <p style="margin: 10px 0; color: #7f8c8d; font-style: italic;">{instructions}</p>
                    <p style="margin: 10px 0; color: #95a5a6; font-size: 0.9em;">Character: '{character}'</p>
                </div>
            </div>
            """

            # Set the HTML content
            self.sign_display_label.setText(html_content)
        else:
            # Fallback if sign not found
            fallback_text = f"""
            <div style="text-align: center; padding: 20px;">
                <div style="font-family: {self.current_font_family}; font-size: {self.current_font_size}px; color: #e74c3c;">
                    <h3>Sign Not Found</h3>
                    <p>No sign data available for '{character}' in {self.current_language}</p>
                    <p>Please check the sign language data files.</p>
                </div>
            </div>
            """
            self.sign_display_label.setText(fallback_text)

    def setup_behavior(self) -> None:
        """Set up mode-specific behavior and event handlers"""
        # Hand preference handling moved to settings window

        # Connect to main window signals if they exist
        if hasattr(self.main_window, "clear_requested"):
            self.main_window.clear_requested.connect(self._on_clear_requested)

        if hasattr(self.main_window, "process_requested"):
            self.main_window.process_requested.connect(self._on_learn_requested)

        # Connect to hand preference changes if main window supports it
        if hasattr(self.main_window, "update_hand_preference"):
            # Connect to the signal, not the method
            self.main_window.update_hand_preference.connect(
                self._on_hand_preference_changed
            )

    def _set_hand_preference(self, hand_preference: str) -> None:
        """Set the hand preference and update the UI"""
        try:
            # Preserve current selection so we can re-apply it after changing hand
            previously_selected_char = getattr(self, "current_character", None)
            previously_selected_type = getattr(self, "current_char_type", None)

            # Update internal state
            self.current_hand_preference = hand_preference

            # Update button visual state
            if hand_preference == "left":
                self.left_hand_btn.setProperty("selected", True)
                self.right_hand_btn.setProperty("selected", False)
            else:
                self.right_hand_btn.setProperty("selected", True)
                self.left_hand_btn.setProperty("selected", False)

            # Force style update
            self.right_hand_btn.style().unpolish(self.right_hand_btn)
            self.right_hand_btn.style().polish(self.right_hand_btn)
            self.left_hand_btn.style().unpolish(self.left_hand_btn)
            self.left_hand_btn.style().polish(self.left_hand_btn)

            # Save to configuration
            try:
                from src.helpmesign.core.startup import set_hand_preference

                set_hand_preference(hand_preference)
            except Exception as e:
                self.logger.warning(f"Could not save hand preference: {e}")

            # If a character is currently selected, keep it selected and refresh display
            if previously_selected_char and previously_selected_type:
                if previously_selected_type == "letter":
                    self.update_button_selection(
                        previously_selected_char, self.alphabet_buttons
                    )
                else:
                    self.update_button_selection(
                        previously_selected_char, self.number_buttons
                    )

                # Refresh the sign for the new hand preference
                self.update_sign_display(
                    previously_selected_char, previously_selected_type
                )
            else:
                # No selection to refresh; just notify handler
                self._on_hand_preference_changed(hand_preference)

        except Exception as e:
            self.logger.error(f"Error setting hand preference: {e}")

    def _on_hand_preference_changed(self, hand_preference: str) -> None:
        """Handle hand preference change"""
        try:
            # Update sign display if there's a current selection
            if hasattr(self, "sign_display_label") and self.sign_display_label:
                # Refresh the current sign display with new hand preference
                pass  # This will be handled by the character selection methods

        except Exception as e:
            self.logger.error(f"Error handling hand preference change: {e}")

    def change_sign_language(self, language: str) -> None:
        """Change the current sign language and update display"""
        self.current_language = language

        # Update the sign display if we have a current character
        if self.current_character and self.current_char_type:
            self.update_sign_display(self.current_character, self.current_char_type)

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
        # Call the main clear_content method to avoid duplication
        self.clear_content()

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
        if hasattr(self.main_window, "set_text_input"):
            self.main_window.set_text_input("")

        # Clear text output if main window has the method
        if hasattr(self.main_window, "set_text_output"):
            self.main_window.set_text_output("")

        # Update status using language configuration
        if hasattr(self.main_window, "set_status"):
            self.main_window.set_status(get_text("ui.status.cleared"))

        # Reset the sign display to default state using language configuration
        if hasattr(self, "sign_display_label"):
            self.sign_display_label.setText(
                get_text("ui.language_selection.sign_will_appear_here")
            )

        # Sign description removed for better space utilization

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
        """Activate the learning mode"""
        try:
            # Set the mode in the main window
            self.main_window.set_mode("learn")
            self.main_window.set_status("Learning mode activated")

            # Add the learning widget to the main window's content area
            if hasattr(self, "learning_widget") and self.learning_widget:
                if hasattr(self.main_window, "content_area"):
                    # Remove any existing learning widget
                    for i in range(self.main_window.content_area.count()):
                        widget = self.main_window.content_area.widget(i)
                        if widget == self.learning_widget:
                            self.main_window.content_area.removeWidget(widget)

                    # Add the learning widget to the content area
                    self.main_window.content_area.addWidget(self.learning_widget)
                    self.main_window.content_area.setCurrentWidget(self.learning_widget)

            # Load saved language selection and update character buttons (only once)
            if not hasattr(self, "_activated"):
                self.load_saved_language_selection()
                self.update_character_buttons()
                self._activated = True

            # Restore hand preference visual state
            self._restore_hand_preference_visual_state()

        except Exception as e:
            self.logger.error(f"Error activating learn mode: {e}")

    def deactivate(self) -> None:
        """Deactivate the learning mode"""
        try:
            # Remove the learning widget from the content area
            if hasattr(self, "learning_widget") and self.learning_widget:
                if hasattr(self.main_window, "content_area"):
                    self.main_window.content_area.removeWidget(self.learning_widget)

        except Exception as e:
            self.logger.error(f"Error deactivating learn mode: {e}")

    def _restore_hand_preference_visual_state(self) -> None:
        """Restore the visual state of hand preference buttons"""
        try:
            if hasattr(self, "right_hand_btn") and hasattr(self, "left_hand_btn"):
                # Reset both buttons
                self.right_hand_btn.setProperty("selected", False)
                self.left_hand_btn.setProperty("selected", False)

                # Apply the current preference
                if self.current_hand_preference == "left":
                    self.left_hand_btn.setProperty("selected", True)
                else:
                    self.right_hand_btn.setProperty("selected", True)

                # Force style update
                self.right_hand_btn.style().unpolish(self.right_hand_btn)
                self.right_hand_btn.style().polish(self.right_hand_btn)
                self.left_hand_btn.style().unpolish(self.left_hand_btn)
                self.left_hand_btn.style().polish(self.left_hand_btn)

        except Exception as e:
            self.logger.error(f"Error restoring hand preference visual state: {e}")

    def _force_layout_stability(self) -> None:
        """Force layout stability to prevent flickering"""
        pass
