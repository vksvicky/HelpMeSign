#!/usr/bin/env python3
"""
Pose Optimization Script
Demonstrates how to use TDD to optimize sign language poses
"""

import json
import os
import sys
from typing import Dict, List, Tuple

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from helpmesign.utils.joint_constraints import JointConstraintValidator


class PoseOptimizer:
    """Optimize sign language poses using TDD principles"""
    
    def __init__(self):
        self.validator = JointConstraintValidator()
    
    def optimize_pose(self, letter: str, sign_type: str = "alphabet") -> Dict[str, List[float]]:
        """
        Optimize a pose for a specific letter using TDD principles
        
        Args:
            letter: The letter to optimize (e.g., "A", "B", "C")
            sign_type: Type of sign ("alphabet" or "number")
            
        Returns:
            Optimized pose data
        """
        print(f"\n=== Optimizing ASL {letter} Pose ===")
        
        # Step 1: Load current pose
        current_pose = self._load_current_pose(letter, sign_type)
        if not current_pose:
            print(f"No current pose found for {letter}")
            return {}
        
        print(f"Current pose loaded: {len(current_pose)} joints")
        
        # Step 2: Validate current pose
        current_valid = self.validator.is_pose_valid(current_pose)
        print(f"Current pose valid: {current_valid}")
        
        # Step 3: Test different arm positions for optimal chest height
        optimal_arm_positions = self._find_optimal_arm_positions()
        
        # Step 4: Test different shoulder positions
        optimal_shoulder_positions = self._find_optimal_shoulder_positions()
        
        # Step 5: Combine optimal positions
        best_pose = self._combine_optimal_positions(
            current_pose, optimal_arm_positions, optimal_shoulder_positions
        )
        
        # Step 6: Validate optimized pose
        optimized_valid = self.validator.is_pose_valid(best_pose)
        print(f"Optimized pose valid: {optimized_valid}")
        
        # Step 7: Calculate improvement score
        current_score = self._calculate_pose_score(current_pose)
        optimized_score = self._calculate_pose_score(best_pose)
        improvement = optimized_score - current_score
        
        print(f"Current score: {current_score:.1f}")
        print(f"Optimized score: {optimized_score:.1f}")
        print(f"Improvement: {improvement:+.1f}")
        
        return best_pose
    
    def _load_current_pose(self, letter: str, sign_type: str) -> Dict[str, List[float]]:
        """Load current pose from JSON file"""
        data_path = f"resources/data/signs/asl/asl_right_hand.json"
        
        try:
            if os.path.exists(data_path):
                with open(data_path, 'r') as f:
                    data = json.load(f)
                    if sign_type in data and letter in data[sign_type]:
                        return data[sign_type][letter].get("pose", {})
        except Exception as e:
            print(f"Error loading pose for {letter}: {e}")
        
        return {}
    
    def _find_optimal_arm_positions(self) -> List[Tuple[int, float]]:
        """Find optimal arm positions for chest height visibility"""
        print("\nTesting arm positions for chest height...")
        
        test_arm_positions = [0, 15, 30, 45, 60, 75, 90]
        optimal_positions = []
        
        for arm_pitch in test_arm_positions:
            test_pose = {
                "mixamorig:RightShoulder": [0, 15, 0],  # Fixed shoulder
                "mixamorig:RightArm": [0, arm_pitch, 0],
                "mixamorig:RightForeArm": [0, 0, 0],
                "mixamorig:RightHand": [0, 0, 0],
            }
            
            # Validate pose
            constrained_pose = self.validator.validate_and_constrain_pose(test_pose)
            is_valid = self.validator.is_pose_valid(constrained_pose)
            
            # Calculate score
            score = self._calculate_pose_score(constrained_pose)
            
            # Check if this is a good chest height position
            arm_pose = constrained_pose.get("mixamorig:RightArm", [0, 0, 0])
            if 30 <= arm_pose[1] <= 60:  # Chest height range
                optimal_positions.append((arm_pitch, score))
                print(f"  Arm pitch {arm_pitch}°: Score {score:.1f}, Valid: {is_valid}")
        
        return optimal_positions
    
    def _find_optimal_shoulder_positions(self) -> List[Tuple[int, float]]:
        """Find optimal shoulder positions to support arm"""
        print("\nTesting shoulder positions...")
        
        test_shoulder_positions = [0, 10, 15, 20, 25, 30, 45]
        optimal_positions = []
        
        for shoulder_pitch in test_shoulder_positions:
            test_pose = {
                "mixamorig:RightShoulder": [0, shoulder_pitch, 0],
                "mixamorig:RightArm": [0, 45, 0],  # Fixed arm
                "mixamorig:RightForeArm": [0, 0, 0],
                "mixamorig:RightHand": [0, 0, 0],
            }
            
            # Validate pose
            constrained_pose = self.validator.validate_and_constrain_pose(test_pose)
            is_valid = self.validator.is_pose_valid(constrained_pose)
            
            # Calculate score
            score = self._calculate_pose_score(constrained_pose)
            
            # Check if this is a good shoulder position
            shoulder_pose = constrained_pose.get("mixamorig:RightShoulder", [0, 0, 0])
            if 0 <= shoulder_pose[1] <= 30:  # Good shoulder range
                optimal_positions.append((shoulder_pitch, score))
                print(f"  Shoulder pitch {shoulder_pitch}°: Score {score:.1f}, Valid: {is_valid}")
        
        return optimal_positions
    
    def _combine_optimal_positions(
        self, 
        current_pose: Dict[str, List[float]], 
        arm_positions: List[Tuple[int, float]], 
        shoulder_positions: List[Tuple[int, float]]
    ) -> Dict[str, List[float]]:
        """Combine optimal arm and shoulder positions"""
        print("\nCombining optimal positions...")
        
        # Find best arm and shoulder positions
        best_arm = max(arm_positions, key=lambda x: x[1]) if arm_positions else (45, 0)
        best_shoulder = max(shoulder_positions, key=lambda x: x[1]) if shoulder_positions else (15, 0)
        
        print(f"Best arm position: {best_arm[0]}° (score: {best_arm[1]:.1f})")
        print(f"Best shoulder position: {best_shoulder[0]}° (score: {best_shoulder[1]:.1f})")
        
        # Create optimized pose
        optimized_pose = current_pose.copy()
        optimized_pose["mixamorig:RightShoulder"] = [0, best_shoulder[0], 0]
        optimized_pose["mixamorig:RightArm"] = [0, best_arm[0], 0]
        
        return optimized_pose
    
    def _calculate_pose_score(self, pose: Dict[str, List[float]]) -> float:
        """Calculate a visibility score for the pose"""
        arm_pose = pose.get("mixamorig:RightArm", [0, 0, 0])
        shoulder_pose = pose.get("mixamorig:RightShoulder", [0, 0, 0])
        
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
    
    def save_optimized_pose(self, letter: str, optimized_pose: Dict[str, List[float]], sign_type: str = "alphabet"):
        """Save the optimized pose back to the JSON file"""
        data_path = f"resources/data/signs/asl/asl_right_hand.json"
        
        try:
            # Load current data
            with open(data_path, 'r') as f:
                data = json.load(f)
            
            # Update the pose
            if sign_type in data and letter in data[sign_type]:
                data[sign_type][letter]["pose"] = optimized_pose
                
                # Save back to file
                with open(data_path, 'w') as f:
                    json.dump(data, f, indent=2)
                
                print(f"\nOptimized pose saved for {letter}")
            else:
                print(f"Could not find {letter} in {sign_type} data")
                
        except Exception as e:
            print(f"Error saving optimized pose: {e}")


def main():
    """Main function to demonstrate pose optimization"""
    if len(sys.argv) < 2:
        print("Usage: python optimize_pose.py <letter>")
        print("Example: python optimize_pose.py A")
        return
    
    letter = sys.argv[1].upper()
    
    optimizer = PoseOptimizer()
    
    # Optimize the pose
    optimized_pose = optimizer.optimize_pose(letter)
    
    if optimized_pose:
        # Save the optimized pose
        optimizer.save_optimized_pose(letter, optimized_pose)
        
        print(f"\n=== Optimization Complete ===")
        print(f"ASL {letter} pose has been optimized and saved!")
        print(f"Key changes:")
        print(f"  Shoulder: {optimized_pose.get('mixamorig:RightShoulder', 'N/A')}")
        print(f"  Arm: {optimized_pose.get('mixamorig:RightArm', 'N/A')}")
    else:
        print(f"Could not optimize pose for {letter}")


if __name__ == "__main__":
    main()
