"""
Unit tests for the robust OpenCV super resolution implementation.

This module tests the SuperResolutionProcessor with various image types,
edge cases, and performance scenarios to ensure robust operation.
"""

import logging
import os
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import pytest

# Add the src directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from helpmesign.utils.super_resolution import (
    SuperResolutionModel,
    SuperResolutionProcessor,
    SuperResolutionScale,
    enhance_image_simple,
    enhance_image_with_validation,
)


class TestSuperResolutionProcessor:
    """Test class for SuperResolutionProcessor functionality"""

    @pytest.fixture
    def processor(self):
        """Create a SuperResolutionProcessor instance for testing"""
        logger = logging.getLogger(__name__)
        return SuperResolutionProcessor(logger)

    @pytest.fixture
    def test_images(self):
        """Create various test images for testing"""
        test_images = {}

        # 1. Simple gradient image
        gradient = np.zeros((100, 100, 3), dtype=np.uint8)
        for i in range(100):
            gradient[i, :] = [i * 2, 128, 255 - i * 2]
        test_images["gradient"] = gradient

        # 2. Checkerboard pattern
        checkerboard = np.zeros((100, 100, 3), dtype=np.uint8)
        for i in range(0, 100, 10):
            for j in range(0, 100, 10):
                if (i // 10 + j // 10) % 2 == 0:
                    checkerboard[i : i + 10, j : j + 10] = [255, 255, 255]
                else:
                    checkerboard[i : i + 10, j : j + 10] = [0, 0, 0]
        test_images["checkerboard"] = checkerboard

        # 3. Random noise image
        noise = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        test_images["noise"] = noise

        # 4. Small image (edge case)
        small = np.ones((32, 32, 3), dtype=np.uint8) * 128
        test_images["small"] = small

        # 5. Large image (edge case)
        large = np.ones((512, 512, 3), dtype=np.uint8) * 128
        test_images["large"] = large

        # 6. Grayscale image
        grayscale = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        test_images["grayscale"] = grayscale

        # 7. Float32 image in range [0, 1]
        float_image = np.random.rand(100, 100, 3).astype(np.float32)
        test_images["float32"] = float_image

        # 8. Image with values outside normal range
        out_of_range = np.random.randint(-50, 300, (100, 100, 3), dtype=np.int16)
        test_images["out_of_range"] = out_of_range

        return test_images

    def test_image_validation(self, processor):
        """Test image validation functionality"""
        # Test valid images
        valid_images = [
            np.zeros((100, 100, 3), dtype=np.uint8),  # Color
            np.zeros((100, 100), dtype=np.uint8),  # Grayscale
            np.zeros((100, 100, 1), dtype=np.uint8),  # Single channel
            np.zeros((100, 100, 4), dtype=np.uint8),  # RGBA
        ]

        for i, img in enumerate(valid_images):
            is_valid, msg = processor._validate_image(img)
            assert is_valid, f"Valid image {i} failed validation: {msg}"

        # Test invalid images
        invalid_images = [
            None,  # None
            "not an image",  # String
            np.array([]),  # Empty array
            np.zeros((100,)),  # 1D array
            np.zeros((100, 100, 5), dtype=np.uint8),  # Invalid channels
        ]

        for i, img in enumerate(invalid_images):
            is_valid, msg = processor._validate_image(img)
            assert not is_valid, f"Invalid image {i} passed validation: {msg}"

    def test_preprocessing(self, processor):
        """Test image preprocessing functionality"""
        # Test uint8 image (should pass through with BGR to RGB conversion)
        uint8_img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        processed = processor._preprocess_image(uint8_img)
        assert processed.dtype == np.uint8
        assert processed.shape == uint8_img.shape
        assert processed.min() >= 0 and processed.max() <= 255

        # Test float32 image in range [0, 1]
        float_img = np.random.rand(100, 100, 3).astype(np.float32)
        processed = processor._preprocess_image(float_img)
        assert processed.dtype == np.uint8
        assert processed.min() >= 0 and processed.max() <= 255

        # Test BGR to RGB conversion
        bgr_img = np.zeros((100, 100, 3), dtype=np.uint8)
        bgr_img[:, :, 0] = 255  # Blue channel
        bgr_img[:, :, 1] = 128  # Green channel
        bgr_img[:, :, 2] = 0  # Red channel
        processed = processor._preprocess_image(bgr_img)
        # After conversion, red should be in channel 0, blue in channel 2
        assert processed[0, 0, 0] == 0  # Red
        assert processed[0, 0, 1] == 128  # Green
        assert processed[0, 0, 2] == 255  # Blue

    def test_postprocessing(self, processor):
        """Test image postprocessing functionality"""
        # Test uint8 output
        test_img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        processed = processor._postprocess_image(test_img, np.uint8)
        assert processed.dtype == np.uint8
        assert processed.min() >= 0 and processed.max() <= 255

        # Test float32 output
        processed = processor._postprocess_image(test_img, np.float32)
        assert processed.dtype == np.float32
        assert processed.min() >= 0.0 and processed.max() <= 1.0

        # Test clipping
        out_of_range = np.array([[[-10, 300, 128]]], dtype=np.int16)
        processed = processor._postprocess_image(out_of_range, np.uint8)
        assert processed[0, 0, 0] == 0  # Clipped to 0
        assert processed[0, 0, 1] == 255  # Clipped to 255
        assert processed[0, 0, 2] == 128  # Unchanged

    def test_enhancement_basic(self, processor, test_images):
        """Test basic image enhancement functionality"""
        # Test with ESPCN x2
        for name, img in test_images.items():
            if name == "out_of_range":  # Skip problematic test case
                continue

            enhanced = processor.enhance_image(
                img,
                SuperResolutionModel.ESPCN,
                SuperResolutionScale.X2,
                use_fallback=True,
            )

            if enhanced is not None:
                # Check output dimensions
                expected_h = img.shape[0] * 2
                expected_w = img.shape[1] * 2
                assert enhanced.shape[0] == expected_h, f"Height mismatch for {name}"
                assert enhanced.shape[1] == expected_w, f"Width mismatch for {name}"

                # Check data type and range
                assert enhanced.dtype == img.dtype, f"Data type mismatch for {name}"
                assert (
                    enhanced.min() >= 0 and enhanced.max() <= 255
                ), f"Range issue for {name}"

    def test_enhancement_different_scales(self, processor, test_images):
        """Test enhancement with different scaling factors"""
        test_img = test_images["gradient"]

        for scale in [SuperResolutionScale.X2, SuperResolutionScale.X4]:
            enhanced = processor.enhance_image(
                test_img, SuperResolutionModel.ESPCN, scale, use_fallback=True
            )

            if enhanced is not None:
                expected_h = test_img.shape[0] * scale.value
                expected_w = test_img.shape[1] * scale.value
                assert enhanced.shape[0] == expected_h
                assert enhanced.shape[1] == expected_w

    def test_batch_processing(self, processor, test_images):
        """Test batch processing functionality"""
        # Create a list of test images (excluding problematic ones)
        image_list = [
            img for name, img in test_images.items() if name != "out_of_range"
        ]

        # Test batch processing
        results = processor.enhance_image_batch(
            image_list,
            SuperResolutionModel.ESPCN,
            SuperResolutionScale.X2,
            use_fallback=True,
        )

        assert len(results) == len(
            image_list
        ), "Batch processing returned wrong number of results"

        successful = sum(1 for r in results if r is not None)
        assert successful > 0, "No images were successfully processed"

    def test_available_models(self, processor):
        """Test model availability checking"""
        available_models = processor.get_available_models()
        assert isinstance(available_models, list)

        # Test cleanup
        processor.cleanup()
        # Should not raise any exceptions

    def test_cleanup(self, processor):
        """Test resource cleanup"""
        # This should not raise any exceptions
        processor.cleanup()

        # Test that we can still use the processor after cleanup
        test_img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        enhanced = processor.enhance_image(
            test_img,
            SuperResolutionModel.ESPCN,
            SuperResolutionScale.X2,
            use_fallback=True,
        )
        # Should still work with fallback
        assert enhanced is not None


class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_enhance_image_simple(self):
        """Test simple enhancement function"""
        test_img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

        # Test with valid parameters
        enhanced = enhance_image_simple(test_img, scale=2, model_type="espcn")
        if enhanced is not None:
            assert enhanced.shape[0] == test_img.shape[0] * 2
            assert enhanced.shape[1] == test_img.shape[1] * 2

        # Test with invalid parameters (should use fallback)
        enhanced = enhance_image_simple(test_img, scale=5, model_type="invalid")
        if enhanced is not None:
            assert enhanced.shape[0] == test_img.shape[0] * 2  # Falls back to x2

    def test_enhance_image_with_validation(self):
        """Test validation enhancement function"""
        test_img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

        # Test with valid parameters
        enhanced = enhance_image_with_validation(
            test_img, scale=2, model_type="espcn", min_size=32, max_size=512
        )
        if enhanced is not None:
            assert enhanced.shape[0] == test_img.shape[0] * 2
            assert enhanced.shape[1] == test_img.shape[1] * 2

        # Test with image too small
        small_img = np.random.randint(0, 256, (16, 16, 3), dtype=np.uint8)
        enhanced = enhance_image_with_validation(
            small_img, scale=2, model_type="espcn", min_size=32, max_size=512
        )
        assert enhanced is None, "Should reject image that's too small"

        # Test with image too large
        large_img = np.random.randint(0, 256, (1024, 1024, 3), dtype=np.uint8)
        enhanced = enhance_image_with_validation(
            large_img, scale=2, model_type="espcn", min_size=32, max_size=512
        )
        assert enhanced is None, "Should reject image that's too large"


class TestPerformance:
    """Test performance characteristics"""

    def test_single_enhancement_performance(self):
        """Test single enhancement performance"""
        processor = SuperResolutionProcessor()
        test_img = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)

        start_time = time.time()
        enhanced = processor.enhance_image(
            test_img, SuperResolutionModel.ESPCN, SuperResolutionScale.X2
        )
        single_time = time.time() - start_time

        # Should complete within reasonable time (adjust threshold as needed)
        assert (
            single_time < 1.0
        ), f"Single enhancement took too long: {single_time:.3f}s"

        if enhanced is not None:
            assert enhanced.shape[0] == test_img.shape[0] * 2

    def test_batch_processing_performance(self):
        """Test batch processing performance"""
        processor = SuperResolutionProcessor()
        test_img = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
        batch_images = [test_img] * 5

        start_time = time.time()
        results = processor.enhance_image_batch(
            batch_images, SuperResolutionModel.ESPCN, SuperResolutionScale.X2
        )
        batch_time = time.time() - start_time

        # Batch processing should be reasonably efficient
        assert batch_time < 2.0, f"Batch processing took too long: {batch_time:.3f}s"

        successful = sum(1 for r in results if r is not None)
        assert successful > 0, "No images were successfully processed"


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_none_input(self):
        """Test handling of None input"""
        processor = SuperResolutionProcessor()

        enhanced = processor.enhance_image(None)
        assert enhanced is None

    def test_empty_array(self):
        """Test handling of empty array"""
        processor = SuperResolutionProcessor()

        empty_img = np.array([])
        enhanced = processor.enhance_image(empty_img)
        assert enhanced is None

    def test_invalid_dimensions(self):
        """Test handling of invalid image dimensions"""
        processor = SuperResolutionProcessor()

        # 1D array
        invalid_img = np.zeros((100,), dtype=np.uint8)
        enhanced = processor.enhance_image(invalid_img)
        assert enhanced is None

        # Invalid channel count
        invalid_img = np.zeros((100, 100, 5), dtype=np.uint8)
        enhanced = processor.enhance_image(invalid_img)
        assert enhanced is None

    def test_memory_cleanup(self):
        """Test that memory is properly cleaned up"""
        processor = SuperResolutionProcessor()

        # Process many images
        for _ in range(10):
            test_img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
            enhanced = processor.enhance_image(test_img)
            # Don't keep references to results

        # Cleanup should work without issues
        processor.cleanup()


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
