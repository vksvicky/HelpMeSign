#!/usr/bin/env python3
"""
Language Loader for HelpMeSign
Handles loading and managing sign languages from languages.json
"""

import json
import os
from typing import Any, Dict, List, Optional

from ..utils.resource_manager import ResourceManager


class LanguageLoader:
    """Loads and manages sign languages from languages.json"""

    def __init__(self):
        self.resource_manager = ResourceManager()
        self.languages: List[Dict[str, Any]] = []
        self.load_languages()

    def load_languages(self) -> None:
        """Load languages from languages.json file"""
        try:
            languages_path = self.resource_manager.get_data_path("languages.json")
            if os.path.exists(languages_path):
                with open(languages_path, "r", encoding="utf-8") as f:
                    self.languages = json.load(f)
            else:
                # Fallback to empty list if file doesn't exist
                self.languages = []
        except Exception as e:
            print(f"Error loading languages: {e}")
            self.languages = []

    def get_all_languages(self) -> List[Dict[str, Any]]:
        """Get all available languages"""
        return self.languages

    def get_language_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Get a specific language by its code"""
        for language in self.languages:
            if language.get("code") == code:
                return language
        return None

    def get_languages_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """Get languages filtered by difficulty level"""
        return [
            lang
            for lang in self.languages
            if lang.get("metadata", {}).get("difficulty") == difficulty
        ]

    def get_languages_by_region(self, region: str) -> List[Dict[str, Any]]:
        """Get languages filtered by region"""
        return [
            lang
            for lang in self.languages
            if region in lang.get("metadata", {}).get("regions", [])
        ]

    def search_languages(self, query: str) -> List[Dict[str, Any]]:
        """Search languages by name, native name, or code"""
        query = query.lower()
        results = []
        for language in self.languages:
            if (
                query in language.get("name", "").lower()
                or query in language.get("nativeName", "").lower()
                or query in language.get("code", "").lower()
            ):
                results.append(language)
        return results

    def get_popular_languages(self) -> List[Dict[str, Any]]:
        """Get popular languages (those with highest speaker counts)"""
        sorted_languages = sorted(
            self.languages,
            key=lambda x: x.get("metadata", {}).get("speakers", 0),
            reverse=True,
        )
        return sorted_languages[:10]  # Top 10 by speaker count

    def get_language_categories(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get languages organized by categories"""
        categories = {
            "popular": self.get_popular_languages(),
            "beginner": self.get_languages_by_difficulty("Beginner"),
            "intermediate": self.get_languages_by_difficulty("Intermediate"),
            "advanced": self.get_languages_by_difficulty("Advanced"),
            "all": self.languages,
        }
        return categories


# Global instance
_language_loader: Optional[LanguageLoader] = None


def get_language_loader() -> LanguageLoader:
    """Get the global language loader instance"""
    global _language_loader
    if _language_loader is None:
        _language_loader = LanguageLoader()
    return _language_loader


def get_all_languages() -> List[Dict[str, Any]]:
    """Get all available languages"""
    return get_language_loader().get_all_languages()


def get_language_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Get a specific language by its code"""
    return get_language_loader().get_language_by_code(code)


def search_languages(query: str) -> List[Dict[str, Any]]:
    """Search languages by name, native name, or code"""
    return get_language_loader().search_languages(query)


def get_language_categories() -> Dict[str, List[Dict[str, Any]]]:
    """Get languages organized by categories"""
    return get_language_loader().get_language_categories()
