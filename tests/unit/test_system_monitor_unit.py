"""
Unit tests for system monitor functionality
"""

import time
import unittest
from typing import Optional
from unittest.mock import MagicMock, Mock, patch

import psutil

from src.helpmesign.utils.system_monitor import (
    SystemMonitor,
    SystemResources,
    get_system_monitor,
    start_system_monitoring,
    stop_system_monitoring,
)


class TestSystemResources(unittest.TestCase):
    """Test SystemResources data class"""

    def test_system_resources_creation(self):
        """Test creating SystemResources instance"""
        resources = SystemResources(
            cpu_percent=25.5,
            memory_percent=60.0,
            memory_used_mb=8192.0,
            memory_total_mb=16384.0,
            disk_usage_percent=45.0,
            disk_used_gb=500.0,
            disk_total_gb=1000.0,
            network_sent_mb=1024.0,
            network_recv_mb=2048.0,
            process_count=150,
            uptime_hours=24.5,
            app_memory_mb=256.0,
            app_cpu_percent=5.0,
            app_threads=8,
            app_connections=2,
        )

        self.assertEqual(resources.cpu_percent, 25.5)
        self.assertEqual(resources.memory_percent, 60.0)
        self.assertEqual(resources.app_memory_mb, 256.0)
        self.assertEqual(resources.app_threads, 8)


class TestSystemMonitor(unittest.TestCase):
    """Test SystemMonitor class"""

    def setUp(self):
        """Set up test fixtures"""
        self.monitor = SystemMonitor(update_interval=0.1)

    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self.monitor, "_monitor_thread") and self.monitor._monitor_thread:
            self.monitor.stop_monitoring()

    def test_initialization(self):
        """Test SystemMonitor initialization"""
        self.assertIsNotNone(self.monitor)
        self.assertEqual(self.monitor.update_interval, 0.1)
        self.assertIsNone(self.monitor._current_resources)
        self.assertFalse(self.monitor._stop_event.is_set())

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    @patch("psutil.net_io_counters")
    @patch("psutil.boot_time")
    @patch("psutil.pids")
    def test_update_resources_success(
        self, mock_pids, mock_boot_time, mock_net_io, mock_disk, mock_memory, mock_cpu
    ):
        """Test successful resource update"""
        # Mock system calls
        mock_cpu.return_value = 25.5
        mock_memory.return_value = Mock(
            percent=60.0,
            used=8589934592,  # 8GB in bytes
            total=17179869184,  # 16GB in bytes
        )
        mock_disk.return_value = Mock(
            percent=45.0,
            used=536870912000,  # 500GB in bytes
            total=1073741824000,  # 1TB in bytes
        )
        mock_net_io.return_value = Mock(
            bytes_sent=1073741824, bytes_recv=2147483648  # 1GB in bytes  # 2GB in bytes
        )
        mock_boot_time.return_value = time.time() - 86400  # 24 hours ago
        mock_pids.return_value = list(range(150))

        # Mock app process
        mock_process = Mock()
        mock_process.memory_info.return_value = Mock(rss=268435456)  # 256MB
        mock_process.cpu_percent.return_value = 5.0
        mock_process.num_threads.return_value = 8
        mock_process.connections.return_value = [Mock(), Mock()]

        with patch("psutil.Process", return_value=mock_process):
            self.monitor._app_process = mock_process
            self.monitor._update_resources()

        # Verify resources were updated
        self.assertIsNotNone(self.monitor._current_resources)
        resources = self.monitor._current_resources

        self.assertEqual(resources.cpu_percent, 25.5)
        self.assertEqual(resources.memory_percent, 60.0)
        self.assertEqual(resources.memory_used_mb, 8192.0)
        self.assertEqual(resources.memory_total_mb, 16384.0)
        self.assertEqual(resources.disk_usage_percent, 45.0)
        self.assertEqual(resources.app_memory_mb, 256.0)
        self.assertEqual(resources.app_threads, 8)
        self.assertEqual(resources.app_connections, 2)

    @patch("psutil.cpu_percent")
    def test_update_resources_exception_handling(self, mock_cpu):
        """Test exception handling during resource update"""
        mock_cpu.side_effect = Exception("Test exception")

        # Should not raise exception
        self.monitor._update_resources()

        # Resources should still be None after exception
        self.assertIsNone(self.monitor._current_resources)

    def test_get_resources_initial_call(self):
        """Test getting resources on initial call"""
        with patch.object(self.monitor, "_update_resources") as mock_update:
            resources = self.monitor.get_resources()

            mock_update.assert_called_once()
            self.assertIsNone(resources)  # Should be None initially

    def test_get_resources_cached(self):
        """Test getting cached resources"""
        # Create mock resources
        mock_resources = SystemResources(
            cpu_percent=25.0,
            memory_percent=60.0,
            memory_used_mb=8192.0,
            memory_total_mb=16384.0,
            disk_usage_percent=45.0,
            disk_used_gb=500.0,
            disk_total_gb=1000.0,
            network_sent_mb=1024.0,
            network_recv_mb=2048.0,
            process_count=150,
            uptime_hours=24.0,
            app_memory_mb=256.0,
            app_cpu_percent=5.0,
            app_threads=8,
            app_connections=2,
        )

        self.monitor._current_resources = mock_resources

        with patch.object(self.monitor, "_update_resources") as mock_update:
            resources = self.monitor.get_resources()

            # Should not call update_resources since we have cached data
            mock_update.assert_not_called()
            self.assertEqual(resources, mock_resources)

    def test_get_formatted_status_compact(self):
        """Test compact status formatting"""
        # Create mock resources
        mock_resources = SystemResources(
            cpu_percent=25.0,
            memory_percent=60.0,
            memory_used_mb=8192.0,
            memory_total_mb=16384.0,
            disk_usage_percent=45.0,
            disk_used_gb=500.0,
            disk_total_gb=1000.0,
            network_sent_mb=1024.0,
            network_recv_mb=2048.0,
            process_count=150,
            uptime_hours=24.0,
            app_memory_mb=256.0,
            app_cpu_percent=5.0,
            app_threads=8,
            app_connections=2,
        )

        self.monitor._current_resources = mock_resources

        status = self.monitor.get_formatted_status(compact=True)

        # Should contain CPU, memory, and app memory info
        self.assertIn("🟢 25%", status)
        self.assertIn("🟡 60%", status)
        self.assertIn("💛 256MB", status)

    def test_get_formatted_status_detailed(self):
        """Test detailed status formatting"""
        # Create mock resources
        mock_resources = SystemResources(
            cpu_percent=25.0,
            memory_percent=60.0,
            memory_used_mb=8192.0,
            memory_total_mb=16384.0,
            disk_usage_percent=45.0,
            disk_used_gb=500.0,
            disk_total_gb=1000.0,
            network_sent_mb=1024.0,
            network_recv_mb=2048.0,
            process_count=150,
            uptime_hours=24.0,
            app_memory_mb=256.0,
            app_cpu_percent=5.0,
            app_threads=8,
            app_connections=2,
        )

        self.monitor._current_resources = mock_resources

        status = self.monitor.get_formatted_status(compact=False)

        # Should contain detailed information
        self.assertIn("CPU: 25.0%", status)
        self.assertIn("RAM: 60.0%", status)
        self.assertIn("8192MB", status)
        self.assertIn("Disk: 45.0%", status)
        self.assertIn("App: 256MB", status)
        self.assertIn("Uptime: 24.0h", status)

    def test_get_formatted_status_no_resources(self):
        """Test status formatting when no resources available"""
        # Mock the get_resources method to return None
        with patch.object(self.monitor, "get_resources", return_value=None):
            status = self.monitor.get_formatted_status()

            self.assertEqual(status, "System: Unavailable")

    def test_cpu_icon_selection(self):
        """Test CPU icon selection based on usage"""
        # Low CPU usage
        icon = self.monitor._get_cpu_icon(15.0)
        self.assertEqual(icon, "🟢")

        # Medium CPU usage
        icon = self.monitor._get_cpu_icon(50.0)
        self.assertEqual(icon, "🟡")

        # High CPU usage
        icon = self.monitor._get_cpu_icon(85.0)
        self.assertEqual(icon, "🔴")

    def test_memory_icon_selection(self):
        """Test memory icon selection based on usage"""
        # Low memory usage
        icon = self.monitor._get_memory_icon(30.0)
        self.assertEqual(icon, "🟢")

        # Medium memory usage
        icon = self.monitor._get_memory_icon(65.0)
        self.assertEqual(icon, "🟡")

        # High memory usage
        icon = self.monitor._get_memory_icon(90.0)
        self.assertEqual(icon, "🔴")

    def test_app_icon_selection(self):
        """Test app memory icon selection based on size"""
        # Low app memory
        icon = self.monitor._get_app_icon(50.0)
        self.assertEqual(icon, "💚")

        # Medium app memory
        icon = self.monitor._get_app_icon(300.0)
        self.assertEqual(icon, "💛")

        # High app memory
        icon = self.monitor._get_app_icon(800.0)
        self.assertEqual(icon, "❤️")

    def test_resource_alerts(self):
        """Test resource alert generation"""
        # Create resources with high usage
        mock_resources = SystemResources(
            cpu_percent=95.0,  # High CPU
            memory_percent=85.0,  # Elevated memory
            memory_used_mb=8192.0,
            memory_total_mb=16384.0,
            disk_usage_percent=95.0,  # Low disk space
            disk_used_gb=950.0,
            disk_total_gb=1000.0,
            network_sent_mb=1024.0,
            network_recv_mb=2048.0,
            process_count=150,
            uptime_hours=24.0,
            app_memory_mb=1200.0,  # High app memory
            app_cpu_percent=5.0,
            app_threads=8,
            app_connections=2,
        )

        self.monitor._current_resources = mock_resources

        alerts = self.monitor.get_resource_alerts()

        # Should have multiple alerts
        self.assertIn("⚠️ High CPU usage", alerts)
        self.assertIn("⚡ Elevated memory usage", alerts)
        self.assertIn("⚠️ Low disk space", alerts)
        self.assertIn("⚠️ High app memory usage", alerts)

    def test_resource_alerts_no_alerts(self):
        """Test resource alerts when no alerts are needed"""
        # Create resources with normal usage
        mock_resources = SystemResources(
            cpu_percent=25.0,
            memory_percent=45.0,
            memory_used_mb=8192.0,
            memory_total_mb=16384.0,
            disk_usage_percent=45.0,
            disk_used_gb=450.0,
            disk_total_gb=1000.0,
            network_sent_mb=1024.0,
            network_recv_mb=2048.0,
            process_count=150,
            uptime_hours=24.0,
            app_memory_mb=256.0,
            app_cpu_percent=5.0,
            app_threads=8,
            app_connections=2,
        )

        self.monitor._current_resources = mock_resources

        alerts = self.monitor.get_resource_alerts()

        # Should have no alerts
        self.assertEqual(len(alerts), 0)

    def test_performance_score_calculation(self):
        """Test performance score calculation"""
        # Create resources with good performance
        mock_resources = SystemResources(
            cpu_percent=20.0,
            memory_percent=40.0,
            memory_used_mb=8192.0,
            memory_total_mb=16384.0,
            disk_usage_percent=30.0,
            disk_used_gb=300.0,
            disk_total_gb=1000.0,
            network_sent_mb=1024.0,
            network_recv_mb=2048.0,
            process_count=150,
            uptime_hours=24.0,
            app_memory_mb=100.0,
            app_cpu_percent=5.0,
            app_threads=8,
            app_connections=2,
        )

        self.monitor._current_resources = mock_resources

        score, level = self.monitor.get_performance_score()

        # Should have good score and excellent or good level
        self.assertGreater(score, 60)
        self.assertIn(level, ["Excellent", "Good"])

    def test_performance_score_poor_performance(self):
        """Test performance score with poor performance"""
        # Create resources with poor performance
        mock_resources = SystemResources(
            cpu_percent=90.0,
            memory_percent=95.0,
            memory_used_mb=8192.0,
            memory_total_mb=16384.0,
            disk_usage_percent=95.0,
            disk_used_gb=950.0,
            disk_total_gb=1000.0,
            network_sent_mb=1024.0,
            network_recv_mb=2048.0,
            process_count=150,
            uptime_hours=24.0,
            app_memory_mb=2000.0,
            app_cpu_percent=5.0,
            app_threads=8,
            app_connections=2,
        )

        self.monitor._current_resources = mock_resources

        score, level = self.monitor.get_performance_score()

        # Should have low score and poor level
        self.assertLess(score, 40)
        self.assertEqual(level, "Poor")

    def test_performance_score_no_resources(self):
        """Test performance score when no resources available"""
        # Mock the get_resources method to return None
        with patch.object(self.monitor, "get_resources", return_value=None):
            score, level = self.monitor.get_performance_score()

            self.assertEqual(score, 0)
            self.assertEqual(level, "Unknown")

    @patch("src.helpmesign.utils.system_monitor.Thread")
    def test_start_monitoring(self, mock_thread):
        """Test starting system monitoring"""
        # Stop any existing monitoring and clear state
        self.monitor.stop_monitoring()
        self.monitor._monitor_thread = None
        self.monitor._stop_event.clear()

        mock_thread_instance = Mock()
        mock_thread_instance.is_alive.return_value = False  # Ensure it's not alive
        mock_thread.return_value = mock_thread_instance

        self.monitor.start_monitoring()

        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
        self.assertFalse(self.monitor._stop_event.is_set())

    def test_start_monitoring_already_running(self):
        """Test starting monitoring when already running"""
        # Mock thread as already running
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        self.monitor._monitor_thread = mock_thread

        with patch("src.helpmesign.utils.system_monitor.Thread") as mock_thread_class:
            self.monitor.start_monitoring()

            # Should not create new thread
            mock_thread_class.assert_not_called()

    def test_stop_monitoring(self):
        """Test stopping system monitoring"""
        # Mock thread
        mock_thread = Mock()
        self.monitor._monitor_thread = mock_thread

        self.monitor.stop_monitoring()

        self.assertTrue(self.monitor._stop_event.is_set())
        mock_thread.join.assert_called_once_with(timeout=5.0)


class TestSystemMonitorGlobalFunctions(unittest.TestCase):
    """Test global system monitor functions"""

    def setUp(self):
        """Set up test fixtures"""
        # Clear global instance
        import src.helpmesign.utils.system_monitor as sm

        sm._system_monitor = None

    def test_get_system_monitor_singleton(self):
        """Test get_system_monitor returns singleton instance"""
        monitor1 = get_system_monitor()
        monitor2 = get_system_monitor()

        self.assertIs(monitor1, monitor2)

    def test_start_system_monitoring(self):
        """Test start_system_monitoring function"""
        with patch(
            "src.helpmesign.utils.system_monitor.get_system_monitor"
        ) as mock_get:
            mock_monitor = Mock()
            mock_get.return_value = mock_monitor

            start_system_monitoring()

            mock_monitor.start_monitoring.assert_called_once()

    def test_stop_system_monitoring(self):
        """Test stop_system_monitoring function"""
        # Clear global instance first
        import src.helpmesign.utils.system_monitor as sm

        sm._system_monitor = None

        # Create a mock monitor and set it as the global instance
        mock_monitor = Mock()
        sm._system_monitor = mock_monitor

        stop_system_monitoring()

        mock_monitor.stop_monitoring.assert_called_once()


class TestSystemMonitorIntegration(unittest.TestCase):
    """Integration tests for system monitor"""

    def setUp(self):
        """Set up test fixtures"""
        self.monitor = SystemMonitor(update_interval=0.1)

    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self.monitor, "_monitor_thread") and self.monitor._monitor_thread:
            self.monitor.stop_monitoring()

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    @patch("psutil.net_io_counters")
    @patch("psutil.boot_time")
    @patch("psutil.pids")
    def test_full_monitoring_cycle(
        self, mock_pids, mock_boot_time, mock_net_io, mock_disk, mock_memory, mock_cpu
    ):
        """Test complete monitoring cycle"""
        # Mock all system calls
        mock_cpu.return_value = 30.0
        mock_memory.return_value = Mock(
            percent=50.0, used=8589934592, total=17179869184
        )
        mock_disk.return_value = Mock(
            percent=40.0, used=429496729600, total=1073741824000
        )
        mock_net_io.return_value = Mock(bytes_sent=1073741824, bytes_recv=2147483648)
        mock_boot_time.return_value = time.time() - 86400
        mock_pids.return_value = list(range(100))

        # Mock app process
        mock_process = Mock()
        mock_process.memory_info.return_value = Mock(rss=134217728)  # 128MB
        mock_process.cpu_percent.return_value = 3.0
        mock_process.num_threads.return_value = 6
        mock_process.connections.return_value = [Mock()]

        with patch("psutil.Process", return_value=mock_process):
            self.monitor._app_process = mock_process

            # Update resources
            self.monitor._update_resources()

            # Get formatted status
            status = self.monitor.get_formatted_status(compact=True)

            # Verify status contains expected information
            self.assertIn("30%", status)
            self.assertIn("50%", status)
            self.assertIn("128MB", status)

            # Check alerts
            alerts = self.monitor.get_resource_alerts()
            self.assertEqual(len(alerts), 0)  # No alerts for normal usage

            # Check performance score
            score, level = self.monitor.get_performance_score()
            self.assertGreater(score, 60)
            self.assertIn(level, ["Good", "Excellent"])


if __name__ == "__main__":
    unittest.main()
