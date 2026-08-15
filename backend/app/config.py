import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "Peblo TV Mini Core API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://peblo_user:peblo_password@localhost:5432/peblo_db"
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://peblo_user:peblo_password@localhost:5432/peblo_db"
    
    # Storage Configuration
    STORAGE_BACKEND: str = "local"  # "local" | "r2"
    UPLOAD_DIR: str = str(BASE_DIR / "storage" / "uploads")
    PUBLISHED_DIR: str = str(BASE_DIR / "storage" / "published")
    REFERENCE_JSON_PATH: str = str(BASE_DIR / "reference.json")
    SEED_DATA_PATH: str = str(BASE_DIR / "data" / "seed_shows.json")
    SAMPLE_ASSETS_DIR: str = str(BASE_DIR / "data" / "sample_assets")
    
    # Cloudflare R2 Credentials (for storage abstraction swap)
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = "peblo-tv-assets"
    R2_PUBLIC_URL_PREFIX: str = "https://assets.peblo.tv"
    
    # Security / RBAC
    SECRET_KEY: str = "peblo-tv-mini-super-secret-key-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
