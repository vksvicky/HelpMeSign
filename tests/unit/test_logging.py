#!/usr/bin/env python3
"""
Simple test for logging functionality
"""

import sys
import os
import logging

# Configure logging for this test
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_logging():
    """Test the logging functionality"""
    logger.info("🧪 Testing logging functionality...")
    
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
        app_logger = setup_logging(config)
        logger.info("✅ Logging setup completed")
        
        # Test different log levels
        app_logger.debug("This is a debug message")
        app_logger.info("This is an info message")
        app_logger.warning("This is a warning message")
        app_logger.error("This is an error message")
        
        logger.info("✅ All log levels tested")
        
        # Test changing log level
        set_log_level("INFO")
        app_logger.debug("This debug message should not appear")
        app_logger.info("This info message should appear")
        
        logger.info("✅ Log level change tested")
        
        # Test getting logger
        test_logger = get_logger("test.module")
        test_logger.info("Test logger working")
        
        logger.info("✅ Logger retrieval tested")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_logging() 