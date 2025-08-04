"""
System Resource Monitor for HelpMeSign
Provides real-time monitoring of system resources specific to the application
"""

import os
import platform
import time
from dataclasses import dataclass
from threading import Event, Thread
from typing import Any, Dict, Optional, Tuple

import psutil

from .logger import get_logger


@dataclass
class SystemResources:
    """Data class for system resource information"""

    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_usage_percent: float
    disk_used_gb: float
    disk_total_gb: float
    network_sent_mb: float
    network_recv_mb: float
    process_count: int
    uptime_hours: float
    app_memory_mb: float
    app_cpu_percent: float
    app_threads: int
    app_connections: int


class SystemMonitor:
    """Real-time system resource monitor for HelpMeSign"""

    def __init__(self, update_interval: float = 2.0):
        """Initialize the system monitor

        Args:
            update_interval: Update interval in seconds
        """
        self.update_interval = update_interval
        self.logger = get_logger("helpmesign.system_monitor")
        self._stop_event = Event()
        self._monitor_thread: Optional[Thread] = None
        self._current_resources: Optional[SystemResources] = None
        self._last_update = 0.0
        self._app_process: Optional[psutil.Process] = None

        # Initialize app process tracking
        self._init_app_process()

    def _init_app_process(self) -> None:
        """Initialize tracking of the current application process"""
        try:
            current_pid = os.getpid()
            self._app_process = psutil.Process(current_pid)
            self.logger.debug(
                f"Initialized app process monitoring for PID: {current_pid}"
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize app process monitoring: {e}")
            self._app_process = None

    def start_monitoring(self) -> None:
        """Start the system monitoring thread"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            self.logger.warning("System monitor is already running")
            return

        self._stop_event.clear()
        self._monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        self.logger.info("System monitoring started")

    def stop_monitoring(self) -> None:
        """Stop the system monitoring thread"""
        self._stop_event.set()
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)
        self.logger.info("System monitoring stopped")

    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        while not self._stop_event.is_set():
            try:
                self._update_resources()
                time.sleep(self.update_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.update_interval)

    def _update_resources(self) -> None:
        """Update current system resources"""
        try:
            # Get system-wide metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            network = psutil.net_io_counters()

            # Get app-specific metrics
            app_memory_mb = 0.0
            app_cpu_percent = 0.0
            app_threads = 0
            app_connections = 0

            if self._app_process:
                try:
                    app_memory_mb = self._app_process.memory_info().rss / 1024 / 1024
                    app_cpu_percent = self._app_process.cpu_percent()
                    app_threads = self._app_process.num_threads()
                    app_connections = len(self._app_process.connections())
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Process may have ended or we don't have access
                    self._init_app_process()

            # Calculate uptime
            uptime_seconds = time.time() - psutil.boot_time()
            uptime_hours = uptime_seconds / 3600

            self._current_resources = SystemResources(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                memory_total_mb=memory.total / 1024 / 1024,
                disk_usage_percent=disk.percent,
                disk_used_gb=disk.used / 1024 / 1024 / 1024,
                disk_total_gb=disk.total / 1024 / 1024 / 1024,
                network_sent_mb=network.bytes_sent / 1024 / 1024,
                network_recv_mb=network.bytes_recv / 1024 / 1024,
                process_count=len(psutil.pids()),
                uptime_hours=uptime_hours,
                app_memory_mb=app_memory_mb,
                app_cpu_percent=app_cpu_percent,
                app_threads=app_threads,
                app_connections=app_connections,
            )

            self._last_update = time.time()

        except Exception as e:
            self.logger.error(f"Error updating system resources: {e}")

    def get_resources(self) -> Optional[SystemResources]:
        """Get current system resources

        Returns:
            Current system resources or None if not available
        """
        if self._current_resources is None:
            self._update_resources()
        return self._current_resources

    def get_formatted_status(self, compact: bool = True) -> str:
        """Get formatted status string for display

        Args:
            compact: If True, show compact format; if False, show detailed format

        Returns:
            Formatted status string
        """
        resources = self.get_resources()
        if resources is None:
            return "System: Unavailable"

        if compact:
            return self._get_compact_status(resources)
        else:
            return self._get_detailed_status(resources)

    def _get_compact_status(self, resources: SystemResources) -> str:
        """Get compact status format"""
        # Show most critical metrics in compact format
        cpu_icon = self._get_cpu_icon(resources.cpu_percent)
        mem_icon = self._get_memory_icon(resources.memory_percent)
        app_icon = self._get_app_icon(resources.app_memory_mb)

        return f"{cpu_icon} {resources.cpu_percent:.0f}% | {mem_icon} {resources.memory_percent:.0f}% | {app_icon} {resources.app_memory_mb:.0f}MB"

    def _get_detailed_status(self, resources: SystemResources) -> str:
        """Get detailed status format"""
        return (
            f"CPU: {resources.cpu_percent:.1f}% | "
            f"RAM: {resources.memory_percent:.1f}% ({resources.memory_used_mb:.0f}MB) | "
            f"Disk: {resources.disk_usage_percent:.1f}% | "
            f"App: {resources.app_memory_mb:.0f}MB | "
            f"Uptime: {resources.uptime_hours:.1f}h"
        )

    def _get_cpu_icon(self, cpu_percent: float) -> str:
        """Get CPU usage icon based on percentage"""
        if cpu_percent < 30:
            return "🟢"
        elif cpu_percent < 70:
            return "🟡"
        else:
            return "🔴"

    def _get_memory_icon(self, memory_percent: float) -> str:
        """Get memory usage icon based on percentage"""
        if memory_percent < 50:
            return "🟢"
        elif memory_percent < 80:
            return "🟡"
        else:
            return "🔴"

    def _get_app_icon(self, app_memory_mb: float) -> str:
        """Get app memory usage icon based on size"""
        if app_memory_mb < 100:
            return "💚"
        elif app_memory_mb < 500:
            return "💛"
        else:
            return "❤️"

    def get_resource_alerts(self) -> list[str]:
        """Get any resource alerts that should be shown to the user

        Returns:
            List of alert messages
        """
        resources = self.get_resources()
        if resources is None:
            return []

        alerts = []

        # CPU alerts
        if resources.cpu_percent > 90:
            alerts.append("⚠️ High CPU usage")
        elif resources.cpu_percent > 70:
            alerts.append("⚡ Elevated CPU usage")

        # Memory alerts
        if resources.memory_percent > 90:
            alerts.append("⚠️ High memory usage")
        elif resources.memory_percent > 80:
            alerts.append("⚡ Elevated memory usage")

        # App-specific alerts
        if resources.app_memory_mb > 1000:
            alerts.append("⚠️ High app memory usage")

        # Disk alerts
        if resources.disk_usage_percent > 90:
            alerts.append("⚠️ Low disk space")

        return alerts

    def get_performance_score(self) -> Tuple[int, str]:
        """Get overall system performance score

        Returns:
            Tuple of (score 0-100, performance level)
        """
        resources = self.get_resources()
        if resources is None:
            return 0, "Unknown"

        # Calculate score based on multiple factors
        cpu_score = max(0, 100 - resources.cpu_percent)
        memory_score = max(0, 100 - resources.memory_percent)
        disk_score = max(0, 100 - resources.disk_usage_percent)

        # App-specific scoring
        app_memory_score = max(
            0, 100 - (resources.app_memory_mb / 10)
        )  # Penalize high app memory

        # Weighted average
        total_score = (
            cpu_score * 0.3
            + memory_score * 0.3
            + disk_score * 0.2
            + app_memory_score * 0.2
        )

        # Determine performance level
        if total_score >= 80:
            level = "Excellent"
        elif total_score >= 60:
            level = "Good"
        elif total_score >= 40:
            level = "Fair"
        else:
            level = "Poor"

        return int(total_score), level


# Global system monitor instance
_system_monitor: Optional[SystemMonitor] = None


def get_system_monitor() -> SystemMonitor:
    """Get the global system monitor instance"""
    global _system_monitor
    if _system_monitor is None:
        _system_monitor = SystemMonitor()
    return _system_monitor


def start_system_monitoring() -> None:
    """Start system monitoring"""
    monitor = get_system_monitor()
    monitor.start_monitoring()


def stop_system_monitoring() -> None:
    """Stop system monitoring"""
    global _system_monitor
    if _system_monitor:
        _system_monitor.stop_monitoring()
        _system_monitor = None
