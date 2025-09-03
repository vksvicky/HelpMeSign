"""
Main AnimateGesturePanel class for Learn mode.
Coordinates all managers and provides the public API for 3D character animation.
"""

from typing import Any, Dict, List, Optional, TypedDict

from ....utils.logger import get_logger

try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QImage, QPixmap
    from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
except Exception:  # pragma: no cover - tests may mock Qt imports

    class QTimer:  # type: ignore[no-redef]
        pass

    class QLabel:  # type: ignore[no-redef]
        pass

    class QWidget:  # type: ignore[no-redef]
        class SizePolicy:
            Expanding = 0
            Fixed = 1

    class QVBoxLayout:  # type: ignore[no-redef]
        pass

    class Qt:  # type: ignore[no-redef]
        class AlignmentFlag:
            AlignCenter = 0

        class WidgetAttribute:
            WA_StyledBackground = 0
            WA_TranslucentBackground = 0

    class QImage:  # type: ignore[no-redef]
        pass

    class QPixmap:  # type: ignore[no-redef]
        pass


from .animation_manager import AnimationManager
from .model_manager import ModelManager
from .panda3d_manager import Panda3DManager
from .rendering_manager import RenderingManager


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

    # Public API methods
    def set_language(self, code: str) -> None:
        """Set the sign language code."""
        # This would typically set up the sign language loader
        pass

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
        self, phrase: str, language: str = "ASL", hand: str = "right"
    ) -> None:
        """Play a phrase with letter-by-letter animation."""
        try:
            # For now, we ignore the language parameter as it's not used in the current implementation
            # This maintains backward compatibility with the existing code
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

    def resizeEvent(self, event):
        """Handle resize events."""
        if not self._headless:
            super().resizeEvent(event)
            self._rendering_manager.update_render_target_size()

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
            from ....core.startup import get_theme

            return get_theme()
        except Exception:
            # Fallback to default Light theme
            return "Light"

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
