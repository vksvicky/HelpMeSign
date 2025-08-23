#!/usr/bin/env python3
"""
Integration tests for the real sign.mt implementation
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from helpmesign.utils.sign_mt_real import (
    AssetManager,
    BergamotTranslator,
    ModelRegistry,
    PoseDataService,
    SignWritingService,
)
from helpmesign.utils.sign_mt_real.complete_pipeline import CompleteSignMTPipeline


def test_asset_manager():
    """Test Asset Manager"""
    print("Testing Asset Manager...")

    asset_manager = AssetManager()

    # Test directory operations
    files = asset_manager.get_directory("lexicons/ase")
    print(f"  Found {len(files)} files in lexicon directory")

    # Test file operations
    lexicon_data = asset_manager.read_json("lexicons/ase/lexicon.json")
    if lexicon_data:
        print(f"  Loaded lexicon with {len(lexicon_data.get('lexicon', {}))} entries")

    # Test model download
    success = asset_manager.download_model("spoken-to-signed", "en", "ase")
    print(f"  Model download: {'Success' if success else 'Failed'}")


def test_model_registry():
    """Test Model Registry"""
    print("\nTesting Model Registry...")

    asset_manager = AssetManager()
    model_registry = ModelRegistry(asset_manager)

    # Test model registry creation
    registry = model_registry.create_model_registry(
        "models/bergamot/spoken-to-signed/en-ase"
    )
    print(f"  Created registry with {len(registry)} files")

    # Test model loading
    success = model_registry.load_model("enase", registry)
    print(f"  Model loading: {'Success' if success else 'Failed'}")


def test_bergamot_translator():
    """Test Bergamot Translator"""
    print("\nTesting Bergamot Translator...")

    asset_manager = AssetManager()
    model_registry = ModelRegistry(asset_manager)
    translator = BergamotTranslator(asset_manager, model_registry)

    # Test online translation (fallback when models aren't available)
    signwriting = translator._simulate_online_translation("hello world", "en", "ase")
    print(f"  Generated SignWriting: {signwriting}")

    # Test post-processing
    processed = translator._post_process_signwriting(signwriting)
    print(f"  Post-processed: {processed}")

    # Test translation response structure
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        response = loop.run_until_complete(
            translator.translate_offline("spoken-to-signed", "hello", "en", "ase")
        )
        print(f"  Offline translation response: {response.text}")
    finally:
        loop.close()


def test_signwriting_service():
    """Test SignWriting Service"""
    print("\nTesting SignWriting Service...")

    asset_manager = AssetManager()
    model_registry = ModelRegistry(asset_manager)
    translator = BergamotTranslator(asset_manager, model_registry)
    service = SignWritingService(translator)

    # Test SignWriting parsing
    symbols = service.parse_signwriting("S5000 M1000")
    print(f"  Parsed {len(symbols)} symbols")
    for symbol in symbols:
        print(f"    {symbol['type']}: {symbol['value']}")

    # Test validation
    is_valid = service.validate_signwriting("S5000 M1000")
    print(f"  SignWriting validation: {'Valid' if is_valid else 'Invalid'}")


def test_pose_data_service():
    """Test Pose Data Service"""
    print("\nTesting Pose Data Service...")

    asset_manager = AssetManager()
    service = PoseDataService(asset_manager)

    # Test lexicon loading
    success = service.load_lexicon("ase")
    print(f"  Lexicon loading: {'Success' if success else 'Failed'}")

    # Test pose generation
    pose_data = service.get_pose_from_signwriting("S5000", "ase")
    if pose_data:
        print(f"  Generated pose with {len(pose_data.joints)} joints")
        print(f"  Duration: {pose_data.duration_ms}ms")

    # Test neutral pose
    neutral_pose = service.get_neutral_pose()
    print(f"  Neutral pose has {len(neutral_pose.joints)} joints")


def test_complete_pipeline():
    """Test Complete Pipeline"""
    print("\nTesting Complete Pipeline...")

    pipeline = CompleteSignMTPipeline("ASL")

    # Test language support
    print(f"  Supported languages: {list(pipeline.language_mappings.keys())}")

    # Test pose sequence generation
    import asyncio

    async def test_async():
        pose_sequence = await pipeline.text_to_pose_sequence("hello")
        print(f"  Generated pose sequence: {len(pose_sequence.frames)} frames")
        print(f"  Total duration: {pose_sequence.total_duration_ms}ms")

        if pose_sequence.frames:
            first_frame = pose_sequence.frames[0]
            print(f"  First frame has {len(first_frame.pose)} joints")

    # Run async test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(test_async())
    finally:
        loop.close()


def test_real_sign_language_data():
    """Test with real sign language data"""
    print("\nTesting Real Sign Language Data...")

    pipeline = CompleteSignMTPipeline("ASL")

    # Test with real ASL signs
    test_words = [
        "hello",
        "goodbye",
        "thank you",
        "welcome",
        "yes",
        "no",
        "please",
        "sorry",
    ]

    import asyncio

    async def test_signs():
        for word in test_words:
            pose_sequence = await pipeline.text_to_pose_sequence(word)
            print(
                f"  '{word}': {len(pose_sequence.frames)} frames, {pose_sequence.total_duration_ms}ms"
            )

    # Run async test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(test_signs())
    finally:
        loop.close()


if __name__ == "__main__":
    print("=== Complete Sign.mt Implementation Test ===\n")

    test_asset_manager()
    test_model_registry()
    test_bergamot_translator()
    test_signwriting_service()
    test_pose_data_service()
    test_complete_pipeline()
    test_real_sign_language_data()

    print("\n=== Test Complete ===")
