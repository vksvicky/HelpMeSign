# macOS Menubar Fix

## Issue Description

On macOS, when running PySide6 applications directly through Python (not as a bundled app), the menubar shows "Python" instead of the application name "HelpMeSign". This is a known limitation of Qt applications on macOS when not packaged as proper `.app` bundles.

## Root Cause

The macOS menubar displays the process name of the application. When running a Python script directly, the process name is "Python" regardless of the application name set in the Qt application metadata.

## Solutions

### Solution 1: Build as macOS App Bundle (Recommended for Production)

The most reliable solution is to build the application as a proper macOS `.app` bundle using the provided build script:

```bash
# Build the application as a macOS app bundle
python3 scripts/build_macos_app.py

# The built app will show "HelpMeSign" in the menubar
```

This works because the app bundle includes an `Info.plist` file with the correct application metadata:
- `CFBundleName`: "HelpMeSign"
- `CFBundleDisplayName`: "HelpMeSign"

### Solution 2: Use the Launcher Script (Development)

For development, use the provided launcher script which properly activates the virtual environment:

```bash
# Use the launcher script
./run_helpmesign.sh

# Or with your virtual environment
clear && source venv/bin/activate && ./run_helpmesign.sh
```

**Note**: This will still show "Python" in the menubar, but the application will work correctly.

### Solution 3: Direct Python Execution (Development)

For development, you can continue using your current method:

```bash
clear && source venv/bin/activate && python3 run_app.py
```

**Note**: This will show "Python" in the menubar.

## Technical Details

### Why the Symbolic Link Approach Doesn't Work

The Stack Overflow solution of creating a symbolic link to Python with the app name doesn't work reliably because:
1. The symbolic link approach can cause import issues with virtual environments
2. macOS security features may prevent the symbolic link from working correctly
3. The process name is still derived from the underlying Python executable

### What We've Implemented

1. **Application Metadata**: Set in `run_app.py` and `main.py`:
   ```python
   app.setApplicationName("HelpMeSign")
   app.setApplicationDisplayName("HelpMeSign")
   ```

2. **Environment Variables**: Set for macOS:
   ```python
   os.environ['APP_NAME'] = "HelpMeSign"
   os.environ['CFBundleName'] = "HelpMeSign"
   os.environ['CFBundleDisplayName'] = "HelpMeSign"
   ```

3. **Process Name Setting**: Attempted using `ctypes`:
   ```python
   ctypes.CDLL('libc.dylib').setproctitle(app_name.encode('utf-8'))
   ```

4. **Build Script**: Proper `Info.plist` configuration in `scripts/build_macos_app.py`

## Recommendations

1. **For Development**: Use the launcher script or your current method - the "Python" menubar is acceptable for development
2. **For Production**: Always build as a macOS app bundle using the build script
3. **For Distribution**: Use the built `.app` bundle which will show the correct application name

## References

- [Stack Overflow Discussion](https://stackoverflow.com/questions/7827430/setting-mac-osx-application-menu-menu-bar-item-to-other-than-python-in-my-pyth)
- [Qt for macOS Documentation](https://doc.qt.io/qt-6/macos.html)
- [py2app Documentation](https://py2app.readthedocs.io/) 