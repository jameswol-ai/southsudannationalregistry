"""
Civil Registration service layer.

South Sudan National Registry

Business logic belongs here.
The Streamlit views should not communicate directly
with SQLAlchemy repositories.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Optional
from uuid import uuid4

from modules.civil_registration.repository import (
    archive_event,
    count_events,
    create_event,
    get_event_by_id,
    get_event_by_reference,
    get_event_counts_by_type,
    list_events,
    search_citizens_by_name_or_national_id,
    update_event,
)


# ============================================================
# HELPERS
# ============================================================

def _clean_optional(value: Any) -> Optional[str]:
    """Normalize optional string values."""
    if value is None:
        return None

    value = str(value).strip()

    return value or None


def _clean_required(value: Any) -> str:
    """Normalize required string values."""
    if value is None:
        return ""

    return str(value).strip()


# ============================================================
# VALIDATION
# ============================================================

def validate_civil_event(
    *,
    reference_number: str,
    event_type: str,
    event_date: date,
) -> Optional[str]:
    """Validate a civil registration record."""

    reference_number = _clean_required(
        reference_number
    )

    event_type = _clean_required(
        event_type
    )

    if not reference_number:
        return "Reference Number is required."

    if not event_type:
        return "Event Type is required."

    if event_date is None:
        return "Event Date is required."

    if event_date > date.today():
        return "Event Date cannot be in the future."

    return None


# ============================================================
# CREATE
# ============================================================

def create_civil_event(
    *,
    reference_number: str,
    event_type: str,
    citizen_id: Optional[str],
    event_date: date,
    registration_centre: Optional[str] = None,
    document_number: Optional[str] = None,
    status: str = "Pending Review",
    notes: Optional[str] = None,
) -> dict[str, Any]:
    """Create a civil registration record."""

    reference_number = _clean_required(
        reference_number
    )

    event_type = _clean_required(
        event_type
    )

    status = _clean_required(
        status
    ) or "Pending Review"

    error = validate_civil_event(
        reference_number=reference_number,
        event_type=event_type,
        event_date=event_date,
    )

    if error:
        return {
            "success": False,
            "message": error,
        }

    existing = get_event_by_reference(
        reference_number
    )

    if existing is not None:
        return {
            "success": False,
            "message": (
                "A civil registration record with "
                f"reference number '{reference_number}' "
                "already exists."
            ),
        }

    event_id = str(uuid4())

    event = create_event(
        event_id=event_id,
        reference_number=reference_number,
        event_type=event_type,
        citizen_id=_clean_optional(citizen_id),
        event_date=event_date,
        registration_centre=_clean_optional(
            registration_centre
        ),
        document_number=_clean_optional(
            document_number
        ),
        status=status,
        notes=_clean_optional(notes),
    )

    if event is None:
        return {
            "success": False,
            "message": (
                "The civil registration record "
                "could not be created."
            ),
        }

    return {
        "success": True,
        "message": (
            "Civil registration record "
            "created successfully."
        ),
        "event": event,
    }


# ============================================================
# UPDATE
# ============================================================

def update_civil_event(
    *,
    event_id: str,
    reference_number: str,
    event_type: str,
    citizen_id: Optional[str],
    event_date: date,
    registration_centre: Optional[str] = None,
    document_number: Optional[str] = None,
    status: str = "Pending Review",
    notes: Optional[str] = None,
) -> dict[str, Any]:
    """Update an existing civil registration record."""

    event_id = _clean_required(event_id)

    if not event_id:
        return {
            "success": False,
            "message": "Civil event ID is required.",
        }

    existing = get_event_by_id(event_id)

    if existing is None:
        return {
            "success": False,
            "message": (
                "The civil registration record "
                "could not be found."
            ),
        }

    reference_number = _clean_required(
        reference_number
    )

    event_type = _clean_required(
        event_type
    )

    status = _clean_required(
        status
    ) or "Pending Review"

    error = validate_civil_event(
        reference_number=reference_number,
        event_type=event_type,
        event_date=event_date,
    )

    if error:
        return {
            "success": False,
            "message": error,
        }

    duplicate = get_event_by_reference(
        reference_number
    )

    if (
        duplicate is not None
        and str(getattr(duplicate, "id", "")) != event_id
    ):
        return {
            "success": False,
            "message": (
                "Another civil registration record "
                f"already uses reference number "
                f"'{reference_number}'."
            ),
        }

    updated = update_event(
        event_id=event_id,
        reference_number=reference_number,
        event_type=event_type,
        citizen_id=_clean_optional(citizen_id),
        event_date=event_date,
        registration_centre=_clean_optional(
            registration_centre
        ),
        document_number=_clean_optional(
            document_number
        ),
        status=status,
        notes=_clean_optional(notes),
    )

    if updated is None:
        return {
            "success": False,
            "message": (
                "The civil registration record "
                "could not be updated."
            ),
        }

    return {
        "success": True,
        "message": (
            "Civil registration record "
            "updated successfully."
        ),
        "event": updated,
    }


# ============================================================
# READ
# ============================================================

def get_civil_event(
    event_id: str,
) -> Any:
    """Return a civil registration record by ID."""

    event_id = _clean_required(event_id)

    if not event_id:
        return None

    return get_event_by_id(event_id)


def list_civil_events(
    *,
    search: Optional[str] = None,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 25,
) -> list[Any]:
    """Return civil registration records."""

    return list_events(
        search=_clean_optional(search),
        event_type=_clean_optional(event_type),
        status=_clean_optional(status),
        limit=max(1, min(limit, 500)),
    )


# ============================================================
# CITIZEN SEARCH
# ============================================================

def search_citizens(
    search: str,
    limit: int = 25,
) -> list[Any]:
    """
    Search citizens for linking to civil events.

    Searches by full name or National ID.
    """

    search = _clean_required(search)

    if not search:
        return []

    return search_citizens_by_name_or_national_id(
        search,
        limit=max(1, min(limit, 100)),
    )


# ============================================================
# ARCHIVE
# ============================================================

def archive_civil_event(
    event_id: str,
) -> dict[str, Any]:
    """Archive a civil registration record."""

    event_id = _clean_required(event_id)

    if not event_id:
        return {
            "success": False,
            "message": "Civil event ID is required.",
        }

    event = get_event_by_id(event_id)

    if event is None:
        return {
            "success": False,
            "message": (
                "The civil registration record "
                "could not be found."
            ),
        }

    archived = archive_event(event_id)

    if not archived:
        return {
            "success": False,
            "message": (
                "The civil registration record "
                "could not be archived."
            ),
        }

    return {
        "success": True,
        "message": (
            "Civil registration record "
            "archived successfully."
        ),
    }


# ============================================================
# REPORTING / SUMMARY
# ============================================================

def get_civil_registration_summary() -> dict[str, int]:
    """Return Civil Registration dashboard metrics."""

    total = count_events()

    counts = get_event_counts_by_type()

    births = int(
        counts.get("Birth", 0)
    )

    deaths = int(
        counts.get("Death", 0)
    )

    marriages = int(
        counts.get("Marriage", 0)
    )

    divorces = int(
        counts.get("Divorce", 0)
    )

    pending = count_events(
        status="Pending Review"
    )

    verified = count_events(
        status="Verified"
    )

    return {
        "total": int(total),
        "births": births,
        "deaths": deaths,
        "marriages": marriages,
        "divorces": divorces,
        "pending": int(pending),
        "verified": int(verified),
    }


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "archive_civil_event",
    "create_civil_event",
    "get_civil_event",
    "get_civil_registration_summary",
    "list_civil_events",
    "search_citizens",
    "update_civil_event",
    "validate_civil_event",
]