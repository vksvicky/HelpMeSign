#!/usr/bin/env python3
"""
Application runner script for HelpMeSign
Provides command-line interface for running the application
"""

import sys
import argparse
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from helpmesign.core.app import create_app
from helpmesign.utils.logger import setup_logging, get_logger
from helpmesign.utils.resource_manager import ResourceManager
from helpmesign.utils.language_manager import get_text, get_list, get_dict


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="HelpMeSign - Sign Language Translation and Learning Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run_app.py                    # Run in dev mode (default)
  python3 run_app.py --env dev          # Run in development mode
  python3 run_app.py --env prod         # Run in production mode
  python3 run_app.py --env dev --debug  # Run in dev mode with debug logging
  python3 run_app.py --env prod --config custom.json  # Run in prod with custom config
        """
    )
    
    parser.add_argument(
        '--env',
        choices=['dev', 'prod'],
        default='dev',
        help='Environment to run in (default: dev)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom configuration file'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='HelpMeSign 1.0.0'
    )
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Get logger
    logger = get_logger("helpmesign.runner")
    logger.info("Starting HelpMeSign application runner")
    
    # Set up logging based on arguments
    if args.debug:
        # Configure debug logging
        import logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger.debug("Debug logging enabled")
    
    # Create Qt application
    app = QApplication(sys.argv)
    logger.debug("QApplication created")
    
    # Set application metadata (must be done before creating any windows)
    app.setApplicationName(get_text("app.name"))
    app.setApplicationVersion(get_text("app.version"))
    app.setOrganizationName(get_text("app.organization"))
    app.setOrganizationDomain(get_text("app.domain"))
    logger.debug("Application metadata set")
    
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
    
    try:
        # Create and run the application
        logger.info(f"Creating application in {args.env} environment")
        helpmesign_app = create_app(args.env)
        helpmesign_app.run()
        
        logger.info("Application started successfully")
        
        # Start the event loop
        sys.exit(app.exec())
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 