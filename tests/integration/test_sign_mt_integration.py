#!/usr/bin/env python3
"""
Integration test for sign.mt integration

This tests the proper sign.mt architecture implementation
"""

import asyncio
import logging
import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from helpmesign.utils.sign_mt_real.complete_pipeline import CompleteSignMTPipeline
from helpmesign.utils.sign_mt_real.model_downloader import ModelDownloader


@pytest.mark.asyncio
async def test_sign_mt_integration():
    """Test the complete sign.mt integration"""

    print("🧪 Testing sign.mt Integration")
    print("=" * 50)

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Test 1: Model Downloader
    print("\n📥 Testing Model Downloader...")
    downloader = ModelDownloader()

    # Check current status
    verification = await downloader.verify_models()
    print(f"Current model status: {verification}")

    # Test 2: Complete Pipeline
    print("\n🔄 Testing Complete Pipeline...")
    pipeline = CompleteSignMTPipeline("ASL")

    # Test translation
    test_text = "Welcome"
    print(f"Testing translation: '{test_text}'")

    try:
        pose_sequence = await pipeline.text_to_pose_sequence(test_text)

        if pose_sequence and pose_sequence.frames:
            print(f"✅ Translation successful!")
            print(f"   Generated {len(pose_sequence.frames)} frames")
            print(f"   Total duration: {pose_sequence.total_duration_ms}ms")
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
                    "mixamorig:RightHand",
                    "mixamorig:LeftHand",
                ]

                for joint in key_joints:
                    if joint in frame.pose:
                        hpr = frame.pose[joint]
                        print(
                            f"     {joint}: H={hpr[0]:.1f}, P={hpr[1]:.1f}, R={hpr[2]:.1f}"
                        )
        else:
            print("❌ Translation failed - no pose sequence generated")

    except Exception as e:
        print(f"❌ Translation error: {e}")

    # Test 3: Multiple languages
    print("\n🌍 Testing Multiple Languages...")
    languages = ["ASL", "BSL"]

    for lang in languages:
        print(f"Testing {lang}...")
        try:
            pipeline.set_language(lang)
            pose_sequence = await pipeline.text_to_pose_sequence("Hello")

            if pose_sequence and pose_sequence.frames:
                print(f"   ✅ {lang}: {len(pose_sequence.frames)} frames")
            else:
                print(f"   ❌ {lang}: No frames generated")

        except Exception as e:
            print(f"   ❌ {lang}: Error - {e}")

    print("\n🎉 sign.mt Integration Test Complete!")


if __name__ == "__main__":
    asyncio.run(test_sign_mt_integration())
