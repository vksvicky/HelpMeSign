#!/usr/bin/env python3
"""
Simple debug script to test color conversion issues
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import cv2
import numpy as np
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication

def test_color_conversion():
    """Test color conversion between Qt and OpenCV"""
    
    # Create a simple test image with known colors
    # Red square in top-left, Green in top-right, Blue in bottom-left
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    test_image[0:50, 0:50] = [255, 0, 0]    # Red (RGB)
    test_image[0:50, 50:100] = [0, 255, 0]  # Green (RGB)
    test_image[50:100, 0:50] = [0, 0, 255]  # Blue (RGB)
    
    print("Original RGB image:")
    print(f"Red pixel (0,0): {test_image[0,0]}")
    print(f"Green pixel (0,50): {test_image[0,50]}")
    print(f"Blue pixel (50,0): {test_image[50,0]}")
    
    # Test 1: RGB -> QImage -> RGB interpretation
    print("\n=== Test 1: RGB -> QImage -> RGB interpretation ===")
    qimage_rgb = QImage(test_image.data, 100, 100, 300, QImage.Format_RGB888)
    pixmap_rgb = QPixmap.fromImage(qimage_rgb)
    
    # Convert back to numpy
    ptr = qimage_rgb.bits()
    if hasattr(ptr, 'setsize'):
        ptr.setsize(qimage_rgb.sizeInBytes() if hasattr(qimage_rgb, 'sizeInBytes') else qimage_rgb.byteCount())
    arr = np.array(ptr).reshape(100, 100, 3)
    
    print(f"Red pixel (0,0): {arr[0,0]}")
    print(f"Green pixel (0,50): {arr[0,50]}")
    print(f"Blue pixel (50,0): {arr[50,0]}")
    
    # Test 2: BGR -> QImage -> RGB interpretation
    print("\n=== Test 2: BGR -> QImage -> RGB interpretation ===")
    bgr_image = cv2.cvtColor(test_image, cv2.COLOR_RGB2BGR)
    print(f"BGR Red pixel (0,0): {bgr_image[0,0]}")
    print(f"BGR Green pixel (0,50): {bgr_image[0,50]}")
    print(f"BGR Blue pixel (50,0): {bgr_image[50,0]}")
    
    qimage_bgr = QImage(bgr_image.data, 100, 100, 300, QImage.Format_RGB888)
    pixmap_bgr = QPixmap.fromImage(qimage_bgr)
    
    # Convert back to numpy
    ptr = qimage_bgr.bits()
    if hasattr(ptr, 'setsize'):
        ptr.setsize(qimage_bgr.sizeInBytes() if hasattr(qimage_bgr, 'sizeInBytes') else qimage_bgr.byteCount())
    arr = np.array(ptr).reshape(100, 100, 3)
    
    print(f"Red pixel (0,0): {arr[0,0]}")
    print(f"Green pixel (0,50): {arr[0,50]}")
    print(f"Blue pixel (50,0): {arr[50,0]}")
    
    # Test 3: RGB -> QImage with BGR888 format
    print("\n=== Test 3: RGB -> QImage with BGR888 format ===")
    qimage_bgr888 = QImage(test_image.data, 100, 100, 300, QImage.Format_BGR888)
    pixmap_bgr888 = QPixmap.fromImage(qimage_bgr888)
    
    # Convert back to numpy
    ptr = qimage_bgr888.bits()
    if hasattr(ptr, 'setsize'):
        ptr.setsize(qimage_bgr888.sizeInBytes() if hasattr(qimage_bgr888, 'sizeInBytes') else qimage_bgr888.byteCount())
    arr = np.array(ptr).reshape(100, 100, 3)
    
    print(f"Red pixel (0,0): {arr[0,0]}")
    print(f"Green pixel (0,50): {arr[0,50]}")
    print(f"Blue pixel (50,0): {arr[50,0]}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    test_color_conversion()
    app.quit()