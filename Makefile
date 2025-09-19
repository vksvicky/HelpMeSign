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
	@echo "  run        - Run the application in development mode (with debug features)"
	@echo "  run-prod   - Run the application in production mode (clean UI)"
	@echo "  run-hand   - Run GLB Viewer with hot reload (requires entr)"
	@echo "  test       - Run all tests"
	@echo "  test-coverage - Run tests with coverage report (auto-detects PySide6)"
	@echo "  test-coverage-quick - Quick coverage report (auto-detects PySide6)"
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
	@echo "🚀 Starting HelpMeSign application (with debug mode)..."
	$(check_venv)
	@$(VENV_PYTHON) run_app.py --env dev --debug

run-prod:
	@echo "🚀 Starting HelpMeSign application (production mode)..."
	$(check_venv)
	@$(VENV_PYTHON) run_app.py --env prod

# run-editor:
# 	@echo "🖐️ Starting Hand Pose Editor independently (dual instance mode)..."
# 	$(check_venv)
# 	@PYTHONPATH=/Users/vivek/Development/HelpMeSign $(VENV_PYTHON) src/helpmesign/modes/learn/hand_pose_editor.py

run-hand:
	@echo "🖐️ Starting GLB Viewer with hot reload (entr)..."
	$(check_venv)
	@which entr > /dev/null || (echo "❌ entr not found. Please install with: brew install entr" && exit 1)
	@echo "glb_viewer.py" | entr -r $(VENV_PYTHON) glb_viewer.py

test:
	@echo "🧪 Running tests..."
	$(check_venv)
	@$(VENV_PYTHON) -m pytest tests/ -v

# Check if PySide6 is available
define check_pyside6
	@$(VENV_PYTHON) -c "import PySide6; print('PySide6 available')" 2>/dev/null || echo "PySide6 not available"
endef

test-coverage:
	@echo "🧪 Running tests with coverage report (detecting PySide6 availability)..."
	$(check_venv)
	@if $(VENV_PYTHON) -c "import PySide6" 2>/dev/null; then \
		echo "✅ PySide6 detected - Running comprehensive tests with Qt support..."; \
		$(VENV_PYTHON) -m pytest tests/ -v --cov=src --cov-branch --cov-context=test --cov-fail-under=0 --cov-report=term-missing --cov-report=html --cov-report=xml; \
	else \
		echo "⚠️  PySide6 not available - Running tests without Qt support..."; \
		$(VENV_PYTHON) -m pytest tests/ -v --cov=src --cov-branch --cov-context=test --cov-fail-under=0 --cov-report=term-missing --cov-report=html --cov-report=xml; \
	fi
	@echo ""
	@echo "📊 Coverage report generated:"
	@echo "  - HTML: htmlcov/index.html"
	@echo "  - XML: coverage.xml"
	@echo "  - Terminal: See above output"

test-coverage-quick:
	@echo "🧪 Running tests with quick coverage report (detecting PySide6 availability)..."
	$(check_venv)
	@if $(VENV_PYTHON) -c "import PySide6" 2>/dev/null; then \
		echo "✅ PySide6 detected - Running comprehensive tests with Qt support..."; \
		$(VENV_PYTHON) -m pytest tests/ --cov=src --cov-branch --cov-context=test --cov-fail-under=0 --cov-report=term-missing; \
	else \
		echo "⚠️  PySide6 not available - Running tests without Qt support..."; \
		$(VENV_PYTHON) -m pytest tests/ --cov=src --cov-branch --cov-context=test --cov-fail-under=0 --cov-report=term-missing; \
	fi

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