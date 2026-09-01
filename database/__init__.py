"""
South Sudan National Registry
Database package.

Public database interface:

    Base
    DATABASE_URL
    SessionLocal
    engine
    get_db
    init_db
    check_database_connection
    get_database_type
    get_database_url_safe
"""

from .database import (
    Base,
    DATABASE_URL,
    SessionLocal,
    check_database_connection,
    engine,
    get_database_type,
    get_database_url_safe,
    get_db,
    init_db,
)


# ============================================================
# ORM MODELS
# ============================================================

from .models import (
    AdministrativeUnit,
    AuditLog,
    Citizen,
    CivilEvent,
    Document,
    Household,
    VoterRecord,
)


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    # Database
    "Base",
    "DATABASE_URL",
    "SessionLocal",
    "engine",
    "get_db",
    "init_db",
    "check_database_connection",
    "get_database_type",
    "get_database_url_safe",

    # Models
    "AdministrativeUnit",
    "AuditLog",
    "Citizen",
    "CivilEvent",
    "Document",
    "Household",
    "VoterRecord",
]
