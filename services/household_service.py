"""
Household service.

Business operations for household registration and management.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from database.models import AuditLog, Citizen, Household


# ============================================================
# HELPERS
# ============================================================

def _generate_id() -> str:
    return f"HH-{uuid4().hex[:12].upper()}"


def _audit(
    db: Session,
    action: str,
    entity_id: str,
    username: str = "system",
    details: Optional[str] = None,
) -> None:

    db.add(
        AuditLog(
            action=action,
            entity_type="Household",
            entity_id=entity_id,
            username=username,
            details=details,
        )
    )


# ============================================================
# CREATE
# ============================================================

def create_household(
    db: Session,
    data: dict[str, Any],
    username: str = "system",
) -> Household:

    household_number = data.get(
        "household_number"
    )

    if household_number:

        existing = (
            db.query(Household)
            .filter(
                Household.household_number
                == household_number,
            )
            .first()
        )

        if existing:
            raise ValueError(
                "A household with this number already exists."
            )

    household = Household(
        id=data.get("id") or _generate_id(),
        **{
            key: value
            for key, value in data.items()
            if key != "id"
        },
    )

    db.add(household)

    db.flush()

    _audit(
        db=db,
        action="CREATE",
        entity_id=household.id,
        username=username,
        details=(
            f"Household created: "
            f"{household.household_number}"
        ),
    )

    db.commit()

    db.refresh(household)

    return household


# ============================================================
# GET
# ============================================================

def get_household(
    db: Session,
    household_id: str,
) -> Optional[Household]:

    return (
        db.query(Household)
        .filter(
            Household.id == household_id,
        )
        .first()
    )


# ============================================================
# LIST
# ============================================================

def list_households(
    db: Session,
    limit: int = 100,
    offset: int = 0,
) -> list[Household]:

    return (
        db.query(Household)
        .order_by(
            Household.created_at.desc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )


# ============================================================
# UPDATE
# ============================================================

def update_household(
    db: Session,
    household_id: str,
    data: dict[str, Any],
    username: str = "system",
) -> Household:

    household = get_household(
        db=db,
        household_id=household_id,
    )

    if not household:
        raise ValueError(
            "Household record was not found."
        )

    protected_fields = {
        "id",
        "created_at",
    }

    for key, value in data.items():

        if key in protected_fields:
            continue

        if not hasattr(household, key):
            continue

        setattr(
            household,
            key,
            value,
        )

    household.updated_at = datetime.utcnow()

    _audit(
        db=db,
        action="UPDATE",
        entity_id=household.id,
        username=username,
        details=(
            f"Household updated: "
            f"{household.household_number}"
        ),
    )

    db.commit()

    db.refresh(household)

    return household


# ============================================================
# DELETE
# ============================================================

def delete_household(
    db: Session,
    household_id: str,
    username: str = "system",
) -> bool:

    household = get_household(
        db=db,
        household_id=household_id,
    )

    if not household:
        return False

    # Prevent accidental deletion of households
    # containing registered citizens.

    member_count = (
        db.query(Citizen)
        .filter(
            Citizen.household_id
            == household.id,
        )
        .count()
    )

    if member_count > 0:
        raise ValueError(
            "Cannot delete a household that contains registered citizens."
        )

    _audit(
        db=db,
        action="DELETE",
        entity_id=household.id,
        username=username,
        details=(
            f"Household deleted: "
            f"{household.household_number}"
        ),
    )

    db.delete(household)

    db.commit()

    return True
