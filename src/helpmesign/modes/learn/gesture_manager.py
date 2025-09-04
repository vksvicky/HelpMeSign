"""
Gesture Management for Learn Mode
Contains gesture validation and animation methods extracted from learn_mode.py
"""

from typing import Any, Dict, List, Optional

from ...utils.joint_constraints import joint_validator


class LearnModeGestureManager:
    """Gesture management methods for Learn Mode"""

    def __init__(self, learn_mode):
        self.learn_mode = learn_mode
        self.logger = learn_mode.logger

    def validate_gesture_before_play(
        self, gesture_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate gesture data against human anatomical constraints before playing

        Args:
            gesture_data: Dictionary containing gesture information including pose data

        Returns:
            Validated and constrained gesture data
        """
        try:
            if not gesture_data or "pose" not in gesture_data:
                self.learn_mode.logger.warning(
                    "Invalid gesture data: missing pose information"
                )
                return gesture_data

            pose = gesture_data["pose"]
            if not isinstance(pose, dict):
                self.learn_mode.logger.warning("Invalid pose data: expected dictionary")
                return gesture_data

            # Validate and constrain the pose
            constrained_pose = joint_validator.validate_and_constrain_pose(pose)

            # Create validated gesture data
            validated_gesture = gesture_data.copy()
            validated_gesture["pose"] = constrained_pose
            validated_gesture["validated"] = True

            # Log validation results
            if constrained_pose != pose:
                self.learn_mode.logger.info(
                    f"Gesture pose constrained: {len(pose)} joints validated"
                )

            return validated_gesture

        except Exception as e:
            self.learn_mode.logger.error(f"Error validating gesture: {e}")
            return gesture_data

    def is_gesture_anatomically_valid(self, gesture_data: Dict[str, Any]) -> bool:
        """
        Check if a gesture is within human anatomical limits

        Args:
            gesture_data: Dictionary containing gesture information including pose data

        Returns:
            True if gesture is valid, False otherwise
        """
        try:
            if not gesture_data or "pose" not in gesture_data:
                return False

            pose = gesture_data["pose"]
            if not isinstance(pose, dict):
                return False

            return joint_validator.is_pose_valid(pose)

        except Exception as e:
            self.learn_mode.logger.error(f"Error checking gesture validity: {e}")
            return False

    def get_gesture_constraint_violations(
        self, gesture_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get detailed information about constraint violations in a gesture

        Args:
            gesture_data: Dictionary containing gesture information including pose data

        Returns:
            List of violation details
        """
        try:
            violations: List[Dict[str, Any]] = []

            if not gesture_data or "pose" not in gesture_data:
                return violations

            pose = gesture_data["pose"]
            if not isinstance(pose, dict):
                return violations

            for joint_name, hpr in pose.items():
                if len(hpr) >= 3:
                    h, p, r = float(hpr[0]), float(hpr[1]), float(hpr[2])
                    constraint = joint_validator.get_joint_constraint(joint_name)

                    if constraint:
                        # Check for violations
                        if (
                            h < constraint.min_h
                            or h > constraint.max_h
                            or p < constraint.min_p
                            or p > constraint.max_p
                            or r < constraint.min_r
                            or r > constraint.max_r
                        ):

                            violations.append(
                                {
                                    "joint": joint_name,
                                    "description": constraint.description,
                                    "original_values": [h, p, r],
                                    "constraints": {
                                        "h": (constraint.min_h, constraint.max_h),
                                        "p": (constraint.min_p, constraint.max_p),
                                        "r": (constraint.min_r, constraint.max_r),
                                    },
                                }
                            )

            return violations

        except Exception as e:
            self.learn_mode.logger.error(f"Error getting gesture violations: {e}")
            return []

    def _get_gesture_data(
        self, character: str, char_type: str, hand: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get gesture data for a character from the sign language loader

        Args:
            character: The character (letter or number)
            char_type: Type of character ("letter" or "number")
            hand: Hand preference ("left" or "right")

        Returns:
            Gesture data dictionary or None if not found
        """
        try:
            if (
                not hasattr(self.learn_mode, "sign_loader")
                or not self.learn_mode.sign_loader
            ):
                return None

            # Try to get gesture data from the sign loader
            if char_type == "letter":
                alphabet_signs = self.learn_mode.sign_loader.get_alphabet_signs(
                    self.learn_mode.current_language, hand
                )
                data = alphabet_signs.get(character.upper())
            elif char_type == "number":
                number_signs = self.learn_mode.sign_loader.get_number_signs(
                    self.learn_mode.current_language, hand
                )
                data = number_signs.get(character)
            else:
                return None

            if data and isinstance(data, dict):
                return data

            return None

        except Exception as e:
            self.learn_mode.logger.error(
                f"Error getting gesture data for '{character}': {e}"
            )
            return None
