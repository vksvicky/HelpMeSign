#!/usr/bin/env python3
"""
Universal build script for HelpMeSign
Builds for macOS and Windows based on the current platform
"""

import os
import sys
import platform
import subprocess

def main():
    """Main build process"""
    print("🚀 Universal Build Script for HelpMeSign")
    print("=" * 50)
    
    current_platform = platform.system()
    
    if current_platform == 'Darwin':
        print("🍎 Detected macOS - building macOS app...")
        subprocess.run([sys.executable, 'scripts/build_macos_app.py'], check=True)
        
    elif current_platform == 'Windows':
        print("🪟 Detected Windows - building Windows executable...")
        subprocess.run([sys.executable, 'scripts/build_windows_exe.py'], check=True)
        
    else:
        print(f"❌ Unsupported platform: {current_platform}")
        print("💡 Supported platforms: macOS, Windows")
        sys.exit(1)

if __name__ == "__main__":
    main() 