"""
Sign Language Data Loader

This module provides utilities for loading and validating sign language data files.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Try to import logger, but make it optional for testing
try:
    from .logger import get_logger

    logger = get_logger(__name__)
except ImportError:
    # Fallback logger for testing environments
    import logging

    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)


class SignLanguageLoader:
    """Loader for sign language data files."""

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the sign language loader.

        Args:
            data_dir: Directory containing sign language data files.
                      Defaults to resources/data/signs relative to project root.
        """
        if data_dir is None:
            # Get the project root directory
            project_root = Path(__file__).parent.parent.parent.parent
            data_dir = str(project_root / "resources" / "data" / "signs")

        self.data_dir = Path(data_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get_available_languages(self) -> List[str]:
        """
        Get list of available sign languages.

        Returns:
            List of language codes (e.g., ['asl', 'bsl'])
        """
        if not self.data_dir.exists():
            logger.warning(f"Sign language data directory not found: {self.data_dir}")
            return []

        languages = []
        for item in self.data_dir.iterdir():
            if item.is_dir():
                languages.append(item.name.upper())

        return sorted(languages)

    def get_available_hands(self, language: str) -> List[str]:
        """
        Get available hand variants for a language.

        Args:
            language: Language code (e.g., 'ASL')

        Returns:
            List of available hand variants (e.g., ['right', 'left'])
        """
        lang_dir = self.data_dir / language.lower()
        if not lang_dir.exists():
            logger.warning(f"Language directory not found: {lang_dir}")
            return []

        hands = []
        for file_path in lang_dir.glob(f"{language.lower()}_*_hand.json"):
            # Extract hand from filename (e.g., asl_right_hand.json -> right)
            parts = file_path.stem.split("_")
            if len(parts) >= 3 and parts[-1] == "hand":
                hands.append(parts[-2])

        return sorted(hands)

    def load_sign_data(
        self, language: str, hand: str = "right"
    ) -> Optional[Dict[str, Any]]:
        """
        Load sign language data for a specific language and hand.

        Args:
            language: Language code (e.g., 'ASL')
            hand: Hand preference ('right' or 'left')

        Returns:
            Dictionary containing sign language data or None if not found
        """
        cache_key = f"{language}_{hand}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Try different filename patterns
        possible_files = [f"{language.lower()}_{hand}_hand.json"]

        lang_dir = self.data_dir / language.lower()
        data = None

        for filename in possible_files:
            file_path = lang_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    logger.info(f"Loaded sign language data: {file_path}")
                    break
                except (json.JSONDecodeError, IOError) as e:
                    logger.error(
                        f"Error loading sign language data from {file_path}: {e}"
                    )
                    continue

        if data is None:
            logger.warning(f"No sign language data found for {language} ({hand} hand)")
            return None

        # Validate the data structure
        if self._validate_sign_data(data):
            self._cache[cache_key] = data
            return data
        else:
            logger.error(
                f"Invalid sign language data structure for {language} ({hand} hand)"
            )
            return None

    def get_alphabet_signs(
        self, language: str, hand: str = "right"
    ) -> Dict[str, Dict[str, str]]:
        """
        Get alphabet signs for a language and hand.

        Args:
            language: Language code (e.g., 'ASL')
            hand: Hand preference ('right' or 'left')

        Returns:
            Dictionary mapping letters to their sign data
        """
        data = self.load_sign_data(language, hand)
        if data is None:
            return {}

        return data.get("alphabet", {})

    def get_number_signs(
        self, language: str, hand: str = "right"
    ) -> Dict[str, Dict[str, str]]:
        """
        Get number signs for a language and hand.

        Args:
            language: Language code (e.g., 'ASL')
            hand: Hand preference ('right' or 'left')

        Returns:
            Dictionary mapping numbers to their sign data
        """
        data = self.load_sign_data(language, hand)
        if data is None:
            return {}

        return data.get("numbers", {})

    def get_sign_svg(
        self, language: str, character: str, hand: str = "right"
    ) -> Optional[str]:
        """
        Get SVG data for a specific sign.

        Args:
            language: Language code (e.g., 'ASL')
            character: Letter or number to get sign for
            hand: Hand preference ('right' or 'left')

        Returns:
            SVG string or None if not found
        """
        # Try alphabet first
        alphabet = self.get_alphabet_signs(language, hand)
        if character.upper() in alphabet:
            return alphabet[character.upper()].get("svg")

        # Try numbers
        numbers = self.get_number_signs(language, hand)
        if character in numbers:
            return numbers[character].get("svg")

        logger.warning(f"Sign not found for '{character}' in {language} ({hand} hand)")
        return None

    def get_sign_instructions(
        self, language: str, character: str, hand: str = "right"
    ) -> Optional[str]:
        """
        Get instructions for performing a specific sign.

        Args:
            language: Language code (e.g., 'ASL')
            character: Letter or number to get instructions for
            hand: Hand preference ('right' or 'left')

        Returns:
            Instructions string or None if not found
        """
        # Try alphabet first
        alphabet = self.get_alphabet_signs(language, hand)
        if character.upper() in alphabet:
            return alphabet[character.upper()].get("instructions")

        # Try numbers
        numbers = self.get_number_signs(language, hand)
        if character in numbers:
            return numbers[character].get("instructions")

        logger.warning(
            f"Instructions not found for '{character}' in {language} ({hand} hand)"
        )
        return None

    def _validate_sign_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate the structure of sign language data.

        Args:
            data: Dictionary containing sign language data

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["language", "hand", "version", "description"]
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return False

        # Check for alphabet or numbers sections
        if "alphabet" not in data and "numbers" not in data:
            logger.error("Data must contain either 'alphabet' or 'numbers' section")
            return False

        # Validate alphabet structure
        if "alphabet" in data:
            for letter, sign_data in data["alphabet"].items():
                if not isinstance(sign_data, dict):
                    logger.error(f"Invalid alphabet entry for {letter}")
                    return False
                if "svg" not in sign_data or "description" not in sign_data:
                    logger.error(
                        f"Missing required fields in alphabet entry for {letter}"
                    )
                    return False

        # Validate numbers structure
        if "numbers" in data:
            for number, sign_data in data["numbers"].items():
                if not isinstance(sign_data, dict):
                    logger.error(f"Invalid numbers entry for {number}")
                    return False
                if "svg" not in sign_data or "description" not in sign_data:
                    logger.error(
                        f"Missing required fields in numbers entry for {number}"
                    )
                    return False

        return True

    def clear_cache(self):
        """Clear the internal cache."""
        self._cache.clear()
        logger.debug("Sign language loader cache cleared")


# Convenience function for quick access
def get_sign_language_loader() -> SignLanguageLoader:
    """
    Get a sign language loader instance.

    Returns:
        SignLanguageLoader instance
    """
    return SignLanguageLoader()
