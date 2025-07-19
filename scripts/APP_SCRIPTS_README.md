# 🚀 Help Me Sign - App Scripts Documentation

## Overview

This directory contains comprehensive scripts for running, building, and deploying the Help Me Sign Flutter application across all environments and platforms.

## 📁 Complete Script Structure

```
scripts/
├── help_me_sign.sh                    # 🎯 Master script (unified interface)
├── run_tests.sh                       # 🧪 Master test runner
├── run_app.sh                         # 🚀 App runner
├── build_app.sh                       # 🏗️  App builder
├── run_tests_ios.sh                   # 🍎 iOS test runner
├── run_tests_android.sh               # 🤖 Android test runner
├── run_tests_web.sh                   # 🌐 Web test runner
├── run_tests_desktop.sh               # 🖥️  Desktop test runner
├── run_tests_ci.sh                    # 🚀 CI/CD test runner
├── run_tests_all_platforms.sh         # 🌍 All platforms test runner
├── README.md                          # 📚 Test scripts documentation
└── APP_SCRIPTS_README.md              # 📚 This documentation
```

## 🎯 Master Script (`help_me_sign.sh`)

The `help_me_sign.sh` script provides a **unified interface** for all development tasks.

### Usage

```bash
./scripts/help_me_sign.sh [command] [options]
```

### Commands

- **`test`** - Run tests across environments
- **`run`** - Run the actual app
- **`build`** - Build the app for distribution
- **`dev`** - Development workflow (test + run)
- **`deploy`** - Production deployment workflow

### Examples

```bash
# Run unit tests for iOS
./scripts/help_me_sign.sh test ios unit

# Run web app in debug mode
./scripts/help_me_sign.sh run web debug

# Build Android app for release
./scripts/help_me_sign.sh build android release

# Development workflow for web
./scripts/help_me_sign.sh dev web

# Deploy to all platforms
./scripts/help_me_sign.sh deploy all

# Show help
./scripts/help_me_sign.sh --help

# List all commands
./scripts/help_me_sign.sh --list-commands

# Check development setup
./scripts/help_me_sign.sh --check-setup
```

## 🚀 App Runner (`run_app.sh`)

The `run_app.sh` script runs the actual Help Me Sign app across all environments.

### Features

- **Cross-platform support** - iOS, Android, Web, macOS, Windows, Linux
- **Multiple modes** - Debug, Release, Profile, Hot Reload
- **Device detection** - Automatic device/emulator detection
- **Error handling** - Comprehensive error reporting

### Usage

```bash
./scripts/run_app.sh [environment] [mode]
```

### Environments

- **`ios`** - iOS Simulator or physical device
- **`android`** - Android Emulator or physical device
- **`web`** - Web browser (Chrome, Firefox, etc.)
- **`macos`** - macOS desktop app
- **`windows`** - Windows desktop app
- **`linux`** - Linux desktop app
- **`all`** - All available platforms

### Modes

- **`debug`** - Debug mode (default)
- **`release`** - Release mode
- **`profile`** - Profile mode
- **`hot-reload`** - Hot reload enabled

### Examples

```bash
# Run iOS app in debug mode
./scripts/run_app.sh ios

# Run Android app in release mode
./scripts/run_app.sh android release

# Run web app with hot reload
./scripts/run_app.sh web hot-reload

# Run app on all platforms
./scripts/run_app.sh all debug

# Check dependencies
./scripts/run_app.sh --check-dependencies

# List environments
./scripts/run_app.sh --list-environments
```

## 🏗️ App Builder (`build_app.sh`)

The `build_app.sh` script builds the Help Me Sign app for distribution across all platforms.

### Features

- **Production builds** - Release-ready builds for all platforms
- **Multiple build types** - Debug, Release, Profile
- **Clean builds** - Option to clean before building
- **Build outputs** - Automatic output location reporting

### Usage

```bash
./scripts/build_app.sh [platform] [build_type] [options]
```

### Platforms

- **`ios`** - iOS app (.ipa file)
- **`android`** - Android app (.apk/.aab files)
- **`web`** - Web app (deployable files)
- **`macos`** - macOS app (.app bundle)
- **`windows`** - Windows app (.exe file)
- **`linux`** - Linux app (executable)
- **`all`** - All platforms

### Build Types

- **`debug`** - Debug build (default)
- **`release`** - Release build
- **`profile`** - Profile build

### Options

- **`--clean`** - Clean build before building
- **`--clean-build`** - Clean build before building

### Examples

```bash
# Build iOS app for release
./scripts/build_app.sh ios release

# Build Android app in debug mode
./scripts/build_app.sh android debug

# Build web app for production
./scripts/build_app.sh web release

# Build all platforms with clean build
./scripts/build_app.sh all release --clean

# List platforms
./scripts/build_app.sh --list-platforms

# Check dependencies
./scripts/build_app.sh --check-dependencies
```

## 🧪 Test Scripts

The test scripts provide comprehensive testing capabilities:

### Master Test Runner (`run_tests.sh`)

```bash
# Run all iOS tests
./scripts/run_tests.sh ios

# Run unit tests for Android
./scripts/run_tests.sh android unit

# Run coverage tests for Web
./scripts/run_tests.sh web coverage

# Run all tests on all platforms
./scripts/run_tests.sh all
```

### Platform-Specific Test Runners

- **`run_tests_ios.sh`** - iOS-specific testing
- **`run_tests_android.sh`** - Android-specific testing
- **`run_tests_web.sh`** - Web-specific testing
- **`run_tests_desktop.sh`** - Desktop-specific testing
- **`run_tests_ci.sh`** - CI/CD environment testing
- **`run_tests_all_platforms.sh`** - All platforms testing

## 🛠️ Development Workflows

### 1. Development Workflow (`dev` command)

The `dev` command runs a complete development workflow:

1. **Run tests** for the specified environment
2. **Run the app** in debug mode

```bash
# Development workflow for web
./scripts/help_me_sign.sh dev web

# Development workflow for iOS
./scripts/help_me_sign.sh dev ios

# Development workflow for Android
./scripts/help_me_sign.sh dev android
```

### 2. Deployment Workflow (`deploy` command)

The `deploy` command runs a complete deployment workflow:

1. **Run tests** for the specified platform
2. **Build the app** in release mode
3. **Prepare for deployment** (placeholder for future implementation)

```bash
# Deploy to all platforms
./scripts/help_me_sign.sh deploy all

# Deploy web app
./scripts/help_me_sign.sh deploy web

# Deploy mobile platforms
./scripts/help_me_sign.sh deploy mobile
```

## 📊 Build Outputs

### iOS
- **Location**: `build/ios/archive/`
- **Output**: `.ipa` file

### Android
- **APK Location**: `build/app/outputs/flutter-apk/`
- **Bundle Location**: `build/app/outputs/bundle/`
- **Output**: `.apk` and `.aab` files

### Web
- **Location**: `build/web/`
- **Output**: Deployable web files

### macOS
- **Location**: `build/macos/Build/Products/Release/`
- **Output**: `.app` bundle

### Windows
- **Location**: `build/windows/runner/Release/`
- **Output**: `.exe` file

### Linux
- **Location**: `build/linux/x64/release/bundle/`
- **Output**: Executable file

## 🔧 Environment Setup

### Prerequisites

1. **Flutter Installation**
   ```bash
   flutter --version
   ```

2. **Platform-Specific Setup**
   - **iOS**: Xcode, iOS Simulator
   - **Android**: Android SDK, ADB, Android Emulator
   - **Web**: Flutter web support enabled
   - **Desktop**: Platform-specific development tools

3. **Script Permissions**
   ```bash
   chmod +x scripts/*.sh
   ```

### Setup Verification

```bash
# Check development setup
./scripts/help_me_sign.sh --check-setup

# Check platform dependencies
./scripts/run_app.sh --check-dependencies

# Check build dependencies
./scripts/build_app.sh --check-dependencies
```

## 🚀 Quick Start

### 1. Basic Usage

```bash
# Check setup
./scripts/help_me_sign.sh --check-setup

# Run app for current platform
./scripts/help_me_sign.sh run desktop debug

# Run tests for current platform
./scripts/help_me_sign.sh test desktop unit

# Build app for current platform
./scripts/help_me_sign.sh build desktop release
```

### 2. Development Workflow

```bash
# Start development workflow
./scripts/help_me_sign.sh dev web

# Run specific tests
./scripts/help_me_sign.sh test ios unit

# Run app with hot reload
./scripts/help_me_sign.sh run web hot-reload
```

### 3. Production Workflow

```bash
# Build for production
./scripts/help_me_sign.sh build all release

# Deploy to all platforms
./scripts/help_me_sign.sh deploy all

# Build specific platform
./scripts/help_me_sign.sh build android release
```

## 📋 Script Features

### Common Features Across All Scripts

- **Color-coded output** - Easy-to-read status messages
- **Error handling** - Comprehensive error reporting
- **Help system** - Built-in documentation
- **Platform detection** - Automatic platform validation
- **Dependency checking** - Prerequisite verification
- **Progress reporting** - Real-time status updates

### Platform Support

- **🍎 iOS** - iOS Simulator, physical devices
- **🤖 Android** - Android Emulator, physical devices
- **🌐 Web** - Chrome, Firefox, Safari
- **🍎 macOS** - macOS desktop apps
- **🪟 Windows** - Windows desktop apps
- **🐧 Linux** - Linux desktop apps

### Build Modes

- **Debug** - Development and debugging
- **Release** - Production deployment
- **Profile** - Performance profiling
- **Hot Reload** - Fast development iteration

## 🔍 Troubleshooting

### Common Issues

1. **Script Not Found**
   ```bash
   # Ensure you're in the project root
   cd /path/to/help_me_sign
   ```

2. **Permission Denied**
   ```bash
   # Make scripts executable
   chmod +x scripts/*.sh
   ```

3. **Flutter Not Found**
   ```bash
   # Add Flutter to PATH
   export PATH="$PATH:/path/to/flutter/bin"
   ```

4. **Platform Not Available**
   ```bash
   # Check platform availability
   ./scripts/run_app.sh --check-dependencies
   ```

### Debug Mode

Run scripts with verbose output:

```bash
# Enable debug mode
set -x
./scripts/help_me_sign.sh run web debug
set +x
```

## 📚 Integration with CI/CD

### GitHub Actions Example

```yaml
name: Build and Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: subosito/flutter-action@v2
      - run: chmod +x scripts/*.sh
      - run: ./scripts/help_me_sign.sh test all
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: subosito/flutter-action@v2
      - run: chmod +x scripts/*.sh
      - run: ./scripts/help_me_sign.sh build web release
```

### GitLab CI Example

```yaml
test:
  image: cirrusci/flutter:latest
  script:
    - chmod +x scripts/*.sh
    - ./scripts/help_me_sign.sh test all

build:
  image: cirrusci/flutter:latest
  script:
    - chmod +x scripts/*.sh
    - ./scripts/help_me_sign.sh build all release
```

## 🎯 Best Practices

### 1. Development

- Use `dev` command for daily development
- Run tests before committing code
- Use hot reload for fast iteration
- Test on target platforms regularly

### 2. Building

- Use clean builds for production
- Test builds on target platforms
- Verify build outputs before deployment
- Use appropriate build types

### 3. Deployment

- Run full test suite before deployment
- Build in release mode for production
- Verify all platform builds
- Test deployment artifacts

## 📈 Performance

### Expected Performance

- **Test Execution**: < 30 seconds per platform
- **App Startup**: < 10 seconds per platform
- **Build Time**: < 5 minutes per platform
- **Hot Reload**: < 2 seconds

### Optimization Tips

- Use clean builds sparingly
- Cache dependencies in CI/CD
- Run tests in parallel when possible
- Use appropriate build modes

## 🔄 Continuous Improvement

### Regular Tasks

- Update Flutter and dependencies
- Test on new platform versions
- Optimize build times
- Add new platform support
- Improve error handling

### Feedback Loop

- Monitor script performance
- Address common issues
- Update documentation
- Add new features
- Improve user experience

## 📞 Support

For issues with the app scripts:

1. Check this documentation
2. Review script help messages
3. Check platform requirements
4. Verify Flutter installation
5. Contact the development team

---

**Last Updated**: $(date)
**Version**: 1.0.0
**Flutter Version**: 3.32.7+ 