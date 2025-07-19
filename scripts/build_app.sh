#!/bin/bash

# Help Me Sign - App Builder
# This script builds the Help Me Sign app for all platforms for distribution

set -e

echo "🏗️  Help Me Sign - App Builder"
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
    echo "Usage: $0 [platform] [build_type]"
    echo ""
    echo "Platforms:"
    echo "  ios          - Build iOS app (.ipa)"
    echo "  android      - Build Android app (.apk/.aab)"
    echo "  web          - Build web app (deployable files)"
    echo "  macos        - Build macOS app (.app)"
    echo "  windows      - Build Windows app (.exe)"
    echo "  linux        - Build Linux app (executable)"
    echo "  all          - Build for all platforms"
    echo ""
    echo "Build Types:"
    echo "  debug        - Debug build (default)"
    echo "  release      - Release build"
    echo "  profile      - Profile build"
    echo ""
    echo "Examples:"
    echo "  $0 ios release              # Build iOS app in release mode"
    echo "  $0 android debug            # Build Android app in debug mode"
    echo "  $0 web release              # Build web app for production"
    echo "  $0 all release              # Build all platforms in release mode"
    echo ""
    echo "Additional Options:"
    echo "  --help, -h                  - Show this help message"
    echo "  --version, -v               - Show version information"
    echo "  --list-platforms, -l        - List available platforms"
    echo "  --check-dependencies, -c    - Check platform dependencies"
    echo "  --clean, --clean-build      - Clean build before building"
}

# Function to show version
show_version() {
    echo "Help Me Sign - App Builder v1.0.0"
    echo "Cross-platform Flutter app builder"
    echo "Supports: iOS, Android, Web, macOS, Windows, Linux"
}

# Function to list platforms
list_platforms() {
    echo "Available Build Platforms:"
    echo ""
    echo "🍎 iOS"
    echo "   • Output: .ipa file"
    echo "   • Requires: macOS, Xcode, iOS Simulator"
    echo "   • Command: flutter build ios"
    echo ""
    echo "🤖 Android"
    echo "   • Output: .apk or .aab file"
    echo "   • Requires: Android SDK, ADB"
    echo "   • Command: flutter build apk or flutter build appbundle"
    echo ""
    echo "🌐 Web"
    echo "   • Output: deployable web files"
    echo "   • Requires: Flutter web support"
    echo "   • Command: flutter build web"
    echo ""
    echo "🍎 macOS"
    echo "   • Output: .app bundle"
    echo "   • Requires: macOS, Xcode"
    echo "   • Command: flutter build macos"
    echo ""
    echo "🪟 Windows"
    echo "   • Output: .exe file"
    echo "   • Requires: Windows, Visual Studio Build Tools"
    echo "   • Command: flutter build windows"
    echo ""
    echo "🐧 Linux"
    echo "   • Output: executable file"
    echo "   • Requires: Linux, development tools"
    echo "   • Command: flutter build linux"
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

# Function to build Flutter command
build_flutter_command() {
    local platform="$1"
    local build_type="$2"
    
    local command="flutter build"
    
    # Add platform
    command="$command $platform"
    
    # Add build type
    case "$build_type" in
        "debug")
            command="$command --debug"
            ;;
        "release")
            command="$command --release"
            ;;
        "profile")
            command="$command --profile"
            ;;
    esac
    
    # Add platform-specific flags
    case "$platform" in
        "android")
            # Build both APK and App Bundle
            echo "flutter build apk --$build_type"
            echo "flutter build appbundle --$build_type"
            return
            ;;
        "web")
            command="$command --web-renderer html"
            ;;
    esac
    
    echo "$command"
}

# Function to build app for specific platform
build_app_platform() {
    local platform="$1"
    local build_type="$2"
    local platform_name="$3"
    
    if check_platform_availability "$platform"; then
        print_status "Building $platform_name app in $build_type mode..."
        
        # Build command
        local commands=$(build_flutter_command "$platform" "$build_type")
        
        # Execute commands
        local success=true
        while IFS= read -r command; do
            if [[ -n "$command" ]]; then
                print_status "Executing: $command"
                if eval "$command"; then
                    print_success "Command completed: $command"
                else
                    print_error "Command failed: $command"
                    success=false
                fi
            fi
        done <<< "$commands"
        
        if $success; then
            print_success "$platform_name app built successfully"
            return 0
        else
            print_error "$platform_name app build failed"
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
        else
            print_warning "$platform_name: Not Available"
        fi
    done
}

# Function to clean build
clean_build() {
    print_status "Cleaning build..."
    if flutter clean; then
        print_success "Build cleaned successfully"
    else
        print_error "Failed to clean build"
        exit 1
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

# Function to build app for all platforms
build_app_all_platforms() {
    local build_type="$1"
    local start_time=$(date +%s)
    local total_platforms=0
    local successful_platforms=0
    
    print_status "Building app for all available platforms..."
    
    local platforms=("ios" "android" "web" "macos" "windows" "linux")
    local platform_names=("iOS" "Android" "Web" "macOS" "Windows" "Linux")
    
    for i in "${!platforms[@]}"; do
        local platform="${platforms[$i]}"
        local platform_name="${platform_names[$i]}"
        
        print_status "Building $platform_name app..."
        
        if build_app_platform "$platform" "$build_type" "$platform_name"; then
            successful_platforms=$((successful_platforms + 1))
        fi
        
        total_platforms=$((total_platforms + 1))
        echo ""
    done
    
    # Calculate total time
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    print_success "App building completed in ${duration} seconds"
    
    # Generate summary
    echo ""
    echo "🏗️  App Build Summary"
    echo "===================="
    echo "✅ Successful Platforms: $successful_platforms/$total_platforms"
    echo "⏱️  Total Time: ${duration} seconds"
    echo "🎯 Build Type: $build_type"
    echo ""
    
    if [ $successful_platforms -eq $total_platforms ]; then
        print_success "All platforms built successfully!"
    else
        print_warning "Some platforms failed to build. Check the logs above."
    fi
}

# Function to show build outputs
show_build_outputs() {
    print_status "Build outputs:"
    echo ""
    
    # Check for build outputs
    if [[ -d "build/ios/archive" ]]; then
        print_success "iOS: build/ios/archive/"
    fi
    
    if [[ -d "build/app/outputs/flutter-apk" ]]; then
        print_success "Android APK: build/app/outputs/flutter-apk/"
    fi
    
    if [[ -d "build/app/outputs/bundle" ]]; then
        print_success "Android Bundle: build/app/outputs/bundle/"
    fi
    
    if [[ -d "build/web" ]]; then
        print_success "Web: build/web/"
    fi
    
    if [[ -d "build/macos/Build/Products/Release" ]]; then
        print_success "macOS: build/macos/Build/Products/Release/"
    fi
    
    if [[ -d "build/windows/runner/Release" ]]; then
        print_success "Windows: build/windows/runner/Release/"
    fi
    
    if [[ -d "build/linux/x64/release/bundle" ]]; then
        print_success "Linux: build/linux/x64/release/bundle/"
    fi
}

# Main execution
main() {
    local platform="$1"
    local build_type="${2:-debug}"
    local clean_build_flag="$3"
    
    # Check prerequisites
    check_flutter
    
    # Handle special commands
    case "$platform" in
        "--help"|"-h")
            show_usage
            exit 0
            ;;
        "--version"|"-v")
            show_version
            exit 0
            ;;
        "--list-platforms"|"-l")
            list_platforms
            exit 0
            ;;
        "--check-dependencies"|"-c")
            check_dependencies
            exit 0
            ;;
    esac
    
    # Validate platform
    case "$platform" in
        "ios"|"android"|"web"|"macos"|"windows"|"linux"|"all")
            # Valid platform
            ;;
        "")
            print_error "No platform specified"
            show_usage
            exit 1
            ;;
        *)
            print_error "Unknown platform: $platform"
            print_error "Use --list-platforms to see available options"
            exit 1
            ;;
    esac
    
    # Validate build type
    case "$build_type" in
        "debug"|"release"|"profile")
            # Valid build type
            ;;
        *)
            print_error "Unknown build type: $build_type"
            show_usage
            exit 1
            ;;
    esac
    
    # Clean build if requested
    if [[ "$clean_build_flag" == "--clean" ]] || [[ "$clean_build_flag" == "--clean-build" ]]; then
        clean_build
    fi
    
    # Get dependencies
    get_dependencies
    
    # Build the app
    print_status "Starting app build..."
    print_status "Platform: $platform"
    print_status "Build Type: $build_type"
    echo ""
    
    if [[ "$platform" == "all" ]]; then
        build_app_all_platforms "$build_type"
    else
        local platform_names=("iOS" "Android" "Web" "macOS" "Windows" "Linux")
        local platform_index=0
        
        case "$platform" in
            "ios") platform_index=0 ;;
            "android") platform_index=1 ;;
            "web") platform_index=2 ;;
            "macos") platform_index=3 ;;
            "windows") platform_index=4 ;;
            "linux") platform_index=5 ;;
        esac
        
        build_app_platform "$platform" "$build_type" "${platform_names[$platform_index]}"
    fi
    
    # Show build outputs
    show_build_outputs
    
    print_success "App builder completed successfully!"
}

# Parse command line arguments
if [[ $# -eq 0 ]]; then
    show_usage
    exit 0
fi

main "$@" 