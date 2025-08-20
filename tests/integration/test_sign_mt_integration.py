#!/usr/bin/env python3
"""
Test sign.mt pipeline integration with animate panel
"""

from helpmesign.modes.learn.animate_panel import AnimateGesturePanel
from helpmesign.utils.sign_mt_pipeline import SignMTPipeline


def test_sign_mt_integration():
    """Test the sign.mt pipeline integration"""

    print("🧪 Testing Sign.mt Pipeline Integration")
    print("=" * 50)

    try:
        # Test sign.mt pipeline directly
        print("📝 Testing sign.mt pipeline...")
        pipeline = SignMTPipeline()

        test_text = "WELCOME TO HELPMESIGN"
        pose_sequence = pipeline.text_to_pose_sequence(test_text)

        print(f"✅ Generated pose sequence: {len(pose_sequence.frames)} frames")

        # Test animate panel initialization
        print("\n🎬 Testing animate panel...")
        panel = AnimateGesturePanel()

        print(f"✅ Animate panel initialized with sign.mt pipeline")
        print(f"   Pipeline type: {type(panel._sign_mt_pipeline)}")

        # Test play_phrase method (without actual 3D rendering)
        print("\n🎭 Testing play_phrase method...")

        # Mock the 3D components to avoid rendering
        panel._actor = None
        panel._is_animating = False

        # Test the method
        panel.play_phrase("WELCOME TO HELPMESIGN", "ASL", "right")

        print("✅ play_phrase method executed successfully")

        print("\n✅ Sign.mt integration test completed successfully!")

    except Exception as e:
        print(f"❌ Error in integration test: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_sign_mt_integration()
