"""
Elections repository.

Database access layer for voter records.
"""

from __future__ import annotations

from sqlalchemy import func


class ElectionsRepository:
    """
    Repository responsible for database operations related
    to elections and voter registration.
    """

    def __init__(self, session, VoterRecord, Citizen):
        self.session = session
        self.VoterRecord = VoterRecord
        self.Citizen = Citizen

    # =========================================================
    # VOTERS
    # =========================================================

    def list_voters(
        self,
        status: str | None = None,
        constituency: str | None = None,
        limit: int = 200,
    ):
        query = self.session.query(self.VoterRecord)

        if status:
            query = query.filter(
                self.VoterRecord.voter_status == status
            )

        if constituency:
            query = query.filter(
                self.VoterRecord.constituency == constituency
            )

        return (
            query
            .order_by(self.VoterRecord.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_voter(self, voter_id):
        return self.session.get(
            self.VoterRecord,
            voter_id,
        )

    def get_voter_by_citizen(self, citizen_id):
        return (
            self.session.query(self.VoterRecord)
            .filter(
                self.VoterRecord.citizen_id == citizen_id
            )
            .first()
        )

    def get_voter_by_number(self, voter_id_number):
        if not voter_id_number:
            return None

        return (
            self.session.query(self.VoterRecord)
            .filter(
                self.VoterRecord.voter_id_number
                == voter_id_number
            )
            .first()
        )

    def add_voter(self, voter):
        self.session.add(voter)
        self.session.flush()
        return voter

    def delete_voter(self, voter):
        self.session.delete(voter)

    # =========================================================
    # CITIZENS
    # =========================================================

    def citizen_exists(self, citizen_id) -> bool:
        return (
            self.session.get(
                self.Citizen,
                citizen_id,
            )
            is not None
        )

    def get_citizen(self, citizen_id):
        return self.session.get(
            self.Citizen,
            citizen_id,
        )

    # =========================================================
    # STATISTICS
    # =========================================================

    def count_voters(self) -> int:
        return (
            self.session.query(
                func.count(self.VoterRecord.id)
            ).scalar()
            or 0
        )

    def count_active_voters(self) -> int:
        return (
            self.session.query(
                func.count(self.VoterRecord.id)
            )
            .filter(
                self.VoterRecord.voter_status == "Active"
            )
            .scalar()
            or 0
        )

    def count_voted(self) -> int:
        return (
            self.session.query(
                func.count(self.VoterRecord.id)
            )
            .filter(
                self.VoterRecord.has_voted.is_(True)
            )
            .scalar()
            or 0
        )

    # =========================================================
    # TRANSACTION CONTROL
    # =========================================================

    def save(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()