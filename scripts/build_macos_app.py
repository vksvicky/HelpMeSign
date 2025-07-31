#!/usr/bin/env python3
"""
Build script for creating macOS app bundle using py2app
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('build_macos.log')
    ]
)
logger = logging.getLogger(__name__)


def check_requirements():
    """Check if all requirements are met"""
    logger.info("🔍 Checking requirements...")
    
    # Check if running on macOS
    if sys.platform != "darwin":
        logger.error("❌ This script must be run on macOS")
        return False
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8+ is required")
        return False
    
    logger.info(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check py2app
    try:
        import py2app
        logger.info("✅ py2app is installed")
    except ImportError:
        logger.warning("❌ py2app is not installed. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "py2app"])
            logger.info("✅ py2app installed successfully")
        except subprocess.CalledProcessError:
            logger.error("❌ Failed to install py2app")
            return False
    
    # Check PySide6
    try:
        import PySide6
        logger.info("✅ PySide6 is installed")
    except ImportError:
        logger.warning("❌ PySide6 is not installed. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PySide6"])
            logger.info("✅ PySide6 installed successfully")
        except subprocess.CalledProcessError:
            logger.error("❌ Failed to install PySide6")
            return False
    
    return True


def create_setup_script():
    """Create setup.py for py2app"""
    setup_content = '''#!/usr/bin/env python3
"""
Setup script for py2app
"""

from setuptools import setup

APP = ['main_prod.py']
DATA_FILES = [
    ('resources', [
        'resources/data/config.json',
        'resources/data/sample_data.txt',
        'resources/images/icon.png',
        'resources/fonts/Roboto-Regular.ttf',
        'resources/fonts/Roboto-Bold.ttf',
        'resources/fonts/Roboto-Light.ttf',
        'resources/fonts/Roboto-Medium.ttf',
        'resources/fonts/Roboto-Thin.ttf'
    ])
]

OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'resources/images/icon.png',
    'plist': {
        'CFBundleName': 'HelpMeSign',
        'CFBundleDisplayName': 'HelpMeSign',
        'CFBundleIdentifier': 'com.helpmesign.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
    },
    'packages': ['PySide6', 'helpmesign'],
    'includes': ['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets'],
    'excludes': ['tkinter', 'test', 'distutils'],
    'optimize': 2,
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
'''
    
    with open('setup_macos.py', 'w') as f:
        f.write(setup_content)
    
    logger.info("✅ Created setup_macos.py")


def create_production_main():
    """Create main_prod.py for production build"""
    prod_main_content = '''#!/usr/bin/env python3
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
        if resource_manager.resource_exists('image', 'icon.png'):
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
'''
    
    with open('main_prod.py', 'w') as f:
        f.write(prod_main_content)
    
    logger.info("✅ Created main_prod.py for production build")


def clean_build_directories():
    """Clean build and dist directories"""
    logger.info("🧹 Cleaning build directories...")
    
    dirs_to_clean = ['build', 'dist']
    files_to_clean = ['setup_macos.py', 'main_prod.py']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            logger.info(f"✅ Cleaned {dir_name}")
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            os.remove(file_name)
            logger.info(f"✅ Cleaned {file_name}")


def build_app():
    """Build the macOS app bundle"""
    try:
        logger.info("🔨 Building macOS app bundle...")
        
        # Run py2app
        subprocess.check_call([sys.executable, 'setup_macos.py', 'py2app'])
        
        logger.info("✅ App bundle built successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Build failed: {e}")
        return False


def verify_app_bundle():
    """Verify the app bundle was created correctly"""
    logger.info("🔍 Verifying app bundle...")
    
    app_path = "dist/HelpMeSign.app"
    if not os.path.exists(app_path):
        logger.error("❌ App bundle not found")
        return False
    
    # Check for required files
    required_files = [
        "dist/HelpMeSign.app/Contents/MacOS/HelpMeSign",
        "dist/HelpMeSign.app/Contents/Info.plist",
        "dist/HelpMeSign.app/Contents/Resources/",
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            logger.error(f"❌ Missing required file: {file_path}")
            return False
    
    logger.info("✅ App bundle verification passed")
    return True


def create_dmg():
    """Create DMG file for distribution"""
    logger.info("📦 Creating DMG file...")
    
    try:
        # Check if create-dmg is available
        subprocess.run(['which', 'create-dmg'], check=True, capture_output=True)
        
        # Create DMG
        dmg_name = "HelpMeSign-1.0.0.dmg"
        app_path = "dist/HelpMeSign.app"
        
        subprocess.check_call([
            'create-dmg',
            '--volname', 'HelpMeSign',
            '--window-pos', '200', '120',
            '--window-size', '600', '400',
            '--icon-size', '100',
            '--icon', 'HelpMeSign.app', '175', '120',
            '--hide-extension', 'HelpMeSign.app',
            '--app-drop-link', '425', '120',
            dmg_name,
            app_path
        ])
        
        logger.info("✅ DMG file created successfully")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("⚠️  create-dmg not found, skipping DMG creation")
        logger.info("💡 Install create-dmg: brew install create-dmg")
        return False


def main():
    """Main build process"""
    logger.info("🚀 Starting macOS app build process...")
    logger.info("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Clean previous builds
    clean_build_directories()
    
    # Create setup script
    create_setup_script()
    
    # Create production main
    create_production_main()
    
    # Build app bundle
    if not build_app():
        sys.exit(1)
    
    # Verify app bundle
    if not verify_app_bundle():
        sys.exit(1)
    
    # Create DMG (optional)
    create_dmg()
    
    logger.info("\n" + "=" * 50)
    logger.info("🎉 Build completed successfully!")
    logger.info(f"📱 App bundle: dist/HelpMeSign.app")
    logger.info("💡 To run: open dist/HelpMeSign.app")


if __name__ == "__main__":
    main() 