#!/usr/bin/env python3
"""Download Roboto fonts for the application"""

import os
import urllib.request
import urllib.error

def download_font(url, filename):
    """Download a font file"""
    try:
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, filename)
        print(f"✓ Downloaded {filename}")
        return True
    except urllib.error.URLError as e:
        print(f"✗ Failed to download {filename}: {e}")
        return False

def main():
    """Download Roboto font files"""
    fonts_dir = "resources/fonts"
    
    # Ensure fonts directory exists
    os.makedirs(fonts_dir, exist_ok=True)
    
    # Roboto font URLs (Google Fonts)
    fonts = {
        "Roboto-Regular.ttf": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf",
        "Roboto-Bold.ttf": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf",
        "Roboto-Light.ttf": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Light.ttf",
        "Roboto-Medium.ttf": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Medium.ttf"
    }
    
    success_count = 0
    for filename, url in fonts.items():
        filepath = os.path.join(fonts_dir, filename)
        if download_font(url, filepath):
            success_count += 1
    
    print(f"\nDownloaded {success_count}/{len(fonts)} font files")
    
    if success_count == len(fonts):
        print("✓ All fonts downloaded successfully!")
    else:
        print("⚠ Some fonts failed to download")

if __name__ == "__main__":
    main() 