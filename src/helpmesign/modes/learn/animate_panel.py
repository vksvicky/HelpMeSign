"""
Panda3D-backed animation panel for Learn mode.
Renders a 3D character inside a Qt widget area without blocking the Qt event loop.

Notes:
- We construct Panda3D ShowBase lazily and step the taskMgr via a QTimer.
- We render to an offscreen buffer and blit to a QLabel as a QImage for simplicity.
- All imports are guarded so tests without Panda3D still run.
"""

from typing import Any, Dict, List, Optional, TypedDict, cast

from ...utils.logger import get_logger

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
        pass

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
        self._animation_timer: Optional[QTimer] = None
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
        # Root of currently loaded model
        self._model_np: Optional[Any] = None

        # Per-word animation state
        class _AnimState(TypedDict):
            frames: List[Dict]
            current_frame: int
            total_frames: int
            duration: int
            frame_duration: int

        self._current_animation: Optional[_AnimState] = None
        # Actor for skinned control (preferred when available)
        self._actor: Optional[Any] = None
        # Simple welcome-wave animation (right hand)
        self._wave_active: bool = False
        self._wave_phase: float = 0.0
        self._wave_target: Optional[Any] = None
        # Friendly intro gesture (both hands sway)
        self._intro_active: bool = False
        self._intro_t: float = 0.0
        self._intro_left: Optional[Any] = None
        self._intro_right: Optional[Any] = None
        # Phrase playback (procedural posing from JSON)
        self._phrase_timer: Optional[QTimer] = None
        self._phrase_queue: List[str] = []
        self._phrase_language: str = "ASL"
        self._phrase_hand: str = "right"
        self._joint_cache: Dict[str, Any] = {}

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

    def play_phrase(
        self, phrase: str, language: str = "ASL", hand: str = "right"
    ) -> None:
        """Sign a phrase word by word with smooth animations."""
        try:
            if getattr(self, "_headless", False):
                return
            # Set animation flag to prevent arm position maintenance from interfering
            self._is_animating = True
            self._log.info(
                "Starting word-based phrase animation - setting _is_animating flag"
            )

            self._phrase_language = language or "ASL"
            self._phrase_hand = hand or "right"

            # Split phrase into words for word-based signing
            words = [
                word.strip() for word in (phrase or "").upper().split() if word.strip()
            ]
            self._phrase_queue = words
            self._log.info(f"Split phrase '{phrase}' into words: {words}")

            if not self._phrase_queue:
                self._is_animating = False
                return

            # Zoom in ONCE at the start of the entire phrase
            self._log.info("Phrase starting - zooming in")
            self._zoom_camera_for_signing(True)

            if self._phrase_timer is None:
                self._phrase_timer = QTimer(self)
                self._phrase_timer.timeout.connect(self._on_phrase_step)
            if not self._phrase_timer.isActive():
                self._phrase_timer.start(1000)  # Start with 1 second interval
        except Exception:
            self._is_animating = False
            pass

    def _on_phrase_step(self) -> None:
        """Handle each step of the word-based phrase animation."""
        try:
            if not self._phrase_queue:
                if self._phrase_timer:
                    self._phrase_timer.stop()
                # Reset animation flag
                self._is_animating = False
                self._log.info(
                    "Word-based phrase animation ended - resetting _is_animating flag"
                )
                # Zoom out ONCE at the end of the entire phrase
                self._log.info("Phrase completed - zooming out")
                self._zoom_camera_for_signing(False)
                return

            word = self._phrase_queue.pop(0)
            self._log.info(f"Signing word: {word}")

            # Try to get word pose and animation
            pose = self._get_word_pose_from_signs(
                self._phrase_language, self._phrase_hand, word
            )
            animation = self._get_word_animation_from_signs(
                self._phrase_language, self._phrase_hand, word
            )
            duration = self._get_word_duration_from_signs(
                self._phrase_language, self._phrase_hand, word
            )

            self._log.info(
                f"Word '{word}' - pose: {pose is not None}, animation: {animation is not None}, duration: {duration}"
            )

            if pose and animation:
                # Apply word with smooth animation
                self._log.info(f"Applying word '{word}' with animation")
                self._apply_word_with_animation(pose, animation, duration)
                # Set timer for next word after animation completes
                if self._phrase_timer:
                    self._phrase_timer.setInterval(duration)
            elif pose:
                # Apply static word pose
                self._log.info(f"Applying word '{word}' with static pose")
                # Apply pose (zoom is handled at phrase level)
                self._apply_pose(pose)
                # Set timer for next word
                if self._phrase_timer:
                    self._phrase_timer.setInterval(duration)
            else:
                # Fallback to letter-by-letter for unknown words
                self._log.info(
                    f"No word data found for '{word}', falling back to letter spelling"
                )
                self._spell_word_letters(word)

        except Exception as e:
            self._log.error(f"Error in word-based phrase step: {e}")
            try:
                if self._phrase_timer:
                    self._phrase_timer.stop()
                # Reset animation flag on error
                self._is_animating = False
                self._log.info(
                    "Word-based phrase animation error - resetting _is_animating flag"
                )
                # Zoom out camera on error
                self._zoom_camera_for_signing(False)
            except Exception:
                pass

    def _get_letter_pose_from_signs(
        self, language: str, hand: str, letter: str
    ) -> Optional[Dict[str, List[float]]]:
        try:
            from ...utils.sign_language_loader import SignLanguageLoader

            loader = SignLanguageLoader()
            alphabet = loader.get_alphabet_signs(language or "ASL", hand or "right")
            data = alphabet.get(letter.upper())
            if data and isinstance(data, dict) and "pose" in data:
                pose = data.get("pose")
                if isinstance(pose, dict):
                    return cast(Dict[str, List[float]], pose)
            # Try two-hand generic file if provided
            alphabet_generic = loader.get_alphabet_signs(language or "ASL", "both")
            data2 = alphabet_generic.get(letter.upper())
            if data2 and isinstance(data2, dict) and "pose" in data2:
                pose2 = data2.get("pose")
                if isinstance(pose2, dict):
                    return cast(Dict[str, List[float]], pose2)
        except Exception:
            return None
        return None

    def _get_word_pose_from_signs(
        self, language: str, hand: str, word: str
    ) -> Optional[Dict[str, List[float]]]:
        """Get pose data for a specific word."""
        try:
            from ...utils.sign_language_loader import SignLanguageLoader

            loader = SignLanguageLoader()

            self._log.info(
                f"Looking for word pose: '{word}' in {language} with {hand} hand"
            )

            # For word-based signing, always try "both" hand variant first (generic joint names)
            # This allows word data to work with both hands regardless of user preference
            pose = loader.get_word_pose(language or "ASL", word, "both")
            if pose:
                self._log.info(f"Found word pose for '{word}' in 'both' hand variant")
                return pose

            # Fall back to specific hand variant
            pose = loader.get_word_pose(language or "ASL", word, hand or "right")
            if pose:
                self._log.info(f"Found word pose for '{word}' in '{hand}' hand variant")
                return pose

            self._log.info(f"No word pose found for '{word}' in any hand variant")
            return None
        except Exception as e:
            self._log.error(f"Error getting word pose for '{word}': {e}")
            return None

    def _get_word_animation_from_signs(
        self, language: str, hand: str, word: str
    ) -> Optional[List[Dict]]:
        """Get animation data for a specific word."""
        try:
            from ...utils.sign_language_loader import SignLanguageLoader

            loader = SignLanguageLoader()

            # Try "both" hand variant first (generic joint names)
            animation = loader.get_word_animation(language or "ASL", word, "both")
            if animation:
                return animation

            # Fall back to specific hand variant
            return loader.get_word_animation(language or "ASL", word, hand or "right")
        except Exception as e:
            self._log.error(f"Error getting word animation for '{word}': {e}")
            return None

    def _get_word_duration_from_signs(self, language: str, hand: str, word: str) -> int:
        """Get duration for a specific word animation."""
        try:
            from ...utils.sign_language_loader import SignLanguageLoader

            loader = SignLanguageLoader()

            # Try "both" hand variant first (generic joint names)
            duration = loader.get_word_duration(language or "ASL", word, "both")
            if duration != 1000:  # If we got a non-default duration
                return duration

            # Fall back to specific hand variant
            return loader.get_word_duration(language or "ASL", word, hand or "right")
        except Exception as e:
            self._log.error(f"Error getting word duration for '{word}': {e}")
            return 1000

    def _apply_word_with_animation(
        self, pose: Dict[str, List[float]], animation: List[Dict], duration: int
    ) -> None:
        """Apply word with smooth animation frames."""
        try:
            self._log.info(
                f"Applying word with animation ({len(animation)} frames, {duration}ms)"
            )

            # Set up animation timer for smooth transitions
            if not hasattr(self, "_animation_timer"):
                from PySide6.QtCore import QTimer

                self._animation_timer = QTimer()
                self._animation_timer.timeout.connect(self._on_animation_frame)

            # Store animation data
            self._current_animation = {
                "frames": animation,
                "current_frame": 0,
                "total_frames": len(animation),
                "duration": duration,
                "frame_duration": duration // len(animation) if animation else 100,
            }

            # Start animation timer (poses will be applied in _on_animation_frame)
            if self._animation_timer is not None:
                self._animation_timer.start(self._current_animation["frame_duration"])

        except Exception as e:
            self._log.error(f"Error applying word animation: {e}")

    def _on_animation_frame(self) -> None:
        """Handle each frame of word animation."""
        try:
            if self._current_animation is None:
                if self._animation_timer is not None:
                    self._animation_timer.stop()
                return

            anim = self._current_animation
            if anim["current_frame"] >= anim["total_frames"]:
                # Animation complete
                if self._animation_timer is not None:
                    self._animation_timer.stop()

                # Animation complete - clean up (zoom is handled at phrase level)
                self._log.info("Word animation completed")
                self._current_animation = None
                return

            # Apply current frame
            frame_data = anim["frames"][anim["current_frame"]]
            if "pose" in frame_data:
                self._apply_pose(frame_data["pose"])

            anim["current_frame"] += 1

        except Exception as e:
            self._log.error(f"Error in animation frame: {e}")

    def _spell_word_letters(self, word: str) -> None:
        """Fallback: spell a word letter by letter."""
        try:
            self._log.info(f"Spelling word '{word}' letter by letter")
            letters = [c for c in word.upper() if c.isalnum()]

            # Add letters to queue and set shorter timer
            if self._phrase_timer:
                self._phrase_timer.setInterval(500)  # Faster for letter spelling

            # Insert letters at the beginning of the queue
            self._phrase_queue = letters + self._phrase_queue

        except Exception as e:
            self._log.error(f"Error spelling word letters: {e}")

    def _apply_pose(self, pose: Dict[str, List[float]]) -> None:
        """Apply HPR to joints by name; supports left/right by suffix in keys."""
        try:
            if self._model_np is None:
                return
            # For left-hand requests, remap any *_r keys to *_l before lookup
            use_left = (self._phrase_hand or "right").lower().startswith("l")

            # Track if any joints were successfully moved
            joints_moved = False

            for joint_name, hpr in pose.items():
                try:
                    name = str(joint_name)

                    # Handle generic joint names (without _r/_l suffix)
                    if not name.endswith(("_r", "_l", "_R", "_L")):
                        # For word-based signing, apply to both hands
                        # For word-based signing, apply to both hands
                        # Check if this is word-based signing by looking at the phrase queue content
                        is_word_based = (
                            hasattr(self, "_phrase_queue")
                            and len(getattr(self, "_phrase_queue", [])) > 0
                        )
                        if is_word_based:
                            # This is word-based signing, apply to both hands
                            right_name = name + "_r"
                            left_name = name + "_l"

                            # Try right hand first
                            right_node = self._get_joint_node(right_name)
                            if right_node is not None:
                                h = float(hpr[0])
                                p = float(hpr[1])
                                r = float(hpr[2])
                                right_node.setHpr(h, p, r)
                                joints_moved = True
                                self._log.info(
                                    f"Applied pose to right hand joint: {right_name}"
                                )

                            # Try left hand
                            left_node = self._get_joint_node(left_name)
                            if left_node is not None:
                                h = float(hpr[0])
                                p = float(hpr[1])
                                r = float(hpr[2])
                                left_node.setHpr(h, p, r)
                                joints_moved = True
                                self._log.info(
                                    f"Applied pose to left hand joint: {left_name}"
                                )
                        else:
                            # Letter-based signing, use single hand
                            if use_left:
                                name = name + "_l"
                            else:
                                name = name + "_r"

                            node = self._get_joint_node(name)
                            if node is None:
                                # Retry with common alias variants
                                alias = self._best_alias(name)
                                node = self._get_joint_node(alias)
                            if node is None:
                                continue
                            h = float(hpr[0])
                            p = float(hpr[1])
                            r = float(hpr[2])
                            node.setHpr(h, p, r)
                            joints_moved = True
                    elif use_left:
                        # Remap right-hand suffixes to left-hand
                        if name.endswith("_r"):
                            name = name[:-2] + "_l"
                        elif name.endswith("_R"):
                            name = name[:-2] + "_L"

                        node = self._get_joint_node(name)
                        if node is None:
                            # Retry with common alias variants
                            alias = self._best_alias(name)
                            node = self._get_joint_node(alias)
                        if node is None:
                            continue
                        h = float(hpr[0])
                        p = float(hpr[1])
                        r = float(hpr[2])
                        node.setHpr(h, p, r)
                        joints_moved = True
                    else:
                        # Use original name for right hand
                        node = self._get_joint_node(name)
                        if node is None:
                            # Retry with common alias variants
                            alias = self._best_alias(name)
                            node = self._get_joint_node(alias)
                        if node is None:
                            continue
                        h = float(hpr[0])
                        p = float(hpr[1])
                        r = float(hpr[2])
                        node.setHpr(h, p, r)
                        joints_moved = True
                except Exception as e:
                    self._log.error(f"Error applying pose to joint {name}: {e}")
                    continue

            # For now, don't try to move larger body parts since the character doesn't respond to joint manipulation
            # Instead, let's try to create a simple sign language animation
            if joints_moved:
                self._log.info("Sign language pose applied successfully")
                # Zoom is now handled at the word level, not in _apply_pose
            else:
                self._log.info(
                    "No joints could be moved - character needs custom animations"
                )

        except Exception:
            pass

    def _get_joint_node(self, name: str) -> Optional[Any]:
        """Find and cache a joint/nodepath by exact or partial name match (case-insensitive)."""
        try:
            key = name.lower()
            if key in self._joint_cache:
                return self._joint_cache[key]
            root = self._model_np or self._scene
            if root is None:
                return None
            # If we have an Actor, try controlJoint to obtain a manipulable NodePath
            try:
                if self._actor is not None:
                    from panda3d.core import NodePath  # type: ignore

                    # Try with alias mapping first (since we know the model uses Mixamo-style names)
                    alias = self._best_alias(name)

                    # Try the alias first
                    if alias != name:
                        cj = self._actor.controlJoint(None, "modelRoot", alias)
                        if cj and not cj.isEmpty():
                            self._joint_cache[key] = cj
                            return cj

                    # Fallback to original name
                    cj = self._actor.controlJoint(None, "modelRoot", name)
                    if cj and not cj.isEmpty():
                        self._joint_cache[key] = cj
                        return cj
            except Exception:
                pass
            # Try exact search first
            np = root.find(f"**/{name}")
            if not np.isEmpty():
                self._joint_cache[key] = np
                return np
            # Fallback: scan for case-insensitive match or substring
            all_nodes = root.findAllMatches("**/*")
            for i in range(all_nodes.getNumPaths()):
                cand = all_nodes.getPath(i)
                nm = cand.getName().lower()
                if nm == key or nm.endswith("/" + key) or key in nm:
                    self._joint_cache[key] = cand
                    return cand
            return None
        except Exception:
            return None

    def _apply_fallback_movement(self) -> None:
        """Try to move larger body parts when finger joints are not available."""
        try:
            # Try to move larger body parts that might exist
            fallback_bones = [
                "hand_r",
                "mixamorig:RightHand",
                "RightHand",
                "wrist_r",
                "upperarm_r",
                "mixamorig:RightArm",
                "RightArm",
                "arm_r",
                "shoulder_r",
                "mixamorig:RightShoulder",
                "RightShoulder",
                "clavicle_r",
                "mixamorig:RightClavicle",
                "RightClavicle",
            ]

            for bone_name in fallback_bones:
                bone = self._get_joint_node(bone_name)
                if bone is not None:
                    # Simple rotation to show some movement
                    if "hand" in bone_name.lower() or "wrist" in bone_name.lower():
                        bone.setHpr(0, 0, 45)  # Rotate wrist
                    elif "arm" in bone_name.lower() or "shoulder" in bone_name.lower():
                        bone.setHpr(0, 30, 0)  # Raise arm slightly
                    elif "clavicle" in bone_name.lower():
                        bone.setHpr(0, 15, 0)  # Slight shoulder movement

                    self._log.info(f"Applied fallback movement to {bone_name}")
                    break
        except Exception:
            pass

    def _best_alias(self, name: str) -> str:
        """Generate likely bone name variant for common rigs (e.g., Mixamo)."""
        try:
            # Expect patterns like index_01_r, thumb_02_l
            raw = name.lower()
            # Determine side
            side = (
                "right"
                if raw.endswith("_r")
                else ("left" if raw.endswith("_l") else "right")
            )
            side_cap = side.capitalize()
            # Extract finger and segment index
            finger_map = {
                "thumb": "Thumb",
                "index": "Index",
                "middle": "Middle",
                "ring": "Ring",
                "pinky": "Pinky",
                "little": "Pinky",
            }
            finger = None
            for k in finger_map.keys():
                if raw.startswith(k + "_"):
                    finger = finger_map[k]
                    break
            seg = "1"
            if "_01" in raw or "_1" in raw:
                seg = "1"
            elif "_02" in raw or "_2" in raw:
                seg = "2"
            elif "_03" in raw or "_3" in raw:
                seg = "3"
            if finger is None:
                return name
            # Common Mixamo-style
            mixamo = f"mixamorig:{side_cap}Hand{finger}{seg}"
            generic = f"{side_cap}Hand{finger}{seg}"
            # Prefer exact search by returning a candidate that _get_joint_node will substring-match
            # We return the first; _get_joint_node does substring fallback
            for candidate in (mixamo, generic, f"{side_cap}{finger}{seg}"):
                # Short-circuit if it exists
                node = self._get_joint_node(candidate)
                if node is not None:
                    return candidate
            return mixamo
        except Exception:
            return name

    def play_welcome(self) -> None:
        """Trigger a brief friendly wave with the right hand (no ML)."""
        try:
            self._wave_target = self._find_node_by_names(
                [
                    "RightHand",
                    "Right Wrist",
                    "hand_r",
                    "r_hand",
                    "RightArm",
                    "mixamorig:RightHand",
                    "Armature_R_Hand",
                ]
            )
            self._wave_active = self._wave_target is not None
            self._wave_phase = 0.0
        except Exception:
            self._wave_active = False

    def play_intro(self) -> None:
        """Start a gentle welcoming gesture with both hands (non-linguistic)."""
        try:
            self._intro_left = self._find_node_by_names(
                [
                    "LeftHand",
                    "Left Wrist",
                    "hand_l",
                    "l_hand",
                    "LeftArm",
                    "mixamorig:LeftHand",
                    "Armature_L_Hand",
                ]
            )
            self._intro_right = self._find_node_by_names(
                [
                    "RightHand",
                    "Right Wrist",
                    "hand_r",
                    "r_hand",
                    "RightArm",
                    "mixamorig:RightHand",
                    "Armature_R_Hand",
                ]
            )
            self._intro_active = (self._intro_left is not None) or (
                self._intro_right is not None
            )
            self._intro_t = 0.0
        except Exception:
            self._intro_active = False

    # ---------- Panda engine setup ----------
    def _ensure_panda(self) -> None:
        if self._panda_ready:
            return
        try:
            # Panda imports
            from direct.showbase.ShowBase import ShowBase  # type: ignore
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
            # Clear existing model
            for child in list(self._scene.getChildren()):
                child.removeNode()

            self._log.info(f"Loading 3D model: {model_path}")
            node = None
            self._actor = None
            # Prefer Actor for skeletal control
            try:
                from direct.actor.Actor import Actor  # type: ignore

                self._actor = Actor(model_path)
                node = self._actor
                self._log.info(
                    "Loaded model as Actor for skeletal control (supports FBX, GLB, etc.)"
                )
            except Exception as e:
                self._actor = None
                self._log.info(f"Actor loading failed: {e}, trying as static model")
                try:
                    node = self._showbase.loader.loadModel(model_path)
                    self._log.info(
                        "Loaded model as static NodePath (no skeletal control)"
                    )
                except Exception as e2:
                    self._log.error(f"Static model loading also failed: {e2}")
                    node = None
            if node is None:
                self._display.setText("Failed to load model")
                return
            node.reparentTo(self._scene)
            try:
                # Bake model-space transforms so bounds are accurate
                node.clearModelNodes()
                node.flattenStrong()
            except Exception:
                pass
            self._model_np = node
            # Normalize orientation to face camera (Y forward). Many tools export Z-up.
            try:
                # Rotate to face camera (front view), adjust yaw as needed for this asset
                # Try different orientations to get proper front view
                # Rotate to stand upright and face camera
                node.setHpr(
                    -180, 0, 0
                )  # Rotate 180 to face front, then pitch -90 to stand upright
            except Exception:
                pass

            # Reset character to neutral pose (arms down) instead of T-pose
            try:
                if self._actor is not None:
                    # Stop any playing animations first
                    try:
                        if hasattr(self._actor, "stop"):
                            self._actor.stop()
                            self._log.info("Stopped any playing animations")
                    except Exception as e:
                        self._log.info(f"Could not stop animations: {e}")

                    # Reset to neutral pose first
                    try:
                        if hasattr(self._actor, "pose"):
                            self._actor.pose("", 0)  # Reset to frame 0
                            self._log.info("Reset Actor to neutral pose")
                    except Exception as e:
                        self._log.info(f"Could not reset pose: {e}")

                    # Try to rotate the character to face forward
                    try:
                        if self._model_np is not None:
                            # Rotate the entire model to face forward
                            self._model_np.setH(180)  # Turn 180 degrees to face forward
                            self._log.info("Rotated model to face forward")
                        if self._actor is not None:
                            # Also try rotating the actor's root
                            actor_root = self._actor.getParent()
                            if actor_root is not None:
                                actor_root.setH(180)
                                self._log.info("Rotated actor root to face forward")
                    except Exception as e:
                        self._log.info(f"Could not rotate model: {e}")

                    # Position arms in front of face for sign language with minimal values
                    try:
                        # Position arms in front of face for sign language
                        arm_joints = [
                            "mixamorig:RightArm",
                            "mixamorig:LeftArm",
                            "mixamorig:RightForeArm",
                            "mixamorig:LeftForeArm",
                        ]

                        for joint_name in arm_joints:
                            joint = self._actor.controlJoint(
                                None, "modelRoot", joint_name
                            )
                            if joint is not None:
                                if "RightArm" in joint_name:
                                    # Right upper arm: bring down to face level
                                    joint.setHpr(100, 90, 0)
                                    self._log.info(
                                        f"Set {joint_name} to optimized position (H=100, P=90, R=0)"
                                    )
                                elif "LeftArm" in joint_name:
                                    # Left upper arm: optimized position from HPR editor
                                    joint.setHpr(-100, 90, 0)
                                    self._log.info(
                                        f"Set {joint_name} to optimized position (H=-100, P=90, R=0)"
                                    )
                                elif "RightForeArm" in joint_name:
                                    # Right forearm: optimized position from HPR editor
                                    joint.setHpr(0, 0, 0)
                                    self._log.info(
                                        f"Set {joint_name} to optimized position (H=0, P=0, R=0)"
                                    )
                                elif "LeftForeArm" in joint_name:
                                    # Left forearm: optimized position from HPR editor
                                    joint.setHpr(0, 0, 0)
                                    self._log.info(
                                        f"Set {joint_name} to optimized position (H=0, P=0, R=0)"
                                    )
                            else:
                                self._log.warning(f"Could not find joint: {joint_name}")

                        # Force Actor skeleton update multiple times to ensure it takes effect
                        self._actor.update()
                        self._actor.update()
                        self._actor.update()
                        self._log.info("Forced Actor skeleton update (3 times)")

                    except Exception as e:
                        self._log.info(f"Error setting sign language pose: {e}")

                    # Hand positioning for sign language
                    try:
                        hand_joints = ["mixamorig:RightHand", "mixamorig:LeftHand"]

                        for joint_name in hand_joints:
                            joint = self._actor.controlJoint(
                                None, "modelRoot", joint_name
                            )
                            if joint is not None:
                                joint.setHpr(0, 0, 0)  # Neutral hand position
                                self._log.info(f"Set {joint_name} to neutral position")

                    except Exception as e:
                        self._log.info(f"Error setting hand position: {e}")
                else:
                    # For non-Actor models, try to rotate arms down
                    self._reset_to_neutral_pose(node)
            except Exception:
                pass
            # Frame and center the model to a comfortable, fully visible size
            self._frame_model(node, fill_fraction=0.75)
            self._current_model = str(model_path)

            # Enhanced lighting for better character appearance
            try:
                from panda3d.core import AmbientLight, DirectionalLight

                # Warmer ambient light for better skin tone
                amb = AmbientLight("amb")
                amb.setColor((0.3, 0.3, 0.3, 1))  # Reduced ambient to avoid washing out
                amb_np = self._scene.attachNewNode(amb)
                self._scene.setLight(amb_np)

                # Main directional light for definition
                key = DirectionalLight("key")
                key.setColor((1.2, 1.1, 1.0, 1))  # More intense, warm light
                key_np = self._scene.attachNewNode(key)
                key_np.setHpr(-45, -30, 0)  # Better angle for character lighting
                self._scene.setLight(key_np)

                # Fill light from opposite side
                fill = DirectionalLight("fill")
                fill.setColor((0.5, 0.6, 0.7, 1))  # Slightly stronger fill light
                fill_np = self._scene.attachNewNode(fill)
                fill_np.setHpr(45, -20, 0)
                self._scene.setLight(fill_np)
            except Exception:
                pass

            # Set character color for better visibility during signing
            try:
                from panda3d.core import VBase4

                # Choose your preferred color here:
                # character_color = VBase4(0.2, 0.4, 0.8, 1.0)  # Blue
                # character_color = VBase4(0.2, 0.8, 0.4, 1.0)  # Green
                # character_color = VBase4(0.8, 0.2, 0.2, 1.0)  # Red
                # character_color = VBase4(0.9, 0.9, 0.2, 1.0)  # Yellow
                # character_color = VBase4(1.0, 1.0, 1.0, 1.0)  # White
                character_color = VBase4(
                    0.2, 0.4, 0.8, 1.0
                )  # Default Blue - Good visibility

                if self._model_np is not None:
                    self._model_np.setColor(character_color)
                    self._log.info(f"Applied character color: {character_color}")

            except Exception as e:
                self._log.info(f"Error setting character color: {e}")

            # Keep the loading text until the first frame blits
            if not getattr(self, "_has_frame", False):
                self._display.setText("3D ready – awaiting first frame…")
            self._log.info("Model loaded successfully")

            # Log all joint names if Actor present
            try:
                if self._actor is not None and hasattr(self._actor, "getJoints"):
                    joints = list(self._actor.getJoints())
                    names = [j.getName() for j in joints] if joints else []
                    self._log.info(f"Total Actor joints: {len(names)}")
                    self._log.info(f"All Actor joints: {names}")

                    # Check if the Actor has any animations
                    if hasattr(self._actor, "getAnimNames"):
                        anim_names = self._actor.getAnimNames()
                        self._log.info(f"Actor animations: {anim_names}")
                    else:
                        self._log.info("Actor has no getAnimNames method")

                    # Check if the Actor has any poses
                    if hasattr(self._actor, "getPoseNames"):
                        pose_names = self._actor.getPoseNames()
                        self._log.info(f"Actor poses: {pose_names}")
                    else:
                        self._log.info("Actor has no getPoseNames method")
            except Exception as e:
                self._log.info(f"Error checking Actor properties: {e}")

            # Dump a list of node names for mapping purposes
            try:
                self._dump_node_names()
            except Exception:
                pass
        except Exception:
            self._display.setText("Failed to load model")
            try:
                self._log.exception("Failed to load 3D model")
            except Exception:
                pass

    def _reset_to_neutral_pose(self, node) -> None:
        """Try to reset character to neutral pose (arms down) instead of T-pose."""
        try:
            # Common arm bone names to rotate down
            arm_bones = [
                "upperarm_r",
                "upperarm_l",
                "upperarm_R",
                "upperarm_L",
                "mixamorig:RightArm",
                "mixamorig:LeftArm",
                "RightArm",
                "LeftArm",
            ]

            for bone_name in arm_bones:
                bone = self._get_joint_node(bone_name)
                if bone is not None:
                    # Rotate arm down (pitch forward)
                    bone.setHpr(0, -45, 0)
                    break
        except Exception:
            pass

    # REMOVED: _ensure_arm_position function - now using HPR editor for manual control

    def _zoom_camera_for_signing(self, is_signing: bool) -> None:
        """Dynamically adjust camera position based on signing state."""
        try:
            import math

            if self._camera is None or self._model_np is None:
                return

            # Get current model bounds for distance calculation
            min_pt, max_pt = self._model_np.getTightBounds()
            if not min_pt or not max_pt:
                return

            size = max_pt - min_pt
            radius = max(1e-3, max(size.x, size.y, size.z) * 0.5)

            # Calculate base distance
            lens = self._showbase.camLens
            fov_v_deg = 40.0
            try:
                fov = lens.getFov()
                if len(fov) == 2:
                    fov_v_deg = float(fov[1])
            except Exception:
                pass
            fov_v = math.radians(max(1.0, fov_v_deg))
            base_distance = (radius / math.tan(fov_v * 0.5)) / 0.75
            base_distance = base_distance * 2.0  # Full body view

            if is_signing:
                # Zoom in for close-up view of hands and face
                distance = base_distance * 0.6  # 60% of full body distance
                height = radius * 0.4  # Lower to focus on upper body - moved up
                self._camera.setPos(0, -distance, height)
                self._camera.lookAt(0, 0, height)
                self._log.info("Camera zoomed in for sign language")
            else:
                # Zoom out for full body view
                distance = base_distance
                height = radius * 0.2  # Lower to show full body - moved up
                self._camera.setPos(0, -distance, height)
                self._camera.lookAt(0, 0, height)
                self._log.info("Camera zoomed out for full body view")

        except Exception as e:
            self._log.info(f"Error adjusting camera: {e}")

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

            # Place camera for full body view when not signing
            # Position camera to show full character with arms in front
            self._camera.setPos(0, -distance, radius * 0.2)  # Full body view - moved up
            self._camera.lookAt(
                0, 0, radius * 0.2
            )  # Look at character's center - moved up

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

            # Advance simple animations after stepping Panda
            # Welcome right-hand wave
            if self._wave_active and self._wave_target is not None:
                try:
                    import math

                    self._wave_phase += 0.12
                    angle = 15.0 * math.sin(self._wave_phase)
                    self._wave_target.setHpr(angle, -20.0, 0.0)
                    # Stop after ~3 cycles
                    if self._wave_phase > math.pi * 6.0:
                        self._wave_active = False
                        self._wave_phase = 0.0
                except Exception:
                    self._wave_active = False

            # Gentle two-hand intro sway
            if self._intro_active:
                try:
                    import math

                    self._intro_t += 0.08
                    sway_l = 8.0 * math.sin(self._intro_t)
                    sway_r = 8.0 * math.sin(self._intro_t + math.pi)
                    if self._intro_left is not None:
                        self._intro_left.setHpr(sway_l, -10.0, 0.0)
                    if self._intro_right is not None:
                        self._intro_right.setHpr(sway_r, -10.0, 0.0)
                    # Run for ~6 seconds
                    if self._intro_t > (6.0 / 0.08):
                        self._intro_active = False
                        self._intro_t = 0.0
                except Exception:
                    self._intro_active = False

            # Phrase playback fallback wrist motion to make progress visible
            if self._phrase_timer is not None and self._phrase_timer.isActive():
                try:
                    if (self._phrase_hand or "right").lower().startswith("r"):
                        wrist = self._find_node_by_names(
                            [
                                "hand_r",
                                "r_hand",
                                "RightHand",
                                "mixamorig:RightHand",
                            ]
                        )
                    else:
                        wrist = self._find_node_by_names(
                            [
                                "hand_l",
                                "l_hand",
                                "LeftHand",
                                "mixamorig:LeftHand",
                            ]
                        )
                    if wrist is not None:
                        import math

                        t = getattr(self, "_phrase_fallback_t", 0.0) + 0.12
                        setattr(self, "_phrase_fallback_t", t)
                        wrist.setHpr(8.0 * math.sin(t), -10.0, 0.0)
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

    # ---------- Helpers ----------
    def _find_node_by_names(self, names) -> Optional[Any]:
        try:
            root = self._model_np or self._scene
            if root is None:
                return None
            all_nodes = root.findAllMatches("**/*")
            keys = [n.lower() for n in names]
            for i in range(all_nodes.getNumPaths()):
                np = all_nodes.getPath(i)
                nm = np.getName().lower()
                if any(k in nm for k in keys):
                    return np
            return None
        except Exception:
            return None

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

    def _dump_node_names(self) -> None:
        """Write a flattened list of node names to a file to aid joint mapping."""
        try:
            root = self._model_np or self._scene
            if root is None:
                return
            names: List[str] = []
            all_nodes = root.findAllMatches("**/*")
            for i in range(all_nodes.getNumPaths()):
                np = all_nodes.getPath(i)
                n = np.getName()
                if n:
                    names.append(n)
            out_path = str(
                (
                    __import__("pathlib").Path(__file__).resolve().parents[5]
                    / "panda_nodes.txt"
                )
            )
            with open(out_path, "w", encoding="utf-8") as f:
                for n in names:
                    f.write(n + "\n")
            try:
                self._log.info(f"Dumped {len(names)} node names to {out_path}")
            except Exception:
                pass
        except Exception:
            pass
