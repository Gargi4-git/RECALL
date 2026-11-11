
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "RECALL"
    APP_ENV: str = "development"

    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    FRONTEND_URL: str = "http://localhost:3000"

    STORAGE_DIR: Path = (
        Path(__file__).resolve().parents[2] / "storage" / "materials"
    )

    MAX_UPLOAD_SIZE_MB: int = 25

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
