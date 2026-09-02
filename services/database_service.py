"""
South Sudan National Registry
Central Database Service
"""

from __future__ import annotations

from typing import Any

from database.database import (
    check_database_connection,
    database_backend,
    database_url_configured,
    get_database_url_safe,
    get_session,
    init_db,
)


class DatabaseService:
    """
    Application-level database operations.

    Modules should not need to understand how
    PostgreSQL, Neon or SQLite is configured.
    """

    @staticmethod
    def initialize() -> dict[str, Any]:

        try:

            init_db()

            health = (
                check_database_connection()
            )

            return {
                "ok": bool(
                    health.get("ok")
                ),
                "backend":
                    database_backend(),
                "configured":
                    database_url_configured(),
                "url":
                    get_database_url_safe(),
                "message":
                    str(
                        health.get(
                            "message",
                            "Database initialized.",
                        )
                    ),
            }

        except Exception as exc:

            return {
                "ok": False,
                "backend":
                    database_backend(),
                "configured":
                    database_url_configured(),
                "url":
                    get_database_url_safe(),
                "message":
                    f"{type(exc).__name__}: {exc}",
            }

    @staticmethod
    def health() -> dict[str, Any]:

        return {
            **check_database_connection(),
            "backend":
                database_backend(),
            "configured":
                database_url_configured(),
            "url":
                get_database_url_safe(),
        }

    @staticmethod
    def session():
        """
        Create a database session for a module.
        """

        return get_session()