#!/usr/bin/env python3
"""
Unit tests for LanguageLoader class
Tests the language loading and management functionality
"""

import json
import os
from unittest.mock import Mock, mock_open, patch

import pytest

from src.helpmesign.utils.language_loader import (
    LanguageLoader,
    get_all_languages,
    get_language_by_code,
    get_language_categories,
    search_languages,
)


class TestLanguageLoader:
    """Test cases for LanguageLoader class"""

    @pytest.fixture
    def sample_languages_data(self):
        """Sample languages data for testing"""
        return [
            {
                "name": "American Sign Language",
                "nativeName": "American Sign Language",
                "code": "ASL",
                "flag": "🇺🇸",
                "metadata": {
                    "speakers": 500000,
                    "difficulty": "Beginner",
                    "regions": ["North America", "United States"],
                },
                "writingSystems": {
                    "fingerspelling": "asl_fingerspelling.json",
                    "numbers": "asl_numbers.json",
                },
            },
            {
                "name": "British Sign Language",
                "nativeName": "British Sign Language",
                "code": "BSL",
                "flag": "🇬🇧",
                "metadata": {
                    "speakers": 250000,
                    "difficulty": "Intermediate",
                    "regions": ["Europe", "United Kingdom"],
                },
                "writingSystems": {
                    "fingerspelling": "bsl_fingerspelling.json",
                    "numbers": "bsl_numbers.json",
                },
            },
            {
                "name": "Japanese Sign Language",
                "nativeName": "日本手話",
                "code": "JSL",
                "flag": "🇯🇵",
                "metadata": {
                    "speakers": 320000,
                    "difficulty": "Advanced",
                    "regions": ["Asia", "Japan"],
                },
                "writingSystems": {
                    "hiragana": "jsl_hiragana.json",
                    "katakana": "jsl_katakana.json",
                    "kanji": "jsl_kanji.json",
                },
            },
        ]

    @pytest.fixture
    def mock_resource_manager(self):
        """Mock ResourceManager for testing"""
        with patch("src.helpmesign.utils.language_loader.ResourceManager") as mock_rm:
            mock_instance = Mock()
            mock_rm.return_value = mock_instance
            mock_instance.get_data_path.return_value = "/fake/path/languages.json"
            yield mock_instance

    def test_language_loader_initialization_success(
        self, sample_languages_data, mock_resource_manager
    ):
        """Test successful initialization with valid data"""
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_languages_data))
        ):
            with patch("os.path.exists", return_value=True):
                loader = LanguageLoader()

                assert len(loader.languages) == 3
                assert loader.languages[0]["code"] == "ASL"
                assert loader.languages[1]["code"] == "BSL"
                assert loader.languages[2]["code"] == "JSL"

    def test_language_loader_initialization_file_not_found(self, mock_resource_manager):
        """Test initialization when languages.json file doesn't exist"""
        with patch("os.path.exists", return_value=False):
            loader = LanguageLoader()

            assert loader.languages == []

    def test_language_loader_initialization_file_error(self, mock_resource_manager):
        """Test initialization when file reading fails"""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", side_effect=Exception("File read error")):
                loader = LanguageLoader()

                assert loader.languages == []

    def test_get_all_languages(self, sample_languages_data, mock_resource_manager):
        """Test get_all_languages method"""
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_languages_data))
        ):
            with patch("os.path.exists", return_value=True):
                loader = LanguageLoader()
                all_languages = loader.get_all_languages()

                assert len(all_languages) == 3
                assert all_languages == sample_languages_data

    def test_get_language_by_code_success(
        self, sample_languages_data, mock_resource_manager
    ):
        """Test get_language_by_code with existing code"""
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_languages_data))
        ):
            with patch("os.path.exists", return_value=True):
                loader = LanguageLoader()
                asl_language = loader.get_language_by_code("ASL")

                assert asl_language is not None
                assert asl_language["code"] == "ASL"
                assert asl_language["name"] == "American Sign Language"

    def test_get_language_by_code_not_found(
        self, sample_languages_data, mock_resource_manager
    ):
        """Test get_language_by_code with non-existing code"""
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_languages_data))
        ):
            with patch("os.path.exists", return_value=True):
                loader = LanguageLoader()
                result = loader.get_language_by_code("XYZ")

                assert result is None

    def test_get_languages_by_difficulty(
        self, sample_languages_data, mock_resource_manager
    ):
        """Test get_languages_by_difficulty method"""
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_languages_data))
        ):
            with patch("os.path.exists", return_value=True):
                loader = LanguageLoader()
                beginner_languages = loader.get_languages_by_difficulty("Beginner")

                assert len(beginner_languages) == 1
                assert beginner_languages[0]["code"] == "ASL"

    def test_get_languages_by_difficulty_no_matches(
        self, sample_languages_data, mock_resource_manager
    ):
        """Test get_languages_by_difficulty with no matches"""
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_languages_data))
        ):
            with patch("os.path.exists", return_value=True):
                loader = LanguageLoader()
                expert_languages = loader.get_languages_by_difficulty("Expert")

                assert len(expert_languages) == 0

    def test_get_languages_by_region(
        self, sample_languages_data, mock_resource_manager
    ):
        """Test get_languages_by_region method"""
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_languages_data))
        ):
            with patch("os.path.exists", return_value=True):
                loader = LanguageLoader()
                asia_languages = loader.get_languages_by_region("Asia")

                assert len(asia_languages) == 1
                assert asia_languages[0]["code"] == "JSL"

    def test_get_languages_by_region_no_matches(
        self, sample_languages_data, mock_resource_manager
    ):
        """Test get_languages_by_region with no matches"""
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_languages_data))
        ):
            with patch("os.path.exists", return_value=True):
                loader = LanguageLoader()
                africa_languages = loader.get_languages_by_region("Africa")

                assert len(africa_languages) == 0

    def test_search_languages_by_name(
        self, sample_languages_data, mock_resource_manager
    ):
        """Test search_languages by name"""
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_languages_data))
        ):
            with patch("os.path.exists", return_value=True):
                loader = LanguageLoader()
                results = loader.search_languages("American")

                assert len(results) == 1
                assert results[0]["code"] == "ASL"

    def test_search_languages_by_native_name(
        self, sample_languages_data, mock_resource_manager
    ):
        """Test search_languages by native name"""
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_languages_data))
        ):
            with patch("os.path.exists", return_value=True):
                loader = LanguageLoader()
                results = loader.search_languages("日本")

                assert len(results) == 1
                assert results[0]["code"] == "JSL"

    def test_search_languages_by_code(
        self, sample_languages_data, mock_resource_manager
    ):
        """Test search_languages by code"""
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_languages_data))
        ):
            with patch("os.path.exists", return_value=True):
                loader = LanguageLoader()
                results = loader.search_languages("BSL")

                assert len(results) == 1
                assert results[0]["code"] == "BSL"

    def test_search_languages_case_insensitive(
        self, sample_languages_data, mock_resource_manager
    ):
        """Test search_languages is case insensitive"""
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_languages_data))
        ):
            with patch("os.path.exists", return_value=True):
                loader = LanguageLoader()
                results = loader.search_languages("american")

                assert len(results) == 1
                assert results[0]["code"] == "ASL"

    def test_search_languages_no_matches(
        self, sample_languages_data, mock_resource_manager
    ):
        """Test search_languages with no matches"""
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_languages_data))
        ):
            with patch("os.path.exists", return_value=True):
                loader = LanguageLoader()
                results = loader.search_languages("XYZ")

                assert len(results) == 0

    def test_get_popular_languages(self, sample_languages_data, mock_resource_manager):
        """Test get_popular_languages method"""
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_languages_data))
        ):
            with patch("os.path.exists", return_value=True):
                loader = LanguageLoader()
                popular_languages = loader.get_popular_languages()

                # Should return top 10 by speaker count, but we only have 3
                assert len(popular_languages) == 3
                # Should be sorted by speaker count descending
                assert popular_languages[0]["code"] == "ASL"  # 500000 speakers
                assert popular_languages[1]["code"] == "JSL"  # 320000 speakers
                assert popular_languages[2]["code"] == "BSL"  # 250000 speakers

    def test_get_language_categories(
        self, sample_languages_data, mock_resource_manager
    ):
        """Test get_language_categories method"""
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_languages_data))
        ):
            with patch("os.path.exists", return_value=True):
                loader = LanguageLoader()
                categories = loader.get_language_categories()

                assert "popular" in categories
                assert "beginner" in categories
                assert "intermediate" in categories
                assert "advanced" in categories
                assert "all" in categories

                assert len(categories["beginner"]) == 1
                assert categories["beginner"][0]["code"] == "ASL"

                assert len(categories["intermediate"]) == 1
                assert categories["intermediate"][0]["code"] == "BSL"

                assert len(categories["advanced"]) == 1
                assert categories["advanced"][0]["code"] == "JSL"

                assert len(categories["all"]) == 3


class TestLanguageLoaderGlobalFunctions:
    """Test cases for global functions in language_loader module"""

    @pytest.fixture
    def sample_languages_data(self):
        """Sample languages data for testing"""
        return [
            {"name": "American Sign Language", "code": "ASL", "flag": "🇺🇸"},
            {"name": "British Sign Language", "code": "BSL", "flag": "🇬🇧"},
        ]

    @patch("src.helpmesign.utils.language_loader._language_loader")
    def test_get_all_languages_global(
        self, mock_loader_instance, sample_languages_data
    ):
        """Test global get_all_languages function"""
        mock_loader_instance.get_all_languages.return_value = sample_languages_data

        result = get_all_languages()

        assert result == sample_languages_data
        mock_loader_instance.get_all_languages.assert_called_once()

    @patch("src.helpmesign.utils.language_loader._language_loader")
    def test_get_language_by_code_global(
        self, mock_loader_instance, sample_languages_data
    ):
        """Test global get_language_by_code function"""
        mock_loader_instance.get_language_by_code.return_value = sample_languages_data[
            0
        ]

        result = get_language_by_code("ASL")

        assert result == sample_languages_data[0]
        mock_loader_instance.get_language_by_code.assert_called_once_with("ASL")

    @patch("src.helpmesign.utils.language_loader._language_loader")
    def test_search_languages_global(self, mock_loader_instance, sample_languages_data):
        """Test global search_languages function"""
        mock_loader_instance.search_languages.return_value = [sample_languages_data[0]]

        result = search_languages("American")

        assert result == [sample_languages_data[0]]
        mock_loader_instance.search_languages.assert_called_once_with("American")

    @patch("src.helpmesign.utils.language_loader._language_loader")
    def test_get_language_categories_global(self, mock_loader_instance):
        """Test global get_language_categories function"""
        expected_categories = {
            "popular": [],
            "beginner": [],
            "intermediate": [],
            "advanced": [],
            "all": [],
        }
        mock_loader_instance.get_language_categories.return_value = expected_categories

        result = get_language_categories()

        assert result == expected_categories
        mock_loader_instance.get_language_categories.assert_called_once()

    def test_global_functions_with_none_loader(self):
        """Test global functions when _language_loader is None"""
        mock_loader = Mock()
        mock_loader.get_all_languages.return_value = []
        mock_loader.get_language_by_code.return_value = None
        mock_loader.search_languages.return_value = []
        mock_loader.get_language_categories.return_value = {}

        with patch(
            "src.helpmesign.utils.language_loader.get_language_loader",
            return_value=mock_loader,
        ):
            # These should handle None gracefully
            result = get_all_languages()
            assert result == []

            result = get_language_by_code("ASL")
            assert result is None

            result = search_languages("test")
            assert result == []

            result = get_language_categories()
            assert result == {}


class TestLanguageLoaderEdgeCases:
    """Test edge cases and error conditions"""

    @pytest.fixture
    def mock_resource_manager(self):
        """Mock ResourceManager for testing"""
        with patch("src.helpmesign.utils.language_loader.ResourceManager") as mock_rm:
            mock_instance = Mock()
            mock_rm.return_value = mock_instance
            mock_instance.get_data_path.return_value = "/fake/path/languages.json"
            yield mock_instance

    def test_language_with_missing_metadata(self, mock_resource_manager):
        """Test handling of languages with missing metadata"""
        languages_data = [
            {
                "name": "Test Language",
                "code": "TEST",
                "flag": "🏳️",
                # Missing metadata
            }
        ]

        with patch("builtins.open", mock_open(read_data=json.dumps(languages_data))):
            with patch("os.path.exists", return_value=True):
                loader = LanguageLoader()

                # Should not crash when accessing metadata
                difficulty_languages = loader.get_languages_by_difficulty("Beginner")
                assert len(difficulty_languages) == 0

                region_languages = loader.get_languages_by_region("Europe")
                assert len(region_languages) == 0

                popular_languages = loader.get_popular_languages()
                assert len(popular_languages) == 1  # Should still be included

    def test_language_with_missing_name_fields(self, mock_resource_manager):
        """Test handling of languages with missing name fields"""
        languages_data = [
            {
                "code": "TEST",
                "flag": "🏳️",
                "metadata": {"speakers": 1000},
                # Missing name and nativeName
            }
        ]

        with patch("builtins.open", mock_open(read_data=json.dumps(languages_data))):
            with patch("os.path.exists", return_value=True):
                loader = LanguageLoader()

                # Search should handle missing name fields gracefully
                results = loader.search_languages("test")
                assert len(results) == 1  # Should match by code

                results = loader.search_languages("missing")
                assert len(results) == 0

    def test_empty_languages_file(self, mock_resource_manager):
        """Test handling of empty languages file"""
        with patch("builtins.open", mock_open(read_data="[]")):
            with patch("os.path.exists", return_value=True):
                loader = LanguageLoader()

                assert loader.languages == []
                assert loader.get_all_languages() == []
                assert loader.get_language_by_code("ASL") is None
                assert loader.search_languages("test") == []
                assert loader.get_popular_languages() == []

                categories = loader.get_language_categories()
                assert categories["all"] == []
                assert categories["popular"] == []
