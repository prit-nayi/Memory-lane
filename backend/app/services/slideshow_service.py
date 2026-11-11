import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.photo import Photo


def list_slideshow_photos(db: Session, visitor_id: uuid.UUID) -> list[Photo]:
    return list(
        db.scalars(
            select(Photo)
            .where(Photo.visitor_id == visitor_id)
            .order_by(Photo.created_at, Photo.id)
        )
    )


def get_slideshow_photo(
    db: Session, visitor_id: uuid.UUID, photo_id: uuid.UUID
) -> Photo | None:
    return db.scalar(
        select(Photo).where(
            Photo.id == photo_id,
            Photo.visitor_id == visitor_id,
        )
    )
