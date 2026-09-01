"""
Citizen service.

Contains business operations for registering, retrieving, updating,
searching and deleting citizen records.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import or_
from sqlalchemy.orm import Session

from database.models import AuditLog, Citizen


# ============================================================
# HELPERS
# ============================================================

def _generate_id() -> str:
    """Generate a registry citizen identifier."""

    return f"CIT-{uuid4().hex[:12].upper()}"


def _audit(
    db: Session,
    action: str,
    entity_id: str,
    username: str = "system",
    details: Optional[str] = None,
) -> None:
    """Write an audit event."""

    db.add(
        AuditLog(
            action=action,
            entity_type="Citizen",
            entity_id=entity_id,
            username=username,
            details=details,
        )
    )


# ============================================================
# CREATE
# ============================================================

def create_citizen(
    db: Session,
    data: dict[str, Any],
    username: str = "system",
) -> Citizen:
    """
    Create a new citizen.

    Raises:
        ValueError:
            If a duplicate national ID or voter ID exists.
    """

    national_id = data.get("national_id")

    if national_id:

        existing = (
            db.query(Citizen)
            .filter(
                Citizen.national_id == national_id,
            )
            .first()
        )

        if existing:
            raise ValueError(
                "A citizen with this National ID already exists."
            )

    voter_id = data.get("voter_id_number")

    if voter_id:

        existing = (
            db.query(Citizen)
            .filter(
                Citizen.voter_id_number == voter_id,
            )
            .first()
        )

        if existing:
            raise ValueError(
                "A citizen with this voter ID already exists."
            )

    citizen = Citizen(
        id=data.get("id") or _generate_id(),
        **{
            key: value
            for key, value in data.items()
            if key != "id"
        },
    )

    db.add(citizen)

    db.flush()

    _audit(
        db=db,
        action="CREATE",
        entity_id=citizen.id,
        username=username,
        details=f"Citizen created: {citizen.full_name}",
    )

    db.commit()

    db.refresh(citizen)

    return citizen


# ============================================================
# GET
# ============================================================

def get_citizen(
    db: Session,
    citizen_id: str,
) -> Optional[Citizen]:
    """Retrieve a citizen by registry ID."""

    return (
        db.query(Citizen)
        .filter(
            Citizen.id == citizen_id,
        )
        .first()
    )


# ============================================================
# LIST
# ============================================================

def list_citizens(
    db: Session,
    limit: int = 100,
    offset: int = 0,
) -> list[Citizen]:
    """Return citizens using pagination."""

    return (
        db.query(Citizen)
        .order_by(
            Citizen.created_at.desc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )


# ============================================================
# SEARCH
# ============================================================

def search_citizens(
    db: Session,
    search_term: str,
    limit: int = 100,
) -> list[Citizen]:
    """
    Search citizens by:

        - Name
        - National ID
        - Voter ID
        - Phone
        - Community
    """

    term = f"%{search_term.strip()}%"

    return (
        db.query(Citizen)
        .filter(
            or_(
                Citizen.full_name.ilike(term),
                Citizen.national_id.ilike(term),
                Citizen.voter_id_number.ilike(term),
                Citizen.phone_number.ilike(term),
                Citizen.community.ilike(term),
            )
        )
        .order_by(
            Citizen.full_name.asc(),
        )
        .limit(limit)
        .all()
    )


# ============================================================
# UPDATE
# ============================================================

def update_citizen(
    db: Session,
    citizen_id: str,
    data: dict[str, Any],
    username: str = "system",
) -> Citizen:
    """Update an existing citizen."""

    citizen = get_citizen(
        db=db,
        citizen_id=citizen_id,
    )

    if not citizen:
        raise ValueError(
            "Citizen record was not found."
        )

    protected_fields = {
        "id",
        "created_at",
    }

    for key, value in data.items():

        if key in protected_fields:
            continue

        if not hasattr(citizen, key):
            continue

        setattr(
            citizen,
            key,
            value,
        )

    citizen.updated_at = datetime.utcnow()

    _audit(
        db=db,
        action="UPDATE",
        entity_id=citizen.id,
        username=username,
        details=f"Citizen updated: {citizen.full_name}",
    )

    db.commit()

    db.refresh(citizen)

    return citizen


# ============================================================
# DELETE
# ============================================================

def delete_citizen(
    db: Session,
    citizen_id: str,
    username: str = "system",
) -> bool:
    """
    Delete a citizen.

    This should normally be restricted to authorized
    administrators in production.
    """

    citizen = get_citizen(
        db=db,
        citizen_id=citizen_id,
    )

    if not citizen:
        return False

    name = citizen.full_name

    _audit(
        db=db,
        action="DELETE",
        entity_id=citizen.id,
        username=username,
        details=f"Citizen deleted: {name}",
    )

    db.delete(citizen)

    db.commit()

    return True
