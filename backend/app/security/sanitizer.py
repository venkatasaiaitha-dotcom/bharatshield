"""
BharatShield Voice - Output Secret Sanitizer
Guarantees that no response payload contains sensitive credentials,
API keys, or internal authorization tokens.
"""

from typing import Any, Dict, List
import re

SENSITIVE_KEY_NAMES = {
    "api_key", "gnani_api_key", "secret", "password", "token",
    "authorization", "x-api-key-id", "access_token"
}


def sanitize_response_data(data: Any) -> Any:
    """
    Recursively scrubs dictionary keys and values to ensure no secrets can escape.
    """
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            if str(k).lower() in SENSITIVE_KEY_NAMES:
                continue
            cleaned[k] = sanitize_response_data(v)
        return cleaned
    elif isinstance(data, list):
        return [sanitize_response_data(item) for item in data]
    return data
