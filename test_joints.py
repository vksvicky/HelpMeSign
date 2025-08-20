#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from helpmesign.utils.signwriting_pipeline import SignWritingPipeline

def test_joint_names():
    """Test the joint name conversion"""
    pipeline = SignWritingPipeline()
    
    # Test the conversion
    test_joints = [
        "index_01", "index_02", "index_03",
        "middle_01", "middle_02", "middle_03",
        "ring_01", "ring_02", "ring_03",
        "pinky_01", "pinky_02", "pinky_03",
        "thumb_01", "thumb_02", "thumb_03"
    ]
    
    print("Testing joint name conversion:")
    for joint in test_joints:
        converted = pipeline._convert_to_mixamo_joint(joint)
        print(f"  {joint} -> {converted}")
    
    # Test pose generation
    print("\nTesting pose generation:")
    from helpmesign.utils.signwriting_pipeline import SignWritingSymbol, HandSide
    pose = pipeline._get_pose_for_symbol(
        SignWritingSymbol(
            symbol="S10000",
            hand_side=HandSide.BOTH,
            position=(0, 0),
            rotation=0.0,
            size=1.0
        )
    )
    
    print("Generated pose keys:")
    for joint in sorted(pose.keys()):
        print(f"  {joint}: {pose[joint]}")

if __name__ == "__main__":
    test_joint_names()
