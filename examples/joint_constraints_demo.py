#!/usr/bin/env python3
"""
Demonstration of joint constraints functionality
Shows how character joints are constrained to human anatomical limits
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from helpmesign.utils.joint_constraints import joint_validator, JointConstraint


def demo_joint_constraints():
    """Demonstrate joint constraint functionality"""
    
    print("🤖 Joint Constraints Demo")
    print("=" * 50)
    print()
    
    # Example 1: Valid pose
    print("📋 Example 1: Valid pose (within human limits)")
    valid_pose = {
        "mixamorig:RightHand": [0, 0, 0],      # Neutral wrist position
        "mixamorig:LeftHand": [0, 0, 0],       # Neutral wrist position
        "mixamorig:Head": [10, 5, 0],          # Slight head turn
        "mixamorig:RightHandIndex1": [0, 45, 0]  # Index finger bent
    }
    
    print(f"Original pose: {valid_pose}")
    constrained_pose = joint_validator.validate_and_constrain_pose(valid_pose)
    print(f"Constrained pose: {constrained_pose}")
    print(f"Is valid: {joint_validator.is_pose_valid(valid_pose)}")
    print()
    
    # Example 2: Invalid pose with violations
    print("⚠️  Example 2: Invalid pose (beyond human limits)")
    invalid_pose = {
        "mixamorig:RightHand": [90, 180, 270],     # Impossible wrist angles
        "mixamorig:LeftHand": [0, 0, 0],           # Valid
        "mixamorig:Head": [200, 100, 50],          # Impossible head angles
        "mixamorig:RightHandIndex1": [0, 200, 0]   # Impossible finger bend
    }
    
    print(f"Original pose: {invalid_pose}")
    constrained_pose = joint_validator.validate_and_constrain_pose(invalid_pose)
    print(f"Constrained pose: {constrained_pose}")
    print(f"Is valid: {joint_validator.is_pose_valid(invalid_pose)}")
    print()
    
    # Example 3: Get constraint information
    print("🔍 Example 3: Joint constraint information")
    joints_to_check = [
        "mixamorig:RightHand",
        "mixamorig:RightHandIndex1", 
        "mixamorig:Head",
        "mixamorig:Neck"
    ]
    
    for joint in joints_to_check:
        constraint = joint_validator.get_joint_constraint(joint)
        if constraint:
            print(f"{joint}:")
            print(f"  Description: {constraint.description}")
            print(f"  Heading (H): {constraint.min_h}° to {constraint.max_h}°")
            print(f"  Pitch (P): {constraint.min_p}° to {constraint.max_p}°")
            print(f"  Roll (R): {constraint.min_r}° to {constraint.max_r}°")
            print()
    
    # Example 4: Single joint validation
    print("🎯 Example 4: Single joint validation")
    test_values = [
        ("mixamorig:RightHand", 0, 0, 0),      # Valid
        ("mixamorig:RightHand", 50, 100, 120), # Invalid
        ("mixamorig:Head", 10, 5, 0),          # Valid
        ("mixamorig:Head", 100, 60, 40),       # Invalid
    ]
    
    for joint_name, h, p, r in test_values:
        constrained_h, constrained_p, constrained_r = joint_validator.validate_single_joint(joint_name, h, p, r)
        print(f"{joint_name}:")
        print(f"  Original: H={h}°, P={p}°, R={r}°")
        print(f"  Constrained: H={constrained_h}°, P={constrained_p}°, R={constrained_r}°")
        print()
    
    # Example 5: Add custom constraint
    print("🔧 Example 5: Adding custom constraint")
    custom_constraint = JointConstraint(
        min_h=-30, max_h=30,
        min_p=-20, max_p=20,
        min_r=-15, max_r=15,
        description="Custom elbow joint"
    )
    
    joint_validator.add_custom_constraint("CustomElbow", custom_constraint)
    
    # Test the custom constraint
    test_pose = {"CustomElbow": [50, 30, 25]}  # Values outside constraints
    constrained = joint_validator.validate_and_constrain_pose(test_pose)
    print(f"Custom joint test:")
    print(f"  Original: {test_pose}")
    print(f"  Constrained: {constrained}")
    print()
    
    print("✅ Joint constraints demo completed!")


def demo_finger_constraints():
    """Demonstrate finger-specific constraints"""
    
    print("👆 Finger Joint Constraints Demo")
    print("=" * 40)
    print()
    
    # Finger joints
    finger_joints = [
        "mixamorig:RightHandThumb1",   # Thumb CMC
        "mixamorig:RightHandThumb2",   # Thumb MCP
        "mixamorig:RightHandThumb3",   # Thumb IP
        "mixamorig:RightHandIndex1",   # Index MCP
        "mixamorig:RightHandIndex2",   # Index PIP
        "mixamorig:RightHandIndex3",   # Index DIP
    ]
    
    print("Finger joint constraints:")
    for joint in finger_joints:
        constraint = joint_validator.get_joint_constraint(joint)
        if constraint:
            print(f"{joint}:")
            print(f"  {constraint.description}")
            print(f"  H: {constraint.min_h}° to {constraint.max_h}°")
            print(f"  P: {constraint.min_p}° to {constraint.max_p}°")
            print(f"  R: {constraint.min_r}° to {constraint.max_r}°")
            print()
    
    # Test finger pose
    print("Testing finger pose:")
    finger_pose = {
        "mixamorig:RightHandThumb1": [0, 0, 0],    # Neutral
        "mixamorig:RightHandIndex1": [0, 90, 0],   # Index bent (valid)
        "mixamorig:RightHandIndex2": [0, 120, 0],  # Index PIP bent (valid)
        "mixamorig:RightHandIndex3": [0, 90, 0],   # Index DIP bent (valid)
    }
    
    print(f"Original finger pose: {finger_pose}")
    constrained = joint_validator.validate_and_constrain_pose(finger_pose)
    print(f"Constrained finger pose: {constrained}")
    print(f"Is valid: {joint_validator.is_pose_valid(finger_pose)}")
    print()


def demo_facial_constraints():
    """Demonstrate facial joint constraints"""
    
    print("😊 Facial Joint Constraints Demo")
    print("=" * 35)
    print()
    
    # Facial joints
    facial_joints = [
        "mixamorig:Jaw",
        "mixamorig:LeftEye",
        "mixamorig:RightEye"
    ]
    
    print("Facial joint constraints:")
    for joint in facial_joints:
        constraint = joint_validator.get_joint_constraint(joint)
        if constraint:
            print(f"{joint}:")
            print(f"  {constraint.description}")
            print(f"  H: {constraint.min_h}° to {constraint.max_h}°")
            print(f"  P: {constraint.min_p}° to {constraint.max_p}°")
            print(f"  R: {constraint.min_r}° to {constraint.max_r}°")
            print()
    
    # Test facial pose
    print("Testing facial pose:")
    facial_pose = {
        "mixamorig:Jaw": [0, 10, 0],      # Slightly open jaw
        "mixamorig:LeftEye": [5, 0, 0],   # Slight eye movement
        "mixamorig:RightEye": [5, 0, 0],  # Slight eye movement
    }
    
    print(f"Original facial pose: {facial_pose}")
    constrained = joint_validator.validate_and_constrain_pose(facial_pose)
    print(f"Constrained facial pose: {constrained}")
    print(f"Is valid: {joint_validator.is_pose_valid(facial_pose)}")
    print()


if __name__ == "__main__":
    try:
        demo_joint_constraints()
        print()
        demo_finger_constraints()
        print()
        demo_facial_constraints()
        
    except Exception as e:
        print(f"Error running demo: {e}")
        import traceback
        traceback.print_exc()
