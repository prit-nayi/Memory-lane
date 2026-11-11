import logging
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.storage import STORAGE_KEY_PATTERN, get_storage_root
from app.db.session import get_db
from app.models.photo import Photo
from app.schemas.slideshow import (
    SlideshowPhotoResponse,
    SlideshowSettingsResponse,
)
from app.services.slideshow_service import (
    get_slideshow_photo,
    list_slideshow_photos,
)


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/slideshow", tags=["slideshow"])
DatabaseSession = Annotated[Session, Depends(get_db)]
SLIDE_DURATION_SECONDS = 7
REFRESH_INTERVAL_SECONDS = 5


@router.get("/photos", response_model=list[SlideshowPhotoResponse])
def get_slideshow_photos(db: DatabaseSession) -> list[SlideshowPhotoResponse]:
    return [
        SlideshowPhotoResponse(
            id=photo.id,
            original_filename=photo.original_filename,
            content_type=photo.content_type,
            image_url=f"/api/v1/slideshow/photos/{photo.id}/image",
            created_at=photo.created_at,
        )
        for photo in list_slideshow_photos(db)
    ]


@router.get("/photos/{photo_id}/image")
def get_slideshow_image(photo_id: uuid.UUID, db: DatabaseSession) -> Response:
    photo = get_slideshow_photo(db, photo_id)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )

    if not STORAGE_KEY_PATTERN.fullmatch(photo.storage_key):
        logger.error("Photo %s has an invalid storage key", photo_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Photo storage record is invalid",
        )

    image_path = Path(get_storage_root()) / photo.storage_key
    if not image_path.is_file():
        logger.warning("Stored image file is missing for photo %s", photo_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo image is unavailable",
        )

    return FileResponse(
        image_path,
        media_type=photo.content_type,
        headers={
            "Cache-Control": "public, max-age=3600",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.get("/settings", response_model=SlideshowSettingsResponse)
def get_slideshow_settings() -> SlideshowSettingsResponse:
    return SlideshowSettingsResponse(
        slide_duration_seconds=SLIDE_DURATION_SECONDS,
        refresh_interval_seconds=REFRESH_INTERVAL_SECONDS,
    )
