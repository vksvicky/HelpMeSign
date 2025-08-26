"""
Rendering and frame handling manager for AnimateGesturePanel.
Handles frame updates, image capture, and display rendering.
"""

from typing import Any, Optional

from ....utils.logger import get_logger

try:
    from PySide6.QtGui import QImage, QPixmap
except Exception:  # pragma: no cover - tests may mock Qt imports

    class QImage:  # type: ignore[no-redef]
        pass

    class QPixmap:  # type: ignore[no-redef]
        pass


class RenderingManager:
    """Manages rendering and frame handling for AnimateGesturePanel"""

    def __init__(self, parent_panel):
        self.parent_panel = parent_panel
        self._log = get_logger("helpmesign.modes.learn.animate_panel.rendering")
        self._capture_counter = 0
        self._capture_every_n_frames = 3

    def on_frame(self) -> None:
        """Handle frame rendering and updates."""
        try:
            if not self.parent_panel._panda_ready:
                return

            # Check if we should stop the frame loop
            if (
                hasattr(self.parent_panel, "_shutdown_requested")
                and self.parent_panel._shutdown_requested
            ):
                return

            self.parent_panel._showbase.taskMgr.step()

            # Attempt RAM image first
            image_updated = False
            if self.parent_panel._color_tex is not None:
                try:
                    tex = self.parent_panel._color_tex
                    if tex.hasRamImage():
                        data = tex.getRamImageAs("RGBA")
                        width = tex.getXSize()
                        height = tex.getYSize()
                        stride = width * 4
                        import warnings

                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore", DeprecationWarning)
                            img = QImage(
                                bytes(data), width, height, stride, QImage.Format_RGBA8888  # type: ignore[attr-defined]
                            ).mirrored(False, True)
                        self.parent_panel._display.setPixmap(QPixmap.fromImage(img))
                        image_updated = True
                except Exception:
                    image_updated = False

            # Fallback: explicit screenshot
            # Throttle capture to reduce driver churn
            self._capture_counter = (self._capture_counter + 1) % max(
                1, self._capture_every_n_frames
            )
            if not image_updated and self._capture_counter == 0:
                try:
                    from panda3d.core import PNMImage

                    pimg = PNMImage()
                    ok = self.parent_panel._showbase.win.getScreenshot(pimg)
                    if ok:
                        width = pimg.getXSize()
                        height = pimg.getYSize()
                        data = pimg.getRamImageAs("RGBA")
                        stride = width * 4
                        import warnings

                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore", DeprecationWarning)
                            img = QImage(
                                bytes(data), width, height, stride, QImage.Format_RGBA8888  # type: ignore[attr-defined]
                            ).mirrored(False, True)
                        self.parent_panel._display.setPixmap(QPixmap.fromImage(img))
                        image_updated = True
                except Exception:
                    pass

            # Advance simple animations after stepping Panda
            # Welcome right-hand wave
            if (
                self.parent_panel._wave_active
                and self.parent_panel._wave_target is not None
            ):
                self.parent_panel._wave_progress += 0.05
                if self.parent_panel._wave_progress >= 1.0:
                    self.parent_panel._wave_active = False
                    self.parent_panel._wave_progress = 0.0
                    # Reset to neutral
                    self.parent_panel._reset_to_neutral_pose()
                else:
                    # Simple sine wave
                    import math

                    wave_angle = (
                        math.sin(self.parent_panel._wave_progress * 4 * math.pi) * 0.3
                    )
                    self.parent_panel._wave_target.setH(wave_angle * 180 / math.pi)

            # Intro animation
            if self.parent_panel._intro_active:
                self.parent_panel._intro_progress += 0.02
                if self.parent_panel._intro_progress >= 1.0:
                    self.parent_panel._intro_active = False
                    self.parent_panel._intro_progress = 0.0
                    # Reset to neutral
                    self.parent_panel._reset_to_neutral_pose()
                else:
                    # Simple rotation
                    rotation = self.parent_panel._intro_progress * 360
                    if self.parent_panel._model_np:
                        self.parent_panel._model_np.setH(rotation)

            # Log first frame for debugging
            if not hasattr(self.parent_panel, "_first_frame_logged"):
                self.parent_panel._first_frame_logged = True
                self._log.info("First frame displayed in 3D panel")

        except Exception as e:
            self._log.error(f"Error in frame rendering: {e}")

    def update_render_target_size(self) -> None:
        """Update the render target size to match the widget."""
        try:
            if not self.parent_panel._panda_ready or not self.parent_panel._showbase:
                return

            # Get widget size
            widget_width = self.parent_panel.width()
            widget_height = self.parent_panel.height()

            if widget_width <= 0 or widget_height <= 0:
                return

            # Update window size
            try:
                self.parent_panel._showbase.win.setSize(widget_width, widget_height)
            except Exception:
                pass

            # Update camera aspect ratio
            try:
                lens = self.parent_panel._showbase.camLens
                if hasattr(lens, "setAspectRatio"):
                    aspect_ratio = widget_width / widget_height
                    lens.setAspectRatio(aspect_ratio)
            except Exception:
                pass

        except Exception as e:
            self._log.error(f"Error updating render target size: {e}")
