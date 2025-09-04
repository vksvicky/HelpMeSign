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

# Ensure venv site-packages is discoverable. Some launch methods can drop it.
try:
    import site
    venv_prefix = os.path.dirname(sys.executable)  # .../venv/bin
    venv_root = os.path.dirname(venv_prefix)      # .../venv
    sp = os.path.join(
        venv_root,
        'lib',
        f"python{sys.version_info.major}.{sys.version_info.minor}",
        'site-packages',
    )
    if os.path.isdir(sp) and sp not in sys.path:
        sys.path.append(sp)
except Exception:
    pass

from helpmesign.utils.logger import setup_logging, get_logger
from helpmesign.utils.resource_manager import ResourceManager
from helpmesign.utils.language_manager import get_text, get_list, get_dict


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description=get_text("app.description"),
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
        # Set DEBUG environment variable for UI debug features
        os.environ['DEBUG'] = 'true'
        
        # Configure debug logging
        import logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger.debug("Debug logging enabled")
        logger.debug("DEBUG environment variable set for UI debug features")
    
    # Create Qt application
    app = QApplication(sys.argv)
    logger.debug("QApplication created")
    
    # Set up signal handlers for graceful shutdown (after Qt app is created)
    import signal
    import atexit
    
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        # Don't call sys.exit() here - let the main loop handle it
        try:
            # Try to quit the Qt application gracefully
            app = QApplication.instance()
            if app:
                app.quit()
        except Exception:
            pass
    
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
    
    # Register cleanup function
    def cleanup():
        try:
            # Shutdown logging gracefully
            import logging
            logging.shutdown()
        except Exception:
            pass
    
    atexit.register(cleanup)

    # Optional 3D support: log interpreter and register glTF loader if available
    try:
        import importlib.util
        from importlib import metadata

        logger.info(f"3D: Python interpreter: {sys.executable}")
        gltf_spec = importlib.util.find_spec('panda3d_gltf')
        gltf_pkg_version = None
        try:
            gltf_pkg_version = metadata.version('panda3d-gltf')
        except Exception:
            pass
        logger.info(f"3D: glTF plugin present? spec={bool(gltf_spec)} pkg_version={gltf_pkg_version}")
        if gltf_spec is not None:
            try:
                import panda3d_gltf  # type: ignore  # noqa: F401
                logger.info("3D: glTF loader registered")
            except Exception as e:
                logger.warning(f"3D: Failed to register glTF loader: {e}")
    except Exception:
        pass
    
    # Set application metadata (must be done before creating any windows)
    app_name = get_text("app.name")
    app.setApplicationName(app_name)
    app.setApplicationVersion(get_text("app.version"))
    app.setOrganizationName(get_text("app.organization"))
    app.setOrganizationDomain(get_text("app.domain"))
    app.setApplicationDisplayName(app_name)
    
    # macOS-specific fix for menubar app name
    if sys.platform == "darwin":
        # Set the process name to match the application name
        # This helps with the menubar display on macOS
        try:
            import ctypes
            ctypes.CDLL('libc.dylib').setproctitle(app_name.encode('utf-8'))
        except:
            # Fallback if ctypes approach fails
            pass
    
    logger.debug("Application metadata set")
    
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
    
    try:
        # Create and run the application
        logger.info("Creating application")
        
        # Check if there's already an application instance
        existing_app = QApplication.instance()
        if existing_app and existing_app != app:
            logger.warning("Another QApplication instance detected, this might cause issues")
        
        # Get the app class safely
        from helpmesign import get_app
        HelpMeSignApp = get_app()
        
        if HelpMeSignApp is None:
            logger.error("PySide6 is not available. Cannot create application.")
            sys.exit(1)
        
        # Create only one application instance
        helpmesign_app = HelpMeSignApp()
        helpmesign_app.run()
        
        logger.info("Application started successfully")
        
        # Start the event loop with graceful shutdown handling
        try:
            exit_code = app.exec()
            sys.exit(exit_code)
        except KeyboardInterrupt:
            logger.info("Event loop interrupted, shutting down gracefully...")
            sys.exit(0)
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        try:
            # Graceful shutdown
            helpmesign_app.close() if 'helpmesign_app' in locals() else None
            app.quit()
        except Exception:
            pass
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running application: {e}")
        try:
            # Graceful shutdown even on error
            helpmesign_app.close() if 'helpmesign_app' in locals() else None
            app.quit()
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main() 