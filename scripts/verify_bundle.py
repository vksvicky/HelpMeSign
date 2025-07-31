#!/usr/bin/env python3
"""
Bundle verification script for HelpMeSign
Verifies that all required files and configurations are present
"""

import os
import json
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('verify_bundle.log')
    ]
)
logger = logging.getLogger(__name__)


def verify_config_files():
    """Verify configuration files are present and valid"""
    logger.info("🔍 Verifying configuration files...")
    
    config_path = Path("resources/data/config.json")
    
    if not config_path.exists():
        logger.error("❌ Config file not found: resources/data/config.json")
        return False
    else:
        logger.info("✅ Config file found: resources/data/config.json")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info("✅ Config file is valid JSON")
    except json.JSONDecodeError as e:
        logger.error(f"❌ Config file is not valid JSON: {e}")
        return False
    
    # Check required sections
    required_sections = ['app_name', 'version', 'window_size', 'theme', 'logging']
    
    for section in required_sections:
        if section not in config:
            logger.error(f"❌ Missing required config section: {section}")
            return False
    
    logger.info("✅ All required config sections present")
    
    # Check window size configuration
    window_size = config.get('window_size', {})
    if 'width' not in window_size or 'height' not in window_size:
        logger.error("❌ Window size configuration incomplete")
        return False
    
    logger.info(f"✅ Window size: {window_size['width']}x{window_size['height']}")
    
    # Check theme configuration
    theme = config.get('theme', {})
    if 'primary_color' not in theme:
        logger.error("❌ Theme configuration incomplete")
        return False
    
    logger.info(f"✅ Primary color: {theme['primary_color']}")
    
    return True


def verify_sample_data():
    """Verify sample data file is present"""
    logger.info("\n🔍 Verifying sample data file...")
    
    sample_data_path = Path("resources/data/sample_data.txt")
    
    if not sample_data_path.exists():
        logger.error("❌ Sample data file not found: resources/data/sample_data.txt")
        return False
    else:
        logger.info("✅ Sample data file found: resources/data/sample_data.txt")
    
    # Check file size
    file_size = sample_data_path.stat().st_size
    logger.info(f"✅ Sample data file size: {file_size} bytes")
    
    return True


def verify_build_scripts():
    """Verify build scripts are present and include config"""
    logger.info("\n🔍 Verifying build scripts...")
    
    build_scripts = [
        "scripts/build_macos_app.py",
        "scripts/build_windows_exe.py",
        "scripts/build_linux_app.py"
    ]
    
    for script in build_scripts:
        if not os.path.exists(script):
            logger.error(f"❌ Build script not found: {script}")
            return False
        else:
            logger.info(f"✅ Build script found: {script}")
        
        # Check if script includes config.json reference
        try:
            with open(script, 'r') as f:
                content = f.read()
            if 'config.json' in content:
                logger.info(f"  ✅ {script} includes config.json")
            else:
                logger.error(f"  ❌ {script} does not include config.json")
                return False
        except Exception as e:
            logger.error(f"  ❌ Error reading {script}: {e}")
            return False
    
    return True


def verify_package_structure():
    """Verify package structure is correct"""
    logger.info("\n🔍 Verifying package structure...")
    
    required_paths = [
        "src/helpmesign/__init__.py",
        "src/helpmesign/core/__init__.py",
        "src/helpmesign/ui/__init__.py",
        "src/helpmesign/utils/__init__.py",
        "src/helpmesign/core/app.py",
        "src/helpmesign/core/startup.py",
        "src/helpmesign/ui/components.py",
        "src/helpmesign/ui/settings_dialog.py",
        "src/helpmesign/utils/logger.py",
        "src/helpmesign/utils/resource_manager.py",
        "src/helpmesign/utils/font_manager.py",
        "main.py",
        "run_app.py",
        "README.md",
        "requirements.txt"
    ]
    
    for path in required_paths:
        if os.path.exists(path):
            logger.info(f"✅ {path}")
        else:
            logger.error(f"❌ {path}")
            return False
    
    return True


def main():
    """Main verification process"""
    logger.info("🧪 HelpMeSign Bundle Verification")
    logger.info("=" * 40)
    
    passed = 0
    total = 0
    
    # Verify configuration files
    total += 1
    if verify_config_files():
        passed += 1
    
    # Verify sample data
    total += 1
    if verify_sample_data():
        passed += 1
    
    # Verify build scripts
    total += 1
    if verify_build_scripts():
        passed += 1
    
    # Verify package structure
    total += 1
    if verify_package_structure():
        passed += 1
    
    logger.info()
    
    logger.info(f"📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("🎉 All checks passed! Bundle is ready for distribution.")
        return True
    else:
        logger.error("⚠️  Some checks failed. Please fix the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 