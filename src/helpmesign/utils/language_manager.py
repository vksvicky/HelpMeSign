"""
Language Manager for HelpMeSign Application
Handles internationalization (i18n) with support for multiple languages and regions
"""

import os
import json
import locale
import platform
from pathlib import Path
from typing import Dict, Any, Optional, List
from .logger import get_logger


class LanguageManager:
    """Manages application internationalization"""
    
    def __init__(self, language: str = "en", region: str = "us"):
        """
        Initialize LanguageManager
        
        Args:
            language: Language code (e.g., "en", "hi", "ja")
            region: Region code (e.g., "gb", "us", "in", "jp")
        """
        self.language = language.lower()
        self.region = region.lower()
        self.logger = get_logger("helpmesign.language")
        self.current_language_data = {}
        self.fallback_language_data = {}
        
        # Load language data
        self._load_language_data()
    
    def _get_language_file_path(self, language: str, region: str) -> Path:
        """Get the path to a language file"""
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent
        return project_root / "resources" / "data" / "languages" / f"{region}_{language}.json"
    
    def _load_language_data(self) -> None:
        """Load language data from JSON files"""
        try:
            # Try to load the requested language
            language_file = self._get_language_file_path(self.language, self.region)
            
            if language_file.exists():
                with open(language_file, 'r', encoding='utf-8') as f:
                    self.current_language_data = json.load(f)
                self.logger.info(f"Loaded language: {self.region}_{self.language}")
            else:
                self.logger.warning(f"Language file not found: {language_file}")
                self._load_fallback_language()
                return
            
            # Load fallback language (British English)
            fallback_file = self._get_language_file_path("en", "us")
            if fallback_file.exists():
                with open(fallback_file, 'r', encoding='utf-8') as f:
                    self.fallback_language_data = json.load(f)
                self.logger.debug("Loaded fallback language: us_en")
            else:
                self.logger.warning("Fallback language file not found")
                
        except Exception as e:
            self.logger.error(f"Error loading language data: {e}")
            self._load_fallback_language()
    
    def _load_fallback_language(self) -> None:
        """Load fallback language when requested language is not available"""
        try:
            fallback_file = self._get_language_file_path("en", "us")
            if fallback_file.exists():
                with open(fallback_file, 'r', encoding='utf-8') as f:
                    self.current_language_data = json.load(f)
                self.logger.info("Using fallback language: us_en")
            else:
                self.logger.error("No language files available")
                self.current_language_data = {}
        except Exception as e:
            self.logger.error(f"Error loading fallback language: {e}")
            self.current_language_data = {}
    
    def get_text(self, key_path: str, default: str = "") -> str:
        """
        Get localized text by key path
        
        Args:
            key_path: Dot-separated path to the text (e.g., "ui.main_window.title")
            default: Default text if key is not found
            
        Returns:
            Localized text or default
        """
        # Handle None or empty key_path
        if key_path is None or not isinstance(key_path, str):
            self.logger.warning(f"Invalid key_path: {key_path}")
            return default
        
        if not key_path.strip():
            self.logger.warning("Empty key_path provided")
            return default
        
        try:
            # Navigate through the nested dictionary
            keys = key_path.split('.')
            value = self.current_language_data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    # Try fallback language
                    fallback_value = self.fallback_language_data
                    for fallback_key in keys:
                        if isinstance(fallback_value, dict) and fallback_key in fallback_value:
                            fallback_value = fallback_value[fallback_key]
                        else:
                            self.logger.warning(f"Text key not found: {key_path}")
                            return default
                    return fallback_value
            
            return str(value) if value is not None else default
            
        except Exception as e:
            self.logger.error(f"Error getting text for key '{key_path}': {e}")
            return default
    
    def get_list(self, key_path: str, default: List[str] = None) -> List[str]:
        """
        Get localized list by key path
        
        Args:
            key_path: Dot-separated path to the list
            default: Default list if key is not found
            
        Returns:
            Localized list or default
        """
        if default is None:
            default = []
        
        # Handle None or empty key_path
        if key_path is None or not isinstance(key_path, str):
            self.logger.warning(f"Invalid key_path: {key_path}")
            return default
        
        if not key_path.strip():
            self.logger.warning("Empty key_path provided")
            return default
        
        try:
            keys = key_path.split('.')
            value = self.current_language_data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    # Try fallback language
                    fallback_value = self.fallback_language_data
                    for fallback_key in keys:
                        if isinstance(fallback_value, dict) and fallback_key in fallback_value:
                            fallback_value = fallback_value[fallback_key]
                        else:
                            self.logger.warning(f"List key not found: {key_path}")
                            return default
                    return fallback_value if isinstance(fallback_value, list) else default
            
            return value if isinstance(value, list) else default
            
        except Exception as e:
            self.logger.error(f"Error getting list for key '{key_path}': {e}")
            return default
    
    def get_dict(self, key_path: str, default: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get localized dictionary by key path
        
        Args:
            key_path: Dot-separated path to the dictionary
            default: Default dictionary if key is not found
            
        Returns:
            Localized dictionary or default
        """
        if default is None:
            default = {}
        
        # Handle None or empty key_path
        if key_path is None or not isinstance(key_path, str):
            self.logger.warning(f"Invalid key_path: {key_path}")
            return default
        
        if not key_path.strip():
            self.logger.warning("Empty key_path provided")
            return default
        
        try:
            keys = key_path.split('.')
            value = self.current_language_data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    # Try fallback language
                    fallback_value = self.fallback_language_data
                    for fallback_key in keys:
                        if isinstance(fallback_value, dict) and fallback_key in fallback_value:
                            fallback_value = fallback_value[fallback_key]
                        else:
                            self.logger.warning(f"Dict key not found: {key_path}")
                            return default
                    return fallback_value if isinstance(fallback_value, dict) else default
            
            return value if isinstance(value, dict) else default
            
        except Exception as e:
            self.logger.error(f"Error getting dict for key '{key_path}': {e}")
            return default
    
    def change_language(self, language: str, region: str) -> bool:
        """
        Change the current language
        
        Args:
            language: New language code
            region: New region code
            
        Returns:
            True if language was changed successfully
        """
        try:
            old_language = f"{self.region}_{self.language}"
            self.language = language.lower()
            self.region = region.lower()
            
            # Reload language data
            self._load_language_data()
            
            new_language = f"{self.region}_{self.language}"
            self.logger.info(f"Language changed from {old_language} to {new_language}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error changing language: {e}")
            return False
    
    def get_available_languages(self) -> List[Dict[str, str]]:
        """
        Get list of available languages
        
        Returns:
            List of language dictionaries with language, region, name, and native_name
        """
        languages = []
        languages_dir = Path(__file__).resolve().parent.parent.parent.parent / "resources" / "data" / "languages"
        
        if not languages_dir.exists():
            return languages
        
        for file_path in languages_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    languages.append({
                        'language': data.get('language', ''),
                        'region': data.get('region', ''),
                        'name': data.get('name', ''),
                        'native_name': data.get('native_name', ''),
                        'file': file_path.name
                    })
            except Exception as e:
                self.logger.warning(f"Error reading language file {file_path}: {e}")
        
        return languages
    
    def get_current_language_info(self) -> Dict[str, str]:
        """
        Get current language information
        
        Returns:
            Dictionary with current language info
        """
        return {
            'language': self.language,
            'region': self.region,
            'name': self.current_language_data.get('name', ''),
            'native_name': self.current_language_data.get('native_name', ''),
            'version': self.current_language_data.get('version', '')
        }
    
    def detect_system_language(self) -> tuple[str, str]:
        """
        Detect system language and region
        
        Returns:
            Tuple of (language, region)
        """
        try:
            # Get system locale
            system_locale = locale.getdefaultlocale()
            if system_locale[0]:
                # Parse locale (e.g., "en_US" -> ("en", "us"))
                locale_parts = system_locale[0].split('_')
                if len(locale_parts) >= 2:
                    return locale_parts[0].lower(), locale_parts[1].lower()
                elif len(locale_parts) == 1:
                    return locale_parts[0].lower(), "us"  # Default region
            
            # Fallback based on platform
            if platform.system() == "Darwin":  # macOS
                return "en", "us"
            elif platform.system() == "Windows":
                return "en", "us"
            else:  # Linux
                return "en", "us"
                
        except Exception as e:
            self.logger.warning(f"Error detecting system language: {e}")
            return "en", "us"  # Default fallback


# Global language manager instance
_language_manager = None

def get_language_manager(language: str = "en", region: str = "us") -> LanguageManager:
    """Get the global language manager instance"""
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager(language, region)
    return _language_manager

def get_text(key_path: str, default: str = "") -> str:
    """Get localized text by key path"""
    return get_language_manager().get_text(key_path, default)

def get_list(key_path: str, default: List[str] = None) -> List[str]:
    """Get localized list by key path"""
    return get_language_manager().get_list(key_path, default)

def get_dict(key_path: str, default: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get localized dictionary by key path"""
    return get_language_manager().get_dict(key_path, default)

def change_language(language: str, region: str) -> bool:
    """Change the current language"""
    return get_language_manager().change_language(language, region)

def get_available_languages() -> List[Dict[str, str]]:
    """Get list of available languages"""
    return get_language_manager().get_available_languages()

def get_current_language_info() -> Dict[str, str]:
    """Get current language information"""
    return get_language_manager().get_current_language_info()

def detect_system_language() -> tuple[str, str]:
    """Detect system language and region"""
    return get_language_manager().detect_system_language() 