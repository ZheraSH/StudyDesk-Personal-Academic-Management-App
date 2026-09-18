"""
Database connection management.
Provides a SQLAlchemy engine, session factory, and context manager.
All database operations go through get_db().
"""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.config.settings import DB_PATH

logger = logging.getLogger(__name__)

# ─────────────────────────── Engine Setup ────────────────────────────

def _create_engine() -> Engine:
    db_url = f"sqlite:///{DB_PATH}"
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        echo=False,  # Set True for SQL debugging
    )
    return engine


_engine: Engine | None = None
_SessionFactory: sessionmaker | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = _create_engine()
        _enable_wal_mode(_engine)
        _enable_foreign_keys(_engine)
    return _engine


def _enable_wal_mode(engine: Engine) -> None:
    """Enable Write-Ahead Logging for better concurrency."""
    with engine.connect() as conn:
        conn.execute(__import__("sqlalchemy").text("PRAGMA journal_mode=WAL"))
        conn.commit()


def _enable_foreign_keys(engine: Engine) -> None:
    """SQLite requires this pragma per connection to enforce FK constraints."""
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_session_factory() -> sessionmaker:
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            autoflush=True,
        )
    return _SessionFactory


# ─────────────────────────── Context Manager ─────────────────────────

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Provide a transactional database session.
    Commits on success, rolls back on exception.

    Usage:
        with get_db() as session:
            result = session.query(Model).all()
    """
    factory = get_session_factory()
    session: Session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ─────────────────────────── Initialization ──────────────────────────

def init_db() -> None:
    """Create all tables if they don't exist. Safe to call on every startup."""
    from src.database.models.base import Base  # noqa: F401 — import triggers all models

    # Import all models so SQLAlchemy knows about them
    import src.database.models.semester       # noqa: F401
    import src.database.models.course         # noqa: F401
    import src.database.models.schedule       # noqa: F401
    import src.database.models.task           # noqa: F401
    import src.database.models.task_checklist # noqa: F401
    import src.database.models.reminder       # noqa: F401
    import src.database.models.attachment     # noqa: F401
    import src.database.models.focus_session  # noqa: F401
    import src.database.models.app_setting    # noqa: F401

    engine = get_engine()
    Base.metadata.create_all(engine)
    logger.info("Database initialized at %s", DB_PATH)
