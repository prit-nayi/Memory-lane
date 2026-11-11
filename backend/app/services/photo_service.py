import logging
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.datastructures import UploadFile

from app.core.storage import (
    PhotoStorageError,
    StagedPhoto,
    discard_staged_upload,
    finalize_upload,
    remove_upload,
    stage_upload,
)
from app.models.photo import Photo
from app.models.visitor import Visitor


logger = logging.getLogger(__name__)


def upload_photos(
    db: Session, visitor: Visitor, uploads: list[UploadFile]
) -> list[Photo]:
    staged_photos: list[StagedPhoto] = []
    finalized_keys: list[str] = []
    try:
        for upload in uploads:
            staged_photos.append(stage_upload(upload))

        photos = [
            Photo(
                visitor_id=visitor.id,
                original_filename=staged.original_filename,
                storage_key=staged.storage_key,
                content_type=staged.content_type,
                file_size=staged.file_size,
                status="pending",
            )
            for staged in staged_photos
        ]
        for staged in staged_photos:
            finalize_upload(staged)
            finalized_keys.append(staged.storage_key)

        db.add_all(photos)
        db.commit()
        return photos
    except Exception:
        db.rollback()
        _cleanup_failed_uploads(staged_photos, finalized_keys)
        raise


def list_visitor_photos(db: Session, visitor_id: uuid.UUID) -> list[Photo]:
    return list(
        db.scalars(
            select(Photo)
            .where(Photo.visitor_id == visitor_id)
            .order_by(Photo.created_at.desc(), Photo.id)
        )
    )


def get_visitor_photo(
    db: Session, visitor_id: uuid.UUID, photo_id: uuid.UUID
) -> Photo | None:
    return db.scalar(
        select(Photo).where(
            Photo.id == photo_id,
            Photo.visitor_id == visitor_id,
        )
    )


def delete_visitor_photo(db: Session, photo: Photo) -> None:
    if photo.status == "approved":
        raise ValueError("Approved photos cannot be deleted by visitors")

    storage_key = photo.storage_key
    db.delete(photo)
    db.commit()
    remove_upload(storage_key)


def _cleanup_failed_uploads(
    staged_photos: list[StagedPhoto], finalized_keys: list[str]
) -> None:
    for staged in staged_photos:
        try:
            discard_staged_upload(staged)
        except PhotoStorageError:
            logger.exception("Could not clean up staged photo after upload failure")

    for storage_key in finalized_keys:
        try:
            remove_upload(storage_key)
        except PhotoStorageError:
            logger.exception("Could not clean up stored photo after upload failure")
