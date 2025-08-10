#!/usr/bin/env python3
"""
Window sizing behavior tests for HelpMeSignApp.
"""

from contextlib import ExitStack
from unittest.mock import Mock, patch


def test_setup_application_uses_default_1280x800_when_not_configured():
    from src.helpmesign.core.app import HelpMeSignApp

    with ExitStack() as stack:
        RM = stack.enter_context(patch("src.helpmesign.core.app.ResourceManager"))
        MW = stack.enter_context(patch("src.helpmesign.core.app.MainWindow"))
        MM = stack.enter_context(patch("src.helpmesign.core.app.ModeManager"))
        SL = stack.enter_context(patch("src.helpmesign.core.app.setup_logging"))
        GT = stack.enter_context(patch("src.helpmesign.core.app.get_text"))

        # minimal setup
        SL.return_value = Mock()
        RM.return_value.load_config.return_value = {}
        mw = Mock()
        MW.return_value = mw
        GT.return_value = "Test Title"

        app = HelpMeSignApp()
        # setup_application is invoked during __init__ in current implementation
        mw.resize.assert_called_with(1280, 800)


def test_setup_application_honors_window_size_from_config():
    from src.helpmesign.core.app import HelpMeSignApp

    with ExitStack() as stack:
        RM = stack.enter_context(patch("src.helpmesign.core.app.ResourceManager"))
        MW = stack.enter_context(patch("src.helpmesign.core.app.MainWindow"))
        MM = stack.enter_context(patch("src.helpmesign.core.app.ModeManager"))
        SL = stack.enter_context(patch("src.helpmesign.core.app.setup_logging"))
        GT = stack.enter_context(patch("src.helpmesign.core.app.get_text"))

        SL.return_value = Mock()
        RM.return_value.load_config.return_value = {
            "window_size": {"width": 1024, "height": 768}
        }
        mw = Mock()
        MW.return_value = mw
        GT.return_value = "Test Title"

        app = HelpMeSignApp()
        mw.resize.assert_called_with(1024, 768)
