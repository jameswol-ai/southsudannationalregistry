"""
Database configuration for the South Sudan National Registry.

Development:
    SQLite is used automatically when DATABASE_URL is not supplied.

Production:
    Set DATABASE_URL to a PostgreSQL connection string, for example:

    postgresql+psycopg://user:password@host:5432/registry

The rest of the application uses SQLAlchemy and does not depend on
a specific database engine.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

DEFAULT_SQLITE_URL = (
    f"sqlite:///{DATA_DIR / 'registry.db'}"
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    DEFAULT_SQLITE_URL,
).strip()


# ============================================================
# SQLALCHEMY ENGINE
# ============================================================

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False,
    }

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)


# ============================================================
# BASE MODEL
# ============================================================

class Base(DeclarativeBase):
    """Base class for all registry ORM models."""

    pass


# ============================================================
# SESSION
# ============================================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    Yield a database session.

    Intended for service-layer use and FastAPI dependency injection.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# INITIALIZATION
# ============================================================

def init_db() -> None:
    """
    Create all database tables.

    For production PostgreSQL deployments, Alembic migrations should
    eventually replace create_all().
    """

    # Import models before create_all so SQLAlchemy knows all tables.
    from . import models  # noqa: F401

    Base.metadata.create_all(
        bind=engine,
    )
