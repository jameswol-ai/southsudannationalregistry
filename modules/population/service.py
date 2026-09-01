from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError

from database.database import SessionLocal
from models import Citizen, Household


def _session():
    return SessionLocal()


def _generate_id(prefix: str) -> str:
    return f"{prefix}-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"


def get_population_summary() -> dict[str, int]:
    db = _session()
    try:
        total = db.scalar(select(func.count(Citizen.id))) or 0
        male = db.scalar(
            select(func.count(Citizen.id)).where(Citizen.gender == "Male")
        ) or 0
        female = db.scalar(
            select(func.count(Citizen.id)).where(Citizen.gender == "Female")
        ) or 0
        verified = db.scalar(
            select(func.count(Citizen.id)).where(
                Citizen.verification_status == "Verified"
            )
        ) or 0
        pending = db.scalar(
            select(func.count(Citizen.id)).where(
                Citizen.verification_status == "Pending Review"
            )
        ) or 0
        households = db.scalar(select(func.count(Household.id))) or 0

        return {
            "total": total,
            "male": male,
            "female": female,
            "verified": verified,
            "pending": pending,
            "households": households,
        }
    finally:
        db.close()


def search_citizens(
    search: str = "",
    state: str = "",
    county: str = "",
    status: str = "",
    limit: int = 200,
) -> list[Citizen]:
    db = _session()

    try:
        stmt = select(Citizen).order_by(Citizen.created_at.desc()).limit(limit)

        if search.strip():
            term = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Citizen.full_name.ilike(term),
                    Citizen.national_id.ilike(term),
                    Citizen.passport_number.ilike(term),
                    Citizen.phone_number.ilike(term),
                    Citizen.email_address.ilike(term),
                )
            )

        if state:
            stmt = stmt.where(Citizen.state_or_region == state)

        if county:
            stmt = stmt.where(Citizen.county_or_payam == county)

        if status:
            stmt = stmt.where(Citizen.verification_status == status)

        return list(db.scalars(stmt).all())

    finally:
        db.close()


def get_citizen(citizen_id: str) -> Optional[Citizen]:
    db = _session()
    try:
        return db.get(Citizen, citizen_id)
    finally:
        db.close()


def create_citizen(data: dict[str, Any]) -> tuple[bool, str, Optional[str]]:
    db = _session()

    try:
        citizen_id = data.get("id") or _generate_id("CIT")

        citizen = Citizen(
            id=citizen_id,
            national_id=data.get("national_id") or None,
            passport_number=data.get("passport_number") or None,
            id_document_type=data.get("id_document_type") or None,
            full_name=data["full_name"].strip(),
            date_of_birth=data.get("date_of_birth"),
            age=int(data.get("age") or 0),
            gender=data.get("gender") or "Other",
            marital_status=data.get("marital_status") or "Single",
            nationality=data.get("nationality") or "South Sudanese",
            phone_number=data.get("phone_number") or None,
            email_address=data.get("email_address") or None,
            emergency_contact_name=data.get("emergency_contact_name") or None,
            emergency_contact_phone=data.get("emergency_contact_phone") or None,
            tribe=data.get("tribe") or "",
            sub_tribe_or_clan=data.get("sub_tribe_or_clan") or None,
            native_language=data.get("native_language") or "",
            state_or_region=data.get("state_or_region") or "",
            county_or_payam=data.get("county_or_payam") or "",
            sub_county_or_boma=data.get("sub_county_or_boma") or "",
            boma=data.get("boma") or None,
            community=data.get("community") or "",
            residential_address=data.get("residential_address") or None,
            duration_of_stay_years=float(
                data.get("duration_of_stay_years") or 0
            ),
            household_id=data.get("household_id") or None,
            household_role=data.get("household_role")
            or "Head of Household",
            is_household_head=bool(data.get("is_household_head", False)),
            education_level=data.get("education_level")
            or "None / Informal",
            is_literate=bool(data.get("is_literate", False)),
            employment_status=data.get("employment_status")
            or "Unemployed / Seeking Work",
            primary_occupation=data.get("primary_occupation") or None,
            employer_or_business_name=data.get(
                "employer_or_business_name"
            ) or None,
            industry_sector=data.get("industry_sector") or None,
            monthly_income_range=data.get("monthly_income_range") or None,
            has_special_needs_or_disability=bool(
                data.get("has_special_needs_or_disability", False)
            ),
            disability_type=data.get("disability_type") or None,
            mother_alive=data.get("mother_alive"),
            father_alive=data.get("father_alive"),
            voter_id_number=data.get("voter_id_number") or None,
            voter_status=data.get("voter_status") or None,
            constituency=data.get("constituency") or None,
            polling_station_id=data.get("polling_station_id") or None,
            polling_station_name=data.get("polling_station_name") or None,
            has_voted=bool(data.get("has_voted", False)),
            voted_at=data.get("voted_at"),
            enumerator_name=data.get("enumerator_name") or "",
            enumerator_badge_id=data.get("enumerator_badge_id") or "",
            enumeration_date=data.get("enumeration_date"),
            verification_status=data.get("verification_status")
            or "Pending Review",
            verification_notes=data.get("verification_notes") or None,
            notes=data.get("notes") or None,
        )

        db.add(citizen)
        db.commit()

        return True, "Citizen registered successfully.", citizen_id

    except IntegrityError:
        db.rollback()
        return (
            False,
            "A citizen with the supplied unique identification "
            "information already exists.",
            None,
        )

    except Exception as exc:
        db.rollback()
        return False, f"Unable to register citizen: {exc}", None

    finally:
        db.close()


def update_citizen(
    citizen_id: str,
    data: dict[str, Any],
) -> tuple[bool, str]:
    db = _session()

    try:
        citizen = db.get(Citizen, citizen_id)

        if citizen is None:
            return False, "Citizen not found."

        protected = {"id", "created_at", "updated_at"}

        for key, value in data.items():
            if key in protected or not hasattr(citizen, key):
                continue

            setattr(citizen, key, value)

        citizen.updated_at = datetime.utcnow()

        db.commit()

        return True, "Citizen updated successfully."

    except IntegrityError:
        db.rollback()
        return False, "The updated identification information conflicts with another record."

    except Exception as exc:
        db.rollback()
        return False, f"Unable to update citizen: {exc}"

    finally:
        db.close()


def delete_citizen(citizen_id: str) -> tuple[bool, str]:
    db = _session()

    try:
        citizen = db.get(Citizen, citizen_id)

        if citizen is None:
            return False, "Citizen not found."

        db.delete(citizen)
        db.commit()

        return True, "Citizen deleted successfully."

    except Exception as exc:
        db.rollback()
        return False, f"Unable to delete citizen: {exc}"

    finally:
        db.close()


def list_households(limit: int = 200) -> list[Household]:
    db = _session()

    try:
        stmt = (
            select(Household)
            .order_by(Household.created_at.desc())
            .limit(limit)
        )

        return list(db.scalars(stmt).all())

    finally:
        db.close()


def create_household(
    household_number: str,
    state_or_region: str,
    county_or_payam: str = "",
    sub_county_or_boma: str = "",
    boma: str = "",
    community: str = "",
    residential_address: str = "",
    head_citizen_id: Optional[str] = None,
) -> tuple[bool, str, Optional[str]]:
    db = _session()

    try:
        household_id = _generate_id("HH")

        household = Household(
            id=household_id,
            household_number=household_number.strip(),
            head_citizen_id=head_citizen_id or None,
            state_or_region=state_or_region.strip(),
            county_or_payam=county_or_payam.strip() or None,
            sub_county_or_boma=sub_county_or_boma.strip() or None,
            boma=boma.strip() or None,
            community=community.strip() or None,
            residential_address=residential_address.strip() or None,
        )

        db.add(household)
        db.commit()

        return True, "Household created successfully.", household_id

    except IntegrityError:
        db.rollback()
        return False, "Household number already exists.", None

    except Exception as exc:
        db.rollback()
        return False, f"Unable to create household: {exc}", None

    finally:
        db.close()
