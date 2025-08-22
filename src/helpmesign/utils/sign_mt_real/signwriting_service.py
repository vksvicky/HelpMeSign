"""
SignWriting Service - Following sign.mt patterns

This implements the SignWriting translation service following their patterns
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .bergamot_translator import BergamotTranslator, TranslationResponse


@dataclass
class SignWritingResponse:
    """SignWriting response following sign.mt patterns"""

    text: str
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class SignWritingService:
    """
    SignWriting Service following sign.mt patterns

    From their SignWritingTranslationService - handles spoken to SignWriting translation
    """

    def __init__(self, bergamot_translator: BergamotTranslator):
        self.logger = logging.getLogger(__name__)
        self.bergamot_translator = bergamot_translator

    async def translate_spoken_to_signwriting(
        self,
        text: str,
        sentences: List[str],
        spoken_language: str,
        signed_language: str,
    ) -> SignWritingResponse:
        """
        Translate spoken text to SignWriting following sign.mt patterns

        From their translateSpokenToSignWriting method
        """
        try:
            direction = "spoken-to-signed"

            # Try offline translation first (like their offlineSpecific)
            try:
                response = await self.bergamot_translator.translate_offline(
                    direction, text, spoken_language, signed_language
                )
                if response.text:
                    self.logger.info(f"Offline translation successful: {response.text}")
                    return SignWritingResponse(text=response.text)
            except Exception as e:
                self.logger.debug(f"Offline translation failed: {e}")

            # Try generic offline translation (like their offlineGeneric)
            try:
                generic_text = f"${spoken_language} ${signed_language} {text}"
                response = await self.bergamot_translator.translate_offline(
                    direction, generic_text, "spoken", "signed"
                )
                if response.text:
                    self.logger.info(
                        f"Generic offline translation successful: {response.text}"
                    )
                    return SignWritingResponse(text=response.text)
            except Exception as e:
                self.logger.debug(f"Generic offline translation failed: {e}")

            # Fallback to online translation (like their online)
            response = self.bergamot_translator.translate_online(
                direction, text, sentences, spoken_language, signed_language
            )

            self.logger.info(f"Online translation successful: {response.text}")
            return SignWritingResponse(text=response.text)

        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            # Return empty SignWriting as fallback
            return SignWritingResponse(text="")

    def preprocess_spoken_text(self, text: str) -> str:
        """
        Preprocess spoken text following sign.mt patterns

        From their preProcessSpokenText method
        """
        return text.replace("\n", " ")

    def postprocess_signwriting(self, text: str) -> str:
        """
        Postprocess SignWriting following sign.mt patterns

        From their postProcessSignWriting method
        """
        try:
            import re

            # Remove all tokens that start with a $
            text = re.sub(r"\$[^\s]+", "", text)

            # Space signs correctly
            text = text.replace(" ", "")
            text = re.sub(r"(\d)M", r"\1 M", text)

            return text

        except Exception as e:
            self.logger.error(f"Error post-processing SignWriting: {e}")
            return text

    def validate_signwriting(self, text: str) -> bool:
        """
        Validate SignWriting following sign.mt patterns
        """
        try:
            if not text.strip():
                return False

            # Basic SignWriting validation
            # SignWriting typically contains symbols like S, M, numbers, etc.
            import re

            signwriting_pattern = r"[SM]\d+"
            matches = re.findall(signwriting_pattern, text)

            return len(matches) > 0

        except Exception as e:
            self.logger.error(f"Error validating SignWriting: {e}")
            return False

    def parse_signwriting(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse SignWriting into structured format following sign.mt patterns
        """
        try:
            import re

            # Parse SignWriting symbols
            symbols = []

            # Split by spaces and parse each symbol
            parts = text.split()
            for part in parts:
                symbol_info = {}

                # Parse S-prefix symbols (hand shapes)
                s_match = re.match(r"S(\d+)", part)
                if s_match:
                    symbol_info["type"] = "hand_shape"
                    symbol_info["value"] = str(int(s_match.group(1)))
                    symbol_info["raw"] = part
                    symbols.append(symbol_info)
                    continue

                # Parse M-prefix symbols (movements)
                m_match = re.match(r"M(\d+)", part)
                if m_match:
                    symbol_info["type"] = "movement"
                    symbol_info["value"] = str(int(m_match.group(1)))
                    symbol_info["raw"] = part
                    symbols.append(symbol_info)
                    continue

                # Parse other symbols
                symbol_info["type"] = "unknown"
                symbol_info["value"] = part
                symbol_info["raw"] = part
                symbols.append(symbol_info)

            return symbols

        except Exception as e:
            self.logger.error(f"Error parsing SignWriting: {e}")
            return []
