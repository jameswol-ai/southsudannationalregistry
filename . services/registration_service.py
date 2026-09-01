"""
Civil registration service.

Handles registration of:

    - Births
    - Deaths
    - Marriages
    - Divorces
    - Other civil events
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from database.models import AuditLog, CivilEvent


# ============================================================
# HELPERS
# ============================================================

def _generate_id() -> str:
    return f"CIV-{uuid4().hex[:12].upper()}"


def _generate_reference() -> str:
    return f"CIV-{datetime.utcnow():%Y%m%d}-{uuid4().hex[:6].upper()}"


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
            entity_type="CivilEvent",
            entity_id=entity_id,
            username=username,
            details=details,
        )
    )


# ============================================================
# CREATE
# ============================================================

def create_civil_event(
    db: Session,
    data: dict[str, Any],
    username: str = "system",
) -> CivilEvent:

    reference_number = (
        data.get("reference_number")
        or _generate_reference()
    )

    existing = (
        db.query(CivilEvent)
        .filter(
            CivilEvent.reference_number
            == reference_number,
        )
        .first()
    )

    if existing:
        raise ValueError(
            "A civil event with this reference number already exists."
        )

    event = CivilEvent(
        id=data.get("id") or _generate_id(),
        reference_number=reference_number,
        **{
            key: value
            for key, value in data.items()
            if key not in {
                "id",
                "reference_number",
            }
        },
    )

    db.add(event)

    db.flush()

    _audit(
        db=db,
        action="CREATE",
        entity_id=event.id,
        username=username,
        details=(
            f"{event.event_type} registration created "
            f"with reference {event.reference_number}"
        ),
    )

    db.commit()

    db.refresh(event)

    return event


# ============================================================
# GET
# ============================================================

def get_civil_event(
    db: Session,
    event_id: str,
) -> Optional[CivilEvent]:

    return (
        db.query(CivilEvent)
        .filter(
            CivilEvent.id == event_id,
        )
        .first()
    )


# ============================================================
# LIST
# ============================================================

def list_civil_events(
    db: Session,
    event_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[CivilEvent]:

    query = db.query(CivilEvent)

    if event_type:
        query = query.filter(
            CivilEvent.event_type
            == event_type,
        )

    return (
        query
        .order_by(
            CivilEvent.event_date.desc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )


# ============================================================
# UPDATE
# ============================================================

def update_civil_event(
    db: Session,
    event_id: str,
    data: dict[str, Any],
    username: str = "system",
) -> CivilEvent:

    event = get_civil_event(
        db=db,
        event_id=event_id,
    )

    if not event:
        raise ValueError(
            "Civil event was not found."
        )

    protected_fields = {
        "id",
        "created_at",
        "reference_number",
    }

    for key, value in data.items():

        if key in protected_fields:
            continue

        if not hasattr(event, key):
            continue

        setattr(
            event,
            key,
            value,
        )

    _audit(
        db=db,
        action="UPDATE",
        entity_id=event.id,
        username=username,
        details=(
            f"Civil event updated: "
            f"{event.reference_number}"
        ),
    )

    db.commit()

    db.refresh(event)

    return event
