"""
Asset Manager - Following sign.mt patterns

This manages model assets and file loading following their AssetService
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


class AssetManager:
    """
    Asset Manager following sign.mt patterns

    From their AssetsService - manages model files and directories
    """

    def __init__(self, base_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.base_path = (
            Path(base_path)
            if base_path
            else Path(__file__).parent.parent.parent.parent.parent / "resources"
        )

        # Create directories if they don't exist
        self.models_path = self.base_path / "models"
        self.models_path.mkdir(parents=True, exist_ok=True)

        self.bergamot_path = self.models_path / "bergamot"
        self.bergamot_path.mkdir(parents=True, exist_ok=True)

        self.lexicon_path = self.base_path / "lexicons"
        self.lexicon_path.mkdir(parents=True, exist_ok=True)

    def get_directory(self, path: str) -> Dict[str, str]:
        """
        Get directory contents following sign.mt patterns

        From their AssetsService.getDirectory method
        """
        try:
            full_path = self.base_path / path
            if not full_path.exists():
                return {}

            files = {}
            for file_path in full_path.rglob("*"):
                if file_path.is_file():
                    # Get relative path from base
                    relative_path = file_path.relative_to(self.base_path)
                    files[file_path.name] = str(relative_path)

            return files

        except Exception as e:
            self.logger.error(f"Error getting directory {path}: {e}")
            return {}

    def stat(self, path: str) -> Dict[str, Any]:
        """
        Get file/directory stats following sign.mt patterns

        From their AssetsService.stat method
        """
        try:
            full_path = self.base_path / path
            if not full_path.exists():
                return {"exists": False}

            stat_info = full_path.stat()
            return {
                "exists": True,
                "isFile": full_path.is_file(),
                "isDirectory": full_path.is_dir(),
                "size": stat_info.st_size,
                "modified": stat_info.st_mtime,
            }

        except Exception as e:
            self.logger.error(f"Error getting stats for {path}: {e}")
            return {"exists": False}

    def read_file(self, path: str) -> Optional[str]:
        """
        Read file contents following sign.mt patterns
        """
        try:
            full_path = self.base_path / path
            if not full_path.exists():
                return None

            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()

        except Exception as e:
            self.logger.error(f"Error reading file {path}: {e}")
            return None

    def read_json(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Read JSON file following sign.mt patterns
        """
        try:
            content = self.read_file(path)
            if content:
                return json.loads(content)
            return None

        except Exception as e:
            self.logger.error(f"Error reading JSON file {path}: {e}")
            return None

    def write_file(self, path: str, content: str) -> bool:
        """
        Write file following sign.mt patterns
        """
        try:
            full_path = self.base_path / path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            return True

        except Exception as e:
            self.logger.error(f"Error writing file {path}: {e}")
            return False

    def write_json(self, path: str, data: Dict[str, Any]) -> bool:
        """
        Write JSON file following sign.mt patterns
        """
        try:
            content = json.dumps(data, indent=2, ensure_ascii=False)
            return self.write_file(path, content)

        except Exception as e:
            self.logger.error(f"Error writing JSON file {path}: {e}")
            return False

    def get_model_path(self, direction: str, from_lang: str, to_lang: str) -> str:
        """
        Get model path following sign.mt patterns

        From their model path structure: models/browsermt/{direction}/{from}-{to}/
        """
        return f"models/bergamot/{direction}/{from_lang}-{to_lang}"

    def get_lexicon_path(self, language: str) -> str:
        """
        Get lexicon path following sign.mt patterns
        """
        return f"lexicons/{language}"

    def download_model(self, direction: str, from_lang: str, to_lang: str) -> bool:
        """
        Create local bergamot model structure following sign.mt patterns

        This creates local model files instead of downloading from external URLs
        """
        try:
            model_path = self.get_model_path(direction, from_lang, to_lang)
            full_path = self.base_path / model_path

            if full_path.exists():
                self.logger.info(f"Model already exists: {model_path}")
                return True

            # Create directory structure
            full_path.mkdir(parents=True, exist_ok=True)

            # Create local model files based on sign.mt patterns
            success = self._create_local_model_files(
                full_path, direction, from_lang, to_lang
            )

            if success:
                self.logger.info(f"Successfully created local model: {model_path}")
                return True
            else:
                self.logger.error(f"Failed to create local model: {model_path}")
                return False

        except Exception as e:
            self.logger.error(
                f"Error creating model {direction}/{from_lang}-{to_lang}: {e}"
            )
            return False

    def _create_local_model_files(
        self, model_path: Path, direction: str, from_lang: str, to_lang: str
    ) -> bool:
        """
        Create local model files following sign.mt patterns

        Based on their actual model structure but created locally
        """
        try:
            import json

            # Create model files based on sign.mt patterns
            model_files = {
                "model.bin": self._create_model_binary(),
                "vocab.json": self._create_vocab_json(from_lang, to_lang),
                "config.json": self._create_config_json(direction, from_lang, to_lang),
                "lexicon.json": self._create_lexicon_json(from_lang, to_lang),
                "pose_mappings.json": self._create_pose_mappings_json(
                    from_lang, to_lang
                ),
            }

            # Write files
            for filename, content in model_files.items():
                file_path = model_path / filename
                if isinstance(content, str):
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                else:
                    with open(file_path, "wb") as f:
                        if isinstance(content, str):
                            f.write(content.encode())
                        elif isinstance(content, bytes):
                            f.write(content)
                        else:
                            f.write(str(content).encode())

            return True

        except Exception as e:
            self.logger.error(f"Error creating local model files: {e}")
            return False

    def _create_model_binary(self) -> bytes:
        """
        Create placeholder model binary following sign.mt patterns
        """
        # This would be the actual bergamot model binary
        # For now, create a placeholder that follows their structure
        return b"bergamot_model_placeholder_binary_data"

    def _create_vocab_json(self, from_lang: str, to_lang: str) -> str:
        """
        Create vocabulary JSON following sign.mt patterns
        """
        vocab_data = {
            "vocab": {
                # Common words in sign language
                "hello": 1,
                "goodbye": 2,
                "thank": 3,
                "you": 4,
                "welcome": 5,
                "yes": 6,
                "no": 7,
                "please": 8,
                "sorry": 9,
                "help": 10,
                "understand": 11,
                "learn": 12,
                "sign": 13,
                "language": 14,
                "deaf": 15,
                "hearing": 16,
                "family": 17,
                "friend": 18,
                "work": 19,
                "school": 20,
                "home": 21,
                "food": 22,
                "water": 23,
                "time": 24,
                "day": 25,
                "night": 26,
                "good": 27,
                "bad": 28,
                "big": 29,
                "small": 30,
                "fast": 31,
                "slow": 32,
                "hot": 33,
                "cold": 34,
                "happy": 35,
                "sad": 36,
                "angry": 37,
                "love": 38,
                "hate": 39,
                "want": 40,
                "need": 41,
                "can": 42,
                "will": 43,
                "do": 44,
                "go": 45,
                "come": 46,
                "see": 47,
                "hear": 48,
                "speak": 49,
                "read": 50,
                "write": 51,
            },
            "source_language": from_lang,
            "target_language": to_lang,
            "vocab_size": 1000,
        }

        return json.dumps(vocab_data, indent=2, ensure_ascii=False)

    def _create_config_json(self, direction: str, from_lang: str, to_lang: str) -> str:
        """
        Create config JSON following sign.mt patterns
        """
        config_data = {
            "model_type": "bergamot",
            "direction": direction,
            "source_language": from_lang,
            "target_language": to_lang,
            "vocab_size": 1000,
            "embedding_dim": 512,
            "hidden_dim": 1024,
            "num_layers": 6,
            "num_heads": 8,
            "dropout": 0.1,
            "max_length": 512,
            "beam_size": 5,
            "length_penalty": 1.0,
        }

        return json.dumps(config_data, indent=2, ensure_ascii=False)

    def _create_lexicon_json(self, from_lang: str, to_lang: str) -> str:
        """
        Create lexicon JSON following sign.mt patterns
        """
        lexicon_data = {
            "lexicon": {
                "hello": {
                    "signwriting": "S5000",
                    "gloss": "HELLO",
                    "confidence": 0.95,
                    "frequency": 100,
                },
                "goodbye": {
                    "signwriting": "S7000",
                    "gloss": "GOODBYE",
                    "confidence": 0.92,
                    "frequency": 85,
                },
                "thank": {
                    "signwriting": "S6000",
                    "gloss": "THANK",
                    "confidence": 0.88,
                    "frequency": 90,
                },
                "you": {
                    "signwriting": "S3000",
                    "gloss": "YOU",
                    "confidence": 0.85,
                    "frequency": 95,
                },
                "welcome": {
                    "signwriting": "S8000",
                    "gloss": "WELCOME",
                    "confidence": 0.90,
                    "frequency": 70,
                },
                "yes": {
                    "signwriting": "S4000",
                    "gloss": "YES",
                    "confidence": 0.87,
                    "frequency": 80,
                },
                "no": {
                    "signwriting": "S2000",
                    "gloss": "NO",
                    "confidence": 0.89,
                    "frequency": 75,
                },
                "please": {
                    "signwriting": "S9000",
                    "gloss": "PLEASE",
                    "confidence": 0.86,
                    "frequency": 65,
                },
                "sorry": {
                    "signwriting": "S10000",
                    "gloss": "SORRY",
                    "confidence": 0.84,
                    "frequency": 60,
                },
                "help": {
                    "signwriting": "S11000",
                    "gloss": "HELP",
                    "confidence": 0.83,
                    "frequency": 55,
                },
            },
            "metadata": {
                "source_language": from_lang,
                "target_language": to_lang,
                "total_entries": 10,
                "version": "1.0.0",
                "created": "2024-01-01",
            },
        }

        return json.dumps(lexicon_data, indent=2, ensure_ascii=False)

    def _create_pose_mappings_json(self, from_lang: str, to_lang: str) -> str:
        """
        Create pose mappings JSON following sign.mt patterns
        """
        pose_mappings = {
            "S5000": {
                "joints": {
                    "mixamorig:RightArm": [0, -15, 0],
                    "mixamorig:RightForeArm": [0, 45, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                    "mixamorig:RightHandIndex1": [0, -60, 0],
                    "mixamorig:RightHandIndex2": [0, -60, 0],
                    "mixamorig:RightHandIndex3": [0, -60, 0],
                    "mixamorig:RightHandMiddle1": [0, -60, 0],
                    "mixamorig:RightHandMiddle2": [0, -60, 0],
                    "mixamorig:RightHandMiddle3": [0, -60, 0],
                    "mixamorig:RightHandRing1": [0, -60, 0],
                    "mixamorig:RightHandRing2": [0, -60, 0],
                    "mixamorig:RightHandRing3": [0, -60, 0],
                    "mixamorig:RightHandPinky1": [0, -60, 0],
                    "mixamorig:RightHandPinky2": [0, -60, 0],
                    "mixamorig:RightHandPinky3": [0, -60, 0],
                },
                "duration_ms": 1500,  # Longer duration for better visibility
                "metadata": {
                    "sign_type": "greeting",
                    "hand_shape": "open",
                    "movement": "static",
                },
            },
            "S7000": {
                "joints": {
                    # ASL Welcome Sign: Both hands open, palms up, moving in circular motion
                    "mixamorig:RightArm": [0, 60, 0],
                    "mixamorig:LeftArm": [0, 60, 0],
                    "mixamorig:RightForeArm": [0, 30, 0],
                    "mixamorig:LeftForeArm": [0, 30, 0],
                    "mixamorig:RightHand": [0, 0, 90],  # Palm facing up
                    "mixamorig:LeftHand": [0, 0, 90],  # Palm facing up
                    # Right hand fingers - natural open position
                    "mixamorig:RightHandIndex1": [0, 0, 0],
                    "mixamorig:RightHandIndex2": [0, 0, 0],
                    "mixamorig:RightHandIndex3": [0, 0, 0],
                    "mixamorig:RightHandMiddle1": [0, 0, 0],
                    "mixamorig:RightHandMiddle2": [0, 0, 0],
                    "mixamorig:RightHandMiddle3": [0, 0, 0],
                    "mixamorig:RightHandRing1": [0, 0, 0],
                    "mixamorig:RightHandRing2": [0, 0, 0],
                    "mixamorig:RightHandRing3": [0, 0, 0],
                    "mixamorig:RightHandPinky1": [0, 0, 0],
                    "mixamorig:RightHandPinky2": [0, 0, 0],
                    "mixamorig:RightHandPinky3": [0, 0, 0],
                    # Left hand fingers - natural open position
                    "mixamorig:LeftHandIndex1": [0, 0, 0],
                    "mixamorig:LeftHandIndex2": [0, 0, 0],
                    "mixamorig:LeftHandIndex3": [0, 0, 0],
                    "mixamorig:LeftHandMiddle1": [0, 0, 0],
                    "mixamorig:LeftHandMiddle2": [0, 0, 0],
                    "mixamorig:LeftHandMiddle3": [0, 0, 0],
                    "mixamorig:LeftHandRing1": [0, 0, 0],
                    "mixamorig:LeftHandRing2": [0, 0, 0],
                    "mixamorig:LeftHandRing3": [0, 0, 0],
                    "mixamorig:LeftHandPinky1": [0, 0, 0],
                    "mixamorig:LeftHandPinky2": [0, 0, 0],
                    "mixamorig:LeftHandPinky3": [0, 0, 0],
                },
                "duration_ms": 2000,  # Longer duration for welcome sign
                "metadata": {
                    "sign_type": "welcome",
                    "hand_shape": "open_both_hands_palms_up",
                    "movement": "welcome_gesture",
                },
            },
            "S6000": {
                "joints": {
                    "mixamorig:RightArm": [0, 75, 0],
                    "mixamorig:RightForeArm": [0, 30, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                    "mixamorig:RightHandIndex1": [0, -45, 0],
                    "mixamorig:RightHandIndex2": [0, -45, 0],
                    "mixamorig:RightHandIndex3": [0, -45, 0],
                    "mixamorig:RightHandMiddle1": [0, -45, 0],
                    "mixamorig:RightHandMiddle2": [0, -45, 0],
                    "mixamorig:RightHandMiddle3": [0, -45, 0],
                    "mixamorig:RightHandRing1": [0, -45, 0],
                    "mixamorig:RightHandRing2": [0, -45, 0],
                    "mixamorig:RightHandRing3": [0, -45, 0],
                    "mixamorig:RightHandPinky1": [0, -45, 0],
                    "mixamorig:RightHandPinky2": [0, -45, 0],
                    "mixamorig:RightHandPinky3": [0, -45, 0],
                },
                "duration_ms": 600,
                "metadata": {
                    "sign_type": "gratitude",
                    "hand_shape": "neutral",
                    "movement": "forward",
                },
            },
            "S2000": {
                "joints": {
                    # ASL Welcome Sign Movement: Hands move outward in welcoming gesture
                    "mixamorig:RightArm": [0, 75, 0],
                    "mixamorig:LeftArm": [0, 75, 0],
                    "mixamorig:RightForeArm": [0, 45, 0],
                    "mixamorig:LeftForeArm": [0, 45, 0],
                    "mixamorig:RightHand": [0, 0, 90],  # Palm facing up
                    "mixamorig:LeftHand": [0, 0, 90],  # Palm facing up
                    # Right hand fingers - natural open position
                    "mixamorig:RightHandIndex1": [0, 0, 0],
                    "mixamorig:RightHandIndex2": [0, 0, 0],
                    "mixamorig:RightHandIndex3": [0, 0, 0],
                    "mixamorig:RightHandMiddle1": [0, 0, 0],
                    "mixamorig:RightHandMiddle2": [0, 0, 0],
                    "mixamorig:RightHandMiddle3": [0, 0, 0],
                    "mixamorig:RightHandRing1": [0, 0, 0],
                    "mixamorig:RightHandRing2": [0, 0, 0],
                    "mixamorig:RightHandRing3": [0, 0, 0],
                    "mixamorig:RightHandPinky1": [0, 0, 0],
                    "mixamorig:RightHandPinky2": [0, 0, 0],
                    "mixamorig:RightHandPinky3": [0, 0, 0],
                    # Left hand fingers - natural open position
                    "mixamorig:LeftHandIndex1": [0, 0, 0],
                    "mixamorig:LeftHandIndex2": [0, 0, 0],
                    "mixamorig:LeftHandIndex3": [0, 0, 0],
                    "mixamorig:LeftHandMiddle1": [0, 0, 0],
                    "mixamorig:LeftHandMiddle2": [0, 0, 0],
                    "mixamorig:LeftHandMiddle3": [0, 0, 0],
                    "mixamorig:LeftHandRing1": [0, 0, 0],
                    "mixamorig:LeftHandRing2": [0, 0, 0],
                    "mixamorig:LeftHandRing3": [0, 0, 0],
                    "mixamorig:LeftHandPinky1": [0, 0, 0],
                    "mixamorig:LeftHandPinky2": [0, 0, 0],
                    "mixamorig:LeftHandPinky3": [0, 0, 0],
                },
                "duration_ms": 1500,
                "metadata": {
                    "sign_type": "welcome_movement",
                    "hand_shape": "open_both_hands_palms_up",
                    "movement": "outward_welcoming_gesture",
                },
            },
            "S10000": {
                "joints": {
                    # Neutral pose - arms relaxed at sides
                    "mixamorig:RightArm": [0, 0, 0],
                    "mixamorig:LeftArm": [0, 0, 0],
                    "mixamorig:RightForeArm": [0, 0, 0],
                    "mixamorig:LeftForeArm": [0, 0, 0],
                    "mixamorig:RightHand": [0, 0, 0],
                    "mixamorig:LeftHand": [0, 0, 0],
                    # Right hand fingers - natural relaxed position
                    "mixamorig:RightHandIndex1": [0, 0, 0],
                    "mixamorig:RightHandIndex2": [0, 0, 0],
                    "mixamorig:RightHandIndex3": [0, 0, 0],
                    "mixamorig:RightHandMiddle1": [0, 0, 0],
                    "mixamorig:RightHandMiddle2": [0, 0, 0],
                    "mixamorig:RightHandMiddle3": [0, 0, 0],
                    "mixamorig:RightHandRing1": [0, 0, 0],
                    "mixamorig:RightHandRing2": [0, 0, 0],
                    "mixamorig:RightHandRing3": [0, 0, 0],
                    "mixamorig:RightHandPinky1": [0, 0, 0],
                    "mixamorig:RightHandPinky2": [0, 0, 0],
                    "mixamorig:RightHandPinky3": [0, 0, 0],
                    # Left hand fingers - natural relaxed position
                    "mixamorig:LeftHandIndex1": [0, 0, 0],
                    "mixamorig:LeftHandIndex2": [0, 0, 0],
                    "mixamorig:LeftHandIndex3": [0, 0, 0],
                    "mixamorig:LeftHandMiddle1": [0, 0, 0],
                    "mixamorig:LeftHandMiddle2": [0, 0, 0],
                    "mixamorig:LeftHandMiddle3": [0, 0, 0],
                    "mixamorig:LeftHandRing1": [0, 0, 0],
                    "mixamorig:LeftHandRing2": [0, 0, 0],
                    "mixamorig:LeftHandRing3": [0, 0, 0],
                    "mixamorig:LeftHandPinky1": [0, 0, 0],
                    "mixamorig:LeftHandPinky2": [0, 0, 0],
                    "mixamorig:LeftHandPinky3": [0, 0, 0],
                },
                "duration_ms": 1000,
                "metadata": {
                    "sign_type": "neutral",
                    "hand_shape": "relaxed_both_hands",
                    "movement": "return_to_neutral",
                },
            },
        }

        return json.dumps(pose_mappings, indent=2, ensure_ascii=False)

    def list_available_models(self) -> List[str]:
        """
        List available models following sign.mt patterns
        """
        try:
            models = []
            bergamot_path = self.base_path / "models" / "bergamot"

            if bergamot_path.exists():
                for direction_dir in bergamot_path.iterdir():
                    if direction_dir.is_dir():
                        for model_dir in direction_dir.iterdir():
                            if model_dir.is_dir():
                                models.append(
                                    str(model_dir.relative_to(self.base_path))
                                )

            return models

        except Exception as e:
            self.logger.error(f"Error listing models: {e}")
            return []
