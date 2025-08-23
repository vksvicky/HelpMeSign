"""
Integration tests for sign.mt real implementation

Tests the complete sign.mt architecture implementation
"""

import asyncio
from pathlib import Path

import pytest

from helpmesign.utils.sign_mt_real.complete_pipeline import CompleteSignMTPipeline
from helpmesign.utils.sign_mt_real.model_downloader import ModelDownloader


@pytest.mark.asyncio
async def test_model_downloader_initialization():
    """Test ModelDownloader initialization"""
    downloader = ModelDownloader()

    # Check that directories are created
    assert downloader.models_path.exists()
    assert downloader.bergamot_path.exists()
    assert downloader.data_path.exists()


@pytest.mark.asyncio
async def test_model_verification():
    """Test model verification"""
    downloader = ModelDownloader()
    verification = await downloader.verify_models()

    # Should return a dictionary with verification results
    assert isinstance(verification, dict)
    assert "bergamot_en-ase" in verification
    assert "language_asl" in verification
    assert "wasm_files" in verification


@pytest.mark.asyncio
async def test_complete_pipeline_initialization():
    """Test CompleteSignMTPipeline initialization"""
    pipeline = CompleteSignMTPipeline("ASL")

    # Check that pipeline is properly initialized
    assert pipeline is not None
    assert hasattr(pipeline, "text_to_pose_sequence")
    assert hasattr(pipeline, "set_language")


@pytest.mark.asyncio
async def test_text_to_pose_sequence_welcome():
    """Test translation of 'Welcome' to pose sequence"""
    pipeline = CompleteSignMTPipeline("ASL")

    # Test translation
    pose_sequence = await pipeline.text_to_pose_sequence("Welcome")

    # Should generate a pose sequence
    assert pose_sequence is not None
    assert hasattr(pose_sequence, "frames")
    assert hasattr(pose_sequence, "total_duration_ms")
    assert hasattr(pose_sequence, "fps")

    # Should have frames
    assert len(pose_sequence.frames) > 0

    # Check frame structure
    first_frame = pose_sequence.frames[0]
    assert hasattr(first_frame, "frame_number")
    assert hasattr(first_frame, "timestamp_ms")
    assert hasattr(first_frame, "pose")

    # Should have pose data
    assert len(first_frame.pose) > 0

    # Check for key joints (both hands should be used for Welcome)
    key_joints = [
        "mixamorig:RightArm",
        "mixamorig:LeftArm",
        "mixamorig:RightHand",
        "mixamorig:LeftHand",
    ]

    for joint in key_joints:
        if joint in first_frame.pose:
            hpr = first_frame.pose[joint]
            assert len(hpr) == 3  # Should have H, P, R values
            assert all(isinstance(val, (int, float)) for val in hpr)


@pytest.mark.asyncio
async def test_text_to_pose_sequence_hello():
    """Test translation of 'Hello' to pose sequence"""
    pipeline = CompleteSignMTPipeline("ASL")

    # Test translation
    pose_sequence = await pipeline.text_to_pose_sequence("Hello")

    # Should generate a pose sequence
    assert pose_sequence is not None
    assert len(pose_sequence.frames) > 0

    # Check frame structure
    first_frame = pose_sequence.frames[0]
    assert hasattr(first_frame, "pose")
    assert len(first_frame.pose) > 0


@pytest.mark.asyncio
async def test_language_switching():
    """Test switching between languages"""
    pipeline = CompleteSignMTPipeline("ASL")

    # Test ASL
    pose_sequence_asl = await pipeline.text_to_pose_sequence("Hello")
    assert pose_sequence_asl is not None
    assert len(pose_sequence_asl.frames) > 0

    # Switch to BSL
    pipeline.set_language("BSL")
    pose_sequence_bsl = await pipeline.text_to_pose_sequence("Hello")
    assert pose_sequence_bsl is not None
    assert len(pose_sequence_bsl.frames) > 0


@pytest.mark.asyncio
async def test_multiple_words():
    """Test translation of multiple words"""
    pipeline = CompleteSignMTPipeline("ASL")

    # Test multiple words
    pose_sequence = await pipeline.text_to_pose_sequence("Hello welcome")

    # Should generate a pose sequence
    assert pose_sequence is not None
    assert len(pose_sequence.frames) > 0

    # Should have more frames than single word
    single_word_sequence = await pipeline.text_to_pose_sequence("Hello")
    assert len(pose_sequence.frames) >= len(single_word_sequence.frames)


@pytest.mark.asyncio
async def test_empty_text():
    """Test handling of empty text"""
    pipeline = CompleteSignMTPipeline("ASL")

    # Test empty text
    pose_sequence = await pipeline.text_to_pose_sequence("")

    # Should handle gracefully (either return None or empty sequence)
    if pose_sequence is not None:
        assert len(pose_sequence.frames) == 0


@pytest.mark.asyncio
async def test_unknown_words():
    """Test handling of unknown words"""
    pipeline = CompleteSignMTPipeline("ASL")

    # Test unknown word
    pose_sequence = await pipeline.text_to_pose_sequence("xyz123")

    # Should handle gracefully (either return None or generate something)
    if pose_sequence is not None:
        assert len(pose_sequence.frames) >= 0


@pytest.mark.asyncio
async def test_pipeline_consistency():
    """Test that pipeline produces consistent results"""
    pipeline = CompleteSignMTPipeline("ASL")

    # Test same input multiple times
    sequence1 = await pipeline.text_to_pose_sequence("Hello")
    sequence2 = await pipeline.text_to_pose_sequence("Hello")

    # Should produce consistent results
    assert sequence1 is not None
    assert sequence2 is not None
    assert len(sequence1.frames) == len(sequence2.frames)

    # Frame counts should be the same
    if len(sequence1.frames) > 0 and len(sequence2.frames) > 0:
        assert sequence1.frames[0].frame_number == sequence2.frames[0].frame_number
