"""
South Sudan National Registry
Database Configuration

Supports:

    SQLite
    PostgreSQL

The database URL is read from the DATABASE_URL
environment variable.

Example PostgreSQL:

    DATABASE_URL=postgresql+psycopg://user:password@host:5432/registry

Example SQLite:

    DATABASE_URL=sqlite:///registry.db
"""

from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# ============================================================
# DATABASE URL
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_SQLITE_PATH = BASE_DIR / "registry.db"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DEFAULT_SQLITE_PATH}",
)


# ============================================================
# ENGINE
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
# SESSION
# ============================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ============================================================
# BASE MODEL
# ============================================================

Base = declarative_base()


# ============================================================
# DATABASE SESSION
# ============================================================

def get_db():
    """
    Provide a database session.

    Usage:

        db = get_db()
        try:
            ...
        finally:
            db.close()
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db() -> None:
    """
    Create all SQLAlchemy tables.

    Models must be imported before create_all()
    so SQLAlchemy knows about their metadata.
    """

    import models  # noqa: F401

    Base.metadata.create_all(
        bind=engine
    )