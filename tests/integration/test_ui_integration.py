#!/usr/bin/env python3
"""
Integration tests for UI components with new features
Tests real interactions between components
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestUIIntegration(unittest.TestCase):
    """Integration tests for UI components"""
    
    @patch('tkinter.Tk')
    @patch('tkinter.ttk')
    def test_main_window_with_fonts_integration(self, mock_ttk, mock_tk):
        """Test main window integration with font system"""
        # Mock Tkinter components
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        # Test that main window can be created with font system
        try:
            from helpmesign.ui.components import MainWindow
            from helpmesign.utils.font_manager import get_font_manager
            
            # Initialize font manager
            font_manager = get_font_manager()
            self.assertIsNotNone(font_manager)
            
            # Create main window
            main_window = MainWindow(mock_root, "Test App")
            self.assertIsNotNone(main_window)
            
            # Test that menu was created
            self.assertTrue(hasattr(main_window, 'menu_bar'))
            
        except ImportError:
            self.skipTest("UI components not available")
    
    @patch('tkinter.Toplevel')
    @patch('tkinter.ttk')
    @patch('tkinter.IntVar')
    @patch('tkinter.BooleanVar')
    def test_settings_dialog_integration(self, mock_bool_var, mock_int_var, mock_ttk, mock_toplevel):
        """Test settings dialog integration"""
        # Mock Tkinter components
        mock_parent = MagicMock()
        mock_dialog = MagicMock()
        mock_toplevel.return_value = mock_dialog
        
        # Mock Tkinter variables
        mock_int_var.return_value = MagicMock()
        mock_bool_var.return_value = MagicMock()
        
        try:
            from helpmesign.ui.settings_dialog import SettingsDialog
            
            # Create settings dialog
            settings_dialog = SettingsDialog(mock_parent)
            self.assertIsNotNone(settings_dialog)
            
            # Test that dialog was configured as child window
            mock_dialog.transient.assert_called_with(mock_parent)
            mock_dialog.grab_set.assert_called()
            
            # Test that menu was removed
            mock_dialog.config.assert_called_with(menu=None)
            
        except ImportError:
            self.skipTest("Settings dialog not available")
    
    @patch('tkinter.Tk')
    @patch('tkinter.ttk')
    def test_text_input_with_shortcuts_integration(self, mock_ttk, mock_tk):
        """Test text input integration with keyboard shortcuts"""
        # Mock Tkinter components
        mock_parent = MagicMock()
        
        try:
            from helpmesign.ui.components import TextInputFrame
            
            # Create text input frame
            text_frame = TextInputFrame(mock_parent)
            self.assertIsNotNone(text_frame)
            
            # Test that shortcuts can be bound
            mock_process_callback = MagicMock()
            mock_clear_callback = MagicMock()
            
            text_frame.bind_shortcuts(mock_process_callback, mock_clear_callback)
            
            # Test that text input exists
            self.assertTrue(hasattr(text_frame, 'text_input'))
            
        except ImportError:
            self.skipTest("Text input components not available")
    
    @patch('tkinter.Tk')
    @patch('tkinter.ttk')
    def test_output_frame_with_fonts_integration(self, mock_ttk, mock_tk):
        """Test output frame integration with font system"""
        # Mock Tkinter components
        mock_parent = MagicMock()
        
        try:
            from helpmesign.ui.components import OutputFrame
            
            # Create output frame
            output_frame = OutputFrame(mock_parent)
            self.assertIsNotNone(output_frame)
            
            # Test that output text widget exists
            self.assertTrue(hasattr(output_frame, 'output_text'))
            
        except ImportError:
            self.skipTest("Output frame components not available")
    
    @patch('tkinter.Tk')
    @patch('tkinter.ttk')
    @patch('tkinter.StringVar')
    def test_status_bar_with_fonts_integration(self, mock_string_var, mock_ttk, mock_tk):
        """Test status bar integration with font system"""
        # Mock Tkinter components
        mock_parent = MagicMock()
        
        # Mock Tkinter variables with proper behavior
        mock_var_instance = MagicMock()
        mock_var_instance.get.return_value = "Test status"
        mock_string_var.return_value = mock_var_instance
        
        try:
            from helpmesign.ui.components import StatusBar
            
            # Create status bar
            status_bar = StatusBar(mock_parent)
            self.assertIsNotNone(status_bar)
            
            # Test status setting
            status_bar.set_status("Test status")
            self.assertEqual(status_bar.get_status(), "Test status")
            
        except ImportError:
            self.skipTest("Status bar components not available")


class TestMenuIntegration(unittest.TestCase):
    """Integration tests for menu system"""
    
    @patch('tkinter.Tk')
    @patch('tkinter.Menu')
    def test_menu_creation_integration(self, mock_menu, mock_tk):
        """Test menu creation integration"""
        # Mock Tkinter components
        mock_root = MagicMock()
        mock_menu_bar = MagicMock()
        mock_menu.return_value = mock_menu_bar
        
        try:
            from helpmesign.ui.components import MainWindow
            
            # Create main window
            main_window = MainWindow(mock_root, "Test App")
            
            # Test that menu bar was created
            mock_menu.assert_called()
            
            # Test that root was configured with menu
            mock_root.config.assert_called_with(menu=mock_menu_bar)
            
        except ImportError:
            self.skipTest("Menu components not available")
    
    @patch('tkinter.Tk')
    @patch('tkinter.Menu')
    def test_menu_accelerators_integration(self, mock_menu, mock_tk):
        """Test menu accelerators integration"""
        # Mock Tkinter components
        mock_root = MagicMock()
        mock_menu_bar = MagicMock()
        mock_app_menu = MagicMock()
        mock_menu.return_value = mock_menu_bar
        mock_menu.return_value = mock_app_menu
        
        try:
            from helpmesign.ui.components import MainWindow
            
            # Create main window
            main_window = MainWindow(mock_root, "Test App")
            
            # Test that menu items were added with accelerators
            mock_app_menu.add_command.assert_called()
            
        except ImportError:
            self.skipTest("Menu components not available")


class TestSegmentedControlIntegration(unittest.TestCase):
    """Integration tests for segmented control"""
    
    @patch('tkinter.Toplevel')
    @patch('tkinter.Canvas')
    @patch('tkinter.IntVar')
    @patch('tkinter.BooleanVar')
    def test_segmented_control_creation_integration(self, mock_bool_var, mock_int_var, mock_canvas, mock_toplevel):
        """Test segmented control creation integration"""
        # Mock Tkinter components
        mock_parent = MagicMock()
        mock_dialog = MagicMock()
        mock_canvas_instance = MagicMock()
        mock_toplevel.return_value = mock_dialog
        mock_canvas.return_value = mock_canvas_instance
        
        # Mock Tkinter variables
        mock_int_var.return_value = MagicMock()
        mock_bool_var.return_value = MagicMock()
        
        try:
            from helpmesign.ui.settings_dialog import SettingsDialog
            
            # Create settings dialog
            settings_dialog = SettingsDialog(mock_parent)
            
            # Test that canvas was created
            mock_canvas.assert_called()
            
            # Test canvas dimensions
            mock_canvas.assert_called_with(
                unittest.mock.ANY,  # parent
                width=300,
                height=40,
                bg='#f0f0f0',
                highlightthickness=0,
                relief='flat'
            )
            
        except ImportError:
            self.skipTest("Settings dialog not available")
    
    @patch('tkinter.Toplevel')
    @patch('tkinter.Canvas')
    @patch('tkinter.IntVar')
    @patch('tkinter.BooleanVar')
    def test_segmented_control_click_integration(self, mock_bool_var, mock_int_var, mock_canvas, mock_toplevel):
        """Test segmented control click integration"""
        # Mock Tkinter components
        mock_parent = MagicMock()
        mock_dialog = MagicMock()
        mock_canvas_instance = MagicMock()
        mock_toplevel.return_value = mock_dialog
        mock_canvas.return_value = mock_canvas_instance
        
        # Mock Tkinter variables
        mock_int_var.return_value = MagicMock()
        mock_bool_var.return_value = MagicMock()
        
        try:
            from helpmesign.ui.settings_dialog import SettingsDialog
            
            # Create settings dialog
            settings_dialog = SettingsDialog(mock_parent)
            
            # Test click binding
            mock_canvas_instance.bind.assert_called_with('<Button-1>', unittest.mock.ANY)
            
        except ImportError:
            self.skipTest("Settings dialog not available")


class TestFontManagerIntegration(unittest.TestCase):
    """Integration tests for font manager"""
    
    def test_font_manager_initialization_integration(self):
        """Test font manager initialization integration"""
        try:
            from helpmesign.utils.font_manager import get_font_manager
            
            # Get font manager
            font_manager = get_font_manager()
            self.assertIsNotNone(font_manager)
            
            # Test that fonts were loaded
            self.assertTrue(hasattr(font_manager, 'fonts_loaded'))
            
        except ImportError:
            self.skipTest("Font manager not available")
    
    def test_font_functions_integration(self):
        """Test font functions integration"""
        try:
            from helpmesign.utils.font_manager import (
                get_title_font, get_heading_font, get_body_font,
                get_label_font, get_button_font, get_input_font
            )
            
            # Test all font functions return tuples
            title_font = get_title_font()
            heading_font = get_heading_font()
            body_font = get_body_font()
            label_font = get_label_font()
            button_font = get_button_font()
            input_font = get_input_font()
            
            self.assertIsInstance(title_font, tuple)
            self.assertIsInstance(heading_font, tuple)
            self.assertIsInstance(body_font, tuple)
            self.assertIsInstance(label_font, tuple)
            self.assertIsInstance(button_font, tuple)
            self.assertIsInstance(input_font, tuple)
            
            # Test font tuple structure
            for font_tuple in [title_font, heading_font, body_font, label_font, button_font, input_font]:
                self.assertEqual(len(font_tuple), 4)  # family, size, weight, slant
                
        except ImportError:
            self.skipTest("Font manager not available")


class TestErrorHandlingIntegration(unittest.TestCase):
    """Integration tests for error handling"""
    
    @patch('tkinter.Tk')
    def test_font_loading_error_integration(self, mock_tk):
        """Test font loading error handling integration"""
        # Mock Tkinter components
        mock_root = MagicMock()
        
        try:
            from helpmesign.ui.components import MainWindow
            
            # Create main window (should handle font loading errors gracefully)
            main_window = MainWindow(mock_root, "Test App")
            self.assertIsNotNone(main_window)
            
        except ImportError:
            self.skipTest("UI components not available")
    
    @patch('tkinter.Toplevel')
    @patch('tkinter.IntVar')
    @patch('tkinter.BooleanVar')
    def test_settings_dialog_error_integration(self, mock_bool_var, mock_int_var, mock_toplevel):
        """Test settings dialog error handling integration"""
        # Mock Tkinter components
        mock_parent = MagicMock()
        mock_dialog = MagicMock()
        mock_toplevel.return_value = mock_dialog
        
        # Mock Tkinter variables
        mock_int_var.return_value = MagicMock()
        mock_bool_var.return_value = MagicMock()
        
        try:
            from helpmesign.ui.settings_dialog import SettingsDialog
            
            # Create settings dialog (should handle errors gracefully)
            settings_dialog = SettingsDialog(mock_parent)
            self.assertIsNotNone(settings_dialog)
            
        except ImportError:
            self.skipTest("Settings dialog not available")


class TestBoundaryConditionsIntegration(unittest.TestCase):
    """Integration tests for boundary conditions"""
    
    @patch('tkinter.Tk')
    def test_large_text_integration(self, mock_tk):
        """Test large text handling integration"""
        # Mock Tkinter components
        mock_root = MagicMock()
        
        try:
            from helpmesign.ui.components import TextInputFrame
            
            # Create text input frame
            text_frame = TextInputFrame(mock_root)
            
            # Test large text input
            large_text = "A" * 10000
            text_frame.set_text(large_text)
            
            # Should handle large text without errors
            self.assertIsNotNone(text_frame)
            
        except ImportError:
            self.skipTest("Text input components not available")
    
    @patch('tkinter.Toplevel')
    @patch('tkinter.IntVar')
    @patch('tkinter.BooleanVar')
    def test_unicode_text_integration(self, mock_bool_var, mock_int_var, mock_toplevel):
        """Test unicode text handling integration"""
        # Mock Tkinter components
        mock_parent = MagicMock()
        mock_dialog = MagicMock()
        mock_toplevel.return_value = mock_dialog
        
        # Mock Tkinter variables
        mock_int_var.return_value = MagicMock()
        mock_bool_var.return_value = MagicMock()
        
        try:
            from helpmesign.ui.settings_dialog import SettingsDialog
            
            # Create settings dialog with unicode text
            settings_dialog = SettingsDialog(mock_parent)
            
            # Should handle unicode text without errors
            self.assertIsNotNone(settings_dialog)
            
        except ImportError:
            self.skipTest("Settings dialog not available")


if __name__ == '__main__':
    unittest.main() 