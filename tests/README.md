# HelpMeSign Test Suite

This directory contains the comprehensive test suite for the HelpMeSign application, organized by test type and functionality.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Pytest configuration and shared fixtures
├── README.md                      # This file
├── unit/                          # Unit tests (isolated components)
│   ├── __init__.py
│   ├── core/                      # Core application tests
│   │   ├── __init__.py
│   │   ├── test_app.py           # Main application class tests
│   │   ├── test_main_app.py      # Main app entry point tests
│   │   ├── test_startup.py       # Startup process tests
│   │   └── test_startup_legacy.py # Legacy startup tests
│   ├── modes/                     # Mode-related tests
│   │   ├── __init__.py
│   │   ├── test_base_mode.py     # Base mode functionality
│   │   ├── test_mode_manager.py  # Mode management tests
│   │   ├── learn/                # Learn mode tests
│   │   │   ├── __init__.py
│   │   │   └── test_learn_mode.py
│   │   └── sign_translate/       # Sign translate mode tests
│   │       ├── __init__.py
│   │       └── test_sign_translate_mode.py
│   ├── ui/                       # UI component tests
│   │   ├── __init__.py
│   │   ├── test_components.py    # UI components (StatusBar, etc.)
│   │   ├── test_debug_menu_shortcuts.py
│   │   ├── test_keyboard_shortcuts.py
│   │   ├── test_os_shortcuts.py
│   │   ├── test_segmented_control.py
│   │   └── test_settings_dialog.py
│   ├── utils/                    # Utility tests
│   │   ├── __init__.py
│   │   ├── test_font_manager.py
│   │   ├── test_language_manager.py
│   │   ├── test_logger.py
│   │   ├── test_resource_manager.py
│   │   ├── test_system_monitor.py
│   │   └── test_theme_manager.py
│   └── config/                   # Configuration tests
│       ├── __init__.py
│       ├── test_config.py
│       ├── test_config_infinite_loop.py
│       ├── test_config_infinite_loop_mock.py
│       └── test_setup.py
├── integration/                   # Integration tests
│   ├── __init__.py
│   ├── simple_startup_test.py
│   ├── test_app_integration.py
│   ├── test_app_settings_integration.py
│   ├── test_language_integration_simple.py
│   ├── test_mode_system_integration.py
│   ├── test_settings_dialog_integration.py
│   ├── test_startup_integration.py
│   └── test_status_bar_system_monitor_integration.py
├── mocks/                        # Mock tests and scenarios
│   ├── __init__.py
│   ├── test_mock_scenarios.py
│   ├── test_mode_system_mocks.py
│   └── test_startup_mocks.py
└── fixtures/                     # Test fixtures and data
    ├── __init__.py
    └── test_data/                # Test data files
```

## Test Categories

### Unit Tests (`tests/unit/`)
- **Core**: Tests for the main application class and startup processes
- **Modes**: Tests for different application modes (Learn, Sign & Translate)
- **UI**: Tests for user interface components and interactions
- **Utils**: Tests for utility functions and helper classes
- **Config**: Tests for configuration management and setup

### Integration Tests (`tests/integration/`)
- End-to-end tests that verify multiple components work together
- Tests for complete workflows and user scenarios
- System-level integration testing

### Mock Tests (`tests/mocks/`)
- Tests that use mocked dependencies
- Scenario-based testing with controlled environments
- Tests for error conditions and edge cases

### Fixtures (`tests/fixtures/`)
- Shared test data and fixtures
- Configuration files for testing
- Sample data for various test scenarios

## Running Tests

### Run All Tests
```bash
make test
# or
python -m pytest
```

### Run Specific Test Categories
```bash
# Unit tests only
python -m pytest tests/unit/

# Integration tests only
python -m pytest tests/integration/

# Core tests only
python -m pytest tests/unit/core/

# UI tests only
python -m pytest tests/unit/ui/
```

### Run Specific Test Files
```bash
# Run a specific test file
python -m pytest tests/unit/core/test_app.py

# Run with verbose output
python -m pytest tests/unit/core/test_app.py -v
```

### Run Tests with Coverage
```bash
# Run with coverage report
python -m pytest --cov=src/helpmesign

# Generate HTML coverage report
python -m pytest --cov=src/helpmesign --cov-report=html
```

## Test Naming Conventions

- **Unit tests**: `test_<module_name>.py`
- **Integration tests**: `test_<feature>_integration.py`
- **Mock tests**: `test_<feature>_mocks.py`
- **Test methods**: `test_<description>`

## Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Descriptive names**: Test names should clearly describe what they're testing
3. **Mocking**: Use mocks for external dependencies and GUI components
4. **Coverage**: Aim for high test coverage, especially for critical paths
5. **Documentation**: Include docstrings explaining test purpose and setup

## Adding New Tests

When adding new tests:

1. **Choose the right category**: Place tests in the appropriate subdirectory
2. **Follow naming conventions**: Use consistent naming patterns
3. **Update this README**: Document new test categories or patterns
4. **Run existing tests**: Ensure new tests don't break existing functionality

## Continuous Integration

Tests are automatically run in CI/CD pipelines:
- GitHub Actions runs the full test suite on every commit
- Coverage reports are generated and tracked
- Test results are reported in pull requests 