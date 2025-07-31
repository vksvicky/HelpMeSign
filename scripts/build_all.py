#!/usr/bin/env python3
"""
Universal build script for HelpMeSign
Builds for macOS and Windows based on the current platform
"""

import os
import sys
import platform
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main build process"""
    logger.info("🚀 Universal Build Script for HelpMeSign")
    logger.info("=" * 50)
    
    current_platform = platform.system()
    
    if current_platform == 'Darwin':
        logger.info("🍎 Detected macOS - building macOS app...")
        subprocess.run([sys.executable, 'scripts/build_macos_app.py'], check=True)
        
    elif current_platform == 'Windows':
        logger.info("🪟 Detected Windows - building Windows executable...")
        subprocess.run([sys.executable, 'scripts/build_windows_exe.py'], check=True)
        
    else:
        logger.error(f"❌ Unsupported platform: {current_platform}")
        logger.info("💡 Supported platforms: macOS, Windows")
        sys.exit(1)

if __name__ == "__main__":
    main() 