"""Database package for the South Sudan National Registry."""

from .database import (
    Base,
    DATABASE_URL,
    SessionLocal,
    engine,
    get_db,
    get_session,
    init_db,
    check_database_connection,
    check_database_health,
    database_backend,
    get_database_type,
    database_url_configured,
    get_database_url_safe,
)

from .models import (
    AdministrativeUnit,
    AuditLog,
    Citizen,
    CivilEvent,
    Document,
    Household,
    VoterRecord,
)

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
    "AdministrativeUnit",
    "AuditLog",
    "Citizen",
    "CivilEvent",
    "Document",
    "Household",
    "VoterRecord",
]
