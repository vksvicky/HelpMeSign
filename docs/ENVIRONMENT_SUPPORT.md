# Environment Support in HelpMeSign

HelpMeSign now supports two distinct environments: **Development** and **Production**, each optimized for their specific use cases.

## Environment Overview

### Development Environment (`dev`)
- **Default for development runs**
- **Purpose**: Development, testing, and debugging
- **Features**:
  - Debug-level logging with detailed information
  - Larger window size (1200x800) for better development workflow
  - Development-specific UI indicators
  - Detailed error messages and stack traces
  - Debug information in output (timestamps, processing details)

### Production Environment (`prod`)
- **Default for built executables**
- **Purpose**: End-user deployment
- **Features**:
  - Info-level logging for minimal output
  - Standard window size (1024x1024)
  - Clean, professional UI without debug indicators
  - Optimized performance
  - Minimal error output for better user experience

## Usage

### Command Line Interface

Both `main.py` and `run_app.py` support environment selection:

```bash
# Development mode (default)
python3 main.py
python3 run_app.py

# Production mode
python3 main.py --env prod
python3 run_app.py --env prod

# Development mode with debug logging
python3 run_app.py --env dev --debug

# Production mode with custom config
python3 run_app.py --env prod --config custom.json
```

### Built Executables

All build scripts create production-ready executables that default to the `prod` environment:

- **macOS**: `dist/HelpMeSign.app` (production mode by default)
- **Windows**: `dist/HelpMeSign.exe` (production mode by default)
- **Linux**: `dist/HelpMeSign` (production mode by default)

Users can still override the environment:
```bash
# macOS
./HelpMeSign.app/Contents/MacOS/HelpMeSign --env dev

# Windows
HelpMeSign.exe --env dev

# Linux
./HelpMeSign --env dev
```

## Implementation Details

### Core Application (`src/helpmesign/core/app.py`)

The main application class accepts an environment parameter:

```python
class HelpMeSignApp:
    def __init__(self, environment: str = "dev"):
        self.environment = environment.lower()
        # Environment-specific configuration
        if self.environment == "prod":
            # Production settings
            window_width = self.config.get('window_size', {}).get('width', 1024)
            window_height = self.config.get('window_size', {}).get('height', 1024)
        else:  # dev environment
            # Development settings
            window_width = self.config.get('dev_window_size', {}).get('width', 1200)
            window_height = self.config.get('dev_window_size', {}).get('height', 800)
```

### Logging System (`src/helpmesign/utils/logger.py`)

Environment-specific logging configuration:

```python
class HelpMeSignLogger:
    def __init__(self, name: str = "HelpMeSign", config: Optional[Dict[str, Any]] = None, environment: str = "dev"):
        self.environment = environment.lower()
        
        # Get log level based on environment
        if self.environment == "prod":
            # Production: Use config or default to INFO
            log_level_str = self.config.get('logging', {}).get('level', 'INFO').upper()
        else:
            # Development: Use config or default to DEBUG
            log_level_str = self.config.get('logging', {}).get('dev_level', 'DEBUG').upper()
```

### Configuration (`resources/data/config.json`)

Environment-specific settings in the configuration file:

```json
{
    "window_size": {
        "width": 1024,
        "height": 1024
    },
    "dev_window_size": {
        "width": 1200,
        "height": 800
    },
    "logging": {
        "level": "INFO",
        "dev_level": "DEBUG"
    },
    "environments": {
        "dev": {
            "debug_mode": true,
            "show_dev_info": true,
            "log_level": "DEBUG",
            "window_size": {
                "width": 1200,
                "height": 800
            },
            "features": {
                "auto_save": true,
                "show_debug_info": true,
                "enable_dev_tools": true
            }
        },
        "prod": {
            "debug_mode": false,
            "show_dev_info": false,
            "log_level": "INFO",
            "window_size": {
                "width": 1024,
                "height": 1024
            },
            "features": {
                "auto_save": true,
                "show_debug_info": false,
                "enable_dev_tools": false
            }
        }
    }
}
```

## Build Scripts

### macOS Build (`scripts/build_macos_app.py`)

Creates a production main file (`main_prod.py`) that defaults to `prod` environment:

```python
def create_production_main():
    """Create a production version of main.py that defaults to prod environment"""
    prod_main_content = '''#!/usr/bin/env python3
"""
Production entry point for HelpMeSign application
"""

import sys
import argparse
from PySide6.QtWidgets import QApplication
from src.helpmesign.core.app import main


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Sign Language Translation and Learning Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  HelpMeSign.app                    # Run in prod mode (default)
  HelpMeSign.app --env prod         # Run in production mode
  HelpMeSign.app --env dev          # Run in development mode
        """
    )
    
    parser.add_argument(
        '--env',
        choices=['dev', 'prod'],
        default='prod',
        help='Environment to run in (default: prod)'
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    main(args.env)
'''
```

### Windows Build (`scripts/build_windows_exe.py`)

Similar to macOS, creates a production main file with `prod` as default.

### Linux Build (`scripts/build_linux_app.py`)

Creates a production main file with `prod` as default, plus additional Linux-specific features:
- Desktop integration (`.desktop` file)
- AppImage creation (optional)
- Debian package creation (optional)

## Environment Differences

| Feature | Development | Production |
|---------|-------------|------------|
| **Default Environment** | `dev` | `prod` |
| **Window Size** | 1200x800 | 1024x1024 |
| **Log Level** | DEBUG | INFO |
| **Log Format** | Detailed with file/line info | Simple format |
| **Debug Info** | Shown in UI and output | Hidden |
| **Error Messages** | Detailed with stack traces | User-friendly |
| **Performance** | Optimized for debugging | Optimized for speed |
| **UI Indicators** | Development mode shown | Clean, professional |

## Benefits

### For Developers
- **Easy Development**: Default to development mode with detailed logging
- **Debugging Support**: Comprehensive error information and debug output
- **Flexible Testing**: Can test both environments from command line
- **Clear Separation**: Distinct configurations for different use cases

### For End Users
- **Optimized Experience**: Production builds are optimized for performance
- **Clean Interface**: No debug information cluttering the UI
- **Professional Appearance**: Standard window sizes and clean design
- **Reliable Operation**: Minimal logging reduces overhead

### For Build Process
- **Automated Production**: Build scripts automatically create production-ready executables
- **Consistent Behavior**: All built executables behave consistently
- **User Override**: Users can still switch to development mode if needed
- **Platform Integration**: Native integration with each platform's conventions

## Migration Notes

The environment support was added without breaking existing functionality:

- **Backward Compatibility**: All existing scripts continue to work
- **Default Behavior**: Development mode remains the default for source runs
- **Gradual Adoption**: Can be adopted incrementally
- **Documentation**: Comprehensive documentation and examples provided

## Future Enhancements

Potential future improvements:

1. **Environment-Specific Themes**: Different color schemes for dev/prod
2. **Feature Flags**: Environment-based feature toggles
3. **Performance Monitoring**: Production-specific performance tracking
4. **Error Reporting**: Different error handling strategies per environment
5. **Configuration Validation**: Environment-specific config validation rules 