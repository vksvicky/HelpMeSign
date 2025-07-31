#!/usr/bin/env python3
"""Setup Roboto fonts for HelpMeSign"""

import os
import requests

def download_font(url, filename):
    """Download a font file"""
    try:
        print(f"Downloading {filename}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✓ Downloaded {filename}")
        return True
    except Exception as e:
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