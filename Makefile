# HelpMeSign Development Makefile

.PHONY: help check format install-hooks test test-coverage run clean

# Virtual environment detection and activation
VENV_PATH := venv
PYTHON := python3
VENV_PYTHON := $(VENV_PATH)/bin/python
VENV_PIP := $(VENV_PATH)/bin/pip

# Check if we're in a virtual environment
define check_venv
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		if [ -d "$(VENV_PATH)" ]; then \
			echo "🔧 Activating virtual environment..."; \
			. $(VENV_PATH)/bin/activate; \
		else \
			echo "❌ Virtual environment not found. Please run 'make setup' first."; \
			exit 1; \
		fi; \
	fi
endef

# Default target
help:
	@echo "HelpMeSign Development Commands:"
	@echo ""
	@echo "Code Quality:"
	@echo "  check      - Run quick code quality checks (black, isort, mypy, flake8)"
	@echo "  format     - Run full checks with auto-fixing"
	@echo "  install-hooks - Install git hooks for automatic checks"
	@echo ""
	@echo "Development:"
	@echo "  run        - Run the application in development mode"
	@echo "  test       - Run all tests"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  clean      - Clean up temporary files"
	@echo ""
	@echo "Setup:"
	@echo "  setup      - Setup development environment"
	@echo "  install    - Install dependencies"
	@echo ""

# Code quality checks
check:
	@echo "🔍 Running quick code quality checks..."
	$(check_venv)
	@$(VENV_PYTHON) scripts/quick_check.py

format:
	@echo "🔧 Running full code quality checks with auto-fixing..."
	$(check_venv)
	@$(VENV_PYTHON) scripts/pre_commit_check.py

install-hooks:
	@echo "🔧 Installing git hooks..."
	$(check_venv)
	@$(VENV_PYTHON) scripts/install_git_hooks.py

# Development commands
run:
	@echo "🚀 Starting HelpMeSign application..."
	$(check_venv)
	@$(VENV_PYTHON) run_app.py --env dev --debug

test:
	@echo "🧪 Running tests..."
	$(check_venv)
	@$(VENV_PYTHON) -m pytest tests/ -v

test-coverage:
	@echo "🧪 Running tests with coverage report..."
	$(check_venv)
	@$(VENV_PYTHON) -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml
	@echo ""
	@echo "📊 Coverage report generated:"
	@echo "  - HTML: htmlcov/index.html"
	@echo "  - XML: coverage.xml"
	@echo "  - Terminal: See above output"

test-coverage-quick:
	@echo "🧪 Running tests with quick coverage report..."
	$(check_venv)
	@$(VENV_PYTHON) -m pytest tests/ --cov=src --cov-report=term-missing

clean:
	@echo "🧹 Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name "htmlcov" -exec rm -rf {} +
	@find . -type f -name "coverage.xml" -delete
	@find . -type f -name ".coverage" -delete
	@echo "✅ Cleanup complete"

# CI/CD commands
ci-check:
	@echo "🔍 Running CI checks..."
	$(check_venv)
	@$(VENV_PYTHON) test_ci_import.py
	@$(VENV_PYTHON) scripts/quick_check.py

# Build commands (placeholder for future)
build:
	@echo "🔨 Building application..."
	@echo "Build commands will be implemented here"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	@if [ ! -d "$(VENV_PATH)" ]; then \
		echo "🔧 Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV_PATH); \
	fi
	@echo "📦 Installing packages..."
	@$(VENV_PIP) install -r requirements.txt
	@$(VENV_PIP) install black isort mypy flake8 pytest pytest-cov
	@echo "✅ Dependencies installed"

# Setup development environment
setup: install install-hooks
	@echo "🎉 Development environment setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  make run    - Start the application"
	@echo "  make check  - Run code quality checks"
	@echo "  make test   - Run tests"
	@echo "  make test-coverage - Run tests with coverage report" 