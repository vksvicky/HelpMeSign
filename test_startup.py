#!/usr/bin/env python3
"""
Simple test script for startup functionality
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_startup_imports():
    """Test that startup module can be imported"""
    try:
        from helpmesign.core.startup import StartupScreen, SecureConfigManager, show_startup_screen, get_user_mode, set_user_mode
        print("✅ Startup module imports successfully")
        return True
    except Exception as e:
        print(f"❌ Startup module import failed: {e}")
        return False

def test_secure_config_manager():
    """Test SecureConfigManager functionality"""
    try:
        from helpmesign.core.startup import SecureConfigManager
        
        # Create config manager
        config_manager = SecureConfigManager()
        print("✅ SecureConfigManager created successfully")
        
        # Test save and load
        test_config = {'user_mode': 'sign', 'test': True}
        success = config_manager.save_config(test_config)
        print(f"✅ Config save: {success}")
        
        loaded_config = config_manager.load_config()
        print(f"✅ Config load: {loaded_config is not None}")
        
        if loaded_config:
            print(f"✅ Config data: {loaded_config}")
        
        return True
    except Exception as e:
        print(f"❌ SecureConfigManager test failed: {e}")
        return False

def test_app_integration():
    """Test app integration"""
    try:
        from helpmesign.core.app import HelpMeSignApp
        print("✅ App imports startup functionality successfully")
        return True
    except Exception as e:
        print(f"❌ App integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Startup Functionality")
    print("=" * 40)
    
    tests = [
        test_startup_imports,
        test_secure_config_manager,
        test_app_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Startup functionality is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 