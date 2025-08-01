#!/usr/bin/env python3
"""
Pre-commit script for HelpMeSign
Runs black, isort, and mypy checks to ensure code quality
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import List, Tuple


def run_command(command: List[str], description: str) -> Tuple[bool, str]:
    """Run a command and return success status and output"""
    print(f"\n{'='*60}")
    print(f"🔍 Running {description}...")
    print(f"Command: {' '.join(command)}")
    print('='*60)
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if result.stdout:
            print("✅ Output:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️  Warnings/Errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} passed!")
            return True, result.stdout
        else:
            print(f"❌ {description} failed with return code {result.returncode}")
            return False, result.stderr
            
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False, str(e)


def run_black_check() -> bool:
    """Run black formatting check"""
    success, _ = run_command(
        [sys.executable, "-m", "black", "--check", "src/", "tests/"],
        "Black formatting check"
    )
    return success


def run_black_format() -> bool:
    """Run black formatting (auto-fix)"""
    success, _ = run_command(
        [sys.executable, "-m", "black", "src/", "tests/"],
        "Black formatting (auto-fix)"
    )
    return success


def run_isort_check() -> bool:
    """Run isort import sorting check"""
    success, _ = run_command(
        [sys.executable, "-m", "isort", "--check-only", "src/", "tests/"],
        "isort import sorting check"
    )
    return success


def run_isort_format() -> bool:
    """Run isort import sorting (auto-fix)"""
    success, _ = run_command(
        [sys.executable, "-m", "isort", "src/", "tests/"],
        "isort import sorting (auto-fix)"
    )
    return success


def run_mypy_check() -> bool:
    """Run mypy type checking"""
    success, _ = run_command(
        [sys.executable, "-m", "mypy", "src/"],
        "mypy type checking"
    )
    return success


def install_dependencies() -> bool:
    """Install required dependencies if not present"""
    dependencies = ["black", "isort", "mypy"]
    
    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
        except ImportError:
            print(f"📦 Installing {dep}...")
            success, _ = run_command(
                [sys.executable, "-m", "pip", "install", dep],
                f"Installing {dep}"
            )
            if not success:
                print(f"❌ Failed to install {dep}")
                return False
    
    return True


def main():
    """Main pre-commit check function"""
    print("🚀 HelpMeSign Pre-commit Code Quality Check")
    print("="*60)
    
    # Check if we're in the right directory
    if not Path("src/helpmesign").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   Expected to find: src/helpmesign/")
        sys.exit(1)
    
    # Install dependencies if needed
    if not install_dependencies():
        print("❌ Failed to install required dependencies")
        sys.exit(1)
    
    # Track overall success
    all_passed = True
    fixes_applied = False
    
    # Run black check first
    black_passed = run_black_check()
    if not black_passed:
        print("\n🔄 Black formatting issues found. Attempting auto-fix...")
        if run_black_format():
            print("✅ Black auto-fix applied successfully")
            fixes_applied = True
            # Re-check after fix
            black_passed = run_black_check()
        else:
            print("❌ Black auto-fix failed")
            all_passed = False
    
    # Run isort check
    isort_passed = run_isort_check()
    if not isort_passed:
        print("\n🔄 isort import sorting issues found. Attempting auto-fix...")
        if run_isort_format():
            print("✅ isort auto-fix applied successfully")
            fixes_applied = True
            # Re-check after fix
            isort_passed = run_isort_check()
        else:
            print("❌ isort auto-fix failed")
            all_passed = False
    
    # Run mypy check
    mypy_passed = run_mypy_check()
    if not mypy_passed:
        all_passed = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 PRE-COMMIT CHECK SUMMARY")
    print("="*60)
    print(f"Black formatting:     {'✅ PASS' if black_passed else '❌ FAIL'}")
    print(f"isort import sorting: {'✅ PASS' if isort_passed else '❌ FAIL'}")
    print(f"mypy type checking:   {'✅ PASS' if mypy_passed else '❌ FAIL'}")
    
    if fixes_applied:
        print("\n🔄 Auto-fixes were applied. Please review the changes and commit them.")
    
    if all_passed:
        print("\n🎉 All checks passed! Ready to commit.")
        sys.exit(0)
    else:
        print("\n❌ Some checks failed. Please fix the issues before committing.")
        print("\n💡 Tips:")
        print("   - Run 'python scripts/pre_commit_check.py' to see detailed errors")
        print("   - Fix formatting issues manually if auto-fix didn't work")
        print("   - Address mypy type errors in your code")
        sys.exit(1)


if __name__ == "__main__":
    main() 