"""
Panda3D initialization and model loading for AnimateGesturePanel.
Extracted from animate_panel.py to reduce file size.
"""

from typing import Any, Optional

from ...utils.logger import get_logger

try:
    from PySide6.QtCore import QTimer
except Exception:  # pragma: no cover - tests may mock Qt imports

    class QTimer:  # type: ignore[no-redef]
        pass


class Panda3DManager:
    """Manages Panda3D initialization and model loading for AnimateGesturePanel"""

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
            # Start tiny; we'll resize to the widget in resizeEvent
            loadPrcFileData("", "win-size 640 640")
            loadPrcFileData("", "framebuffer-multisample 1")
            # loadPrcFileData("", "multisamples 4")

            # Check if ShowBase already exists
            try:
                from direct.showbase.ShowBaseGlobal import base

                if hasattr(base, "render"):
                    self.parent_panel._showbase = base
                    self._log.info("Using existing ShowBase instance")
                else:
                    raise AttributeError("Existing ShowBase not properly initialized")
            except (ImportError, AttributeError):
                # Create new ShowBase instance
                self.parent_panel._showbase = ShowBase(windowType="offscreen")

            # Basic scene
            self.parent_panel._scene = self.parent_panel._showbase.render.attachNewNode(
                "scene"
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
            self.parent_panel._display.setText("3D loading…")
            self._log.info("Panda3D offscreen context ready")

            # Initialize render size to match current widget size
            try:
                self.parent_panel._update_render_target_size()
            except Exception:
                pass
        except Exception:
            # If Panda is not available, keep panel inert
            self.parent_panel._display.setText("3D not available")
            self.parent_panel._panda_ready = False
            try:
                import traceback

                self._log.exception("Failed to initialize Panda3D offscreen context")
            except Exception:
                pass

    def load_model_internal(self, model_path: str) -> None:
        """Load 3D model with default neutral pose."""
        try:
            if not self.parent_panel._panda_ready:
                return

            # Clear existing model
            for child in list(self.parent_panel._scene.getChildren()):
                child.removeNode()

            # Load the model
            self._log.info(f"Loading 3D model: {model_path}")
            try:
                from panda3d.core import (  # type: ignore[attr-defined]
                    Filename,
                    NodePath,
                )
            except ImportError:
                # Fallback import path
                from panda3d import Filename, NodePath  # type: ignore[attr-defined]

            # Load as Actor for skeletal control
            try:
                from direct.actor.Actor import Actor

                self.parent_panel._actor = Actor(
                    model_path,
                    {
                        "idle": model_path,
                    },
                )
                self.parent_panel._model_np = self.parent_panel._actor
                self.parent_panel._log.info(
                    "Loaded model as Actor for skeletal control"
                )
            except Exception:
                # Fallback to regular model loading
                self.parent_panel._model_np = (
                    self.parent_panel._showbase.loader.loadModel(Filename(model_path))
                )
                self.parent_panel._actor = None
                self.parent_panel._log.info("Loaded model as regular NodePath")

            # Parent to scene
            self.parent_panel._model_np.reparentTo(self.parent_panel._scene)

            # Apply default neutral pose
            self.parent_panel._apply_default_neutral_pose()

            # Set up camera and lighting
            self.parent_panel._set_camera_for_default_pose()
            self.parent_panel._setup_lighting()

            # Frame the model
            self.parent_panel._frame_model(self.parent_panel._model_np)

            self.parent_panel._log.info(
                "Applied model's natural pose and positioned camera for optimal viewing"
            )

        except Exception as e:
            self._log.error(f"Error loading model {model_path}: {e}")
            self.parent_panel._model_np = None
            self.parent_panel._actor = None

    def apply_default_neutral_pose(self):
        """Apply a default neutral pose to the model."""
        try:
            if not self.parent_panel._model_np:
                return

            # Try to get the model's natural pose
            if self.parent_panel._actor:
                # For Actor models, play the idle animation
                try:
                    self.parent_panel._actor.loop("idle")
                except Exception:
                    # If no idle animation, just use the default pose
                    pass
            else:
                # For regular models, try to find and apply a neutral pose
                try:
                    # Look for common neutral pose names
                    neutral_poses = [
                        "neutral",
                        "idle",
                        "rest",
                        "default",
                        "T-pose",
                        "A-pose",
                    ]
                    for pose_name in neutral_poses:
                        try:
                            if hasattr(self.parent_panel._model_np, "pose") and hasattr(
                                self.parent_panel._model_np, "setPose"
                            ):
                                self.parent_panel._model_np.setPose(pose_name)
                                break
                        except Exception:
                            continue
                except Exception:
                    pass

            self.parent_panel._log.info(
                "Using character's natural model pose - no joint modifications applied"
            )

        except Exception as e:
            self._log.error(f"Error applying default neutral pose: {e}")

    def set_camera_for_default_pose(self) -> None:
        """Set up camera for viewing the default pose."""
        try:
            if not self.parent_panel._model_np:
                return

            # Position camera for front-facing view
            self.parent_panel._camera.setPos(0, -5, 1.5)  # Back and slightly up
            self.parent_panel._camera.lookAt(self.parent_panel._model_np)

            self.parent_panel._log.info(
                "Camera positioned for front-facing T-pose view"
            )

        except Exception as e:
            self._log.error(f"Error setting camera: {e}")

    def setup_lighting(self):
        """Set up lighting for the 3D scene."""
        try:
            if not self.parent_panel._showbase:
                return

            # Clear existing lights
            for child in list(self.parent_panel._scene.getChildren()):
                if hasattr(child, "isLight") and child.isLight():
                    child.removeNode()

            # Create ambient light
            from panda3d.core import AmbientLight, DirectionalLight, PointLight, Vec4

            ambient = AmbientLight("ambient")
            ambient.setColor(Vec4(0.3, 0.3, 0.3, 1))
            ambient_np = self.parent_panel._scene.attachNewNode(ambient)
            self.parent_panel._scene.setLight(ambient_np)

            # Create main directional light
            dlight = DirectionalLight("dlight")
            dlight.setColor(Vec4(0.8, 0.8, 0.8, 1))
            dlight_np = self.parent_panel._scene.attachNewNode(dlight)
            dlight_np.setHpr(45, -45, 0)
            self.parent_panel._scene.setLight(dlight_np)

            # Create fill light
            fill = DirectionalLight("fill")
            fill.setColor(Vec4(0.4, 0.4, 0.5, 1))
            fill_np = self.parent_panel._scene.attachNewNode(fill)
            fill_np.setHpr(-45, -45, 0)
            self.parent_panel._scene.setLight(fill_np)

        except Exception as e:
            self._log.error(f"Error setting up lighting: {e}")

    def frame_model(self, node, fill_fraction: float = 0.55) -> None:
        """Frame the model in the camera view."""
        try:
            if not node or not self.parent_panel._camera:
                return

            # Get the model's bounding box
            bounds = node.getBounds()
            if not bounds.isEmpty():
                # Calculate the center and size
                center = bounds.getCenter()
                size = bounds.getSize()
                max_size = max(size.getX(), size.getY(), size.getZ())

                # Position camera to frame the model
                distance = max_size / (2 * fill_fraction)
                camera_pos = center + (0, -distance, distance * 0.3)
                self.parent_panel._camera.setPos(camera_pos)
                self.parent_panel._camera.lookAt(center)

        except Exception as e:
            self._log.error(f"Error framing model: {e}")

    def find_node_by_names(self, names) -> Optional[Any]:
        """Find a node by trying multiple possible names."""
        try:
            if not self.parent_panel._model_np:
                return None

            for name in names:
                try:
                    node = self.parent_panel._model_np.find(f"**/{name}")
                    if node and not node.isEmpty():
                        return node
                except Exception:
                    continue

            return None

        except Exception as e:
            self._log.error(f"Error finding node by names: {e}")
            return None

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

    def dump_node_names(self) -> None:
        """Dump all node names for debugging."""
        try:
            if not self.parent_panel._model_np:
                return

            def print_nodes(node, indent=0):
                print("  " * indent + node.getName())
                for child in node.getChildren():
                    print_nodes(child, indent + 1)

            print("Model node hierarchy:")
            print_nodes(self.parent_panel._model_np)

        except Exception as e:
            self._log.error(f"Error dumping node names: {e}")

    def shutdown(self):
        """Shutdown Panda3D manager."""
        try:
            # Clear Panda3D references
            if hasattr(self.parent_panel, "_actor") and self.parent_panel._actor:
                try:
                    self.parent_panel._actor.cleanup()
                except Exception:
                    pass
                self.parent_panel._actor = None

            if hasattr(self.parent_panel, "_model_np") and self.parent_panel._model_np:
                try:
                    self.parent_panel._model_np.removeNode()
                except Exception:
                    pass
                self.parent_panel._model_np = None

            if hasattr(self.parent_panel, "_camera") and self.parent_panel._camera:
                self.parent_panel._camera = None

            if hasattr(self.parent_panel, "_showbase") and self.parent_panel._showbase:
                try:
                    self.parent_panel._showbase.destroy()
                except Exception:
                    pass
                self.parent_panel._showbase = None

            # Clear texture references
            if hasattr(self.parent_panel, "_color_tex"):
                self.parent_panel._color_tex = None

        except Exception as e:
            self._log.error(f"Error during Panda3D manager shutdown: {e}")
