#!/usr/bin/env python3
"""
Test script for Sign.mt compatible pipeline
"""

from helpmesign.utils.sign_mt_pipeline import SignMTPipeline


def test_sign_mt_pipeline():
    """Test the Sign.mt pipeline"""

    print("🧪 Testing Sign.mt Compatible Pipeline")
    print("=" * 50)

    # Initialize pipeline
    pipeline = SignMTPipeline()

    # Test text to pose sequence
    test_text = "WELCOME TO HELPMESIGN"
    print(f"📝 Input text: '{test_text}'")

    try:
        pose_sequence = pipeline.text_to_pose_sequence(test_text)

        print(f"✅ Generated pose sequence:")
        print(f"   Total frames: {len(pose_sequence.frames)}")
        print(f"   Duration: {pose_sequence.total_duration_ms}ms")
        print(f"   FPS: {pose_sequence.fps}")

        # Show first few frames
        print(f"\n🎬 First 3 frames:")
        for i, frame in enumerate(pose_sequence.frames[:3]):
            print(f"   Frame {frame.frame_number}: {frame.timestamp_ms}ms")
            print(f"     Joints: {len(frame.pose)} joints")

            # Show some key joints
            key_joints = [
                "mixamorig:RightArm",
                "mixamorig:LeftArm",
                "mixamorig:RightHandIndex1",
            ]
            for joint in key_joints:
                if joint in frame.pose:
                    hpr = frame.pose[joint]
                    print(
                        f"     {joint}: H={hpr[0]:.1f}, P={hpr[1]:.1f}, R={hpr[2]:.1f}"
                    )

        # Test neutral pose
        neutral_pose = pipeline.get_neutral_pose()
        print(f"\n🔄 Neutral pose:")
        print(f"   Joints: {len(neutral_pose)} joints")

        # Test individual words
        print(f"\n🔤 Testing individual words:")
        test_words = ["WELCOME", "TO", "HELP", "ME", "SIGN"]

        for word in test_words:
            word_sequence = pipeline.text_to_pose_sequence(word)
            print(
                f"   '{word}': {len(word_sequence.frames)} frames, {word_sequence.total_duration_ms}ms"
            )

        print(f"\n✅ Sign.mt pipeline test completed successfully!")

    except Exception as e:
        print(f"❌ Error testing pipeline: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_sign_mt_pipeline()
