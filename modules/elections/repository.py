from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from database.models import (
    Citizen,
    VoterRecord,
)


class ElectionsRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def get_voter(
        self,
        voter_id: str,
    ) -> VoterRecord | None:

        return (
            self.db.query(VoterRecord)
            .filter(
                VoterRecord.id == voter_id
            )
            .first()
        )

    def get_voter_by_citizen(
        self,
        citizen_id: str,
    ) -> VoterRecord | None:

        return (
            self.db.query(VoterRecord)
            .filter(
                VoterRecord.citizen_id
                == citizen_id
            )
            .first()
        )

    def list_voters(
        self,
        search: str | None = None,
        limit: int = 500,
    ) -> list[VoterRecord]:

        query = self.db.query(
            VoterRecord
        )

        if search:

            pattern = (
                f"%{search.strip()}%"
            )

            query = query.join(
                Citizen
            ).filter(
                Citizen.full_name.ilike(
                    pattern
                )
            )

        return (
            query
            .order_by(
                VoterRecord.created_at.desc()
            )
            .limit(limit)
            .all()
        )

    def count_voters(self) -> int:

        return int(
            self.db.query(
                func.count(
                    VoterRecord.id
                )
            ).scalar()
            or 0
        )

    def add_voter(
        self,
        voter: VoterRecord,
    ) -> VoterRecord:

        self.db.add(voter)
        self.db.flush()

        return voter