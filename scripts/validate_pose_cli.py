#!/usr/bin/env python3
"""
Command-line pose validation script
Validates poses without requiring the full GUI
"""

import json
import os
import sys
from typing import Dict, List

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from helpmesign.utils.joint_constraints import joint_validator


def validate_pose(letter: str, hand: str = "right") -> Dict:
    """Validate a pose for a specific letter and hand"""
    print(f"\n=== Validating ASL {letter} ({hand} hand) ===")
    
    # Load pose data
    file_path = f"resources/data/signs/asl/asl_{hand}_hand.json"
    
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if "alphabet" not in data or letter not in data["alphabet"]:
            return {"error": f"No pose data found for letter {letter}"}
        
        pose_data = data["alphabet"][letter].get("pose", {})
        
        if not pose_data:
            return {"error": f"No pose data in letter {letter}"}
        
        print(f"Loaded pose with {len(pose_data)} joints")
        
        # Validate pose
        constrained_pose = joint_validator.validate_and_constrain_pose(pose_data)
        is_valid = joint_validator.is_pose_valid(pose_data)
        
        # Check for violations
        violations = []
        for joint_name, original_hpr in pose_data.items():
            if joint_name in constrained_pose:
                constrained_hpr = constrained_pose[joint_name]
                if original_hpr != constrained_hpr:
                    violations.append({
                        "joint": joint_name,
                        "original": original_hpr,
                        "constrained": constrained_hpr
                    })
        
        # Calculate pose score
        score = calculate_pose_score(pose_data)
        
        result = {
            "letter": letter,
            "hand": hand,
            "is_valid": is_valid,
            "violations": violations,
            "violation_count": len(violations),
            "pose_score": score,
            "joint_count": len(pose_data),
            "key_joints": get_key_joints(pose_data)
        }
        
        # Print results
        print(f"Validation Status: {'VALID' if is_valid else 'INVALID'}")
        print(f"Violations: {len(violations)}")
        print(f"Pose Score: {score:.1f}/100")
        
        if violations:
            print("\nConstraint Violations:")
            for violation in violations:
                print(f"  {violation['joint']}: {violation['original']} → {violation['constrained']}")
        
        print(f"\nKey Joint Positions:")
        for joint_name, hpr in result["key_joints"].items():
            print(f"  {joint_name}: [{hpr[0]:.1f}, {hpr[1]:.1f}, {hpr[2]:.1f}]")
        
        return result
        
    except Exception as e:
        return {"error": f"Error validating pose: {e}"}


def calculate_pose_score(pose_data: Dict[str, List[float]]) -> float:
    """Calculate a visibility score for the pose"""
    arm_pose = pose_data.get("mixamorig:RightArm", [0, 0, 0])
    shoulder_pose = pose_data.get("mixamorig:RightShoulder", [0, 0, 0])
    
    arm_pitch = arm_pose[1]
    shoulder_pitch = shoulder_pose[1]
    
    # Base score from arm position (30-60 degrees is optimal)
    if 30 <= arm_pitch <= 60:
        arm_score = 100 - abs(arm_pitch - 45) * 2  # Peak at 45 degrees
    else:
        arm_score = max(0, 100 - abs(arm_pitch - 45) * 3)
    
    # Shoulder support score
    if 0 <= shoulder_pitch <= 30:
        shoulder_score = 100 - abs(shoulder_pitch - 15) * 2  # Peak at 15 degrees
    else:
        shoulder_score = max(0, 100 - abs(shoulder_pitch - 15) * 3)
    
    return (arm_score + shoulder_score) / 2


def get_key_joints(pose_data: Dict[str, List[float]]) -> Dict[str, List[float]]:
    """Get key joint positions for display"""
    key_joints = {}
    
    # Important joints for sign language
    important_joints = [
        "mixamorig:RightShoulder",
        "mixamorig:RightArm", 
        "mixamorig:RightForeArm",
        "mixamorig:RightHand",
        "mixamorig:RightHandIndex1",
        "mixamorig:RightHandThumb1"
    ]
    
    for joint_name in important_joints:
        if joint_name in pose_data:
            key_joints[joint_name] = pose_data[joint_name]
    
    return key_joints


def validate_all_letters(hand: str = "right") -> Dict:
    """Validate poses for all available letters"""
    print(f"\n=== Validating All ASL Letters ({hand} hand) ===")
    
    file_path = f"resources/data/signs/asl/asl_{hand}_hand.json"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return {}
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if "alphabet" not in data:
            print("No alphabet data found")
            return {}
        
        results = {}
        valid_count = 0
        total_count = 0
        
        for letter in sorted(data["alphabet"].keys()):
            if letter.isalpha():  # Only validate letters
                result = validate_pose(letter, hand)
                results[letter] = result
                
                if result.get("is_valid", False):
                    valid_count += 1
                total_count += 1
        
        print(f"\n=== Summary ===")
        print(f"Total letters: {total_count}")
        print(f"Valid poses: {valid_count}")
        print(f"Invalid poses: {total_count - valid_count}")
        print(f"Success rate: {(valid_count/total_count)*100:.1f}%")
        
        # Show invalid poses
        invalid_poses = [letter for letter, result in results.items() 
                        if not result.get("is_valid", True)]
        if invalid_poses:
            print(f"Invalid poses: {', '.join(invalid_poses)}")
        
        return results
        
    except Exception as e:
        print(f"Error validating all letters: {e}")
        return {}


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python validate_pose_cli.py <letter> [hand]")
        print("  python validate_pose_cli.py all [hand]")
        print("")
        print("Examples:")
        print("  python validate_pose_cli.py A")
        print("  python validate_pose_cli.py A left")
        print("  python validate_pose_cli.py all")
        print("  python validate_pose_cli.py all left")
        return
    
    letter = sys.argv[1].upper()
    hand = sys.argv[2] if len(sys.argv) > 2 else "right"
    
    if letter == "ALL":
        validate_all_letters(hand)
    else:
        result = validate_pose(letter, hand)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"\nValidation complete for {letter}")


if __name__ == "__main__":
    main()
