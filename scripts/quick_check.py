#!/usr/bin/env python3
"""
Quick pre-commit check for HelpMeSign
Fast checks without auto-fixing - for git hooks
"""

import subprocess
import sys
from pathlib import Path


def run_check(command: list, name: str) -> bool:
    """Run a check command and return success status"""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0:
            print(f"✅ {name} passed")
            return True
        else:
            print(f"❌ {name} failed")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ {name} error: {e}")
        return False


def main():
    """Quick pre-commit checks"""
    print("🔍 Quick pre-commit checks...")
    
    # Check if we're in the right directory
    if not Path("src/helpmesign").exists():
        print("❌ Error: Run from project root")
        sys.exit(1)
    
    all_passed = True
    
    # Black check
    if not run_check([sys.executable, "-m", "black", "--check", "src/", "tests/"], "Black"):
        all_passed = False
    
    # isort check
    if not run_check([sys.executable, "-m", "isort", "--check-only", "src/", "tests/"], "isort"):
        all_passed = False
    
    # mypy check
    if not run_check([sys.executable, "-m", "mypy", "src/"], "mypy"):
        all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed!")
        sys.exit(0)
    else:
        print("\n❌ Some checks failed. Run 'python scripts/pre_commit_check.py' for fixes.")
        sys.exit(1)


if __name__ == "__main__":
    main() 