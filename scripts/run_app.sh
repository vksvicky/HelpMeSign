#!/bin/bash

# Help Me Sign - App Runner
# This script runs the actual Help Me Sign app across all environments

set -e

echo "🚀 Help Me Sign - App Runner"
echo "============================"

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
    echo "Usage: $0 [environment] [mode]"
    echo ""
    echo "Environments:"
    echo "  ios          - Run app on iOS"
    echo "  android      - Run app on Android"
    echo "  web          - Run app on Web"
    echo "  macos        - Run app on macOS"
    echo "  windows      - Run app on Windows"
    echo "  linux        - Run app on Linux"
    echo "  all          - Run app on all available platforms"
    echo ""
    echo "Modes:"
    echo "  debug        - Run in debug mode (default)"
    echo "  release      - Run in release mode"
    echo "  profile      - Run in profile mode"
    echo "  hot-reload   - Run with hot reload enabled"
    echo ""
    echo "Examples:"
    echo "  $0 ios                    # Run iOS app in debug mode"
    echo "  $0 android release        # Run Android app in release mode"
    echo "  $0 web hot-reload         # Run web app with hot reload"
    echo "  $0 all debug              # Run app on all platforms in debug mode"
    echo ""
    echo "Additional Options:"
    echo "  --help, -h                - Show this help message"
    echo "  --version, -v             - Show version information"
    echo "  --list-environments, -l   - List available environments"
    echo "  --check-dependencies, -c  - Check platform dependencies"
}

# Function to show version
show_version() {
    echo "Help Me Sign - App Runner v1.0.0"
    echo "Cross-platform Flutter app runner"
    echo "Supports: iOS, Android, Web, macOS, Windows, Linux"
}

# Function to list environments
list_environments() {
    echo "Available App Environments:"
    echo ""
    echo "🍎 iOS"
    echo "   • iOS Simulator or physical device"
    echo "   • Requires: macOS, Xcode, iOS Simulator"
    echo "   • Command: flutter run -d ios"
    echo ""
    echo "🤖 Android"
    echo "   • Android Emulator or physical device"
    echo "   • Requires: Android SDK, ADB, Android Emulator"
    echo "   • Command: flutter run -d android"
    echo ""
    echo "🌐 Web"
    echo "   • Web browser"
    echo "   • Requires: Flutter web support, browser"
    echo "   • Command: flutter run -d chrome"
    echo ""
    echo "🍎 macOS"
    echo "   • macOS desktop app"
    echo "   • Requires: macOS, Xcode"
    echo "   • Command: flutter run -d macos"
    echo ""
    echo "🪟 Windows"
    echo "   • Windows desktop app"
    echo "   • Requires: Windows, Visual Studio Build Tools"
    echo "   • Command: flutter run -d windows"
    echo ""
    echo "🐧 Linux"
    echo "   • Linux desktop app"
    echo "   • Requires: Linux, development tools"
    echo "   • Command: flutter run -d linux"
    echo ""
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

# Function to check platform availability
check_platform_availability() {
    local platform="$1"
    
    case "$platform" in
        "ios")
            if [[ "$OSTYPE" == "darwin"* ]] && command -v xcrun >/dev/null 2>&1; then
                return 0
            else
                return 1
            fi
            ;;
        "android")
            if command -v adb >/dev/null 2>&1; then
                return 0
            else
                return 1
            fi
            ;;
        "web")
            if flutter config --list | grep -q "enable-web: true"; then
                return 0
            else
                return 1
            fi
            ;;
        "macos")
            if [[ "$OSTYPE" == "darwin"* ]]; then
                return 0
            else
                return 1
            fi
            ;;
        "windows")
            if [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "cygwin"* ]]; then
                return 0
            else
                return 1
            fi
            ;;
        "linux")
            if [[ "$OSTYPE" == "linux"* ]]; then
                return 0
            else
                return 1
            fi
            ;;
        *)
            return 1
            ;;
    esac
}

# Function to get device ID for platform
get_device_id() {
    local platform="$1"
    
    case "$platform" in
        "ios")
            # Get iOS Simulator device ID
            local device_id=$(flutter devices | grep "iPhone" | head -n 1 | awk '{print $1}')
            if [[ -n "$device_id" ]]; then
                echo "$device_id"
            else
                echo "ios"
            fi
            ;;
        "android")
            # Get Android device ID
            local device_id=$(flutter devices | grep "android" | head -n 1 | awk '{print $1}')
            if [[ -n "$device_id" ]]; then
                echo "$device_id"
            else
                echo "android"
            fi
            ;;
        "web")
            echo "chrome"
            ;;
        "macos")
            echo "macos"
            ;;
        "windows")
            echo "windows"
            ;;
        "linux")
            echo "linux"
            ;;
        *)
            echo ""
            ;;
    esac
}

# Function to build Flutter command
build_flutter_command() {
    local platform="$1"
    local mode="$2"
    local device_id="$3"
    
    local command="flutter run"
    
    # Add device flag
    if [[ -n "$device_id" ]]; then
        command="$command -d $device_id"
    fi
    
    # Add mode flag
    case "$mode" in
        "debug")
            # Debug is default, no flag needed
            ;;
        "release")
            command="$command --release"
            ;;
        "profile")
            command="$command --profile"
            ;;
        "hot-reload")
            command="$command --hot"
            ;;
    esac
    
    # Add platform-specific flags
    case "$platform" in
        "web")
            command="$command --web-port=8080"
            ;;
        "ios")
            command="$command --debug"
            ;;
        "android")
            command="$command --debug"
            ;;
    esac
    
    echo "$command"
}

# Function to run app on specific platform
run_app_platform() {
    local platform="$1"
    local mode="$2"
    local platform_name="$3"
    
    if check_platform_availability "$platform"; then
        print_status "Running $platform_name app in $mode mode..."
        
        # Get device ID
        local device_id=$(get_device_id "$platform")
        if [[ -z "$device_id" ]]; then
            print_error "No device found for $platform_name"
            return 1
        fi
        
        # Build command
        local command=$(build_flutter_command "$platform" "$mode" "$device_id")
        print_status "Executing: $command"
        
        # Run the app
        if eval "$command"; then
            print_success "$platform_name app started successfully"
            return 0
        else
            print_error "$platform_name app failed to start"
            return 1
        fi
    else
        print_warning "$platform_name not available on this system"
        return 1
    fi
}

# Function to check dependencies
check_dependencies() {
    print_status "Checking platform dependencies..."
    
    local platforms=("ios" "android" "web" "macos" "windows" "linux")
    local platform_names=("iOS" "Android" "Web" "macOS" "Windows" "Linux")
    
    for i in "${!platforms[@]}"; do
        local platform="${platforms[$i]}"
        local platform_name="${platform_names[$i]}"
        
        if check_platform_availability "$platform"; then
            print_success "$platform_name: Available"
            
            # Check for devices
            local device_id=$(get_device_id "$platform")
            if [[ -n "$device_id" ]]; then
                print_status "  Device: $device_id"
            else
                print_warning "  No device found"
            fi
        else
            print_warning "$platform_name: Not Available"
        fi
    done
}

# Function to run app on all platforms
run_app_all_platforms() {
    local mode="$1"
    local start_time=$(date +%s)
    local total_platforms=0
    local successful_platforms=0
    
    print_status "Running app on all available platforms..."
    
    local platforms=("ios" "android" "web" "macos" "windows" "linux")
    local platform_names=("iOS" "Android" "Web" "macOS" "Windows" "Linux")
    
    for i in "${!platforms[@]}"; do
        local platform="${platforms[$i]}"
        local platform_name="${platform_names[$i]}"
        
        print_status "Starting $platform_name app..."
        
        if run_app_platform "$platform" "$mode" "$platform_name"; then
            successful_platforms=$((successful_platforms + 1))
        fi
        
        total_platforms=$((total_platforms + 1))
        echo ""
    done
    
    # Calculate total time
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    print_success "App deployment completed in ${duration} seconds"
    
    # Generate summary
    echo ""
    echo "📱 App Deployment Summary"
    echo "========================"
    echo "✅ Successful Platforms: $successful_platforms/$total_platforms"
    echo "⏱️  Total Time: ${duration} seconds"
    echo "🎯 Mode: $mode"
    echo ""
    
    if [ $successful_platforms -eq $total_platforms ]; then
        print_success "All platforms deployed successfully!"
    else
        print_warning "Some platforms failed to deploy. Check the logs above."
    fi
}

# Function to get dependencies
get_dependencies() {
    print_status "Getting Flutter dependencies..."
    if flutter pub get; then
        print_success "Dependencies updated successfully"
    else
        print_error "Failed to get dependencies"
        exit 1
    fi
}

# Main execution
main() {
    local environment="$1"
    local mode="${2:-debug}"
    
    # Check prerequisites
    check_flutter
    get_dependencies
    
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
        "--check-dependencies"|"-c")
            check_dependencies
            exit 0
            ;;
    esac
    
    # Validate environment
    case "$environment" in
        "ios"|"android"|"web"|"macos"|"windows"|"linux"|"all")
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
    
    # Validate mode
    case "$mode" in
        "debug"|"release"|"profile"|"hot-reload")
            # Valid mode
            ;;
        *)
            print_error "Unknown mode: $mode"
            show_usage
            exit 1
            ;;
    esac
    
    # Run the app
    print_status "Starting app deployment..."
    print_status "Environment: $environment"
    print_status "Mode: $mode"
    echo ""
    
    if [[ "$environment" == "all" ]]; then
        run_app_all_platforms "$mode"
    else
        local platform_names=("iOS" "Android" "Web" "macOS" "Windows" "Linux")
        local platform_index=0
        
        case "$environment" in
            "ios") platform_index=0 ;;
            "android") platform_index=1 ;;
            "web") platform_index=2 ;;
            "macos") platform_index=3 ;;
            "windows") platform_index=4 ;;
            "linux") platform_index=5 ;;
        esac
        
        run_app_platform "$environment" "$mode" "${platform_names[$platform_index]}"
    fi
    
    print_success "App runner completed successfully!"
}

# Parse command line arguments
if [[ $# -eq 0 ]]; then
    show_usage
    exit 0
fi

main "$@" 