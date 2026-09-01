"""
Database configuration for the South Sudan National Registry.

Development
-----------
SQLite is used automatically when DATABASE_URL is not supplied.

Production
----------
Set DATABASE_URL to a PostgreSQL connection string.

Examples:

    postgresql://user:password@host:5432/registry

    postgresql+psycopg2://user:password@host:5432/registry

    postgresql+psycopg://user:password@host:5432/registry

The application uses SQLAlchemy and does not depend on a
specific database engine.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# DATABASE URL
# ============================================================

DEFAULT_SQLITE_URL = (
    f"sqlite:///{DATA_DIR / 'registry.db'}"
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    DEFAULT_SQLITE_URL,
).strip()


if not DATABASE_URL:
    DATABASE_URL = DEFAULT_SQLITE_URL


# ============================================================
# SQLITE CONFIGURATION
# ============================================================

connect_args: dict[str, object] = {}

if DATABASE_URL.startswith("sqlite"):

    connect_args = {
        "check_same_thread": False,
    }


# ============================================================
# SQLALCHEMY ENGINE
# ============================================================

engine_kwargs: dict[str, object] = {
    "pool_pre_ping": True,
}


# SQLite-specific settings
if connect_args:

    engine_kwargs["connect_args"] = connect_args


# PostgreSQL-specific settings
#
# PostgreSQL connection pools are useful for the Registry API,
# Streamlit and other application processes sharing the database.
if DATABASE_URL.startswith("postgresql"):

    engine_kwargs["pool_size"] = int(
        os.getenv(
            "DATABASE_POOL_SIZE",
            "5",
        )
    )

    engine_kwargs["max_overflow"] = int(
        os.getenv(
            "DATABASE_MAX_OVERFLOW",
            "10",
        )
    )


engine = create_engine(
    DATABASE_URL,
    **engine_kwargs,
)


# ============================================================
# BASE MODEL
# ============================================================

class Base(DeclarativeBase):
    """
    Base class for all registry ORM models.
    """

    pass


# ============================================================
# SESSION FACTORY
# ============================================================

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db() -> Generator[Session, None, None]:
    """
    Yield a SQLAlchemy database session.

    Suitable for:

        - Service-layer operations
        - FastAPI dependency injection
        - Streamlit operations
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
    Create all registered database tables.

    SQLAlchemy's create_all() is intentionally used here for the
    current development/alpha stage.

    Production deployments should eventually use Alembic migrations.
    """

    # Import models before create_all().
    #
    # This ensures all ORM classes have been registered with Base.metadata.
    from . import models  # noqa: F401

    Base.metadata.create_all(
        bind=engine,
    )


# ============================================================
# DATABASE HEALTH CHECK
# ============================================================

def check_database_connection() -> bool:
    """
    Test whether the configured database is reachable.

    Returns:
        True when the connection succeeds.
        False when the connection fails.
    """

    try:

        with engine.connect():

            return True

    except Exception:

        return False


# ============================================================
# DATABASE INFORMATION
# ============================================================

def get_database_type() -> str:
    """
    Return a human-readable database engine name.
    """

    if DATABASE_URL.startswith("sqlite"):

        return "SQLite"

    if DATABASE_URL.startswith("postgresql"):

        return "PostgreSQL"

    return "SQLAlchemy Database"


def get_database_url_safe() -> str:
    """
    Return the database URL with credentials hidden.

    This is intended for administration/status displays.
    """

    value = DATABASE_URL

    if "@" not in value:

        return value

    prefix, suffix = value.rsplit(
        "@",
        1,
    )

    if "://" not in prefix:

        return value

    scheme, credentials = prefix.split(
        "://",
        1,
    )

    if ":" in credentials:

        username = credentials.split(
            ":",
            1,
        )[0]

        return (
            f"{scheme}://"
            f"{username}:********@"
            f"{suffix}"
        )

    return value
