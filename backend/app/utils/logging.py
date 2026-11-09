"""
BharatShield Voice - Safe Structured Logging
Provides sanitized logging that automatically redacts API keys, credentials, OTPs, and tokens.
"""

import logging
import re
from typing import Any

# Sensitive patterns to scrub from log messages
REDACT_PATTERNS = [
    (re.compile(r'(?i)(api[_-]?key|secret|token|password|auth|bearer)[\s:=]+["\']?([a-zA-Z0-9_\-\.]{8,})["\']?'), r'\1=[REDACTED]'),
    (re.compile(r'(?i)\b(\d{4,6})\b(?=.*otp|.*pin|.*code)'), r'[REDACTED_CODE]'),
    (re.compile(r'\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b'), r'[REDACTED_CARD]'),
]


class SensitiveDataFilter(logging.Filter):
    """
    Log filter that masks potential API keys and credential strings.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern, replacement in REDACT_PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)
        return True


def get_logger(name: str) -> logging.Logger:
    """
    Configures and returns a safe logger instance.
    """
    logger = logging.getLogger(f"bharatshield.{name}")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        handler.addFilter(SensitiveDataFilter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
