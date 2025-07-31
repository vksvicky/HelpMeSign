#!/usr/bin/env python3
"""
Test runner script for HelpMeSign
Provides comprehensive test execution with various options and coverage reporting
"""

import sys
import os
import argparse
import subprocess
import unittest
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def check_coverage_available():
    """Check if coverage module is available"""
    try:
        import coverage
        return True
    except ImportError:
        return False


def run_tests_with_coverage(test_pattern, output_format='term'):
    """Run tests with coverage reporting"""
    if not check_coverage_available():
        logger.warning("⚠️  Coverage module not available. Install with: pip install coverage")
        return False
    
    try:
        import coverage
        
        # Start coverage measurement with specific configuration
        cov = coverage.Coverage(
            source=['src'],
            omit=[
                '*/tests/*',
                '*/venv/*',
                '*/build/*',
                '*/dist/*',
                '*/__pycache__/*',
                '*/pyscript/*',
                '*/scripts/*',
                'setup.py',
                'main.py',
                'main_prod.py',
                'run_app.py',
                'run_tests.py',
                'build.py',
                'setup_macos.py'
            ]
        )
        cov.start()
        
        # Run tests
        loader = unittest.TestLoader()
        suite = loader.discover('tests', pattern=test_pattern)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Stop coverage and generate report
        cov.stop()
        cov.save()
        
        if output_format == 'html':
            cov.html_report(directory='htmlcov')
            logger.info(f"📊 HTML coverage report generated in htmlcov/")
        elif output_format == 'xml':
            cov.xml_report(outfile='coverage.xml')
            logger.info(f"📊 XML coverage report generated as coverage.xml")
        else:
            cov.report()
        
        return result.wasSuccessful()
        
    except Exception as e:
        logger.error(f"❌ Error running tests with coverage: {e}")
        return False


def run_tests_without_coverage(test_pattern, verbose=False):
    """Run tests without coverage reporting"""
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern=test_pattern)
    
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(
        description="HelpMeSign Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run_tests.py                    # Run all tests
  python3 run_tests.py --unit             # Run only unit tests
  python3 run_tests.py --integration      # Run only integration tests
  python3 run_tests.py --mocks            # Run only mock tests
  python3 run_tests.py --coverage         # Run with coverage report
  python3 run_tests.py --coverage html    # Generate HTML coverage report
  python3 run_tests.py --verbose          # Verbose output
  python3 run_tests.py --quick            # Quick test run
        """
    )
    
    parser.add_argument(
        '--unit',
        action='store_true',
        help='Run only unit tests'
    )
    
    parser.add_argument(
        '--integration',
        action='store_true',
        help='Run only integration tests'
    )
    
    parser.add_argument(
        '--mocks',
        action='store_true',
        help='Run only mock tests'
    )
    
    parser.add_argument(
        '--coverage',
        nargs='?',
        const='term',
        choices=['term', 'html', 'xml'],
        help='Run tests with coverage reporting (term, html, or xml)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Quick test run (skip slow tests)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='HelpMeSign Test Runner 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Determine test pattern based on arguments
    if args.unit:
        test_pattern = 'test_*.py'
        test_category = 'unit'
    elif args.integration:
        test_pattern = 'test_*.py'
        test_category = 'integration'
    elif args.mocks:
        test_pattern = 'test_*.py'
        test_category = 'mocks'
    else:
        test_pattern = 'test_*.py'
        test_category = 'all'
    
    logger.info(f"🧪 Running HelpMeSign Tests ({test_category})")
    logger.info("=" * 50)
    
    # Check if tests directory exists
    if not os.path.exists('tests'):
        logger.error("❌ Tests directory not found")
        sys.exit(1)
    
    # Run tests
    success = False
    
    if args.coverage:
        logger.info(f"📊 Running tests with {args.coverage} coverage reporting...")
        success = run_tests_with_coverage(test_pattern, args.coverage)
    else:
        logger.info("🔍 Running tests...")
        success = run_tests_without_coverage(test_pattern, args.verbose)
    
    # Print summary
    logger.info("=" * 50)
    if success:
        logger.info("✅ All tests passed!")
    else:
        logger.error("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 