"""
South Sudan National Registry
Production Database Configuration

Supports:
    - Neon / PostgreSQL in production
    - SQLite for local development

Production database configuration is supplied through the
DATABASE_URL environment variable or Streamlit secrets.
Never commit database credentials to GitHub.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# DATABASE URL
# ============================================================


def _read_database_url() -> str | None:
    """Read DATABASE_URL from environment or Streamlit secrets."""
    value = os.getenv("DATABASE_URL")

    if value:
        return value.strip()

    # Streamlit Cloud exposes root-level secrets as environment
    # variables, but this fallback also supports direct st.secrets use.
    try:
        import streamlit as st

        secret = st.secrets.get("DATABASE_URL")
        if secret:
            return str(secret).strip()
    except Exception:
        pass

    return None


def _normalise_database_url(url: str) -> str:
    """Normalise common PostgreSQL URLs for SQLAlchemy."""
    url = url.strip()

    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]

    # Neon connection strings normally already contain sslmode=require.
    # Do not alter an explicitly supplied SSL configuration.
    if url.startswith("postgresql://") and "sslmode=" not in url:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}sslmode=require"

    return url


_configured_database_url = _read_database_url()

if _configured_database_url:
    DATABASE_URL = _normalise_database_url(_configured_database_url)
else:
    DATABASE_URL = "sqlite:///" + str(DATA_DIR / "registry.db")


IS_POSTGRESQL = DATABASE_URL.startswith(("postgresql://", "postgresql+"))
IS_SQLITE = DATABASE_URL.startswith("sqlite://")


# ============================================================
# ENGINE CONFIGURATION
# ============================================================

connect_args: dict[str, Any] = {}
engine_options: dict[str, Any] = {
    "pool_pre_ping": True,
}

if IS_SQLITE:
    connect_args = {"check_same_thread": False}

if IS_POSTGRESQL:
    # Neon may suspend compute between requests. Keep stale connections
    # from surfacing as application errors and recycle connections that
    # have been idle for a while.
    engine_options.update(
        {
            "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "5")),
            "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "1800")),
        }
    )


engine: Engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    **engine_options,
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
    """SQLAlchemy declarative base."""

    pass


# ============================================================
# DATABASE INITIALIZATION
# ============================================================


def init_db() -> None:
    """
    Create all registered SQLAlchemy tables.

    This is intentionally idempotent and safe to call during application
    startup. It does not delete or alter existing records.

    For future production schema evolution, use Alembic migrations rather
    than relying on create_all() for structural changes.
    """
    from database.models import Base as ModelsBase

    ModelsBase.metadata.create_all(bind=engine)


# ============================================================
# HEALTH CHECK
# ============================================================


def check_database_health() -> dict[str, Any]:
    """
    Verify that the configured database can accept a simple query.

    Returns a serialisable status dictionary suitable for Streamlit,
    FastAPI, logs, or an administration dashboard.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "ok": True,
            "database": database_backend(),
            "url_configured": bool(_configured_database_url),
            "message": "Database connection is healthy.",
        }
    except Exception as exc:
        return {
            "ok": False,
            "database": database_backend(),
            "url_configured": bool(_configured_database_url),
            "message": f"{type(exc).__name__}: {exc}",
        }


def database_backend() -> str:
    """Return a safe, human-readable database backend name."""
    if IS_POSTGRESQL:
        return "PostgreSQL / Neon"
    if IS_SQLITE:
        return "SQLite (local development)"
    return "Configured SQL database"


def database_url_configured() -> bool:
    """Return True when an external DATABASE_URL was supplied."""
    return bool(_configured_database_url)


# ============================================================
# SESSION DEPENDENCY
# ============================================================


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
