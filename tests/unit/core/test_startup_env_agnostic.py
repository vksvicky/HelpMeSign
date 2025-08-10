#!/usr/bin/env python3
"""
Env-agnostic tests for SecureConfigManager behavior.
"""

from unittest.mock import mock_open, patch


def test_secure_config_manager_save_config_has_no_environment():
    """Saving config should not include an 'environment' field anymore."""
    from src.helpmesign.core.startup import SecureConfigManager

    manager = SecureConfigManager()

    # Patch HMAC and file ops
    with patch.object(manager, "_create_hmac", return_value=b"sig"):
        with patch("builtins.open", mock_open()) as m:
            with patch("os.chmod"):
                manager.save_config({"user_mode": "sign"})

                # First write should contain JSON data without 'environment'
                handle = m()
                first_write = handle.write.call_args_list[0][0][0]
                assert b"environment" not in first_write


def test_secure_config_manager_load_config_ignores_environment_field():
    """Loading a config that contains an environment field should still succeed."""
    from src.helpmesign.core.startup import SecureConfigManager

    manager = SecureConfigManager()

    # Prepare a config payload that includes an environment field
    import json

    payload = json.dumps({"user_mode": "learn", "environment": "dev"})
    file_bytes = payload.encode("utf-8") + b"\n---SIGNATURE---\n" + b"fake"

    with patch("builtins.open", mock_open(read_data=file_bytes)):
        with patch.object(manager, "_verify_hmac", return_value=True):
            with patch("pathlib.Path.exists", return_value=True):
                loaded = manager.load_config()

    # Should return the parsed config (environment presence does not block)
    assert loaded.get("user_mode") == "learn"
    assert "environment" in loaded
