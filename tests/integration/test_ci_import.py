#!/usr/bin/env python3
"""
CI-safe import test for HelpMeSign
Tests the conditional import functionality without requiring GUI libraries
"""

import os
import sys

# Add src to path
test_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(test_dir))
src_path = os.path.join(project_root, "src")
sys.path.insert(0, src_path)


def test_safe_import():
    """Test the safe import functionality"""
    try:
        # Test the safe import pattern
        from helpmesign import get_app

        # Try to get the app class
        app_class = get_app()

        # Verify that get_app returns either None (no PySide6) or a class
        if app_class is None:
            print(
                "[OK] Safe import working correctly - PySide6 not available (expected in CI)"
            )
            # Verify that the function returns None when PySide6 is not available
            assert app_class is None, "Expected None when PySide6 not available"
        else:
            print("[OK] Safe import working correctly - PySide6 available")
            # Verify that the function returns a callable class when PySide6 is available
            assert callable(app_class), "Expected callable class when PySide6 available"
            assert hasattr(app_class, '__name__'), "Expected class to have __name__ attribute"

        # Verify the import was successful
        assert hasattr(get_app, '__call__'), "get_app should be callable"

    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        assert False, f"Import error: {e}"
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        assert False, f"Unexpected error: {e}"


def test_utility_imports():
    """Test that utility modules can be imported safely"""
    try:
        # Test utility imports that don't require PySide6
        from helpmesign.utils.language_manager import get_dict, get_list, get_text
        from helpmesign.utils.logger import get_logger
        from helpmesign.utils.resource_manager import ResourceManager

        # Verify that the imported functions/classes are callable
        assert callable(get_dict), "get_dict should be callable"
        assert callable(get_list), "get_list should be callable"
        assert callable(get_text), "get_text should be callable"
        assert callable(get_logger), "get_logger should be callable"
        assert callable(ResourceManager), "ResourceManager should be callable"

        # Test basic functionality
        logger = get_logger("test")
        assert logger is not None, "Logger should not be None"
        assert hasattr(logger, 'info'), "Logger should have info method"

        # Test ResourceManager instantiation
        rm = ResourceManager()
        assert rm is not None, "ResourceManager should not be None"
        assert hasattr(rm, 'get_data_path'), "ResourceManager should have get_data_path method"

        print("[OK] Utility modules import successfully and work correctly")

    except ImportError as e:
        print(f"[ERROR] Utility import error: {e}")
        assert False, f"Utility import error: {e}"
    except Exception as e:
        print(f"[ERROR] Unexpected utility error: {e}")
        assert False, f"Unexpected utility error: {e}"


def main():
    """Main test function"""
    print("[INFO] Testing HelpMeSign CI-safe imports...")
    print("=" * 50)

    utility_ok = True
    app_ok = True

    # Test utility imports first
    try:
        test_utility_imports()
        print("[OK] Utility imports test passed!")
    except Exception as e:
        print(f"[ERROR] Utility imports test failed: {e}")
        utility_ok = False

    # Test safe app import
    try:
        test_safe_import()
        print("[OK] Safe import test passed!")
    except Exception as e:
        print(f"[ERROR] Safe import test failed: {e}")
        app_ok = False

    print("=" * 50)
    if utility_ok and app_ok:
        print("[OK] All CI import tests passed!")
        sys.exit(0)
    else:
        print("[ERROR] Some CI import tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
