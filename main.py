#!/usr/bin/env python3
"""
Main entry point for HelpMeSign application
"""

import sys
import argparse
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QCoreApplication
from src.helpmesign.utils.resource_manager import ResourceManager
from src.helpmesign.utils.logger import get_logger
from src.helpmesign.utils.language_manager import get_text, get_list, get_dict

# Set application name in environment (helps with macOS menubar)
if sys.platform == "darwin":  # macOS
    os.environ['APP_NAME'] = get_text("app.name")
    os.environ['CFBundleName'] = get_text("app.name")
    os.environ['CFBundleDisplayName'] = get_text("app.name")
    os.environ['QT_MAC_WANTS_LAYER'] = '1'
    os.environ['QT_MAC_DISABLE_ICON'] = '0'
    os.environ['QT_MAC_APP_NAME'] = get_text("app.name")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description=get_text("app.description"),
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
    
    # Set application name in environment before creating QApplication
    app_name = get_text("app.name")
    os.environ['QT_MAC_APP_NAME'] = app_name
    
    # Create Qt application first
    app = QApplication(sys.argv)
    
    # Set application metadata after QApplication creation
    app_name = get_text("app.name")
    QCoreApplication.setApplicationName(app_name)
    QCoreApplication.setApplicationVersion(get_text("app.version"))
    QCoreApplication.setOrganizationName(get_text("app.organization"))
    QCoreApplication.setOrganizationDomain(get_text("app.domain"))
    
    # Set the application name in the app object as well
    app.setApplicationName(app_name)
    app.setApplicationDisplayName(app_name)
    
    logger.debug("Application metadata set")
    logger.debug("QApplication created")
    
    # # Set additional properties for macOS
    # if sys.platform == "darwin":  # macOS
    #     app.setAttribute(QApplication.AA_EnableHighDpiScaling, True)
    #     app.setAttribute(QApplication.AA_UseHighDpiPixmaps, True)
    #     logger.debug("macOS-specific attributes set")
    
    # # Set application icon early
    # try:
    #     resource_manager = ResourceManager()
    #     icon_path = resource_manager.get_image_path('icon.png')
    #     if resource_manager.resource_exists('image', 'icon.png'):
    #         app.setWindowIcon(QIcon(icon_path))
    #         logger.info(f"Application icon set successfully: {icon_path}")
    #     else:
    #         logger.warning("Application icon not found in resources")
    # except Exception as e:
    #     logger.error(f"Could not set application icon: {e}")
    
    # Set additional properties for macOS
    if sys.platform == "darwin":  # macOS
        # Force the application name in the menu bar
        try:
            from PySide6.QtCore import QTimer
            def set_menu_name():
                # This ensures the menu name is set after the app is fully initialized
                app.setApplicationDisplayName(app_name)
                QCoreApplication.setApplicationName(app_name)
            
            # Delay slightly to ensure proper initialization
            QTimer.singleShot(0, set_menu_name)
        except Exception as e:
            logger.warning(f"Could not set delayed menu name: {e}")
        
        logger.debug("macOS-specific attributes set")
    
    # Set application icon early
    try:
        resource_manager = ResourceManager()
        icon_path = resource_manager.get_image_path('icon.png')
        if resource_manager.resource_exists('images', 'icon.png'):
            app.setWindowIcon(QIcon(icon_path))
            logger.info(f"Application icon set successfully: {icon_path}")
        else:
            logger.warning("Application icon not found in resources")
    except Exception as e:
        logger.error(f"Could not set application icon: {e}")
    
    # Create and run the application
    logger.info("Creating application")
    
    # Get the app class safely
    from src.helpmesign import get_app
    HelpMeSignApp = get_app()
    
    if HelpMeSignApp is None:
        logger.error("PySide6 is not available. Cannot create application.")
        sys.exit(1)
    
    helpmesign_app = HelpMeSignApp()
    helpmesign_app.run()
    
    logger.info("Application started successfully")
    
    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 