"""
Tests for Audio Validation & Security Lifecycle
"""

import pytest
from app.security.validation import validate_audio_file, AudioValidationError


def test_valid_wav_audio():
    # Valid RIFF header
    dummy_wav = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00" + b"\x00" * 40
    is_valid, ext = validate_audio_file("recording.wav", "audio/wav", dummy_wav)
    assert is_valid is True
    assert ext == ".wav"


def test_empty_audio_rejected():
    with pytest.raises(AudioValidationError) as exc:
        validate_audio_file("empty.wav", "audio/wav", b"")
    assert "empty" in str(exc.value.detail).lower()


def test_oversized_audio_rejected():
    # 26 MB (limit is 25 MB)
    large_bytes = b"0" * (26 * 1024 * 1024)
    with pytest.raises(AudioValidationError) as exc:
        validate_audio_file("huge.mp3", "audio/mpeg", large_bytes)
    assert "exceeds" in str(exc.value.detail).lower()


def test_unsupported_file_extension():
    with pytest.raises(AudioValidationError) as exc:
        validate_audio_file("malicious.exe", "application/x-msdownload", b"MZ\x90\x00")
    assert "unsupported" in str(exc.value.detail).lower()


def test_corrupt_wav_header():
    # .wav file but doesn't have RIFF header
    with pytest.raises(AudioValidationError) as exc:
        validate_audio_file("fake.wav", "audio/wav", b"NOT_A_WAV_HEADER_AT_ALL_XYZ")
    assert "corrupted" in str(exc.value.detail).lower()
