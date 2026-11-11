import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.dependencies import (
    AuthenticatedAdmin,
    DatabaseSession,
)
from app.core.config import settings
from app.core.security import (
    create_admin_access_token,
    hash_admin_password,
    verify_admin_password,
)
from app.core.storage import PhotoStorageError
from app.models.admin_user import AdminUser
from app.models.photo import Photo
from app.models.visitor import Visitor
from app.schemas.admin import (
    AdminDashboardResponse,
    AdminLoginRequest,
    AdminLoginResponse,
    AdminPhotoResponse,
    AdminVisitorResponse,
    AdminVisitorUpdateRequest,
    SlideshowSettingsResponse,
    SlideshowSettingsUpdate,
)
from app.services.admin_service import (
    get_admin_photo,
    get_dashboard_counts,
    get_slideshow_settings,
    list_admin_photos,
    list_admin_visitors,
    update_slideshow_settings,
)
from app.services.photo_service import delete_visitor_photo
from app.services.websocket_manager import broadcast_slideshow_update


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
DummyPasswordHash = hash_admin_password("invalid-login-timing-placeholder")


@router.post("/login", response_model=AdminLoginResponse)
def admin_login(
    request: AdminLoginRequest, db: DatabaseSession
) -> AdminLoginResponse:
    if not settings.admin_token_secret or len(settings.admin_token_secret) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin authentication is not configured",
        )

    admin = db.scalar(
        select(AdminUser).where(
            AdminUser.username == request.username.strip(),
            AdminUser.is_active.is_(True),
        )
    )
    password_hash = admin.password_hash if admin is not None else DummyPasswordHash
    valid_password = verify_admin_password(request.password, password_hash)
    if admin is None or not valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    try:
        token = create_admin_access_token(
            admin.username,
            settings.admin_token_secret,
            settings.admin_token_expire_minutes,
        )
    except ValueError as exc:
        logger.exception("Admin token configuration is invalid")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin authentication is not configured",
        ) from exc

    return AdminLoginResponse(
        access_token=token,
        expires_in=settings.admin_token_expire_minutes * 60,
    )


@router.get("/dashboard", response_model=AdminDashboardResponse)
def admin_dashboard(
    db: DatabaseSession, admin: AuthenticatedAdmin
) -> AdminDashboardResponse:
    return AdminDashboardResponse(**get_dashboard_counts(db))


@router.get("/visitors", response_model=list[AdminVisitorResponse])
def admin_visitors(
    db: DatabaseSession, admin: AuthenticatedAdmin
) -> list[AdminVisitorResponse]:
    return [
        AdminVisitorResponse(**visitor)
        for visitor in list_admin_visitors(db)
    ]


@router.patch(
    "/visitors/{visitor_id}", response_model=AdminVisitorResponse
)
def update_visitor_status(
    visitor_id: uuid.UUID,
    request: AdminVisitorUpdateRequest,
    db: DatabaseSession,
    admin: AuthenticatedAdmin,
    background_tasks: BackgroundTasks,
) -> AdminVisitorResponse:
    visitor = db.get(Visitor, visitor_id)
    if visitor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visitor not found",
        )
    visitor.is_active = request.is_active
    try:
        db.commit()
        db.refresh(visitor)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Could not update visitor %s status", visitor_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update visitor",
        ) from exc

    background_tasks.add_task(broadcast_slideshow_update)
    photo_count = db.scalar(
        select(func.count()).select_from(Photo).where(
            Photo.visitor_id == visitor.id
        )
    )
    return AdminVisitorResponse(
        id=visitor.id,
        name=visitor.name,
        is_active=visitor.is_active,
        photo_count=int(photo_count or 0),
        created_at=visitor.created_at,
    )


@router.get("/photos", response_model=list[AdminPhotoResponse])
def admin_photos(
    db: DatabaseSession,
    admin: AuthenticatedAdmin,
    visitor_id: Annotated[uuid.UUID | None, Query()] = None,
) -> list[AdminPhotoResponse]:
    return [
        AdminPhotoResponse(
            id=photo.id,
            visitor_id=photo.visitor_id,
            visitor_name=photo.visitor.name,
            original_filename=photo.original_filename,
            content_type=photo.content_type,
            file_size=photo.file_size,
            created_at=photo.created_at,
        )
        for photo in list_admin_photos(db, visitor_id)
    ]


@router.delete(
    "/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_admin_photo(
    photo_id: uuid.UUID,
    db: DatabaseSession,
    admin: AuthenticatedAdmin,
    background_tasks: BackgroundTasks,
) -> None:
    photo = get_admin_photo(db, photo_id)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )
    try:
        delete_visitor_photo(db, photo)
    except (PhotoStorageError, SQLAlchemyError) as exc:
        logger.exception("Admin could not delete photo %s", photo_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete photo",
        ) from exc
    background_tasks.add_task(broadcast_slideshow_update)


@router.get("/settings", response_model=SlideshowSettingsResponse)
def admin_get_settings(
    db: DatabaseSession, admin: AuthenticatedAdmin
) -> SlideshowSettingsResponse:
    return SlideshowSettingsResponse.model_validate(
        get_slideshow_settings(db)
    )


@router.put("/settings", response_model=SlideshowSettingsResponse)
def admin_update_settings(
    request: SlideshowSettingsUpdate,
    db: DatabaseSession,
    admin: AuthenticatedAdmin,
) -> SlideshowSettingsResponse:
    try:
        settings_record = update_slideshow_settings(
            db, request.model_dump()
        )
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Could not update slideshow settings")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update slideshow settings",
        ) from exc
    return SlideshowSettingsResponse.model_validate(settings_record)
