from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Vizart AI API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str

    # CORS settings
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Directory settings
    UPLOAD_DIR: str = "./static/uploads"
    RESULTS_DIR: str = "./static/results"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # AI Model settings
    MODEL_CACHE_DIR: str = "./models"
    ENABLE_GPU: bool = True
    MODEL_DEVICE: str = "cuda" if ENABLE_GPU else "cpu"

    # Processing settings
    MAX_CONCURRENT_JOBS: int = 4
    JOB_TIMEOUT: int = 300  # 5 minutes
    RESULT_EXPIRY_TIME: int = 3600  # 1 hour

    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"

    # Database settings
    DATABASE_URL: str = "postgresql://user:password@localhost/vizart_db"

    # AWS S3 settings (optional)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None

    # Monitoring settings
    SENTRY_DSN: Optional[str] = None

    # Allowed image formats
    ALLOWED_MIME_TYPES: List[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure directories exist
for directory in [settings.UPLOAD_DIR, settings.RESULTS_DIR, settings.MODEL_CACHE_DIR]:
    Path(directory).mkdir(parents=True, exist_ok=True)