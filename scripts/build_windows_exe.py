#!/usr/bin/env python3
"""
Build script for creating a Windows 64-bit executable for HelpMeSign
Uses PyInstaller to create a native Windows .exe file
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
    
    # Check if we're on Windows
    if platform.system() != 'Windows':
        print("❌ This script must be run on Windows")
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
    version_file=None,
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
    """Build the Windows executable"""
    print("🔨 Building Windows executable...")
    
    try:
        # Run PyInstaller
        subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'HelpMeSign.spec'
        ], check=True)
        
        print("✅ Windows executable built successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def verify_exe():
    """Verify the built executable"""
    print("🔍 Verifying built executable...")
    
    exe_path = "dist/HelpMeSign.exe"
    if not os.path.exists(exe_path):
        print("❌ Executable not found")
        return False
    
    print(f"✅ Executable found at: {exe_path}")
    
    # Check executable size
    exe_size = os.path.getsize(exe_path)
    exe_size_mb = exe_size / (1024 * 1024)
    print(f"📦 Executable size: {exe_size_mb:.1f} MB")
    
    # Check if it's 64-bit
    try:
        import pefile
        pe = pefile.PE(exe_path)
        if pe.OPTIONAL_HEADER.Magic == 0x20b:  # PE32+
            print("✅ 64-bit executable confirmed")
        else:
            print("⚠️  Executable is 32-bit")
    except ImportError:
        print("⚠️  pefile not available, cannot verify architecture")
    
    return True

def create_installer():
    """Create an NSIS installer (optional)"""
    print("📦 Creating NSIS installer...")
    
    # Create NSIS script
    nsis_script = '''!include "MUI2.nsh"

; Basic settings
Name "HelpMeSign"
OutFile "HelpMeSign-Setup.exe"
InstallDir "$PROGRAMFILES64\\HelpMeSign"
RequestExecutionLevel admin

; Interface settings
!define MUI_ABORTWARNING
!define MUI_ICON "resources\\images\\icon.png"
!define MUI_UNICON "resources\\images\\icon.png"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

Section "HelpMeSign" SecMain
    SetOutPath "$INSTDIR"
    File "dist\\HelpMeSign.exe"
    File "README.md"
    File "LICENSE"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    ; Create start menu shortcut
    CreateDirectory "$SMPROGRAMS\\HelpMeSign"
    CreateShortCut "$SMPROGRAMS\\HelpMeSign\\HelpMeSign.lnk" "$INSTDIR\\HelpMeSign.exe"
    CreateShortCut "$SMPROGRAMS\\HelpMeSign\\Uninstall.lnk" "$INSTDIR\\Uninstall.exe"
    
    ; Create desktop shortcut
    CreateShortCut "$DESKTOP\\HelpMeSign.lnk" "$INSTDIR\\HelpMeSign.exe"
    
    ; Registry entries
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\HelpMeSign" "DisplayName" "HelpMeSign"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\HelpMeSign" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\HelpMeSign" "DisplayIcon" "$INSTDIR\\HelpMeSign.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\HelpMeSign" "Publisher" "HelpMeSign"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\HelpMeSign" "DisplayVersion" "1.0.0"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\HelpMeSign" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\HelpMeSign" "NoRepair" 1
SectionEnd

Section "Uninstall"
    ; Remove files
    Delete "$INSTDIR\\HelpMeSign.exe"
    Delete "$INSTDIR\\README.md"
    Delete "$INSTDIR\\LICENSE"
    Delete "$INSTDIR\\Uninstall.exe"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\\HelpMeSign\\HelpMeSign.lnk"
    Delete "$SMPROGRAMS\\HelpMeSign\\Uninstall.lnk"
    RMDir "$SMPROGRAMS\\HelpMeSign"
    Delete "$DESKTOP\\HelpMeSign.lnk"
    
    ; Remove directory
    RMDir "$INSTDIR"
    
    ; Remove registry entries
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\HelpMeSign"
SectionEnd
'''
    
    with open('installer.nsi', 'w') as f:
        f.write(nsis_script)
    
    print("✅ Created installer.nsi")
    
    try:
        # Check if NSIS is available
        subprocess.run(['makensis', '/VERSION'], check=True, capture_output=True)
        
        # Create installer
        subprocess.run(['makensis', 'installer.nsi'], check=True)
        
        print("✅ NSIS installer created successfully!")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  NSIS not available, skipping installer creation")
        print("💡 Install NSIS: https://nsis.sourceforge.io/Download")
        return False

def main():
    """Main build process"""
    print("🪟 Building HelpMeSign for Windows")
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
    
    # Create installer (optional)
    create_installer()
    
    print("\n🎉 Windows build completed successfully!")
    print("📁 Executable location: dist/HelpMeSign.exe")
    print("💡 To run: dist\\HelpMeSign.exe")

if __name__ == "__main__":
    main() 