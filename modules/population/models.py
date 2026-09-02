"""
Population module models.

Exports the database models used by the population module.
"""

from database.models import (
    Citizen,
    Household,
    AdministrativeUnit,
)

__all__ = [
    "Citizen",
    "Household",
    "AdministrativeUnit",
]
