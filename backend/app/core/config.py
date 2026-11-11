from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "Memory Lane"
    database_url: str
    frontend_url: str = "http://localhost:5173"
    storage_path: Path = Path("storage/uploads")
    max_image_size_mb: int = Field(default=10, ge=1)
    max_photos_per_upload: int = Field(default=10, ge=1)

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()