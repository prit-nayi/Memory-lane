from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.visitor import (
    VisitorRegistrationRequest,
    VisitorRegistrationResponse,
    VisitorResponse,
    VisitorVerificationRequest,
)
from app.services.visitor_service import get_visitor_by_access_code, register_visitor


router = APIRouter(prefix="/api/v1/visitors", tags=["visitors"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/register",
    response_model=VisitorRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_visitor(
    request: VisitorRegistrationRequest, db: DatabaseSession
) -> VisitorRegistrationResponse:
    visitor, access_code = register_visitor(db, request.name)
    visitor_data = VisitorResponse.model_validate(visitor).model_dump()
    return VisitorRegistrationResponse(
        **visitor_data,
        access_code=access_code,
    )


@router.post("/verify", response_model=VisitorResponse)
def verify_visitor(
    request: VisitorVerificationRequest, db: DatabaseSession
) -> VisitorResponse:
    visitor = get_visitor_by_access_code(db, request.access_code)
    if visitor is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access code",
        )
    return VisitorResponse.model_validate(visitor)


@router.get("/me", response_model=VisitorResponse)
def get_current_visitor(
    db: DatabaseSession,
    access_code: Annotated[
        str,
        Header(alias="X-Visitor-Access-Code", min_length=16, max_length=19),
    ],
) -> VisitorResponse:
    visitor = get_visitor_by_access_code(db, access_code)
    if visitor is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access code",
        )
    return VisitorResponse.model_validate(visitor)
