from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, cast

from ...utils.logger import get_logger

try:
    from PySide6.QtCore import QCoreApplication, QLibraryInfo, QObject, QSize, Qt, QUrl
    from PySide6.QtGui import QColor, QVector3D
    from PySide6.QtQuick import QQuickView
    from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWidgets import QVBoxLayout, QWidget
except Exception:  # pragma: no cover - CI may mock Qt
    QQuickView = object  # type: ignore
    QWidget = object  # type: ignore
    QVBoxLayout = object  # type: ignore
    QUrl = object  # type: ignore
    QObject = object  # type: ignore
    QVector3D = object  # type: ignore


class Quick3DGesturePanel(QWidget):
    """QtQuick3D-backed panel that loads a GLB and poses joints procedurally.

    Public API mirrors the previous panel:
    - load_character(model_path: str)
    - set_language(code: str)
    - play_gesture(char_code: str, hand: str)
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._log = get_logger("helpmesign.quick3d.panel")
        self._language: str = "generic"
        self._model_path: Optional[str] = None
        self._joint_cache: Dict[str, QObject] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._layout = layout

        # Ensure Qt can locate plugins: only add the root plugins path
        try:
            plugins_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)
            if plugins_path:
                QCoreApplication.addLibraryPath(plugins_path)
        except Exception:
            pass

        # Web fallback viewer (three.js) - added but hidden unless needed
        self._web = QWebEngineView(self)
        try:
            # Allow local HTML to import remote modules and read local files
            s = self._web.settings()
            s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            s.setAttribute(
                QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
            )
            s.setAttribute(
                QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True
            )
        except Exception:
            pass
        # Hook JS console to Python logs for diagnostics
        try:

            class _LoggingWebPage(QWebEnginePage):
                def __init__(self, logger, parent=None):
                    super().__init__(parent)
                    self._logger = logger

                def javaScriptConsoleMessage(
                    self, level, message, lineNumber, sourceID
                ):
                    self._logger.info(
                        f"WebConsole[{level}] {sourceID}:{lineNumber}: {message}"
                    )

            self._web.setPage(_LoggingWebPage(self._log, self._web))
        except Exception:
            pass
        layout.addWidget(self._web)
        # Start with web collapsed; we prefer Quick3D when available
        try:
            self._web.setVisible(False)
            self._web.setMaximumHeight(0)
        except Exception:
            pass

        # Try native QtQuick3D first
        self._view = None
        self._quick_container = None
        self._use_quick3d = False
        try:
            self._view = QQuickView()
            try:
                self._view.setColor(QColor(0, 0, 0, 0))
                self._view.setResizeMode(QQuickView.ResizeMode.SizeRootObjectToView)
            except Exception:
                pass
            try:
                self._quick_container = QWidget.createWindowContainer(self._view, self)
                self._quick_container.setMinimumSize(1, 1)
                self._quick_container.setFocusPolicy(Qt.FocusPolicy.TabFocus)
                layout.insertWidget(0, self._quick_container)
                try:
                    # Make the Quick3D container consume available space
                    self._layout.setStretch(0, 1)
                    self._layout.setStretch(1, 0)
                except Exception:
                    pass
            except Exception:
                self._quick_container = None
        except Exception:
            self._view = None

        # Load QML scene (resolve via ResourceManager to project root)
        try:
            from ...utils.resource_manager import ResourceManager

            qml_path = (
                Path(ResourceManager().base_path)
                / "resources"
                / "qml"
                / "CharacterView.qml"
            )
        except Exception:
            # Fallback: climb five levels from this file to project root
            qml_path = (
                Path(__file__).resolve().parent.parent.parent.parent.parent
                / "resources"
                / "qml"
                / "CharacterView.qml"
            )
        # Attempt to load QML into view
        self._qml_path = QUrl.fromLocalFile(str(qml_path))
        self._root = None
        try:
            if self._view is not None:
                self._view.setSource(self._qml_path)
                self._root = self._view.rootObject()
                if self._root:
                    self._use_quick3d = True
                    if self._quick_container:
                        self._quick_container.setVisible(True)
                        try:
                            self._quick_container.setMaximumHeight(16777215)
                        except Exception:
                            pass
                    try:
                        self._web.setVisible(False)
                        self._web.setMaximumHeight(0)
                    except Exception:
                        pass
                    self._log.info(
                        "QtQuick3D initialized successfully; using native renderer"
                    )
                else:
                    self._log.warning(
                        "QtQuick3D root not created; falling back to web viewer"
                    )
                    if self._quick_container:
                        self._quick_container.setVisible(False)
                        try:
                            self._quick_container.setMaximumHeight(0)
                        except Exception:
                            pass
                    try:
                        self._web.setVisible(True)
                        self._web.setMaximumHeight(16777215)
                    except Exception:
                        pass
        except Exception:
            self._log.exception(
                "Error initializing QtQuick3D; falling back to web viewer"
            )
            if self._quick_container:
                try:
                    self._quick_container.setVisible(False)
                    self._quick_container.setMaximumHeight(0)
                except Exception:
                    pass
            try:
                self._web.setVisible(True)
                self._web.setMaximumHeight(16777215)
            except Exception:
                pass

    # ---------- Public API ----------
    def set_language(self, code: str) -> None:
        self._language = (code or "generic").lower()
        # No-op for now; reserved for per-language model/pose tweaks

    def load_character(self, model_path: str) -> None:
        self._model_path = model_path
        try:
            from PySide6.QtCore import QUrl

            path_str = str(model_path)
            if self._use_quick3d and self._root is not None:
                # Use native Quick3D
                url = (
                    QUrl.fromLocalFile(path_str)
                    if not path_str.startswith("file://")
                    else QUrl(path_str)
                )
                self._root.setProperty("modelSource", url)
                if self._quick_container:
                    self._quick_container.setVisible(True)
                    try:
                        self._quick_container.setMaximumHeight(16777215)
                    except Exception:
                        pass
                try:
                    self._web.setVisible(False)
                    self._web.setMaximumHeight(0)
                except Exception:
                    pass
                self._log.info(f"Quick3D model set: {url.toString()}")
            else:
                # Fallback to web viewer
                if self._quick_container:
                    self._quick_container.setVisible(False)
                    try:
                        self._quick_container.setMaximumHeight(0)
                    except Exception:
                        pass
                try:
                    self._web.setVisible(True)
                    self._web.setMaximumHeight(16777215)
                except Exception:
                    pass
                if not path_str.startswith("file://"):
                    url = QUrl.fromLocalFile(path_str)
                else:
                    url = QUrl(path_str)
                try:
                    from ...utils.resource_manager import ResourceManager

                    html_path = (
                        Path(ResourceManager().base_path)
                        / "resources"
                        / "web"
                        / "three_viewer.html"
                    )
                except Exception:
                    html_path = (
                        Path(__file__).resolve().parent.parent.parent.parent.parent
                        / "resources"
                        / "web"
                        / "three_viewer.html"
                    )
                viewer = QUrl.fromLocalFile(str(html_path))
                try:
                    encoded_bytes = QUrl.toPercentEncoding(url.toString())
                    # mypy: QUrl.toPercentEncoding returns QByteArray; cast for typing
                    encoded = cast(bytes, encoded_bytes.data()).decode(
                        "utf-8", "ignore"
                    )
                except Exception:
                    encoded = url.toString()
                viewer_with_src_str = viewer.toString() + "?src=" + encoded
                self._log.info(f"Loading 3D viewer: {viewer_with_src_str}")
                try:
                    self._web.setUrl(QUrl("about:blank"))
                except Exception:
                    pass
                self._web.setUrl(QUrl(viewer_with_src_str))
            self._joint_cache.clear()
        except Exception:
            self._log.exception("Failed to set model source")

    def play_gesture(self, char_code: str, hand: str) -> None:
        letter = (char_code or "").strip().upper()
        if letter == "A":
            self._pose_a(hand)

    # ---------- Helpers ----------
    # Placeholder for future QML signal hook
    def _node(self, name: str) -> Optional[QObject]:
        if name in self._joint_cache:
            return self._joint_cache[name]
        try:
            if not self._root:
                return None
            obj = self._root.findChild(QObject, name)  # search by objectName from GLB
            if obj is not None:
                self._joint_cache[name] = obj
            return obj
        except Exception:
            return None

    def _set_euler(
        self, joint_name: str, h: float = 0.0, p: float = 0.0, r: float = 0.0
    ) -> None:
        node = self._node(joint_name)
        if not node:
            return
        try:
            node.setProperty("eulerRotation", QVector3D(h, p, r))
        except Exception:
            pass

    def _pose_a(self, hand: str) -> None:
        # Names follow UE-style used by your GLB
        side = "r" if (hand or "").lower().startswith("r") else "l"
        # Reset relevant joints to zero
        for base in (
            f"clavicle_{side}",
            f"upperarm_{side}",
            f"lowerarm_{side}",
            f"hand_{side}",
            f"thumb_01_{side}",
            f"thumb_02_{side}",
            f"thumb_03_{side}",
            f"index_01_{side}",
            f"index_02_{side}",
            f"index_03_{side}",
            f"middle_01_{side}",
            f"middle_02_{side}",
            f"middle_03_{side}",
            f"ring_01_{side}",
            f"ring_02_{side}",
            f"ring_03_{side}",
            f"pinky_01_{side}",
            f"pinky_02_{side}",
            f"pinky_03_{side}",
        ):
            self._set_euler(base, 0.0, 0.0, 0.0)

        # Bring arm forward and bend elbow slightly
        roll_sign = -1.0 if side == "r" else 1.0
        self._set_euler(f"clavicle_{side}", 0.0, -20.0, 10.0 * roll_sign)
        self._set_euler(f"upperarm_{side}", 0.0, -30.0, 15.0 * roll_sign)
        self._set_euler(f"lowerarm_{side}", 0.0, -40.0, 0.0)
        self._set_euler(f"hand_{side}", 0.0, 10.0, 0.0)

        # Curl fingers for a fist
        curl_p = -55.0
        minor_p = -35.0
        for finger in ("index", "middle", "ring", "pinky"):
            self._set_euler(f"{finger}_01_{side}", 0.0, curl_p, 0.0)
            self._set_euler(f"{finger}_02_{side}", 0.0, minor_p, 0.0)
            self._set_euler(f"{finger}_03_{side}", 0.0, minor_p, 0.0)

        # Thumb along the side
        self._set_euler(f"thumb_01_{side}", 0.0, -15.0, 15.0)
        self._set_euler(f"thumb_02_{side}", 0.0, -20.0, 0.0)
        self._set_euler(f"thumb_03_{side}", 0.0, -10.0, 0.0)
