"""
South Sudan National Registry
Database Service
"""

from __future__ import annotations

from typing import Any

from database.database import (
    check_database_connection,
    database_backend,
    database_url_configured,
    init_db,
)


class DatabaseService:
    """Application-level database operations."""

    @staticmethod
    def initialize() -> dict[str, Any]:
        try:
            init_db()

            health = check_database_connection()

            return {
                "ok": bool(health.get("ok")),
                "backend": database_backend(),
                "configured": database_url_configured(),
                "message": health.get(
                    "message",
                    "Database initialized.",
                ),
            }

        except Exception as exc:

            return {
                "ok": False,
                "backend": database_backend(),
                "configured": database_url_configured(),
                "message": (
                    f"{type(exc).__name__}: {exc}"
                ),
            }

    @staticmethod
    def health() -> dict[str, Any]:
        return check_database_connection()