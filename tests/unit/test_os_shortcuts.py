#!/usr/bin/env python3
"""
Test script to demonstrate OS-specific keyboard shortcuts
"""

import platform
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from helpmesign.ui.components import get_os_shortcuts

def test_os_detection():
    """Test OS detection and shortcut generation"""
    logger.info("=== OS-Specific Keyboard Shortcuts Test ===")
    
    # Get current OS
    system = platform.system()
    logger.info(f"Current OS: {system}")
    
    # Get shortcuts
    shortcuts = get_os_shortcuts()
    logger.info(f"Detected shortcuts: {shortcuts}")
    
    logger.info("=== Menu Examples ===")
    if system == "Darwin":  # macOS
        logger.info("macOS Menu Display:")
        if 'cmd' in shortcuts:
            logger.info(f"  Settings...    {shortcuts['cmd']},")
            logger.info(f"  Quit HelpMeSign {shortcuts['cmd']}Q")
            logger.info(f"  Clear All      {shortcuts['cmd']}K")
            logger.info(f"  Close Window   {shortcuts['cmd']}W")
        logger.info(f"  HelpMeSign Help F1")
    else:  # Windows/Linux
        logger.info("Windows/Linux Menu Display:")
        if 'cmd' in shortcuts:
            logger.info(f"  Settings...    {shortcuts['cmd']}+,")
            logger.info(f"  Quit HelpMeSign {shortcuts['cmd']}+Q")
            logger.info(f"  Clear All      {shortcuts['cmd']}+K")
            logger.info(f"  Close Window   {shortcuts['cmd']}+W")
        logger.info(f"  HelpMeSign Help F1")
    
    logger.info("=== Help Dialog Example ===")
    if system == "Darwin":
        logger.info("macOS Help Text:")
        if 'cmd' in shortcuts:
            logger.info(f"• {shortcuts['cmd']}, - Open Settings")
            logger.info(f"• {shortcuts['cmd']}K - Clear All")
            logger.info(f"• {shortcuts['cmd']}W - Close Window")
            logger.info(f"• {shortcuts['cmd']}Q - Quit Application")
        logger.info(f"• F1 - Show Help")
        if 'cmd' in shortcuts and 'enter' in shortcuts:
            logger.info(f"• {shortcuts['cmd']}{shortcuts['enter']} - Process Text")
        if 'cmd' in shortcuts and 'shift' in shortcuts:
            logger.info(f"• {shortcuts['cmd']}{shortcuts['shift']}K - Clear Text Input")
    else:
        logger.info("Windows/Linux Help Text:")
        if 'cmd' in shortcuts:
            logger.info(f"• {shortcuts['cmd']}+, - Open Settings")
            logger.info(f"• {shortcuts['cmd']}+K - Clear All")
            logger.info(f"• {shortcuts['cmd']}+W - Close Window")
            logger.info(f"• {shortcuts['cmd']}+Q - Quit Application")
        logger.info(f"• F1 - Show Help")
        if 'cmd' in shortcuts and 'enter' in shortcuts:
            logger.info(f"• {shortcuts['cmd']}+{shortcuts['enter']} - Process Text")
        if 'cmd' in shortcuts and 'shift' in shortcuts:
            logger.info(f"• {shortcuts['cmd']}+{shortcuts['shift']}+K - Clear Text Input")
    
    logger.info("=== Cross-Platform Build Test ===")
    logger.info("When you build the app for different platforms:")
    logger.info("• macOS app (.app): Will show ⌘ symbols")
    logger.info("• Windows exe (.exe): Will show Ctrl symbols")
    logger.info("• Linux executable: Will show Ctrl symbols")
    logger.info("The actual keyboard bindings work on all platforms!")

if __name__ == "__main__":
    test_os_detection() 