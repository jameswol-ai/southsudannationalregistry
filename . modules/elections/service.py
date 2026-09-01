from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from database.database import SessionLocal
from models import Citizen, VoterRecord


def _session():
    return SessionLocal()


def _generate_id() -> str:
    return f"VOT-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"


def get_election_summary() -> dict[str, int]:
    db = _session()

    try:
        total = db.scalar(
            select(func.count(VoterRecord.id))
        ) or 0

        active = db.scalar(
            select(func.count(VoterRecord.id)).where(
                VoterRecord.voter_status == "Active"
            )
        ) or 0

        voted = db.scalar(
            select(func.count(VoterRecord.id)).where(
                VoterRecord.has_voted.is_(True)
            )
        ) or 0

        return {
            "total": total,
            "active": active,
            "voted": voted,
        }

    finally:
        db.close()


def list_voters(
    status: str = "",
    constituency: str = "",
    limit: int = 200,
) -> list[VoterRecord]:
    db = _session()

    try:
        stmt = (
            select(VoterRecord)
            .order_by(VoterRecord.created_at.desc())
            .limit(limit)
        )

        if status:
            stmt = stmt.where(
                VoterRecord.voter_status == status
            )

        if constituency:
            stmt = stmt.where(
                VoterRecord.constituency == constituency
            )

        return list(db.scalars(stmt).all())

    finally:
        db.close()


def register_voter(
    data: dict[str, Any],
) -> tuple[bool, str, str | None]:
    db = _session()

    try:
        citizen_id = data["citizen_id"]

        citizen = db.get(
            Citizen,
            citizen_id,
        )

        if citizen is None:
            return False, "Citizen not found.", None

        existing = db.scalar(
            select(VoterRecord).where(
                VoterRecord.citizen_id == citizen_id
            )
        )

        if existing:
            return False, "Citizen already has a voter record.", None

        voter_id = _generate_id()

        record = VoterRecord(
            id=voter_id,
            citizen_id=citizen_id,
            voter_id_number=data.get(
                "voter_id_number"
            ) or None,
            voter_status=data.get(
                "voter_status"
            ) or "Active",
            constituency=data.get(
                "constituency"
            ) or None,
            polling_station_id=data.get(
                "polling_station_id"
            ) or None,
            polling_station_name=data.get(
                "polling_station_name"
            ) or None,
        )

        db.add(record)
        db.commit()

        return True, "Voter registered successfully.", voter_id

    except IntegrityError:
        db.rollback()
        return False, "Voter ID already exists.", None

    except Exception as exc:
        db.rollback()
        return False, f"Unable to register voter: {exc}", None

    finally:
        db.close()


def update_voter(
    voter_id: str,
    data: dict[str, Any],
) -> tuple[bool, str]:
    db = _session()

    try:
        voter = db.get(
            VoterRecord,
            voter_id,
        )

        if voter is None:
            return False, "Voter record not found."

        for key, value in data.items():
            if key in {
                "id",
                "citizen_id",
                "created_at",
            }:
                continue

            if hasattr(voter, key):
                setattr(voter, key, value)

        voter.updated_at = datetime.utcnow()

        db.commit()

        return True, "Voter record updated successfully."

    except Exception as exc:
        db.rollback()
        return False, f"Unable to update voter: {exc}"

    finally:
        db.close()


def record_vote(
    voter_id: str,
) -> tuple[bool, str]:
    db = _session()

    try:
        voter = db.get(
            VoterRecord,
            voter_id,
        )

        if voter is None:
            return False, "Voter record not found."

        if voter.voter_status != "Active":
            return False, "Only active voters can be marked as voted."

        if voter.has_voted:
            return False, "This voter has already been marked as voted."

        voter.has_voted = True
        voter.voted_at = datetime.utcnow()

        db.commit()

        return True, "Vote status recorded."

    except Exception as exc:
        db.rollback()
        return False, f"Unable to record vote: {exc}"

    finally:
        db.close()
