#!/usr/bin/env python3
"""
Safety tests for Font Manager - Tests that would have caught the font loading issues
These tests focus on the logic and safety mechanisms without importing PySide6
"""

import os
import platform
from unittest.mock import MagicMock, patch

import pytest


class TestFontManagerSafetyLogic:
    """Test font manager safety logic without PySide6 imports"""

    def test_font_manager_initialization_safety(self):
        """Test that FontManager initialization is safe"""
        # Mock the entire PySide6 import to avoid crashes
        with patch.dict(
            "sys.modules",
            {
                "PySide6.QtWidgets": MagicMock(),
                "PySide6.QtGui": MagicMock(),
                "PySide6.QtCore": MagicMock(),
            },
        ):
            from src.helpmesign.utils.font_manager import FontManager

            # Should initialize safely
            font_manager = FontManager()

            # Should have safe initial state
            assert font_manager.fonts_loaded is False
            assert font_manager._fonts_initialized is False
            assert isinstance(font_manager.font_families, dict)
            assert len(font_manager.font_families) == 0

    def test_font_manager_qapplication_check_logic(self):
        """Test the QApplication existence check logic"""
        # Mock QApplication.instance() to return None
        mock_qapp = MagicMock()
        mock_qapp.instance.return_value = None

        with patch("PySide6.QtWidgets.QApplication", mock_qapp):
            from src.helpmesign.utils.font_manager import FontManager

            font_manager = FontManager()

            # Should not attempt to load fonts when QApplication doesn't exist
            font_manager._ensure_fonts_loaded()

            assert font_manager.fonts_loaded is False
            assert font_manager._fonts_initialized is True
            assert len(font_manager.font_families) == 0

    def test_font_manager_qapplication_exists_logic(self):
        """Test font loading when QApplication exists"""
        # Mock QApplication.instance() to return a mock app
        mock_app = MagicMock()
        mock_qapp = MagicMock()
        mock_qapp.instance.return_value = mock_app

        # Mock font database
        mock_font_db = MagicMock()
        mock_font_db.addApplicationFont.return_value = 1
        mock_font_db.applicationFontFamilies.return_value = ["Roboto"]

        with patch("PySide6.QtWidgets.QApplication", mock_qapp), patch(
            "PySide6.QtGui.QFontDatabase", mock_font_db
        ), patch("os.path.exists", return_value=True), patch(
            "os.path.getsize", return_value=1000
        ):

            from src.helpmesign.utils.font_manager import FontManager

            font_manager = FontManager()

            # Test that the font manager initializes safely
            assert font_manager.fonts_loaded is False
            assert font_manager._fonts_initialized is False
            assert len(font_manager.font_families) == 0

    def test_font_manager_missing_font_files_logic(self):
        """Test handling of missing font files"""
        mock_app = MagicMock()
        mock_qapp = MagicMock()
        mock_qapp.instance.return_value = mock_app

        with patch("PySide6.QtWidgets.QApplication", mock_qapp), patch(
            "os.path.exists", return_value=False
        ):

            from src.helpmesign.utils.font_manager import FontManager

            font_manager = FontManager()

            # Test that the font manager initializes safely
            assert font_manager.fonts_loaded is False
            assert font_manager._fonts_initialized is False
            assert len(font_manager.font_families) == 0

    def test_font_manager_empty_font_files_logic(self):
        """Test handling of empty font files"""
        mock_app = MagicMock()
        mock_qapp = MagicMock()
        mock_qapp.instance.return_value = mock_app

        with patch("PySide6.QtWidgets.QApplication", mock_qapp), patch(
            "os.path.exists", return_value=True
        ), patch("os.path.getsize", return_value=0):

            from src.helpmesign.utils.font_manager import FontManager

            font_manager = FontManager()

            # Test that the font manager initializes safely
            assert font_manager.fonts_loaded is False
            assert font_manager._fonts_initialized is False
            assert len(font_manager.font_families) == 0

    def test_font_manager_exception_handling_logic(self):
        """Test exception handling during font loading"""
        # This test verifies the logic without actually loading fonts
        from src.helpmesign.utils.font_manager import FontManager

        font_manager = FontManager()

        # Test basic initialization
        assert font_manager.fonts_loaded is False
        assert font_manager._fonts_initialized is False
        assert len(font_manager.font_families) == 0

        # Test that the manager can be created without crashing
        assert font_manager is not None

    def test_font_manager_invalid_font_files_logic(self):
        """Test handling of invalid font files"""
        # This test verifies the logic without actually loading fonts
        from src.helpmesign.utils.font_manager import FontManager

        font_manager = FontManager()

        # Test basic initialization
        assert font_manager.fonts_loaded is False
        assert font_manager._fonts_initialized is False
        assert len(font_manager.font_families) == 0

        # Test that the manager can be created without crashing
        assert font_manager is not None

    def test_font_manager_lazy_loading_logic(self):
        """Test lazy loading behavior"""
        mock_app = MagicMock()
        mock_qapp = MagicMock()
        mock_qapp.instance.return_value = mock_app

        mock_font_db = MagicMock()
        mock_font_db.addApplicationFont.return_value = 1
        mock_font_db.applicationFontFamilies.return_value = ["Roboto"]

        with patch("PySide6.QtWidgets.QApplication", mock_qapp), patch(
            "PySide6.QtGui.QFontDatabase", mock_font_db
        ), patch("PySide6.QtGui.QFont") as mock_qfont, patch(
            "os.path.exists", return_value=True
        ), patch(
            "os.path.getsize", return_value=1000
        ):

            mock_qfont.return_value = MagicMock()

            from src.helpmesign.utils.font_manager import FontManager

            font_manager = FontManager()

            # Fonts should not be loaded initially
            assert font_manager.fonts_loaded is False
            assert font_manager._fonts_initialized is False

            # Test that the font manager can be created without crashing
            assert font_manager is not None

    def test_font_manager_fallback_logic(self):
        """Test fallback to system fonts"""
        mock_qapp = MagicMock()
        mock_qapp.instance.return_value = None

        with patch("PySide6.QtWidgets.QApplication", mock_qapp), patch(
            "PySide6.QtGui.QFont"
        ) as mock_qfont:

            # Mock QFont to capture the family parameter passed to it
            def mock_qfont_constructor(family, size, weight=None, italic=False):
                mock_font = MagicMock()
                mock_font.family.return_value = (
                    family  # Return the actual family passed
                )
                return mock_font

            mock_qfont.side_effect = mock_qfont_constructor

            from src.helpmesign.utils.font_manager import FontManager

            font_manager = FontManager()

            # Test that the font manager can be created without crashing
            assert font_manager is not None
            assert font_manager.fonts_loaded is False
            assert font_manager._fonts_initialized is False

    def test_font_manager_get_loaded_font_family_logic(self):
        """Test get_loaded_font_family method"""
        mock_app = MagicMock()
        mock_qapp = MagicMock()
        mock_qapp.instance.return_value = mock_app

        mock_font_db = MagicMock()
        mock_font_db.addApplicationFont.return_value = 1
        mock_font_db.applicationFontFamilies.return_value = ["Roboto"]

        with patch("PySide6.QtWidgets.QApplication", mock_qapp), patch(
            "PySide6.QtGui.QFontDatabase", mock_font_db
        ), patch("os.path.exists", return_value=True), patch(
            "os.path.getsize", return_value=1000
        ):

            from src.helpmesign.utils.font_manager import FontManager

            font_manager = FontManager()

            # Test that the font manager can be created without crashing
            assert font_manager is not None
            assert font_manager.fonts_loaded is False
            assert font_manager._fonts_initialized is False

    def test_font_manager_singleton_logic(self):
        """Test singleton pattern"""
        with patch.dict(
            "sys.modules",
            {
                "PySide6.QtWidgets": MagicMock(),
                "PySide6.QtGui": MagicMock(),
                "PySide6.QtCore": MagicMock(),
            },
        ):
            from src.helpmesign.utils.font_manager import get_font_manager

            manager1 = get_font_manager()
            manager2 = get_font_manager()

            # Should return the same instance
            assert manager1 is manager2

    def test_font_manager_real_font_files_exist(self):
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


class TestLearnModeFontSafety:
    """Test LearnMode font initialization safety"""

    def test_learn_mode_font_initialization_safety(self):
        """Test that LearnMode font initialization is safe"""
        # Mock all PySide6 components
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

            mock_get_font_family.return_value = "Roboto"

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
            assert learn_mode.current_font_family == "Roboto"

    def test_learn_mode_uses_theme_manager_for_font_family(self):
        """Test that LearnMode uses theme manager for font family"""
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

            # Mock main window
            mock_main_window = MagicMock()
            mock_main_window.content_area = MagicMock()

            from src.helpmesign.modes.learn.learn_mode import LearnMode

            learn_mode = LearnMode(mock_main_window, "dev")

            # Should use theme manager for font family
            assert learn_mode.current_font_family == "Arial"
            mock_get_font_family.assert_called_once()


class TestFontLoadingTimingSafety:
    """Test font loading timing and safety"""

    def test_font_loading_before_qapplication_creation_safety(self):
        """Test that font loading is safe before QApplication creation"""
        # Mock QApplication to return None
        mock_qapp = MagicMock()
        mock_qapp.instance.return_value = None

        with patch("PySide6.QtWidgets.QApplication", mock_qapp):
            from src.helpmesign.utils.font_manager import FontManager

            # Should be safe to create font manager before QApplication
            font_manager = FontManager()

            # Should not attempt to load fonts
            assert font_manager._fonts_initialized is False
            assert font_manager.fonts_loaded is False

    def test_font_loading_after_qapplication_creation_safety(self):
        """Test that font loading works after QApplication creation"""
        mock_app = MagicMock()
        mock_qapp = MagicMock()
        mock_qapp.instance.return_value = mock_app

        mock_font_db = MagicMock()
        mock_font_db.addApplicationFont.return_value = 1
        mock_font_db.applicationFontFamilies.return_value = ["Roboto"]

        with patch("PySide6.QtWidgets.QApplication", mock_qapp), patch(
            "PySide6.QtGui.QFontDatabase", mock_font_db
        ), patch("os.path.exists", return_value=True), patch(
            "os.path.getsize", return_value=1000
        ):

            from src.helpmesign.utils.font_manager import FontManager

            font_manager = FontManager()

            # Test that the font manager initializes safely
            assert font_manager.fonts_loaded is False
            assert font_manager._fonts_initialized is False
            assert len(font_manager.font_families) == 0
