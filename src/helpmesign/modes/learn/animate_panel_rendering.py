"""
Rendering and frame handling for AnimateGesturePanel.
Extracted from animate_panel.py to reduce file size.
"""

from typing import Any, Optional

from ...utils.logger import get_logger

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
                try:
                    import math

                    self.parent_panel._wave_time += 0.016  # ~60 FPS
                    wave_progress = min(self.parent_panel._wave_time / 2.0, 1.0)

                    if wave_progress >= 1.0:
                        # Wave complete
                        self.parent_panel._wave_active = False
                        self.parent_panel._wave_target = None
                    else:
                        # Continue wave
                        wave_offset = math.sin(wave_progress * math.pi * 2) * 0.2
                        right_hand = self.parent_panel._get_joint_node("right_hand")
                        if right_hand:
                            current_pos = right_hand.getPos()
                            right_hand.setPos(
                                current_pos[0],
                                current_pos[1],
                                current_pos[2] + wave_offset,
                            )
                except Exception:
                    self.parent_panel._wave_active = False

            # Intro animation
            if self.parent_panel._intro_active:
                try:
                    self.parent_panel._intro_t += 0.016  # ~60 FPS
                    intro_duration = 3.0

                    if self.parent_panel._intro_t >= intro_duration:
                        # Intro complete
                        self.parent_panel._intro_active = False
                    else:
                        # Continue intro
                        intro_progress = self.parent_panel._intro_t / intro_duration
                        # Simple intro animation - could be expanded
                        pass
                except Exception:
                    self.parent_panel._intro_active = False

            # Log first frame
            if not hasattr(self.parent_panel, "_first_frame_logged"):
                self.parent_panel._log.info("First frame displayed in 3D panel")
                self.parent_panel._first_frame_logged = True

        except Exception as e:
            self._log.error(f"Error in frame rendering: {e}")

    def resizeEvent(self, event):
        """Handle widget resize events."""
        try:
            # Call parent resize event
            super(self.parent_panel.__class__, self.parent_panel).resizeEvent(event)

            # Update render target size
            self.parent_panel._update_render_target_size()

        except Exception as e:
            self._log.error(f"Error in resize event: {e}")

    def update_render_target_size(self) -> None:
        """Update the render target size to match the widget size."""
        try:
            if not self.parent_panel._showbase or not self.parent_panel._panda_ready:
                return

            # Get current widget size
            width = self.parent_panel.width()
            height = self.parent_panel.height()

            if width <= 0 or height <= 0:
                return

            # Update the window size
            self.parent_panel._showbase.win.setSize(width, height)

            # Update camera aspect ratio
            if hasattr(self.parent_panel._showbase, "camLens"):
                lens = self.parent_panel._showbase.camLens
                if hasattr(lens, "setAspectRatio"):
                    aspect_ratio = width / height
                    lens.setAspectRatio(aspect_ratio)

        except Exception as e:
            self._log.error(f"Error updating render target size: {e}")

    def shutdown(self):
        """Gracefully shutdown the rendering system."""
        try:
            self.parent_panel._shutdown_requested = True

            # Stop all timers
            if hasattr(self.parent_panel, "_timer") and self.parent_panel._timer:
                self.parent_panel._timer.stop()
                self.parent_panel._timer = None

            # Stop animations
            self.parent_panel._is_animating = False
            self.parent_panel._wave_active = False
            self.parent_panel._intro_active = False

            # Clear texture references
            if hasattr(self.parent_panel, "_color_tex"):
                self.parent_panel._color_tex = None

            # Clear display widget
            if hasattr(self.parent_panel, "_display") and self.parent_panel._display:
                try:
                    self.parent_panel._display.clear()
                    self.parent_panel._display.deleteLater()
                except Exception:
                    pass
                self.parent_panel._display = None

            # Force garbage collection
            import gc

            gc.collect()

            self._log.info("Rendering system shutdown completed")

        except Exception as e:
            self._log.error(f"Error during rendering shutdown: {e}")

    def get_display_widget(self):
        """Get the display widget for rendering."""
        return self.parent_panel._display

    def set_display_widget(self, display_widget):
        """Set the display widget for rendering."""
        self.parent_panel._display = display_widget

    def is_panda_ready(self) -> bool:
        """Check if Panda3D is ready for rendering."""
        return self.parent_panel._panda_ready

    def set_panda_ready(self, ready: bool):
        """Set Panda3D ready state."""
        self.parent_panel._panda_ready = ready

    def get_showbase(self):
        """Get the Panda3D ShowBase instance."""
        return self.parent_panel._showbase

    def set_showbase(self, showbase):
        """Set the Panda3D ShowBase instance."""
        self.parent_panel._showbase = showbase

    def get_color_texture(self):
        """Get the color texture for rendering."""
        return self.parent_panel._color_tex

    def set_color_texture(self, texture):
        """Set the color texture for rendering."""
        self.parent_panel._color_tex = texture
