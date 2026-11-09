"""
BharatShield Voice - Secure Configuration System
Handles environment variable loading, secret protection, and runtime configuration.
Never prints, serializes, or leaks API keys.
"""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr

# Resolve base directories
BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BACKEND_DIR / ".env"

PLACEHOLDER_KEYS = {"", "PASTE_KEY_HERE", "your_gnani_api_key_here", "CHANGE_ME"}


class Settings(BaseSettings):
    """
    Application Settings.
    The Gnani API key is stored as a SecretStr to prevent accidental logging or exposure.
    """
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH) if ENV_PATH.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Core Application Info
    APP_NAME: str = "BharatShield Voice API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")

    # Gnani AI Configuration (Strictly server-side)
    GNANI_API_KEY: SecretStr = Field(default=SecretStr(""), env="GNANI_API_KEY")
    GNANI_API_BASE_URL: str = Field(default="https://api.vachana.ai", env="GNANI_API_BASE_URL")
    GNANI_STT_ENDPOINT: str = Field(default="/stt/v3", env="GNANI_STT_ENDPOINT")
    GNANI_TTS_ENDPOINT: str = Field(default="/api/v1/tts/inference", env="GNANI_TTS_ENDPOINT")
    GNANI_REQUEST_TIMEOUT_SECONDS: float = Field(default=30.0, env="GNANI_REQUEST_TIMEOUT_SECONDS")

    # Security & Upload Limits
    MAX_AUDIO_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB limit
    ALLOWED_AUDIO_EXTENSIONS: List[str] = [".wav", ".mp3", ".m4a", ".ogg", ".webm", ".flac", ".aac"]
    ALLOWED_AUDIO_MIMES: List[str] = [
        "audio/wav", "audio/x-wav", "audio/wave",
        "audio/mpeg", "audio/mp3",
        "audio/mp4", "audio/x-m4a", "audio/m4a",
        "audio/ogg", "audio/opus",
        "audio/webm",
        "audio/flac", "audio/x-flac",
        "audio/aac", "audio/x-aac"
    ]

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60

    @property
    def is_gnani_configured(self) -> bool:
        """
        Check if a valid, non-placeholder Gnani API key is configured.
        """
        raw_key = self.GNANI_API_KEY.get_secret_value().strip()
        return raw_key != "" and raw_key not in PLACEHOLDER_KEYS

    def get_gnani_api_key_secret(self) -> str:
        """
        Retrieve raw key for authorized server-side HTTP calls only.
        NEVER expose in responses or logs.
        """
        return self.GNANI_API_KEY.get_secret_value()

    def get_masked_status(self) -> dict:
        """
        Safe status dictionary for diagnostics and health check.
        Never reveals actual key contents or fragments.
        """
        configured = self.is_gnani_configured
        return {
            "configured": configured,
            "status": "ready" if configured else "pending_key",
            "base_url": self.GNANI_API_BASE_URL
        }

    def __repr__(self) -> str:
        return f"<Settings app='{self.APP_NAME}' gnani_configured={self.is_gnani_configured}>"


# Global settings instance
settings = Settings()
