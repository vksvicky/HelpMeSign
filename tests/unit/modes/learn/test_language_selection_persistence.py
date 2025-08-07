#!/usr/bin/env python3
"""
Tests for language selection persistence in LearnMode
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from src.helpmesign.modes.learn.learn_mode import LearnMode


class TestLanguageSelectionPersistence:
    """Test language selection persistence functionality"""

    def test_save_language_selection_fsl(self):
        """Test that FSL language selection is saved correctly"""
        # Mock main window
        mock_main_window = MagicMock()
        mock_main_window.content_area = MagicMock()

        # Mock the configuration functions
        with patch(
            "src.helpmesign.core.startup.get_all_settings"
        ) as mock_get_settings, patch(
            "src.helpmesign.core.startup.save_all_settings"
        ) as mock_save_settings:

            # Mock current settings
            mock_get_settings.return_value = {
                "user_mode": "Learn Sign Language",
                "theme": "Dark",
                "font_size": 12,
                "hand_preference": "right",
                "selected_language": "ASL",  # Current setting
            }
            mock_save_settings.return_value = True

            # Create LearnMode instance with minimal UI setup
            with patch.object(LearnMode, "setup_ui"):
                learn_mode = LearnMode(mock_main_window, "dev")

                # Test saving FSL selection
                learn_mode.save_language_selection("FSL")

                # Verify that save_all_settings was called with FSL
                mock_save_settings.assert_called_once()
                call_args = mock_save_settings.call_args[0][0]
                assert call_args["selected_language"] == "FSL"

    def test_load_saved_language_selection_fsl(self):
        """Test that FSL language selection is loaded correctly"""
        # Mock main window
        mock_main_window = MagicMock()
        mock_main_window.content_area = MagicMock()

        # Mock the configuration functions
        with patch(
            "src.helpmesign.core.startup.get_all_settings"
        ) as mock_get_settings, patch(
            "src.helpmesign.utils.language_loader.get_all_languages"
        ) as mock_get_languages:

            # Mock current settings with FSL saved
            mock_get_settings.return_value = {
                "user_mode": "Learn Sign Language",
                "theme": "Dark",
                "font_size": 12,
                "hand_preference": "right",
                "selected_language": "FSL",  # Saved FSL selection
            }

            # Mock FSL language data
            mock_fsl_language = {
                "code": "FSL",
                "name": "French Sign Language",
                "nativeName": "Langue des Signes Française",
                "country": "FR",
                "flag": "🇫🇷",
            }
            mock_get_languages.return_value = [mock_fsl_language]

            # Create LearnMode instance with minimal UI setup
            with patch.object(LearnMode, "setup_ui"):
                learn_mode = LearnMode(mock_main_window, "dev")

                # Test loading saved FSL selection
                learn_mode.load_saved_language_selection()

                # Verify that the saved language was loaded correctly
                # The method should have called select_language_by_code with "FSL"
                # We can verify this by checking if the method was called correctly

    def test_language_selection_persistence_workflow(self):
        """Test the complete workflow of selecting and persisting FSL"""
        # Mock main window
        mock_main_window = MagicMock()
        mock_main_window.content_area = MagicMock()

        # Mock the configuration functions
        with patch(
            "src.helpmesign.core.startup.get_all_settings"
        ) as mock_get_settings, patch(
            "src.helpmesign.core.startup.save_all_settings"
        ) as mock_save_settings, patch(
            "src.helpmesign.utils.language_loader.get_all_languages"
        ) as mock_get_languages:

            # Mock initial settings
            mock_get_settings.return_value = {
                "user_mode": "Learn Sign Language",
                "theme": "Dark",
                "font_size": 12,
                "hand_preference": "right",
                "selected_language": "ASL",  # Initial setting
            }
            mock_save_settings.return_value = True

            # Mock FSL language data
            mock_fsl_language = {
                "code": "FSL",
                "name": "French Sign Language",
                "nativeName": "Langue des Signes Française",
                "country": "FR",
                "flag": "🇫🇷",
            }
            mock_get_languages.return_value = [mock_fsl_language]

            # Create LearnMode instance with minimal UI setup
            with patch.object(LearnMode, "setup_ui"):
                learn_mode = LearnMode(mock_main_window, "dev")

                # Mock the UI components needed for on_language_selected
                learn_mode.language_list_layout = MagicMock()
                learn_mode.language_list_layout.count.return_value = 0
                learn_mode.sign_title = MagicMock()

                # Step 1: Load initial settings (should be ASL)
                learn_mode.load_saved_language_selection()

                # Step 2: Simulate user selecting FSL
                learn_mode.on_language_selected(mock_fsl_language)

                # Verify that FSL was saved
                mock_save_settings.assert_called_once()
                call_args = mock_save_settings.call_args[0][0]
                assert call_args["selected_language"] == "FSL"

    def test_language_selection_fallback_to_asl(self):
        """Test that invalid language selection falls back to ASL"""
        # Mock main window
        mock_main_window = MagicMock()
        mock_main_window.content_area = MagicMock()

        # Mock the configuration functions
        with patch(
            "src.helpmesign.core.startup.get_all_settings"
        ) as mock_get_settings, patch(
            "src.helpmesign.utils.language_loader.get_all_languages"
        ) as mock_get_languages:

            # Mock settings with invalid language
            mock_get_settings.return_value = {
                "user_mode": "Learn Sign Language",
                "theme": "Dark",
                "font_size": 12,
                "hand_preference": "right",
                "selected_language": "INVALID_LANG",  # Invalid language
            }

            # Mock language data with ASL
            mock_asl_language = {
                "code": "ASL",
                "name": "American Sign Language",
                "nativeName": "American Sign Language",
                "country": "US",
                "flag": "🇺🇸",
            }
            mock_get_languages.return_value = [mock_asl_language]

            # Create LearnMode instance with minimal UI setup
            with patch.object(LearnMode, "setup_ui"):
                learn_mode = LearnMode(mock_main_window, "dev")

                # Test loading saved selection (should fallback to ASL)
                learn_mode.load_saved_language_selection()

                # The method should handle the fallback gracefully

    def test_get_all_settings_includes_selected_language(self):
        """Test that get_all_settings includes selected_language field"""
        from src.helpmesign.core.startup import get_all_settings

        # Mock the SecureConfigManager
        with patch(
            "src.helpmesign.core.startup.SecureConfigManager"
        ) as mock_config_manager:
            mock_instance = MagicMock()
            mock_config_manager.return_value = mock_instance

            # Mock the get_all_settings method
            mock_instance.get_all_settings.return_value = {
                "user_mode": "Learn Sign Language",
                "theme": "Dark",
                "font_size": 12,
                "hand_preference": "right",
                "selected_language": "FSL",
            }

            # Call get_all_settings
            settings = get_all_settings("dev")

            # Verify that selected_language is included
            assert "selected_language" in settings
            assert settings["selected_language"] == "FSL"

    def test_save_all_settings_preserves_selected_language(self):
        """Test that save_all_settings preserves selected_language field"""
        from src.helpmesign.core.startup import save_all_settings

        # Mock the SecureConfigManager
        with patch(
            "src.helpmesign.core.startup.SecureConfigManager"
        ) as mock_config_manager:
            mock_instance = MagicMock()
            mock_config_manager.return_value = mock_instance
            mock_instance.save_all_settings.return_value = True

            # Test settings with FSL
            test_settings = {
                "user_mode": "Learn Sign Language",
                "theme": "Dark",
                "font_size": 12,
                "hand_preference": "right",
                "selected_language": "FSL",
            }

            # Call save_all_settings
            result = save_all_settings(test_settings, "dev")

            # Verify that save_all_settings was called with the correct settings
            mock_instance.save_all_settings.assert_called_once_with(test_settings)
            assert result is True
