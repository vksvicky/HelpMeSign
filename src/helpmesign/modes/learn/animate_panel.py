"""
Panda3D-backed animation panel for Learn mode.
Renders a 3D character inside a Qt widget area without blocking the Qt event loop.

Notes:
- We construct Panda3D ShowBase lazily and step the taskMgr via a QTimer.
- We render to an offscreen buffer and blit to a QLabel as a QImage for simplicity.
- All imports are guarded so tests without Panda3D still run.
"""

from typing import Any, Dict, Optional

from ...utils.logger import get_logger

try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QImage, QPixmap
    from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
except Exception:  # pragma: no cover - tests may mock Qt imports
    QTimer = object  # type: ignore
    QLabel = object  # type: ignore
    QWidget = object  # type: ignore
    QVBoxLayout = object  # type: ignore
    Qt = object  # type: ignore
    QImage = object  # type: ignore
    QPixmap = object  # type: ignore


class AnimateGesturePanel(QWidget):
    """Lightweight wrapper to render Panda3D frames into a Qt widget.

    Public API:
    - load_character(model_path: str)
    - set_language(code: str)
    - play_gesture(char_code: str, hand: str)
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        # If no QApplication exists (e.g., tests before Qt mocks), avoid QWidget init
        self._log = get_logger("helpmesign.modes.learn.animate_panel")
        self._headless: bool = False

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

            can_build_qwidget = QApplication.instance() is not None
        except Exception:
            can_build_qwidget = False

        if can_build_qwidget:
            super().__init__(parent)
            # Render target
            self._display = QLabel(self)
            try:
                self._display.setAlignment(Qt.AlignmentFlag.AlignCenter)
            except Exception:
                pass
            self._display.setText("3D panel (inactive)")
            try:
                # Allow stylesheet border/background on this widget to paint
                self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
                self.setAutoFillBackground(False)
                # Make the inner QLabel fully transparent for compositing
                self._display.setAttribute(
                    Qt.WidgetAttribute.WA_TranslucentBackground, True
                )
                self._display.setAutoFillBackground(False)
                # Transparent background so Panda3D alpha shows through
                self._display.setStyleSheet(
                    "background: transparent; color:#80838a; font-size:13px;"
                )
            except Exception:
                pass

            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self._display)
        else:
            # Headless path: do not invoke QWidget ctor; keep as inert object
            self._headless = True
            self._display = _make_stub_label()

        # Panda runtime (lazy)
        self._panda_ready = False
        self._timer: Optional[QTimer] = None
        self._language: str = "ASL"
        self._character_model: Optional[str] = None
        self._current_model: Optional[str] = None
        self._clip_map: Dict[str, Dict[str, str]] = {}
        self._has_frame: bool = False
        self._pixel_ratio: float = 1.0
        self._capture_every_n_frames: int = 1
        self._capture_counter: int = 0
        # Render-to-RAM texture (created in _ensure_panda). Annotated to satisfy mypy.
        self._color_tex: Optional[Any] = None

    # No-op overrides in headless mode so callers can still set properties safely
    def setObjectName(self, name: str) -> None:
        if getattr(self, "_headless", False):
            self._object_name = name
            return
        try:
            return super().setObjectName(name)
        except Exception:
            return None

    def setFixedHeight(self, h: int) -> None:
        if getattr(self, "_headless", False):
            self._fixed_height = h
            return
        try:
            return super().setFixedHeight(h)
        except Exception:
            return None

    def setSizePolicy(self, *args, **kwargs) -> None:
        if getattr(self, "_headless", False):
            return None
        try:
            return super().setSizePolicy(*args, **kwargs)
        except Exception:
            return None

    def setStyleSheet(self, *args, **kwargs) -> None:
        if getattr(self, "_headless", False):
            return None
        try:
            return super().setStyleSheet(*args, **kwargs)
        except Exception:
            return None

    # ---------- Public API ----------
    def set_language(self, code: str) -> None:
        self._language = code or self._language

    def load_character(self, model_path: str) -> None:
        # Debounce duplicate requests
        if self._current_model and str(self._current_model) == str(model_path):
            return
        self._character_model = model_path
        if getattr(self, "_headless", False):
            return
        self._ensure_panda()
        self._load_model_internal(model_path)

    def play_gesture(self, char_code: str, hand: str) -> None:
        if getattr(self, "_headless", False):
            return
        if not self._panda_ready:
            return
        self._play_clip_internal(char_code, hand)

    # ---------- Panda engine setup ----------
    def _ensure_panda(self) -> None:
        if self._panda_ready:
            return
        try:
            # Panda imports
            from direct.showbase.ShowBase import ShowBase  # type: ignore
            from panda3d.core import AntialiasAttrib, loadPrcFileData  # type: ignore

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

            self._showbase = ShowBase(windowType="offscreen")

            # Basic scene
            self._scene = self._showbase.render.attachNewNode("scene")
            self._camera = self._showbase.cam
            # Transparent background; underlying Qt widget will show through
            self._showbase.setBackgroundColor(0, 0, 0, 0)

            # Enable physically-based rendering so glTF materials/textures display correctly
            try:
                from simplepbr import init as pbr_init

                pbr_init(
                    window=self._showbase.win,
                    render_node=self._showbase.render,
                    use_normal_maps=True,
                    use_emission_maps=True,
                )
            except Exception:
                # Fallback to the built-in shader generator
                try:
                    self._showbase.render.setShaderAuto()
                except Exception:
                    pass

            # Improve edges
            try:
                self._showbase.render.setAntialias(AntialiasAttrib.MAuto)
            except Exception:
                pass
            # Set reasonable defaults for the lens
            try:
                lens = self._showbase.camLens
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
            self._color_tex = None
            try:
                from panda3d.core import GraphicsOutput, Texture

                tex = Texture()
                self._showbase.win.addRenderTexture(tex, GraphicsOutput.RTMCopyRam)
                self._color_tex = tex
            except Exception:
                self._color_tex = None

            # Timer to step Panda each frame
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._on_frame)
            self._timer.start(33)  # ~30 FPS

            self._panda_ready = True
            self._display.setText("3D loading…")
            self._log.info("Panda3D offscreen context ready")

            # Initialize render size to match current widget size
            try:
                self._update_render_target_size()
            except Exception:
                pass
        except Exception:
            # If Panda is not available, keep panel inert
            self._display.setText("3D not available")
            self._panda_ready = False
            try:
                import traceback

                self._log.exception("Failed to initialize Panda3D offscreen context")
            except Exception:
                pass

    def _load_model_internal(self, model_path: str) -> None:
        try:
            if not self._panda_ready:
                return
            from panda3d.core import Loader

            # Clear existing model
            for child in list(self._scene.getChildren()):
                child.removeNode()

            self._log.info(f"Loading 3D model: {model_path}")
            node = self._showbase.loader.loadModel(model_path)
            node.reparentTo(self._scene)
            try:
                # Bake model-space transforms so bounds are accurate
                node.clearModelNodes()
                node.flattenStrong()
            except Exception:
                pass
            # Normalize orientation to face camera (Y forward). Many tools export Z-up.
            try:
                # Rotate to face camera (front view), adjust yaw as needed for this asset
                node.setHpr(-90, 0, 0)
            except Exception:
                pass
            # Frame and center the model to a comfortable, fully visible size
            self._frame_model(node, fill_fraction=0.75)
            self._current_model = str(model_path)

            # Simple light (optional)
            try:
                from panda3d.core import AmbientLight, DirectionalLight

                amb = AmbientLight("amb")
                amb.setColor((0.6, 0.6, 0.6, 1))
                amb_np = self._scene.attachNewNode(amb)
                self._scene.setLight(amb_np)

                key = DirectionalLight("key")
                key.setColor((0.8, 0.8, 0.8, 1))
                key_np = self._scene.attachNewNode(key)
                key_np.setHpr(-30, -20, 0)
                self._scene.setLight(key_np)
            except Exception:
                pass

            # Keep the loading text until the first frame blits
            if not getattr(self, "_has_frame", False):
                self._display.setText("3D ready – awaiting first frame…")
            self._log.info("Model loaded successfully")
        except Exception:
            self._display.setText("Failed to load model")
            try:
                self._log.exception("Failed to load 3D model")
            except Exception:
                pass

    def _frame_model(self, node, fill_fraction: float = 0.55) -> None:
        """Center the model and set camera distance so it fills the view.

        fill_fraction controls how much of the vertical FOV the model height should occupy.
        """
        try:
            import math

            from panda3d.core import Point3

            # Compute tight bounds in model space
            min_pt, max_pt = node.getTightBounds()
            if not min_pt or not max_pt:
                # Fallback: simple placement
                node.setPos(0, 3.0, 0)
                node.setScale(1.5)
                self._camera.setPos(0, -6.0, 1.5)
                self._camera.lookAt(node)
                return

            size = max_pt - min_pt
            center = (min_pt + max_pt) * 0.5

            # Move model so its center is at the origin
            node.setPos(-center.x, -center.y, -center.z)

            # Use bounding sphere radius to compute distance
            radius = max(1e-3, max(size.x, size.y, size.z) * 0.5)
            lens = self._showbase.camLens
            fov_v_deg = 40.0
            try:
                fov = lens.getFov()
                if len(fov) == 2:
                    fov_v_deg = float(fov[1])
            except Exception:
                pass
            fov_v = math.radians(max(1.0, fov_v_deg))
            distance = (radius / math.tan(fov_v * 0.5)) / max(
                0.2, min(0.95, fill_fraction)
            )
            distance = distance * 2.0  # back off more to fit whole body

            # Place camera on -Y looking at the model center
            self._camera.setPos(0, -distance, radius * 0.4)
            self._camera.lookAt(0, 0, radius * 0.2)

            # Keep neutral scaling
            node.setScale(1.0)
        except Exception:
            # Non-fatal framing issues should not break the panel
            try:
                node.setPos(0, 3.0, 0)
                node.setScale(1.5)
                self._camera.setPos(0, -6.0, 1.5)
                self._camera.lookAt(node)
            except Exception:
                pass

    def _play_clip_internal(self, char_code: str, hand: str) -> None:
        # Placeholder: in a follow-up pass we will map clip names and advance animations
        # based on (self._language, char_code, hand). For now, no-op to keep panel stable.
        pass

    # ---------- Frame pump ----------
    def _on_frame(self) -> None:
        try:
            if not self._panda_ready:
                return
            self._showbase.taskMgr.step()

            # Attempt RAM image first
            image_updated = False
            if self._color_tex is not None:
                try:
                    tex = self._color_tex
                    if tex.hasRamImage():
                        data = tex.getRamImageAs("RGBA")
                        width = tex.getXSize()
                        height = tex.getYSize()
                        stride = width * 4
                        img = QImage(
                            bytes(data), width, height, stride, QImage.Format_RGBA8888  # type: ignore[attr-defined]
                        ).mirrored(False, True)
                        self._display.setPixmap(QPixmap.fromImage(img))
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
                    ok = self._showbase.win.getScreenshot(pimg)
                    if ok:
                        width = pimg.getXSize()
                        height = pimg.getYSize()
                        data = pimg.getRamImageAs("RGBA")
                        stride = width * 4
                        img = QImage(
                            bytes(data), width, height, stride, QImage.Format_RGBA8888  # type: ignore[attr-defined]
                        ).mirrored(False, True)
                        self._display.setPixmap(QPixmap.fromImage(img))
                        image_updated = True
                except Exception:
                    pass

            if image_updated and not self._has_frame:
                self._has_frame = True
                self._display.setText("")
                try:
                    self._log.info("First frame displayed in 3D panel")
                except Exception:
                    pass
        except Exception:
            # Keep silent in production; no need to spam logs if frames drop
            pass

    # ---------- Resize handling ----------
    def resizeEvent(self, event):
        """Ensure the offscreen buffer matches the widget size for crisp output."""
        try:
            # Call base implementation when we are a real QWidget
            if not getattr(self, "_headless", False):
                try:
                    super().resizeEvent(event)
                except Exception:
                    pass

            # Update Panda3D render target size if running
            self._update_render_target_size()
        except Exception:
            pass

    def _update_render_target_size(self) -> None:
        """Resize Panda3D offscreen window to the widget size (no-op if inactive)."""
        try:
            if getattr(self, "_headless", False):
                return
            if not getattr(self, "_panda_ready", False):
                return

            w = max(1, int(self.width()))
            h = max(1, int(self.height()))

            # Account for device pixel ratio for HiDPI displays
            ratio = 1.0
            try:
                wh = self.window().windowHandle() if self.window() else None
                if wh and hasattr(wh, "devicePixelRatio"):
                    ratio = float(wh.devicePixelRatio()) or 1.0
            except Exception:
                ratio = 1.0

            rw = max(32, int(w * ratio))
            rh = max(32, int(h * ratio))
            self._pixel_ratio = ratio

            try:
                self._showbase.win.setSize(rw, rh)
            except Exception:
                pass
        except Exception:
            pass
