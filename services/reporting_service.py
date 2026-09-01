"""
Reporting and dashboard service.

Provides aggregate information for:

    - Streamlit dashboards
    - Registry API
    - Next.js AI Studio
    - Future analytics modules
"""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from database.models import (
    Citizen,
    CivilEvent,
    Household,
)


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

def get_dashboard_summary(
    db: Session,
) -> dict:

    total_citizens = (
        db.query(
            func.count(Citizen.id)
        ).scalar()
        or 0
    )

    total_households = (
        db.query(
            func.count(Household.id)
        ).scalar()
        or 0
    )

    total_civil_events = (
        db.query(
            func.count(CivilEvent.id)
        ).scalar()
        or 0
    )

    verified_citizens = (
        db.query(
            func.count(Citizen.id)
        )
        .filter(
            Citizen.verification_status
            == "Verified",
        )
        .scalar()
        or 0
    )

    pending_verification = (
        db.query(
            func.count(Citizen.id)
        )
        .filter(
            Citizen.verification_status
            == "Pending Review",
        )
        .scalar()
        or 0
    )

    rejected_citizens = (
        db.query(
            func.count(Citizen.id)
        )
        .filter(
            Citizen.verification_status
            == "Rejected",
        )
        .scalar()
        or 0
    )

    return {
        "total_citizens": total_citizens,
        "total_households": total_households,
        "total_civil_events": total_civil_events,
        "verified_citizens": verified_citizens,
        "pending_verification": pending_verification,
        "rejected_citizens": rejected_citizens,
    }


# ============================================================
# CITIZEN STATISTICS
# ============================================================

def get_citizen_statistics(
    db: Session,
) -> dict:

    total = (
        db.query(
            func.count(Citizen.id)
        ).scalar()
        or 0
    )

    male = (
        db.query(
            func.count(Citizen.id)
        )
        .filter(
            Citizen.gender == "Male",
        )
        .scalar()
        or 0
    )

    female = (
        db.query(
            func.count(Citizen.id)
        )
        .filter(
            Citizen.gender == "Female",
        )
        .scalar()
        or 0
    )

    other = (
        db.query(
            func.count(Citizen.id)
        )
        .filter(
            Citizen.gender == "Other",
        )
        .scalar()
        or 0
    )

    return {
        "total": total,
        "male": male,
        "female": female,
        "other": other,
    }


# ============================================================
# HOUSEHOLD STATISTICS
# ============================================================

def get_household_statistics(
    db: Session,
) -> dict:

    total_households = (
        db.query(
            func.count(Household.id)
        ).scalar()
        or 0
    )

    total_members = (
        db.query(
            func.count(Citizen.id)
        )
        .filter(
            Citizen.household_id.isnot(None),
        )
        .scalar()
        or 0
    )

    households_with_members = (
        db.query(
            func.count(
                func.distinct(
                    Citizen.household_id
                )
            )
        )
        .filter(
            Citizen.household_id.isnot(None),
        )
        .scalar()
        or 0
    )

    average_household_size = 0.0

    if households_with_members:
        average_household_size = (
            total_members
            / households_with_members
        )

    return {
        "total_households": total_households,
        "total_members": total_members,
        "households_with_members": households_with_members,
        "average_household_size": round(
            average_household_size,
            2,
        ),
    }


# ============================================================
# CIVIL REGISTRATION STATISTICS
# ============================================================

def get_civil_registration_statistics(
    db: Session,
) -> dict:

    event_types = [
        "Birth",
        "Death",
        "Marriage",
        "Divorce",
    ]

    result = {}

    for event_type in event_types:

        result[event_type.lower()] = (
            db.query(
                func.count(CivilEvent.id)
            )
            .filter(
                CivilEvent.event_type
                == event_type,
            )
            .scalar()
            or 0
        )

    result["total"] = (
        db.query(
            func.count(CivilEvent.id)
        ).scalar()
        or 0
    )

    return result


# ============================================================
# VERIFICATION STATISTICS
# ============================================================

def get_verification_statistics(
    db: Session,
) -> dict:

    statuses = [
        "Pending Review",
        "Verified",
        "Rejected",
    ]

    result = {}

    for status in statuses:

        result[status.lower().replace(" ", "_")] = (
            db.query(
                func.count(Citizen.id)
            )
            .filter(
                Citizen.verification_status
                == status,
            )
            .scalar()
            or 0
        )

    result["total"] = (
        db.query(
            func.count(Citizen.id)
        ).scalar()
        or 0
    )

    return result
