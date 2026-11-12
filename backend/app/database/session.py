import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


def get_db():
    db = SessionLocal()

    try:
        yield db

    except Exception:
        logger.exception("Database session error")
        db.rollback()
        raise

    finally:
        db.close()