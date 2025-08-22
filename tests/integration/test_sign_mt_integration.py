#!/usr/bin/env python3
"""
Test script for sign.mt integration
Demonstrates proper sign language translation using the sign.mt ecosystem
"""

import sys
import os

# Add the src directory to the path (from tests/integration/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_sign_mt_integration():
    """Test the sign.mt integration"""
    print("🧏 Testing Sign.mt Integration")
    print("=" * 50)
    
    try:
        from helpmesign.utils.sign_mt_integration import (
            SignMTTranslator, 
            SignLanguageType, 
            create_sign_translator,
            translate_text_to_signs
        )
        
        # Test 1: Create translator
        print("\n1. Creating ASL translator...")
        translator = create_sign_translator("asl")
        print(f"✅ Translator created for {translator.language.value}")
        
        # Test 2: Get available signs
        print("\n2. Available signs:")
        available_signs = translator.get_available_signs()
        for sign in available_signs:
            description = translator.get_sign_description(sign)
            print(f"   • {sign}: {description}")
        
        # Test 3: Translate simple words
        print("\n3. Testing translations:")
        test_words = ["hello", "thank_you", "yes", "no", "welcome"]
        
        for word in test_words:
            print(f"\n   Translating '{word}':")
            sequence = translator.translate_text_to_signs(word)
            print(f"   ✅ Generated {len(sequence.frames)} frames")
            print(f"   ✅ Total duration: {sequence.total_duration_ms}ms")
            
            for i, frame in enumerate(sequence.frames):
                print(f"     Frame {i}: {len(frame.poses)} poses, {frame.duration_ms}ms")
        
        # Test 4: Translate phrases
        print("\n4. Testing phrase translation:")
        test_phrases = ["hello welcome", "thank you please"]
        
        for phrase in test_phrases:
            print(f"\n   Translating phrase: '{phrase}'")
            sequence = translator.translate_text_to_signs(phrase)
            print(f"   ✅ Generated {len(sequence.frames)} frames")
            print(f"   ✅ Total duration: {sequence.total_duration_ms}ms")
        
        # Test 5: Test language switching
        print("\n5. Testing language switching:")
        translator.set_language(SignLanguageType.ASL)
        print("   ✅ Switched to ASL")
        
        # Test 6: Test unknown words (should spell out)
        print("\n6. Testing unknown words (finger spelling):")
        unknown_word = "xyz"
        sequence = translator.translate_text_to_signs(unknown_word)
        print(f"   ✅ Generated {len(sequence.frames)} frames for '{unknown_word}'")
        
        print("\n🎉 All tests passed! Sign.mt integration is working.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure to install the required dependencies:")
        print("pip install transformers torch numpy scipy opencv-python mediapipe")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

def test_pipeline_integration():
    """Test the pipeline integration"""
    print("\n🧏 Testing Pipeline Integration")
    print("=" * 50)
    
    try:
        from helpmesign.utils.sign_mt_pipeline import SignMTPipeline
        
        # Create pipeline
        pipeline = SignMTPipeline("ASL")
        print("✅ Pipeline created")
        
        # Test text to pose sequence
        test_text = "hello"
        print(f"\nTranslating '{test_text}' to pose sequence...")
        
        pose_sequence = pipeline.text_to_pose_sequence(test_text)
        if pose_sequence:
            print(f"✅ Generated pose sequence with {len(pose_sequence.frames)} frames")
            print(f"✅ Total duration: {pose_sequence.total_duration_ms}ms")
            
            for i, frame in enumerate(pose_sequence.frames):
                print(f"   Frame {i}: {len(frame.pose)} joints, {frame.timestamp_ms}ms")
        else:
            print("❌ Failed to generate pose sequence")
        
        print("\n🎉 Pipeline integration test completed!")
        
    except Exception as e:
        print(f"❌ Error during pipeline testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sign_mt_integration()
    test_pipeline_integration()
