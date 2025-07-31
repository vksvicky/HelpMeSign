#!/bin/bash

# HelpMeSign Launcher Script
# This script helps set the correct application name in the macOS menubar

clear

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set the application name
APP_NAME="HelpMeSign"

# On macOS, try to set the process name
if [[ "$OSTYPE" == "darwin"* ]]; then
        # Check if virtual environment exists and activate it first
        if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
            echo "Activating virtual environment..."
            source "$SCRIPT_DIR/venv/bin/activate"
            # Use the Python from virtual environment
            PYTHON_PATH="$VIRTUAL_ENV/bin/python"
        else
            # Find the Python executable (fallback)
            PYTHON_PATH=$(which python3)
            if [ -z "$PYTHON_PATH" ]; then
                PYTHON_PATH=$(which python)
            fi
        fi
        
        if [ -n "$PYTHON_PATH" ]; then
            echo "Using Python: $PYTHON_PATH"
            
            # Run the application directly with the virtual environment Python
            # Note: This will show "Python" in the menubar, but the app will work correctly
            # For the correct app name in menubar, build the app using: python3 scripts/build_macos_app.py
            "$PYTHON_PATH" "$SCRIPT_DIR/run_app.py" "$@"
        else
            echo "Error: Python not found"
            exit 1
        fi
else
    # On other platforms, just run normally
    # Check if virtual environment exists and activate it
    if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
        echo "Activating virtual environment..."
        source "$SCRIPT_DIR/venv/bin/activate"
        python "$SCRIPT_DIR/run_app.py" "$@"
    else
        python3 "$SCRIPT_DIR/run_app.py" "$@"
    fi
fi 