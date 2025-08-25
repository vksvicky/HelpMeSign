"""
Animation and pose handling for AnimateGesturePanel.
Extracted from animate_panel.py to reduce file size.
"""

from typing import Any, Dict, List, Optional

from ...utils.logger import get_logger


class AnimationManager:
    """Manages animation and pose handling for AnimateGesturePanel"""

    def __init__(self, parent_panel):
        self.parent_panel = parent_panel
        self._log = get_logger("helpmesign.modes.learn.animate_panel.animation")

    def on_signing_animation_frame(self) -> None:
        """Handle signing animation frame updates."""
        try:
            if not self.parent_panel._is_animating or not self.parent_panel._actor:
                return

            # Get current animation time
            current_time = self.parent_panel._actor.getCurrentAnimTime()
            if current_time is None:
                return

            # Check if animation is complete
            anim_duration = self.parent_panel._actor.getCurrentAnimLength()
            if anim_duration and current_time >= anim_duration:
                # Animation complete, stop and reset
                self.parent_panel._is_animating = False
                self.parent_panel._actor.stop()
                self.parent_panel._reset_to_neutral_pose()
                return

            # Continue animation
            self.parent_panel._actor.pose("idle", current_time)

        except Exception as e:
            self._log.error(f"Error in signing animation frame: {e}")
            self.parent_panel._is_animating = False

    def get_letter_pose_from_signs(
        self, char_code: str, hand: str
    ) -> Optional[Dict[str, List[float]]]:
        """Get pose data for a letter from sign language data."""
        try:
            if not self.parent_panel.sign_loader:
                return None

            # Get sign data for the character
            sign_data = self.parent_panel.sign_loader.get_sign_data(char_code, hand)
            if not sign_data:
                return None

            # Extract pose data
            pose_data = sign_data.get("pose", {})
            if not pose_data:
                return None

            return pose_data

        except Exception as e:
            self._log.error(f"Error getting letter pose: {e}")
            return None

    def apply_word_with_animation(self, word: str, hand: str) -> None:
        """Apply a word with letter-by-letter animation."""
        try:
            if not word or not self.parent_panel._actor:
                return

            # Start word animation
            self.parent_panel._is_animating = True
            self.parent_panel._current_word = word
            self.parent_panel._current_hand = hand
            self.parent_panel._word_index = 0

            # Start with first letter
            self.parent_panel._spell_word_letters(word)

        except Exception as e:
            self._log.error(f"Error applying word animation: {e}")
            self.parent_panel._is_animating = False

    def on_animation_frame(self) -> None:
        """Handle general animation frame updates."""
        try:
            if not self.parent_panel._is_animating:
                return

            # Handle word spelling animation
            if (
                hasattr(self.parent_panel, "_current_word")
                and self.parent_panel._current_word
            ):
                self.parent_panel._spell_word_letters(self.parent_panel._current_word)

        except Exception as e:
            self._log.error(f"Error in animation frame: {e}")
            self.parent_panel._is_animating = False

    def spell_word_letters(self, word: str) -> None:
        """Spell out a word letter by letter."""
        try:
            if not self.parent_panel._actor or not word:
                return

            # Get current letter
            if self.parent_panel._word_index >= len(word):
                # Word complete
                self.parent_panel._is_animating = False
                self.parent_panel._current_word = None
                self.parent_panel._reset_to_neutral_pose()
                return

            char = word[self.parent_panel._word_index]
            hand = getattr(self.parent_panel, "_current_hand", "right")

            # Get pose for this letter
            pose_data = self.parent_panel._get_letter_pose_from_signs(char, hand)
            if pose_data:
                self.parent_panel._apply_pose(pose_data)

            # Move to next letter after delay
            self.parent_panel._word_index += 1

        except Exception as e:
            self._log.error(f"Error spelling word letters: {e}")
            self.parent_panel._is_animating = False

    def apply_pose(self, pose: Dict[str, List[float]]) -> None:
        """Apply a pose to the character."""
        try:
            if not self.parent_panel._actor or not pose:
                return

            # Apply pose to each joint
            for joint_name, values in pose.items():
                if len(values) >= 3:  # Need at least x, y, z
                    joint_node = self.parent_panel._get_joint_node(joint_name)
                    if joint_node:
                        # Set position
                        joint_node.setPos(values[0], values[1], values[2])

                        # Set rotation if provided
                        if len(values) >= 6:  # x, y, z, h, p, r
                            joint_node.setHpr(values[3], values[4], values[5])

        except Exception as e:
            self._log.error(f"Error applying pose: {e}")

    def get_joint_node(self, name: str) -> Optional[Any]:
        """Get a joint node by name."""
        try:
            if not self.parent_panel._model_np:
                return None

            # Try different naming conventions
            possible_names = [
                name,
                name.lower(),
                name.upper(),
                name.replace("_", ""),
                name.replace(" ", ""),
            ]

            for joint_name in possible_names:
                try:
                    node = self.parent_panel._model_np.find(f"**/{joint_name}")
                    if node and not node.isEmpty():
                        return node
                except Exception:
                    continue

            return None

        except Exception as e:
            self._log.error(f"Error getting joint node {name}: {e}")
            return None

    def apply_fallback_movement(self) -> None:
        """Apply fallback movement when pose data is not available."""
        try:
            if not self.parent_panel._actor:
                return

            # Simple wave animation as fallback
            import math
            import time

            current_time = time.time()
            wave_offset = math.sin(current_time * 2) * 0.1

            # Apply to right hand if available
            right_hand = self.parent_panel._get_joint_node("right_hand")
            if right_hand:
                current_pos = right_hand.getPos()
                right_hand.setPos(
                    current_pos[0], current_pos[1], current_pos[2] + wave_offset
                )

        except Exception as e:
            self._log.error(f"Error applying fallback movement: {e}")

    def best_alias(self, name: str) -> str:
        """Find the best alias for a joint name."""
        try:
            # Common joint name mappings
            aliases = {
                "right_hand": ["right_hand", "r_hand", "hand_r", "rightHand", "RHand"],
                "left_hand": ["left_hand", "l_hand", "hand_l", "leftHand", "LHand"],
                "right_arm": ["right_arm", "r_arm", "arm_r", "rightArm", "RArm"],
                "left_arm": ["left_arm", "l_arm", "arm_l", "leftArm", "LArm"],
                "head": ["head", "Head", "HEAD"],
                "neck": ["neck", "Neck", "NECK"],
                "spine": ["spine", "Spine", "SPINE", "spine_01", "spine_02"],
            }

            # Check if we have a mapping for this name
            if name in aliases:
                for alias in aliases[name]:
                    if self.parent_panel._get_joint_node(alias):
                        return alias

            # Return original name if no mapping found
            return name

        except Exception as e:
            self._log.error(f"Error finding best alias: {e}")
            return name

    def play_welcome(self) -> None:
        """Play welcome animation."""
        try:
            if not self.parent_panel._actor:
                return

            # Simple welcome wave
            self.parent_panel._wave_active = True
            self.parent_panel._wave_target = 1.0
            self.parent_panel._wave_time = 0.0

        except Exception as e:
            self._log.error(f"Error playing welcome: {e}")

    def play_intro(self) -> None:
        """Play intro animation."""
        try:
            if not self.parent_panel._actor:
                return

            # Simple intro animation
            self.parent_panel._intro_active = True
            self.parent_panel._intro_t = 0.0

        except Exception as e:
            self._log.error(f"Error playing intro: {e}")

    def reset_to_neutral_pose(self) -> None:
        """Reset the character to neutral pose."""
        try:
            if not self.parent_panel._actor:
                return

            # Stop any active animations
            self.parent_panel._actor.stop()

            # Reset to idle pose
            try:
                self.parent_panel._actor.pose("idle", 0)
            except Exception:
                # If no idle pose, just reset position
                pass

        except Exception as e:
            self._log.error(f"Error resetting to neutral pose: {e}")

    def pause_animation_and_reset_to_default(self) -> None:
        """Pause animation and reset to default pose."""
        try:
            # Stop animations
            self.parent_panel._is_animating = False
            self.parent_panel._wave_active = False
            self.parent_panel._intro_active = False

            # Reset to default pose
            self.parent_panel._reset_to_neutral_pose()

        except Exception as e:
            self._log.error(f"Error pausing animation: {e}")

    def shutdown(self):
        """Shutdown animation manager."""
        try:
            # Stop animations
            self.parent_panel._is_animating = False
            self.parent_panel._wave_active = False
            self.parent_panel._intro_active = False

        except Exception as e:
            self._log.error(f"Error during animation manager shutdown: {e}")
