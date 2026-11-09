"""
BharatShield Voice - Speech Synthesis Service
Handles localized voice generation for user explanations using Gnani Timbre TTS.
"""

from typing import Optional
from app.services.gnani.provider import GnaniProvider
from app.utils.logging import get_logger

logger = get_logger("speech_service")


class SpeechService:
    def __init__(self, gnani_provider: Optional[GnaniProvider] = None):
        self.gnani = gnani_provider or GnaniProvider()

    async def generate_spoken_explanation(
        self,
        text: str,
        language: str = "te-IN"
    ) -> Optional[bytes]:
        """
        Synthesizes spoken guidance via Gnani TTS.
        Returns WAV audio bytes if available, or None if provider is unconfigured/failed.
        """
        if not self.gnani.is_configured:
            logger.info("Speech synthesis requested but Gnani is unconfigured.")
            return None

        return await self.gnani.synthesize_speech(text=text, language=language)
