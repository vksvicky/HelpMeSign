# Internationalization (i18n) System

## Overview

HelpMeSign now supports internationalization with a comprehensive language management system that allows for easy addition of new languages and regions. The system uses JSON configuration files for all user-facing text, making it simple to add support for multiple languages including Indian languages and Japanese scripts.

## Language File Structure

### Naming Convention

Language files follow the pattern: `{region}_{language}.json`

Examples:
- `gb_en.json` - British English
- `us_en.json` - American English
- `in_hi.json` - Indian Hindi
- `in_ta.json` - Indian Tamil
- `jp_ja.json` - Japanese (Hiragana/Katakana)
- `jp_ja_kanji.json` - Japanese (Kanji)

### File Organization

```
resources/data/languages/
├── gb_en.json          # British English (default)
├── us_en.json          # American English
├── in_hi.json          # Indian Hindi
├── in_ta.json          # Indian Tamil
├── jp_ja.json          # Japanese (Hiragana/Katakana)
└── jp_ja_kanji.json    # Japanese (Kanji)
```

## Language File Format

Each language file contains a structured JSON object with the following sections:

```json
{
  "language": "en",
  "region": "gb",
  "name": "British English",
  "native_name": "British English",
  "version": "1.0.0",
  
  "app": {
    "name": "HelpMeSign",
    "description": "Sign Language Translation and Learning Application",
    "version": "1.0.0",
    "organization": "CycleRunCode Club",
    "domain": "https://cycleruncode.club"
  },
  
  "startup": {
    "title": "Welcome to HelpMeSign",
    "subtitle": "Choose your preferred mode:",
    "info_text": "You can change this setting later in the application preferences.",
    "auto_close_message": "Auto-closing startup screen (no choice made)"
  },
  
  "modes": {
    "sign_translate": {
      "name": "Sign & Translate",
      "description": "Convert text to sign language symbols and gestures",
      "button_text": "Sign & Translate",
      "previous_choice_text": "Sign & Translate (Previous Choice)"
    },
    "learn": {
      "name": "Learn Sign Language",
      "description": "Educational mode for learning sign language vocabulary and grammar",
      "button_text": "Learn Sign Language",
      "previous_choice_text": "Learn Sign Language (Previous Choice)"
    }
  },
  
  "ui": {
    "main_window": {
      "title": "HelpMeSign",
      "dev_title": "HelpMeSign (DEV)",
      "prod_title": "HelpMeSign (PROD)"
    },
    "text_input": {
      "placeholder": "Enter text to translate or learn...",
      "label": "Input Text:",
      "clear_button": "Clear",
      "process_button": "Process",
      "placeholder_alt": "Type your text here..."
    },
    "output": {
      "label": "Output:",
      "empty_message": "Please enter some text to process.",
      "clear_button": "Clear Output",
      "placeholder": "Processed text will appear here..."
    },
    "status": {
      "default": "Ready",
      "processing": "Processing...",
      "cleared": "Text cleared",
      "mode_prefix": "Mode: ",
      "converted_prefix": "Converted '",
      "converted_suffix": "' to sign language",
      "learning_prefix": "Learning information for '",
      "learning_suffix": "'",
      "error_prefix": "Error processing text: "
    }
  },
  
  "menu": {
    "helpmesign": {
      "name": "HelpMeSign",
      "about": "About HelpMeSign",
      "preferences": "Preferences...",
      "quit": "Quit HelpMeSign"
    },
    "file": {
      "name": "File",
      "new": "New",
      "open": "Open...",
      "save": "Save",
      "save_as": "Save As...",
      "close": "Close",
      "quit": "Quit"
    },
    "edit": {
      "name": "Edit",
      "undo": "Undo",
      "redo": "Redo",
      "cut": "Cut",
      "copy": "Copy",
      "paste": "Paste",
      "select_all": "Select All",
      "clear": "Clear"
    },
    "view": {
      "name": "View",
      "zoom_in": "Zoom In",
      "zoom_out": "Zoom Out",
      "actual_size": "Actual Size",
      "fit_to_window": "Fit to Window"
    },
    "settings": {
      "name": "Settings",
      "preferences": "Preferences...",
      "mode": "Mode"
    },
    "help": {
      "name": "Help",
      "help": "HelpMeSign Help",
      "about": "About HelpMeSign"
    }
  },
  
  "settings": {
    "title": "Settings",
    "mode_section": "Application Mode",
    "mode_label": "Select your preferred mode:",
    "mode_sign_translate": "Sign & Translate",
    "mode_learn": "Learn Sign Language",
    "mode_description": "This setting determines how the application processes your input text.",
    "buttons": {
      "ok": "OK",
      "cancel": "Cancel",
      "apply": "Apply"
    }
  },
  
  "about": {
    "title": "About HelpMeSign",
    "description": "HelpMeSign is a desktop application for sign language translation and learning. It provides tools for converting text to sign language and educational content for learning sign language vocabulary and grammar.",
    "version": "Version",
    "copyright": "© 2024 HelpMeSign. All rights reserved.",
    "website": "Website",
    "support": "Support",
    "content": "<h2>HelpMeSign</h2><p>A Python application for Sign Language translation and learning.</p><p>Built with PySide6 (Qt for Python)</p><p>Version 1.0.0</p>"
  },
  
  "sign_language": {
    "conversion": {
      "hello": "👋 Wave hand",
      "hi": "👋 Wave hand",
      "thank": "🙏 Hand to chin, then forward",
      "thanks": "🙏 Hand to chin, then forward",
      "thank_you": "🙏 Hand to chin, then forward",
      "yes": "👍 Nod head and fist",
      "no": "👎 Shake head and index finger",
      "please": "🤲 Flat hand, palm up, circular motion",
      "sorry": "🤝 Fist over heart, circular motion",
      "spell_prefix": "🤟 Spell: "
    },
    "learning": {
      "title_prefix": "📚 Sign Language Learning: \"",
      "title_suffix": "\"",
      "basic_signs_title": "🤟 Basic Signs:",
      "basic_signs": {
        "hello": "Hello: Wave your hand",
        "thank_you": "Thank you: Touch chin with fingertips, then move hand forward",
        "yes": "Yes: Nod head while making a fist",
        "no": "No: Shake head while pointing index finger"
      },
      "tips_title": "💡 Tips:",
      "tips": [
        "Always maintain eye contact",
        "Use facial expressions to convey emotion",
        "Keep movements clear and deliberate",
        "Practice regularly for fluency"
      ],
      "practice_prefix": "🎯 Practice: Try signing \"",
      "practice_suffix": "\" using the basic signs above!"
    }
  },
  
  "errors": {
    "general": "An error occurred",
    "file_not_found": "File not found",
    "permission_denied": "Permission denied",
    "invalid_input": "Invalid input",
    "network_error": "Network error",
    "unknown": "Unknown error"
  },
  
  "messages": {
    "success": "Success",
    "warning": "Warning",
    "error": "Error",
    "info": "Information",
    "confirm": "Confirm",
    "cancel": "Cancel",
    "ok": "OK",
    "yes": "Yes",
    "no": "No"
  },
  
  "shortcuts": {
    "settings": "Settings...",
    "quit": "Quit HelpMeSign",
    "clear_all": "Clear All",
    "close_window": "Close Window",
    "help": "HelpMeSign Help",
    "process_text": "Process Text",
    "clear_input": "Clear Text Input"
  },
  
  "os_shortcuts": {
    "macos": {
      "cmd": "⌘",
      "option": "⌥",
      "shift": "⇧",
      "ctrl": "⌃",
      "enter": "↵",
      "delete": "⌫",
      "escape": "⎋"
    },
    "windows": {
      "cmd": "Ctrl",
      "option": "Alt",
      "shift": "Shift",
      "ctrl": "Ctrl",
      "enter": "Enter",
      "delete": "Del",
      "escape": "Esc"
    },
    "linux": {
      "cmd": "Ctrl",
      "option": "Alt",
      "shift": "Shift",
      "ctrl": "Ctrl",
      "enter": "Enter",
      "delete": "Del",
      "escape": "Esc"
    }
  },
  
  "help": {
    "title": "HelpMeSign Help",
    "getting_started_title": "Getting Started",
    "getting_started_steps": [
      "1. Enter text in the input field",
      "2. Press Enter or click \"Process\" to translate",
      "3. View the output in the text area below",
      "4. Use \"Clear\" to reset the application"
    ],
    "keyboard_shortcuts_title": "Keyboard Shortcuts",
    "keyboard_shortcuts": {
      "enter": "Enter - Process text",
      "ctrl_enter": "Ctrl+Enter - Process text",
      "ctrl_shift_k": "Ctrl+Shift+K - Clear all",
      "ctrl_comma": "Ctrl+, - Open settings",
      "f1": "F1 - Show help",
      "ctrl_q": "Ctrl+Q - Quit application"
    }
  }
}
```

## Usage in Code

### Basic Text Retrieval

```python
from helpmesign.utils.language_manager import get_text

# Get a simple text string
app_name = get_text("app.name")
window_title = get_text("ui.main_window.title")
```

### List Retrieval

```python
from helpmesign.utils.language_manager import get_list

# Get a list of items
tips = get_list("sign_language.learning.tips")
for tip in tips:
    print(tip)
```

### Dictionary Retrieval

```python
from helpmesign.utils.language_manager import get_dict

# Get a dictionary of key-value pairs
basic_signs = get_dict("sign_language.learning.basic_signs")
for sign_name, description in basic_signs.items():
    print(f"{sign_name}: {description}")

# Get OS-specific shortcuts
from helpmesign.ui.components import get_os_shortcuts
shortcuts = get_os_shortcuts()
print(f"Command key: {shortcuts['cmd']}")
```

### Language Management

```python
from helpmesign.utils.language_manager import (
    get_language_manager, change_language, 
    get_available_languages, get_current_language_info
)

# Get the language manager
lang_manager = get_language_manager()

# Change language
success = change_language("en", "us")  # Switch to US English

# Get available languages
languages = get_available_languages()
for lang in languages:
    print(f"{lang['name']} ({lang['native_name']})")

# Get current language info
current_info = get_current_language_info()
print(f"Current: {current_info['language']}_{current_info['region']}")
```

## Adding New Languages

### Step 1: Create Language File

Create a new JSON file in `resources/data/languages/` following the naming convention:

```bash
# For Indian Hindi
touch resources/data/languages/in_hi.json

# For Japanese (Hiragana/Katakana)
touch resources/data/languages/jp_ja.json

# For Japanese (Kanji)
touch resources/data/languages/jp_ja_kanji.json
```

### Step 2: Copy and Translate

1. Copy the content from `gb_en.json` (the default language)
2. Update the metadata:
   ```json
   {
     "language": "hi",
     "region": "in",
     "name": "Indian Hindi",
     "native_name": "हिंदी",
     "version": "1.0.0"
   }
   ```
3. Translate all text values to the target language
4. Keep the same structure and keys

### Step 3: Test

Run the application to verify the new language works correctly:

```bash
python3 main.py --env dev
```

## System Language Detection

The system automatically detects the user's system language and region:

```python
from helpmesign.utils.language_manager import detect_system_language

language, region = detect_system_language()
print(f"Detected: {language}_{region}")
```

## OS-Specific Shortcuts

The system provides platform-specific keyboard shortcut symbols that automatically adapt to the user's operating system:

### Supported Platforms

- **macOS**: Uses native symbols (⌘, ⌥, ⇧, ⌃, ↵, ⌫, ⎋)
- **Windows**: Uses standard text labels (Ctrl, Alt, Shift, Enter, Del, Esc)
- **Linux**: Uses standard text labels (Ctrl, Alt, Shift, Enter, Del, Esc)

### Usage

```python
from helpmesign.ui.components import get_os_shortcuts

# Get shortcuts for current OS
shortcuts = get_os_shortcuts()

# Use in UI
cmd_symbol = shortcuts['cmd']  # "⌘" on macOS, "Ctrl" on Windows/Linux
option_symbol = shortcuts['option']  # "⌥" on macOS, "Alt" on Windows/Linux
```

### Configuration

OS shortcuts are defined in each language file under the `os_shortcuts` section:

```json
{
  "os_shortcuts": {
    "macos": {
      "cmd": "⌘",
      "option": "⌥",
      "shift": "⇧",
      "ctrl": "⌃",
      "enter": "↵",
      "delete": "⌫",
      "escape": "⎋"
    },
    "windows": {
      "cmd": "Ctrl",
      "option": "Alt",
      "shift": "Shift",
      "ctrl": "Ctrl",
      "enter": "Enter",
      "delete": "Del",
      "escape": "Esc"
    },
    "linux": {
      "cmd": "Ctrl",
      "option": "Alt",
      "shift": "Shift",
      "ctrl": "Ctrl",
      "enter": "Enter",
      "delete": "Del",
      "escape": "Esc"
    }
  }
}
```

### Benefits

1. **Native Look**: Shortcuts display using platform-appropriate symbols
2. **Consistent Experience**: Same shortcuts work across all supported languages
3. **Easy Maintenance**: Centralized configuration in language files
4. **Automatic Detection**: No manual configuration required
5. **Fallback Support**: Graceful degradation for unknown systems

## Fallback System

If a requested language is not available, the system falls back to British English (`gb_en.json`). This ensures the application always has text to display, even if translations are incomplete.

## Benefits

1. **Easy Maintenance**: All user-facing text is centralized in JSON files
2. **Consistent Naming**: Clear naming convention for language files
3. **Extensible**: Easy to add new languages and regions
4. **Fallback Support**: Graceful degradation when translations are missing
5. **System Integration**: Automatic detection of user's preferred language
6. **Structured Data**: Support for text, lists, and dictionaries
7. **Version Control**: Language files can be versioned and tracked
8. **OS-Aware Shortcuts**: Platform-specific keyboard shortcut symbols
9. **Cross-Platform Consistency**: Same shortcuts work across all supported languages

## Future Enhancements

1. **Language Selection UI**: Add a language selector in settings
2. **Translation Management**: Tools for managing and updating translations
3. **Pluralization Support**: Handle plural forms in different languages
4. **RTL Support**: Right-to-left language support (Arabic, Hebrew)
5. **Font Support**: Automatic font selection based on language
6. **Cultural Adaptations**: Region-specific content and formatting
7. **Custom Shortcut Mapping**: Allow users to customize keyboard shortcuts
8. **Accessibility Shortcuts**: Support for accessibility features and screen readers

## Best Practices

1. **Always use language keys**: Never hard-code text in the application
2. **Keep keys descriptive**: Use clear, hierarchical key names
3. **Test all languages**: Verify translations work correctly
4. **Maintain consistency**: Use the same key structure across all language files
5. **Version control**: Track changes to language files
6. **Documentation**: Keep translations well-documented
7. **Cultural sensitivity**: Consider cultural differences in translations 