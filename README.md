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

The application uses multiple configuration systems:

### Application Configuration
`resources/data/config.json` for application settings including:
- Window size
- Theme colors
- Application settings

### User Preferences (Secure)
`~/.helpmesign/user_config.secure` for secure user preferences:
- User mode selection (Sign/Learn)
- Last updated timestamp
- HMAC-protected data integrity

## Startup Screen

HelpMeSign features an innovative startup screen that allows users to choose their preferred mode:

### **Sign Mode** ✍️
- Document signing capabilities
- Digital signature workflows
- Contract management features

### **Learn Mode** 📚
- Educational content about digital signatures
- Best practices and tutorials
- Interactive learning modules

### **Key Features**
- **First-time Setup**: Automatic startup screen on first launch
- **Secure Storage**: HMAC-protected configuration files
- **Menu Integration**: Easy mode switching via application menu
- **Persistent Preferences**: Remembers user choice across sessions
- **Tamper Detection**: Prevents unauthorized configuration changes

### **Security Implementation**
- **HMAC Signatures**: Cryptographic data integrity verification
- **Restricted Permissions**: Owner-only file access (600)
- **Secure Key Management**: Automatic key generation and storage
- **Tamper Detection**: Immediate detection of configuration modifications

## Testing

The project includes a comprehensive test suite covering all scenarios with the following structure:

### Test Structure
- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests for component interaction
- `tests/mocks/` - Mock-based tests for various scenarios

### Test Coverage Categories

Our test suite covers all essential testing scenarios:

#### **Happy Path Tests** ✅
- Normal operation with valid inputs
- Successful user interactions
- Proper data flow and state management

#### **Success Tests** ✅
- Edge cases that still succeed
- Alternative valid paths
- Performance under normal conditions

#### **Unhappy Path Tests** ⚠️
- Expected failures and error conditions
- Missing or invalid data handling
- Graceful degradation scenarios

#### **Negative Tests** ❌
- Invalid inputs and edge cases
- Boundary condition testing
- Malformed data handling

#### **Error Tests** 🚨
- System errors and exceptions
- File system issues
- Network and external dependency failures

#### **Exception Tests** 💥
- Unhandled exception scenarios
- Critical failure modes
- Recovery mechanisms

#### **Boundary Tests** 📏
- Data size limits
- Performance boundaries
- Resource constraints

#### **Security Tests** 🔒
- Data integrity verification
- Tamper detection
- Access control validation

#### **Integration Tests** 🔗
- Component interaction testing
- End-to-end workflows
- Cross-module dependencies

#### **Mock Tests** 🎭
- External dependency mocking
- Isolated unit testing
- Controlled test environments

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

The test suite provides comprehensive coverage including:

#### **Core Functionality Tests**
- **Resource Management**: File operations, configuration loading/saving
- **UI Components**: Tkinter widgets, event handling, user interactions
- **Application Logic**: Main app flow, startup screen, mode switching
- **Security**: HMAC-based config protection, tamper detection

#### **Startup Screen Tests**
- **User Choice Flow**: Sign/Learn mode selection
- **Configuration Persistence**: Secure storage and retrieval
- **Menu Integration**: Mode switching via application menu
- **Error Handling**: Graceful failure recovery

#### **Security Tests**
- **Data Integrity**: HMAC signature verification
- **Tamper Detection**: Configuration file modification detection
- **Access Control**: File permission management
- **Key Management**: Secure key generation and storage

#### **Performance Tests**
- **Large Data Handling**: Multi-megabyte configuration files
- **Concurrent Access**: Multiple application instances
- **Memory Usage**: Efficient resource management
- **Response Time**: UI responsiveness under load

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