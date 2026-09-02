"""
Population Service.

Business logic for population registration and statistics.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database.models import AuditLog, Citizen, Household

from .repository import PopulationRepository


class PopulationValidationError(ValueError):
    """Raised when population data fails validation."""


class PopulationService:

    def __init__(
        self,
        db: Session,
        username: str = "system",
    ):

        self.db = db
        self.username = username
        self.repository = PopulationRepository(db)

    # ========================================================
    # VALIDATION
    # ========================================================

    @staticmethod
    def calculate_age(
        date_of_birth: date | None,
    ) -> int:

        if not date_of_birth:
            return 0

        today = date.today()

        age = (
            today.year
            - date_of_birth.year
            - (
                (today.month, today.day)
                < (
                    date_of_birth.month,
                    date_of_birth.day,
                )
            )
        )

        return max(0, age)

    def validate_citizen(
        self,
        values: dict[str, Any],
        citizen_id: str | None = None,
    ) -> None:

        full_name = str(
            values.get("full_name") or ""
        ).strip()

        if not full_name:
            raise PopulationValidationError(
                "Full name is required."
            )

        national_id = values.get("national_id")

        if national_id:
            national_id = str(national_id).strip()

            existing = (
                self.repository.get_by_national_id(
                    national_id
                )
            )

            if existing and existing.id != citizen_id:
                raise PopulationValidationError(
                    "National ID already exists."
                )

        voter_id = values.get("voter_id_number")

        if voter_id:
            voter_id = str(voter_id).strip()

            existing = (
                self.repository.get_by_voter_id(
                    voter_id
                )
            )

            if existing and existing.id != citizen_id:
                raise PopulationValidationError(
                    "Voter ID already exists."
                )

        dob = values.get("date_of_birth")

        if dob and dob > date.today():
            raise PopulationValidationError(
                "Date of birth cannot be in the future."
            )

        duration = values.get(
            "duration_of_stay_years",
            0.0,
        )

        try:
            duration = float(duration)
        except (TypeError, ValueError):
            raise PopulationValidationError(
                "Duration of stay must be numeric."
            )

        if duration < 0:
            raise PopulationValidationError(
                "Duration of stay cannot be negative."
            )

    # ========================================================
    # AUDIT
    # ========================================================

    def _audit(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        details: str,
    ) -> None:

        self.db.add(
            AuditLog(
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                username=self.username,
                details=details,
                created_at=datetime.utcnow(),
            )
        )

    # ========================================================
    # CREATE
    # ========================================================

    def create_citizen(
        self,
        values: dict[str, Any],
    ) -> Citizen:

        self.validate_citizen(values)

        citizen = Citizen(
            id=str(uuid.uuid4()),
            full_name=str(
                values.get("full_name") or ""
            ).strip(),
        )

        fields = {
            key: value
            for key, value in values.items()
            if key != "id"
            and hasattr(Citizen, key)
        }

        for field, value in fields.items():
            setattr(citizen, field, value)

        citizen.age = self.calculate_age(
            citizen.date_of_birth
        )

        citizen.created_at = datetime.utcnow()
        citizen.updated_at = datetime.utcnow()

        try:
            self.repository.add_citizen(citizen)

            self._audit(
                "CREATE",
                "Citizen",
                citizen.id,
                f"Created citizen record for {citizen.full_name}.",
            )

            self.db.commit()
            self.db.refresh(citizen)

            return citizen

        except IntegrityError as exc:
            self.db.rollback()

            raise PopulationValidationError(
                "Citizen could not be saved because "
                "a unique database value already exists."
            ) from exc

        except Exception:
            self.db.rollback()
            raise

    # ========================================================
    # UPDATE
    # ========================================================

    def update_citizen(
        self,
        citizen_id: str,
        values: dict[str, Any],
    ) -> Citizen:

        citizen = self.repository.get_citizen(
            citizen_id
        )

        if citizen is None:
            raise PopulationValidationError(
                "Citizen record was not found."
            )

        self.validate_citizen(
            values,
            citizen_id=citizen_id,
        )

        clean_values = dict(values)

        if "date_of_birth" in clean_values:
            clean_values["age"] = self.calculate_age(
                clean_values["date_of_birth"]
            )

        try:
            citizen = self.repository.update_citizen(
                citizen,
                clean_values,
            )

            self._audit(
                "UPDATE",
                "Citizen",
                citizen.id,
                f"Updated citizen record for {citizen.full_name}.",
            )

            self.db.commit()
            self.db.refresh(citizen)

            return citizen

        except IntegrityError as exc:
            self.db.rollback()

            raise PopulationValidationError(
                "Citizen could not be updated because "
                "a unique database value already exists."
            ) from exc

        except Exception:
            self.db.rollback()
            raise

    # ========================================================
    # ARCHIVE
    # ========================================================

    def archive_citizen(
        self,
        citizen_id: str,
    ) -> Citizen:

        citizen = self.repository.get_citizen(
            citizen_id
        )

        if citizen is None:
            raise PopulationValidationError(
                "Citizen record was not found."
            )

        try:
            citizen.verification_status = "Archived"
            citizen.updated_at = datetime.utcnow()

            self._audit(
                "ARCHIVE",
                "Citizen",
                citizen.id,
                f"Archived citizen record for {citizen.full_name}.",
            )

            self.db.commit()
            self.db.refresh(citizen)

            return citizen

        except Exception:
            self.db.rollback()
            raise

    # ========================================================
    # READ
    # ========================================================

    def get_citizen(
        self,
        citizen_id: str,
    ) -> Citizen | None:

        return self.repository.get_citizen(
            citizen_id
        )

    def search_citizens(
        self,
        search: str | None = None,
        state: str | None = None,
        county: str | None = None,
        gender: str | None = None,
        verification_status: str | None = None,
        limit: int = 500,
    ) -> list[Citizen]:

        return self.repository.list_citizens(
            search=search,
            state=state,
            county=county,
            gender=gender,
            verification_status=verification_status,
            limit=limit,
        )

    # ========================================================
    # STATISTICS
    # ========================================================

    def dashboard_statistics(self) -> dict[str, Any]:

        return {
            "total_citizens":
                self.repository.count_citizens(),
            "total_households":
                self.repository.count_households(),
            "by_gender":
                self.repository.count_by_gender(),
            "by_state":
                self.repository.count_by_state(),
            "by_verification_status":
                self.repository.count_by_verification_status(),
        }

    # ========================================================
    # HOUSEHOLDS
    # ========================================================

    def create_household(
        self,
        values: dict[str, Any],
    ) -> Household:

        number = str(
            values.get("household_number") or ""
        ).strip()

        if not number:
            raise PopulationValidationError(
                "Household number is required."
            )

        existing = (
            self.repository.get_household_by_number(
                number
            )
        )

        if existing:
            raise PopulationValidationError(
                "Household number already exists."
            )

        household = Household(
            id=str(uuid.uuid4()),
            household_number=number,
            state_or_region=str(
                values.get("state_or_region") or ""
            ).strip(),
            county_or_payam=values.get(
                "county_or_payam"
            ),
            sub_county_or_boma=values.get(
                "sub_county_or_boma"
            ),
            boma=values.get("boma"),
            community=values.get("community"),
            residential_address=values.get(
                "residential_address"
            ),
            head_citizen_id=values.get(
                "head_citizen_id"
            ),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        try:
            self.repository.add_household(
                household
            )

            self._audit(
                "CREATE",
                "Household",
                household.id,
                f"Created household {number}.",
            )

            self.db.commit()
            self.db.refresh(household)

            return household

        except IntegrityError as exc:
            self.db.rollback()

            raise PopulationValidationError(
                "Household could not be saved because "
                "the household number already exists."
            ) from exc

        except Exception:
            self.db.rollback()
            raise