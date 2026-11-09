"""
BharatShield Voice - In-Memory Rate Limiting
Simple token-bucket rate limiter to protect backend endpoints from automated abuse.
"""

import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException
from app.config import settings

# Stores IP -> (remaining_tokens, last_refill_timestamp)
_RATE_LIMIT_BUCKETS: Dict[str, Tuple[float, float]] = {}


def check_rate_limit(request: Request):
    """
    Checks if client IP is within allowed request budget.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    now = time.time()
    rate = settings.RATE_LIMIT_REQUESTS_PER_MINUTE / 60.0  # tokens per second
    capacity = settings.RATE_LIMIT_REQUESTS_PER_MINUTE

    tokens, last_time = _RATE_LIMIT_BUCKETS.get(client_ip, (capacity, now))

    # Refill tokens based on elapsed time
    elapsed = now - last_time
    tokens = min(capacity, tokens + elapsed * rate)

    if tokens < 1.0:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait a moment before sending more requests."
        )

    _RATE_LIMIT_BUCKETS[client_ip] = (tokens - 1.0, now)
