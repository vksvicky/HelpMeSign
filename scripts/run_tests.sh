#!/bin/bash

# Help Me Sign - Master Test Runner
# This script provides a unified interface to run tests in various environments

set -e

echo "🎯 Help Me Sign - Master Test Runner"
echo "===================================="

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

# Function to show usage
show_usage() {
    echo "Usage: $0 [environment] [test_type]"
    echo ""
    echo "Environments:"
    echo "  ios          - Run tests for iOS"
    echo "  android      - Run tests for Android"
    echo "  web          - Run tests for Web"
    echo "  desktop      - Run tests for Desktop (macOS/Windows)"
    echo "  ci           - Run tests for CI/CD environment"
    echo "  all          - Run tests for all platforms"
    echo ""
    echo "Test Types:"
    echo "  unit         - Run unit tests only"
    echo "  widget       - Run widget tests only"
    echo "  integration  - Run integration tests only"
    echo "  golden       - Run golden tests only"
    echo "  coverage     - Run tests with coverage"
    echo "  all          - Run all test types (default)"
    echo ""
    echo "Examples:"
    echo "  $0 ios                    # Run all iOS tests"
    echo "  $0 android unit           # Run unit tests for Android"
    echo "  $0 web coverage           # Run coverage tests for Web"
    echo "  $0 desktop widget         # Run widget tests for Desktop"
    echo "  $0 ci all                 # Run all tests in CI environment"
    echo "  $0 all                    # Run all tests on all platforms"
    echo ""
    echo "Additional Options:"
    echo "  --help, -h                - Show this help message"
    echo "  --version, -v             - Show version information"
    echo "  --list-environments, -l   - List available environments"
}

# Function to show version
show_version() {
    echo "Help Me Sign - Master Test Runner v1.0.0"
    echo "Comprehensive test suite for cross-platform Flutter app"
    echo "Supports: iOS, Android, Web, macOS, Windows"
}

# Function to list environments
list_environments() {
    echo "Available Test Environments:"
    echo ""
    echo "🍎 iOS (run_tests_ios.sh)"
    echo "   • iOS-specific camera integration"
    echo "   • iOS permission handling"
    echo "   • iOS gesture recognition"
    echo "   • Requires: macOS, Xcode"
    echo ""
    echo "🤖 Android (run_tests_android.sh)"
    echo "   • Android-specific camera integration"
    echo "   • Android permission handling"
    echo "   • Android gesture recognition"
    echo "   • Requires: Android SDK, ADB"
    echo ""
    echo "🌐 Web (run_tests_web.sh)"
    echo "   • WebRTC camera access"
    echo "   • Web permission handling"
    echo "   • Browser compatibility"
    echo "   • Requires: Flutter web support"
    echo ""
    echo "🖥️  Desktop (run_tests_desktop.sh)"
    echo "   • macOS and Windows support"
    echo "   • Desktop camera access"
    echo "   • Desktop UI responsiveness"
    echo "   • Platform-specific features"
    echo ""
    echo "🚀 CI/CD (run_tests_ci.sh)"
    echo "   • GitHub Actions, GitLab CI, etc."
    echo "   • Automated testing"
    echo "   • Coverage reporting"
    echo "   • Performance testing"
    echo ""
    echo "🌍 All Platforms (run_tests_all_platforms.sh)"
    echo "   • Comprehensive cross-platform testing"
    echo "   • All environments combined"
    echo "   • Complete test coverage"
    echo "   • Platform availability detection"
}

# Function to run specific environment tests
run_environment_tests() {
    local environment="$1"
    local test_type="${2:-all}"
    local script_path="scripts/run_tests_${environment}.sh"
    
    if [[ ! -f "$script_path" ]]; then
        print_error "Test script not found: $script_path"
        exit 1
    fi
    
    print_status "Running $environment tests with type: $test_type"
    print_status "Executing: $script_path $test_type"
    
    if "$script_path" "$test_type"; then
        print_success "$environment tests completed successfully"
    else
        print_error "$environment tests failed"
        exit 1
    fi
}

# Function to check Flutter installation
check_flutter() {
    if ! command -v flutter >/dev/null 2>&1; then
        print_error "Flutter is not installed or not in PATH"
        print_error "Please install Flutter and add it to your PATH"
        exit 1
    fi
    
    print_status "Flutter version: $(flutter --version | head -n 1)"
}

# Function to check script directory
check_script_directory() {
    if [[ ! -d "scripts" ]]; then
        print_error "Scripts directory not found. Please run this script from the project root."
        exit 1
    fi
}

# Main execution
main() {
    local environment="$1"
    local test_type="${2:-all}"
    
    # Check prerequisites
    check_flutter
    check_script_directory
    
    # Handle special commands
    case "$environment" in
        "--help"|"-h")
            show_usage
            exit 0
            ;;
        "--version"|"-v")
            show_version
            exit 0
            ;;
        "--list-environments"|"-l")
            list_environments
            exit 0
            ;;
    esac
    
    # Validate environment
    case "$environment" in
        "ios"|"android"|"web"|"desktop"|"ci"|"all")
            # Valid environment
            ;;
        "")
            print_error "No environment specified"
            show_usage
            exit 1
            ;;
        *)
            print_error "Unknown environment: $environment"
            print_error "Use --list-environments to see available options"
            exit 1
            ;;
    esac
    
    # Validate test type
    case "$test_type" in
        "unit"|"widget"|"integration"|"golden"|"coverage"|"all")
            # Valid test type
            ;;
        *)
            print_error "Unknown test type: $test_type"
            show_usage
            exit 1
            ;;
    esac
    
    # Run the tests
    print_status "Starting test execution..."
    print_status "Environment: $environment"
    print_status "Test Type: $test_type"
    echo ""
    
    run_environment_tests "$environment" "$test_type"
    
    print_success "Master test runner completed successfully!"
}

# Parse command line arguments
if [[ $# -eq 0 ]]; then
    show_usage
    exit 0
fi

main "$@" 