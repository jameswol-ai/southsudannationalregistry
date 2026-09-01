"""
Registry Reports module.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from database.database import SessionLocal
from services.reporting_service import (
    get_citizen_statistics,
    get_civil_registration_statistics,
    get_household_statistics,
    get_verification_statistics,
)


def render() -> None:

    st.title("Reports")

    st.caption(
        "National registry statistics and operational reporting."
    )

    db = SessionLocal()

    try:

        citizen_stats = get_citizen_statistics(
            db
        )

        household_stats = get_household_statistics(
            db
        )

        civil_stats = get_civil_registration_statistics(
            db
        )

        verification_stats = get_verification_statistics(
            db
        )

    finally:

        db.close()

    # ========================================================
    # CITIZENS
    # ========================================================

    st.subheader("Citizen Demographics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total",
            f"{citizen_stats['total']:,}",
        )

    with col2:
        st.metric(
            "Male",
            f"{citizen_stats['male']:,}",
        )

    with col3:
        st.metric(
            "Female",
            f"{citizen_stats['female']:,}",
        )

    with col4:
        st.metric(
            "Other",
            f"{citizen_stats['other']:,}",
        )

    st.divider()

    # ========================================================
    # HOUSEHOLDS
    # ========================================================

    st.subheader("Households")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Households",
            f"{household_stats['total_households']:,}",
        )

    with col2:

        st.metric(
            "Members",
            f"{household_stats['total_members']:,}",
        )

    with col3:

        st.metric(
            "Average Household Size",
            household_stats[
                "average_household_size"
            ],
        )

    st.divider()

    # ========================================================
    # CIVIL REGISTRATION
    # ========================================================

    st.subheader("Civil Registration")

    civil_df = pd.DataFrame(
        {
            "Event Type": [
                "Birth",
                "Death",
                "Marriage",
                "Divorce",
            ],
            "Records": [
                civil_stats["birth"],
                civil_stats["death"],
                civil_stats["marriage"],
                civil_stats["divorce"],
            ],
        }
    )

    st.dataframe(
        civil_df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # ========================================================
    # VERIFICATION
    # ========================================================

    st.subheader("Verification")

    verification_df = pd.DataFrame(
        {
            "Status": [
                "Pending Review",
                "Verified",
                "Rejected",
            ],
            "Citizens": [
                verification_stats[
                    "pending_review"
                ],
                verification_stats[
                    "verified"
                ],
                verification_stats[
                    "rejected"
                ],
            ],
        }
    )

    st.dataframe(
        verification_df,
        use_container_width=True,
        hide_index=True,
  )
