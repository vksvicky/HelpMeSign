#!/usr/bin/env python3
"""
Test runner script for HelpMeSign
Provides comprehensive test execution with various options and coverage reporting
"""

import sys
import os
import argparse
import subprocess
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


def check_pytest_available():
    """Check if pytest module is available"""
    try:
        import pytest
        return True
    except ImportError:
        return False


def check_coverage_available():
    """Check if coverage module is available"""
    try:
        import coverage
        return True
    except ImportError:
        return False


def run_tests_with_coverage(test_path, output_format='term'):
    """Run tests with coverage reporting using pytest"""
    if not check_pytest_available():
        logger.error("❌ pytest not available. Install with: pip install pytest")
        return False
    
    if not check_coverage_available():
        logger.warning("⚠️  Coverage module not available. Install with: pip install coverage")
        return False
    
    try:
        # Build pytest command with coverage
        cmd = [
            sys.executable, '-m', 'pytest',
            test_path,
            '--cov=src',
            '--cov-report=term-missing'
        ]
        
        if output_format == 'html':
            cmd.extend(['--cov-report=html:htmlcov'])
        elif output_format == 'xml':
            cmd.extend(['--cov-report=xml:coverage.xml'])
        
        # Run pytest with coverage
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if output_format == 'html':
            logger.info(f"📊 HTML coverage report generated in htmlcov/")
        elif output_format == 'xml':
            logger.info(f"📊 XML coverage report generated as coverage.xml")
        
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"❌ Error running tests with coverage: {e}")
        return False


def run_tests_without_coverage(test_path, verbose=False):
    """Run tests without coverage reporting using pytest"""
    if not check_pytest_available():
        logger.error("❌ pytest not available. Install with: pip install pytest")
        return False
    
    try:
        # Build pytest command
        cmd = [sys.executable, '-m', 'pytest', test_path]
        
        if verbose:
            cmd.append('-v')
        else:
            cmd.append('-q')
        
        # Run pytest
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"❌ Error running tests: {e}")
        return False


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
    
    # Determine test path based on arguments
    if args.unit:
        test_path = 'tests/unit'
        test_category = 'unit'
    elif args.integration:
        test_path = 'tests/integration'
        test_category = 'integration'
    elif args.mocks:
        test_path = 'tests/mocks'
        test_category = 'mocks'
    else:
        test_path = 'tests'
        test_category = 'all'
    
    logger.info(f"🧪 Running HelpMeSign Tests ({test_category})")
    logger.info("=" * 50)
    
    # Check if tests directory exists
    if not os.path.exists(test_path):
        logger.error(f"❌ Test directory '{test_path}' not found")
        sys.exit(1)
    
    # Run tests
    success = False
    
    if args.coverage:
        logger.info(f"📊 Running tests with {args.coverage} coverage reporting...")
        success = run_tests_with_coverage(test_path, args.coverage)
    else:
        logger.info("🔍 Running tests...")
        success = run_tests_without_coverage(test_path, args.verbose)
    
    # Print summary
    logger.info("=" * 50)
    if success:
        logger.info("✅ All tests passed!")
    else:
        logger.error("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 