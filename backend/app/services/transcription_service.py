"""
BharatShield Voice - Transcription Service
Coordinates audio intake, Gnani STT processing, language detection, and fallback handling.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from app.services.gnani.provider import GnaniProvider
from app.analysis.language_engine import detect_language_and_mixing
from app.analysis.schemas import LanguageDetectionResult
from app.utils.logging import get_logger

logger = get_logger("transcription_service")


class TranscriptionService:
    def __init__(self, gnani_provider: Optional[GnaniProvider] = None):
        self.gnani = gnani_provider or GnaniProvider()

    async def transcribe_audio(
        self,
        file_path: Path,
        mime_type: str = "audio/wav",
        language_hint: str = "indic-auto"
    ) -> Dict[str, Any]:
        """
        Transcribes speech using Gnani Vachana STT and analyzes language/code-mixing.
        """
        # Call Gnani STT Provider
        gnani_result = await self.gnani.transcribe_audio(
            file_path=file_path,
            mime_type=mime_type,
            language_code=language_hint
        )

        transcript = gnani_result.get("transcript", "")
        provider_name = gnani_result.get("provider", "unknown")

        # Perform language & code-mixing detection on resulting text
        if transcript:
            lang_result = detect_language_and_mixing(transcript, hint_language=language_hint)
        else:
            lang_result = LanguageDetectionResult(
                detected_language="No Speech Detected",
                confidence=0.0,
                code_mixed=False,
                languages=[]
            )

        return {
            "transcript": transcript,
            "language_info": lang_result,
            "provider": provider_name,
            "error": gnani_result.get("error")
        }
