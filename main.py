#!/usr/bin/env python3
"""
Main entry point for HelpMeSign application
"""

import sys
import argparse
import os

# Set application metadata before importing Qt
os.environ['QT_MAC_WANTS_LAYER'] = '1'  # Force layer-backed views on macOS
os.environ['QT_MAC_DISABLE_ICON'] = '0'  # Enable icons on macOS

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QCoreApplication
from src.helpmesign.core.app import create_app
from src.helpmesign.utils.resource_manager import ResourceManager
from src.helpmesign.utils.logger import get_logger
from src.helpmesign.utils.language_manager import get_text, get_list, get_dict

# Set application name in environment (helps with macOS menubar)
if sys.platform == "darwin":  # macOS
    os.environ['APP_NAME'] = get_text("app.name")
    os.environ['CFBundleName'] = get_text("app.name")
    os.environ['CFBundleDisplayName'] = get_text("app.name")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="HelpMeSign - Sign Language Translation and Learning Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 main.py                    # Run in dev mode (default)
  python3 main.py --env dev          # Run in development mode
  python3 main.py --env prod         # Run in production mode
        """
    )
    
    parser.add_argument(
        '--env',
        choices=['dev', 'prod'],
        default='dev',
        help='Environment to run in (default: dev)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'{get_text("app.version")}'
    )
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Get logger
    logger = get_logger("helpmesign.main")
    logger.info("Starting HelpMeSign application")
    
    # Set application name before creating QApplication
    QCoreApplication.setApplicationName(get_text("app.name"))
    QCoreApplication.setApplicationVersion(get_text("app.version"))
    QCoreApplication.setOrganizationName(get_text("app.organization"))
    QCoreApplication.setOrganizationDomain(get_text("app.domain"))
    
    logger.debug("Application metadata set")
    
    # Create Qt application
    app = QApplication(sys.argv)
    logger.debug("QApplication created")
    
    # Set additional properties for macOS
    if sys.platform == "darwin":  # macOS
        app.setAttribute(QApplication.AA_DontShowIconsInMenus, False)
        app.setAttribute(QApplication.AA_EnableHighDpiScaling, True)
        app.setAttribute(QApplication.AA_UseHighDpiPixmaps, True)
        logger.debug("macOS-specific attributes set")
    
    # Set application icon early
    try:
        resource_manager = ResourceManager()
        icon_path = resource_manager.get_image_path('icon.png')
        if resource_manager.resource_exists('image', 'icon.png'):
            app.setWindowIcon(QIcon(icon_path))
            logger.info(f"Application icon set successfully: {icon_path}")
        else:
            logger.warning("Application icon not found in resources")
    except Exception as e:
        logger.error(f"Could not set application icon: {e}")
    
    # Create and run the application
    logger.info(f"Creating application in {args.env} environment")
    helpmesign_app = create_app(args.env)
    helpmesign_app.run()
    
    logger.info("Application started successfully")
    
    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 