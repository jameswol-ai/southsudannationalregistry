"""
Seed data for local development.

The seed is deliberately small and non-authoritative.
It exists only to make the Streamlit application immediately
testable after installation.

Usage:

    python -m database.seed
"""

from __future__ import annotations

from datetime import date

from .database import SessionLocal, init_db
from .models import AdministrativeUnit, Citizen, Household


def seed_database() -> None:

    init_db()

    db = SessionLocal()

    try:

        existing = db.query(Citizen).count()

        if existing:
            print(
                f"Database already contains {existing} citizen(s)."
            )
            return

        # ----------------------------------------------------
        # Administrative unit
        # ----------------------------------------------------

        adm = AdministrativeUnit(
            id="ADM-CES-001",
            unit_type="State",
            name="Central Equatoria",
            code="CES",
            state_or_region="Central Equatoria",
            headquarters="Juba",
        )

        db.add(adm)

        # ----------------------------------------------------
        # Household
        # ----------------------------------------------------

        household = Household(
            id="HH-DEMO-001",
            household_number="HH-DEMO-001",
            state_or_region="Central Equatoria",
            county_or_payam="Juba",
            sub_county_or_boma="Juba",
            boma="Gudele",
            community="Gudele",
            residential_address="Juba",
        )

        db.add(household)

        db.flush()

        # ----------------------------------------------------
        # Citizens
        # ----------------------------------------------------

        citizens = [
            Citizen(
                id="CIT-DEMO-001",
                national_id="SS-DEMO-0001",
                id_document_type="National ID",
                full_name="Demo Citizen One",
                date_of_birth=date(
                    1990,
                    1,
                    1,
                ),
                age=36,
                gender="Male",
                marital_status="Married",
                nationality="South Sudanese",
                tribe="Example",
                native_language="English",
                state_or_region="Central Equatoria",
                county_or_payam="Juba",
                sub_county_or_boma="Juba",
                boma="Gudele",
                community="Gudele",
                household_id=household.id,
                household_role="Head of Household",
                is_household_head=True,
                education_level="Secondary Education",
                is_literate=True,
                employment_status="Self-Employed / Business",
                primary_occupation="Business Owner",
                enumerator_name="Demo Enumerator",
                enumerator_badge_id="DEMO-001",
                enumeration_date=date.today(),
                verification_status="Verified",
            ),
            Citizen(
                id="CIT-DEMO-002",
                national_id="SS-DEMO-0002",
                id_document_type="National ID",
                full_name="Demo Citizen Two",
                date_of_birth=date(
                    1994,
                    5,
                    12,
                ),
                age=32,
                gender="Female",
                marital_status="Married",
                nationality="South Sudanese",
                tribe="Example",
                native_language="English",
                state_or_region="Central Equatoria",
                county_or_payam="Juba",
                sub_county_or_boma="Juba",
                boma="Gudele",
                community="Gudele",
                household_id=household.id,
                household_role="Spouse",
                is_household_head=False,
                education_level="Tertiary / Bachelor Degree",
                is_literate=True,
                employment_status="Employed (Private Sector)",
                primary_occupation="Administrator",
                enumerator_name="Demo Enumerator",
                enumerator_badge_id="DEMO-001",
                enumeration_date=date.today(),
                verification_status="Pending Review",
            ),
        ]

        db.add_all(citizens)

        db.commit()

        print(
            "South Sudan National Registry demo data seeded successfully."
        )

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


if __name__ == "__main__":
    seed_database()
