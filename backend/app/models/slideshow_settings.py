from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class SlideshowSettings(Base):
    __tablename__ = "slideshow_settings"
    __table_args__ = (
        CheckConstraint(
            "slide_duration_seconds BETWEEN 3 AND 30",
            name="ck_slideshow_settings_slide_duration",
        ),
        CheckConstraint(
            "refresh_interval_seconds BETWEEN 5 AND 300",
            name="ck_slideshow_settings_refresh_interval",
        ),
        CheckConstraint(
            "fade_duration_ms BETWEEN 250 AND 2000",
            name="ck_slideshow_settings_fade_duration",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    slide_duration_seconds: Mapped[int] = mapped_column(
        Integer, nullable=False, default=7, server_default="7"
    )
    refresh_interval_seconds: Mapped[int] = mapped_column(
        Integer, nullable=False, default=5, server_default="5"
    )
    fade_duration_ms: Mapped[int] = mapped_column(
        Integer, nullable=False, default=750, server_default="750"
    )
    allow_shuffle: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    allow_fullscreen: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
