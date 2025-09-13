"""
Main AnimateGesturePanel class for Learn mode.
Coordinates all managers and provides the public API for 3D character animation.
"""

from typing import Any, Dict, List, Optional

from ....utils.logger import get_logger

try:
    from PySide6.QtCore import QPoint, QRect, Qt, QTimer
    from PySide6.QtGui import QIcon, QImage, QPixmap
    from PySide6.QtWidgets import (
        QDialog,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover - tests may mock Qt imports
    pass

# Import OpenCV and numpy outside try-except to ensure they're always available
import cv2
import numpy as np

from .animation_manager import AnimationManager
from .model_manager import ModelManager
from .panda3d_manager import Panda3DManager
from .rendering_manager import RenderingManager


class ZoomLens(QLabel):
    """Super resolution zoom lens using OpenCV DNN"""
    
    # Zoom lens configuration constants
    LENS_SIZE = 300
    ZOOM_MAGNIFICATION = 6  # 4x zoom
    SOURCE_REGION_SIZE = 50 # Base source region size (will be scaled by 8x for high-res)

    def __init__(self, parent_panel, parent=None):
        super().__init__(parent)
        self.parent_panel = parent_panel
        self.setFixedSize(self.LENS_SIZE, self.LENS_SIZE)
        self.setStyleSheet(
            f"""
            QLabel {{
                border: 3px solid #007acc;
                border-radius: {self.LENS_SIZE // 2}px;
                background-color: transparent;
            }}
        """
        )
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(True)
        self.hide()

        # Enable mouse tracking for dragging
        self.setMouseTracking(True)
        self.dragging = False
        self.drag_start_pos = None

        # Initialize super resolution model
        self.sr_model = None
        self._init_super_resolution()

        # No timer needed - zoom lens updates only when necessary

    def _init_super_resolution(self):
        """Initialize the super resolution model"""
        try:
            import os

            # Get the project root directory (go up from src/helpmesign/modes/learn/animate_panel/)
            current_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
                )
            )

            # Try EDSR x2 model first (more reliable)
            edsr_path = os.path.join(
                project_root,
                "resources",
                "models",
                "super_resolution",
                "EDSR_x2.pb",
            )

            self.parent_panel._log.debug(f"Looking for EDSR model at: {edsr_path}")
            self.parent_panel._log.debug(f"Model exists: {os.path.exists(edsr_path)}")

            # Skip loading EDSR models - they're too slow for real-time use (2+ seconds per operation)
            # Use enhanced interpolation instead for fast, high-quality results
            self.parent_panel._log.info(
                "Using enhanced interpolation for fast, high-quality zoom (EDSR models too slow for real-time)"
            )
            self.sr_model = None
        except Exception as e:
            self.parent_panel._log.warning(
                f"Failed to initialize super resolution: {e}"
            )
            self.sr_model = None

    def update_zoom_view(self):
        """Update the zoomed view using super resolution for high-quality magnification"""
        try:
            if not self.isVisible():
                return

            # Try to get high-resolution image first, fallback to display pixmap
            high_res_image = None
            if (
                hasattr(self.parent_panel, "_rendering_manager")
                and self.parent_panel._rendering_manager
            ):
                high_res_image = (
                    self.parent_panel._rendering_manager.get_high_res_image()
                )

            if high_res_image and not high_res_image.isNull():
                # Use high-resolution image for better zoom quality
                current_pixmap = QPixmap.fromImage(high_res_image)
                self.parent_panel._log.debug(
                    f"Using high-res image: {high_res_image.width()}x{high_res_image.height()}"
                )
            elif hasattr(self.parent_panel, "_display") and self.parent_panel._display:
                current_pixmap = self.parent_panel._display.pixmap()
                if not current_pixmap.isNull():
                    pass
                else:
                    return
            else:
                return

            # Get the lens center position relative to the main panel
            lens_center_relative_to_panel = self.mapTo(
                self.parent_panel, self.rect().center()
            )

            # Get the display widget position relative to the main panel
            display_widget = self.parent_panel._display
            display_top_left_relative = display_widget.mapTo(
                self.parent_panel, display_widget.rect().topLeft()
            )

            # Calculate the lens position within the display widget
            display_x = (
                lens_center_relative_to_panel.x() - display_top_left_relative.x()
            )
            display_y = (
                lens_center_relative_to_panel.y() - display_top_left_relative.y()
            )

            # Scale coordinates for high-resolution image
            # The high-res image is 8x larger than the display
            if high_res_image and not high_res_image.isNull():
                scale_factor = 8  # 8x high-res rendering
                high_res_x = display_x * scale_factor
                high_res_y = display_y * scale_factor
                source_size = self.SOURCE_REGION_SIZE * scale_factor  # Scaled source for high-res
            else:
                high_res_x = display_x
                high_res_y = display_y
                source_size = self.SOURCE_REGION_SIZE

            source_x = max(0, high_res_x - source_size // 2)
            source_y = max(0, high_res_y - source_size // 2)

            # Ensure we don't go beyond the pixmap bounds
            source_x = min(source_x, current_pixmap.width() - source_size)
            source_y = min(source_y, current_pixmap.height() - source_size)
            source_x = max(0, source_x)
            source_y = max(0, source_y)

            # Debug extraction coordinates (simplified)
            if high_res_image and not high_res_image.isNull():
                self.parent_panel._log.debug(
                    f"Extracting from high-res: ({source_x}, {source_y}) size: {source_size}"
                )

            # Extract the source area
            source_rect = QRect(source_x, source_y, source_size, source_size)
            cropped_pixmap = current_pixmap.copy(source_rect)

            # Debug cropped pixmap (simplified)
            if cropped_pixmap.isNull():
                self.parent_panel._log.warning("Failed to crop pixmap")

            if not cropped_pixmap.isNull():
                # Try super resolution first, fallback to high-quality scaling
                try:
                    # Convert QPixmap to OpenCV format
                    qimage = cropped_pixmap.toImage()
                    width = qimage.width()
                    height = qimage.height()

                    # Get image data
                    ptr = qimage.bits()
                    data = bytes(ptr)

                    # Convert to numpy array (RGBA format)
                    arr = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 4)

                    # Convert RGBA to RGB with proper alpha handling
                    alpha = arr[:, :, 3]
                    rgb = arr[:, :, :3]

                    # Use the original image without forcing a white background
                    rgb_image = rgb.copy()

                    # Debug input image (simplified)
                    if rgb_image.min() == rgb_image.max():
                        self.parent_panel._log.warning("Input image appears to be uniform")

                    # Apply super resolution if model is available
                    if self.sr_model is not None:
                        try:
                            # Preprocess image for better super resolution results
                            preprocessed = self._preprocess_for_sr(rgb_image)

                            # Use super resolution for 2x upscaling
                            super_res_image = self.sr_model.upsample(preprocessed)

                            # Postprocess for better quality
                            enhanced = self._postprocess_sr_result(super_res_image)

                            # Take center 250x250 from the super resolution result
                            sr_height, sr_width = enhanced.shape[:2]
                            center_start_h = (sr_height - 250) // 2
                            center_start_w = (sr_width - 250) // 2
                            final_image = enhanced[
                                center_start_h : center_start_h + 250,
                                center_start_w : center_start_w + 250,
                            ]

                            self.parent_panel._log.debug(
                                f"Super resolution applied: {rgb_image.shape} -> {super_res_image.shape} -> {final_image.shape}"
                            )

                        except Exception as sr_error:
                            self.parent_panel._log.warning(
                                f"Super resolution failed, using fallback: {sr_error}"
                            )
                            # Fallback to high-quality interpolation with enhancement
                            final_image = self._enhanced_interpolation(
                                rgb_image, (self.LENS_SIZE, self.LENS_SIZE)
                            )
                    else:
                        # Use enhanced interpolation as fallback
                        final_image = self._enhanced_interpolation(
                            rgb_image, (300, 300)
                        )

                    # Convert back to QPixmap - ensure contiguous memory
                    height, width, _ = final_image.shape
                    bytes_per_line = 3 * width

                    # Debug logging (simplified)
                    if final_image.min() == final_image.max():
                        self.parent_panel._log.warning("Final image appears to be uniform")

                    # Ensure the array is contiguous in memory
                    final_image_contiguous = np.ascontiguousarray(final_image)

                    q_image = QImage(
                        final_image_contiguous.data,
                        width,
                        height,
                        bytes_per_line,
                        QImage.Format_RGB888,
                    )

                    # Debug QImage (simplified)
                    if q_image.isNull():
                        self.parent_panel._log.warning("Failed to create QImage")

                    scaled_pixmap = QPixmap.fromImage(q_image)

                    # Debug QPixmap (simplified)
                    if scaled_pixmap.isNull():
                        self.parent_panel._log.warning("Failed to create QPixmap")

                    # Create a circular zoom lens with magnified content
                    from PySide6.QtGui import QPainter, QPainterPath

                    # Create a circular pixmap with theme-aware background
                    circular_pixmap = QPixmap(self.LENS_SIZE, self.LENS_SIZE)
                    # Use theme-appropriate background color
                    current_theme = self.parent_panel.get_current_theme()
                    if current_theme == "Light":
                        circular_pixmap.fill(
                            Qt.GlobalColor.white
                        )  # White background for light theme
                    else:
                        circular_pixmap.fill(
                            Qt.GlobalColor.transparent
                        )  # Transparent for dark theme

                    painter = QPainter(circular_pixmap)
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

                    # Set circular clipping region
                    path = QPainterPath()
                    path.addEllipse(0, 0, self.LENS_SIZE, self.LENS_SIZE)
                    painter.setClipPath(path)

                    # Draw the magnified content
                    painter.drawPixmap(0, 0, scaled_pixmap)
                    painter.end()

                    # Debug final circular pixmap (simplified)
                    if circular_pixmap.isNull():
                        self.parent_panel._log.warning("Failed to create circular pixmap")

                    self.setPixmap(circular_pixmap)

                except Exception as cv_error:
                    # Final fallback to Qt scaling
                    self.parent_panel._log.warning(
                        f"OpenCV processing failed, using Qt fallback: {cv_error}"
                    )
                    # Create a circular zoom lens with magnified content (fallback)
                    from PySide6.QtGui import QPainter, QPainterPath

                    fallback_scaled_pixmap = cropped_pixmap.scaled(
                        250,
                        250,
                        Qt.AspectRatioMode.IgnoreAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )

                    # Create a circular pixmap with theme-aware background
                    circular_pixmap = QPixmap(self.LENS_SIZE, self.LENS_SIZE)
                    # Use theme-appropriate background color
                    current_theme = self.parent_panel.get_current_theme()
                    if current_theme == "Light":
                        circular_pixmap.fill(
                            Qt.GlobalColor.white
                        )  # White background for light theme
                    else:
                        circular_pixmap.fill(
                            Qt.GlobalColor.transparent
                        )  # Transparent for dark theme

                    painter = QPainter(circular_pixmap)
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

                    # Set circular clipping region
                    path = QPainterPath()
                    path.addEllipse(0, 0, self.LENS_SIZE, self.LENS_SIZE)
                    painter.setClipPath(path)

                    # Draw the magnified content
                    painter.drawPixmap(0, 0, fallback_scaled_pixmap)
                    painter.end()

                    self.setPixmap(circular_pixmap)
            else:
                self.setText("No Image")
        except Exception as e:
            self.parent_panel._log.warning(f"Error updating zoom lens: {e}")
            self.setText("Error")

    def show_lens(self, x, y):
        """Show the lens at the specified position"""
        # Position the lens so it's centered on the click point
        # Ensure the lens stays within the parent widget bounds
        parent_width = self.parent().width() if self.parent() else 400
        parent_height = self.parent().height() if self.parent() else 400

        # Calculate position with bounds checking
        lens_x = max(0, min(x - self.width() // 2, parent_width - self.width()))
        lens_y = max(0, min(y - self.height() // 2, parent_height - self.height()))

        # Only update if position has changed significantly
        current_pos = self.pos()
        if (
            abs(current_pos.x() - lens_x) > 2
            or abs(current_pos.y() - lens_y) > 2
            or not self.isVisible()
        ):

            self.move(lens_x, lens_y)
            self.show()
            self.raise_()  # Bring to front

            # Update the zoom view immediately
            self.update_zoom_view()

            # Debug logging
            self.parent_panel._log.debug(
                f"Zoom lens positioned at ({lens_x}, {lens_y}) for click at ({x}, {y})"
            )

    def hide_lens(self):
        """Hide the lens"""
        self.hide()
        self.update_timer.stop()

    def _preprocess_for_sr(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better super resolution results"""
        try:
            # Apply slight sharpening to enhance details before super resolution
            kernel = np.array([[-0.5, -1, -0.5], [-1, 7, -1], [-0.5, -1, -0.5]])
            sharpened = cv2.filter2D(image, -1, kernel)

            # Blend original with sharpened for natural look
            preprocessed = cv2.addWeighted(image, 0.7, sharpened, 0.3, 0)

            # Ensure values are in valid range
            preprocessed = np.clip(preprocessed, 0, 255).astype(np.uint8)

            return preprocessed
        except Exception as e:
            self.parent_panel._log.warning(f"Preprocessing failed: {e}")
            return image

    def _postprocess_sr_result(self, image: np.ndarray) -> np.ndarray:
        """Postprocess super resolution result for better quality"""
        try:
            # Apply unsharp masking for better edge definition
            gaussian = cv2.GaussianBlur(image, (0, 0), 1.0)
            unsharp_mask = cv2.addWeighted(image, 1.5, gaussian, -0.5, 0)

            # Apply contrast enhancement
            enhanced = cv2.convertScaleAbs(unsharp_mask, alpha=1.1, beta=5)

            # Apply edge enhancement
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            edge_enhanced = cv2.filter2D(enhanced, -1, kernel)

            # Blend for natural but sharp look
            final = cv2.addWeighted(enhanced, 0.8, edge_enhanced, 0.2, 0)

            # Ensure values are in valid range
            final = np.clip(final, 0, 255).astype(np.uint8)

            return final
        except Exception as e:
            self.parent_panel._log.warning(f"Postprocessing failed: {e}")
            return image

    def _enhanced_interpolation(
        self, image: np.ndarray, target_size: tuple
    ) -> np.ndarray:
        """Enhanced interpolation with optimized quality improvements for real-time performance"""
        try:
            # Use Lanczos4 for high-quality upscaling
            upscaled = cv2.resize(image, target_size, interpolation=cv2.INTER_LANCZOS4)

            # Apply moderate unsharp masking for better edge definition
            gaussian = cv2.GaussianBlur(upscaled, (0, 0), 1.2)
            unsharp_mask = cv2.addWeighted(upscaled, 1.4, gaussian, -0.4, 0)

            # Apply moderate contrast enhancement
            enhanced = cv2.convertScaleAbs(unsharp_mask, alpha=1.1, beta=5)

            # Apply single sharpening pass for good detail without being too slow
            kernel = np.array([[-0.5, -1, -0.5], [-1, 7, -1], [-0.5, -1, -0.5]])
            sharpened = cv2.filter2D(enhanced, -1, kernel)

            # Blend for natural but sharp look
            final = cv2.addWeighted(enhanced, 0.7, sharpened, 0.3, 0)

            # Apply final contrast boost
            final = cv2.convertScaleAbs(final, alpha=1.05, beta=2)

            # Ensure values are in valid range
            final = np.clip(final, 0, 255).astype(np.uint8)

            return final
        except Exception as e:
            self.parent_panel._log.warning(f"Enhanced interpolation failed: {e}")
            # Fallback to simple Lanczos4
            return cv2.resize(image, target_size, interpolation=cv2.INTER_LANCZOS4)

    def mousePressEvent(self, event):
        """Handle mouse press to start dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_start_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            self.parent_panel._log.debug("Zoom lens: Mouse press - dragging started")
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            # Move the lens to follow the mouse
            new_pos = event.globalPosition().toPoint() - self.drag_start_pos
            # Keep within parent bounds
            parent_rect = self.parent().rect()
            new_pos.setX(max(0, min(new_pos.x(), parent_rect.width() - self.width())))
            new_pos.setY(max(0, min(new_pos.y(), parent_rect.height() - self.height())))
            self.move(new_pos)
            # Update the zoom view immediately after moving
            self.update_zoom_view()
            self.parent_panel._log.debug(
                f"Zoom lens: Mouse move - moved to ({new_pos.x()}, {new_pos.y()})"
            )
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release to stop dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.drag_start_pos = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)


class AnimateGesturePanel(QWidget):
    """Lightweight wrapper to render Panda3D frames into a Qt widget.

    Public API:
    - load_character(model_path: str)
    - set_language(code: str)
    - play_gesture(char_code: str, hand: str)
    """

    def __init__(
        self, parent: Optional[QWidget] = None, headless: bool = False
    ) -> None:
        # If no QApplication exists (e.g., tests before Qt mocks), avoid QWidget init
        self._log = get_logger("helpmesign.modes.learn.animate_panel")
        self._headless: bool = headless

        def _make_stub_label():
            class _Stub:
                def setAlignment(self, *_, **__):
                    return None

                def setText(self, *_):
                    return None

                def setAttribute(self, *_, **__):
                    return None

                def setAutoFillBackground(self, *_):
                    return None

                def setStyleSheet(self, *_):
                    return None

                def setPixmap(self, *_):
                    return None

            return _Stub()

        can_build_qwidget = False
        try:
            from PySide6.QtWidgets import QApplication

            app = QApplication.instance()
            can_build_qwidget = app is not None and hasattr(app, "activeWindow")
        except Exception:
            can_build_qwidget = False

        if can_build_qwidget:
            super().__init__(parent)
            # Render target
            self._display = QLabel(self)
            try:
                self._display.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self._display.setText("Loading 3D character...")
                self._display.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
                self._display.setAutoFillBackground(True)
                # Theme-aware background color will be set in _apply_theme_colors
            except Exception:
                self._display = _make_stub_label()

            # Layout
            layout = QVBoxLayout(self)
            layout.addWidget(self._display)
            layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(layout)

            # Add zoom button overlay
            self._create_zoom_button()

            # Set widget properties
            self.setObjectName("AnimateGesturePanel")
            self.setFixedHeight(400)
            # Theme-aware background color will be set in _apply_theme_colors
        else:
            # Headless mode for tests
            self._headless = True
            self._display = _make_stub_label()

        # Initialize managers
        self._panda_manager = Panda3DManager(self)
        self._rendering_manager = RenderingManager(self)
        self._animation_manager = AnimationManager(self)
        self._model_manager = ModelManager(self)

        # Panda3D state
        self._panda_ready: bool = False
        self._showbase: Optional[Any] = None
        self._scene: Optional[Any] = None
        self._camera: Optional[Any] = None
        self._color_tex: Optional[Any] = None
        self._timer: Optional[QTimer] = None

        # Model state
        self._model_np: Optional[Any] = None
        self._actor: Optional[Any] = None

        # Animation state
        self._is_animating: bool = False
        self._wave_active: bool = False
        self._wave_progress: float = 0.0
        self._wave_target: Optional[Any] = None
        self._intro_active: bool = False
        self._intro_progress: float = 0.0
        self._current_word: Optional[str] = None
        self._current_hand: Optional[str] = None
        self._word_index: int = 0

        # Timers
        self._animation_timer: Optional[QTimer] = None
        self._phrase_timer: Optional[QTimer] = None

        # Sign language loader
        self.sign_loader: Optional[Any] = None

        # Shutdown state
        self._shutdown_requested: bool = False

        # Zoom lens reference
        self._zoom_lens: Optional[ZoomLens] = None
        self._last_zoom_pos: Optional[QPoint] = None

    def _apply_theme_colors(self) -> None:
        """Apply theme-aware colors to the panel and display."""
        try:
            if self._headless:
                return

            current_theme = self.get_current_theme()

            if current_theme == "Light":
                # Light theme colors - darker gray for better character contrast
                bg_color = "#e5e7eb"  # Medium light gray for better contrast
                text_color = "#1e293b"  # Dark blue-gray
            else:
                # Dark theme colors
                bg_color = "#2b2b2b"  # Dark gray
                text_color = "#ffffff"  # White

            # Apply to main panel with object name specificity
            self.setStyleSheet(
                f"#animateGesturePanel {{ background-color: {bg_color}; }}"
            )

            # Apply to display label
            if hasattr(self, "_display") and self._display:
                self._display.setStyleSheet(
                    f"background-color: {bg_color}; color: {text_color};"
                )

            self._log.info(f"Applied {current_theme} theme colors to 3D panel")

        except Exception as e:
            self._log.error(f"Error applying theme colors: {e}")
            # Fallback to dark theme
            if hasattr(self, "_display") and self._display:
                self._display.setStyleSheet("background-color: #2b2b2b; color: white;")
            self.setStyleSheet("#animateGesturePanel { background-color: #2b2b2b; }")

    def _create_zoom_button(self) -> None:
        """Create and position the zoom button in the top-right corner"""
        try:
            if self._headless:
                return

            # Create zoom button
            self._zoom_button = QPushButton("🔍", self)
            self._zoom_button.setFixedSize(40, 40)
            self._zoom_button.setStyleSheet(
                """
                QPushButton {
                    background-color: rgba(0, 0, 0, 0.7);
                    color: white;
                    border: 2px solid rgba(255, 255, 255, 0.8);
                    border-radius: 20px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 0.9);
                    border-color: white;
                }
                QPushButton:pressed {
                    background-color: rgba(0, 0, 0, 1.0);
                }
            """
            )
            self._zoom_button.clicked.connect(self._toggle_zoom_mode)
            self._zoom_button.setToolTip(
                "Toggle Zoom Lens (Click to activate, click again to deactivate)"
            )

            # Position button in top-right corner
            self._zoom_button.move(self.width() - 50, 10)

            # Create zoom lens
            try:
                self._zoom_lens = ZoomLens(self, self)
                self._log.info("Zoom lens created successfully")
            except Exception as lens_error:
                self._log.error(f"Error creating zoom lens: {lens_error}")
                self._zoom_lens = None
            self._zoom_mode_active = False

        except Exception as e:
            self._log.error(f"Error creating zoom button: {e}")

    def _toggle_zoom_mode(self) -> None:
        """Toggle zoom lens mode on/off"""
        try:
            if self._headless:
                return

            # Ensure zoom lens is created
            if not hasattr(self, "_zoom_lens") or self._zoom_lens is None:
                try:
                    self._zoom_lens = ZoomLens(self, self)
                    self._log.info("Zoom lens created on demand")
                except Exception as lens_error:
                    self._log.error(f"Error creating zoom lens on demand: {lens_error}")
                    return

            self._zoom_mode_active = not self._zoom_mode_active

            if self._zoom_mode_active:
                # Enable zoom mode - show zoom lens at center
                center_x = self.width() // 2
                center_y = self.height() // 2
                if self._zoom_lens and hasattr(self._zoom_lens, "show_lens"):
                    self._zoom_lens.show_lens(center_x, center_y)
                self._zoom_button.setStyleSheet(
                    """
                    QPushButton {
                        background-color: rgba(0, 122, 204, 0.9);
                        color: white;
                        border: 2px solid rgba(255, 255, 255, 0.8);
                        border-radius: 20px;
                        font-size: 16px;
                        font-weight: bold;
                    }
                """
                )
            else:
                # Disable zoom mode
                if self._zoom_lens:
                    self._zoom_lens.hide_lens()
                self._display.setText("Loading 3D character...")
                self._zoom_button.setStyleSheet(
                    """
                    QPushButton {
                        background-color: rgba(0, 0, 0, 0.7);
                        color: white;
                        border: 2px solid rgba(255, 255, 255, 0.8);
                        border-radius: 20px;
                        font-size: 16px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: rgba(0, 0, 0, 0.9);
                        border-color: white;
                    }
                    QPushButton:pressed {
                        background-color: rgba(0, 0, 0, 1.0);
                    }
                """
                )

        except Exception as e:
            self._log.error(f"Error toggling zoom mode: {e}")

    def resizeEvent(self, event) -> None:
        """Handle resize events and reposition zoom button"""
        try:
            if not self._headless:
                super().resizeEvent(event)
                self._rendering_manager.update_render_target_size()

                # Reposition zoom button
                if hasattr(self, "_zoom_button") and self._zoom_button:
                    self._zoom_button.move(self.width() - 50, 10)

        except Exception as e:
            self._log.error(f"Error in resize event: {e}")

    def mousePressEvent(self, event) -> None:
        """Handle mouse press events for zoom lens"""
        try:
            if self._headless:
                return

            if hasattr(self, "_zoom_mode_active") and self._zoom_mode_active:
                # Show zoom lens at click position
                if self._zoom_lens and hasattr(self._zoom_lens, "show_lens"):
                    self._zoom_lens.show_lens(event.x(), event.y())

                # Also pass through to parent for pose updates
                super().mousePressEvent(event)
            else:
                # Pass through to parent
                super().mousePressEvent(event)

        except Exception as e:
            self._log.error(f"Error in mouse press event: {e}")

    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move events to update zoom lens position"""
        try:
            if self._headless:
                return

            if (
                hasattr(self, "_zoom_mode_active")
                and self._zoom_mode_active
                and hasattr(self, "_zoom_lens")
                and self._zoom_lens
                and hasattr(self._zoom_lens, "isVisible")
                and self._zoom_lens.isVisible()
            ):
                # Only update position if mouse has moved significantly (avoid micro-movements)
                # and throttle updates to prevent excessive calls
                if hasattr(self._zoom_lens, "show_lens"):
                    # Check if we have a last position and if movement is significant
                    if (
                        self._last_zoom_pos is None
                        or abs(event.x() - self._last_zoom_pos.x()) > 5
                        or abs(event.y() - self._last_zoom_pos.y()) > 5
                    ):
                        self._last_zoom_pos = event.position().toPoint()
                        # Use a timer to throttle updates
                        if not hasattr(self, "_zoom_update_timer"):
                            self._zoom_update_timer = QTimer(self)
                            self._zoom_update_timer.setSingleShot(True)
                            self._zoom_update_timer.timeout.connect(
                                lambda: self._zoom_lens.show_lens(event.x(), event.y())
                            )
                        # Cancel previous timer and start new one
                        self._zoom_update_timer.stop()
                        self._zoom_update_timer.start(16)  # ~60fps max
            else:
                # Pass through to parent
                super().mouseMoveEvent(event)

        except Exception as e:
            self._log.error(f"Error in mouse move event: {e}")

    def mouseReleaseEvent(self, event) -> None:
        """Handle mouse release events"""
        try:
            if self._headless:
                return

            if hasattr(self, "_zoom_mode_active") and self._zoom_mode_active:
                # Keep lens visible after mouse release, but still pass through for pose updates
                super().mouseReleaseEvent(event)
            else:
                # Pass through to parent
                super().mouseReleaseEvent(event)

        except Exception as e:
            self._log.error(f"Error in mouse release event: {e}")

    # Public API methods
    def set_language(self, code: str) -> None:
        """Set the sign language code."""
        self.current_language = code
        # Initialize sign language loader if not already done
        if not self.sign_loader:
            from ....utils.sign_language_loader import get_sign_language_loader

            self.sign_loader = get_sign_language_loader()

    def load_character(self, model_path: str) -> None:
        """Load a 3D character model."""
        try:
            # Ensure Panda3D is ready
            self._panda_manager.ensure_panda()

            # Load the model
            self._model_manager.load_model_internal(model_path)
        except Exception as e:
            self._log.error(f"Error loading character: {e}")

    def play_gesture(self, char_code: str, hand: str) -> None:
        """Play a gesture for a character code."""
        try:
            pose_data = self._animation_manager.get_letter_pose_from_signs(
                char_code, hand
            )
            if pose_data:
                self._animation_manager.apply_pose(pose_data)
        except Exception as e:
            self._log.error(f"Error playing gesture: {e}")

    def play_phrase(
        self, phrase: str, language: Optional[str] = None, hand: Optional[str] = None
    ) -> None:
        """Play a phrase with letter-by-letter animation."""
        try:
            # If no language provided, get it from global settings
            if not language:
                # Try to get from learn mode global settings
                if hasattr(self, "learn_mode"):
                    language = getattr(self.learn_mode, "current_language", None)
                if not language:
                    self._log.error("No language available in global settings")
                    return

            # If no hand provided, get it from global settings
            if not hand:
                # Try to get from learn mode global settings
                if hasattr(self, "learn_mode"):
                    hand = getattr(self.learn_mode, "current_hand_preference", None)
                if not hand:
                    self._log.error("No hand preference available in global settings")
                    return

            # Set the language for the animation manager
            self.set_language(language)

            # Apply word animation
            self._animation_manager.apply_word_with_animation(phrase, hand)
        except Exception as e:
            self._log.error(f"Error playing phrase: {e}")

    # Qt widget methods
    def setObjectName(self, name: str) -> None:
        """Set the object name."""
        if not self._headless:
            super().setObjectName(name)

    def setFixedHeight(self, h: int) -> None:
        """Set fixed height."""
        if not self._headless:
            super().setFixedHeight(h)

    def setSizePolicy(self, *args, **kwargs) -> None:
        """Set size policy."""
        if not self._headless:
            super().setSizePolicy(*args, **kwargs)

    def setStyleSheet(self, *args, **kwargs) -> None:
        """Set style sheet."""
        if not self._headless:
            super().setStyleSheet(*args, **kwargs)

    # Frame handling
    def _on_frame(self) -> None:
        """Handle frame updates."""
        self._rendering_manager.on_frame()

    def _on_signing_animation_frame(self) -> None:
        """Handle signing animation frame updates."""
        self._animation_manager.on_signing_animation_frame()

    def _on_animation_frame(self) -> None:
        """Handle general animation frame updates."""
        self._animation_manager.on_animation_frame()

    # Animation methods (delegated to managers)
    def _spell_word_letters(self, word: str) -> None:
        """Spell out a word letter by letter."""
        self._animation_manager.spell_word_letters(word)

    def _apply_pose(self, pose: Dict[str, List[float]]) -> None:
        """Apply a pose to the character."""
        self._animation_manager.apply_pose(pose)

    def _reset_to_neutral_pose(self) -> None:
        """Reset to neutral pose."""
        self._animation_manager.reset_to_neutral_pose()

    def pause_animation_and_reset_to_default(self) -> None:
        """Pause animation and reset to default."""
        self._animation_manager.pause_animation_and_reset_to_default()

    def play_welcome(self) -> None:
        """Play welcome animation."""
        self._animation_manager.play_welcome()

    def play_intro(self) -> None:
        """Play intro animation."""
        self._animation_manager.play_intro()

    # Model methods (delegated to managers)
    def _find_node_by_names(self, names) -> Optional[Any]:
        """Find a node by trying multiple possible names."""
        return self._model_manager._find_node_by_names(names)

    def _get_joint_node(self, name: str) -> Optional[Any]:
        """Get a joint node by name."""
        return self._model_manager._get_joint_node(name)

    def _apply_fallback_movement(self) -> None:
        """Apply fallback movement."""
        self._model_manager._apply_fallback_movement()

    def validate_pose_before_application(self, pose: Dict[str, List[float]]) -> bool:
        """Validate pose before application."""
        return self._model_manager.validate_pose_before_application(pose)

    def is_pose_anatomically_valid(self, pose: Dict[str, List[float]]) -> bool:
        """Check if pose is anatomically valid."""
        return self._model_manager.is_pose_anatomically_valid(pose)

    def get_joint_constraint_info(self, joint_name: str) -> Optional[Dict]:
        """Get joint constraint info."""
        return self._model_manager.get_joint_constraint_info(joint_name)

    def _dump_node_names(self) -> None:
        """Dump node names for debugging."""
        self._model_manager._dump_node_names()

    def refresh_lighting_for_theme(self) -> None:
        """Refresh the 3D lighting and background colors to match the current theme."""
        try:
            # Refresh 3D lighting if Panda3D is ready
            if self._panda_ready and hasattr(self, "_model_np") and self._model_np:
                # Re-setup lighting with current theme
                self._model_manager._setup_lighting()
                self._log.info("3D lighting refreshed for current theme")

            # Refresh background colors
            self._apply_theme_colors()

        except Exception as e:
            self._log.error(f"Error refreshing lighting for theme: {e}")

    def get_current_theme(self) -> str:
        """Get the current application theme."""
        try:
            # Use the global theme manager instead of loading configuration
            from ....utils.theme_manager import get_theme_manager

            theme_manager = get_theme_manager()
            return theme_manager.get_current_theme()
        except Exception:
            # Fallback to default Light theme
            return "Light"

    def update_zoom_lens_if_visible(self) -> None:
        """Update the zoom lens if it's currently visible."""
        try:
            if (
                hasattr(self, "_zoom_lens")
                and self._zoom_lens
                and hasattr(self._zoom_lens, "isVisible")
                and self._zoom_lens.isVisible()
            ):
                # Update immediately since this is called after the display is updated
                self._zoom_lens.update_zoom_view()
        except Exception as e:
            self._log.warning(f"Error updating zoom lens: {e}")

    # Cleanup
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            self._shutdown_requested = True

            # Stop timers
            if self._timer:
                self._timer.stop()
                self._timer = None

            if self._animation_timer:
                self._animation_timer.stop()
                self._animation_timer = None

            if self._phrase_timer:
                self._phrase_timer.stop()
                self._phrase_timer = None

            # Shutdown Panda3D manager
            self._panda_manager.shutdown()

            # Clear references
            self._actor = None
            self._model_np = None
            self._camera = None
            self._showbase = None
            self._color_tex = None
            self._panda_ready = False

            # Clear display
            if hasattr(self, "_display") and self._display:
                try:
                    if not self._headless:
                        self._display.setPixmap(QPixmap())
                except Exception:
                    pass

        except Exception as e:
            self._log.error(f"Error during cleanup: {e}")

    def closeEvent(self, event):
        """Handle close events."""
        self.cleanup()
        if not self._headless:
            super().closeEvent(event)
