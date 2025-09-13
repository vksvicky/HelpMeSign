"""
Advanced Super Resolution utilities for HelpMeSign.
Supports Real-ESRGAN, SRCNN, and other high-quality upscaling methods.
"""

import os
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np

from .logger import get_logger


class SuperResolutionProcessor:
    """Advanced super resolution processor with multiple model support"""

    def __init__(self, logger: Optional[Any] = None) -> None:
        self.logger = logger or get_logger("helpmesign.utils.super_resolution")
        self._models: Dict[str, Any] = {}
        self._model_paths = self._get_model_paths()

    def _get_model_paths(self) -> Dict[str, str]:
        """Get paths to available super resolution models"""
        try:
            # Get the project root directory
            current_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(current_dir))
            )
            models_dir = os.path.join(
                project_root, "resources", "models", "super_resolution"
            )

            return {
                "esrgan": os.path.join(models_dir, "RealESRGAN_x4plus.pth"),
                "srcnn": os.path.join(models_dir, "SRCNN_x2.pb"),
                "espcn": os.path.join(models_dir, "ESPCN_x2.pb"),
                "edsr": os.path.join(models_dir, "EDSR_x2.pb"),
            }
        except Exception as e:
            self.logger.warning(f"Could not get model paths: {e}")
            return {}

    def get_available_models(self) -> List[str]:
        """Get list of available super resolution models"""
        available = []
        for model_name, model_path in self._model_paths.items():
            if os.path.exists(model_path):
                available.append(model_name)
        return available

    def load_model(self, model_name: str) -> bool:
        """Load a specific super resolution model"""
        try:
            if model_name in self._models:
                return True  # Already loaded

            if model_name not in self._model_paths:
                self.logger.error(f"Unknown model: {model_name}")
                return False

            model_path = self._model_paths[model_name]
            if not os.path.exists(model_path):
                self.logger.warning(f"Model file not found: {model_path}")
                return False

            if model_name == "esrgan":
                return self._load_esrgan_model(model_path)
            elif model_name in ["srcnn", "espcn", "edsr"]:
                return self._load_opencv_model(model_name, model_path)
            else:
                self.logger.error(f"Unsupported model type: {model_name}")
                return False

        except Exception as e:
            self.logger.error(f"Error loading model {model_name}: {e}")
            return False

    def _load_esrgan_model(self, model_path: str) -> bool:
        """Load Real-ESRGAN model (if available)"""
        try:
            # Try to import Real-ESRGAN
            try:
                from basicsr.archs.rrdbnet_arch import (  # type: ignore[import-not-found]
                    RRDBNet,
                )
                from realesrgan import RealESRGANer  # type: ignore[import-not-found]

                # Create Real-ESRGAN model
                model = RRDBNet(
                    num_in_ch=3,
                    num_out_ch=3,
                    num_feat=64,
                    num_block=23,
                    num_grow_ch=32,
                    scale=4,
                )
                self._models["esrgan"] = RealESRGANer(
                    scale=4,
                    model_path=model_path,
                    model=model,
                    tile=0,
                    tile_pad=10,
                    pre_pad=0,
                    half=False,
                )
                self.logger.info("Real-ESRGAN model loaded successfully")
                return True

            except ImportError:
                self.logger.warning(
                    "Real-ESRGAN not available, install with: pip install realesrgan"
                )
                return False

        except Exception as e:
            self.logger.error(f"Error loading Real-ESRGAN: {e}")
            return False

    def _load_opencv_model(self, model_name: str, model_path: str) -> bool:
        """Load OpenCV DNN super resolution model"""
        try:
            # Check if model file exists and is valid
            if not os.path.exists(model_path):
                self.logger.warning(f"Model file not found: {model_path}")
                return False

            # Check file size (should be > 1MB for real models)
            file_size = os.path.getsize(model_path)
            if file_size < 1024 * 1024:  # Less than 1MB
                self.logger.warning(
                    f"Model file too small ({file_size} bytes), likely corrupted: {model_path}"
                )
                return False

            sr_model = cv2.dnn_superres.DnnSuperResImpl_create()  # type: ignore[attr-defined]
            sr_model.readModel(model_path)

            # Set model based on type
            if model_name == "srcnn":
                sr_model.setModel("srcnn", 2)
            elif model_name == "espcn":
                sr_model.setModel("espcn", 2)
            elif model_name == "edsr":
                sr_model.setModel("edsr", 2)

            self._models[model_name] = sr_model
            self.logger.info(f"{model_name.upper()} model loaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error loading {model_name} model: {e}")
            return False

    def enhance_image(
        self, image: np.ndarray, model_name: str = "espcn", use_fallback: bool = True
    ) -> np.ndarray:
        """Enhance image using specified super resolution model"""
        try:
            # Validate input
            if image is None or image.size == 0:
                self.logger.error("Invalid input image")
                return image

            # Load model if not already loaded
            if model_name not in self._models:
                if not self.load_model(model_name):
                    if use_fallback:
                        self.logger.warning(
                            f"Model {model_name} not available, using fallback"
                        )
                        return self._fallback_enhancement(image)
                    else:
                        return image

            # Apply super resolution
            start_time = time.time()

            if model_name == "esrgan":
                enhanced, _ = self._models[model_name].enhance(image, outscale=2)
            else:
                enhanced = self._models[model_name].upsample(image)

            processing_time = time.time() - start_time
            self.logger.debug(
                f"Super resolution processing time: {processing_time:.3f}s"
            )

            return enhanced

        except Exception as e:
            self.logger.error(f"Error enhancing image with {model_name}: {e}")
            if use_fallback:
                return self._fallback_enhancement(image)
            return image

    def _fallback_enhancement(self, image: np.ndarray) -> np.ndarray:
        """High-quality fallback enhancement using OpenCV"""
        try:
            # Use LANCZOS4 for high-quality upscaling
            height, width = image.shape[:2]
            upscaled = cv2.resize(
                image, (width * 2, height * 2), interpolation=cv2.INTER_LANCZOS4
            )

            # Apply unsharp masking for better edge definition
            gaussian = cv2.GaussianBlur(upscaled, (0, 0), 1.0)
            unsharp_mask = cv2.addWeighted(upscaled, 1.5, gaussian, -0.5, 0)

            # Apply contrast enhancement
            enhanced = cv2.convertScaleAbs(unsharp_mask, alpha=1.1, beta=5)

            return enhanced

        except Exception as e:
            self.logger.error(f"Fallback enhancement failed: {e}")
            return image

    def cleanup(self) -> None:
        """Clean up loaded models"""
        try:
            self._models.clear()
            self.logger.info("Super resolution models cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


# Convenience functions
def enhance_image_simple(
    image: np.ndarray, scale: int = 2, model_type: str = "espcn"  # noqa: ARG001
) -> np.ndarray:
    """Simple image enhancement function"""
    processor = SuperResolutionProcessor()
    try:
        return processor.enhance_image(image, model_type)
    finally:
        processor.cleanup()


def enhance_image_with_validation(
    image: np.ndarray,
    scale: int = 2,  # noqa: ARG001
    model_type: str = "espcn",
    min_size: int = 32,
    max_size: int = 2048,
) -> np.ndarray:
    """Enhanced image with validation"""
    processor = SuperResolutionProcessor()
    try:
        # Validate image size
        height, width = image.shape[:2]
        if width < min_size or height < min_size:
            processor.logger.warning(f"Image too small: {width}x{height}")
            return image
        if width > max_size or height > max_size:
            processor.logger.warning(f"Image too large: {width}x{height}")
            return image

        return processor.enhance_image(image, model_type)
    finally:
        processor.cleanup()
