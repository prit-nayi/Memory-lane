from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_admin_token_username, hash_access_code
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.models.visitor import Visitor


DatabaseSession = Annotated[Session, Depends(get_db)]
AccessCodeHeader = Annotated[
    str, Header(alias="X-Visitor-Access-Code", min_length=16, max_length=19)
]


def get_authenticated_visitor(
    db: DatabaseSession, access_code: AccessCodeHeader
) -> Visitor:
    visitor = db.scalar(
        select(Visitor).where(
            Visitor.access_code_hash == hash_access_code(access_code)
        )
    )
    if visitor is None or not visitor.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access code",
        )
    return visitor


AuthenticatedVisitor = Annotated[
    Visitor, Depends(get_authenticated_visitor)
]

AdminBearer = HTTPBearer(auto_error=False)


def get_authenticated_admin(
    db: DatabaseSession,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(AdminBearer)
    ],
) -> AdminUser:
    if not settings.admin_token_secret or len(settings.admin_token_secret) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin authentication is not configured",
        )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = get_admin_token_username(
        credentials.credentials, settings.admin_token_secret
    )
    admin = (
        db.scalar(
            select(AdminUser).where(
                AdminUser.username == username,
                AdminUser.is_active.is_(True),
            )
        )
        if username
        else None
    )
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired admin session",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return admin


AuthenticatedAdmin = Annotated[AdminUser, Depends(get_authenticated_admin)]
