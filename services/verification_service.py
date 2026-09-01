"""
Verification service.

Controls the citizen verification workflow.

Workflow:

    Pending Review
          |
          +----> Verified
          |
          +----> Rejected
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from database.models import AuditLog, Citizen


# ============================================================
# AUDIT
# ============================================================

def _audit(
    db: Session,
    action: str,
    citizen_id: str,
    username: str,
    details: Optional[str] = None,
) -> None:

    db.add(
        AuditLog(
            action=action,
            entity_type="Citizen",
            entity_id=citizen_id,
            username=username,
            details=details,
        )
    )


# ============================================================
# VERIFICATION QUEUE
# ============================================================

def get_verification_queue(
    db: Session,
    status: str = "Pending Review",
    limit: int = 100,
) -> list[Citizen]:

    return (
        db.query(Citizen)
        .filter(
            Citizen.verification_status
            == status,
        )
        .order_by(
            Citizen.created_at.asc(),
        )
        .limit(limit)
        .all()
    )


# ============================================================
# VERIFY
# ============================================================

def verify_citizen(
    db: Session,
    citizen_id: str,
    username: str,
    notes: Optional[str] = None,
) -> Citizen:

    citizen = (
        db.query(Citizen)
        .filter(
            Citizen.id == citizen_id,
        )
        .first()
    )

    if not citizen:
        raise ValueError(
            "Citizen record was not found."
        )

    citizen.verification_status = "Verified"

    if notes:
        citizen.notes = notes

    _audit(
        db=db,
        action="VERIFY",
        citizen_id=citizen.id,
        username=username,
        details=(
            f"Citizen verified: "
            f"{citizen.full_name}"
        ),
    )

    db.commit()

    db.refresh(citizen)

    return citizen


# ============================================================
# REJECT
# ============================================================

def reject_citizen(
    db: Session,
    citizen_id: str,
    username: str,
    reason: str,
) -> Citizen:

    if not reason.strip():
        raise ValueError(
            "A rejection reason is required."
        )

    citizen = (
        db.query(Citizen)
        .filter(
            Citizen.id == citizen_id,
        )
        .first()
    )

    if not citizen:
        raise ValueError(
            "Citizen record was not found."
        )

    citizen.verification_status = "Rejected"

    citizen.notes = reason

    _audit(
        db=db,
        action="REJECT",
        citizen_id=citizen.id,
        username=username,
        details=(
            f"Citizen rejected: "
            f"{reason}"
        ),
    )

    db.commit()

    db.refresh(citizen)

    return citizen
