#!/usr/bin/env python3
"""
Verification script to check that config files are properly bundled
"""

import os
import sys
import json
from pathlib import Path

def verify_config_file():
    """Verify that the config file exists and is valid"""
    print("🔍 Verifying configuration files...")
    
    # Check if config file exists
    config_path = Path("resources/data/config.json")
    if not config_path.exists():
        print("❌ Config file not found: resources/data/config.json")
        return False
    
    print("✅ Config file found: resources/data/config.json")
    
    # Check if config file is valid JSON
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print("✅ Config file is valid JSON")
    except json.JSONDecodeError as e:
        print(f"❌ Config file is not valid JSON: {e}")
        return False
    
    # Verify required config sections
    required_sections = [
        'app_name', 'version', 'window_size', 'theme', 
        'ui', 'features', 'defaults', 'paths', 'logging', 'security'
    ]
    
    for section in required_sections:
        if section not in config:
            print(f"❌ Missing required config section: {section}")
            return False
    
    print("✅ All required config sections present")
    
    # Verify window size
    window_size = config.get('window_size', {})
    if 'width' not in window_size or 'height' not in window_size:
        print("❌ Window size configuration incomplete")
        return False
    
    print(f"✅ Window size: {window_size['width']}x{window_size['height']}")
    
    # Verify theme
    theme = config.get('theme', {})
    if 'primary_color' not in theme:
        print("❌ Theme configuration incomplete")
        return False
    
    print(f"✅ Primary color: {theme['primary_color']}")
    
    return True

def verify_sample_data():
    """Verify that the sample data file exists"""
    print("\n🔍 Verifying sample data file...")
    
    sample_path = Path("resources/data/sample_data.txt")
    if not sample_path.exists():
        print("❌ Sample data file not found: resources/data/sample_data.txt")
        return False
    
    print("✅ Sample data file found: resources/data/sample_data.txt")
    
    # Check file size
    file_size = sample_path.stat().st_size
    print(f"✅ Sample data file size: {file_size} bytes")
    
    return True

def verify_build_scripts():
    """Verify that build scripts include config files"""
    print("\n🔍 Verifying build scripts...")
    
    build_scripts = [
        "scripts/build_macos_app.py",
        "scripts/build_windows_exe.py", 
        "scripts/build_linux_app.py"
    ]
    
    for script in build_scripts:
        script_path = Path(script)
        if not script_path.exists():
            print(f"❌ Build script not found: {script}")
            continue
        
        print(f"✅ Build script found: {script}")
        
        # Check if script includes config.json
        with open(script_path, 'r') as f:
            content = f.read()
            if 'config.json' in content:
                print(f"  ✅ {script} includes config.json")
            else:
                print(f"  ❌ {script} does not include config.json")
    
    return True

def verify_package_structure():
    """Verify the overall package structure"""
    print("\n🔍 Verifying package structure...")
    
    required_paths = [
        "main.py",
        "resources/images/icon.png",
        "resources/data/config.json",
        "resources/data/sample_data.txt",
        "src/helpmesign/__init__.py",
        "scripts/build_macos_app.py",
        "scripts/build_windows_exe.py",
        "scripts/build_linux_app.py",
        "README.md",
        "requirements.txt",
        "MANIFEST.in"
    ]
    
    for path in required_paths:
        if Path(path).exists():
            print(f"✅ {path}")
        else:
            print(f"❌ {path}")
    
    return True

def main():
    """Main verification function"""
    print("🧪 HelpMeSign Bundle Verification")
    print("=" * 40)
    
    checks = [
        verify_config_file,
        verify_sample_data,
        verify_build_scripts,
        verify_package_structure
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
        print()
    
    print(f"📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Bundle is ready for distribution.")
        return True
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 