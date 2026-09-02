"""
Civil Registration module models.

Exports the database models used by the civil registration module.
"""

from database.models import (
    CivilEvent,
    Citizen,
    Document,
)

__all__ = [
    "CivilEvent",
    "Citizen",
    "Document",
]
