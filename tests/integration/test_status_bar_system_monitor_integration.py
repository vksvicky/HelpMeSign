"""
Integration tests for status bar with system monitoring
"""

import time
import unittest
from unittest.mock import MagicMock, Mock, patch

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from src.helpmesign.ui.components import MainWindow, StatusBar
from src.helpmesign.utils.system_monitor import SystemMonitor, SystemResources


class TestStatusBarSystemMonitorIntegration(unittest.TestCase):
    """Integration tests for status bar with system monitoring"""

    def setUp(self):
        """Set up test fixtures"""
        # Create QApplication if it doesn't exist
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])

        self.status_bar = StatusBar()

    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self.status_bar, "cleanup"):
            self.status_bar.cleanup()

    def test_status_bar_initialization_with_system_monitor(self):
        """Test status bar initializes with system monitor"""
        # Check that system monitor label exists
        self.assertIsNotNone(self.status_bar.system_monitor_label)
        self.assertEqual(
            self.status_bar.system_monitor_label.text(), "System: Initializing..."
        )

    @patch("src.helpmesign.utils.system_monitor.get_system_monitor")
    def test_system_monitor_integration(self, mock_get_monitor):
        """Test system monitor integration with status bar"""
        # Mock system monitor
        mock_monitor = Mock()
        mock_get_monitor.return_value = mock_monitor

        # Create new status bar to trigger system monitor setup
        status_bar = StatusBar()

        # Verify system monitor was started
        mock_monitor.start_monitoring.assert_called_once()

        # Clean up
        status_bar.cleanup()

    def test_system_monitor_update_timer(self):
        """Test system monitor update timer functionality"""
        # Check that update timer exists and is running
        self.assertIsNotNone(self.status_bar.update_timer)
        self.assertTrue(self.status_bar.update_timer.isActive())

    @patch("src.helpmesign.utils.system_monitor.get_system_monitor")
    def test_system_monitor_status_update(self, mock_get_monitor):
        """Test system monitor status updates"""
        # Mock system monitor with specific return values
        mock_monitor = Mock()
        mock_monitor.get_formatted_status.return_value = "🟢 25% | 🟡 60% | 💚 128MB"
        mock_monitor.get_resource_alerts.return_value = []
        mock_get_monitor.return_value = mock_monitor

        # Create new status bar
        status_bar = StatusBar()

        # Trigger update manually
        status_bar._update_system_monitor()

        # Check that status was updated
        self.assertEqual(
            status_bar.system_monitor_label.text(), "🟢 25% | 🟡 60% | 💚 128MB"
        )

        # Clean up
        status_bar.cleanup()

    @patch("src.helpmesign.utils.system_monitor.get_system_monitor")
    def test_system_monitor_alert_styling(self, mock_get_monitor):
        """Test system monitor alert styling"""
        # Mock system monitor with alerts
        mock_monitor = Mock()
        mock_monitor.get_formatted_status.return_value = "🔴 95% | 🔴 90% | ❤️ 1500MB"
        mock_monitor.get_resource_alerts.return_value = ["⚠️ High CPU usage"]
        mock_get_monitor.return_value = mock_monitor

        # Create new status bar
        status_bar = StatusBar()

        # Trigger update manually
        status_bar._update_system_monitor()

        # Check that styling was applied for alerts
        self.assertIn("color: #ff6b6b", status_bar.system_monitor_label.styleSheet())
        self.assertIn("font-weight: bold", status_bar.system_monitor_label.styleSheet())

        # Clean up
        status_bar.cleanup()

    @patch("src.helpmesign.utils.system_monitor.get_system_monitor")
    def test_system_monitor_normal_styling(self, mock_get_monitor):
        """Test system monitor normal styling when no alerts"""
        # Mock system monitor without alerts
        mock_monitor = Mock()
        mock_monitor.get_formatted_status.return_value = "🟢 25% | 🟢 50% | 💚 128MB"
        mock_monitor.get_resource_alerts.return_value = []
        mock_get_monitor.return_value = mock_monitor

        # Create new status bar
        status_bar = StatusBar()

        # Trigger update manually
        status_bar._update_system_monitor()

        # Check that normal styling was applied
        self.assertIn("color: #666", status_bar.system_monitor_label.styleSheet())

        # Clean up
        status_bar.cleanup()

    def test_system_monitor_error_handling(self):
        """Test system monitor error handling"""
        # Mock system monitor to raise exception
        with patch(
            "src.helpmesign.utils.system_monitor.get_system_monitor"
        ) as mock_get_monitor:
            mock_get_monitor.side_effect = Exception("Test error")

            # Create new status bar - should handle error gracefully
            status_bar = StatusBar()

            # Check that error message is displayed
            self.assertEqual(
                status_bar.system_monitor_label.text(), "System: Monitoring unavailable"
            )

            # Clean up
            status_bar.cleanup()

    def test_status_bar_cleanup(self):
        """Test status bar cleanup functionality"""
        # Mock system monitor
        mock_monitor = Mock()

        with patch(
            "src.helpmesign.utils.system_monitor.get_system_monitor",
            return_value=mock_monitor,
        ):
            status_bar = StatusBar()

            # Verify timer is running
            self.assertTrue(status_bar.update_timer.isActive())

            # Clean up
            status_bar.cleanup()

            # Verify timer was stopped and monitor was stopped
            self.assertFalse(status_bar.update_timer.isActive())
            mock_monitor.stop_monitoring.assert_called_once()


class TestMainWindowSystemMonitorIntegration(unittest.TestCase):
    """Integration tests for main window with system monitoring"""

    def setUp(self):
        """Set up test fixtures"""
        # Create QApplication if it doesn't exist
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])

        self.main_window = MainWindow()

    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self.main_window, "closeEvent"):
            # Simulate close event
            from PySide6.QtGui import QCloseEvent

            close_event = QCloseEvent()
            self.main_window.closeEvent(close_event)

    def test_main_window_has_system_monitor(self):
        """Test main window includes system monitoring in status bar"""
        # Check that status bar exists and has system monitor
        self.assertIsNotNone(self.main_window.status_bar)
        self.assertIsNotNone(self.main_window.status_bar.system_monitor_label)

    def test_main_window_close_cleanup(self):
        """Test main window cleanup on close"""
        # Mock status bar cleanup
        with patch.object(self.main_window.status_bar, "cleanup") as mock_cleanup:
            # Simulate close event
            from PySide6.QtGui import QCloseEvent

            close_event = QCloseEvent()
            self.main_window.closeEvent(close_event)

            # Verify cleanup was called
            mock_cleanup.assert_called_once()

    def test_main_window_status_bar_layout(self):
        """Test main window status bar layout includes system monitor"""
        # Check that status bar has both status label and system monitor label
        self.assertIsNotNone(self.main_window.status_bar.status_label)
        self.assertIsNotNone(self.main_window.status_bar.system_monitor_label)

        # Check that system monitor is positioned on the right
        layout = self.main_window.status_bar.layout()
        self.assertIsNotNone(layout)

        # The system monitor label should be the last widget in the layout
        widget_count = layout.count()
        last_widget = layout.itemAt(widget_count - 1).widget()
        self.assertEqual(last_widget, self.main_window.status_bar.system_monitor_label)


class TestSystemMonitorRealTimeIntegration(unittest.TestCase):
    """Real-time integration tests for system monitoring"""

    def setUp(self):
        """Set up test fixtures"""
        # Create QApplication if it doesn't exist
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])

    def test_real_time_system_monitor_updates(self):
        """Test real-time system monitor updates"""
        # Create system monitor
        monitor = SystemMonitor(update_interval=0.1)

        try:
            # Start monitoring
            monitor.start_monitoring()

            # Wait for first update
            time.sleep(0.2)

            # Get resources
            resources = monitor.get_resources()

            # Verify we got some resources
            self.assertIsNotNone(resources)
            self.assertIsInstance(resources, SystemResources)

            # Verify basic resource values are reasonable
            self.assertGreaterEqual(resources.cpu_percent, 0)
            self.assertLessEqual(resources.cpu_percent, 100)
            self.assertGreaterEqual(resources.memory_percent, 0)
            self.assertLessEqual(resources.memory_percent, 100)
            self.assertGreaterEqual(resources.app_memory_mb, 0)

        finally:
            # Clean up
            monitor.stop_monitoring()

    def test_system_monitor_formatted_output(self):
        """Test system monitor formatted output"""
        # Create system monitor
        monitor = SystemMonitor(update_interval=0.1)

        try:
            # Start monitoring
            monitor.start_monitoring()

            # Wait for first update
            time.sleep(0.2)

            # Get formatted status
            compact_status = monitor.get_formatted_status(compact=True)
            detailed_status = monitor.get_formatted_status(compact=False)

            # Verify status strings are not empty
            self.assertIsNotNone(compact_status)
            self.assertIsNotNone(detailed_status)
            self.assertGreater(len(compact_status), 0)
            self.assertGreater(len(detailed_status), 0)

            # Verify compact status contains expected elements
            self.assertIn("%", compact_status)

            # Verify detailed status contains expected elements
            self.assertIn("CPU:", detailed_status)
            self.assertIn("RAM:", detailed_status)

        finally:
            # Clean up
            monitor.stop_monitoring()

    def test_system_monitor_performance_scoring(self):
        """Test system monitor performance scoring"""
        # Create system monitor
        monitor = SystemMonitor(update_interval=0.1)

        try:
            # Start monitoring
            monitor.start_monitoring()

            # Wait for first update
            time.sleep(0.2)

            # Get performance score
            score, level = monitor.get_performance_score()

            # Verify score is reasonable
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)

            # Verify level is valid
            valid_levels = ["Excellent", "Good", "Fair", "Poor", "Unknown"]
            self.assertIn(level, valid_levels)

        finally:
            # Clean up
            monitor.stop_monitoring()


if __name__ == "__main__":
    unittest.main()
