from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from database.database import SessionLocal
from models import Citizen, CivilEvent


def _session():
    return SessionLocal()


def _generate_id(prefix: str) -> str:
    return f"{prefix}-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"


def get_event_summary() -> dict[str, int]:
    db = _session()

    try:
        total = db.scalar(
            select(func.count(CivilEvent.id))
        ) or 0

        births = db.scalar(
            select(func.count(CivilEvent.id)).where(
                CivilEvent.event_type == "Birth"
            )
        ) or 0

        deaths = db.scalar(
            select(func.count(CivilEvent.id)).where(
                CivilEvent.event_type == "Death"
            )
        ) or 0

        marriages = db.scalar(
            select(func.count(CivilEvent.id)).where(
                CivilEvent.event_type == "Marriage"
            )
        ) or 0

        pending = db.scalar(
            select(func.count(CivilEvent.id)).where(
                CivilEvent.status == "Pending Review"
            )
        ) or 0

        return {
            "total": total,
            "births": births,
            "deaths": deaths,
            "marriages": marriages,
            "pending": pending,
        }

    finally:
        db.close()


def list_civil_events(
    event_type: str = "",
    status: str = "",
    limit: int = 200,
) -> list[CivilEvent]:
    db = _session()

    try:
        stmt = (
            select(CivilEvent)
            .order_by(CivilEvent.event_date.desc())
            .limit(limit)
        )

        if event_type:
            stmt = stmt.where(
                CivilEvent.event_type == event_type
            )

        if status:
            stmt = stmt.where(
                CivilEvent.status == status
            )

        return list(db.scalars(stmt).all())

    finally:
        db.close()


def create_civil_event(
    data: dict[str, Any],
) -> tuple[bool, str, str | None]:
    db = _session()

    try:
        event_id = _generate_id("CE")

        event = CivilEvent(
            id=event_id,
            reference_number=data["reference_number"].strip(),
            event_type=data["event_type"],
            citizen_id=data.get("citizen_id") or None,
            event_date=data["event_date"],
            registration_centre=data.get(
                "registration_centre"
            ) or None,
            document_number=data.get(
                "document_number"
            ) or None,
            status=data.get("status")
            or "Pending Review",
            notes=data.get("notes") or None,
        )

        if event.citizen_id:
            citizen = db.get(
                Citizen,
                event.citizen_id,
            )

            if citizen is None:
                return False, "Citizen does not exist.", None

        db.add(event)
        db.commit()

        return (
            True,
            "Civil event registered successfully.",
            event_id,
        )

    except IntegrityError:
        db.rollback()
        return False, "Reference number already exists.", None

    except Exception as exc:
        db.rollback()
        return False, f"Unable to register event: {exc}", None

    finally:
        db.close()


def update_civil_event(
    event_id: str,
    data: dict[str, Any],
) -> tuple[bool, str]:
    db = _session()

    try:
        event = db.get(
            CivilEvent,
            event_id,
        )

        if event is None:
            return False, "Civil event not found."

        for key, value in data.items():
            if key in {
                "id",
                "created_at",
                "reference_number",
            }:
                continue

            if hasattr(event, key):
                setattr(event, key, value)

        db.commit()

        return True, "Civil event updated successfully."

    except Exception as exc:
        db.rollback()
        return False, f"Unable to update event: {exc}"

    finally:
        db.close()
