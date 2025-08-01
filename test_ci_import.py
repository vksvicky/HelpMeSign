#!/usr/bin/env python3
"""
CI-safe import test for HelpMeSign
Tests the conditional import functionality without requiring GUI libraries
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_safe_import():
    """Test the safe import functionality"""
    try:
        # Test the safe import pattern
        from helpmesign import get_app
        
        # Try to get the app class
        app_class = get_app()
        
        if app_class is None:
            print("✅ Safe import working correctly - PySide6 not available (expected in CI)")
            return True
        else:
            print("✅ Safe import working correctly - PySide6 available")
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_utility_imports():
    """Test that utility modules can be imported safely"""
    try:
        # Test utility imports that don't require PySide6
        from helpmesign.utils.language_manager import get_text, get_list, get_dict
        from helpmesign.utils.logger import get_logger
        from helpmesign.utils.resource_manager import ResourceManager
        
        print("✅ Utility modules import successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Utility import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected utility error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing HelpMeSign CI-safe imports...")
    print("=" * 50)
    
    # Test utility imports first
    utility_ok = test_utility_imports()
    
    # Test safe app import
    app_ok = test_safe_import()
    
    print("=" * 50)
    if utility_ok and app_ok:
        print("✅ All CI import tests passed!")
        sys.exit(0)
    else:
        print("❌ Some CI import tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 