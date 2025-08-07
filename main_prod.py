#!/usr/bin/env python3
"""
Production entry point for HelpMeSign application
"""
import sys
import os
import argparse
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QCoreApplication
from src.helpmesign.core.app import create_app
from src.helpmesign.utils.resource_manager import ResourceManager

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Sign Language Translation and Learning Application")
    parser.add_argument('--env', choices=['dev', 'prod'], default='prod', help='Environment to run in (default: prod)')
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Set application metadata
    QCoreApplication.setApplicationName("HelpMeSign")
    QCoreApplication.setApplicationVersion("1.0.0")
    QCoreApplication.setOrganizationName("HelpMeSign")
    QCoreApplication.setOrganizationDomain("helpmesign.com")
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Set macOS-specific attributes
    app.setAttribute(QApplication.AA_DontShowIconsInMenus, False)
    app.setAttribute(QApplication.AA_EnableHighDpiScaling, True)
    app.setAttribute(QApplication.AA_UseHighDpiPixmaps, True)
    
    # Set application icon
    try:
        resource_manager = ResourceManager()
        icon_path = resource_manager.get_image_path('icon.png')
        if resource_manager.resource_exists('images', 'icon.png'):
            app.setWindowIcon(QIcon(icon_path))
    except Exception:
        pass  # Icon not critical for production
    
    # Create and run the application
    helpmesign_app = create_app(args.env)
    helpmesign_app.run()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
