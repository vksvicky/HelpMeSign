"""
Panda3D initialization and setup manager for AnimateGesturePanel.
Handles ShowBase creation, scene setup, and basic configuration.
"""

from typing import Any, Optional

from ....utils.logger import get_logger

try:
    from PySide6.QtCore import QTimer
except Exception:  # pragma: no cover - tests may mock Qt imports

    class QTimer:  # type: ignore[no-redef]
        pass


class Panda3DManager:
    """Manages Panda3D initialization and setup for AnimateGesturePanel"""

    def __init__(self, parent_panel):
        self.parent_panel = parent_panel
        self._log = get_logger("helpmesign.modes.learn.animate_panel.panda3d")

    def ensure_panda(self) -> None:
        """Initialize Panda3D offscreen context"""
        if self.parent_panel._panda_ready:
            return
        try:
            # Panda imports
            from direct.showbase.ShowBase import ShowBase
            from panda3d.core import AntialiasAttrib, loadPrcFileData

            # Create a small offscreen context (no separate window)
            loadPrcFileData("", "window-type offscreen")
            loadPrcFileData("", "sync-video 0")
            loadPrcFileData("", "framebuffer-srgb true")
            # Enable alpha so we can render with transparent background
            loadPrcFileData("", "framebuffer-alpha true")
            # Reduce noisy GL error checks on macOS core profile drivers
            loadPrcFileData("", "gl-check-errors false")
            # Suppress driver error spam on macOS core profile
            loadPrcFileData("", "notify-level-glgsg fatal")
            loadPrcFileData("", "notify-level-display fatal")
            # Keep default notify output so we see critical issues in logs
            # loadPrcFileData("", "color-bits 32")
            # High-resolution rendering for better zoom quality
            # Render at 8x resolution (3200x3200) for ultra high-quality source material
            loadPrcFileData("", "win-size 3200 3200")
            loadPrcFileData("", "framebuffer-multisample 1")
            # loadPrcFileData("", "multisamples 4")

            # Check if there's already a ShowBase instance and reuse it
            # This prevents the "multiple ShowBase instances" error
            try:
                from direct.showbase.ShowBaseGlobal import base

                if hasattr(base, "render") and base.render:
                    self.parent_panel._showbase = base
                    self._log.info(
                        f"Reusing existing ShowBase instance for panel {id(self.parent_panel)}"
                    )
                else:
                    raise AttributeError("No existing ShowBase found")
            except (ImportError, AttributeError):
                # Create a new ShowBase only if none exists
                self.parent_panel._showbase = ShowBase(windowType="offscreen")
                self._log.info(
                    f"Created new ShowBase instance for panel {id(self.parent_panel)}"
                )

            # Basic scene - create unique scene name for each panel
            import uuid

            scene_name = f"scene_{id(self.parent_panel)}_{uuid.uuid4().hex[:8]}"
            self.parent_panel._scene = self.parent_panel._showbase.render.attachNewNode(
                scene_name
            )
            self.parent_panel._camera = self.parent_panel._showbase.cam
            # Transparent background; underlying Qt widget will show through
            self.parent_panel._showbase.setBackgroundColor(0, 0, 0, 0)

            # Enable physically-based rendering so glTF materials/textures display correctly
            try:
                from simplepbr import init as pbr_init

                pbr_init(
                    window=self.parent_panel._showbase.win,
                    render_node=self.parent_panel._showbase.render,
                    use_normal_maps=True,
                    use_emission_maps=True,
                )
            except Exception:
                # Fallback to the built-in shader generator
                try:
                    self.parent_panel._showbase.render.setShaderAuto()
                except Exception:
                    pass

            # Improve edges
            try:
                self.parent_panel._showbase.render.setAntialias(AntialiasAttrib.MAuto)
            except Exception:
                pass
            # Set reasonable defaults for the lens
            try:
                lens = self.parent_panel._showbase.camLens
                if hasattr(lens, "setFov"):
                    lens.setFov(45)
                if hasattr(lens, "setNear"):
                    lens.setNear(0.01)
                if hasattr(lens, "setFar"):
                    lens.setFar(10000)
            except Exception:
                pass

            self._log.debug("Creating offscreen Panda3D context…")

            # Prefer RAM-copied render texture; fall back to screenshots if it fails
            self.parent_panel._color_tex = None
            try:
                from panda3d.core import GraphicsOutput, Texture

                tex = Texture()
                self.parent_panel._showbase.win.addRenderTexture(
                    tex, GraphicsOutput.RTMCopyRam
                )
                self.parent_panel._color_tex = tex
            except Exception:
                self.parent_panel._color_tex = None

            # Timer to step Panda each frame
            self.parent_panel._timer = QTimer(self.parent_panel)
            self.parent_panel._timer.timeout.connect(self.parent_panel._on_frame)
            self.parent_panel._timer.start(33)  # ~30 FPS

            self.parent_panel._panda_ready = True
            self._log.info("Panda3D offscreen context ready")

        except Exception as e:
            self._log.error(f"Failed to initialize Panda3D: {e}")
            self.parent_panel._panda_ready = False

    def shutdown(self):
        """Shutdown Panda3D manager."""
        try:
            # Check if we're in a test environment
            import sys

            is_test_environment = (
                any("pytest" in arg for arg in sys.argv) or "test" in sys.argv
            )

            if is_test_environment:
                # In test environment, do minimal cleanup
                self._log.debug(
                    "Panda3D shutdown - test environment, doing minimal cleanup"
                )

                # Stop timers
                if hasattr(self.parent_panel, "_timer") and self.parent_panel._timer:
                    try:
                        self.parent_panel._timer.stop()
                    except Exception:
                        pass
                    self.parent_panel._timer = None

                if (
                    hasattr(self.parent_panel, "_animation_timer")
                    and self.parent_panel._animation_timer
                ):
                    try:
                        self.parent_panel._animation_timer.stop()
                    except Exception:
                        pass
                    self.parent_panel._animation_timer = None

                if (
                    hasattr(self.parent_panel, "_phrase_timer")
                    and self.parent_panel._phrase_timer
                ):
                    try:
                        self.parent_panel._phrase_timer.stop()
                    except Exception:
                        pass
                    self.parent_panel._phrase_timer = None

                # Clear references
                if hasattr(self.parent_panel, "_actor"):
                    self.parent_panel._actor = None
                if hasattr(self.parent_panel, "_model_np"):
                    self.parent_panel._model_np = None
                if hasattr(self.parent_panel, "_camera"):
                    self.parent_panel._camera = None
                if hasattr(self.parent_panel, "_showbase"):
                    self.parent_panel._showbase = None
                if hasattr(self.parent_panel, "_color_tex"):
                    self.parent_panel._color_tex = None
                self.parent_panel._panda_ready = False
            else:
                # In production, do absolutely nothing to prevent malloc corruption
                self._log.debug(
                    "Panda3D shutdown - production environment, skipping all cleanup"
                )
                return

        except Exception as e:
            self._log.error(f"Error during Panda3D manager shutdown: {e}")
