"""
Joint movement limits and validation utilities.
Prevents inhuman positions and ensures biomechanically correct poses.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple


class JointType(Enum):
    """Types of joints for different validation rules."""

    ARM = "arm"
    FOREARM = "forearm"
    HAND = "hand"
    FINGER = "finger"
    THUMB = "thumb"
    HEAD = "head"
    NECK = "neck"
    SHOULDER = "shoulder"
    ELBOW = "elbow"
    WRIST = "wrist"


@dataclass
class JointLimit:
    """Defines movement limits for a joint."""

    joint_name: str
    joint_type: JointType
    h_min: float  # Heading minimum
    h_max: float  # Heading maximum
    p_min: float  # Pitch minimum
    p_max: float  # Pitch maximum
    r_min: float  # Roll minimum
    r_max: float  # Roll maximum
    description: str = ""


class JointValidator:
    """Validates joint movements to prevent inhuman positions."""

    def __init__(self):
        self.joint_limits = self._create_joint_limits()

    def _create_joint_limits(self) -> Dict[str, JointLimit]:
        """Create biomechanically accurate joint limits."""
        return {
            # Arm joints
            "mixamorig:RightArm": JointLimit(
                "mixamorig:RightArm",
                JointType.ARM,
                h_min=-90,
                h_max=90,  # Side-to-side
                p_min=-45,
                p_max=180,  # Forward/backward
                r_min=-45,
                r_max=45,  # Rotation
                description="Right upper arm",
            ),
            "mixamorig:LeftArm": JointLimit(
                "mixamorig:LeftArm",
                JointType.ARM,
                h_min=-90,
                h_max=90,  # Side-to-side
                p_min=-45,
                p_max=180,  # Forward/backward
                r_min=-45,
                r_max=45,  # Rotation
                description="Left upper arm",
            ),
            # Forearm joints
            "mixamorig:RightForeArm": JointLimit(
                "mixamorig:RightForeArm",
                JointType.FOREARM,
                h_min=-45,
                h_max=45,  # Side-to-side
                p_min=0,
                p_max=150,  # Bend elbow
                r_min=-90,
                r_max=90,  # Pronation/supination
                description="Right forearm",
            ),
            "mixamorig:LeftForeArm": JointLimit(
                "mixamorig:LeftForeArm",
                JointType.FOREARM,
                h_min=-45,
                h_max=45,  # Side-to-side
                p_min=0,
                p_max=150,  # Bend elbow
                r_min=-90,
                r_max=90,  # Pronation/supination
                description="Left forearm",
            ),
            # Hand joints
            "mixamorig:RightHand": JointLimit(
                "mixamorig:RightHand",
                JointType.HAND,
                h_min=-45,
                h_max=45,  # Side-to-side
                p_min=-45,
                p_max=45,  # Up/down
                r_min=-90,
                r_max=90,  # Rotation
                description="Right hand",
            ),
            "mixamorig:LeftHand": JointLimit(
                "mixamorig:LeftHand",
                JointType.HAND,
                h_min=-45,
                h_max=45,  # Side-to-side
                p_min=-45,
                p_max=45,  # Up/down
                r_min=-90,
                r_max=90,  # Rotation
                description="Left hand",
            ),
            # Finger joints (Index)
            "mixamorig:RightHandIndex1": JointLimit(
                "mixamorig:RightHandIndex1",
                JointType.FINGER,
                h_min=-30,
                h_max=30,  # Side-to-side
                p_min=0,
                p_max=90,  # Bend
                r_min=-15,
                r_max=15,  # Twist
                description="Right index finger MCP",
            ),
            "mixamorig:RightHandIndex2": JointLimit(
                "mixamorig:RightHandIndex2",
                JointType.FINGER,
                h_min=-10,
                h_max=10,  # Side-to-side
                p_min=0,
                p_max=120,  # Bend
                r_min=-5,
                r_max=5,  # Twist
                description="Right index finger PIP",
            ),
            "mixamorig:RightHandIndex3": JointLimit(
                "mixamorig:RightHandIndex3",
                JointType.FINGER,
                h_min=-5,
                h_max=5,  # Side-to-side
                p_min=0,
                p_max=90,  # Bend
                r_min=-2,
                r_max=2,  # Twist
                description="Right index finger DIP",
            ),
            # Thumb joints
            "mixamorig:RightHandThumb1": JointLimit(
                "mixamorig:RightHandThumb1",
                JointType.THUMB,
                h_min=-45,
                h_max=45,  # Side-to-side
                p_min=-30,
                p_max=90,  # Bend
                r_min=-45,
                r_max=45,  # Rotation
                description="Right thumb MCP",
            ),
            "mixamorig:RightHandThumb2": JointLimit(
                "mixamorig:RightHandThumb2",
                JointType.THUMB,
                h_min=-20,
                h_max=20,  # Side-to-side
                p_min=0,
                p_max=90,  # Bend
                r_min=-10,
                r_max=10,  # Twist
                description="Right thumb IP",
            ),
            "mixamorig:RightHandThumb3": JointLimit(
                "mixamorig:RightHandThumb3",
                JointType.THUMB,
                h_min=-10,
                h_max=10,  # Side-to-side
                p_min=0,
                p_max=60,  # Bend
                r_min=-5,
                r_max=5,  # Twist
                description="Right thumb tip",
            ),
            # Head and neck
            "mixamorig:Head": JointLimit(
                "mixamorig:Head",
                JointType.HEAD,
                h_min=-60,
                h_max=60,  # Turn left/right
                p_min=-45,
                p_max=45,  # Nod up/down
                r_min=-30,
                r_max=30,  # Tilt
                description="Head",
            ),
            "mixamorig:Neck": JointLimit(
                "mixamorig:Neck",
                JointType.NECK,
                h_min=-45,
                h_max=45,  # Turn left/right
                p_min=-30,
                p_max=30,  # Nod up/down
                r_min=-20,
                r_max=20,  # Tilt
                description="Neck",
            ),
        }

    def validate_pose(
        self, pose_data: Dict[str, List[float]]
    ) -> Tuple[bool, List[str]]:
        """
        Validate a pose to ensure all joints are within human limits.

        Args:
            pose_data: Dictionary of joint_name -> [h, p, r] values

        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        violations = []

        for joint_name, hpr in pose_data.items():
            if not isinstance(hpr, list) or len(hpr) != 3:
                violations.append(
                    f"Invalid HPR data for {joint_name}: {hpr} (expected 3 values)"
                )
                continue

            h, p, r = hpr[0], hpr[1], hpr[2]

            if joint_name in self.joint_limits:
                limit = self.joint_limits[joint_name]

                # Check each axis
                if h < limit.h_min or h > limit.h_max:
                    violations.append(
                        f"{joint_name} heading {h}° outside limits [{limit.h_min}, {limit.h_max}]°"
                    )

                if p < limit.p_min or p > limit.p_max:
                    violations.append(
                        f"{joint_name} pitch {p}° outside limits [{limit.p_min}, {limit.p_max}]°"
                    )

                if r < limit.r_min or r > limit.r_max:
                    violations.append(
                        f"{joint_name} roll {r}° outside limits [{limit.r_min}, {limit.r_max}]°"
                    )
            else:
                # Unknown joint - use conservative limits
                if abs(h) > 180 or abs(p) > 180 or abs(r) > 180:
                    violations.append(
                        f"Unknown joint {joint_name} has extreme values: H={h}°, P={p}°, R={r}°"
                    )

        return len(violations) == 0, violations

    def validate_pose_sequence(
        self, pose_sequence: List[Dict]
    ) -> Tuple[bool, List[str]]:
        """
        Validate a sequence of poses.

        Args:
            pose_sequence: List of pose dictionaries

        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        all_violations = []

        for i, pose_frame in enumerate(pose_sequence):
            if "poses" in pose_frame:
                # Convert poses to the format expected by validate_pose
                pose_data = {}
                for pose in pose_frame["poses"]:
                    if "joint" in pose and "h" in pose and "p" in pose and "r" in pose:
                        pose_data[pose["joint"]] = [pose["h"], pose["p"], pose["r"]]

                is_valid, violations = self.validate_pose(pose_data)
                if not is_valid:
                    all_violations.extend([f"Frame {i}: {v}" for v in violations])

        return len(all_violations) == 0, all_violations

    def get_joint_limit(self, joint_name: str) -> Optional[JointLimit]:
        """Get the movement limit for a specific joint."""
        return self.joint_limits.get(joint_name)

    def clamp_pose(
        self, joint_name: str, h: float, p: float, r: float
    ) -> Tuple[float, float, float]:
        """
        Clamp pose values to valid ranges.

        Args:
            joint_name: Name of the joint
            h, p, r: Heading, pitch, roll values

        Returns:
            Clamped h, p, r values
        """
        if joint_name not in self.joint_limits:
            # Unknown joint - use conservative limits
            return (
                max(-180, min(180, h)),
                max(-180, min(180, p)),
                max(-180, min(180, r)),
            )

        limit = self.joint_limits[joint_name]
        return (
            max(limit.h_min, min(limit.h_max, h)),
            max(limit.p_min, min(limit.p_max, p)),
            max(limit.r_min, min(limit.r_max, r)),
        )
