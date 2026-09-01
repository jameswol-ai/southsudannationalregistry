"""
Registry Overview module.
"""

from __future__ import annotations

import streamlit as st

from database.database import SessionLocal
from services.reporting_service import get_dashboard_summary


def render() -> None:

    st.title("South Sudan National Registry")
    st.caption(
        "National population, civil registration and identity platform."
    )

    db = SessionLocal()

    try:
        summary = get_dashboard_summary(db)

    finally:
        db.close()

    st.subheader("Registry Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Registered Citizens",
            f"{summary['total_citizens']:,}",
        )

    with col2:
        st.metric(
            "Households",
            f"{summary['total_households']:,}",
        )

    with col3:
        st.metric(
            "Civil Events",
            f"{summary['total_civil_events']:,}",
        )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Verified Citizens",
            f"{summary['verified_citizens']:,}",
        )

    with col2:
        st.metric(
            "Pending Verification",
            f"{summary['pending_verification']:,}",
        )

    with col3:
        st.metric(
            "Rejected",
            f"{summary['rejected_citizens']:,}",
        )

    st.divider()

    st.subheader("Registry Status")

    verification_total = (
        summary["verified_citizens"]
        + summary["pending_verification"]
        + summary["rejected_citizens"]
    )

    if verification_total == 0:

        st.info(
            "No citizen records have been registered yet."
        )

    else:

        verified_percentage = (
            summary["verified_citizens"]
            / verification_total
        ) * 100

        st.progress(
            min(
                max(
                    verified_percentage / 100,
                    0.0,
                ),
                1.0,
            )
        )

        st.write(
            f"Verification completion: "
            f"**{verified_percentage:.1f}%**"
      )
