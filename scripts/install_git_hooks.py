#!/usr/bin/env python3
"""
Install git hooks for HelpMeSign
Sets up pre-commit hooks to run code quality checks
"""

import os
import shutil
import sys
from pathlib import Path


def install_pre_commit_hook():
    """Install the pre-commit git hook"""
    # Get the git hooks directory
    git_dir = Path(".git")
    if not git_dir.exists():
        print("❌ Error: Not a git repository")
        print("   Run 'git init' first")
        return False
    
    hooks_dir = git_dir / "hooks"
    pre_commit_hook = hooks_dir / "pre-commit"
    
    # Create hooks directory if it doesn't exist
    hooks_dir.mkdir(exist_ok=True)
    
    # Get the path to our quick check script
    script_path = Path(__file__).parent / "quick_check.py"
    
    # Create the pre-commit hook content
    hook_content = f"""#!/bin/sh
# HelpMeSign pre-commit hook
# Runs code quality checks before commit

echo "🔍 Running pre-commit checks..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

# Run the quick check script
python3 "{script_path.absolute()}"

# Exit with the script's exit code
exit $?
"""
    
    # Write the hook file
    try:
        with open(pre_commit_hook, 'w') as f:
            f.write(hook_content)
        
        # Make it executable
        os.chmod(pre_commit_hook, 0o755)
        
        print(f"✅ Pre-commit hook installed: {pre_commit_hook}")
        return True
        
    except Exception as e:
        print(f"❌ Error installing pre-commit hook: {e}")
        return False


def install_commit_msg_hook():
    """Install a commit-msg hook for better commit messages"""
    git_dir = Path(".git")
    hooks_dir = git_dir / "hooks"
    commit_msg_hook = hooks_dir / "commit-msg"
    
    # Create hooks directory if it doesn't exist
    hooks_dir.mkdir(exist_ok=True)
    
    # Create a simple commit message hook
    hook_content = """#!/bin/sh
# HelpMeSign commit-msg hook
# Validates commit message format

# Get the commit message
commit_msg=$(cat "$1")

# Check if message is not empty
if [ -z "$commit_msg" ]; then
    echo "❌ Error: Commit message cannot be empty"
    exit 1
fi

# Check if message is too short
if [ ${#commit_msg} -lt 10 ]; then
    echo "❌ Error: Commit message too short (minimum 10 characters)"
    echo "   Current message: '$commit_msg'"
    exit 1
fi

# Check if message starts with a capital letter
if ! echo "$commit_msg" | grep -q '^[A-Z]'; then
    echo "❌ Error: Commit message should start with a capital letter"
    echo "   Current message: '$commit_msg'"
    exit 1
fi

echo "✅ Commit message looks good!"
exit 0
"""
    
    try:
        with open(commit_msg_hook, 'w') as f:
            f.write(hook_content)
        
        # Make it executable
        os.chmod(commit_msg_hook, 0o755)
        
        print(f"✅ Commit-msg hook installed: {commit_msg_hook}")
        return True
        
    except Exception as e:
        print(f"❌ Error installing commit-msg hook: {e}")
        return False


def main():
    """Install git hooks"""
    print("🔧 Installing HelpMeSign Git Hooks")
    print("="*50)
    
    # Check if we're in the right directory
    if not Path("src/helpmesign").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   Expected to find: src/helpmesign/")
        sys.exit(1)
    
    success = True
    
    # Install pre-commit hook
    if install_pre_commit_hook():
        print("✅ Pre-commit hook installed successfully")
    else:
        print("❌ Failed to install pre-commit hook")
        success = False
    
    # Install commit-msg hook
    if install_commit_msg_hook():
        print("✅ Commit-msg hook installed successfully")
    else:
        print("❌ Failed to install commit-msg hook")
        success = False
    
    print("\n" + "="*50)
    if success:
        print("🎉 All git hooks installed successfully!")
        print("\n📋 What happens now:")
        print("   • Pre-commit hook will run black, isort, and mypy checks")
        print("   • Commit-msg hook will validate commit message format")
        print("   • Commits will be blocked if checks fail")
        print("\n💡 To run checks manually:")
        print("   • Full check with auto-fix: python scripts/pre_commit_check.py")
        print("   • Quick check only: python scripts/quick_check.py")
    else:
        print("❌ Some hooks failed to install")
        sys.exit(1)


if __name__ == "__main__":
    main() 