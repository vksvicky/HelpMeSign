"""
Model Downloader - Download and manage sign.mt models

This utility downloads and manages the actual sign.mt models and data
"""

import asyncio
import json
import logging
import os
import shutil
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


class ModelDownloader:
    """
    Download and manage sign.mt models and data
    """

    def __init__(self, base_path: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.base_path = (
            base_path or Path(__file__).parent.parent.parent.parent.parent / "resources"
        )

        # Create model directories
        self.models_path = self.base_path / "models"
        self.models_path.mkdir(parents=True, exist_ok=True)

        self.bergamot_path = self.models_path / "bergamot"
        self.bergamot_path.mkdir(parents=True, exist_ok=True)

        self.data_path = self.base_path / "data"
        self.data_path.mkdir(parents=True, exist_ok=True)

    async def download_sign_mt_models(self) -> bool:
        """
        Download all required sign.mt models
        """
        try:
            self.logger.info("Starting sign.mt model download")

            # Download Bergamot models
            if not await self._download_bergamot_models():
                return False

            # Download sign language data
            if not await self._download_sign_language_data():
                return False

            # Download WebAssembly files
            if not await self._download_wasm_files():
                return False

            self.logger.info("Successfully downloaded all sign.mt models")
            return True

        except Exception as e:
            self.logger.error(f"Error downloading sign.mt models: {e}")
            return False

    async def _download_bergamot_models(self) -> bool:
        """
        Download Bergamot translation models
        """
        try:
            # Model configurations from sign.mt
            models = {
                "en-ase": {
                    "url": "https://sign.mt/models/bergamot/spoken-to-signed/en-ase",
                    "files": ["config.json", "model.bin", "lex.50.50.bin", "vocab.spm"],
                },
                "en-bfi": {
                    "url": "https://sign.mt/models/bergamot/spoken-to-signed/en-bfi",
                    "files": ["config.json", "model.bin", "lex.50.50.bin", "vocab.spm"],
                },
                "de-gsg": {
                    "url": "https://sign.mt/models/bergamot/spoken-to-signed/de-gsg",
                    "files": ["config.json", "model.bin", "lex.50.50.bin", "vocab.spm"],
                },
                "de-sgg": {
                    "url": "https://sign.mt/models/bergamot/spoken-to-signed/de-sgg",
                    "files": ["config.json", "model.bin", "lex.50.50.bin", "vocab.spm"],
                },
            }

            for model_name, model_info in models.items():
                if not await self._download_bergamot_model(model_name, model_info):
                    self.logger.warning(f"Failed to download model: {model_name}")
                    continue

            return True

        except Exception as e:
            self.logger.error(f"Error downloading Bergamot models: {e}")
            return False

    async def _download_bergamot_model(
        self, model_name: str, model_info: Dict[str, Any]
    ) -> bool:
        """
        Download a specific Bergamot model
        """
        try:
            model_dir = self.bergamot_path / model_name
            model_dir.mkdir(parents=True, exist_ok=True)

            # Check if model already exists
            if self._model_exists(model_dir, model_info["files"]):
                self.logger.info(
                    f"Model {model_name} already exists, skipping download"
                )
                return True

            self.logger.info(f"Downloading Bergamot model: {model_name}")

            # Download each file
            for filename in model_info["files"]:
                url = f"{model_info['url']}/{filename}"
                file_path = model_dir / filename

                if not await self._download_file(url, file_path):
                    self.logger.error(f"Failed to download {filename} for {model_name}")
                    return False

            self.logger.info(f"Successfully downloaded model: {model_name}")
            return True

        except Exception as e:
            self.logger.error(f"Error downloading model {model_name}: {e}")
            return False

    async def _download_sign_language_data(self) -> bool:
        """
        Download sign language data from sign.mt
        """
        try:
            # Sign language data URLs
            data_sources = {
                "asl": "https://sign.mt/data/asl",
                "bsl": "https://sign.mt/data/bsl",
                "gsg": "https://sign.mt/data/gsg",
                "sgg": "https://sign.mt/data/sgg",
            }

            for lang_code, url in data_sources.items():
                if not await self._download_language_data(lang_code, url):
                    self.logger.warning(f"Failed to download data for {lang_code}")
                    continue

            return True

        except Exception as e:
            self.logger.error(f"Error downloading sign language data: {e}")
            return False

    async def _download_language_data(self, lang_code: str, url: str) -> bool:
        """
        Download data for a specific language
        """
        try:
            lang_dir = self.data_path / "signs" / lang_code
            lang_dir.mkdir(parents=True, exist_ok=True)

            # Files to download
            files = ["lexicon.json", "pose_mappings.json", "signwriting_mappings.json"]

            for filename in files:
                file_url = f"{url}/{filename}"
                file_path = lang_dir / filename

                if not await self._download_file(file_url, file_path):
                    self.logger.warning(
                        f"Failed to download {filename} for {lang_code}"
                    )
                    continue

            return True

        except Exception as e:
            self.logger.error(f"Error downloading language data for {lang_code}: {e}")
            return False

    async def _download_wasm_files(self) -> bool:
        """
        Download WebAssembly files
        """
        try:
            wasm_dir = self.bergamot_path / "wasm"
            wasm_dir.mkdir(parents=True, exist_ok=True)

            # WebAssembly files needed
            wasm_files = {
                "bergamot-translator-worker.js": "https://sign.mt/wasm/bergamot-translator-worker.js",
                "bergamot-translator-worker.wasm": "https://sign.mt/wasm/bergamot-translator-worker.wasm",
            }

            for filename, url in wasm_files.items():
                file_path = wasm_dir / filename

                if not file_path.exists():
                    self.logger.info(f"Downloading WebAssembly file: {filename}")
                    if not await self._download_file(url, file_path):
                        self.logger.error(f"Failed to download {filename}")
                        return False

            return True

        except Exception as e:
            self.logger.error(f"Error downloading WebAssembly files: {e}")
            return False

    async def _download_file(self, url: str, file_path: Path) -> bool:
        """
        Download a file from URL
        """
        try:
            # Check if file already exists
            if file_path.exists():
                self.logger.debug(f"File already exists: {file_path}")
                return True

            self.logger.info(f"Downloading: {url} -> {file_path}")

            # Download with progress tracking
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded_size = 0

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        # Log progress for large files
                        if (
                            total_size > 0 and downloaded_size % (1024 * 1024) == 0
                        ):  # Every MB
                            progress = (downloaded_size / total_size) * 100
                            self.logger.info(f"Download progress: {progress:.1f}%")

            self.logger.info(f"Successfully downloaded: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error downloading {url}: {e}")
            return False

    def _model_exists(self, model_dir: Path, required_files: List[str]) -> bool:
        """
        Check if a model already exists with all required files
        """
        try:
            for filename in required_files:
                file_path = model_dir / filename
                if not file_path.exists():
                    return False

            return True

        except Exception:
            return False

    def get_model_path(self, model_name: str) -> Optional[Path]:
        """
        Get the path to a downloaded model
        """
        try:
            model_path = self.bergamot_path / model_name
            if model_path.exists():
                return model_path
            return None

        except Exception as e:
            self.logger.error(f"Error getting model path for {model_name}: {e}")
            return None

    def get_language_data_path(self, lang_code: str) -> Optional[Path]:
        """
        Get the path to language data
        """
        try:
            data_path = self.data_path / "signs" / lang_code
            if data_path.exists():
                return data_path
            return None

        except Exception as e:
            self.logger.error(f"Error getting language data path for {lang_code}: {e}")
            return None

    def list_available_models(self) -> List[str]:
        """
        List all available models
        """
        try:
            models = []
            for model_dir in self.bergamot_path.iterdir():
                if model_dir.is_dir() and model_dir.name != "wasm":
                    models.append(model_dir.name)
            return models

        except Exception as e:
            self.logger.error(f"Error listing models: {e}")
            return []

    def list_available_languages(self) -> List[str]:
        """
        List all available languages
        """
        try:
            languages = []
            signs_dir = self.data_path / "signs"
            if signs_dir.exists():
                for lang_dir in signs_dir.iterdir():
                    if lang_dir.is_dir():
                        languages.append(lang_dir.name)
            return languages

        except Exception as e:
            self.logger.error(f"Error listing languages: {e}")
            return []

    async def verify_models(self) -> Dict[str, bool]:
        """
        Verify that all required models are properly downloaded
        """
        try:
            verification_results = {}

            # Check Bergamot models
            expected_models = ["en-ase", "en-bfi", "de-gsg", "de-sgg"]
            for model_name in expected_models:
                model_path = self.get_model_path(model_name)
                if model_path:
                    # Check for required files
                    required_files = [
                        "config.json",
                        "model.bin",
                        "lex.50.50.bin",
                        "vocab.spm",
                    ]
                    verification_results[f"bergamot_{model_name}"] = self._model_exists(
                        model_path, required_files
                    )
                else:
                    verification_results[f"bergamot_{model_name}"] = False

            # Check language data
            expected_languages = ["asl", "bsl", "gsg", "sgg"]
            for lang_code in expected_languages:
                data_path = self.get_language_data_path(lang_code)
                if data_path:
                    required_files = ["lexicon.json", "pose_mappings.json"]
                    verification_results[f"language_{lang_code}"] = all(
                        (data_path / filename).exists() for filename in required_files
                    )
                else:
                    verification_results[f"language_{lang_code}"] = False

            # Check WebAssembly files
            wasm_dir = self.bergamot_path / "wasm"
            wasm_files = [
                "bergamot-translator-worker.js",
                "bergamot-translator-worker.wasm",
            ]
            verification_results["wasm_files"] = all(
                (wasm_dir / filename).exists() for filename in wasm_files
            )

            return verification_results

        except Exception as e:
            self.logger.error(f"Error verifying models: {e}")
            return {}


async def download_sign_mt_models(base_path: Optional[Path] = None) -> bool:
    """
    Convenience function to download all sign.mt models
    """
    downloader = ModelDownloader(base_path)
    return await downloader.download_sign_mt_models()


def verify_sign_mt_models(base_path: Optional[Path] = None) -> Dict[str, bool]:
    """
    Convenience function to verify sign.mt models
    """
    downloader = ModelDownloader(base_path)
    return asyncio.run(downloader.verify_models())
