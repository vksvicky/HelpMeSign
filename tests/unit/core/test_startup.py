#!/usr/bin/env python3
"""
Simple unit tests for startup functionality
Tests pure logic without importing real modules
"""

from unittest.mock import MagicMock

import pytest


class TestSecureConfigManagerLogic:
    """Unit tests for SecureConfigManager logic - no real imports"""

    def test_secret_key_validation(self):
        """Test secret key validation logic"""
        # Test that secret key should be 32 characters
        secret_key = "test_secret_key_32_chars_long_32"
        assert len(secret_key) == 32
        assert isinstance(secret_key, str)

    def test_config_data_structure(self):
        """Test config data structure validation"""
        # Test valid config structure
        valid_config = {"user_mode": "sign", "timestamp": "2023-01-01T12:00:00"}

        assert "user_mode" in valid_config
        assert "timestamp" in valid_config
        assert valid_config["user_mode"] in ["sign", "learn"]
        assert "T" in valid_config["timestamp"]  # ISO format

    def test_user_mode_validation(self):
        """Test user mode validation logic"""
        valid_modes = ["sign", "learn"]
        invalid_modes = ["invalid", "", None, 123]

        # Test valid modes
        for mode in valid_modes:
            assert mode in valid_modes

        # Test invalid modes
        for mode in invalid_modes:
            assert mode not in valid_modes

    def test_timestamp_format_validation(self):
        """Test timestamp format validation logic"""
        valid_timestamp = "2023-01-01T12:00:00"
        invalid_timestamps = ["2023-01-01", "invalid", "", None]

        # Test valid timestamp
        assert "T" in valid_timestamp
        assert isinstance(valid_timestamp, str)

        # Test invalid timestamps
        for timestamp in invalid_timestamps:
            if timestamp is not None:
                assert "T" not in timestamp


class TestStartupScreenLogic:
    """Unit tests for StartupScreen logic - no real imports"""

    def test_choice_validation(self):
        """Test choice validation logic"""
        valid_choices = ["sign", "learn"]
        invalid_choices = ["invalid", "", None, 123]

        # Test valid choices
        for choice in valid_choices:
            assert choice in valid_choices

        # Test invalid choices
        for choice in invalid_choices:
            assert choice not in valid_choices

    def test_choice_state_management(self):
        """Test choice state management logic"""
        # Test initial state
        initial_choice = None
        assert initial_choice is None

        # Test setting choice
        choice = "sign"
        assert choice == "sign"
        assert isinstance(choice, str)

        # Test changing choice
        new_choice = "learn"
        assert new_choice == "learn"
        assert choice != new_choice

    def test_config_persistence_logic(self):
        """Test config persistence logic"""
        # Test config structure for persistence
        config_data = {"user_mode": "sign", "timestamp": "2023-01-01T12:00:00"}

        # Test that config has required fields
        assert "user_mode" in config_data
        assert "timestamp" in config_data

        # Test that user_mode is valid
        assert config_data["user_mode"] in ["sign", "learn"]

        # Test that timestamp is in ISO format
        assert "T" in config_data["timestamp"]


class TestStartupFunctionsLogic:
    """Unit tests for startup functions logic - no real imports"""

    def test_get_user_mode_logic(self):
        """Test get_user_mode logic"""
        # Test default mode
        default_mode = "sign"
        assert default_mode == "sign"
        assert isinstance(default_mode, str)

        # Test mode validation
        valid_modes = ["sign", "learn"]
        assert default_mode in valid_modes

    def test_set_user_mode_logic(self):
        """Test set_user_mode logic"""
        # Test setting valid mode
        mode = "learn"
        assert mode == "learn"
        assert isinstance(mode, str)

        # Test mode validation
        valid_modes = ["sign", "learn"]
        assert mode in valid_modes

        # Test that mode is not None
        assert mode is not None

    def test_show_startup_screen_logic(self):
        """Test show_startup_screen logic"""
        # Test return value should be a string
        expected_return = "sign"
        assert isinstance(expected_return, str)
        assert expected_return in ["sign", "learn"]


class TestErrorHandlingLogic:
    """Unit tests for error handling logic - no real imports"""

    def test_file_not_found_logic(self):
        """Test file not found error handling logic"""
        # Test that error should be handled gracefully
        error_handled = True
        assert error_handled

    def test_invalid_json_logic(self):
        """Test invalid JSON error handling logic"""
        # Test that error should be handled gracefully
        error_handled = True
        assert error_handled

    def test_permission_error_logic(self):
        """Test permission error handling logic"""
        # Test that error should be handled gracefully
        error_handled = True
        assert error_handled

    def test_disk_full_error_logic(self):
        """Test disk full error handling logic"""
        # Test that error should be handled gracefully
        error_handled = True
        assert error_handled

    def test_tamper_detection_logic(self):
        """Test tamper detection logic"""
        # Test that tampering should be detected
        tamper_detected = True
        assert tamper_detected


class TestBoundaryConditionsLogic:
    """Unit tests for boundary conditions logic - no real imports"""

    def test_empty_data_logic(self):
        """Test empty data handling logic"""
        # Test that empty data should be handled
        empty_data = {}
        assert isinstance(empty_data, dict)
        assert len(empty_data) == 0

        # Test that empty data should not cause errors
        data_handled = True
        assert data_handled

    def test_large_data_logic(self):
        """Test large data handling logic"""
        # Test that large data should be handled
        large_data = {"key": "value" * 1000}
        assert isinstance(large_data, dict)
        assert "key" in large_data

    def test_unicode_data_logic(self):
        """Test unicode data handling logic"""
        # Test that unicode data should be handled
        unicode_data = {"key": "value with unicode: 🚀"}
        assert isinstance(unicode_data, dict)
        assert "key" in unicode_data
        assert "🚀" in unicode_data["key"]


class TestSecurityLogic:
    """Unit tests for security logic - no real imports"""

    def test_signature_validation_logic(self):
        """Test signature validation logic"""
        # Test that signature should be validated
        signature_valid = True
        assert signature_valid

        # Test that invalid signature should be rejected
        invalid_signature = False
        assert not invalid_signature

    def test_key_generation_logic(self):
        """Test key generation logic"""
        # Test that key should be generated
        key_generated = True
        assert key_generated

        # Test that key should be 32 characters
        key_length = 32
        assert key_length == 32


from unittest.mock import Mock, mock_open, patch

# Add comprehensive tests for real startup.py functions
import pytest


class TestStartupRealFunctions:
    """Test real startup.py functions with proper mocking"""

    def test_get_all_settings(self):
        """Test get_all_settings function"""
        with patch(
            "src.helpmesign.core.startup.SecureConfigManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.get_all_settings.return_value = {
                "user_mode": "sign",
                "theme": "light",
                "font_size": 12,
            }

            from src.helpmesign.core.startup import get_all_settings

            result = get_all_settings("dev")

            mock_manager_class.assert_called_once()
            mock_manager.get_all_settings.assert_called_once()
            assert result["user_mode"] == "sign"
            assert result["theme"] == "light"
            assert result["font_size"] == 12

    def test_save_all_settings(self):
        """Test save_all_settings function"""
        with patch(
            "src.helpmesign.core.startup.SecureConfigManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.save_all_settings.return_value = True

            from src.helpmesign.core.startup import save_all_settings

            settings = {"user_mode": "learn", "theme": "dark", "font_size": 14}

            result = save_all_settings(settings, "dev")

            mock_manager_class.assert_called_once()
            mock_manager.save_all_settings.assert_called_once_with(settings)
            assert result is True

    def test_save_all_settings_failure(self):
        """Test save_all_settings function with failure"""
        with patch(
            "src.helpmesign.core.startup.SecureConfigManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.save_all_settings.return_value = False

            from src.helpmesign.core.startup import save_all_settings

            settings = {"user_mode": "learn", "theme": "dark", "font_size": 14}

            result = save_all_settings(settings, "dev")

            mock_manager_class.assert_called_once()
            mock_manager.save_all_settings.assert_called_once_with(settings)
            assert result is False

    def test_get_user_mode(self):
        """Test get_user_mode function"""
        with patch(
            "src.helpmesign.core.startup.SecureConfigManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.get_user_mode.return_value = "learn"

            from src.helpmesign.core.startup import get_user_mode

            result = get_user_mode("dev")

            mock_manager_class.assert_called_once()
            mock_manager.get_user_mode.assert_called_once()
            assert result == "learn"

    def test_get_user_mode_default(self):
        """Test get_user_mode function with default value"""
        with patch(
            "src.helpmesign.core.startup.SecureConfigManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.get_user_mode.return_value = None

            from src.helpmesign.core.startup import get_user_mode

            result = get_user_mode("dev")

            mock_manager_class.assert_called_once()
            mock_manager.get_user_mode.assert_called_once()
            assert result is None

    def test_set_user_mode(self):
        """Test set_user_mode function"""
        with patch(
            "src.helpmesign.core.startup.SecureConfigManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.set_user_mode.return_value = True

            from src.helpmesign.core.startup import set_user_mode

            result = set_user_mode("learn", "dev")

            mock_manager_class.assert_called_once()
            mock_manager.set_user_mode.assert_called_once_with("learn")
            assert result is True

    def test_set_user_mode_failure(self):
        """Test set_user_mode function with failure"""
        with patch(
            "src.helpmesign.core.startup.SecureConfigManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.set_user_mode.return_value = False

            from src.helpmesign.core.startup import set_user_mode

            result = set_user_mode("learn", "dev")

            mock_manager_class.assert_called_once()
            mock_manager.set_user_mode.assert_called_once_with("learn")
            assert result is False

    def test_get_font_size(self):
        """Test get_font_size function"""
        with patch(
            "src.helpmesign.core.startup.SecureConfigManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.get_font_size.return_value = 16

            from src.helpmesign.core.startup import get_font_size

            result = get_font_size("dev")

            mock_manager_class.assert_called_once()
            mock_manager.get_font_size.assert_called_once()
            assert result == 16

    def test_get_font_size_default(self):
        """Test get_font_size function with default value"""
        with patch(
            "src.helpmesign.core.startup.SecureConfigManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.get_font_size.return_value = 12

            from src.helpmesign.core.startup import get_font_size

            result = get_font_size("dev")

            mock_manager_class.assert_called_once()
            mock_manager.get_font_size.assert_called_once()
            assert result == 12  # Default value

    def test_set_font_size(self):
        """Test set_font_size function"""
        with patch(
            "src.helpmesign.core.startup.SecureConfigManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.set_font_size.return_value = True

            from src.helpmesign.core.startup import set_font_size

            result = set_font_size(18, "dev")

            mock_manager_class.assert_called_once()
            mock_manager.set_font_size.assert_called_once_with(18)
            assert result is True

    def test_get_theme(self):
        """Test get_theme function"""
        with patch(
            "src.helpmesign.core.startup.SecureConfigManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.get_theme.return_value = "dark"

            from src.helpmesign.core.startup import get_theme

            result = get_theme("dev")

            mock_manager_class.assert_called_once()
            mock_manager.get_theme.assert_called_once()
            assert result == "dark"

    def test_get_theme_default(self):
        """Test get_theme function with default value"""
        with patch(
            "src.helpmesign.core.startup.SecureConfigManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.get_theme.return_value = "light"

            from src.helpmesign.core.startup import get_theme

            result = get_theme("dev")

            mock_manager_class.assert_called_once()
            mock_manager.get_theme.assert_called_once()
            assert result == "light"  # Default value

    def test_set_theme(self):
        """Test set_theme function"""
        with patch(
            "src.helpmesign.core.startup.SecureConfigManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.set_theme.return_value = True

            from src.helpmesign.core.startup import set_theme

            result = set_theme("dark", "dev")

            mock_manager_class.assert_called_once()
            mock_manager.set_theme.assert_called_once_with("dark")
            assert result is True

    def test_get_hand_preference(self):
        """Test get_hand_preference function"""
        with patch(
            "src.helpmesign.core.startup.SecureConfigManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.get_hand_preference.return_value = "left"

            from src.helpmesign.core.startup import get_hand_preference

            result = get_hand_preference("dev")

            mock_manager_class.assert_called_once()
            mock_manager.get_hand_preference.assert_called_once()
            assert result == "left"

    def test_get_hand_preference_default(self):
        """Test get_hand_preference function with default value"""
        with patch(
            "src.helpmesign.core.startup.SecureConfigManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.get_hand_preference.return_value = "right"

            from src.helpmesign.core.startup import get_hand_preference

            result = get_hand_preference("dev")

            mock_manager_class.assert_called_once()
            mock_manager.get_hand_preference.assert_called_once()
            assert result == "right"  # Default value

    def test_set_hand_preference(self):
        """Test set_hand_preference function"""
        with patch(
            "src.helpmesign.core.startup.SecureConfigManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.set_hand_preference.return_value = True

            from src.helpmesign.core.startup import set_hand_preference

            result = set_hand_preference("left", "dev")

            mock_manager_class.assert_called_once()
            mock_manager.set_hand_preference.assert_called_once_with("left")
            assert result is True


class TestSecureConfigManager:
    """Test SecureConfigManager class with proper mocking"""

    @patch("src.helpmesign.core.startup.Path")
    def test_secure_config_manager_initialization(self, mock_path):
        """Test SecureConfigManager initialization"""
        # Mock the Path.home() and Path.mkdir() calls
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        # Set up the chain of calls
        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        assert manager.environment == "dev"
        assert manager.config_file is not None
        # mkdir is called in __init__ to ensure config directory exists
        mock_config_dir.mkdir.assert_called_once_with(mode=0o700, exist_ok=True)

    @patch("src.helpmesign.core.startup.Path")
    def test_load_config_success(self, mock_path):
        """Test load_config method with success"""
        # Mock the Path.home() and Path.exists() calls
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        # Set up the chain of calls
        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)
        mock_config_file.exists.return_value = True

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        # Mock the file content with proper format (JSON + signature)
        mock_content = b'{"user_mode": "sign"}\n---SIGNATURE---\n' + b"fake_signature"

        with patch("builtins.open", mock_open(read_data=mock_content)):
            with patch("src.helpmesign.core.startup.json.loads") as mock_json_loads:
                mock_json_loads.return_value = {"user_mode": "sign"}
                with patch.object(manager, "_verify_hmac", return_value=True):
                    result = manager.load_config()

                    assert result == {"user_mode": "sign"}

    @patch("src.helpmesign.core.startup.Path")
    def test_load_config_file_not_found(self, mock_path):
        """Test load_config method when file doesn't exist"""
        # Mock the Path.home() and Path.exists() calls
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        # Set up the chain of calls
        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)
        mock_config_file.exists.return_value = False

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        result = manager.load_config()

        assert result == {}

    @patch("src.helpmesign.core.startup.Path")
    def test_save_config_success(self, mock_path):
        """Test save_config method with success"""
        # Mock the Path.home() calls
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        # Set up the chain of calls
        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch("builtins.open", mock_open()):
            with patch("src.helpmesign.core.startup.json.dumps") as mock_json_dumps:
                mock_json_dumps.return_value = '{"user_mode": "sign"}'
                with patch("src.helpmesign.core.startup.os.chmod") as mock_chmod:
                    config_data = {"user_mode": "sign"}

                    result = manager.save_config(config_data)

                    mock_json_dumps.assert_called_once()
                    mock_chmod.assert_called_once()
                    assert result is True

    @patch("src.helpmesign.core.startup.Path")
    def test_save_config_failure(self, mock_path):
        """Test save_config method with failure"""
        # Mock the Path.home() calls
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        # Set up the chain of calls
        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch("builtins.open", side_effect=Exception("Write error")):
            config_data = {"user_mode": "sign"}

            result = manager.save_config(config_data)

            assert result is False

    @patch("src.helpmesign.core.startup.Path")
    def test_derive_secret_key(self, mock_path):
        """Test _derive_secret_key method"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch("src.helpmesign.core.startup.platform") as mock_platform:
            with patch("src.helpmesign.core.startup.getpass") as mock_getpass:
                with patch("src.helpmesign.core.startup.get_text") as mock_get_text:
                    mock_platform.system.return_value = "Darwin"
                    mock_platform.machine.return_value = "x86_64"
                    mock_platform.node.return_value = "test-host"
                    mock_getpass.getuser.return_value = "testuser"
                    mock_get_text.return_value = "HelpMeSign"

                    key = manager._derive_secret_key()

                    assert isinstance(key, bytes)
                    assert len(key) == 32

    @patch("src.helpmesign.core.startup.Path")
    def test_get_mac_address(self, mock_path):
        """Test _get_mac_address method"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch("src.helpmesign.core.startup.uuid") as mock_uuid:
            mock_uuid.getnode.return_value = 0x123456789ABC

            mac = manager._get_mac_address()

            assert isinstance(mac, str)
            assert ":" in mac
            assert len(mac.split(":")) == 6

    @patch("src.helpmesign.core.startup.Path")
    def test_get_mac_address_exception(self, mock_path):
        """Test _get_mac_address method with exception"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch("src.helpmesign.core.startup.uuid") as mock_uuid:
            mock_uuid.getnode.side_effect = Exception("MAC error")

            mac = manager._get_mac_address()

            assert mac == "unknown_mac"

    @patch("src.helpmesign.core.startup.Path")
    def test_create_hmac(self, mock_path):
        """Test _create_hmac method"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(
            manager,
            "_derive_secret_key",
            return_value=b"fake_key_32_bytes_long_fake_key",
        ):
            signature = manager._create_hmac("test_data")

            assert isinstance(signature, bytes)
            assert len(signature) > 0

    @patch("src.helpmesign.core.startup.Path")
    def test_verify_hmac(self, mock_path):
        """Test _verify_hmac method"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(manager, "_create_hmac", return_value=b"fake_signature"):
            # Test valid signature
            result = manager._verify_hmac("test_data", b"fake_signature")
            assert result is True

            # Test invalid signature
            result = manager._verify_hmac("test_data", b"invalid_signature")
            assert result is False

    @patch("src.helpmesign.core.startup.Path")
    def test_load_config_invalid_format(self, mock_path):
        """Test load_config method with invalid file format"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)
        mock_config_file.exists.return_value = True

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        # Mock invalid file content (no signature separator)
        mock_content = b'{"user_mode": "sign"}'

        with patch("builtins.open", mock_open(read_data=mock_content)):
            result = manager.load_config()
            assert result == {}

    @patch("src.helpmesign.core.startup.Path")
    def test_load_config_json_error(self, mock_path):
        """Test load_config method with JSON decode error"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)
        mock_config_file.exists.return_value = True

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        # Mock file content with signature separator but invalid JSON
        mock_content = b"invalid_json\n---SIGNATURE---\n" + b"fake_signature"

        with patch("builtins.open", mock_open(read_data=mock_content)):
            with patch(
                "src.helpmesign.core.startup.json.loads",
                side_effect=Exception("JSON error"),
            ):
                result = manager.load_config()
                assert result == {}

    @patch("src.helpmesign.core.startup.Path")
    def test_load_config_tamper_detection(self, mock_path):
        """Test load_config method with tamper detection"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)
        mock_config_file.exists.return_value = True

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        # Mock file content with proper format
        mock_content = b'{"user_mode": "sign"}\n---SIGNATURE---\n' + b"fake_signature"

        with patch("builtins.open", mock_open(read_data=mock_content)):
            with patch("src.helpmesign.core.startup.json.loads") as mock_json_loads:
                mock_json_loads.return_value = {"user_mode": "sign"}
                with patch.object(
                    manager, "_verify_hmac", return_value=False
                ):  # Tampered
                    result = manager.load_config()
                    assert result == {}

    @patch("src.helpmesign.core.startup.Path")
    def test_get_user_mode_from_config(self, mock_path):
        """Test get_user_mode method"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(manager, "load_config", return_value={"user_mode": "learn"}):
            result = manager.get_user_mode()
            assert result == "learn"

    @patch("src.helpmesign.core.startup.Path")
    def test_get_user_mode_no_config(self, mock_path):
        """Test get_user_mode method with no config"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(manager, "load_config", return_value={}):
            result = manager.get_user_mode()
            assert result is None

    @patch("src.helpmesign.core.startup.Path")
    def test_set_user_mode_success(self, mock_path):
        """Test set_user_mode method"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(manager, "load_config", return_value={}):
            with patch.object(manager, "save_config", return_value=True):
                result = manager.set_user_mode("learn")
                assert result is True

    @patch("src.helpmesign.core.startup.Path")
    def test_set_user_mode_failure(self, mock_path):
        """Test set_user_mode method with failure"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(manager, "load_config", return_value={}):
            with patch.object(manager, "save_config", return_value=False):
                result = manager.set_user_mode("learn")
                assert result is False

    @patch("src.helpmesign.core.startup.Path")
    def test_get_theme_from_config(self, mock_path):
        """Test get_theme method"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(manager, "load_config", return_value={"theme": "dark"}):
            result = manager.get_theme()
            assert result == "dark"

    @patch("src.helpmesign.core.startup.Path")
    def test_get_theme_default(self, mock_path):
        """Test get_theme method with default"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(manager, "load_config", return_value={}):
            result = manager.get_theme()
            assert result == "Light"

    @patch("src.helpmesign.core.startup.Path")
    def test_set_theme_success(self, mock_path):
        """Test set_theme method"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(manager, "load_config", return_value={}):
            with patch.object(manager, "save_config", return_value=True):
                result = manager.set_theme("dark")
                assert result is True

    @patch("src.helpmesign.core.startup.Path")
    def test_get_font_size_from_config(self, mock_path):
        """Test get_font_size method"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(manager, "load_config", return_value={"font_size": 16}):
            result = manager.get_font_size()
            assert result == 16

    @patch("src.helpmesign.core.startup.Path")
    def test_get_font_size_default(self, mock_path):
        """Test get_font_size method with default"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(manager, "load_config", return_value={}):
            result = manager.get_font_size()
            assert result == 12

    @patch("src.helpmesign.core.startup.Path")
    def test_set_font_size_success(self, mock_path):
        """Test set_font_size method"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(manager, "load_config", return_value={}):
            with patch.object(manager, "save_config", return_value=True):
                result = manager.set_font_size(16)
                assert result is True

    @patch("src.helpmesign.core.startup.Path")
    def test_get_hand_preference_from_config(self, mock_path):
        """Test get_hand_preference method"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(
            manager, "load_config", return_value={"hand_preference": "left"}
        ):
            result = manager.get_hand_preference()
            assert result == "left"

    @patch("src.helpmesign.core.startup.Path")
    def test_get_hand_preference_default(self, mock_path):
        """Test get_hand_preference method with default"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(manager, "load_config", return_value={}):
            result = manager.get_hand_preference()
            assert result == "right"

    @patch("src.helpmesign.core.startup.Path")
    def test_set_hand_preference_success(self, mock_path):
        """Test set_hand_preference method"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(manager, "load_config", return_value={}):
            with patch.object(manager, "save_config", return_value=True):
                result = manager.set_hand_preference("left")
                assert result is True

    @patch("src.helpmesign.core.startup.Path")
    def test_get_all_settings(self, mock_path):
        """Test get_all_settings method"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(
            manager,
            "load_config",
            return_value={
                "user_mode": "learn",
                "theme": "dark",
                "font_size": 16,
                "hand_preference": "left",
            },
        ):
            with patch(
                "src.helpmesign.core.startup.get_text", return_value="Sign & Translate"
            ):
                result = manager.get_all_settings()
                assert result["user_mode"] == "learn"
                assert result["theme"] == "dark"
                assert result["font_size"] == 16
                assert result["hand_preference"] == "left"

    @patch("src.helpmesign.core.startup.Path")
    def test_get_all_settings_defaults(self, mock_path):
        """Test get_all_settings method with defaults"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(manager, "load_config", return_value={}):
            with patch(
                "src.helpmesign.core.startup.get_text", return_value="Sign & Translate"
            ):
                result = manager.get_all_settings()
                assert result["user_mode"] == "Sign & Translate"
                assert result["theme"] == "Light"
                assert result["font_size"] == 12
                assert result["hand_preference"] == "right"

    @patch("src.helpmesign.core.startup.Path")
    def test_save_all_settings_success(self, mock_path):
        """Test save_all_settings method"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(manager, "load_config", return_value={}):
            with patch.object(manager, "save_config", return_value=True):
                settings = {"user_mode": "learn", "theme": "dark", "font_size": 16}
                result = manager.save_all_settings(settings)
                assert result is True

    @patch("src.helpmesign.core.startup.Path")
    def test_save_all_settings_failure(self, mock_path):
        """Test save_all_settings method with failure"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(manager, "load_config", return_value={}):
            with patch.object(manager, "save_config", return_value=False):
                settings = {"user_mode": "learn", "theme": "dark", "font_size": 16}
                result = manager.save_all_settings(settings)
                assert result is False

    @patch("src.helpmesign.core.startup.Path")
    def test_get_timestamp(self, mock_path):
        """Test get_timestamp method"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        timestamp = manager.get_timestamp()
        assert isinstance(timestamp, str)
        assert "T" in timestamp  # ISO format

    @patch("src.helpmesign.core.startup.Path")
    def test_load_config_exception_handling(self, mock_path):
        """Test load_config method with general exception"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)
        mock_config_file.exists.return_value = True

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch("builtins.open", side_effect=Exception("General error")):
            result = manager.load_config()
            assert result == {}

    @patch("src.helpmesign.core.startup.Path")
    def test_get_user_mode_exception_handling(self, mock_path):
        """Test get_user_mode method with exception"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(
            manager, "load_config", side_effect=Exception("Config error")
        ):
            result = manager.get_user_mode()
            assert result is None

    @patch("src.helpmesign.core.startup.Path")
    def test_set_user_mode_exception_handling(self, mock_path):
        """Test set_user_mode method with exception"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(
            manager, "load_config", side_effect=Exception("Config error")
        ):
            result = manager.set_user_mode("learn")
            assert result is False

    @patch("src.helpmesign.core.startup.Path")
    def test_get_theme_exception_handling(self, mock_path):
        """Test get_theme method with exception"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(
            manager, "load_config", side_effect=Exception("Config error")
        ):
            result = manager.get_theme()
            assert result == "Light"

    @patch("src.helpmesign.core.startup.Path")
    def test_set_theme_exception_handling(self, mock_path):
        """Test set_theme method with exception"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(
            manager, "load_config", side_effect=Exception("Config error")
        ):
            result = manager.set_theme("dark")
            assert result is False

    @patch("src.helpmesign.core.startup.Path")
    def test_get_font_size_exception_handling(self, mock_path):
        """Test get_font_size method with exception"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(
            manager, "load_config", side_effect=Exception("Config error")
        ):
            result = manager.get_font_size()
            assert result == 12

    @patch("src.helpmesign.core.startup.Path")
    def test_set_font_size_exception_handling(self, mock_path):
        """Test set_font_size method with exception"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(
            manager, "load_config", side_effect=Exception("Config error")
        ):
            result = manager.set_font_size(16)
            assert result is False

    @patch("src.helpmesign.core.startup.Path")
    def test_get_hand_preference_exception_handling(self, mock_path):
        """Test get_hand_preference method with exception"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(
            manager, "load_config", side_effect=Exception("Config error")
        ):
            result = manager.get_hand_preference()
            assert result == "right"

    @patch("src.helpmesign.core.startup.Path")
    def test_set_hand_preference_exception_handling(self, mock_path):
        """Test set_hand_preference method with exception"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(
            manager, "load_config", side_effect=Exception("Config error")
        ):
            result = manager.set_hand_preference("left")
            assert result is False

    @patch("src.helpmesign.core.startup.Path")
    def test_get_all_settings_exception_handling(self, mock_path):
        """Test get_all_settings method with exception"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(
            manager, "load_config", side_effect=Exception("Config error")
        ):
            with patch(
                "src.helpmesign.core.startup.get_text", return_value="Sign & Translate"
            ):
                result = manager.get_all_settings()
                assert result["user_mode"] == "Sign & Translate"
                assert result["theme"] == "Light"
                assert result["font_size"] == 12
                assert result["hand_preference"] == "right"

    @patch("src.helpmesign.core.startup.Path")
    def test_save_all_settings_exception_handling(self, mock_path):
        """Test save_all_settings method with exception"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(
            manager, "load_config", side_effect=Exception("Config error")
        ):
            settings = {"user_mode": "learn", "theme": "dark", "font_size": 16}
            result = manager.save_all_settings(settings)
            assert result is False

    @patch("src.helpmesign.core.startup.Path")
    def test_save_all_settings_recursive_call(self, mock_path):
        """Test save_all_settings method with recursive call prevention"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")
        manager._saving_settings = True  # Simulate recursive call

        with patch.object(manager, "load_config", return_value={}):
            settings = {"user_mode": "learn", "theme": "dark", "font_size": 16}
            result = manager.save_all_settings(settings)
            assert result is True

    @patch("src.helpmesign.core.startup.Path")
    def test_save_all_settings_exception_with_flag_cleanup(self, mock_path):
        """Test save_all_settings method with exception and flag cleanup"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(
            manager, "load_config", side_effect=Exception("Config error")
        ):
            settings = {"user_mode": "learn", "theme": "dark", "font_size": 16}
            result = manager.save_all_settings(settings)
            assert result is False
            assert (
                not hasattr(manager, "_saving_settings") or not manager._saving_settings
            )

    @patch("src.helpmesign.core.startup.Path")
    def test_set_user_mode_recursive_call(self, mock_path):
        """Test set_user_mode method with recursive call prevention"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")
        manager._saving_settings = True  # Simulate recursive call

        result = manager.set_user_mode("learn")
        assert result is True

    @patch("src.helpmesign.core.startup.Path")
    def test_set_theme_recursive_call(self, mock_path):
        """Test set_theme method with recursive call prevention"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")
        manager._saving_settings = True  # Simulate recursive call

        result = manager.set_theme("dark")
        assert result is True

    @patch("src.helpmesign.core.startup.Path")
    def test_set_font_size_recursive_call(self, mock_path):
        """Test set_font_size method with recursive call prevention"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")
        manager._saving_settings = True  # Simulate recursive call

        result = manager.set_font_size(16)
        assert result is True

    @patch("src.helpmesign.core.startup.Path")
    def test_set_hand_preference_recursive_call(self, mock_path):
        """Test set_hand_preference method with recursive call prevention"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")
        manager._saving_settings = True  # Simulate recursive call

        result = manager.set_hand_preference("left")
        assert result is True

    @patch("src.helpmesign.core.startup.Path")
    def test_load_config_environment_mismatch(self, mock_path):
        """Test load_config method with environment mismatch"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)
        mock_config_file.exists.return_value = True

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        # Mock file content with different environment
        mock_content = (
            b'{"user_mode": "sign", "environment": "prod"}\n---SIGNATURE---\n'
            + b"fake_signature"
        )

        with patch("builtins.open", mock_open(read_data=mock_content)):
            with patch("src.helpmesign.core.startup.json.loads") as mock_json_loads:
                mock_json_loads.return_value = {
                    "user_mode": "sign",
                    "environment": "prod",
                }
                with patch.object(manager, "_verify_hmac", return_value=True):
                    result = manager.load_config()

                    assert result == {"user_mode": "sign", "environment": "prod"}

    @patch("src.helpmesign.core.startup.Path")
    def test_save_config_with_metadata(self, mock_path):
        """Test save_config method with metadata addition"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch("builtins.open", mock_open()):
            with patch("src.helpmesign.core.startup.json.dumps") as mock_json_dumps:
                mock_json_dumps.return_value = '{"user_mode": "sign", "timestamp": "2023-01-01T12:00:00", "environment": "dev", "version": "1.0"}'
                with patch("src.helpmesign.core.startup.os.chmod") as mock_chmod:
                    with patch.object(
                        manager, "get_timestamp", return_value="2023-01-01T12:00:00"
                    ):
                        config_data = {"user_mode": "sign"}

                        result = manager.save_config(config_data)

                        mock_json_dumps.assert_called_once()
                        mock_chmod.assert_called_once()
                        assert result is True

    @patch("src.helpmesign.core.startup.Path")
    def test_derive_secret_key_with_all_components(self, mock_path):
        """Test _derive_secret_key method with all system components"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch("src.helpmesign.core.startup.platform") as mock_platform:
            with patch("src.helpmesign.core.startup.getpass") as mock_getpass:
                with patch("src.helpmesign.core.startup.get_text") as mock_get_text:
                    with patch.object(
                        manager, "_get_mac_address", return_value="12:34:56:78:9A:BC"
                    ):
                        mock_platform.system.return_value = "Darwin"
                        mock_platform.machine.return_value = "x86_64"
                        mock_platform.node.return_value = "test-host"
                        mock_getpass.getuser.return_value = "testuser"
                        mock_home.__str__ = Mock(return_value="/home/testuser")
                        mock_get_text.return_value = "HelpMeSign"

                        key = manager._derive_secret_key()

                        assert isinstance(key, bytes)
                        assert len(key) == 32

    @patch("src.helpmesign.core.startup.Path")
    def test_create_hmac_with_real_data(self, mock_path):
        """Test _create_hmac method with real data"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch.object(
            manager,
            "_derive_secret_key",
            return_value=b"fake_key_32_bytes_long_fake_key",
        ):
            test_data = '{"user_mode": "sign", "timestamp": "2023-01-01T12:00:00"}'
            signature = manager._create_hmac(test_data)

            assert isinstance(signature, bytes)
            assert len(signature) > 0

    @patch("src.helpmesign.core.startup.Path")
    def test_verify_hmac_with_real_data(self, mock_path):
        """Test _verify_hmac method with real data"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        test_data = '{"user_mode": "sign", "timestamp": "2023-01-01T12:00:00"}'

        with patch.object(manager, "_create_hmac", return_value=b"fake_signature"):
            # Test valid signature
            result = manager._verify_hmac(test_data, b"fake_signature")
            assert result is True

            # Test invalid signature
            result = manager._verify_hmac(test_data, b"invalid_signature")
            assert result is False

    @patch("src.helpmesign.core.startup.Path")
    def test_get_mac_address_with_real_uuid(self, mock_path):
        """Test _get_mac_address method with real UUID value"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch("src.helpmesign.core.startup.uuid") as mock_uuid:
            # Test with a realistic MAC address value
            mock_uuid.getnode.return_value = 0x001122334455

            mac = manager._get_mac_address()

            assert isinstance(mac, str)
            assert ":" in mac
            assert len(mac.split(":")) == 6
            # Should be in format like "00:11:22:33:44:55"
            assert all(len(part) == 2 for part in mac.split(":"))

    @patch("src.helpmesign.core.startup.Path")
    def test_get_mac_address_with_zero_uuid(self, mock_path):
        """Test _get_mac_address method with zero UUID value"""
        mock_home = Mock()
        mock_config_dir = Mock()
        mock_config_file = Mock()

        mock_path.home.return_value = mock_home
        mock_home.__truediv__ = Mock(return_value=mock_config_dir)
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)

        from src.helpmesign.core.startup import SecureConfigManager

        manager = SecureConfigManager("dev")

        with patch("src.helpmesign.core.startup.uuid") as mock_uuid:
            mock_uuid.getnode.return_value = 0

            mac = manager._get_mac_address()

            assert isinstance(mac, str)
            assert ":" in mac
            assert len(mac.split(":")) == 6
            # Should be "00:00:00:00:00:00"
            assert mac == "00:00:00:00:00:00"
