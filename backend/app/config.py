"""
QuishGuard — Application Configuration
Production-ready: auto-handles Render DATABASE_URL, PORT, and persistent disk.
"""

import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_database_url(url: str) -> str:
    """Normalize DATABASE_URL for async SQLAlchemy.
    
    Render provides: postgresql://user:pass@host:port/db
    SQLAlchemy async needs: postgresql+asyncpg://user:pass@host:port/db
    """
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # === Application ===
    app_name: str = "QuishGuard"
    app_version: str = "0.1.0"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # === Database ===
    # Render auto-provides DATABASE_URL — we normalize it for asyncpg
    database_url: str = _normalize_database_url(
        os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./quishguard_local.db")
    )
    database_url_sync: str = ""

    # === Server ===
    # Render auto-provides PORT
    port: int = int(os.environ.get("PORT", "8000"))

    # === Security ===
    secret_key: str = os.environ.get("SECRET_KEY", "change-me-to-a-secure-random-string-in-production")
    api_key_prefix: str = "qg_live_"
    encryption_algorithm: str = "HS256"

    # === File Upload ===
    max_file_size_mb: int = 10
    # Render persistent disk mount: /data/uploads
    upload_dir: str = os.environ.get("UPLOAD_DIR", "./uploads")
    allowed_extensions: str = "png,jpg,jpeg,webp"

    # === Rate Limiting ===
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 100

    # === Threat Intelligence ===
    google_safe_browsing_api_key: str = ""
    google_safe_browsing_client_id: str = "quishguard"
    urlscan_api_key: str = ""

    # === ML Models ===
    # On Render, models are stored on persistent disk /data/models
    ai_detector_model_path: str = os.environ.get(
        "AI_DETECTOR_MODEL_PATH",
        "./models_pretrained/ai_detector_efficientnet_b4.pt"
    )
    url_classifier_model_path: str = os.environ.get(
        "URL_CLASSIFIER_MODEL_PATH",
        "./models_pretrained/url_classifier_xgboost.pkl"
    )
    qr_tampering_model_path: str = os.environ.get(
        "QR_TAMPERING_MODEL_PATH",
        "./models_pretrained/qr_tampering_resnet18.pt"
    )

    # === CORS ===
    # In production, set to your Vercel frontend URL
    cors_origins: str = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8000"
    )

    # === Logging ===
    log_level: str = "INFO"

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.allowed_extensions.split(",")]

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir)


settings = Settings()
