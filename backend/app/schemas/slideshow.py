import uuid
from datetime import datetime

from pydantic import BaseModel


class SlideshowPhotoResponse(BaseModel):
    id: uuid.UUID
    original_filename: str
    content_type: str
    image_url: str
    created_at: datetime


class SlideshowSettingsResponse(BaseModel):
    slide_duration_seconds: int
    refresh_interval_seconds: int
    fade_duration_ms: int = 750
    allow_shuffle: bool = True
    allow_fullscreen: bool = True
