import logging

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.visitors import router as visitors_router
from app.db.session import get_db


logger = logging.getLogger(__name__)

app = FastAPI(
    title="Memory Lane API",
    description="Visitor photo slideshow application",
    version="1.0.0",
)
app.include_router(visitors_router)


@app.get("/")
def root():
    return {"message": "Welcome to Memory Lane API"}


@app.get("/health")
def health():
    return {"status": "healthy", "application": "Memory Lane"}


@app.get("/health/database")
def database_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.exception("Database health check failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        ) from exc
    return {"status": "healthy", "database": "connected"}