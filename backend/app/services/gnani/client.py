"""
BharatShield Voice - Gnani AI Client
Encapsulates all raw HTTP interactions with the Gnani Vachana / VoiceOS platform.
Strictly safeguards API credentials from logging, exceptions, and serialization.
"""

import httpx
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger("gnani_client")


class GnaniAPIException(Exception):
    """Safe exception that never exposes credentials or internal keys."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class GnaniClient:
    """
    Low-level HTTP client for official Gnani AI (Vachana) REST endpoints.
    Handles authentication, timeouts, and error handling without exposing secrets.
    """

    def __init__(self):
        self.base_url = settings.GNANI_API_BASE_URL.rstrip("/")
        self.timeout = settings.GNANI_REQUEST_TIMEOUT_SECONDS

    def _get_headers(self) -> Dict[str, str]:
        """
        Build authentication headers using the server-side environment secret.
        Raises GnaniAPIException if key is not configured.
        """
        if not settings.is_gnani_configured:
            raise GnaniAPIException("Gnani API key is not configured in backend environment", status_code=503)

        api_key = settings.get_gnani_api_key_secret()
        return {
            "X-API-Key-ID": api_key,
            "Accept": "application/json"
        }

    async def transcribe_audio_file(
        self,
        file_path: Path,
        mime_type: str = "audio/wav",
        language_code: str = "indic-auto",
        model: str = "prisma-v3.0"
    ) -> Dict[str, Any]:
        """
        Submits audio to Gnani STT API (v3 / prisma series) for multilingual transcription.
        """
        headers = self._get_headers()
        endpoint = f"{self.base_url}{settings.GNANI_STT_ENDPOINT}"

        if not file_path.exists():
            raise GnaniAPIException("Target audio file not found on disk", status_code=400)

        file_size = file_path.stat().st_size
        if file_size == 0:
            raise GnaniAPIException("Audio file is empty", status_code=400)

        logger.info(f"Submitting audio to Gnani STT: size={file_size} bytes, lang={language_code}, model={model}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                with open(file_path, "rb") as f:
                    files = {
                        "audio_file": (file_path.name, f, mime_type)
                    }
                    data = {
                        "model": model,
                        "language_code": language_code
                    }
                    response = await client.post(endpoint, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    data = response.json()
                    logger.info("Gnani STT transcription successful")
                    return data
                elif response.status_code in (401, 403):
                    logger.warning("Gnani STT authentication failed (HTTP %s)", response.status_code)
                    raise GnaniAPIException("Gnani API authentication failed. Verify GNANI_API_KEY.", status_code=401)
                else:
                    logger.error("Gnani STT returned error HTTP %s", response.status_code)
                    raise GnaniAPIException(f"Gnani STT failed with HTTP {response.status_code}", status_code=response.status_code)

        except httpx.TimeoutException:
            logger.error("Gnani STT request timed out")
            raise GnaniAPIException("Gnani STT request timed out", status_code=504)
        except httpx.RequestError as exc:
            logger.error("Gnani network communication error: %s", type(exc).__name__)
            raise GnaniAPIException("Network error communicating with Gnani STT service", status_code=502)

    async def synthesize_speech(
        self,
        text: str,
        language: str = "te-IN",
        voice: str = "Pranav",
        model: str = "timbre-v2.5"
    ) -> bytes:
        """
        Synthesizes text into speech audio via Gnani TTS (Timbre series).
        """
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "audio/wav, audio/mpeg, application/octet-stream"

        endpoint = f"{self.base_url}{settings.GNANI_TTS_ENDPOINT}"

        payload = {
            "text": text,
            "voice": voice,
            "model": model,
            "language": language,
            "speed": 1.0,
            "audio_config": {
                "encoding": "linear_pcm",
                "container": "wav",
                "num_channels": 1,
                "sample_rate": 24000,
                "sample_width": 2
            }
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                if response.status_code == 200:
                    return response.content
                elif response.status_code in (401, 403):
                    raise GnaniAPIException("Gnani TTS authentication failed", status_code=401)
                else:
                    raise GnaniAPIException(f"Gnani TTS failed with HTTP {response.status_code}", status_code=response.status_code)
        except httpx.TimeoutException:
            raise GnaniAPIException("Gnani TTS request timed out", status_code=504)
        except httpx.RequestError as exc:
            raise GnaniAPIException("Network error communicating with Gnani TTS service", status_code=502)
