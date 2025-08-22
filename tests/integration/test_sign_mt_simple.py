#!/usr/bin/env python3
"""
Simple test for sign.mt integration
Tests the core functionality without full application dependencies
"""

import sys
import os
import json

# Add the src directory to the path (from tests/integration/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_sign_mt_core():
    """Test the core sign.mt integration functionality"""
    print("🧏 Testing Sign.mt Core Integration")
    print("=" * 50)
    
    try:
        # Test the sign.mt integration module directly
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'helpmesign', 'utils'))
        
        from sign_mt_integration import (
            SignMTTranslator, 
            SignLanguageType, 
            SignSequence,
            SignFrame,
            SignPose
        )
        
        print("✅ Successfully imported sign.mt integration modules")
        
        # Test 1: Create translator
        print("\n1. Creating ASL translator...")
        translator = SignMTTranslator(SignLanguageType.ASL)
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
        
        # Test 4: Test pose conversion
        print("\n4. Testing pose conversion:")
        test_pose = SignPose("mixamorig:RightArm", 0, 45, 0)
        pose_dict = test_pose.to_dict()
        print(f"   ✅ Pose converted: {pose_dict}")
        
        # Test 5: Test frame conversion
        print("\n5. Testing frame conversion:")
        frame = SignFrame(
            frame_number=0,
            timestamp_ms=0,
            duration_ms=500
        )
        frame.poses.append(test_pose)
        pose_dict = frame.to_pose_dict()
        print(f"   ✅ Frame converted: {pose_dict}")
        
        print("\n🎉 All core tests passed! Sign.mt integration is working.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure to install the required dependencies:")
        print("pip install transformers torch numpy scipy opencv-python mediapipe")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

def test_pose_mappings():
    """Test the pose mappings file"""
    print("\n🧏 Testing Pose Mappings")
    print("=" * 50)
    
    try:
        # Test the pose mappings file (from tests/integration/)
        mapping_file = os.path.join(os.path.dirname(__file__), '..', '..', 'resources/data/signs/asl/pose_mappings.json')
        
        if os.path.exists(mapping_file):
            with open(mapping_file, 'r') as f:
                mappings = json.load(f)
            
            print(f"✅ Loaded pose mappings with {len(mappings)} signs")
            
            for sign, data in mappings.items():
                description = data.get("description", "No description")
                frames = data.get("frames", [])
                print(f"   • {sign}: {description} ({len(frames)} frames)")
                
                for i, frame in enumerate(frames):
                    poses = frame.get("poses", [])
                    duration = frame.get("duration_ms", 0)
                    print(f"     Frame {i}: {len(poses)} poses, {duration}ms")
            
            print("\n✅ Pose mappings test passed!")
        else:
            print(f"❌ Pose mappings file not found: {mapping_file}")
            
    except Exception as e:
        print(f"❌ Error testing pose mappings: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sign_mt_core()
    test_pose_mappings()
