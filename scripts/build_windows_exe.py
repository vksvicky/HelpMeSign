#!/usr/bin/env python3
"""
Build script for creating Windows executable using PyInstaller
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
        logging.FileHandler('build_windows.log')
    ]
)
logger = logging.getLogger(__name__)


def check_requirements():
    """Check if all requirements are met"""
    logger.info("🔍 Checking requirements...")
    
    # Check if running on Windows
    if platform.system() != 'Windows':
        logger.error("❌ This script must be run on Windows")
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
    QCoreApplication.setOrganizationName("HelpMeSign")
    QCoreApplication.setOrganizationDomain("helpmesign.com")
    
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
    version_file=None,
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
    """Build the Windows executable"""
    try:
        logger.info("🔨 Building Windows executable...")
        
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
    
    exe_path = "dist/HelpMeSign.exe"
    if not os.path.exists(exe_path):
        logger.error("❌ Executable not found")
        return False
    
    # Check file size
    exe_size = os.path.getsize(exe_path)
    exe_size_mb = exe_size / (1024 * 1024)
    logger.info(f"📦 Executable size: {exe_size_mb:.1f} MB")
    
    # Try to get version info (Windows-specific)
    try:
        import win32api
        info = win32api.GetFileVersionInfo(exe_path, "\\")
        version = f"{info['FileVersionMS'] >> 16}.{info['FileVersionMS'] & 0xFFFF}.{info['FileVersionLS'] >> 16}.{info['FileVersionLS'] & 0xFFFF}"
        logger.info(f"✅ Executable version: {version}")
    except ImportError:
        logger.warning("⚠️  pywin32 not available, skipping version check")
    except Exception:
        logger.warning("⚠️  Could not get version info")
    
    logger.info("✅ Executable verification passed")
    return True


def create_installer():
    """Create NSIS installer"""
    logger.info("📦 Creating installer...")
    
    try:
        # Check if NSIS is available
        subprocess.run(['makensis', '/VERSION'], check=True, capture_output=True)
        
        # Create NSIS script
        nsis_script = '''!define APP_NAME "HelpMeSign"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "HelpMeSign"
!define APP_EXE "HelpMeSign.exe"

!include "MUI2.nsh"

Name "${APP_NAME}"
OutFile "HelpMeSign-Setup.exe"
InstallDir "$PROGRAMFILES\\${APP_NAME}"
InstallDirRegKey HKCU "Software\\${APP_NAME}" ""

!define MUI_ABORTWARNING
!define MUI_ICON "resources\\images\\icon.ico"
!define MUI_UNICON "resources\\images\\icon.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Main Application" SecMain
    SetOutPath "$INSTDIR"
    File "dist\\${APP_EXE}"
    
    WriteRegStr HKCU "Software\\${APP_NAME}" "" $INSTDIR
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    CreateDirectory "$SMPROGRAMS\\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk" "$INSTDIR\\${APP_EXE}"
    CreateShortCut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\${APP_EXE}"
    
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\${APP_EXE}"
    Delete "$INSTDIR\\Uninstall.exe"
    RMDir "$INSTDIR"
    
    Delete "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk"
    RMDir "$SMPROGRAMS\\${APP_NAME}"
    Delete "$DESKTOP\\${APP_NAME}.lnk"
    
    DeleteRegKey HKCU "Software\\${APP_NAME}"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}"
SectionEnd
'''
        
        with open('installer.nsi', 'w') as f:
            f.write(nsis_script)
        
        # Run NSIS
        subprocess.check_call(['makensis', 'installer.nsi'])
        
        logger.info("✅ Installer created successfully")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("⚠️  NSIS not found, skipping installer creation")
        logger.info("💡 Install NSIS: https://nsis.sourceforge.io/Download")
        return False


def main():
    """Main build process"""
    logger.info("🚀 Starting Windows executable build process...")
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
    
    # Create installer (optional)
    create_installer()
    
    logger.info("\n" + "=" * 50)
    logger.info("🎉 Build completed successfully!")
    logger.info(f"📦 Executable: dist/HelpMeSign.exe")
    logger.info("💡 To run: dist\\HelpMeSign.exe")


if __name__ == "__main__":
    main() 