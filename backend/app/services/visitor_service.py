import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import generate_access_code, hash_access_code
from app.models.visitor import Visitor


logger = logging.getLogger(__name__)
MAX_ACCESS_CODE_ATTEMPTS = 5


def register_visitor(db: Session, name: str) -> tuple[Visitor, str]:
    for attempt in range(MAX_ACCESS_CODE_ATTEMPTS):
        access_code = generate_access_code()
        visitor = Visitor(name=name, access_code_hash=hash_access_code(access_code))
        db.add(visitor)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            if attempt == MAX_ACCESS_CODE_ATTEMPTS - 1:
                logger.exception("Could not allocate a unique visitor access code")
                raise
            continue

        db.refresh(visitor)
        return visitor, access_code

    raise RuntimeError("Visitor registration exhausted access-code attempts")


def get_visitor_by_access_code(db: Session, access_code: str) -> Visitor | None:
    code_hash = hash_access_code(access_code)
    return db.scalar(
        select(Visitor).where(Visitor.access_code_hash == code_hash)
    )
