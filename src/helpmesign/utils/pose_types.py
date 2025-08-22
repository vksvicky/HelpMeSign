"""
Pose types shared across the sign language pipeline
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class PoseFrame:
    """Single frame in pose sequence"""

    frame_number: int
    pose: Dict[str, List[float]]  # joint_name -> [h, p, r]
    timestamp_ms: int


@dataclass
class PoseSequence:
    """Complete pose sequence for 3D animation"""

    frames: List[PoseFrame]
    total_duration_ms: int
    fps: int = 30


@dataclass
class GlossItem:
    """Represents a word-gloss pair"""

    word: Optional[str]
    gloss: str


@dataclass
class Gloss:
    """Represents a sequence of gloss items"""

    items: List[GlossItem]
