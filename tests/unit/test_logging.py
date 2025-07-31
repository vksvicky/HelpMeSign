#!/usr/bin/env python3
"""
Simple test for logging functionality
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_logging():
    """Test the logging functionality"""
    print("🧪 Testing logging functionality...")
    
    try:
        from helpmesign.utils.logger import setup_logging, get_logger, set_log_level
        
        # Test config
        config = {
            'logging': {
                'level': 'DEBUG',
                'file_enabled': True,
                'console_enabled': True
            }
        }
        
        # Set up logging
        logger = setup_logging(config)
        print("✅ Logging setup completed")
        
        # Test different log levels
        logger.debug("This is a debug message")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        
        print("✅ All log levels tested")
        
        # Test changing log level
        set_log_level("INFO")
        logger.debug("This debug message should not appear")
        logger.info("This info message should appear")
        
        print("✅ Log level change tested")
        
        # Test getting logger
        test_logger = get_logger("test.module")
        test_logger.info("Test logger working")
        
        print("✅ Logger retrieval tested")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_logging() 