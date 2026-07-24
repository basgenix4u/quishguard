"""
QuishGuard — Application Configuration
Loads all settings from environment variables with sensible defaults.
"""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    database_url: str = "postgresql+asyncpg://quishguard:quishguard_dev@localhost:5432/quishguard_db"
    database_url_sync: str = "postgresql+psycopg2://quishguard:quishguard_dev@localhost:5432/quishguard_db"

    # === Security ===
    secret_key: str = "change-me-to-a-secure-random-string-in-production"
    api_key_prefix: str = "qg_live_"
    encryption_algorithm: str = "HS256"

    # === File Upload ===
    max_file_size_mb: int = 10
    upload_dir: str = "./uploads"
    allowed_extensions: str = "png,jpg,jpeg,webp"

    # === Rate Limiting ===
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 100

    # === Threat Intelligence ===
    google_safe_browsing_api_key: str = ""
    google_safe_browsing_client_id: str = "quishguard"
    urlscan_api_key: str = ""

    # === ML Models ===
    ai_detector_model_path: str = "./models_pretrained/ai_detector_efficientnet_b4.pt"
    url_classifier_model_path: str = "./models_pretrained/url_classifier_xgboost.pkl"
    qr_tampering_model_path: str = "./models_pretrained/qr_tampering_resnet18.pt"

    # === CORS ===
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

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
