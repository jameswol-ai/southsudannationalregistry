"""
South Sudan National Registry
Database Configuration

Supports:
    - SQLite for local development
    - PostgreSQL / Neon for production
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Generator
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_SQLITE_PATH = (
    BASE_DIR / "data" / "registry.db"
)

DEFAULT_SQLITE_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)


def _read_database_url() -> str:
    """
    Read DATABASE_URL from environment or
    Streamlit secrets.

    Falls back to SQLite for local development.
    """

    value = os.getenv(
        "DATABASE_URL",
        "",
    ).strip()

    if value:
        return value

    try:
        import streamlit as st

        value = str(
            st.secrets.get(
                "DATABASE_URL",
                "",
            )
        ).strip()

        if value:
            return value

    except Exception:
        pass

    return (
        f"sqlite:///{DEFAULT_SQLITE_PATH}"
    )


def _normalize_database_url(
    url: str,
) -> str:

    if url.startswith("postgres://"):
        url = (
            "postgresql+psycopg://"
            + url[len("postgres://"):]
        )

    elif url.startswith("postgresql://"):
        url = (
            "postgresql+psycopg://"
            + url[len("postgresql://"):]
        )

    if (
        url.startswith("postgresql")
        and "sslmode=" not in url
    ):
        separator = (
            "&"
            if "?" in url
            else "?"
        )

        url = (
            f"{url}"
            f"{separator}"
            f"sslmode=require"
        )

    return url


DATABASE_URL = _normalize_database_url(
    _read_database_url()
)


connect_args: dict[str, object] = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args[
        "check_same_thread"
    ] = False


engine: Engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[
    Session,
    None,
    None,
]:
    """
    Dependency-style database session.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def get_session() -> Session:
    """
    Return an independent database session.

    Modules can use this when they are not
    running inside FastAPI dependency injection.
    """

    return SessionLocal()


def init_db() -> None:
    """
    Import ORM models and create missing tables.

    Existing tables are preserved.
    """

    import database.models  # noqa: F401

    Base.metadata.create_all(
        bind=engine
    )


def check_database_connection() -> dict[str, object]:
    """
    Test the database connection.
    """

    try:

        with engine.connect() as connection:

            connection.execute(
                text("SELECT 1")
            )

        return {
            "ok": True,
            "message":
                "Database connection is healthy.",
        }

    except Exception as exc:

        return {
            "ok": False,
            "message":
                f"{type(exc).__name__}: {exc}",
        }


def check_database_health() -> dict[str, object]:
    return check_database_connection()


def database_backend() -> str:
    return engine.dialect.name


def get_database_type() -> str:
    return database_backend()


def database_url_configured() -> bool:
    return bool(
        os.getenv(
            "DATABASE_URL",
            "",
        ).strip()
    )


def get_database_url_safe() -> str:
    """
    Return the database URL without exposing
    the password.
    """

    try:

        parsed = urlsplit(
            DATABASE_URL
        )

        if (
            not parsed.netloc
            or "@"
            not in parsed.netloc
        ):
            return DATABASE_URL

        credentials, host = (
            parsed.netloc.rsplit(
                "@",
                1,
            )
        )

        username = credentials.split(
            ":",
            1,
        )[0]

        safe_netloc = (
            f"{username}:***@{host}"
        )

        return urlunsplit(
            (
                parsed.scheme,
                safe_netloc,
                parsed.path,
                parsed.query,
                parsed.fragment,
            )
        )

    except Exception:
        return "<database-url-unavailable>"


__all__ = [
    "Base",
    "DATABASE_URL",
    "SessionLocal",
    "engine",
    "get_db",
    "get_session",
    "init_db",
    "check_database_connection",
    "check_database_health",
    "database_backend",
    "get_database_type",
    "database_url_configured",
    "get_database_url_safe",
]