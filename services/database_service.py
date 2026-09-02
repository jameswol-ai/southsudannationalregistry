"""Application-level database service."""

from __future__ import annotations

from typing import Any

from database.database import (
    check_database_connection,
    database_backend,
    database_url_configured,
    get_database_url_safe,
    init_db,
)


class DatabaseService:
    """Central database lifecycle and health operations."""

    @staticmethod
    def initialize() -> dict[str, Any]:
        try:
            init_db()
            health = check_database_connection()
            return {
                "ok": bool(health.get("ok")),
                "backend": database_backend(),
                "configured": database_url_configured(),
                "url": get_database_url_safe(),
                "message": str(health.get("message", "Database initialized.")),
            }
        except Exception as exc:
            return {
                "ok": False,
                "backend": database_backend(),
                "configured": database_url_configured(),
                "url": get_database_url_safe(),
                "message": f"{type(exc).__name__}: {exc}",
            }

    @staticmethod
    def health() -> dict[str, Any]:
        return {
            **check_database_connection(),
            "backend": database_backend(),
            "configured": database_url_configured(),
            "url": get_database_url_safe(),
        }
