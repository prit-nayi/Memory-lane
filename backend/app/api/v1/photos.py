import logging
import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Header,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_access_code
from app.core.storage import (
    ImageTooLargeError,
    InvalidImageError,
    PhotoStorageError,
    UnsupportedImageError,
)
from app.db.session import get_db
from app.models.visitor import Visitor
from app.schemas.photo import PhotoResponse
from app.services.photo_service import (
    delete_visitor_photo,
    get_visitor_photo,
    list_visitor_photos,
    upload_photos,
)


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/photos", tags=["photos"])
DatabaseSession = Annotated[Session, Depends(get_db)]
AccessCodeHeader = Annotated[
    str, Header(alias="X-Visitor-Access-Code", min_length=16, max_length=19)
]


def _get_authenticated_visitor(db: Session, access_code: str) -> Visitor:
    visitor = db.scalar(
        select(Visitor).where(
            Visitor.access_code_hash == hash_access_code(access_code)
        )
    )
    if visitor is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access code",
        )
    return visitor


@router.post(
    "/upload",
    response_model=list[PhotoResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_photos(
    db: DatabaseSession,
    access_code: AccessCodeHeader,
    files: Annotated[list[UploadFile], File(...)],
) -> list[PhotoResponse]:
    visitor = _get_authenticated_visitor(db, access_code)
    if not files:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Select at least one image",
        )
    if len(files) > settings.max_photos_per_upload:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"No more than {settings.max_photos_per_upload} images may be "
            "uploaded at once",
        )

    try:
        photos = upload_photos(db, visitor, files)
    except ImageTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=str(exc),
        ) from exc
    except UnsupportedImageError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(exc),
        ) from exc
    except InvalidImageError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    except (PhotoStorageError, SQLAlchemyError) as exc:
        logger.exception("Could not save visitor photo upload")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save uploaded images",
        ) from exc
    return [PhotoResponse.model_validate(photo) for photo in photos]


@router.get("/my-photos", response_model=list[PhotoResponse])
def get_my_photos(
    db: DatabaseSession, access_code: AccessCodeHeader
) -> list[PhotoResponse]:
    visitor = _get_authenticated_visitor(db, access_code)
    return [
        PhotoResponse.model_validate(photo)
        for photo in list_visitor_photos(db, visitor.id)
    ]


@router.get("/{photo_id}", response_model=PhotoResponse)
def get_photo(
    photo_id: uuid.UUID,
    db: DatabaseSession,
    access_code: AccessCodeHeader,
) -> PhotoResponse:
    visitor = _get_authenticated_visitor(db, access_code)
    photo = get_visitor_photo(db, visitor.id, photo_id)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )
    return PhotoResponse.model_validate(photo)


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(
    photo_id: uuid.UUID,
    db: DatabaseSession,
    access_code: AccessCodeHeader,
) -> None:
    visitor = _get_authenticated_visitor(db, access_code)
    photo = get_visitor_photo(db, visitor.id, photo_id)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )
    try:
        delete_visitor_photo(db, photo)
    except (PhotoStorageError, SQLAlchemyError) as exc:
        logger.exception("Could not delete visitor photo %s", photo_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete photo",
        ) from exc
