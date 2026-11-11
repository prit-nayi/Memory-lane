import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.photo import Photo


def list_slideshow_photos(db: Session) -> list[Photo]:
    return list(
        db.scalars(select(Photo).order_by(Photo.created_at, Photo.id))
    )


def get_slideshow_photo(db: Session, photo_id: uuid.UUID) -> Photo | None:
    return db.get(Photo, photo_id)
