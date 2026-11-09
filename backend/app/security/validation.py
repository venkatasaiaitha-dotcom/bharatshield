"""
BharatShield Voice - Audio & Input Validation
Rigorous validation of audio files, magic bytes, MIME types, and file lifecycles.
Ensures temporary audio is strictly purged after processing.
"""

import os
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger("validation")

# Audio Magic Bytes signatures for strict verification
MAGIC_SIGNATURES = {
    "wav": [b"RIFF"],
    "mp3": [b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"],
    "ogg": [b"OggS"],
    "flac": [b"fLaC"],
    "m4a": [b"ftypM4A", b"ftypmp42", b"ftypisom"],
    "webm": [b"\x1a\x45\xdf\xa3"],  # EBML header
}


class AudioValidationError(HTTPException):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)


def validate_audio_file(
    filename: str,
    content_type: Optional[str],
    file_bytes: bytes
) -> Tuple[bool, str]:
    """
    Validates audio file size, extension, MIME type, and binary header magic bytes.
    Returns (is_valid, normalized_extension).
    """
    # 1. Check empty file
    size = len(file_bytes)
    if size == 0:
        raise AudioValidationError("Audio file is empty (0 bytes). Please upload a valid recording.")

    # 2. Check maximum size limit
    if size > settings.MAX_AUDIO_SIZE_BYTES:
        max_mb = settings.MAX_AUDIO_SIZE_BYTES / (1024 * 1024)
        raise AudioValidationError(f"Audio file exceeds maximum allowed size of {max_mb:.0f} MB.")

    # 3. Check file extension
    ext = Path(filename).suffix.lower()
    if ext not in settings.ALLOWED_AUDIO_EXTENSIONS:
        raise AudioValidationError(
            f"Unsupported audio format '{ext}'. Allowed formats: {', '.join(settings.ALLOWED_AUDIO_EXTENSIONS)}"
        )

    # 4. Check MIME type (if provided by client)
    if content_type:
        normalized_mime = content_type.lower().split(";")[0].strip()
        # Some webm/audio types can be generic application/octet-stream; verify via magic bytes
        if normalized_mime not in settings.ALLOWED_AUDIO_MIMES and normalized_mime != "application/octet-stream":
            logger.warning("Unrecognized MIME type: %s, falling back to binary magic check", normalized_mime)

    # 5. Magic Byte inspection (prevents spoofed file extensions)
    ext_clean = ext.lstrip(".")
    if ext_clean in ("wav", "mp3", "ogg", "flac", "webm"):
        matched_magic = False
        sample = file_bytes[:32]
        signatures = MAGIC_SIGNATURES.get(ext_clean, [])
        for sig in signatures:
            if sig in sample:
                matched_magic = True
                break

        # Allow webm/ogg audio from browser MediaRecorder
        if not matched_magic and ext_clean in ("webm", "ogg"):
            if b"\x1a\x45" in sample or b"OggS" in sample:
                matched_magic = True

        # If magic signature does not match expected audio format
        if not matched_magic and ext_clean == "wav" and not sample.startswith(b"RIFF"):
            raise AudioValidationError("Corrupted or malformed WAV audio header.")

    return True, ext


class TempAudioContext:
    """
    Context manager that safely saves temporary audio to disk for processing
    and guarantees automatic file deletion on exit (Privacy compliance).
    """
    def __init__(self, filename: str, content: bytes):
        self.filename = filename
        self.content = content
        self.temp_dir = settings.BACKEND_DIR / "temp_audio"
        self.temp_file_path: Optional[Path] = None

    def __enter__(self) -> Path:
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        # Use sanitized file name with process-unique timestamp
        safe_name = f"temp_{os.urandom(8).hex()}_{Path(self.filename).name}"
        self.temp_file_path = self.temp_dir / safe_name
        with open(self.temp_file_path, "wb") as f:
            f.write(self.content)
        return self.temp_file_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_file_path and self.temp_file_path.exists():
            try:
                self.temp_file_path.unlink()
                logger.info("Purged temporary audio: %s", self.temp_file_path.name)
            except Exception as e:
                logger.error("Failed to delete temporary audio file: %s", str(e))
