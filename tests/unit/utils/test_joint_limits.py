"""
Tests for joint movement limits and validation.
Ensures inhuman positions are detected and prevented.
"""

from unittest.mock import Mock

import pytest

from src.helpmesign.utils.joint_limits import JointLimit, JointType, JointValidator


class TestJointLimits:
    """Test joint limit definitions and validation."""

    def test_joint_limit_creation(self):
        """Test creating joint limits with proper ranges."""
        validator = JointValidator()

        # Test arm limits
        right_arm_limit = validator.get_joint_limit("mixamorig:RightArm")
        assert right_arm_limit is not None
        assert right_arm_limit.joint_type == JointType.ARM
        assert right_arm_limit.h_min == -90
        assert right_arm_limit.h_max == 90
        assert right_arm_limit.p_min == -45
        assert right_arm_limit.p_max == 180

        # Test finger limits
        index_limit = validator.get_joint_limit("mixamorig:RightHandIndex1")
        assert index_limit is not None
        assert index_limit.joint_type == JointType.FINGER
        assert index_limit.h_min == -30
        assert index_limit.h_max == 30
        assert index_limit.p_min == 0
        assert index_limit.p_max == 90

    def test_valid_pose_validation(self):
        """Test that valid poses pass validation."""
        validator = JointValidator()

        # Valid pose data
        valid_pose = {
            "mixamorig:RightArm": [0, 45, 0],  # Normal arm position
            "mixamorig:RightHand": [0, 0, 0],  # Neutral hand
            "mixamorig:RightHandIndex1": [0, 45, 0],  # Normal finger bend
        }

        is_valid, violations = validator.validate_pose(valid_pose)
        assert is_valid
        assert len(violations) == 0

    def test_inhuman_arm_positions(self):
        """Test detection of inhuman arm positions."""
        validator = JointValidator()

        # Test extreme arm positions
        inhuman_poses = [
            # Arm bent backwards (impossible)
            {"mixamorig:RightArm": [0, 200, 0]},
            # Arm rotated too far
            {"mixamorig:RightArm": [120, 45, 0]},
            # Arm twisted impossibly
            {"mixamorig:RightArm": [0, 45, 90]},
        ]

        for pose in inhuman_poses:
            is_valid, violations = validator.validate_pose(pose)
            assert not is_valid
            assert len(violations) > 0
            assert "outside limits" in violations[0]

    def test_inhuman_finger_positions(self):
        """Test detection of inhuman finger positions."""
        validator = JointValidator()

        # Test extreme finger positions
        inhuman_finger_poses = [
            # Finger bent backwards (impossible)
            {"mixamorig:RightHandIndex1": [0, -45, 0]},
            # Finger bent too far
            {"mixamorig:RightHandIndex1": [0, 120, 0]},
            # Finger twisted too much
            {"mixamorig:RightHandIndex1": [0, 45, 30]},
        ]

        for pose in inhuman_finger_poses:
            is_valid, violations = validator.validate_pose(pose)
            assert not is_valid
            assert len(violations) > 0

    def test_inhuman_hand_positions(self):
        """Test detection of inhuman hand positions."""
        validator = JointValidator()

        # Test extreme hand positions
        inhuman_hand_poses = [
            # Hand rotated impossibly
            {"mixamorig:RightHand": [0, 0, 180]},
            # Hand bent too far
            {"mixamorig:RightHand": [0, 90, 0]},
        ]

        for pose in inhuman_hand_poses:
            is_valid, violations = validator.validate_pose(pose)
            assert not is_valid
            assert len(violations) > 0

    def test_inhuman_head_positions(self):
        """Test detection of inhuman head positions."""
        validator = JointValidator()

        # Test extreme head positions
        inhuman_head_poses = [
            # Head turned too far
            {"mixamorig:Head": [90, 0, 0]},
            # Head tilted too far
            {"mixamorig:Head": [0, 0, 60]},
            # Head bent too far
            {"mixamorig:Head": [0, 90, 0]},
        ]

        for pose in inhuman_head_poses:
            is_valid, violations = validator.validate_pose(pose)
            assert not is_valid
            assert len(violations) > 0

    def test_pose_sequence_validation(self):
        """Test validation of pose sequences."""
        validator = JointValidator()

        # Valid pose sequence
        valid_sequence = [
            {
                "duration_ms": 500,
                "poses": [
                    {"joint": "mixamorig:RightArm", "h": 0, "p": 45, "r": 0},
                    {"joint": "mixamorig:RightHand", "h": 0, "p": 0, "r": 0},
                ],
            }
        ]

        is_valid, violations = validator.validate_pose_sequence(valid_sequence)
        assert is_valid
        assert len(violations) == 0

        # Invalid pose sequence
        invalid_sequence = [
            {
                "duration_ms": 500,
                "poses": [
                    {
                        "joint": "mixamorig:RightArm",
                        "h": 0,
                        "p": 200,
                        "r": 0,
                    },  # Impossible
                    {"joint": "mixamorig:RightHand", "h": 0, "p": 0, "r": 0},
                ],
            }
        ]

        is_valid, violations = validator.validate_pose_sequence(invalid_sequence)
        assert not is_valid
        assert len(violations) > 0

    def test_unknown_joint_handling(self):
        """Test handling of unknown joints."""
        validator = JointValidator()

        # Unknown joint with extreme values
        unknown_pose = {"unknown_joint": [360, 360, 360]}  # Impossible values

        is_valid, violations = validator.validate_pose(unknown_pose)
        assert not is_valid
        assert len(violations) > 0
        assert "extreme values" in violations[0]

    def test_pose_clamping(self):
        """Test that pose values are properly clamped to valid ranges."""
        validator = JointValidator()

        # Test clamping extreme values
        h, p, r = validator.clamp_pose("mixamorig:RightArm", 200, -100, 90)
        assert h == 90  # Clamped to max
        assert p == -45  # Clamped to min
        assert r == 45  # Clamped to max

        # Test clamping unknown joint
        h, p, r = validator.clamp_pose("unknown_joint", 360, -360, 360)
        assert h == 180  # Clamped to conservative limit
        assert p == -180
        assert r == 180

    def test_current_pose_data_validation(self):
        """Test validation of current pose data in the system."""
        validator = JointValidator()

        # Test current pose mappings from the system
        current_poses = [
            # From pose_mappings.json
            {"mixamorig:RightArm": [0, 45, 0]},  # hello sign
            {"mixamorig:RightArm": [0, 30, 0]},  # thank_you sign
            {"mixamorig:Head": [0, 15, 0]},  # yes sign
            {"mixamorig:Head": [15, 0, 0]},  # no sign
        ]

        for pose in current_poses:
            is_valid, violations = validator.validate_pose(pose)
            assert (
                is_valid
            ), f"Current pose failed validation: {pose}, violations: {violations}"

    def test_edge_case_validation(self):
        """Test edge cases in validation."""
        validator = JointValidator()

        # Test boundary values
        boundary_pose = {"mixamorig:RightArm": [90, 180, 45]}  # All at maximum limits

        is_valid, violations = validator.validate_pose(boundary_pose)
        assert is_valid  # Should be valid at boundaries

        # Test just beyond boundaries
        beyond_boundary_pose = {
            "mixamorig:RightArm": [91, 181, 46]  # Just beyond limits
        }

        is_valid, violations = validator.validate_pose(beyond_boundary_pose)
        assert not is_valid
        assert len(violations) == 3  # All three axes should violate

    def test_multiple_joint_violations(self):
        """Test detection of multiple joint violations in a single pose."""
        validator = JointValidator()

        # Multiple joints with violations
        multi_violation_pose = {
            "mixamorig:RightArm": [200, 300, 100],  # All axes violated
            "mixamorig:RightHand": [100, 100, 200],  # All axes violated
            "mixamorig:RightHandIndex1": [50, 150, 30],  # All axes violated
        }

        is_valid, violations = validator.validate_pose(multi_violation_pose)
        assert not is_valid
        assert len(violations) >= 9  # At least 3 violations per joint

    def test_invalid_data_handling(self):
        """Test handling of invalid pose data."""
        validator = JointValidator()

        # Test incomplete HPR data
        invalid_poses = [
            {"mixamorig:RightArm": [0, 45]},  # Missing roll
            {"mixamorig:RightArm": [0]},  # Missing pitch and roll
            {"mixamorig:RightArm": []},  # Empty array
            {"mixamorig:RightArm": [0, 45, 0, 90]},  # Too many values
        ]

        for pose in invalid_poses:
            is_valid, violations = validator.validate_pose(pose)
            assert not is_valid
            assert len(violations) > 0
            assert "Invalid HPR data" in violations[0]


class TestJointValidatorIntegration:
    """Integration tests for joint validator with real pose data."""

    def test_real_sign_pose_validation(self):
        """Test validation of real sign language poses."""
        validator = JointValidator()

        # Real sign poses that should be valid
        real_sign_poses = [
            # Hello sign
            {
                "mixamorig:RightArm": [0, 45, 0],
                "mixamorig:RightForeArm": [0, 0, 0],
                "mixamorig:RightHand": [0, 0, 0],
            },
            # Thank you sign
            {
                "mixamorig:RightArm": [0, 30, 0],
                "mixamorig:RightForeArm": [0, 0, 0],
                "mixamorig:RightHand": [0, 0, 0],
            },
            # Welcome sign (both hands)
            {
                "mixamorig:RightArm": [0, 30, 0],
                "mixamorig:LeftArm": [0, 30, 0],
                "mixamorig:RightHand": [0, 0, 0],
                "mixamorig:LeftHand": [0, 0, 0],
            },
        ]

        for pose in real_sign_poses:
            is_valid, violations = validator.validate_pose(pose)
            assert (
                is_valid
            ), f"Real sign pose failed validation: {pose}, violations: {violations}"

    def test_finger_spelling_validation(self):
        """Test validation of finger spelling poses."""
        validator = JointValidator()

        # Finger spelling poses
        finger_spelling_poses = [
            # Letter A (fist)
            {"mixamorig:RightHand": [0, 0, 0]},
            # Letter B (index finger up)
            {"mixamorig:RightHandIndex1": [0, 90, 0]},
            # Letter C (curved hand)
            {"mixamorig:RightHand": [0, 0, 45]},
        ]

        for pose in finger_spelling_poses:
            is_valid, violations = validator.validate_pose(pose)
            assert (
                is_valid
            ), f"Finger spelling pose failed validation: {pose}, violations: {violations}"
