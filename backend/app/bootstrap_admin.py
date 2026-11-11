import logging

from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_admin_password
from app.db.session import SessionLocal
from app.models.admin_user import AdminUser


logger = logging.getLogger(__name__)


def bootstrap_admin() -> None:
    username = (settings.admin_username or "").strip()
    password = settings.admin_password or ""
    token_secret = settings.admin_token_secret or ""
    if not username:
        raise ValueError("Set ADMIN_USERNAME before bootstrapping the administrator")
    if len(password) < 12:
        raise ValueError("ADMIN_PASSWORD must contain at least 12 characters")
    if len(token_secret) < 32:
        raise ValueError("ADMIN_TOKEN_SECRET must contain at least 32 characters")

    db = SessionLocal()
    try:
        admin = db.scalar(
            select(AdminUser).where(AdminUser.username == username)
        )
        if admin is None:
            admin = AdminUser(username=username, password_hash="")
            db.add(admin)
        admin.password_hash = hash_admin_password(password)
        admin.is_active = True
        db.commit()
        logger.info("Bootstrapped administrator account %s", username)
    except Exception:
        db.rollback()
        logger.exception("Could not bootstrap administrator account")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bootstrap_admin()
