# Build Scripts

This folder contains build scripts for creating native executables from the HelpMeSign Python application.

## Available Scripts

### `build_macos_app.py`
Creates a native macOS `.app` bundle using py2app.

**Requirements:**
- macOS system
- Python 3.8+
- py2app

**Usage:**
```bash
python3 build_macos_app.py
```

**Output:**
- `dist/HelpMeSign.app` - Native macOS application bundle
- `HelpMeSign.dmg` - Optional DMG installer

### `build_windows_exe.py`
Creates a Windows 64-bit executable using PyInstaller.

**Requirements:**
- Windows system
- Python 3.8+
- PyInstaller
- pefile (optional, for executable analysis)

**Usage:**
```bash
python3 build_windows_exe.py
```

**Output:**
- `dist/HelpMeSign.exe` - 64-bit Windows executable
- `HelpMeSign-Setup.exe` - Optional NSIS installer

### `build_linux_app.py`
Creates a Linux executable using PyInstaller.

**Requirements:**
- Linux system
- Python 3.8+
- PyInstaller

**Usage:**
```bash
python3 build_linux_app.py
```

**Output:**
- `dist/HelpMeSign` - Linux executable
- `HelpMeSign.tar.gz` - Compressed package

### `build_all.py`
Universal build script that automatically detects the platform and runs the appropriate build script.

**Usage:**
```bash
python3 build_all.py
```

## Project Structure

```
scripts/
├── __init__.py              # Package initialization
├── README.md               # This file
├── build_macos_app.py      # macOS app bundle builder
├── build_windows_exe.py    # Windows executable builder
├── build_linux_app.py      # Linux executable builder
└── build_all.py           # Universal build script
```

## Dependencies

### macOS Build Dependencies
```bash
pip3 install py2app
```

### Windows Build Dependencies
```bash
pip3 install pyinstaller pefile
```

### Linux Build Dependencies
```bash
pip3 install pyinstaller
```

### Optional Tools
- **create-dmg** (macOS): For creating DMG installers
  ```bash
  brew install create-dmg
  ```
- **NSIS** (Windows): For creating Windows installers
  - Download from: https://nsis.sourceforge.io/Download

## Build Process

Each build script follows this process:

1. **Check Requirements** - Verify platform and dependencies
2. **Clean Build Directories** - Remove previous builds
3. **Create Configuration** - Generate build-specific config files
4. **Build Executable** - Run the appropriate build tool
5. **Verify Output** - Check the built executable
6. **Create Installer** - Generate optional installer packages

## Output Location

All built executables are placed in the `dist/` directory at the project root:

```
dist/
├── HelpMeSign.app/          # macOS app bundle
├── HelpMeSign.exe          # Windows executable
├── HelpMeSign              # Linux executable
├── HelpMeSign.dmg          # macOS DMG installer (optional)
├── HelpMeSign-Setup.exe    # Windows NSIS installer (optional)
└── HelpMeSign.tar.gz       # Linux package (optional)
``` 