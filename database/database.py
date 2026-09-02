"""
South Sudan National Registry
Database Configuration
"""

from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


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

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)


if not DATABASE_URL:

    DATABASE_URL = (
        "sqlite:///"
        + str(
            DATA_DIR
            / "registry.db"
        )
    )


# ============================================================
# SQLITE OPTIONS
# ============================================================

connect_args = {}

if DATABASE_URL.startswith(
    "sqlite"
):

    connect_args = {
        "check_same_thread": False,
    }


# ============================================================
# ENGINE
# ============================================================

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)


# ============================================================
# SESSION
# ============================================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# ============================================================
# BASE
# ============================================================

class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base.
    """

    pass


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db() -> None:
    """
    Create all registered SQLAlchemy tables.

    Models are imported here so that they are registered
    before create_all() executes.
    """

    try:

        from database.models import Base as ModelsBase

        ModelsBase.metadata.create_all(
            bind=engine
        )

        return

    except ImportError:

        pass


    # Fallback to this module's Base.

    Base.metadata.create_all(
        bind=engine
    )


# ============================================================
# SESSION DEPENDENCY
# ============================================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()
