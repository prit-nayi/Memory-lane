import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.photo import Photo
from app.models.slideshow_settings import SlideshowSettings
from app.models.visitor import Visitor


DEFAULT_SLIDESHOW_SETTINGS = {
    "slide_duration_seconds": 7,
    "refresh_interval_seconds": 5,
    "fade_duration_ms": 750,
    "allow_shuffle": True,
    "allow_fullscreen": True,
}


def get_dashboard_counts(db: Session) -> dict[str, int]:
    total_visitors = db.scalar(select(func.count()).select_from(Visitor)) or 0
    active_visitors = db.scalar(
        select(func.count()).select_from(Visitor).where(Visitor.is_active.is_(True))
    ) or 0
    total_photos = db.scalar(select(func.count()).select_from(Photo)) or 0
    return {
        "total_visitors": total_visitors,
        "active_visitors": active_visitors,
        "total_photos": total_photos,
    }


def list_admin_visitors(db: Session) -> list[dict]:
    rows = db.execute(
        select(
            Visitor.id,
            Visitor.name,
            Visitor.is_active,
            Visitor.created_at,
            func.count(Photo.id).label("photo_count"),
        )
        .outerjoin(Photo, Photo.visitor_id == Visitor.id)
        .group_by(Visitor.id)
        .order_by(Visitor.created_at.desc(), Visitor.id)
    ).all()
    return [
        {
            "id": row.id,
            "name": row.name,
            "is_active": row.is_active,
            "created_at": row.created_at,
            "photo_count": row.photo_count,
        }
        for row in rows
    ]


def get_admin_photo(db: Session, photo_id: uuid.UUID) -> Photo | None:
    return db.scalar(
        select(Photo)
        .options(joinedload(Photo.visitor))
        .where(Photo.id == photo_id)
    )


def list_admin_photos(
    db: Session, visitor_id: uuid.UUID | None = None
) -> list[Photo]:
    statement = select(Photo).options(joinedload(Photo.visitor))
    if visitor_id is not None:
        statement = statement.where(Photo.visitor_id == visitor_id)
    return list(
        db.scalars(
            statement.order_by(Photo.created_at.desc(), Photo.id)
        )
    )


def get_slideshow_settings(db: Session) -> SlideshowSettings:
    record = db.get(SlideshowSettings, 1)
    if record is not None:
        return record
    return SlideshowSettings(id=1, **DEFAULT_SLIDESHOW_SETTINGS)


def update_slideshow_settings(
    db: Session, values: dict
) -> SlideshowSettings:
    record = db.get(SlideshowSettings, 1)
    if record is None:
        record = SlideshowSettings(id=1, **values)
        db.add(record)
    else:
        for key, value in values.items():
            setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record
