#!/usr/bin/env python3
"""
Unit test to see what pose data the pipeline is generating
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from helpmesign.utils.sign_mt_pipeline import SignMTPipeline


def main():
    # Create pipeline
    pipeline = SignMTPipeline("ASL")

    # Test with "Welcome"
    text = "Welcome"
    print(f"Testing with text: '{text}'")

    # Generate pose sequence
    pose_sequence = pipeline.text_to_pose_sequence(text)

    print(f"Generated pose sequence: {len(pose_sequence.frames)} frames")
    print(f"Total duration: {pose_sequence.total_duration_ms}ms")
    print(f"FPS: {pose_sequence.fps}")

    # Show first frame pose data
    if pose_sequence.frames:
        first_frame = pose_sequence.frames[0]
        print(f"\nFirst frame pose data:")
        print(f"Frame number: {first_frame.frame_number}")
        print(f"Timestamp: {first_frame.timestamp_ms}ms")
        print(f"Pose joints: {list(first_frame.pose.keys())}")

        # Show some joint values
        for joint_name, hpr in first_frame.pose.items():
            print(f"  {joint_name}: {hpr}")

    # Show last frame pose data
    if len(pose_sequence.frames) > 1:
        last_frame = pose_sequence.frames[-1]
        print(f"\nLast frame pose data:")
        print(f"Frame number: {last_frame.frame_number}")
        print(f"Timestamp: {last_frame.timestamp_ms}ms")
        print(f"Pose joints: {list(last_frame.pose.keys())}")


if __name__ == "__main__":
    main()
