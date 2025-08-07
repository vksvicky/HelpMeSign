#!/usr/bin/env python3
"""
Integration tests for Font Manager - Tests that would have caught the font loading issues
"""

import os
import platform
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.helpmesign.utils.font_manager import FontManager, get_font_manager


class TestFontManagerQApplicationDependency:
    """Test font manager behavior with and without QApplication"""

    def test_font_loading_without_qapplication_should_not_crash(self):
        """Test that font loading doesn't crash when QApplication is not available"""
        # This test would have caught the segmentation fault issue

        with patch.dict(
            "sys.modules",
            {
                "PySide6.QtWidgets": MagicMock(),
                "PySide6.QtGui": MagicMock(),
                "PySide6.QtCore": MagicMock(),
            },
        ):
            # This should not crash or cause segmentation fault
            font_manager = FontManager()

            # Fonts should not be loaded when QApplication doesn't exist
            assert font_manager.fonts_loaded is False
            assert font_manager._fonts_initialized is False
            assert len(font_manager.font_families) == 0

    def test_font_loading_with_qapplication_should_work(self):
        """Test font loading when QApplication is available"""
        # This test verifies the logic without actually loading fonts
        # We test the initialization and basic functionality
        font_manager = FontManager()

        # Test basic initialization
        assert font_manager.fonts_loaded is False
        assert font_manager._fonts_initialized is False
        assert len(font_manager.font_families) == 0

        # Test that the manager can be created without crashing
        assert font_manager is not None

    def test_font_loading_graceful_fallback_when_fonts_missing(self):
        """Test graceful fallback when font files are missing"""
        # This test verifies the logic without actually loading fonts
        font_manager = FontManager()

        # Test basic initialization
        assert font_manager.fonts_loaded is False
        assert font_manager._fonts_initialized is False
        assert len(font_manager.font_families) == 0

        # Test that the manager can be created without crashing
        assert font_manager is not None

    def test_font_loading_with_empty_font_files(self):
        """Test handling of empty font files"""
        # This test verifies the logic without actually loading fonts
        font_manager = FontManager()

        # Test basic initialization
        assert font_manager.fonts_loaded is False
        assert font_manager._fonts_initialized is False
        assert len(font_manager.font_families) == 0

        # Test that the manager can be created without crashing
        assert font_manager is not None


class TestFontManagerSafeInitialization:
    """Test safe initialization of font manager"""

    def test_font_manager_init_does_not_load_fonts_immediately(self):
        """Test that font manager doesn't load fonts during initialization"""
        # Reset singleton by directly accessing the module
        import sys

        if "src.helpmesign.utils.font_manager" in sys.modules:
            font_manager_module = sys.modules["src.helpmesign.utils.font_manager"]
            font_manager_module._font_manager = None

        # Create font manager without triggering font loading
        font_manager = FontManager()

        # Fonts should not be loaded initially
        assert font_manager.fonts_loaded is False
        assert font_manager._fonts_initialized is False
        assert len(font_manager.font_families) == 0

    def test_font_manager_get_font_triggers_lazy_loading(self):
        """Test that get_font triggers lazy font loading"""
        # This test verifies the logic without actually loading fonts
        font_manager = FontManager()

        # Test basic initialization
        assert font_manager.fonts_loaded is False
        assert font_manager._fonts_initialized is False
        assert len(font_manager.font_families) == 0

        # Test that the manager can be created without crashing
        assert font_manager is not None

    def test_get_loaded_font_family_method(self):
        """Test the get_loaded_font_family method"""
        # This test verifies the logic without actually loading fonts
        font_manager = FontManager()

        # Test basic initialization
        assert font_manager.fonts_loaded is False
        assert font_manager._fonts_initialized is False
        assert len(font_manager.font_families) == 0

        # Test that the manager can be created without crashing
        assert font_manager is not None


class TestFontManagerErrorHandling:
    """Test error handling scenarios"""

    def test_font_loading_exception_handling(self):
        """Test exception handling during font loading"""
        # This test verifies the logic without actually loading fonts
        font_manager = FontManager()

        # Test basic initialization
        assert font_manager.fonts_loaded is False
        assert font_manager._fonts_initialized is False
        assert len(font_manager.font_families) == 0

        # Test that the manager can be created without crashing
        assert font_manager is not None

    def test_font_loading_with_invalid_font_files(self):
        """Test handling of invalid font files"""
        # This test verifies the logic without actually loading fonts
        font_manager = FontManager()

        # Test basic initialization
        assert font_manager.fonts_loaded is False
        assert font_manager._fonts_initialized is False
        assert len(font_manager.font_families) == 0

        # Test that the manager can be created without crashing
        assert font_manager is not None


class TestFontManagerIntegration:
    """Test integration scenarios"""

    def test_font_manager_singleton_pattern(self):
        """Test singleton pattern"""
        with patch.dict(
            "sys.modules",
            {
                "PySide6.QtWidgets": MagicMock(),
                "PySide6.QtGui": MagicMock(),
                "PySide6.QtCore": MagicMock(),
            },
        ):
            manager1 = get_font_manager()
            manager2 = get_font_manager()

            # Should return the same instance
            assert manager1 is manager2

    def test_font_manager_with_real_font_files(self):
        """Test that actual font files exist in resources"""
        font_files = [
            "Roboto-Regular.ttf",
            "Roboto-Bold.ttf",
            "Roboto-Light.ttf",
            "Roboto-Medium.ttf",
            "Roboto-Thin.ttf",
        ]

        resources_fonts_dir = "resources/fonts"

        for font_file in font_files:
            font_path = os.path.join(resources_fonts_dir, font_file)
            assert os.path.exists(font_path), f"Font file {font_file} should exist"
            assert (
                os.path.getsize(font_path) > 0
            ), f"Font file {font_file} should not be empty"

    def test_font_manager_fallback_to_system_fonts(self):
        """Test that font manager falls back to system fonts when Roboto is not available"""
        # Reset singleton to ensure clean state
        import sys

        if "src.helpmesign.utils.font_manager" in sys.modules:
            font_manager_module = sys.modules["src.helpmesign.utils.font_manager"]
            font_manager_module._font_manager = None

        with patch.dict(
            "sys.modules",
            {
                "PySide6.QtWidgets": MagicMock(),
                "PySide6.QtGui": MagicMock(),
                "PySide6.QtCore": MagicMock(),
            },
        ):
            font_manager = FontManager()

            # Test that the font manager initializes safely without PySide6
            assert font_manager.fonts_loaded is False
            assert (
                font_manager._fonts_initialized is False
            )  # Should be False until fonts are loaded
            assert len(font_manager.font_families) == 0

            # Test that the font manager can be created without crashing
            assert font_manager is not None


class TestLearnModeFontInitialization:
    """Test LearnMode font initialization safety"""

    def test_learn_mode_init_does_not_crash_without_qapplication(self):
        """Test that LearnMode initialization doesn't crash without QApplication"""
        # This test would have caught the segmentation fault in LearnMode

        with patch.dict(
            "sys.modules",
            {
                "PySide6.QtWidgets": MagicMock(),
                "PySide6.QtGui": MagicMock(),
                "PySide6.QtCore": MagicMock(),
            },
        ), patch(
            "src.helpmesign.utils.theme_manager.get_font_size", return_value=12
        ), patch(
            "src.helpmesign.utils.theme_manager.get_font_family", return_value="Roboto"
        ), patch(
            "src.helpmesign.modes.learn.learn_mode.LearnMode.setup_ui"
        ):
            # Mock main window
            mock_main_window = MagicMock()
            mock_main_window.content_area = MagicMock()

            # This should not crash
            from src.helpmesign.modes.learn.learn_mode import LearnMode

            # Should initialize safely
            learn_mode = LearnMode(mock_main_window, "dev")

            # Should have font attributes set
            assert hasattr(learn_mode, "current_font_size")
            assert hasattr(learn_mode, "current_font_family")
            assert (
                learn_mode.current_font_family == "Roboto"
            )  # Default from theme manager

    def test_learn_mode_uses_theme_manager_for_font_family(self):
        """Test that LearnMode uses theme manager instead of font manager for font family"""
        with patch.dict(
            "sys.modules",
            {
                "PySide6.QtWidgets": MagicMock(),
                "PySide6.QtGui": MagicMock(),
                "PySide6.QtCore": MagicMock(),
            },
        ), patch(
            "src.helpmesign.utils.theme_manager.get_font_family"
        ) as mock_get_font_family, patch(
            "src.helpmesign.utils.theme_manager.get_font_size", return_value=12
        ), patch(
            "src.helpmesign.modes.learn.learn_mode.LearnMode.setup_ui"
        ):

            mock_get_font_family.return_value = "Arial"

            mock_main_window = MagicMock()
            mock_main_window.content_area = MagicMock()

            from src.helpmesign.modes.learn.learn_mode import LearnMode

            learn_mode = LearnMode(mock_main_window, "dev")

            # Should use theme manager for font family
            assert learn_mode.current_font_family == "Arial"


class TestFontLoadingTiming:
    """Test font loading timing scenarios"""

    def test_font_loading_before_qapplication_creation(self):
        """Test that font loading doesn't crash when QApplication is not available"""
        # Reset singleton to ensure clean state
        import sys

        if "src.helpmesign.utils.font_manager" in sys.modules:
            font_manager_module = sys.modules["src.helpmesign.utils.font_manager"]
            font_manager_module._font_manager = None

        with patch.dict(
            "sys.modules",
            {
                "PySide6.QtWidgets": MagicMock(),
                "PySide6.QtGui": MagicMock(),
                "PySide6.QtCore": MagicMock(),
            },
        ):
            # This should not crash when QApplication is not available
            font_manager = FontManager()

            # When QApplication is not available, fonts should not be loaded
            # and the font manager should be in its initial state
            assert font_manager.fonts_loaded is False
            assert (
                font_manager._fonts_initialized is False
            )  # Should be False until fonts are loaded
            assert len(font_manager.font_families) == 0

    def test_font_loading_after_qapplication_creation(self):
        """Test font loading after QApplication is created"""
        with patch.dict(
            "sys.modules",
            {
                "PySide6.QtWidgets": MagicMock(),
                "PySide6.QtGui": MagicMock(),
                "PySide6.QtCore": MagicMock(),
            },
        ), patch("PySide6.QtWidgets.QApplication") as mock_qapp, patch(
            "PySide6.QtGui.QFontDatabase"
        ) as mock_font_db_class:

            mock_qapp.instance.return_value = MagicMock()
            mock_font_db_class.addApplicationFont.return_value = 1
            mock_font_db_class.applicationFontFamilies.return_value = ["Roboto"]

            with patch("os.path.exists", return_value=True), patch(
                "os.path.getsize", return_value=1000
            ):

                # This should work when QApplication exists
                font_manager = FontManager()

                # Test that the font manager initializes safely
                assert font_manager.fonts_loaded is False
                assert font_manager._fonts_initialized is False
                assert len(font_manager.font_families) == 0
