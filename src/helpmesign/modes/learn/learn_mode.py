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
from ..base_mode import BaseMode


class LearnMode(BaseMode):
    """Learn Sign Language mode - character selection and sign display"""

    def __init__(self, main_window, environment: str = "dev"):
        # Initialize font attributes before calling parent __init__
        # Get current font size and family once and store them
        from src.helpmesign.utils.font_manager import get_font_manager
        from src.helpmesign.utils.theme_manager import get_font_size

        self.current_font_size = get_font_size()
        # Use font manager to get proper Roboto font family
        font_manager = get_font_manager()
        self.current_font_family = font_manager._get_current_font_family()

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
        layout.setSpacing(15)  # Reduced spacing for better layout

        # Hand preference selector - innovative icon-based design
        hand_selector_layout = QHBoxLayout()
        hand_selector_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Add stretch first to push buttons to the right
        hand_selector_layout.addStretch()

        # Hand preference icons
        self.right_hand_btn = QPushButton("🖐️")
        self.left_hand_btn = QPushButton("🤚")

        # Style the hand preference buttons with better visual feedback
        hand_button_style = """
            QPushButton {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 8px;
                font-size: 20px;
                min-width: 40px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #dee2e6;
            }
            QPushButton:pressed {
                background-color: #0056b3;
                border-color: #0056b3;
                color: white;
            }
            QPushButton[selected="true"] {
                background-color: #28a745;
                border-color: #28a745;
                color: white;
                border-width: 4px;
                font-weight: bold;
            }
        """

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

        # DEBUG: Commented out style updates to debug override issue
        # # Force style update to ensure visual state is applied
        # self.right_hand_btn.style().unpolish(self.right_hand_btn)
        # self.right_hand_btn.style().polish(self.right_hand_btn)
        # self.left_hand_btn.style().unpolish(self.left_hand_btn)
        # self.left_hand_btn.style().polish(self.left_hand_btn)
        #
        # # Force a repaint to ensure visual state is visible
        # self.right_hand_btn.update()
        # self.left_hand_btn.update()

        # Connect hand preference buttons
        self.right_hand_btn.clicked.connect(lambda: self._set_hand_preference("right"))
        self.left_hand_btn.clicked.connect(lambda: self._set_hand_preference("left"))

        hand_selector_layout.addWidget(self.right_hand_btn)
        hand_selector_layout.addWidget(self.left_hand_btn)

        layout.addLayout(hand_selector_layout)

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

    def create_language_selector(self):
        """Create the language selection component"""
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFont
        from PySide6.QtWidgets import (
            QComboBox,
            QFrame,
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QPushButton,
            QScrollArea,
            QVBoxLayout,
            QWidget,
        )

        from ...utils.language_loader import get_all_languages, get_language_categories

        # Create language selector group
        language_group = QGroupBox(get_text("ui.language_selection.title"))
        language_group.setFont(
            QFont(
                self.current_font_family, self.current_font_size - 1, QFont.Weight.Bold
            )
        )
        language_group.setStyleSheet(
            """
            QGroupBox {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
        )

        layout = QVBoxLayout(language_group)
        layout.setSpacing(10)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(
            get_text("ui.language_selection.search_placeholder")
        )
        self.search_box.textChanged.connect(self.on_search_changed)
        self.search_box.setStyleSheet(
            """
            QLineEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """
        )
        layout.addWidget(self.search_box)

        # Category selector
        self.category_combo = QComboBox()
        self.category_combo.addItem(
            get_text("ui.language_selection.category_popular"), "popular"
        )
        self.category_combo.addItem(
            get_text("ui.language_selection.category_beginner"), "beginner"
        )
        self.category_combo.addItem(
            get_text("ui.language_selection.category_intermediate"), "intermediate"
        )
        self.category_combo.addItem(
            get_text("ui.language_selection.category_advanced"), "advanced"
        )
        self.category_combo.addItem(
            get_text("ui.language_selection.category_all"), "all"
        )
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        self.category_combo.setStyleSheet(
            """
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #6c757d;
            }
        """
        )
        layout.addWidget(self.category_combo)

        # Language list area
        self.language_list_area = QScrollArea()
        self.language_list_area.setWidgetResizable(True)
        self.language_list_area.setMaximumHeight(
            280
        )  # Increased height for better space utilization
        self.language_list_area.setStyleSheet(
            """
            QScrollArea {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }
            QScrollBar:vertical {
                background-color: #f8f9fa;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #ced4da;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #adb5bd;
            }
        """
        )

        # Language list widget
        self.language_list_widget = QWidget()
        self.language_list_layout = QVBoxLayout(self.language_list_widget)
        self.language_list_layout.setSpacing(
            3
        )  # Reduced spacing for more compact layout
        self.language_list_layout.setContentsMargins(4, 4, 4, 4)  # Reduced margins

        self.language_list_area.setWidget(self.language_list_widget)
        layout.addWidget(self.language_list_area)

        # Initialize language data
        self.languages = get_all_languages()
        self.categories = get_language_categories()
        self.selected_language = None
        self.filtered_languages = []

        # Populate initial language list
        self.populate_language_list("popular")

        return language_group

    def populate_language_list(self, category: str):
        """Populate the language list based on category"""
        # Clear existing items
        for i in reversed(range(self.language_list_layout.count())):
            self.language_list_layout.itemAt(i).widget().setParent(None)

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

        # Create language buttons
        for language in languages:
            btn = self.create_language_button(language)
            self.language_list_layout.addWidget(btn)

        # Add stretch to push buttons to top
        self.language_list_layout.addStretch()

    def create_language_button(self, language: dict):
        """Create a button for a language with enhanced display"""
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

        # Format button text with just flag and code
        button_text = f"{flag} {code}"

        btn = QPushButton(button_text)
        btn.setCheckable(True)
        btn.setProperty("language_code", code)
        btn.setProperty("language_data", language)
        btn.clicked.connect(lambda: self.on_language_selected(language))

        # Style the button with compact, professional design using Roboto font
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 6px 8px;
                text-align: left;
                font-family: "{self.current_font_family}";
                font-size: 11px;
                font-weight: 500;
                color: #495057;
                min-height: 28px;
                line-height: 1.1;
            }}
            QPushButton:hover {{
                background-color: #f8f9fa;
                border-color: #007bff;
            }}
            QPushButton:checked {{
                background-color: #007bff;
                color: white;
                border-color: #0056b3;
                font-weight: 600;
            }}
            QPushButton:pressed {{
                background-color: #0056b3;
            }}
        """
        )

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

    def on_search_changed(self, text: str):
        """Handle search text changes"""
        from ...utils.language_loader import search_languages

        if text.strip():
            # Search in all languages
            search_results = search_languages(text)
            self.populate_search_results(search_results)
        else:
            # Show current category
            current_category = self.category_combo.currentData()
            self.populate_language_list(current_category)

    def populate_search_results(self, languages: list):
        """Populate language list with search results"""
        # Clear existing items
        for i in reversed(range(self.language_list_layout.count())):
            item = self.language_list_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        self.filtered_languages = languages

        # Create language buttons for search results
        for language in languages:
            btn = self.create_language_button(language)
            self.language_list_layout.addWidget(btn)

        # Add stretch to push buttons to top
        self.language_list_layout.addStretch()

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

        # Sign title
        self.sign_title = QLabel("Sign Language")
        self.sign_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sign_title.setStyleSheet(
            """
            QLabel {
                font-weight: bold;
                font-size: 16px;
                color: #333;
                margin-bottom: 10px;
            }
        """
        )
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
        """Set hand preference and update UI"""
        self.current_hand_preference = hand_preference

        # Update button states
        if hand_preference == "right":
            self.right_hand_btn.setProperty("selected", True)
            self.left_hand_btn.setProperty("selected", False)
        else:
            self.right_hand_btn.setProperty("selected", False)
            self.left_hand_btn.setProperty("selected", True)

        # DEBUG: Commented out style updates to debug override issue
        # # Force style update with more aggressive approach
        # self.right_hand_btn.style().unpolish(self.right_hand_btn)
        # self.right_hand_btn.style().polish(self.right_hand_btn)
        # self.left_hand_btn.style().unpolish(self.left_hand_btn)
        # self.left_hand_btn.style().polish(self.left_hand_btn)
        #
        # # Force immediate repaint
        # self.right_hand_btn.repaint()
        # self.left_hand_btn.repaint()
        #
        # # Force parent widget to update
        # if hasattr(self, 'learning_widget') and self.learning_widget:
        #     self.learning_widget.update()

        # Save hand preference to config
        try:
            from src.helpmesign.core.startup import set_hand_preference

            set_hand_preference(hand_preference)
        except Exception as e:
            # Log error but don't crash the application
            if hasattr(self, "logger"):
                self.logger.error(f"Failed to save hand preference to config: {e}")

        # Update sign display if we have a current character
        if (
            hasattr(self, "current_character")
            and self.current_character
            and self.current_char_type
        ):
            self.update_sign_display(self.current_character, self.current_char_type)

    def _on_hand_preference_changed(self, hand_preference: str) -> None:
        """Handle hand preference changes and update sign display"""
        # Update the sign display if we have a current character
        if self.current_character and self.current_char_type:
            self.update_sign_display(self.current_character, self.current_char_type)

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
        # DEBUG: Disabled font updates to debug hand preference override issue
        # Update fonts to match current font size setting
        # self.update_fonts()
        pass

    def update_fonts(self) -> None:
        """Update fonts following the defined process:
        Only update fonts in currently visible window, never update button fonts
        """
        from src.helpmesign.utils.font_manager import get_font_manager
        from src.helpmesign.utils.theme_manager import get_font_size

        try:
            # Only update fonts if this mode is currently visible
            if (
                not hasattr(self, "learning_widget")
                or not self.learning_widget.isVisible()
            ):
                return

            # Update stored font size and family using proper font manager
            self.current_font_size = get_font_size()
            font_manager = get_font_manager()
            self.current_font_family = font_manager._get_current_font_family()

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

            # Hand preference group moved to settings window

            # Sign description removed for better space utilization

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

        # DEBUG: Disabled layout stability to debug hand preference override issue
        # Force a layout update after a short delay to ensure all font updates are complete
        from PySide6.QtCore import QTimer

        # QTimer.singleShot(100, self._force_layout_stability)
        # DEBUG: Commented out hand preference restoration to debug override issue
        # # Ensure hand preference visual state is properly restored
        # QTimer.singleShot(50, self._restore_hand_preference_visual_state)

    def deactivate(self) -> None:
        """Deactivate this mode - called when switching away from this mode"""
        # Switch back to default content
        self.main_window.content_area.setCurrentWidget(self.main_window.default_content)

    def _restore_hand_preference_visual_state(self) -> None:
        """Restore the visual state of hand preference buttons based on saved preference"""
        try:
            if hasattr(self, "right_hand_btn") and hasattr(self, "left_hand_btn"):
                # Get current preference from config
                try:
                    from src.helpmesign.core.startup import get_hand_preference

                    current_pref = get_hand_preference()
                except Exception:
                    current_pref = "right"  # Default fallback

                # Update internal state
                self.current_hand_preference = current_pref

                # Set button properties
                if current_pref == "left":
                    self.left_hand_btn.setProperty("selected", True)
                    self.right_hand_btn.setProperty("selected", False)
                else:
                    self.right_hand_btn.setProperty("selected", True)
                    self.left_hand_btn.setProperty("selected", False)

                    # DEBUG: Commented out style updates to debug override issue
                # # Force style update with more aggressive approach
                # self.right_hand_btn.style().unpolish(self.right_hand_btn)
                # self.right_hand_btn.style().polish(self.right_hand_btn)
                # self.left_hand_btn.style().unpolish(self.left_hand_btn)
                # self.left_hand_btn.style().polish(self.left_hand_btn)
                #
                # # Force immediate repaint
                # self.right_hand_btn.repaint()
                # self.left_hand_btn.repaint()
                #
                # # Force parent widget to update
                # if hasattr(self, 'learning_widget') and self.learning_widget:
                #     self.learning_widget.update()

                # Log success if logger is available
                if hasattr(self, "logger"):
                    self.logger.debug(
                        f"Hand preference visual state restored: {current_pref}"
                    )
        except Exception as e:
            # Log error if logger is available
            if hasattr(self, "logger"):
                self.logger.error(f"Error restoring hand preference visual state: {e}")

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
