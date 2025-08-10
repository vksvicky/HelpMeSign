#!/usr/bin/env python3
"""
Logger env-agnostic tests for level fallback/validation.
"""

import logging


def test_logger_dev_level_fallback_when_level_missing():
    from src.helpmesign.utils.logger import HelpMeSignLogger

    config = {"logging": {"dev_level": "WARNING"}}
    logger = HelpMeSignLogger("TestLogger", config)
    assert logger.logger.level == logging.WARNING


def test_logger_invalid_levels_default_to_info():
    from src.helpmesign.utils.logger import HelpMeSignLogger

    config = {"logging": {"level": "INVALID", "dev_level": "ALSO_INVALID"}}
    logger = HelpMeSignLogger("TestLogger", config)
    assert logger.logger.level == logging.INFO
