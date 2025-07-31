#!/usr/bin/env python3
"""
Build script for creating Linux executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('build_linux.log')
    ]
)
logger = logging.getLogger(__name__)


def check_requirements():
    """Check if all requirements are met"""
    logger.info("🔍 Checking requirements...")
    
    # Check if running on Linux
    if platform.system() != 'Linux':
        logger.error("❌ This script must be run on Linux")
        return False
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8+ is required")
        return False
    
    logger.info(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check PyInstaller
    try:
        import PyInstaller
        logger.info("✅ PyInstaller is installed")
    except ImportError:
        logger.warning("❌ PyInstaller is not installed. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller"])
            logger.info("✅ PyInstaller installed successfully")
        except subprocess.CalledProcessError:
            logger.error("❌ Failed to install PyInstaller")
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
    parser = argparse.ArgumentParser(description="HelpMeSign - Sign Language Translation and Learning Application")
    parser.add_argument('--env', choices=['dev', 'prod'], default='prod', help='Environment to run in (default: prod)')
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Set application metadata
    QCoreApplication.setApplicationName("HelpMeSign")
    QCoreApplication.setApplicationVersion("1.0.0")
    QCoreApplication.setOrganizationName("CycleRunCode Club")
    QCoreApplication.setOrganizationDomain("https://cycleruncode.club")
    
    # Create Qt application
    app = QApplication(sys.argv)
    
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


def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_prod.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources/data/config.json', 'resources/data'),
        ('resources/data/sample_data.txt', 'resources/data'),
        ('resources/images/icon.png', 'resources/images'),
        ('resources/fonts/Roboto-Regular.ttf', 'resources/fonts'),
        ('resources/fonts/Roboto-Bold.ttf', 'resources/fonts'),
        ('resources/fonts/Roboto-Light.ttf', 'resources/fonts'),
        ('resources/fonts/Roboto-Medium.ttf', 'resources/fonts'),
        ('resources/fonts/Roboto-Thin.ttf', 'resources/fonts'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'helpmesign',
        'helpmesign.core',
        'helpmesign.ui',
        'helpmesign.utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'test', 'distutils'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HelpMeSign',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/images/icon.png',
)
'''
    
    with open('HelpMeSign.spec', 'w') as f:
        f.write(spec_content)
    
    logger.info("✅ Created HelpMeSign.spec")


def clean_build_directories():
    """Clean build and dist directories"""
    logger.info("🧹 Cleaning build directories...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['main_prod.py', 'HelpMeSign.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            logger.info(f"✅ Cleaned {dir_name}")
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            os.remove(file_name)
            logger.info(f"✅ Cleaned {file_name}")


def build_executable():
    """Build the Linux executable"""
    try:
        logger.info("🔨 Building Linux executable...")
        
        # Run PyInstaller
        subprocess.check_call([sys.executable, '-m', 'PyInstaller', 'HelpMeSign.spec'])
        
        logger.info("✅ Executable built successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Build failed: {e}")
        return False


def verify_executable():
    """Verify the executable was created correctly"""
    logger.info("🔍 Verifying executable...")
    
    exe_path = "dist/HelpMeSign"
    if not os.path.exists(exe_path):
        logger.error("❌ Executable not found")
        return False
    
    # Check file size
    exe_size = os.path.getsize(exe_path)
    exe_size_mb = exe_size / (1024 * 1024)
    logger.info(f"📦 Executable size: {exe_size_mb:.1f} MB")
    
    # Make executable
    os.chmod(exe_path, 0o755)
    logger.info("✅ Executable permissions set")
    
    logger.info("✅ Executable verification passed")
    return True


def create_desktop_file():
    """Create .desktop file for desktop integration"""
    logger.info("📦 Creating .desktop file...")
    
    desktop_content = '''[Desktop Entry]
Version=1.0
Type=Application
Name=HelpMeSign
Comment=Sign Language Translation and Learning Application
Exec={}/HelpMeSign
Icon={}/icon.png
Terminal=false
Categories=Education;Accessibility;
'''.format(os.path.abspath('dist'), os.path.abspath('dist/resources/images'))
    
    with open('HelpMeSign.desktop', 'w') as f:
        f.write(desktop_content)
    
    logger.info("✅ Created HelpMeSign.desktop")


def create_appimage():
    """Create AppImage (optional)"""
    logger.info("📦 Creating AppImage...")
    
    try:
        # Check if appimagetool is available
        subprocess.run(['which', 'appimagetool'], check=True, capture_output=True)
        
        # Create AppDir structure
        appdir = "HelpMeSign.AppDir"
        if os.path.exists(appdir):
            shutil.rmtree(appdir)
        
        os.makedirs(f"{appdir}/usr/bin", exist_ok=True)
        os.makedirs(f"{appdir}/usr/share/applications", exist_ok=True)
        os.makedirs(f"{appdir}/usr/share/icons/hicolor/256x256/apps", exist_ok=True)
        
        # Copy executable
        shutil.copy("dist/HelpMeSign", f"{appdir}/usr/bin/")
        
        # Copy desktop file
        shutil.copy("HelpMeSign.desktop", f"{appdir}/usr/share/applications/")
        
        # Copy icon
        shutil.copy("resources/images/icon.png", f"{appdir}/usr/share/icons/hicolor/256x256/apps/")
        
        # Create AppRun
        apprun_content = '''#!/bin/bash
cd "$(dirname "$0")"
exec "$(dirname "$0")/usr/bin/HelpMeSign" "$@"
'''
        with open(f"{appdir}/AppRun", 'w') as f:
            f.write(apprun_content)
        os.chmod(f"{appdir}/AppRun", 0o755)
        
        # Create AppImage
        subprocess.check_call(['appimagetool', appdir, 'HelpMeSign-1.0.0-x86_64.AppImage'])
        
        logger.info("✅ AppImage created successfully")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("⚠️  appimagetool not found, skipping AppImage creation")
        logger.info("💡 Install appimagetool: https://github.com/AppImage/appimagetool")
        return False


def create_debian_package():
    """Create Debian package (optional)"""
    logger.info("📦 Creating Debian package...")
    
    try:
        # Check if dpkg-deb is available
        subprocess.run(['which', 'dpkg-deb'], check=True, capture_output=True)
        
        # Create package structure
        pkg_dir = "helpmesign_1.0.0_amd64"
        if os.path.exists(pkg_dir):
            shutil.rmtree(pkg_dir)
        
        os.makedirs(f"{pkg_dir}/usr/bin", exist_ok=True)
        os.makedirs(f"{pkg_dir}/usr/share/applications", exist_ok=True)
        os.makedirs(f"{pkg_dir}/usr/share/icons/hicolor/256x256/apps", exist_ok=True)
        os.makedirs(f"{pkg_dir}/DEBIAN", exist_ok=True)
        
        # Copy files
        shutil.copy("dist/HelpMeSign", f"{pkg_dir}/usr/bin/")
        shutil.copy("HelpMeSign.desktop", f"{pkg_dir}/usr/share/applications/")
        shutil.copy("resources/images/icon.png", f"{pkg_dir}/usr/share/icons/hicolor/256x256/apps/")
        
        # Create control file
        control_content = '''Package: helpmesign
Version: 1.0.0
Architecture: amd64
Maintainer: HelpMeSign Team <support@helpmesign.com>
Depends: libc6, libstdc++6
Description: Sign Language Translation and Learning Application
 HelpMeSign is a desktop application for sign language
 translation and learning. It provides tools for converting
 text to sign language and educational content for learning
 sign language vocabulary and grammar.
'''
        with open(f"{pkg_dir}/DEBIAN/control", 'w') as f:
            f.write(control_content)
        
        # Create package
        subprocess.check_call(['dpkg-deb', '--build', pkg_dir])
        
        logger.info("✅ Debian package created successfully")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("⚠️  dpkg-deb not found, skipping Debian package creation")
        return False


def main():
    """Main build process"""
    logger.info("🚀 Starting Linux executable build process...")
    logger.info("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Clean previous builds
    clean_build_directories()
    
    # Create production main
    create_production_main()
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if not build_executable():
        sys.exit(1)
    
    # Verify executable
    if not verify_executable():
        sys.exit(1)
    
    # Create desktop file
    create_desktop_file()
    
    # Create AppImage (optional)
    create_appimage()
    
    # Create Debian package (optional)
    create_debian_package()
    
    logger.info("\n" + "=" * 50)
    logger.info("🎉 Build completed successfully!")
    logger.info(f"📦 Executable: dist/HelpMeSign")
    logger.info("💡 To run: ./dist/HelpMeSign")


if __name__ == "__main__":
    main() 