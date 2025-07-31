# macOS Menubar Fix

## Issue Description

On macOS, when running Qt applications (like HelpMeSign) directly through Python, the menubar shows "Python" instead of the application name "HelpMeSign". This is a known limitation of Qt applications on macOS when not packaged as a proper `.app` bundle.

## Root Cause

The macOS menubar displays the process name of the application. When running a Python script directly, the process name is "Python" rather than the application name. This happens because:

1. The application is launched through the Python interpreter
2. macOS sees the process as "Python" rather than "HelpMeSign"
3. Qt's menubar inherits this process name

## Solutions Implemented

### Solution 1: Launcher Script with Symbolic Link (Development)

The `run_helpmesign.sh` script implements a workaround using symbolic links:

```bash
# Create a temporary symbolic link to Python with the app name
TEMP_PYTHON_LINK="/tmp/HelpMeSign_python"
ln -sf "$PYTHON_PATH" "$TEMP_PYTHON_LINK"

# Run the application using the symbolic link
"$TEMP_PYTHON_LINK" "$SCRIPT_DIR/run_app.py" "$@"
```

This approach:
- Creates a symbolic link named "HelpMeSign_python" pointing to the actual Python executable
- Runs the application through this symbolic link
- macOS sees the process name as "HelpMeSign_python" instead of "Python"
- The menubar displays "HelpMeSign" instead of "Python"

**Usage:**
```bash
./run_helpmesign.sh
```

### Solution 2: macOS App Bundle (Production)

The most robust solution is to build the application as a proper macOS `.app` bundle using the build script:

```bash
python3 scripts/build_macos_app.py
```

This creates a proper macOS application with:
- `Info.plist` file containing the correct application name
- Proper bundle structure
- Correct menubar display

**Benefits:**
- Native macOS application experience
- Correct menubar display
- Proper application icon
- Can be distributed and installed like other macOS apps

### Solution 3: Direct Python Execution (Fallback)

For development without the launcher script:

```bash
clear && source venv/bin/activate && python3 run_app.py
```

**Note:** This will show "Python" in the menubar, but the application will function correctly.

## Technical Details

### Symbolic Link Approach

The symbolic link approach works because:
1. macOS uses the executable name as the process name
2. By creating a symbolic link with the desired name, we trick macOS into using that name
3. The symbolic link points to the actual Python executable, so functionality is preserved

### App Bundle Approach

The app bundle approach works because:
1. `Info.plist` contains `CFBundleName` and `CFBundleDisplayName` keys
2. macOS reads these keys to determine the application name
3. The menubar displays the value from `CFBundleDisplayName`

## Implementation in HelpMeSign

### Launcher Script Features

The `run_helpmesign.sh` script includes:

- Virtual environment detection and activation
- Cross-platform compatibility (macOS vs other platforms)
- Automatic cleanup of temporary symbolic links
- Error handling for missing Python installations

### Build Script Integration

The macOS build script (`scripts/build_macos_app.py`) includes:

- Proper `Info.plist` configuration
- Application icon integration
- Bundle identifier setup
- Version information

## Testing

To verify the menubar fix is working:

1. **Development:** Run `./run_helpmesign.sh` and check that the menubar shows "HelpMeSign"
2. **Production:** Build the app bundle and check that the menubar shows "HelpMeSign"

## References

- [Stack Overflow Discussion](https://stackoverflow.com/questions/7827430/setting-mac-osx-application-menu-menu-bar-item-to-other-than-python-in-my-pyth)
- [Qt for macOS Documentation](https://doc.qt.io/qt-6/macos.html)
- [macOS App Bundle Guidelines](https://developer.apple.com/library/archive/documentation/CoreFoundation/Conceptual/CFBundles/BundleTypes/BundleTypes.html) 