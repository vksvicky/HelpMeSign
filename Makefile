# HelpMeSign Development Makefile

.PHONY: help check format install-hooks test run clean

# Default target
help:
	@echo "HelpMeSign Development Commands:"
	@echo ""
	@echo "Code Quality:"
	@echo "  check      - Run quick code quality checks (black, isort, mypy)"
	@echo "  format     - Run full checks with auto-fixing"
	@echo "  install-hooks - Install git hooks for automatic checks"
	@echo ""
	@echo "Development:"
	@echo "  run        - Run the application in development mode"
	@echo "  test       - Run all tests"
	@echo "  clean      - Clean up temporary files"
	@echo ""

# Code quality checks
check:
	@echo "🔍 Running quick code quality checks..."
	@python3 scripts/quick_check.py

format:
	@echo "🔧 Running full code quality checks with auto-fixing..."
	@python3 scripts/pre_commit_check.py

install-hooks:
	@echo "🔧 Installing git hooks..."
	@python3 scripts/install_git_hooks.py

# Development commands
run:
	@echo "🚀 Starting HelpMeSign application..."
	@python3 run_app.py --env dev --debug

test:
	@echo "🧪 Running tests..."
	@python3 -m pytest tests/ -v

clean:
	@echo "🧹 Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@echo "✅ Cleanup complete"

# CI/CD commands
ci-check:
	@echo "🔍 Running CI checks..."
	@python3 test_ci_import.py
	@python3 scripts/quick_check.py

# Build commands (placeholder for future)
build:
	@echo "🔨 Building application..."
	@echo "Build commands will be implemented here"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	@pip install -r requirements.txt
	@pip install black isort mypy pytest
	@echo "✅ Dependencies installed"

# Setup development environment
setup: install install-hooks
	@echo "🎉 Development environment setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  make run    - Start the application"
	@echo "  make check  - Run code quality checks"
	@echo "  make test   - Run tests" 