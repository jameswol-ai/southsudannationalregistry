"""
Citizen verification module.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from database.database import SessionLocal
from services.verification_service import (
    get_verification_queue,
    reject_citizen,
    verify_citizen,
)


def render() -> None:

    st.title("Verification")

    st.caption(
        "Review citizen registrations and manage verification decisions."
    )

    db = SessionLocal()

    try:

        queue = get_verification_queue(
            db=db,
            status="Pending Review",
            limit=500,
        )

    finally:

        db.close()

    # ========================================================
    # QUEUE SUMMARY
    # ========================================================

    st.metric(
        "Pending Verification",
        f"{len(queue):,}",
    )

    st.divider()

    if not queue:

        st.success(
            "There are no citizens awaiting verification."
        )

        return

    # ========================================================
    # QUEUE
    # ========================================================

    st.subheader("Verification Queue")

    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Citizen ID":
                        citizen.id,
                    "National ID":
                        citizen.national_id or "",
                    "Name":
                        citizen.full_name,
                    "Gender":
                        citizen.gender,
                    "State":
                        citizen.state_or_region,
                    "County / Payam":
                        citizen.county_or_payam,
                    "Status":
                        citizen.verification_status,
                }
                for citizen in queue
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # ========================================================
    # DECISION
    # ========================================================

    st.subheader("Verification Decision")

    citizen_options = {
        f"{citizen.full_name} — {citizen.id}":
            citizen.id
        for citizen in queue
    }

    selected = st.selectbox(
        "Citizen",
        list(citizen_options.keys()),
    )

    citizen_id = citizen_options[selected]

    decision = st.radio(
        "Decision",
        [
            "Verify",
            "Reject",
        ],
        horizontal=True,
    )

    notes = st.text_area(
        "Verification Notes / Rejection Reason"
    )

    if decision == "Reject" and not notes.strip():

        st.warning(
            "A rejection reason is required before rejecting a record."
        )

    if st.button(
        "Apply Decision",
        type="primary",
    ):

        if decision == "Reject" and not notes.strip():

            st.error(
                "Please provide a rejection reason."
            )

            return

        db = SessionLocal()

        try:

            if decision == "Verify":

                citizen = verify_citizen(
                    db=db,
                    citizen_id=citizen_id,
                    username="streamlit",
                    notes=notes.strip() or None,
                )

                st.success(
                    f"{citizen.full_name} has been verified."
                )

            else:

                citizen = reject_citizen(
                    db=db,
                    citizen_id=citizen_id,
                    username="streamlit",
                    reason=notes.strip(),
                )

                st.success(
                    f"{citizen.full_name} has been rejected."
                )

            st.rerun()

        except Exception as exc:

            db.rollback()

            st.error(
                f"Verification action failed: {exc}"
            )

        finally:

            db.close()
