#!/usr/bin/env python3
"""
Unit tests for joint constraints functionality
"""

from typing import Dict, List

import pytest

from src.helpmesign.utils.joint_constraints import (
    JointConstraint,
    JointConstraintValidator,
    joint_validator,
)


class TestJointConstraint:
    """Test JointConstraint dataclass"""

    def test_joint_constraint_creation(self):
        """Test creating a joint constraint"""
        constraint = JointConstraint(
            min_h=-45,
            max_h=45,
            min_p=-30,
            max_p=30,
            min_r=-20,
            max_r=20,
            description="Test joint",
        )

        assert constraint.min_h == -45
        assert constraint.max_h == 45
        assert constraint.min_p == -30
        assert constraint.max_p == 30
        assert constraint.min_r == -20
        assert constraint.max_r == 20
        assert constraint.description == "Test joint"

    def test_joint_constraint_default_description(self):
        """Test joint constraint with default description"""
        constraint = JointConstraint(
            min_h=-45, max_h=45, min_p=-30, max_p=30, min_r=-20, max_r=20
        )

        assert constraint.description == ""


class TestJointConstraintValidator:
    """Test JointConstraintValidator functionality"""

    def test_validator_initialization(self):
        """Test validator initialization"""
        validator = JointConstraintValidator()
        assert validator is not None
        assert len(validator.constraints) > 0

    def test_clamp_value(self):
        """Test value clamping functionality"""
        validator = JointConstraintValidator()

        # Test within range
        assert validator._clamp_value(0, -10, 10) == 0

        # Test below minimum
        assert validator._clamp_value(-15, -10, 10) == -10

        # Test above maximum
        assert validator._clamp_value(15, -10, 10) == 10

    def test_validate_single_joint(self):
        """Test single joint validation"""
        validator = JointConstraintValidator()

        # Test valid values
        h, p, r = validator.validate_single_joint("mixamorig:RightHand", 0, 0, 0)
        assert h == 0
        assert p == 0
        assert r == 0

        # Test values that need clamping
        h, p, r = validator.validate_single_joint("mixamorig:RightHand", 50, 100, 120)
        assert h <= 30  # Should be clamped to max_h
        assert p <= 80  # Should be clamped to max_p
        assert r <= 90  # Should be clamped to max_r

    def test_validate_single_joint_unknown_joint(self):
        """Test validation of unknown joint"""
        validator = JointConstraintValidator()

        # Test unknown joint (should return original values)
        h, p, r = validator.validate_single_joint("UnknownJoint", 45, 60, 75)
        assert h == 45
        assert p == 60
        assert r == 75

    def test_validate_and_constrain_pose(self):
        """Test pose validation and constraining"""
        validator = JointConstraintValidator()

        # Test valid pose
        valid_pose = {"mixamorig:RightHand": [0, 0, 0], "mixamorig:LeftHand": [0, 0, 0]}

        constrained_pose = validator.validate_and_constrain_pose(valid_pose)
        assert constrained_pose == valid_pose

        # Test pose with violations
        invalid_pose = {
            "mixamorig:RightHand": [50, 100, 120],  # Values outside constraints
            "mixamorig:LeftHand": [0, 0, 0],
        }

        constrained_pose = validator.validate_and_constrain_pose(invalid_pose)
        assert constrained_pose != invalid_pose

        # Check that values were clamped
        right_hand = constrained_pose["mixamorig:RightHand"]
        assert right_hand[0] <= 30  # h should be clamped
        assert right_hand[1] <= 80  # p should be clamped
        assert right_hand[2] <= 90  # r should be clamped

    def test_validate_and_constrain_pose_mixed_joints(self):
        """Test pose validation with mixed valid and invalid joints"""
        validator = JointConstraintValidator()

        pose = {
            "mixamorig:RightHand": [50, 100, 120],  # Invalid
            "mixamorig:LeftHand": [0, 0, 0],  # Valid
            "UnknownJoint": [45, 60, 75],  # Unknown (should pass through)
        }

        constrained_pose = validator.validate_and_constrain_pose(pose)

        # Right hand should be constrained
        right_hand = constrained_pose["mixamorig:RightHand"]
        assert right_hand[0] <= 30
        assert right_hand[1] <= 80
        assert right_hand[2] <= 90

        # Left hand should remain unchanged
        assert constrained_pose["mixamorig:LeftHand"] == [0, 0, 0]

        # Unknown joint should pass through
        assert constrained_pose["UnknownJoint"] == [45, 60, 75]

    def test_is_pose_valid(self):
        """Test pose validity checking"""
        validator = JointConstraintValidator()

        # Test valid pose
        valid_pose = {"mixamorig:RightHand": [0, 0, 0], "mixamorig:LeftHand": [0, 0, 0]}
        assert validator.is_pose_valid(valid_pose) is True

        # Test invalid pose
        invalid_pose = {
            "mixamorig:RightHand": [50, 100, 120],  # Values outside constraints
            "mixamorig:LeftHand": [0, 0, 0],
        }
        assert validator.is_pose_valid(invalid_pose) is False

    def test_get_joint_constraint(self):
        """Test getting joint constraint information"""
        validator = JointConstraintValidator()

        # Test existing joint
        constraint = validator.get_joint_constraint("mixamorig:RightHand")
        assert constraint is not None
        assert constraint.description == "Right wrist"

        # Test non-existing joint
        constraint = validator.get_joint_constraint("NonExistentJoint")
        assert constraint is None

    def test_add_custom_constraint(self):
        """Test adding custom constraints"""
        validator = JointConstraintValidator()

        custom_constraint = JointConstraint(
            min_h=-10,
            max_h=10,
            min_p=-10,
            max_p=10,
            min_r=-10,
            max_r=10,
            description="Custom joint",
        )

        validator.add_custom_constraint("CustomJoint", custom_constraint)

        # Verify constraint was added
        constraint = validator.get_joint_constraint("CustomJoint")
        assert constraint is not None
        assert constraint.description == "Custom joint"

    def test_pose_with_invalid_hpr_format(self):
        """Test handling of poses with invalid HPR format"""
        validator = JointConstraintValidator()

        pose = {
            "mixamorig:RightHand": [0, 0],  # Missing roll component
            "mixamorig:LeftHand": [
                0,
                0,
                0,
                0,
            ],  # Too many components (should be processed)
            "mixamorig:Head": "invalid",  # Not a list
        }

        constrained_pose = validator.validate_and_constrain_pose(pose)

        # Should skip invalid entries and only process valid ones
        assert "mixamorig:RightHand" not in constrained_pose  # Missing component
        assert (
            "mixamorig:LeftHand" in constrained_pose
        )  # Too many components but still valid
        assert "mixamorig:Head" not in constrained_pose  # Not a list


class TestGlobalJointValidator:
    """Test the global joint validator instance"""

    def test_global_validator_availability(self):
        """Test that global validator is available"""
        assert joint_validator is not None
        assert isinstance(joint_validator, JointConstraintValidator)

    def test_global_validator_constraints(self):
        """Test that global validator has constraints"""
        assert len(joint_validator.constraints) > 0

        # Check for some expected joints
        expected_joints = [
            "mixamorig:RightHand",
            "mixamorig:LeftHand",
            "mixamorig:Head",
            "mixamorig:Neck",
        ]

        for joint in expected_joints:
            constraint = joint_validator.get_joint_constraint(joint)
            assert constraint is not None, f"Constraint for {joint} should exist"

    def test_global_validator_functionality(self):
        """Test global validator functionality"""
        pose = {"mixamorig:RightHand": [50, 100, 120]}

        constrained_pose = joint_validator.validate_and_constrain_pose(pose)
        assert constrained_pose != pose

        # Check that values were properly constrained
        right_hand = constrained_pose["mixamorig:RightHand"]
        assert right_hand[0] <= 30
        assert right_hand[1] <= 80
        assert right_hand[2] <= 90


class TestFingerJointConstraints:
    """Test specific finger joint constraints"""

    def test_thumb_constraints(self):
        """Test thumb joint constraints"""
        validator = JointConstraintValidator()

        # Test thumb CMC joint
        constraint = validator.get_joint_constraint("mixamorig:RightHandThumb1")
        assert constraint is not None
        assert constraint.description == "Right thumb CMC joint"

        # Test thumb MCP joint
        constraint = validator.get_joint_constraint("mixamorig:RightHandThumb2")
        assert constraint is not None
        assert constraint.description == "Right thumb MCP joint"

        # Test thumb IP joint
        constraint = validator.get_joint_constraint("mixamorig:RightHandThumb3")
        assert constraint is not None
        assert constraint.description == "Right thumb IP joint"

    def test_finger_constraints(self):
        """Test finger joint constraints"""
        validator = JointConstraintValidator()

        # Test index finger
        constraint = validator.get_joint_constraint("mixamorig:RightHandIndex1")
        assert constraint is not None
        assert constraint.description == "Right index MCP joint"

        # Test middle finger
        constraint = validator.get_joint_constraint("mixamorig:RightHandMiddle1")
        assert constraint is not None
        assert constraint.description == "Right middle MCP joint"

        # Test ring finger
        constraint = validator.get_joint_constraint("mixamorig:RightHandRing1")
        assert constraint is not None
        assert constraint.description == "Right ring MCP joint"

        # Test pinky finger
        constraint = validator.get_joint_constraint("mixamorig:RightHandPinky1")
        assert constraint is not None
        assert constraint.description == "Right pinky MCP joint"

    def test_left_hand_mirroring(self):
        """Test that left hand constraints are properly mirrored"""
        validator = JointConstraintValidator()

        # Compare right and left hand constraints
        right_hand = validator.get_joint_constraint("mixamorig:RightHand")
        left_hand = validator.get_joint_constraint("mixamorig:LeftHand")

        assert right_hand is not None
        assert left_hand is not None

        # Constraints should be the same for wrists
        assert right_hand.min_h == left_hand.min_h
        assert right_hand.max_h == left_hand.max_h
        assert right_hand.min_p == left_hand.min_p
        assert right_hand.max_p == left_hand.max_p
        assert right_hand.min_r == left_hand.min_r
        assert right_hand.max_r == left_hand.max_r


class TestFacialJointConstraints:
    """Test facial joint constraints"""

    def test_facial_constraints(self):
        """Test facial joint constraints"""
        validator = JointConstraintValidator()

        # Test jaw
        constraint = validator.get_joint_constraint("mixamorig:Jaw")
        assert constraint is not None
        assert constraint.description == "Jaw movement"

        # Test eyes
        left_eye = validator.get_joint_constraint("mixamorig:LeftEye")
        right_eye = validator.get_joint_constraint("mixamorig:RightEye")

        assert left_eye is not None
        assert right_eye is not None
        assert left_eye.description == "Left eye movement"
        assert right_eye.description == "Right eye movement"

        # Eye constraints should be the same
        assert left_eye.min_h == right_eye.min_h
        assert left_eye.max_h == right_eye.max_h
        assert left_eye.min_p == right_eye.min_p
        assert left_eye.max_p == right_eye.max_p
        assert left_eye.min_r == right_eye.min_r
        assert left_eye.max_r == right_eye.max_r
