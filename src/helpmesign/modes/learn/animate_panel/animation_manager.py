"""
Animation and pose handling manager for AnimateGesturePanel.
Handles character animations, pose applications, and gesture playback.
"""

from typing import Any, Dict, List, Optional

from ....utils.logger import get_logger


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

            # Continue animation - don't apply idle pose, use natural pose
            # self.parent_panel._actor.pose("idle", current_time)  # Removed to avoid T-pose

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

            # Get alphabet signs for the character
            # Get language from global settings, not configuration
            try:
                # Try to get from parent panel's learn mode global settings
                if hasattr(self.parent_panel, "learn_mode"):
                    language = getattr(
                        self.parent_panel.learn_mode, "current_language", None
                    )
                else:
                    language = None

                if not language:
                    self._log.error("No language available in global settings")
                    return None
            except Exception as e:
                self._log.error(f"Failed to get language from global settings: {e}")
                return None

            alphabet = self.parent_panel.sign_loader.get_alphabet_signs(language, hand)
            if char_code.upper() not in alphabet:
                return None

            # Extract pose data from the sign data
            sign_data = alphabet[char_code.upper()]
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
        """Spell out a word letter by letter with animation."""
        try:
            if not self.parent_panel._is_animating or not word:
                return

            # Check if we've completed all letters
            if self.parent_panel._word_index >= len(word):
                # Word complete, stop animation
                self.parent_panel._is_animating = False
                self.parent_panel._current_word = None
                self.parent_panel._word_index = 0
                self.parent_panel._reset_to_neutral_pose()
                return

            # Get current letter
            current_letter = word[self.parent_panel._word_index]

            # Get pose for this letter
            pose_data = self.get_letter_pose_from_signs(
                current_letter, self.parent_panel._current_hand
            )

            if pose_data:
                # Apply the pose
                self.parent_panel._apply_pose(pose_data)

                # Move to next letter after a delay
                self.parent_panel._word_index += 1

                # Schedule next letter
                if hasattr(self.parent_panel, "_phrase_timer"):
                    self.parent_panel._phrase_timer.singleShot(
                        1000, lambda: self.spell_word_letters(word)
                    )
            else:
                # No pose data for this letter, skip to next
                self.parent_panel._word_index += 1
                self.spell_word_letters(word)

        except Exception as e:
            self._log.error(f"Error spelling word letters: {e}")
            self.parent_panel._is_animating = False

    def apply_pose(self, pose: Dict[str, List[float]]) -> None:
        """Apply a pose to the character."""
        try:
            if not self.parent_panel._actor or not pose:
                return

            # Validate pose before application
            if not self.parent_panel.validate_pose_before_application(pose):
                self._log.warning("Pose validation failed, applying fallback movement")
                self.parent_panel._apply_fallback_movement()
                return

            # Apply each joint rotation using Actor controlJoint method
            for joint_name, rotation_data in pose.items():
                if len(rotation_data) >= 3:  # Need at least x, y, z
                    try:
                        # Use Actor's controlJoint method for proper joint control
                        joint = self.parent_panel._actor.controlJoint(
                            None, "modelRoot", joint_name
                        )
                        if joint is not None:
                            # Apply rotation (assuming rotation_data is [x, y, z] in degrees)
                            joint.setHpr(
                                rotation_data[0], rotation_data[1], rotation_data[2]
                            )
                            self._log.debug(
                                f"Applied pose to joint {joint_name}: {rotation_data}"
                            )
                        else:
                            self._log.warning(f"Could not control joint: {joint_name}")
                    except Exception as joint_error:
                        self._log.warning(
                            f"Error applying pose to joint {joint_name}: {joint_error}"
                        )

            # Update the actor after applying all poses
            self.parent_panel._actor.update()

        except Exception as e:
            self._log.error(f"Error applying pose: {e}")
            # Fallback to neutral pose
            self.parent_panel._reset_to_neutral_pose()

    def play_welcome(self) -> None:
        """Play welcome animation."""
        try:
            if not self.parent_panel._actor:
                return

            # Find right hand for waving
            right_hand = self.parent_panel._find_node_by_names(
                ["RightHand", "right_hand", "hand.R"]
            )
            if right_hand:
                self.parent_panel._wave_target = right_hand
                self.parent_panel._wave_active = True
                self.parent_panel._wave_progress = 0.0

        except Exception as e:
            self._log.error(f"Error playing welcome animation: {e}")

    def play_intro(self) -> None:
        """Play intro animation."""
        try:
            if not self.parent_panel._model_np:
                return

            # Start intro rotation
            self.parent_panel._intro_active = True
            self.parent_panel._intro_progress = 0.0

        except Exception as e:
            self._log.error(f"Error playing intro animation: {e}")

    def reset_to_neutral_pose(self) -> None:
        """Reset character to neutral pose."""
        try:
            if not self.parent_panel._actor:
                return

            # Stop any active animations
            self.parent_panel._is_animating = False
            self.parent_panel._wave_active = False
            self.parent_panel._intro_active = False

            # Apply the hands-down pose as the neutral pose
            try:
                self.parent_panel._actor.stop()
                self.parent_panel._actor.pose("Armature|mixamo.com|Layer0", 0)
                self._log.info("Reset to neutral pose - applied hands-down pose")
            except Exception as pose_error:
                self._log.warning(f"Could not apply hands-down pose: {pose_error}")
                self._log.info("Using model's natural pose")

        except Exception as e:
            self._log.error(f"Error resetting to neutral pose: {e}")

    def pause_animation_and_reset_to_default(self) -> None:
        """Pause current animation and reset to default pose."""
        try:
            # Stop all animations
            self.parent_panel._is_animating = False
            self.parent_panel._wave_active = False
            self.parent_panel._intro_active = False

            # Reset to neutral pose
            self.reset_to_neutral_pose()

        except Exception as e:
            self._log.error(f"Error pausing animation and resetting: {e}")
