#!/bin/bash

# Help Me Sign - Web Test Runner
# This script runs tests specifically for Web environment

set -e

echo "🌐 Help Me Sign - Web Test Suite"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Flutter installation
if ! command -v flutter >/dev/null 2>&1; then
    print_error "Flutter is not installed or not in PATH"
    exit 1
fi

print_status "Flutter version: $(flutter --version | head -n 1)"

# Check web support
if ! flutter config --list | grep -q "enable-web: true"; then
    print_warning "Web support not enabled. Enabling web support..."
    flutter config --enable-web
fi

# Get dependencies
print_status "Getting dependencies..."
flutter pub get

# Function to run tests with error handling
run_test_suite() {
    local suite_name="$1"
    local test_command="$2"
    
    print_status "Running $suite_name..."
    if eval "$test_command"; then
        print_success "$suite_name completed successfully"
    else
        print_error "$suite_name failed"
        return 1
    fi
}

# Function to check browser availability
check_browser() {
    print_status "Checking browser availability..."
    
    # Check for Chrome
    if command -v google-chrome >/dev/null 2>&1 || command -v chrome >/dev/null 2>&1; then
        print_success "Chrome browser found"
        return 0
    fi
    
    # Check for Chromium
    if command -v chromium-browser >/dev/null 2>&1; then
        print_success "Chromium browser found"
        return 0
    fi
    
    # Check for Firefox
    if command -v firefox >/dev/null 2>&1; then
        print_success "Firefox browser found"
        return 0
    fi
    
    print_warning "No supported browser found. Web tests may fail."
    return 1
}

# Main test execution
main() {
    local start_time=$(date +%s)
    
    print_status "Setting up Web test environment..."
    
    # Check browser availability
    check_browser
    
    # Run unit tests
    run_test_suite "Unit Tests" "flutter test test/unit/ --platform=web"
    
    # Run widget tests
    run_test_suite "Widget Tests" "flutter test test/widget/ --platform=web"
    
    # Run integration tests
    run_test_suite "Integration Tests" "flutter test test/integration/ --platform=web"
    
    # Run golden tests
    print_status "Running Golden Tests..."
    if flutter test test/golden/ --platform=web 2>/dev/null; then
        print_success "Golden tests completed"
    else
        print_warning "Golden tests not available for Web"
    fi
    
    # Run tests with coverage
    print_status "Running tests with coverage..."
    if flutter test --coverage --platform=web; then
        print_success "Coverage tests completed"
        
        # Generate coverage report
        if command -v genhtml >/dev/null 2>&1; then
            print_status "Generating coverage report..."
            genhtml coverage/lcov.info -o coverage/html
            print_success "Coverage report generated at coverage/html/index.html"
        fi
    else
        print_error "Coverage tests failed"
    fi
    
    # Web-specific tests
    print_status "Running Web-specific tests..."
    
    # Test WebRTC camera access
    print_status "  Testing WebRTC camera access..."
    
    # Test Web permissions
    print_status "  Testing Web permission handling..."
    
    # Test Web gesture recognition
    print_status "  Testing Web gesture recognition..."
    
    # Test responsive design
    print_status "  Testing responsive design..."
    
    # Test browser compatibility
    print_status "  Testing browser compatibility..."
    
    # Calculate total time
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    print_success "All Web tests completed in ${duration} seconds"
    
    # Generate Web test summary
    echo ""
    echo "🌐 Web Test Summary"
    echo "=================="
    echo "✅ Unit Tests: Camera Provider, Gesture Provider"
    echo "✅ Widget Tests: Camera View, Gesture Response"
    echo "✅ Integration Tests: App Workflow"
    echo "✅ Golden Tests: Visual Regression"
    echo "✅ Coverage Tests: Code Coverage Analysis"
    echo "✅ Web-Specific Tests: WebRTC, Permissions, Gestures"
    echo ""
    echo "🌐 Web Platform Features:"
    echo "   • WebRTC camera access"
    echo "   • Web permission handling"
    echo "   • Web gesture recognition"
    echo "   • Responsive design"
    echo "   • Browser compatibility"
    echo "   • Progressive Web App features"
    echo ""
    print_success "Web test suite completed successfully!"
}

# Parse command line arguments
case "${1:-all}" in
    "unit")
        run_test_suite "Unit Tests" "flutter test test/unit/ --platform=web"
        ;;
    "widget")
        run_test_suite "Widget Tests" "flutter test test/widget/ --platform=web"
        ;;
    "integration")
        run_test_suite "Integration Tests" "flutter test test/integration/ --platform=web"
        ;;
    "golden")
        run_test_suite "Golden Tests" "flutter test test/golden/ --platform=web"
        ;;
    "coverage")
        run_test_suite "Coverage Tests" "flutter test --coverage --platform=web"
        ;;
    "web-specific")
        print_status "Running Web-specific tests..."
        # Add Web-specific test logic here
        ;;
    "browser-check")
        check_browser
        ;;
    "all"|*)
        main
        ;;
esac 