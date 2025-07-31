# HelpMeSign

A simple python3 GUI application built with tkinter.

## Features

- Fixed 1024x1024 window size (configurable)
- Custom app icon (icon.png)
- Text input and processing
- Output display with scrollbar
- Status bar
- Keyboard shortcuts (Enter to process)
- Resource management system

## Requirements

- python3 3.x (tkinter comes built-in)

## Running the Application

### Using the Application Runner Script (Recommended)
```bash
# Run normally
python3 run_app.py

# Run in debug mode
python3 run_app.py --debug

# Run with custom config
python3 run_app.py --config custom_config.json

# Get help
python3 run_app.py --help
```

### Alternative Methods
```bash
# Run from root directory
python3 main.py

# Or install and run as package
pip install -e .
helpmesign

# Or run directly from source
python3 -m helpmesign.core.app
```

## Usage

1. Enter text in the input field
2. Press Enter or click "Process" to process the text
3. View the output in the text area below
4. Use "Clear" to reset the application

## Project Structure

```
HelpMeSign/
├── src/
│   └── helpmesign/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   └── app.py              # Main application logic
│       ├── ui/
│       │   ├── __init__.py
│       │   └── components.py       # UI components
│       ├── utils/
│       │   ├── __init__.py
│       │   └── resource_manager.py # Resource management
│       └── services/
│           └── __init__.py         # Future services
├── scripts/                        # Build scripts
│   ├── __init__.py
│   ├── README.md                   # Scripts documentation
│   ├── build_macos_app.py          # macOS app bundle builder
│   ├── build_windows_exe.py        # Windows executable builder
│   └── build_all.py                # Universal build script
├── resources/                      # Application resources
│   ├── images/                     # Image files (icons, etc.)
│   └── data/                       # Data files (config, sample data, etc.)
├── tests/                          # Test suite
├── main.py                         # Application entry point
├── run_app.py                      # Application runner script
├── run_tests.py                    # Test runner script
├── build.py                        # Convenience build script
├── setup.py                        # Package setup
├── requirements.txt                # Dependencies
└── README.md                       # This file
```

### Key Components

- **`src/helpmesign/`** - Main package directory
- **`core/`** - Core application logic and business rules
- **`ui/`** - User interface components and layouts
- **`utils/`** - Utility functions and helper classes
- **`services/`** - External service integrations (future)

## Configuration

The application uses `resources/data/config.json` for configuration settings including:
- Window size
- Theme colors
- Application settings

## Testing

The project includes a comprehensive test suite with the following test categories:

### Test Structure
- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests for component interaction
- `tests/mocks/` - Mock-based tests for various scenarios

### Running Tests

#### Using the Test Runner Script (Recommended)
```bash
# Run all tests
python3 run_tests.py

# Run specific test categories
python3 run_tests.py --unit
python3 run_tests.py --integration
python3 run_tests.py --mocks

# Run quick test subset for development
python3 run_tests.py --quick

# Run with coverage report
python3 run_tests.py --coverage

# Verbose output with detailed test information
python3 run_tests.py --verbose

# Clear terminal and run tests with verbose output (Development workflow)
clear && python3 run_tests.py --verbose

# Get help
python3 run_tests.py --help
```

#### Alternative Method
```bash
# Run all tests with coverage
python3 tests/test_runner.py

# Run specific test categories
python3 tests/test_runner.py unit
python3 tests/test_runner.py integration
python3 tests/test_runner.py mocks

# Run quick test subset
python3 tests/test_runner.py quick

# Get help
python3 tests/test_runner.py help
```

### Test Coverage

The test suite covers:
- **Happy Path**: Normal operation scenarios
- **Error Handling**: Exception and error conditions
- **Boundary Cases**: Edge cases and limits
- **Negative Cases**: Invalid inputs and failure scenarios
- **Mock Scenarios**: Various mocked external dependencies

### Development Workflow

For active development, use the following command to get a clean terminal and detailed test output:

```bash
clear && python3 run_tests.py --verbose
```

This command:
- **`clear`** - Clears the terminal for better readability
- **`&&`** - Only runs tests if clear command succeeds
- **`--verbose`** - Provides detailed output including test names, execution time, and any failures

This is particularly useful when:
- Debugging test failures
- Monitoring test execution progress
- Ensuring clean test output in CI/CD environments
- Getting comprehensive feedback during development iterations

## Building Executables

### macOS App Bundle

To create a native macOS `.app` bundle:

```bash
# Install build dependencies
pip3 install py2app

# Build the app
python3 scripts/build_macos_app.py
```

This will create:
- `dist/HelpMeSign.app` - Native macOS application bundle
- `HelpMeSign.dmg` - Optional DMG installer (if create-dmg is available)

### Windows 64-bit Executable

To create a Windows 64-bit executable:

```bash
# Install build dependencies
pip3 install pyinstaller pefile

# Build the executable
python3 scripts/build_windows_exe.py
```

This will create:
- `dist/HelpMeSign.exe` - 64-bit Windows executable
- `HelpMeSign-Setup.exe` - Optional NSIS installer (if NSIS is available)

### Universal Build

To build for the current platform automatically:

```bash
# Using the convenience script (recommended)
python3 build.py

# Or directly from scripts folder
python3 scripts/build_all.py
```

### Build Requirements

#### macOS
- Python 3.8+
- py2app
- create-dmg (optional, for DMG creation)

#### Windows
- Python 3.8+
- PyInstaller
- pefile (for executable analysis)
- NSIS (optional, for installer creation)

### Build Output

After building, you'll find the executables in the `dist/` directory:

```
dist/
├── HelpMeSign.app/          # macOS app bundle
├── HelpMeSign.exe          # Windows executable
├── HelpMeSign.dmg          # macOS DMG installer (optional)
└── HelpMeSign-Setup.exe    # Windows NSIS installer (optional)
```

### Test Dependencies

```bash
pip install coverage
``` 