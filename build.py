#!/usr/bin/env python3
"""
Convenience build script for HelpMeSign
Redirects to the appropriate build script in the scripts folder
"""

import sys
import os

# Add the scripts directory to the path
scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
sys.path.insert(0, scripts_dir)

# Import and run the universal build script
from build_all import main

if __name__ == "__main__":
    main() 