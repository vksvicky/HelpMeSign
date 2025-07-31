#!/usr/bin/env python3
"""
Build script for creating a Linux executable for HelpMeSign
Uses PyInstaller to create a native Linux executable
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
    
    # Check if we're on Linux
    if platform.system() != 'Linux':
        print("❌ This script must be run on Linux")
        return False
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✅ PyInstaller is installed")
    except ImportError:
        print("❌ PyInstaller is not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller installed successfully")
    
    return True

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources/images/icon.png', 'resources/images'),
        ('resources/data/config.json', 'resources/data'),
        ('resources/data/sample_data.txt', 'resources/data'),
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'helpmesign',
        'helpmesign.core',
        'helpmesign.ui',
        'helpmesign.utils',
        'helpmesign.services',
        'tkinter',
        'tkinter.ttk',
        'json',
        'pathlib',
        'datetime',
        'sys',
        'os',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'scipy', 'pandas', 'PIL', 'Pillow',
        'requests', 'psutil', 'coverage', 'pytest', 'unittest',
    ],
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
    
    print("✅ Created HelpMeSign.spec")

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
    
    # Clean PyInstaller cache
    cache_dir = os.path.expanduser('~/.cache/pyinstaller')
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        print("✅ Cleaned PyInstaller cache")
    
    print("✅ Build directories cleaned")

def build_exe():
    """Build the Linux executable"""
    print("🔨 Building Linux executable...")
    
    try:
        # Run PyInstaller
        subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'HelpMeSign.spec'
        ], check=True)
        
        print("✅ Linux executable built successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def verify_exe():
    """Verify the built executable"""
    print("🔍 Verifying built executable...")
    
    exe_path = "dist/HelpMeSign"
    if not os.path.exists(exe_path):
        print("❌ Executable not found")
        return False
    
    print(f"✅ Executable found at: {exe_path}")
    
    # Check executable size
    exe_size = os.path.getsize(exe_path)
    exe_size_mb = exe_size / (1024 * 1024)
    print(f"📦 Executable size: {exe_size_mb:.1f} MB")
    
    # Make executable
    os.chmod(exe_path, 0o755)
    print("✅ Made executable")
    
    return True

def create_package():
    """Create a tar.gz package"""
    print("📦 Creating tar.gz package...")
    
    try:
        import tarfile
        
        # Create tar.gz
        with tarfile.open('HelpMeSign.tar.gz', 'w:gz') as tar:
            tar.add('dist/HelpMeSign', arcname='HelpMeSign')
            tar.add('README.md', arcname='README.md')
            tar.add('LICENSE', arcname='LICENSE')
        
        print("✅ Created HelpMeSign.tar.gz")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create package: {e}")
        return False

def main():
    """Main build process"""
    print("🐧 Building HelpMeSign for Linux")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if not build_exe():
        sys.exit(1)
    
    # Verify executable
    if not verify_exe():
        sys.exit(1)
    
    # Create package
    create_package()
    
    print("\n🎉 Linux build completed successfully!")
    print("📁 Executable location: dist/HelpMeSign")
    print("📦 Package location: HelpMeSign.tar.gz")
    print("💡 To run: ./dist/HelpMeSign")

if __name__ == "__main__":
    main() 