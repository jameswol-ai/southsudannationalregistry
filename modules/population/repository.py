"""
Population Repository.

Database access for citizens and households.

Repository responsibilities:
    - Queries
    - Persistence
    - Counts
    - Filtering
    - Transaction helpers

Business rules belong in service.py.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from database.models import Citizen, Household


class PopulationRepository:

    def __init__(self, db: Session):
        self.db = db

    # ========================================================
    # CITIZENS
    # ========================================================

    def get_citizen(self, citizen_id: str) -> Citizen | None:
        return (
            self.db.query(Citizen)
            .filter(Citizen.id == citizen_id)
            .first()
        )

    def get_by_national_id(
        self,
        national_id: str,
    ) -> Citizen | None:

        return (
            self.db.query(Citizen)
            .filter(Citizen.national_id == national_id)
            .first()
        )

    def get_by_voter_id(
        self,
        voter_id_number: str,
    ) -> Citizen | None:

        return (
            self.db.query(Citizen)
            .filter(
                Citizen.voter_id_number == voter_id_number
            )
            .first()
        )

    def list_citizens(
        self,
        search: str | None = None,
        state: str | None = None,
        county: str | None = None,
        gender: str | None = None,
        verification_status: str | None = None,
        limit: int = 500,
    ) -> list[Citizen]:

        query = self.db.query(Citizen)

        if search:
            pattern = f"%{search.strip()}%"

            query = query.filter(
                or_(
                    Citizen.full_name.ilike(pattern),
                    Citizen.national_id.ilike(pattern),
                    Citizen.phone_number.ilike(pattern),
                    Citizen.voter_id_number.ilike(pattern),
                    Citizen.passport_number.ilike(pattern),
                )
            )

        if state:
            query = query.filter(
                Citizen.state_or_region == state
            )

        if county:
            query = query.filter(
                Citizen.county_or_payam == county
            )

        if gender:
            query = query.filter(
                Citizen.gender == gender
            )

        if verification_status:
            query = query.filter(
                Citizen.verification_status
                == verification_status
            )

        return (
            query
            .order_by(Citizen.full_name.asc())
            .limit(limit)
            .all()
        )

    def count_citizens(self) -> int:
        return int(
            self.db.query(
                func.count(Citizen.id)
            ).scalar()
            or 0
        )

    def count_by_gender(self) -> dict[str, int]:

        rows = (
            self.db.query(
                Citizen.gender,
                func.count(Citizen.id),
            )
            .group_by(Citizen.gender)
            .all()
        )

        return {
            str(gender or "Unknown"): int(count)
            for gender, count in rows
        }

    def count_by_state(self) -> dict[str, int]:

        rows = (
            self.db.query(
                Citizen.state_or_region,
                func.count(Citizen.id),
            )
            .group_by(Citizen.state_or_region)
            .order_by(func.count(Citizen.id).desc())
            .all()
        )

        return {
            str(state or "Unknown"): int(count)
            for state, count in rows
        }

    def count_by_verification_status(self) -> dict[str, int]:

        rows = (
            self.db.query(
                Citizen.verification_status,
                func.count(Citizen.id),
            )
            .group_by(Citizen.verification_status)
            .all()
        )

        return {
            str(status or "Unknown"): int(count)
            for status, count in rows
        }

    def add_citizen(
        self,
        citizen: Citizen,
    ) -> Citizen:

        self.db.add(citizen)
        self.db.flush()

        return citizen

    def update_citizen(
        self,
        citizen: Citizen,
        values: dict[str, Any],
    ) -> Citizen:

        for field, value in values.items():
            if hasattr(citizen, field):
                setattr(citizen, field, value)

        citizen.updated_at = datetime.utcnow()

        self.db.flush()

        return citizen

    # ========================================================
    # HOUSEHOLDS
    # ========================================================

    def get_household(
        self,
        household_id: str,
    ) -> Household | None:

        return (
            self.db.query(Household)
            .filter(Household.id == household_id)
            .first()
        )

    def get_household_by_number(
        self,
        household_number: str,
    ) -> Household | None:

        return (
            self.db.query(Household)
            .filter(
                Household.household_number
                == household_number
            )
            .first()
        )

    def list_households(
        self,
        search: str | None = None,
        state: str | None = None,
        county: str | None = None,
        limit: int = 500,
    ) -> list[Household]:

        query = self.db.query(Household)

        if search:
            pattern = f"%{search.strip()}%"

            query = query.filter(
                or_(
                    Household.household_number.ilike(pattern),
                    Household.community.ilike(pattern),
                    Household.residential_address.ilike(pattern),
                )
            )

        if state:
            query = query.filter(
                Household.state_or_region == state
            )

        if county:
            query = query.filter(
                Household.county_or_payam == county
            )

        return (
            query
            .order_by(Household.household_number.asc())
            .limit(limit)
            .all()
        )

    def count_households(self) -> int:

        return int(
            self.db.query(
                func.count(Household.id)
            ).scalar()
            or 0
        )

    def add_household(
        self,
        household: Household,
    ) -> Household:

        self.db.add(household)
        self.db.flush()

        return household

    def update_household(
        self,
        household: Household,
        values: dict[str, Any],
    ) -> Household:

        for field, value in values.items():
            if hasattr(household, field):
                setattr(household, field, value)

        household.updated_at = datetime.utcnow()

        self.db.flush()

        return household

    # ========================================================
    # LOCATION LOOKUPS
    # ========================================================

    def get_states(self) -> list[str]:

        rows = (
            self.db.query(
                Citizen.state_or_region
            )
            .filter(
                Citizen.state_or_region.isnot(None)
            )
            .filter(
                Citizen.state_or_region != ""
            )
            .distinct()
            .order_by(Citizen.state_or_region.asc())
            .all()
        )

        return [row[0] for row in rows]

    def get_counties(
        self,
        state: str | None = None,
    ) -> list[str]:

        query = (
            self.db.query(
                Citizen.county_or_payam
            )
            .filter(
                Citizen.county_or_payam.isnot(None)
            )
            .filter(
                Citizen.county_or_payam != ""
            )
        )

        if state:
            query = query.filter(
                Citizen.state_or_region == state
            )

        rows = (
            query
            .distinct()
            .order_by(Citizen.county_or_payam.asc())
            .all()
        )

        return [row[0] for row in rows]