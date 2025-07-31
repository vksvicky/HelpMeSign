#!/usr/bin/env python3
"""
Application runner script for HelpMeSign
Provides command-line interface for running the application with various options
"""

import sys
import os
import argparse
import json
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from helpmesign.core.app import HelpMeSignApp, create_app
import tkinter as tk


def load_custom_config(config_path):
    """Load custom configuration from file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config from {config_path}: {e}")
        return None


def setup_environment():
    """Set up the environment for the application"""
    # Ensure resources directory exists
    resources_dir = Path("resources")
    if not resources_dir.exists():
        print("Creating resources directory...")
        resources_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (resources_dir / "images").mkdir(exist_ok=True)
        (resources_dir / "data").mkdir(exist_ok=True)
        
        # Create default config if it doesn't exist
        config_file = resources_dir / "data" / "config.json"
        if not config_file.exists():
            default_config = {
                "app_name": "HelpMeSign",
                "version": "1.0.0",
                "window_size": {
                    "width": 1024,
                    "height": 1024
                },
                "theme": {
                    "primary_color": "#3498db",
                    "secondary_color": "#2ecc71"
                },
                "settings": {
                    "auto_save": True,
                    "debug_mode": False
                }
            }
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            print("Created default configuration file")


def main():
    """Main entry point for the application runner"""
    parser = argparse.ArgumentParser(
        description="HelpMeSign Application Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run_app.py                    # Run normally
  python3 run_app.py --debug            # Run in debug mode
  python3 run_app.py --config my_config.json  # Use custom config
  python3 run_app.py --help             # Show this help
        """
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with verbose output'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom configuration file'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='HelpMeSign 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Set up environment
    setup_environment()
    
    if args.debug:
        print("🔍 Debug mode enabled")
        print(f"📁 Working directory: {os.getcwd()}")
        print(f"🐍 Python version: {sys.version}")
        print(f"📦 Resources directory: {Path('resources').absolute()}")
    
    # Load custom config if specified
    custom_config = None
    if args.config:
        custom_config = load_custom_config(args.config)
        if custom_config is None:
            print("❌ Failed to load custom config, using default")
    
    try:
        if args.debug:
            print("🚀 Starting HelpMeSign application...")
        
        # Create and run the application
        app = create_app()
        
        if args.debug:
            print("✅ Application created successfully")
            print("🖥️  Starting main loop...")
        
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 