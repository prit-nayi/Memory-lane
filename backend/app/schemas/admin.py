import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AdminLoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=256)


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AdminDashboardResponse(BaseModel):
    total_visitors: int
    active_visitors: int
    total_photos: int


class AdminVisitorResponse(BaseModel):
    id: uuid.UUID
    name: str
    is_active: bool
    photo_count: int
    created_at: datetime


class AdminVisitorUpdateRequest(BaseModel):
    is_active: bool


class AdminPhotoResponse(BaseModel):
    id: uuid.UUID
    visitor_id: uuid.UUID
    visitor_name: str
    original_filename: str
    content_type: str
    file_size: int
    created_at: datetime


class SlideshowSettingsBase(BaseModel):
    slide_duration_seconds: int = Field(ge=3, le=30)
    refresh_interval_seconds: int = Field(ge=5, le=300)
    fade_duration_ms: int = Field(ge=250, le=2000, multiple_of=250)
    allow_shuffle: bool
    allow_fullscreen: bool


class SlideshowSettingsUpdate(SlideshowSettingsBase):
    pass


class SlideshowSettingsResponse(SlideshowSettingsBase):
    model_config = ConfigDict(from_attributes=True)

    updated_at: datetime | None = None
