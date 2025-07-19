#!/bin/bash

# 🎨 Help Me Sign - Icon Generation Script
# Generates app icons for all platforms from a source image

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}📱 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if ImageMagick is installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v magick &> /dev/null; then
        print_error "ImageMagick is not installed. Please install it first:"
        echo "  macOS: brew install imagemagick"
        echo "  Ubuntu: sudo apt-get install imagemagick"
        echo "  Windows: Download from https://imagemagick.org/"
        exit 1
    fi
    
    print_success "ImageMagick v7 found (using magick command)"
}

# Create directories
create_directories() {
    print_status "Creating icon directories..."
    
    # Android directories
    mkdir -p android/app/src/main/res/mipmap-mdpi
    mkdir -p android/app/src/main/res/mipmap-hdpi
    mkdir -p android/app/src/main/res/mipmap-xhdpi
    mkdir -p android/app/src/main/res/mipmap-xxhdpi
    mkdir -p android/app/src/main/res/mipmap-xxxhdpi
    
    # iOS directories
    mkdir -p ios/Runner/Assets.xcassets/AppIcon.appiconset
    
    # macOS directories
    mkdir -p macos/Runner/Assets.xcassets/AppIcon.appiconset
    
    # Web directory
    mkdir -p web/icons
    
    # Windows directory
    mkdir -p windows/runner/resources
    
    print_success "Directories created"
}

# Generate Android icons
generate_android_icons() {
    print_status "Generating Android icons..."
    
    # Android icon sizes
    magick assets/icons/source_icon.png -resize 48x48 android/app/src/main/res/mipmap-mdpi/ic_launcher.png
    magick assets/icons/source_icon.png -resize 72x72 android/app/src/main/res/mipmap-hdpi/ic_launcher.png
    magick assets/icons/source_icon.png -resize 96x96 android/app/src/main/res/mipmap-xhdpi/ic_launcher.png
    magick assets/icons/source_icon.png -resize 144x144 android/app/src/main/res/mipmap-xxhdpi/ic_launcher.png
    magick assets/icons/source_icon.png -resize 192x192 android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png
    
    # Adaptive icons (Android 8.0+)
    magick assets/icons/source_icon.png -resize 108x108 android/app/src/main/res/mipmap-mdpi/ic_launcher_foreground.png
    magick assets/icons/source_icon.png -resize 162x162 android/app/src/main/res/mipmap-hdpi/ic_launcher_foreground.png
    magick assets/icons/source_icon.png -resize 216x216 android/app/src/main/res/mipmap-xhdpi/ic_launcher_foreground.png
    magick assets/icons/source_icon.png -resize 324x324 android/app/src/main/res/mipmap-xxhdpi/ic_launcher_foreground.png
    magick assets/icons/source_icon.png -resize 432x432 android/app/src/main/res/mipmap-xxxhdpi/ic_launcher_foreground.png
    
    print_success "Android icons generated"
}

# Generate iOS icons
generate_ios_icons() {
    print_status "Generating iOS icons..."
    
    # iOS icon sizes
    magick assets/icons/source_icon.png -resize 20x20 ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-20x20@1x.png
    magick assets/icons/source_icon.png -resize 40x40 ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-20x20@2x.png
    magick assets/icons/source_icon.png -resize 60x60 ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-20x20@3x.png
    magick assets/icons/source_icon.png -resize 29x29 ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-29x29@1x.png
    magick assets/icons/source_icon.png -resize 58x58 ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-29x29@2x.png
    magick assets/icons/source_icon.png -resize 87x87 ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-29x29@3x.png
    magick assets/icons/source_icon.png -resize 40x40 ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-40x40@1x.png
    magick assets/icons/source_icon.png -resize 80x80 ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-40x40@2x.png
    magick assets/icons/source_icon.png -resize 120x120 ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-40x40@3x.png
    magick assets/icons/source_icon.png -resize 120x120 ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-60x60@2x.png
    magick assets/icons/source_icon.png -resize 180x180 ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-60x60@3x.png
    magick assets/icons/source_icon.png -resize 76x76 ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-76x76@1x.png
    magick assets/icons/source_icon.png -resize 152x152 ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-76x76@2x.png
    magick assets/icons/source_icon.png -resize 167x167 ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-83.5x83.5@2x.png
    magick assets/icons/source_icon.png -resize 1024x1024 ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-1024x1024@1x.png
    
    print_success "iOS icons generated"
}

# Generate macOS icons (Universal App Support)
generate_macos_icons() {
    print_status "Generating macOS icons (Universal App Support)..."
    
    # macOS icon sizes for universal app
    magick assets/icons/source_icon.png -resize 16x16 macos/Runner/Assets.xcassets/AppIcon.appiconset/icon_16x16.png
    magick assets/icons/source_icon.png -resize 32x32 macos/Runner/Assets.xcassets/AppIcon.appiconset/icon_16x16@2x.png
    magick assets/icons/source_icon.png -resize 32x32 macos/Runner/Assets.xcassets/AppIcon.appiconset/icon_32x32.png
    magick assets/icons/source_icon.png -resize 64x64 macos/Runner/Assets.xcassets/AppIcon.appiconset/icon_32x32@2x.png
    magick assets/icons/source_icon.png -resize 128x128 macos/Runner/Assets.xcassets/AppIcon.appiconset/icon_128x128.png
    magick assets/icons/source_icon.png -resize 256x256 macos/Runner/Assets.xcassets/AppIcon.appiconset/icon_128x128@2x.png
    magick assets/icons/source_icon.png -resize 256x256 macos/Runner/Assets.xcassets/AppIcon.appiconset/icon_256x256.png
    magick assets/icons/source_icon.png -resize 512x512 macos/Runner/Assets.xcassets/AppIcon.appiconset/icon_256x256@2x.png
    magick assets/icons/source_icon.png -resize 512x512 macos/Runner/Assets.xcassets/AppIcon.appiconset/icon_512x512.png
    magick assets/icons/source_icon.png -resize 1024x1024 macos/Runner/Assets.xcassets/AppIcon.appiconset/icon_512x512@2x.png
    
    print_success "macOS icons generated (Universal App Support)"
}

# Generate Web icons
generate_web_icons() {
    print_status "Generating Web icons..."
    
    # Web icon sizes
    magick assets/icons/source_icon.png -resize 192x192 web/icons/Icon-192.png
    magick assets/icons/source_icon.png -resize 512x512 web/icons/Icon-512.png
    magick assets/icons/source_icon.png -resize 16x16 web/icons/favicon.png
    magick assets/icons/source_icon.png -resize 32x32 web/icons/favicon-32x32.png
    magick assets/icons/source_icon.png -resize 16x16 web/icons/favicon-16x16.png
    magick assets/icons/source_icon.png -resize 180x180 web/icons/apple-touch-icon.png
    
    print_success "Web icons generated"
}

# Generate Windows icons
generate_windows_icons() {
    print_status "Generating Windows icons..."
    
    # Windows icon sizes
    magick assets/icons/source_icon.png -resize 16x16 windows/runner/resources/icon_16x16.png
    magick assets/icons/source_icon.png -resize 32x32 windows/runner/resources/icon_32x32.png
    magick assets/icons/source_icon.png -resize 48x48 windows/runner/resources/icon_48x48.png
    magick assets/icons/source_icon.png -resize 64x64 windows/runner/resources/icon_64x64.png
    magick assets/icons/source_icon.png -resize 128x128 windows/runner/resources/icon_128x128.png
    magick assets/icons/source_icon.png -resize 256x256 windows/runner/resources/icon_256x256.png
    
    print_success "Windows icons generated"
}

# Create macOS Contents.json
create_macos_contents_json() {
    print_status "Creating macOS Contents.json..."
    
    cat > macos/Runner/Assets.xcassets/AppIcon.appiconset/Contents.json << 'EOF'
{
  "images" : [
    {
      "filename" : "icon_16x16.png",
      "idiom" : "mac",
      "scale" : "1x",
      "size" : "16x16"
    },
    {
      "filename" : "icon_16x16@2x.png",
      "idiom" : "mac",
      "scale" : "2x",
      "size" : "16x16"
    },
    {
      "filename" : "icon_32x32.png",
      "idiom" : "mac",
      "scale" : "1x",
      "size" : "32x32"
    },
    {
      "filename" : "icon_32x32@2x.png",
      "idiom" : "mac",
      "scale" : "2x",
      "size" : "32x32"
    },
    {
      "filename" : "icon_128x128.png",
      "idiom" : "mac",
      "scale" : "1x",
      "size" : "128x128"
    },
    {
      "filename" : "icon_128x128@2x.png",
      "idiom" : "mac",
      "scale" : "2x",
      "size" : "128x128"
    },
    {
      "filename" : "icon_256x256.png",
      "idiom" : "mac",
      "scale" : "1x",
      "size" : "256x256"
    },
    {
      "filename" : "icon_256x256@2x.png",
      "idiom" : "mac",
      "scale" : "2x",
      "size" : "256x256"
    },
    {
      "filename" : "icon_512x512.png",
      "idiom" : "mac",
      "scale" : "1x",
      "size" : "512x512"
    },
    {
      "filename" : "icon_512x512@2x.png",
      "idiom" : "mac",
      "scale" : "2x",
      "size" : "512x512"
    }
  ],
  "info" : {
    "author" : "xcode",
    "version" : 1
  }
}
EOF
    
    print_success "macOS Contents.json created"
}

# Create iOS Contents.json
create_ios_contents_json() {
    print_status "Creating iOS Contents.json..."
    
    cat > ios/Runner/Assets.xcassets/AppIcon.appiconset/Contents.json << 'EOF'
{
  "images" : [
    {
      "filename" : "Icon-App-20x20@1x.png",
      "idiom" : "iphone",
      "scale" : "1x",
      "size" : "20x20"
    },
    {
      "filename" : "Icon-App-20x20@2x.png",
      "idiom" : "iphone",
      "scale" : "2x",
      "size" : "20x20"
    },
    {
      "filename" : "Icon-App-20x20@3x.png",
      "idiom" : "iphone",
      "scale" : "3x",
      "size" : "20x20"
    },
    {
      "filename" : "Icon-App-29x29@1x.png",
      "idiom" : "iphone",
      "scale" : "1x",
      "size" : "29x29"
    },
    {
      "filename" : "Icon-App-29x29@2x.png",
      "idiom" : "iphone",
      "scale" : "2x",
      "size" : "29x29"
    },
    {
      "filename" : "Icon-App-29x29@3x.png",
      "idiom" : "iphone",
      "scale" : "3x",
      "size" : "29x29"
    },
    {
      "filename" : "Icon-App-40x40@1x.png",
      "idiom" : "iphone",
      "scale" : "1x",
      "size" : "40x40"
    },
    {
      "filename" : "Icon-App-40x40@2x.png",
      "idiom" : "iphone",
      "scale" : "2x",
      "size" : "40x40"
    },
    {
      "filename" : "Icon-App-40x40@3x.png",
      "idiom" : "iphone",
      "scale" : "3x",
      "scale" : "3x",
      "size" : "40x40"
    },
    {
      "filename" : "Icon-App-60x60@2x.png",
      "idiom" : "iphone",
      "scale" : "2x",
      "size" : "60x60"
    },
    {
      "filename" : "Icon-App-60x60@3x.png",
      "idiom" : "iphone",
      "scale" : "3x",
      "size" : "60x60"
    },
    {
      "filename" : "Icon-App-20x20@1x.png",
      "idiom" : "ipad",
      "scale" : "1x",
      "size" : "20x20"
    },
    {
      "filename" : "Icon-App-20x20@2x.png",
      "idiom" : "ipad",
      "scale" : "2x",
      "size" : "20x20"
    },
    {
      "filename" : "Icon-App-29x29@1x.png",
      "idiom" : "ipad",
      "scale" : "1x",
      "size" : "29x29"
    },
    {
      "filename" : "Icon-App-29x29@2x.png",
      "idiom" : "ipad",
      "scale" : "2x",
      "size" : "29x29"
    },
    {
      "filename" : "Icon-App-40x40@1x.png",
      "idiom" : "ipad",
      "scale" : "1x",
      "size" : "40x40"
    },
    {
      "filename" : "Icon-App-40x40@2x.png",
      "idiom" : "ipad",
      "scale" : "2x",
      "size" : "40x40"
    },
    {
      "filename" : "Icon-App-76x76@1x.png",
      "idiom" : "ipad",
      "scale" : "1x",
      "size" : "76x76"
    },
    {
      "filename" : "Icon-App-76x76@2x.png",
      "idiom" : "ipad",
      "scale" : "2x",
      "size" : "76x76"
    },
    {
      "filename" : "Icon-App-83.5x83.5@2x.png",
      "idiom" : "ipad",
      "scale" : "2x",
      "size" : "83.5x83.5"
    },
    {
      "filename" : "Icon-App-1024x1024@1x.png",
      "idiom" : "ios-marketing",
      "scale" : "1x",
      "size" : "1024x1024"
    }
  ],
  "info" : {
    "author" : "xcode",
    "version" : 1
  }
}
EOF
    
    print_success "iOS Contents.json created"
}

# Update web manifest
update_web_manifest() {
    print_status "Updating web manifest..."
    
    cat > web/manifest.json << 'EOF'
{
    "name": "Help Me Sign",
    "short_name": "HelpMeSign",
    "start_url": ".",
    "display": "standalone",
    "background_color": "#0175C2",
    "theme_color": "#0175C2",
    "description": "A cross-platform Flutter application that uses real-time camera processing and machine learning to recognize hand gestures and respond with animated hand gestures.",
    "orientation": "portrait-primary",
    "prefer_related_applications": false,
    "icons": [
        {
            "src": "icons/Icon-192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "icons/Icon-512.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ]
}
EOF
    
    print_success "Web manifest updated"
}

# Update web index.html
update_web_index() {
    print_status "Updating web index.html..."
    
    # Add favicon and icon links to web/index.html
    sed -i '' '/<title>/a\
    <link rel="icon" type="image/png" sizes="32x32" href="icons/favicon-32x32.png">\
    <link rel="icon" type="image/png" sizes="16x16" href="icons/favicon-16x16.png">\
    <link rel="apple-touch-icon" sizes="180x180" href="icons/apple-touch-icon.png">\
    <link rel="manifest" href="manifest.json">' web/index.html
    
    print_success "Web index.html updated"
}

# Main execution
main() {
    echo "🎨 Help Me Sign - Icon Generation Script"
    echo "========================================"
    
    # Check if source icon exists
    if [ ! -f "assets/icons/source_icon.png" ]; then
        print_error "Source icon not found at assets/icons/source_icon.png"
        echo "Please place your source icon (OK gesture) at assets/icons/source_icon.png"
        echo "The icon should be at least 1024x1024 pixels for best results."
        exit 1
    fi
    
    check_dependencies
    create_directories
    
    generate_android_icons
    generate_ios_icons
    generate_macos_icons
    generate_web_icons
    generate_windows_icons
    
    create_macos_contents_json
    create_ios_contents_json
    update_web_manifest
    update_web_index
    
    echo ""
    print_success "🎉 All icons generated successfully!"
    echo ""
    echo "📱 Platform Support:"
    echo "  ✅ Android (All densities)"
    echo "  ✅ iOS (iPhone & iPad)"
    echo "  ✅ macOS (Universal App - Intel + Apple Silicon)"
    echo "  ✅ Web (PWA support)"
    echo "  ✅ Windows"
    echo ""
    echo "🚀 Next Steps:"
    echo "  1. Place your source icon at: assets/icons/source_icon.png"
    echo "  2. Run: chmod +x scripts/generate_icons.sh"
    echo "  3. Run: ./scripts/generate_icons.sh"
    echo "  4. Build your app: flutter build [platform]"
    echo ""
    echo "💡 For universal macOS app:"
    echo "  flutter build macos --release"
    echo "  This will create a universal binary supporting both Intel and Apple Silicon"
}

# Run main function
main "$@" 