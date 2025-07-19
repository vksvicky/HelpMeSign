#!/bin/bash

# Help Me Sign - Master Script
# This script provides a unified interface for running tests and the actual app

set -e

echo "🎯 Help Me Sign - Master Script"
echo "=============================="

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
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  test [environment] [test_type]    - Run tests"
    echo "  run [environment] [mode]          - Run the actual app"
    echo "  build [platform] [build_type]     - Build the app for distribution"
    echo "  dev [environment]                 - Development workflow (test + run)"
    echo "  deploy [platform]                 - Production deployment workflow"
    echo ""
    echo "Test Environments:"
    echo "  ios, android, web, desktop, ci, all"
    echo ""
    echo "App Environments:"
    echo "  ios, android, web, macos, windows, linux, all"
    echo ""
    echo "Build Platforms:"
    echo "  ios, android, web, macos, windows, linux, all"
    echo ""
    echo "Examples:"
    echo "  $0 test ios unit                 # Run unit tests for iOS"
    echo "  $0 run web debug                 # Run web app in debug mode"
    echo "  $0 build android release         # Build Android app for release"
    echo "  $0 dev web                       # Development workflow for web"
    echo "  $0 deploy all                    # Deploy to all platforms"
    echo ""
    echo "Additional Options:"
    echo "  --help, -h                       - Show this help message"
    echo "  --version, -v                    - Show version information"
    echo "  --list-commands, -l              - List available commands"
    echo "  --check-setup, -c                - Check development setup"
}

# Function to show version
show_version() {
    echo "Help Me Sign - Master Script v1.0.0"
    echo "Comprehensive Flutter development toolkit"
    echo "Supports: Testing, Running, Building, Deployment"
}

# Function to list commands
list_commands() {
    echo "Available Commands:"
    echo ""
    echo "🧪 Testing Commands:"
    echo "  test ios unit                    - Run unit tests for iOS"
    echo "  test android widget              - Run widget tests for Android"
    echo "  test web integration             - Run integration tests for Web"
    echo "  test desktop coverage            - Run coverage tests for Desktop"
    echo "  test all                         - Run all tests on all platforms"
    echo ""
    echo "🚀 App Running Commands:"
    echo "  run ios debug                    - Run iOS app in debug mode"
    echo "  run android release              - Run Android app in release mode"
    echo "  run web hot-reload               - Run web app with hot reload"
    echo "  run macos profile                - Run macOS app in profile mode"
    echo "  run all debug                    - Run app on all platforms"
    echo ""
    echo "🏗️  Building Commands:"
    echo "  build ios release                - Build iOS app for release"
    echo "  build android debug              - Build Android app in debug"
    echo "  build web release                - Build web app for production"
    echo "  build all release                - Build all platforms for release"
    echo ""
    echo "🛠️  Development Workflow:"
    echo "  dev web                          - Test + Run for web development"
    echo "  dev ios                          - Test + Run for iOS development"
    echo "  dev android                      - Test + Run for Android development"
    echo ""
    echo "🚀 Deployment Workflow:"
    echo "  deploy all                       - Test + Build + Deploy all platforms"
    echo "  deploy web                       - Test + Build + Deploy web"
    echo "  deploy mobile                    - Test + Build + Deploy mobile platforms"
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

# Function to check development setup
check_setup() {
    print_status "Checking development setup..."
    
    # Check Flutter
    check_flutter
    
    # Check script directory
    if [[ ! -d "scripts" ]]; then
        print_error "Scripts directory not found. Please run this script from the project root."
        exit 1
    fi
    
    # Check required scripts
    local required_scripts=("run_tests.sh" "run_app.sh" "build_app.sh")
    for script in "${required_scripts[@]}"; do
        if [[ ! -f "scripts/$script" ]]; then
            print_error "Required script not found: scripts/$script"
            exit 1
        fi
    done
    
    # Check script permissions
    for script in "${required_scripts[@]}"; do
        if [[ ! -x "scripts/$script" ]]; then
            print_warning "Script not executable: scripts/$script"
            print_status "Making script executable..."
            chmod +x "scripts/$script"
        fi
    done
    
    print_success "Development setup is ready!"
}

# Function to run tests
run_tests() {
    local environment="$1"
    local test_type="$2"
    
    print_status "Running tests for $environment..."
    if ./scripts/run_tests.sh "$environment" "$test_type"; then
        print_success "Tests completed successfully"
        return 0
    else
        print_error "Tests failed"
        return 1
    fi
}

# Function to run app
run_app() {
    local environment="$1"
    local mode="$2"
    
    print_status "Running app for $environment..."
    if ./scripts/run_app.sh "$environment" "$mode"; then
        print_success "App started successfully"
        return 0
    else
        print_error "App failed to start"
        return 1
    fi
}

# Function to build app
build_app() {
    local platform="$1"
    local build_type="$2"
    
    print_status "Building app for $platform..."
    if ./scripts/build_app.sh "$platform" "$build_type"; then
        print_success "App built successfully"
        return 0
    else
        print_error "App build failed"
        return 1
    fi
}

# Function to run development workflow
run_dev_workflow() {
    local environment="$1"
    
    print_status "Starting development workflow for $environment..."
    
    # Run tests first
    print_status "Step 1: Running tests..."
    if run_tests "$environment" "all"; then
        print_success "Tests passed"
    else
        print_warning "Tests failed, but continuing with app run..."
    fi
    
    echo ""
    
    # Run the app
    print_status "Step 2: Running app..."
    if run_app "$environment" "debug"; then
        print_success "Development workflow completed successfully"
    else
        print_error "Development workflow failed"
        return 1
    fi
}

# Function to run deployment workflow
run_deploy_workflow() {
    local platform="$1"
    
    print_status "Starting deployment workflow for $platform..."
    
    # Run tests first
    print_status "Step 1: Running tests..."
    if run_tests "$platform" "all"; then
        print_success "Tests passed"
    else
        print_error "Tests failed. Deployment aborted."
        return 1
    fi
    
    echo ""
    
    # Build the app
    print_status "Step 2: Building app..."
    if build_app "$platform" "release"; then
        print_success "App built successfully"
    else
        print_error "App build failed. Deployment aborted."
        return 1
    fi
    
    echo ""
    
    # Deployment step (placeholder for future implementation)
    print_status "Step 3: Deploying app..."
    print_warning "Deployment step not yet implemented"
    print_status "Build artifacts are ready for manual deployment"
    
    print_success "Deployment workflow completed successfully"
}

# Main execution
main() {
    local command="$1"
    local arg1="$2"
    local arg2="$3"
    
    # Check prerequisites
    check_flutter
    
    # Handle special commands
    case "$command" in
        "--help"|"-h")
            show_usage
            exit 0
            ;;
        "--version"|"-v")
            show_version
            exit 0
            ;;
        "--list-commands"|"-l")
            list_commands
            exit 0
            ;;
        "--check-setup"|"-c")
            check_setup
            exit 0
            ;;
    esac
    
    # Validate command
    case "$command" in
        "test"|"run"|"build"|"dev"|"deploy")
            # Valid command
            ;;
        "")
            print_error "No command specified"
            show_usage
            exit 1
            ;;
        *)
            print_error "Unknown command: $command"
            print_error "Use --list-commands to see available options"
            exit 1
            ;;
    esac
    
    # Execute command
    case "$command" in
        "test")
            run_tests "$arg1" "$arg2"
            ;;
        "run")
            run_app "$arg1" "$arg2"
            ;;
        "build")
            build_app "$arg1" "$arg2"
            ;;
        "dev")
            run_dev_workflow "$arg1"
            ;;
        "deploy")
            run_deploy_workflow "$arg1"
            ;;
    esac
    
    print_success "Master script completed successfully!"
}

# Parse command line arguments
if [[ $# -eq 0 ]]; then
    show_usage
    exit 0
fi

main "$@" 