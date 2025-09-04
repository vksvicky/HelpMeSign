#!/usr/bin/env python3
"""
Joint constraints for human anatomical limitations
Ensures character joints stay within realistic human ranges for fingers, hands, and facial expressions
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

from .logger import get_logger


@dataclass
class JointConstraint:
    """Defines the range of motion for a specific joint"""

    min_h: float  # Minimum heading (yaw) in degrees
    max_h: float  # Maximum heading (yaw) in degrees
    min_p: float  # Minimum pitch in degrees
    max_p: float  # Maximum pitch in degrees
    min_r: float  # Minimum roll in degrees
    max_r: float  # Maximum roll in degrees
    description: str = ""  # Human-readable description of the joint


class JointConstraintValidator:
    """Validates and constrains joint movements to human anatomical limits"""

    def __init__(self):
        self.logger = get_logger("helpmesign.joint_constraints")
        self.constraints = self._initialize_constraints()

    def _initialize_constraints(self) -> Dict[str, JointConstraint]:
        """Initialize joint constraints based on human anatomy"""
        return {
            # Head and Neck
            "mixamorig:Head": JointConstraint(
                min_h=-60,
                max_h=60,  # Head rotation left/right
                min_p=-45,
                max_p=45,  # Head up/down
                min_r=-30,
                max_r=30,  # Head tilt
                description="Head rotation and tilt",
            ),
            "mixamorig:Neck": JointConstraint(
                min_h=-45,
                max_h=45,  # Neck rotation
                min_p=-30,
                max_p=30,  # Neck flexion/extension
                min_r=-20,
                max_r=20,  # Neck lateral flexion
                description="Neck movement",
            ),
            # Shoulders
            "mixamorig:RightShoulder": JointConstraint(
                min_h=-90,
                max_h=180,  # Shoulder abduction/adduction
                min_p=-60,
                max_p=180,  # Shoulder flexion/extension
                min_r=-90,
                max_r=90,  # Shoulder internal/external rotation
                description="Right shoulder movement",
            ),
            "mixamorig:LeftShoulder": JointConstraint(
                min_h=-180,
                max_h=90,  # Shoulder abduction/adduction (mirrored)
                min_p=-60,
                max_p=180,  # Shoulder flexion/extension
                min_r=-90,
                max_r=90,  # Shoulder internal/external rotation
                description="Left shoulder movement",
            ),
            # Arms
            "mixamorig:RightArm": JointConstraint(
                min_h=-45,
                max_h=45,  # Arm rotation
                min_p=0,
                max_p=150,  # Arm flexion
                min_r=-90,
                max_r=90,  # Arm rotation
                description="Right upper arm",
            ),
            "mixamorig:LeftArm": JointConstraint(
                min_h=-45,
                max_h=45,  # Arm rotation
                min_p=0,
                max_p=150,  # Arm flexion
                min_r=-90,
                max_r=90,  # Arm rotation
                description="Left upper arm",
            ),
            # Forearms
            "mixamorig:RightForeArm": JointConstraint(
                min_h=-45,
                max_h=45,  # Forearm rotation
                min_p=0,
                max_p=150,  # Forearm flexion
                min_r=-90,
                max_r=90,  # Forearm pronation/supination
                description="Right forearm",
            ),
            "mixamorig:LeftForeArm": JointConstraint(
                min_h=-45,
                max_h=45,  # Forearm rotation
                min_p=0,
                max_p=150,  # Forearm flexion
                min_r=-90,
                max_r=90,  # Forearm pronation/supination
                description="Left forearm",
            ),
            # Wrists
            "mixamorig:RightHand": JointConstraint(
                min_h=-30,
                max_h=30,  # Wrist abduction/adduction
                min_p=-80,
                max_p=80,  # Wrist flexion/extension
                min_r=-90,
                max_r=90,  # Wrist rotation
                description="Right wrist",
            ),
            "mixamorig:LeftHand": JointConstraint(
                min_h=-30,
                max_h=30,  # Wrist abduction/adduction
                min_p=-80,
                max_p=80,  # Wrist flexion/extension
                min_r=-90,
                max_r=90,  # Wrist rotation
                description="Left wrist",
            ),
            # Finger joints - Right Hand
            "mixamorig:RightHandThumb1": JointConstraint(
                min_h=-45,
                max_h=45,  # Thumb CMC joint
                min_p=-20,
                max_p=20,  # Thumb flexion/extension
                min_r=-90,
                max_r=90,  # Thumb abduction/adduction (increased for ASL signs)
                description="Right thumb CMC joint",
            ),
            "mixamorig:RightHandThumb2": JointConstraint(
                min_h=-30,
                max_h=30,  # Thumb MCP joint
                min_p=0,
                max_p=80,  # Thumb flexion
                min_r=-30,
                max_r=30,  # Thumb abduction
                description="Right thumb MCP joint",
            ),
            "mixamorig:RightHandThumb3": JointConstraint(
                min_h=-20,
                max_h=20,  # Thumb IP joint
                min_p=0,
                max_p=120,  # Thumb flexion (increased for ASL signs)
                min_r=-20,
                max_r=20,  # Thumb rotation
                description="Right thumb IP joint",
            ),
            # Index finger - Right
            "mixamorig:RightHandIndex1": JointConstraint(
                min_h=-30,
                max_h=30,  # Index MCP joint
                min_p=0,
                max_p=120,  # Index flexion (increased for ASL signs)
                min_r=-45,
                max_r=45,  # Index abduction/adduction
                description="Right index MCP joint",
            ),
            "mixamorig:RightHandIndex2": JointConstraint(
                min_h=-20,
                max_h=20,  # Index PIP joint
                min_p=0,
                max_p=120,  # Index flexion
                min_r=-20,
                max_r=20,  # Index rotation
                description="Right index PIP joint",
            ),
            "mixamorig:RightHandIndex3": JointConstraint(
                min_h=-15,
                max_h=15,  # Index DIP joint
                min_p=0,
                max_p=120,  # Index flexion (increased for ASL signs)
                min_r=-15,
                max_r=15,  # Index rotation
                description="Right index DIP joint",
            ),
            # Middle finger - Right
            "mixamorig:RightHandMiddle1": JointConstraint(
                min_h=-20,
                max_h=20,  # Middle MCP joint
                min_p=0,
                max_p=120,  # Middle flexion (increased for ASL signs)
                min_r=-30,
                max_r=30,  # Middle abduction/adduction
                description="Right middle MCP joint",
            ),
            "mixamorig:RightHandMiddle2": JointConstraint(
                min_h=-15,
                max_h=15,  # Middle PIP joint
                min_p=0,
                max_p=120,  # Middle flexion
                min_r=-15,
                max_r=15,  # Middle rotation
                description="Right middle PIP joint",
            ),
            "mixamorig:RightHandMiddle3": JointConstraint(
                min_h=-10,
                max_h=10,  # Middle DIP joint
                min_p=0,
                max_p=120,  # Middle flexion (increased for ASL signs)
                min_r=-10,
                max_r=10,  # Middle rotation
                description="Right middle DIP joint",
            ),
            # Ring finger - Right
            "mixamorig:RightHandRing1": JointConstraint(
                min_h=-20,
                max_h=20,  # Ring MCP joint
                min_p=0,
                max_p=120,  # Ring flexion (increased for ASL signs)
                min_r=-30,
                max_r=30,  # Ring abduction/adduction
                description="Right ring MCP joint",
            ),
            "mixamorig:RightHandRing2": JointConstraint(
                min_h=-15,
                max_h=15,  # Ring PIP joint
                min_p=0,
                max_p=120,  # Ring flexion
                min_r=-15,
                max_r=15,  # Ring rotation
                description="Right ring PIP joint",
            ),
            "mixamorig:RightHandRing3": JointConstraint(
                min_h=-10,
                max_h=10,  # Ring DIP joint
                min_p=0,
                max_p=120,  # Ring flexion (increased for ASL signs)
                min_r=-10,
                max_r=10,  # Ring rotation
                description="Right ring DIP joint",
            ),
            # Pinky finger - Right
            "mixamorig:RightHandPinky1": JointConstraint(
                min_h=-30,
                max_h=30,  # Pinky MCP joint
                min_p=0,
                max_p=120,  # Pinky flexion (increased for ASL signs)
                min_r=-45,
                max_r=45,  # Pinky abduction/adduction
                description="Right pinky MCP joint",
            ),
            "mixamorig:RightHandPinky2": JointConstraint(
                min_h=-20,
                max_h=20,  # Pinky PIP joint
                min_p=0,
                max_p=120,  # Pinky flexion
                min_r=-20,
                max_r=20,  # Pinky rotation
                description="Right pinky PIP joint",
            ),
            "mixamorig:RightHandPinky3": JointConstraint(
                min_h=-15,
                max_h=15,  # Pinky DIP joint
                min_p=0,
                max_p=120,  # Pinky flexion (increased for ASL signs)
                min_r=-15,
                max_r=15,  # Pinky rotation
                description="Right pinky DIP joint",
            ),
            # Finger joints - Left Hand (mirrored)
            "mixamorig:LeftHandThumb1": JointConstraint(
                min_h=-45,
                max_h=45,  # Thumb CMC joint
                min_p=-20,
                max_p=20,  # Thumb flexion/extension
                min_r=-45,
                max_r=45,  # Thumb abduction/adduction
                description="Left thumb CMC joint",
            ),
            "mixamorig:LeftHandThumb2": JointConstraint(
                min_h=-30,
                max_h=30,  # Thumb MCP joint
                min_p=0,
                max_p=80,  # Thumb flexion
                min_r=-30,
                max_r=30,  # Thumb abduction
                description="Left thumb MCP joint",
            ),
            "mixamorig:LeftHandThumb3": JointConstraint(
                min_h=-20,
                max_h=20,  # Thumb IP joint
                min_p=0,
                max_p=120,  # Thumb flexion (increased for ASL signs)
                min_r=-20,
                max_r=20,  # Thumb rotation
                description="Left thumb IP joint",
            ),
            # Index finger - Left
            "mixamorig:LeftHandIndex1": JointConstraint(
                min_h=-30,
                max_h=30,  # Index MCP joint
                min_p=0,
                max_p=120,  # Index flexion (increased for ASL signs)
                min_r=-45,
                max_r=45,  # Index abduction/adduction
                description="Left index MCP joint",
            ),
            "mixamorig:LeftHandIndex2": JointConstraint(
                min_h=-20,
                max_h=20,  # Index PIP joint
                min_p=0,
                max_p=120,  # Index flexion
                min_r=-20,
                max_r=20,  # Index rotation
                description="Left index PIP joint",
            ),
            "mixamorig:LeftHandIndex3": JointConstraint(
                min_h=-15,
                max_h=15,  # Index DIP joint
                min_p=0,
                max_p=120,  # Index flexion (increased for ASL signs)
                min_r=-15,
                max_r=15,  # Index rotation
                description="Left index DIP joint",
            ),
            # Middle finger - Left
            "mixamorig:LeftHandMiddle1": JointConstraint(
                min_h=-20,
                max_h=20,  # Middle MCP joint
                min_p=0,
                max_p=120,  # Middle flexion (increased for ASL signs)
                min_r=-30,
                max_r=30,  # Middle abduction/adduction
                description="Left middle MCP joint",
            ),
            "mixamorig:LeftHandMiddle2": JointConstraint(
                min_h=-15,
                max_h=15,  # Middle PIP joint
                min_p=0,
                max_p=120,  # Middle flexion
                min_r=-15,
                max_r=15,  # Middle rotation
                description="Left middle PIP joint",
            ),
            "mixamorig:LeftHandMiddle3": JointConstraint(
                min_h=-10,
                max_h=10,  # Middle DIP joint
                min_p=0,
                max_p=120,  # Middle flexion (increased for ASL signs)
                min_r=-10,
                max_r=10,  # Middle rotation
                description="Left middle DIP joint",
            ),
            # Ring finger - Left
            "mixamorig:LeftHandRing1": JointConstraint(
                min_h=-20,
                max_h=20,  # Ring MCP joint
                min_p=0,
                max_p=120,  # Ring flexion (increased for ASL signs)
                min_r=-30,
                max_r=30,  # Ring abduction/adduction
                description="Left ring MCP joint",
            ),
            "mixamorig:LeftHandRing2": JointConstraint(
                min_h=-15,
                max_h=15,  # Ring PIP joint
                min_p=0,
                max_p=120,  # Ring flexion
                min_r=-15,
                max_r=15,  # Ring rotation
                description="Left ring PIP joint",
            ),
            "mixamorig:LeftHandRing3": JointConstraint(
                min_h=-10,
                max_h=10,  # Ring DIP joint
                min_p=0,
                max_p=120,  # Ring flexion (increased for ASL signs)
                min_r=-10,
                max_r=10,  # Ring rotation
                description="Left ring DIP joint",
            ),
            # Pinky finger - Left
            "mixamorig:LeftHandPinky1": JointConstraint(
                min_h=-30,
                max_h=30,  # Pinky MCP joint
                min_p=0,
                max_p=120,  # Pinky flexion (increased for ASL signs)
                min_r=-45,
                max_r=45,  # Pinky abduction/adduction
                description="Left pinky MCP joint",
            ),
            "mixamorig:LeftHandPinky2": JointConstraint(
                min_h=-20,
                max_h=20,  # Pinky PIP joint
                min_p=0,
                max_p=120,  # Pinky flexion
                min_r=-20,
                max_r=20,  # Pinky rotation
                description="Left pinky PIP joint",
            ),
            "mixamorig:LeftHandPinky3": JointConstraint(
                min_h=-15,
                max_h=15,  # Pinky DIP joint
                min_p=0,
                max_p=120,  # Pinky flexion (increased for ASL signs)
                min_r=-15,
                max_r=15,  # Pinky rotation
                description="Left pinky DIP joint",
            ),
            # Facial joints (if available in the model)
            "mixamorig:Jaw": JointConstraint(
                min_h=-10,
                max_h=10,  # Jaw side-to-side
                min_p=-20,
                max_p=20,  # Jaw open/close
                min_r=-5,
                max_r=5,  # Jaw rotation
                description="Jaw movement",
            ),
            "mixamorig:LeftEye": JointConstraint(
                min_h=-15,
                max_h=15,  # Eye horizontal movement
                min_p=-10,
                max_p=10,  # Eye vertical movement
                min_r=-5,
                max_r=5,  # Eye rotation
                description="Left eye movement",
            ),
            "mixamorig:RightEye": JointConstraint(
                min_h=-15,
                max_h=15,  # Eye horizontal movement
                min_p=-10,
                max_p=10,  # Eye vertical movement
                min_r=-5,
                max_r=5,  # Eye rotation
                description="Right eye movement",
            ),
        }

    def validate_and_constrain_pose(
        self, pose: Dict[str, List[float]]
    ) -> Dict[str, List[float]]:
        """
        Validate and constrain a pose to human anatomical limits

        Args:
            pose: Dictionary mapping joint names to [h, p, r] values

        Returns:
            Constrained pose with values within human limits
        """
        constrained_pose = {}
        violations = []

        for joint_name, hpr in pose.items():
            # Check if hpr is a valid list with at least 3 numeric values
            if not isinstance(hpr, (list, tuple)) or len(hpr) < 3:
                self.logger.warning(f"Invalid HPR format for joint {joint_name}: {hpr}")
                continue

            try:
                h, p, r = float(hpr[0]), float(hpr[1]), float(hpr[2])
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid HPR values for joint {joint_name}: {hpr}")
                continue

            # Get constraint for this joint
            constraint = self.constraints.get(joint_name)

            if constraint:
                # Apply constraints
                constrained_h = self._clamp_value(h, constraint.min_h, constraint.max_h)
                constrained_p = self._clamp_value(p, constraint.min_p, constraint.max_p)
                constrained_r = self._clamp_value(r, constraint.min_r, constraint.max_r)

                # Check for violations
                if h != constrained_h or p != constrained_p or r != constrained_r:
                    violations.append(
                        {
                            "joint": joint_name,
                            "original": [h, p, r],
                            "constrained": [
                                constrained_h,
                                constrained_p,
                                constrained_r,
                            ],
                            "description": constraint.description,
                        }
                    )

                constrained_pose[joint_name] = [
                    constrained_h,
                    constrained_p,
                    constrained_r,
                ]
            else:
                # No constraint found, use original values but log warning
                self.logger.warning(f"No constraint found for joint: {joint_name}")
                constrained_pose[joint_name] = [h, p, r]

        # Log violations if any
        if violations:
            self.logger.warning(
                f"Joint constraint violations detected: {len(violations)} joints"
            )
            for violation in violations:
                self.logger.debug(
                    f"Joint '{violation['joint']}' ({violation['description']}) "
                    f"constrained from {violation['original']} to {violation['constrained']}"
                )

        return constrained_pose

    def _clamp_value(self, value: float, min_val: float, max_val: float) -> float:
        """Clamp a value to the specified range"""
        return max(min_val, min(max_val, value))

    def get_joint_constraint(self, joint_name: str) -> Optional[JointConstraint]:
        """Get the constraint for a specific joint"""
        return self.constraints.get(joint_name)

    def add_custom_constraint(
        self, joint_name: str, constraint: JointConstraint
    ) -> None:
        """Add a custom constraint for a joint"""
        self.constraints[joint_name] = constraint
        self.logger.info(f"Added custom constraint for joint: {joint_name}")

    def validate_single_joint(
        self, joint_name: str, h: float, p: float, r: float
    ) -> Tuple[float, float, float]:
        """
        Validate and constrain a single joint

        Returns:
            Tuple of (constrained_h, constrained_p, constrained_r)
        """
        constraint = self.constraints.get(joint_name)

        if constraint:
            constrained_h = self._clamp_value(h, constraint.min_h, constraint.max_h)
            constrained_p = self._clamp_value(p, constraint.min_p, constraint.max_p)
            constrained_r = self._clamp_value(r, constraint.min_r, constraint.max_r)

            return constrained_h, constrained_p, constrained_r
        else:
            # No constraint found, return original values
            self.logger.warning(f"No constraint found for joint: {joint_name}")
            return h, p, r

    def is_pose_valid(self, pose: Dict[str, List[float]]) -> bool:
        """
        Check if a pose is within human anatomical limits

        Returns:
            True if pose is valid, False otherwise
        """
        for joint_name, hpr in pose.items():
            if len(hpr) >= 3:
                h, p, r = float(hpr[0]), float(hpr[1]), float(hpr[2])
                constraint = self.constraints.get(joint_name)

                if constraint:
                    if (
                        h < constraint.min_h
                        or h > constraint.max_h
                        or p < constraint.min_p
                        or p > constraint.max_p
                        or r < constraint.min_r
                        or r > constraint.max_r
                    ):
                        return False

        return True


# Global instance for easy access
joint_validator = JointConstraintValidator()
