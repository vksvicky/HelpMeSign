#!/usr/bin/env python3
"""
Build script for creating a macOS app bundle for HelpMeSign
Uses py2app to create a native macOS .app bundle
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    # Check if we're on macOS
    if platform.system() != 'Darwin':
        print("❌ This script must be run on macOS")
        return False
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check if py2app is installed
    try:
        import py2app
        print("✅ py2app is installed")
    except ImportError:
        print("❌ py2app is not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "py2app"], check=True)
        print("✅ py2app installed successfully")
    
    return True

def create_setup_py():
    """Create setup.py for py2app"""
    setup_content = '''#!/usr/bin/env python3
"""
Setup script for py2app to create macOS app bundle
"""

from setuptools import setup
import py2app

# App configuration
APP = ['main.py']
DATA_FILES = [
    ('resources', [
        'resources/images/icon.png',
        'resources/data/config.json',
        'resources/data/sample_data.txt'
    ]),
    ('', ['README.md', 'LICENSE'])
]

OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'resources/images/icon.png',
    'plist': {
        'CFBundleName': 'HelpMeSign',
        'CFBundleDisplayName': 'HelpMeSign',
        'CFBundleIdentifier': 'com.helpmesign.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': '© 2024 HelpMeSign',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.14.0',
        'NSRequiresAquaSystemAppearance': False,
    },
    'packages': ['tkinter', 'json', 'pathlib'],
    'includes': ['helpmesign'],
    'excludes': ['matplotlib', 'numpy', 'scipy', 'pandas'],
    'optimize': 2,
    'strip': True,
}

setup(
    name='HelpMeSign',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
'''
    
    with open('setup_macos.py', 'w') as f:
        f.write(setup_content)
    
    print("✅ Created setup_macos.py")

def clean_build_dirs():
    """Clean previous build directories"""
    print("🧹 Cleaning previous build directories...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ Cleaned {dir_name}")
    
    # Clean .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
    
    print("✅ Build directories cleaned")

def build_app():
    """Build the macOS app"""
    print("🔨 Building macOS app...")
    
    try:
        # Run py2app
        subprocess.run([
            sys.executable, 'setup_macos.py', 'py2app', '--clean'
        ], check=True)
        
        print("✅ macOS app built successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def verify_app():
    """Verify the built app"""
    print("🔍 Verifying built app...")
    
    app_path = "dist/HelpMeSign.app"
    if not os.path.exists(app_path):
        print("❌ App bundle not found")
        return False
    
    print(f"✅ App bundle found at: {app_path}")
    
    # Check app size
    app_size = sum(f.stat().st_size for f in Path(app_path).rglob('*') if f.is_file())
    app_size_mb = app_size / (1024 * 1024)
    print(f"📦 App size: {app_size_mb:.1f} MB")
    
    # Check if app is executable
    try:
        subprocess.run(['open', app_path], check=True, timeout=5)
        print("✅ App launches successfully")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        print("⚠️  Could not test app launch (this is normal in CI)")
    
    return True

def create_dmg():
    """Create a DMG installer (optional)"""
    print("📦 Creating DMG installer...")
    
    try:
        # Check if create-dmg is available
        subprocess.run(['which', 'create-dmg'], check=True, capture_output=True)
        
        # Create DMG
        subprocess.run([
            'create-dmg',
            '--volname', 'HelpMeSign',
            '--window-pos', '200', '120',
            '--window-size', '600', '400',
            '--icon-size', '100',
            '--icon', 'HelpMeSign.app', '175', '120',
            '--hide-extension', 'HelpMeSign.app',
            '--app-drop-link', '425', '120',
            'HelpMeSign.dmg',
            'dist/'
        ], check=True)
        
        print("✅ DMG created successfully!")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  create-dmg not available, skipping DMG creation")
        print("💡 Install create-dmg: brew install create-dmg")
        return False

def main():
    """Main build process"""
    print("🍎 Building HelpMeSign for macOS")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Create setup.py
    create_setup_py()
    
    # Build app
    if not build_app():
        sys.exit(1)
    
    # Verify app
    if not verify_app():
        sys.exit(1)
    
    # Create DMG (optional)
    create_dmg()
    
    print("\n🎉 macOS build completed successfully!")
    print("📁 App location: dist/HelpMeSign.app")
    print("💡 To run: open dist/HelpMeSign.app")

if __name__ == "__main__":
    main() 