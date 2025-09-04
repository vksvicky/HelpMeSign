#!/usr/bin/env python3
"""
Tests for theme validation and settings timestamp functionality
"""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.helpmesign.core.startup import (
    SecureConfigManager,
    get_settings_with_timestamps,
)


class TestThemeValidation:
    """Test theme validation functionality"""

    def test_validate_theme_valid_values(self, isolated_config_manager):
        """Test that valid theme values pass validation"""
        config_manager = isolated_config_manager

        # Test valid themes
        assert config_manager._validate_theme("Light") is True
        assert config_manager._validate_theme("Dark") is True
        assert config_manager._validate_theme("System") is True

    def test_validate_theme_invalid_values(self, isolated_config_manager):
        """Test that invalid theme values fail validation"""
        config_manager = isolated_config_manager

        # Test invalid themes
        assert config_manager._validate_theme("Invalid") is False
        assert config_manager._validate_theme("") is False
        assert config_manager._validate_theme(None) is False
        assert config_manager._validate_theme("light") is False  # Case sensitive
        assert config_manager._validate_theme("DARK") is False  # Case sensitive

    def test_set_theme_with_validation(self, isolated_config_manager):
        """Test that set_theme validates theme before saving"""
        config_manager = isolated_config_manager

        with patch.object(config_manager, "load_config", return_value={}), patch.object(
            config_manager, "save_config", return_value=True
        ) as mock_save:

            # Valid theme should save
            result = config_manager.set_theme("Light")
            assert result is True
            mock_save.assert_called_once()

            # Check that timestamp was added
            call_args = mock_save.call_args[0][0]
            assert call_args["theme"] == "Light"
            assert "last_updated" in call_args
            assert "theme_last_changed" in call_args

    def test_set_theme_invalid_theme(self, isolated_config_manager):
        """Test that set_theme rejects invalid themes"""
        config_manager = isolated_config_manager

        with patch.object(config_manager, "load_config", return_value={}), patch.object(
            config_manager, "save_config"
        ) as mock_save:

            # Invalid theme should not save
            result = config_manager.set_theme("Invalid")
            assert result is False
            mock_save.assert_not_called()

    def test_validate_settings_comprehensive(self, isolated_config_manager):
        """Test comprehensive settings validation"""
        config_manager = isolated_config_manager

        # Valid settings
        valid_settings = {
            "theme": "Light",
            "font_size": 12,
            "user_mode": "Sign & Translate",
            "hand_preference": "right",
        }
        assert config_manager._validate_settings(valid_settings) is True

        # Invalid theme
        invalid_theme = valid_settings.copy()
        invalid_theme["theme"] = "Invalid"
        assert config_manager._validate_settings(invalid_theme) is False

        # Invalid font size (too small)
        invalid_font_small = valid_settings.copy()
        invalid_font_small["font_size"] = 5
        assert config_manager._validate_settings(invalid_font_small) is False

        # Invalid font size (too large)
        invalid_font_large = valid_settings.copy()
        invalid_font_large["font_size"] = 100
        assert config_manager._validate_settings(invalid_font_large) is False

        # Invalid font size (not integer)
        invalid_font_type = valid_settings.copy()
        invalid_font_type["font_size"] = "12"
        assert config_manager._validate_settings(invalid_font_type) is False

        # Invalid user mode
        invalid_mode = valid_settings.copy()
        invalid_mode["user_mode"] = "Invalid Mode"
        assert config_manager._validate_settings(invalid_mode) is False

        # Invalid hand preference
        invalid_hand = valid_settings.copy()
        invalid_hand["hand_preference"] = "middle"
        assert config_manager._validate_settings(invalid_hand) is False

    def test_save_all_settings_with_validation(self, isolated_config_manager):
        """Test that save_all_settings validates settings before saving"""
        config_manager = isolated_config_manager

        with patch.object(config_manager, "load_config", return_value={}), patch.object(
            config_manager, "save_config", return_value=True
        ) as mock_save:

            # Valid settings should save
            valid_settings = {
                "theme": "Light",
                "font_size": 12,
                "user_mode": "Sign & Translate",
            }
            result = config_manager.save_all_settings(valid_settings)
            assert result is True
            mock_save.assert_called_once()

            # Check that timestamps were added
            call_args = mock_save.call_args[0][0]
            assert call_args["theme"] == "Light"
            assert call_args["font_size"] == 12
            assert call_args["user_mode"] == "Sign & Translate"
            assert "last_updated" in call_args
            assert "theme_last_changed" in call_args
            assert "font_size_last_changed" in call_args
            assert "user_mode_last_changed" in call_args

    def test_save_all_settings_invalid_settings(self, isolated_config_manager):
        """Test that save_all_settings rejects invalid settings"""
        config_manager = isolated_config_manager

        with patch.object(config_manager, "load_config", return_value={}), patch.object(
            config_manager, "save_config"
        ) as mock_save:

            # Invalid settings should not save
            invalid_settings = {
                "theme": "Invalid",
                "font_size": 5,
                "user_mode": "Invalid Mode",
            }
            result = config_manager.save_all_settings(invalid_settings)
            assert result is False
            mock_save.assert_not_called()


class TestSettingsTimestamps:
    """Test settings timestamp functionality"""

    def test_get_settings_with_timestamps(self, isolated_config_manager):
        """Test getting settings with timestamp information"""
        config_manager = isolated_config_manager

        mock_config = {
            "theme": "Light",
            "font_size": 12,
            "user_mode": "Sign & Translate",
            "hand_preference": "right",
            "last_updated": "2025-01-01T12:00:00",
            "theme_last_changed": "2025-01-01T12:00:00",
            "font_size_last_changed": "2025-01-01T12:00:00",
        }

        with patch.object(
            config_manager, "load_config", return_value=mock_config
        ), patch.object(
            config_manager,
            "get_all_settings",
            return_value={
                "theme": "Light",
                "font_size": 12,
                "user_mode": "Sign & Translate",
                "hand_preference": "right",
            },
        ):

            result = config_manager.get_settings_with_timestamps()

            assert result["theme"] == "Light"
            assert result["font_size"] == 12
            assert result["last_updated"] == "2025-01-01T12:00:00"
            assert result["theme_last_changed"] == "2025-01-01T12:00:00"
            assert result["font_size_last_changed"] == "2025-01-01T12:00:00"
            assert result["user_mode_last_changed"] == "Never"  # Not in mock config

    def test_get_settings_with_timestamps_missing_data(self, isolated_config_manager):
        """Test getting settings with timestamps when some data is missing"""
        config_manager = isolated_config_manager

        mock_config = {}  # Empty config

        with patch.object(
            config_manager, "load_config", return_value=mock_config
        ), patch.object(
            config_manager,
            "get_all_settings",
            return_value={
                "theme": "Light",
                "font_size": 12,
                "user_mode": "Sign & Translate",
                "hand_preference": "right",
            },
        ):

            result = config_manager.get_settings_with_timestamps()

            assert result["theme"] == "Light"
            assert result["font_size"] == 12
            assert result["last_updated"] == "Never"
            assert result["theme_last_changed"] == "Never"
            assert result["font_size_last_changed"] == "Never"
            assert result["user_mode_last_changed"] == "Never"
            assert result["hand_preference_last_changed"] == "Never"

    def test_get_settings_with_timestamps_global_function(self):
        """Test the global get_settings_with_timestamps function"""
        with patch(
            "src.helpmesign.core.startup.SecureConfigManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager

            expected_result = {
                "theme": "Light",
                "font_size": 12,
                "last_updated": "2025-01-01T12:00:00",
            }
            mock_manager.get_settings_with_timestamps.return_value = expected_result

            result = get_settings_with_timestamps()

            assert result == expected_result
            mock_manager.get_settings_with_timestamps.assert_called_once()

    def test_get_settings_with_timestamps_error_handling(self, isolated_config_manager):
        """Test error handling in get_settings_with_timestamps"""
        config_manager = isolated_config_manager

        with patch.object(
            config_manager, "load_config", side_effect=Exception("Test error")
        ):
            result = config_manager.get_settings_with_timestamps()
            assert result == {}

    def test_timestamp_tracking_on_changes(self, isolated_config_manager):
        """Test that timestamps are only added when values actually change"""
        config_manager = isolated_config_manager

        existing_config = {
            "theme": "Light",
            "font_size": 12,
            "user_mode": "Sign & Translate",
            "last_updated": "2025-01-01T12:00:00",
        }

        with patch.object(
            config_manager, "load_config", return_value=existing_config
        ), patch.object(config_manager, "save_config", return_value=True) as mock_save:

            # Only change theme, not font_size
            new_settings = {
                "theme": "Dark",
                "font_size": 12,  # Same as existing
                "user_mode": "Learn Sign Language",
            }

            result = config_manager.save_all_settings(new_settings)
            assert result is True

            # Check that timestamps were added only for changed values
            call_args = mock_save.call_args[0][0]
            assert call_args["theme"] == "Dark"
            assert call_args["font_size"] == 12
            assert call_args["user_mode"] == "Learn Sign Language"
            assert "theme_last_changed" in call_args
            assert "user_mode_last_changed" in call_args
            # font_size_last_changed should not be added since it didn't change
            assert "font_size_last_changed" not in call_args


if __name__ == "__main__":
    pytest.main([__file__])
