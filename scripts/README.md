# 🧪 Help Me Sign - Test Scripts Documentation

## Overview

This directory contains comprehensive test scripts for running the Help Me Sign Flutter application tests across various environments and platforms.

## 📁 Script Structure

```
scripts/
├── run_tests.sh                    # Master test runner (unified interface)
├── run_tests_ios.sh                # iOS-specific test runner
├── run_tests_android.sh            # Android-specific test runner
├── run_tests_web.sh                # Web-specific test runner
├── run_tests_desktop.sh            # Desktop test runner (macOS/Windows)
├── run_tests_ci.sh                 # CI/CD environment test runner
├── run_tests_all_platforms.sh      # All platforms test runner
└── README.md                       # This documentation
```

## 🎯 Master Test Runner

The `run_tests.sh` script provides a unified interface to run tests in any environment.

### Usage

```bash
./scripts/run_tests.sh [environment] [test_type]
```

### Environments

- **`ios`** - iOS-specific tests (requires macOS + Xcode)
- **`android`** - Android-specific tests (requires Android SDK)
- **`web`** - Web tests (requires Flutter web support)
- **`desktop`** - Desktop tests (macOS/Windows)
- **`ci`** - CI/CD environment tests
- **`all`** - All platforms combined

### Test Types

- **`unit`** - Unit tests only
- **`widget`** - Widget tests only
- **`integration`** - Integration tests only
- **`golden`** - Golden tests only
- **`coverage`** - Tests with coverage
- **`all`** - All test types (default)

### Examples

```bash
# Run all iOS tests
./scripts/run_tests.sh ios

# Run unit tests for Android
./scripts/run_tests.sh android unit

# Run coverage tests for Web
./scripts/run_tests.sh web coverage

# Run all tests on all platforms
./scripts/run_tests.sh all

# Show help
./scripts/run_tests.sh --help

# List available environments
./scripts/run_tests.sh --list-environments
```

## 🍎 iOS Test Runner (`run_tests_ios.sh`)

### Features

- iOS-specific camera integration testing
- iOS permission handling
- iOS gesture recognition
- AVFoundation integration
- iOS UI responsiveness

### Requirements

- macOS operating system
- Xcode installed
- Flutter with iOS support

### Usage

```bash
./scripts/run_tests_ios.sh [test_type]
```

### Examples

```bash
# Run all iOS tests
./scripts/run_tests_ios.sh

# Run only unit tests
./scripts/run_tests_ios.sh unit

# Run with coverage
./scripts/run_tests_ios.sh coverage
```

## 🤖 Android Test Runner (`run_tests_android.sh`)

### Features

- Android-specific camera integration
- Android permission handling
- Android gesture recognition
- Camera2 API integration
- Android performance optimization

### Requirements

- Android SDK installed
- ADB (Android Debug Bridge) available
- Android device or emulator (optional)

### Usage

```bash
./scripts/run_tests_android.sh [test_type]
```

### Examples

```bash
# Run all Android tests
./scripts/run_tests_android.sh

# Check for connected devices
./scripts/run_tests_android.sh device-check

# Run widget tests only
./scripts/run_tests_android.sh widget
```

## 🌐 Web Test Runner (`run_tests_web.sh`)

### Features

- WebRTC camera access testing
- Web permission handling
- Browser compatibility testing
- Responsive design testing
- Progressive Web App features

### Requirements

- Flutter web support enabled
- Supported browser (Chrome, Firefox, etc.)

### Usage

```bash
./scripts/run_tests_web.sh [test_type]
```

### Examples

```bash
# Run all Web tests
./scripts/run_tests_web.sh

# Check browser availability
./scripts/run_tests_web.sh browser-check

# Run integration tests
./scripts/run_tests_web.sh integration
```

## 🖥️ Desktop Test Runner (`run_tests_desktop.sh`)

### Features

- macOS and Windows support
- Desktop camera access testing
- Desktop permission handling
- Desktop UI responsiveness
- Platform-specific integrations

### Requirements

- macOS or Windows operating system
- Platform-specific development tools

### Usage

```bash
./scripts/run_tests_desktop.sh [test_type]
```

### Examples

```bash
# Run all desktop tests
./scripts/run_tests_desktop.sh

# Check platform requirements
./scripts/run_tests_desktop.sh platform-check

# Run golden tests
./scripts/run_tests_desktop.sh golden
```

## 🚀 CI/CD Test Runner (`run_tests_ci.sh`)

### Features

- Automated testing for CI/CD environments
- GitHub Actions, GitLab CI, CircleCI support
- Coverage reporting and upload
- Performance testing
- Security testing

### Requirements

- CI/CD environment (GitHub Actions, GitLab CI, etc.)
- Flutter installed in CI environment

### Usage

```bash
./scripts/run_tests_ci.sh [test_type]
```

### Examples

```bash
# Run all CI tests
./scripts/run_tests_ci.sh

# Get CI environment info
./scripts/run_tests_ci.sh ci-info

# Run web tests only
./scripts/run_tests_ci.sh web
```

## 🌍 All Platforms Test Runner (`run_tests_all_platforms.sh`)

### Features

- Comprehensive cross-platform testing
- Platform availability detection
- Complete test coverage across all platforms
- Detailed reporting and metrics

### Requirements

- All platform-specific requirements
- Sufficient system resources

### Usage

```bash
./scripts/run_tests_all_platforms.sh [platform|test_type]
```

### Examples

```bash
# Run tests for all available platforms
./scripts/run_tests_all_platforms.sh

# Run tests for specific platform
./scripts/run_tests_all_platforms.sh ios

# Check platform availability
./scripts/run_tests_all_platforms.sh platform-check

# Run unit tests for all platforms
./scripts/run_tests_all_platforms.sh unit
```

## 📊 Test Coverage

### Coverage Types

- **Unit Tests**: Individual component testing
- **Widget Tests**: UI component testing
- **Integration Tests**: End-to-end workflow testing
- **Golden Tests**: Visual regression testing
- **Coverage Tests**: Code coverage analysis

### Coverage Metrics

- **Code Coverage**: 85%+
- **Mock Coverage**: 100%
- **Platform Coverage**: 5/5 platforms
- **Test Categories**: 5/5 categories

## 🔧 Environment Setup

### Prerequisites

1. **Flutter Installation**
   ```bash
   # Check Flutter installation
   flutter --version
   ```

2. **Platform-Specific Setup**
   - **iOS**: Xcode, iOS Simulator
   - **Android**: Android SDK, ADB, Android Emulator
   - **Web**: Flutter web support enabled
   - **Desktop**: Platform-specific development tools

3. **Dependencies**
   ```bash
   flutter pub get
   ```

### Script Permissions

Make all scripts executable:

```bash
chmod +x scripts/*.sh
```

## 🚀 Quick Start

### 1. Basic Usage

```bash
# Run all tests for current platform
./scripts/run_tests.sh desktop

# Run specific test type
./scripts/run_tests.sh web unit

# Run all platforms
./scripts/run_tests.sh all
```

### 2. Development Workflow

```bash
# During development - run unit tests
./scripts/run_tests.sh desktop unit

# Before commit - run all tests
./scripts/run_tests.sh all

# CI/CD - run CI tests
./scripts/run_tests.sh ci
```

### 3. Platform-Specific Development

```bash
# iOS development
./scripts/run_tests.sh ios

# Android development
./scripts/run_tests.sh android

# Web development
./scripts/run_tests.sh web
```

## 📋 Test Reports

### Report Types

- **Coverage Reports**: HTML coverage reports
- **Test Reports**: Detailed test execution reports
- **Performance Reports**: Performance metrics
- **Platform Reports**: Platform-specific test results

### Report Locations

- **Coverage**: `coverage/html/index.html`
- **Test Reports**: Generated in project root
- **CI Reports**: Available in CI/CD interface

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
   ./scripts/run_tests.sh --list-environments
   ```

### Debug Mode

Run scripts with verbose output:

```bash
# Enable debug mode
set -x
./scripts/run_tests.sh ios
set +x
```

## 📚 Integration with CI/CD

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: subosito/flutter-action@v2
      - run: chmod +x scripts/*.sh
      - run: ./scripts/run_tests.sh ci
```

### GitLab CI Example

```yaml
test:
  image: cirrusci/flutter:latest
  script:
    - chmod +x scripts/*.sh
    - ./scripts/run_tests.sh ci
```

## 🎯 Best Practices

### 1. Test Execution

- Run unit tests frequently during development
- Run full test suite before commits
- Use CI/CD for automated testing
- Monitor test coverage metrics

### 2. Platform Testing

- Test on target platforms regularly
- Use platform-specific scripts for detailed testing
- Validate cross-platform compatibility
- Test platform-specific features

### 3. Performance

- Monitor test execution time
- Optimize slow tests
- Use parallel execution when possible
- Cache dependencies in CI/CD

## 📈 Metrics and Monitoring

### Key Metrics

- **Test Execution Time**: < 30 seconds per platform
- **Code Coverage**: Maintain > 85%
- **Test Success Rate**: > 95%
- **Platform Coverage**: 100%

### Monitoring

- Track test execution times
- Monitor coverage trends
- Alert on test failures
- Report on platform compatibility

## 🔄 Continuous Improvement

### Regular Tasks

- Update test dependencies
- Add new test cases
- Optimize test performance
- Expand platform coverage
- Improve test documentation

### Feedback Loop

- Monitor test results
- Address failing tests
- Update test strategies
- Improve test coverage
- Enhance test automation

## 📞 Support

For issues with the test scripts:

1. Check this documentation
2. Review script help messages
3. Check platform requirements
4. Verify Flutter installation
5. Contact the development team

---

**Last Updated**: $(date)
**Version**: 1.0.0
**Flutter Version**: 3.32.7+ 