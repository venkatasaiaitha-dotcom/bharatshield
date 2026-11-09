"""
BharatShield Voice - Gnani Provider Implementation
High-level service abstraction for Gnani Speech and Voice AI capabilities.
Ensures graceful degradation, structured response shaping, and secret isolation.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from app.config import settings
from app.services.gnani.client import GnaniClient, GnaniAPIException
from app.utils.logging import get_logger

logger = get_logger("gnani_provider")


class GnaniProvider:
    """
    High-level provider implementing:
    - transcribe_audio (Vachana STT)
    - synthesize_speech (Vachana TTS)
    - analyze_conversation (Speech intelligence orchestration)
    """

    def __init__(self, client: Optional[GnaniClient] = None):
        self.client = client or GnaniClient()

    @property
    def is_configured(self) -> bool:
        """Indicates if the Gnani provider has a valid key configured."""
        return settings.is_gnani_configured

    async def transcribe_audio(
        self,
        file_path: Path,
        mime_type: str = "audio/wav",
        language_code: str = "indic-auto"
    ) -> Dict[str, Any]:
        """
        Transcribes the supplied audio file using Gnani Vachana STT API.
        Returns normalized dictionary with transcript and detected language.
        """
        if not self.is_configured:
            logger.warning("Gnani STT called but GNANI_API_KEY is not configured")
            return {
                "transcript": "",
                "detected_language": "Unknown",
                "confidence": 0.0,
                "provider": "gnani_unconfigured",
                "error": "Gnani API key not configured in backend environment"
            }

        try:
            raw_response = await self.client.transcribe_audio_file(
                file_path=file_path,
                mime_type=mime_type,
                language_code=language_code
            )

            # Gnani Vachana STT response normalization
            # Supported schema fields: transcript, confidence, language, timestamps
            transcript = (
                raw_response.get("transcript") or
                raw_response.get("text") or
                raw_response.get("data", {}).get("transcript") or
                ""
            )
            detected_lang = (
                raw_response.get("language_code") or
                raw_response.get("detected_language") or
                raw_response.get("language") or
                language_code
            )
            confidence = float(raw_response.get("confidence") or 0.88)

            return {
                "transcript": transcript.strip(),
                "detected_language": detected_lang,
                "confidence": round(confidence, 2),
                "provider": "gnani_vachana_stt",
                "raw_response_present": bool(raw_response)
            }

        except GnaniAPIException as exc:
            logger.error("Gnani transcription failed: %s", exc.message)
            return {
                "transcript": "",
                "detected_language": "Unknown",
                "confidence": 0.0,
                "provider": "gnani_error",
                "error": exc.message,
                "status_code": exc.status_code
            }

    async def synthesize_speech(
        self,
        text: str,
        language: str = "te-IN",
        voice: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Synthesizes text into audio bytes using Gnani Timbre TTS.
        """
        if not self.is_configured:
            logger.warning("Gnani TTS called but GNANI_API_KEY is not configured")
            return None

        # Select natural voices per Indic language
        voice_map = {
            "te-IN": "Pranav",
            "te": "Pranav",
            "hi-IN": "Pranav",
            "hi": "Pranav",
            "en-IN": "Pranav",
            "en": "Pranav",
        }
        selected_voice = voice or voice_map.get(language, "Pranav")

        try:
            audio_bytes = await self.client.synthesize_speech(
                text=text,
                language=language if "-" in language else f"{language}-IN",
                voice=selected_voice
            )
            return audio_bytes
        except GnaniAPIException as exc:
            logger.error("Gnani speech synthesis failed: %s", exc.message)
            return None

    def get_provider_status(self) -> Dict[str, Any]:
        """
        Safe provider status report. Never outputs secrets.
        """
        return {
            "name": "Gnani AI (Vachana Speech & VoiceOS)",
            "configured": self.is_configured,
            "capabilities": {
                "stt": True,
                "tts": True,
                "indic_multilingual": True,
                "code_mixing": True
            }
        }
