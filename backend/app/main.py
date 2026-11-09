"""
BharatShield Voice - Main Application Entrypoint
FastAPI application with CORS, security headers, structured logging, and safe error routing.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.api.routes import health, analyze
from app.utils.logging import get_logger

logger = get_logger("main")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multilingual AI safety system for Indian voice conversations and calls.",
    docs_url="/docs" if settings.DEBUG or settings.ENVIRONMENT == "development" else None,
    redoc_url=None
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    Appends hardened HTTP security headers to all responses.
    """
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Safe global exception handler that logs errors safely and returns clean messages.
    Never exposes stack traces, credentials, or file paths to clients.
    """
    logger.error("Unhandled server exception: %s", type(exc).__name__)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "An unexpected error occurred during processing.",
            "type": type(exc).__name__,
            "message": "Please verify your input or try again shortly."
        }
    )


# Mount application routers
app.include_router(health.router)
app.include_router(analyze.router)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "tagline": "Understand the call. Detect the risk. Protect yourself.",
        "status": "online",
        "docs": "/docs" if settings.DEBUG or settings.ENVIRONMENT == "development" else "disabled"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
