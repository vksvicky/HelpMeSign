#!/usr/bin/env python3
"""
Logging utility for HelpMeSign application
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional


class HelpMeSignLogger:
    """Centralized logging manager for HelpMeSign application"""

    def __init__(
        self,
        name: str = "HelpMeSign",
        config: Optional[Dict[str, Any]] = None,
        environment: str = "dev",
    ):
        self.name = name
        self.config = config or {}
        self.environment = environment.lower()
        self.logger = None
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Set up the logger with configuration"""
        # Create logger
        self.logger = logging.getLogger(self.name)

        # Get log level based on environment
        if self.environment == "prod":
            # Production: Use config or default to INFO
            log_level_str = self.config.get("logging", {}).get("level", "INFO").upper()
        else:
            # Development: Use config or default to DEBUG
            log_level_str = (
                self.config.get("logging", {}).get("dev_level", "DEBUG").upper()
            )

        log_level = getattr(logging, log_level_str, logging.INFO)
        self.logger.setLevel(log_level)

        # Clear any existing handlers
        self.logger.handlers.clear()

        # Create formatters based on environment
        if self.environment == "prod":
            # Production: Simple formatter
            detailed_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            simple_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
        else:
            # Development: Detailed formatter with file and line info
            detailed_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s"
            )
            simple_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)

        # File handler (if enabled in config)
        if self.config.get("logging", {}).get("file_enabled", True):
            log_file = self._get_log_file_path()
            if log_file:
                try:
                    # Ensure log directory exists
                    log_file.parent.mkdir(parents=True, exist_ok=True)

                    # Create rotating file handler
                    file_handler = logging.handlers.RotatingFileHandler(
                        log_file, maxBytes=1024 * 1024, backupCount=5  # 1MB
                    )
                    file_handler.setLevel(log_level)
                    file_handler.setFormatter(detailed_formatter)
                    self.logger.addHandler(file_handler)

                    self.logger.info(f"Logging to file: {log_file}")
                except Exception as e:
                    self.logger.warning(f"Could not set up file logging: {e}")

        # Log startup information
        self.logger.info(
            f"Logger initialized for '{self.name}' with level: {log_level_str} in {self.environment} environment"
        )

    def _get_log_file_path(self) -> Optional[Path]:
        """Get the log file path"""
        # Try to get from config first
        config_log_path = self.config.get("logging", {}).get("file_path")
        if config_log_path:
            return Path(config_log_path)

        # Default to user's home directory with environment suffix
        try:
            log_dir = Path.home() / ".helpmesign" / "logs"
            log_filename = f"{self.name}_{self.environment}.log"
            return log_dir / log_filename
        except Exception:
            return None

    def get_logger(self) -> logging.Logger:
        """Get the configured logger"""
        return self.logger

    def set_level(self, level: str) -> None:
        """Set the log level dynamically"""
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(log_level)

        # Update all handlers
        for handler in self.logger.handlers:
            handler.setLevel(log_level)

    def add_file_handler(self, file_path: str) -> None:
        """Add an additional file handler"""
        try:
            file_handler = logging.FileHandler(file_path)
            file_handler.setLevel(self.logger.level)

            # Use detailed formatter for file logging
            if self.environment == "prod":
                formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            else:
                formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s"
                )

            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            self.logger.info(f"Added file handler: {file_path}")
        except Exception as e:
            self.logger.error(f"Could not add file handler: {e}")


# Global logger instance
_logger_instance = None


def get_logger(
    name: str = "helpmesign",
    config: Optional[Dict[str, Any]] = None,
    environment: str = "dev",
) -> logging.Logger:
    """Get a logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = HelpMeSignLogger(name, config, environment)
    return _logger_instance.get_logger()


def setup_logging(config: Dict[str, Any], environment: str = "dev") -> logging.Logger:
    """Set up logging with configuration"""
    global _logger_instance
    _logger_instance = HelpMeSignLogger("helpmesign", config, environment)
    return _logger_instance.get_logger()


def set_log_level(level: str) -> None:
    """Set the log level for the global logger"""
    if _logger_instance:
        _logger_instance.set_level(level)


def log_function_entry(logger: logging.Logger, func_name: str, **kwargs) -> None:
    """Log function entry with parameters"""
    if logger.isEnabledFor(logging.DEBUG):
        params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        logger.debug(f"Entering {func_name}({params})")


def log_function_exit(logger: logging.Logger, func_name: str, result=None) -> None:
    """Log function exit with result"""
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Exiting {func_name} -> {result}")


def log_exception(logger: logging.Logger, message: str, exc_info=True) -> None:
    """Log an exception with full traceback"""
    logger.error(message, exc_info=exc_info)
