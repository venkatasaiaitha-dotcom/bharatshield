"""
BharatShield Voice - Health & Readiness Diagnostics Endpoint
Exposes operational status without ever leaking keys, secrets, or internal paths.
"""

from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """
    Public health check endpoint.
    Returns backend readiness and Gnani configuration status.
    NEVER includes the API key or secret values.
    """
    masked = settings.get_masked_status()
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "gnani_configured": masked["configured"],
        "gnani_status": masked["status"],
        "environment": settings.ENVIRONMENT
    }
