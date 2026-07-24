"""
QuishGuard — FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    logger.info(f"🚀 {settings.app_name} v{settings.app_version} starting up...")

    # Ensure upload directory exists
    upload_path = settings.upload_path
    upload_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"📁 Upload directory: {upload_path.resolve()}")

    logger.info(f"🧠 ML model paths configured:")
    logger.info(f"   AI Detector: {settings.ai_detector_model_path}")
    logger.info(f"   URL Classifier: {settings.url_classifier_model_path}")
    logger.info(f"   QR Tampering: {settings.qr_tampering_model_path}")

    # Initialize database tables
    from app.database import init_db
    await init_db()

    yield

    logger.info(f"🛑 {settings.app_name} shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multimodal Deep Learning Framework for Detecting AI-Generated Images and QR Phishing (Quishing)",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.api_v1_prefix)


# === Smoke Test Routes ===

@app.get("/", tags=["Health"])
async def root():
    """Root health check."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "debug": settings.debug,
    }
