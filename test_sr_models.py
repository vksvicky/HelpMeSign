#!/usr/bin/env python3
"""
Test script to verify OpenCV Super Resolution models are working correctly
Based on the tutorial from https://jeanvitor.com/how-use-opencv-superresolution-sr/
"""

import cv2
import numpy as np
import time
from pathlib import Path

def test_super_resolution_models():
    """Test all available super resolution models"""
    
    # Model paths
    models_dir = Path("resources/models/super_resolution")
    
    # Test models
    test_models = [
        ("EDSR", "EDSR_x4.pb", 4),
        ("EDSR", "EDSR_x2.pb", 2),
    ]
    
    # Create a test image (simple pattern)
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    test_image[25:75, 25:75] = [255, 255, 255]  # White square
    test_image[40:60, 40:60] = [0, 0, 0]        # Black square inside
    
    print("Testing Super Resolution Models")
    print("=" * 50)
    print(f"Input image shape: {test_image.shape}")
    
    for model_name, model_file, scale in test_models:
        model_path = models_dir / model_file
        
        if not model_path.exists():
            print(f"❌ {model_name} x{scale}: Model file not found at {model_path}")
            continue
            
        try:
            # Create super resolution model
            sr_model = cv2.dnn_superres.DnnSuperResImpl_create()
            sr_model.readModel(str(model_path))
            sr_model.setModel(model_name.lower(), scale)
            
            # Test the model
            start_time = time.time()
            upsampled = sr_model.upsample(test_image)
            end_time = time.time()
            
            print(f"✅ {model_name} x{scale}: {test_image.shape} -> {upsampled.shape} ({end_time - start_time:.3f}s)")
            
        except Exception as e:
            print(f"❌ {model_name} x{scale}: Error - {e}")
    
    print("\nTesting fallback interpolation...")
    
    # Test fallback interpolation
    start_time = time.time()
    fallback_result = cv2.resize(test_image, (400, 400), interpolation=cv2.INTER_LANCZOS4)
    end_time = time.time()
    
    print(f"✅ Fallback LANCZOS4: {test_image.shape} -> {fallback_result.shape} ({end_time - start_time:.3f}s)")

if __name__ == "__main__":
    test_super_resolution_models()
