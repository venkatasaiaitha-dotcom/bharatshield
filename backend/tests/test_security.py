"""
Tests for Security & Secret Isolation
"""

from app.config import settings
from app.security.sanitizer import sanitize_response_data
from app.services.gnani.provider import GnaniProvider


def test_settings_secret_masking():
    # settings repr must never contain raw key
    assert "PASTE_KEY_HERE" not in repr(settings)
    masked = settings.get_masked_status()
    assert "PASTE_KEY_HERE" not in str(masked)
    assert "gnani_key" not in masked


def test_sanitizer_removes_secrets():
    payload = {
        "status": "success",
        "gnani_api_key": "SUPER_SECRET_12345",
        "api_key": "SECRET_KEY_VALUE",
        "data": {
            "token": "BEARER_TOKEN",
            "transcript": "Hello sir"
        }
    }
    cleaned = sanitize_response_data(payload)

    assert "gnani_api_key" not in cleaned
    assert "api_key" not in cleaned
    assert "token" not in cleaned["data"]
    assert cleaned["data"]["transcript"] == "Hello sir"


def test_provider_status_no_secrets():
    provider = GnaniProvider()
    status = provider.get_provider_status()

    assert "name" in status
    assert "capabilities" in status
    assert "api_key" not in status
    assert "GNANI_API_KEY" not in str(status)
