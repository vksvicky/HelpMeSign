#!/usr/bin/env python3
"""
Simple CI import test - one-liner version
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from helpmesign import get_app
    app = get_app()
    if app is None:
        print("✅ Safe import working - PySide6 not available (expected in CI)")
    else:
        print("✅ Safe import working - PySide6 available")
    sys.exit(0)
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1) 