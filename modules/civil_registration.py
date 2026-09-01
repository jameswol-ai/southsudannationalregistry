"""
Civil Registration module.

Handles registration and review of civil events:

    - Birth
    - Death
    - Marriage
    - Divorce
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from database.database import SessionLocal
from services.registration_service import (
    create_civil_event,
    list_civil_events,
)


EVENT_TYPES = [
    "Birth",
    "Death",
    "Marriage",
    "Divorce",
]


def _event_rows(events):

    return [
        {
            "Reference": event.reference_number,
            "Event Type": event.event_type,
            "Citizen ID": event.citizen_id or "",
            "Event Date": event.event_date,
            "Registration Centre": (
                event.registration_centre or ""
            ),
            "Document Number": (
                event.document_number or ""
            ),
            "Status": event.status,
        }
        for event in events
    ]


def render() -> None:

    st.title("Civil Registration")

    st.caption(
        "Register and manage civil status events "
        "within the national registry."
    )

    tab_register, tab_records = st.tabs(
        [
            "Register Event",
            "Civil Records",
        ]
    )

    # ========================================================
    # REGISTER EVENT
    # ========================================================

    with tab_register:

        st.subheader("New Civil Registration")

        with st.form("civil_event_form"):

            event_type = st.selectbox(
                "Event Type",
                EVENT_TYPES,
            )

            citizen_id = st.text_input(
                "Citizen ID",
                help="Leave blank where the event is not yet linked to a citizen.",
            )

            event_date = st.date_input(
                "Event Date",
                value=date.today(),
            )

            registration_centre = st.text_input(
                "Registration Centre"
            )

            document_number = st.text_input(
                "Document / Certificate Number"
            )

            notes = st.text_area(
                "Notes"
            )

            submitted = st.form_submit_button(
                "Register Civil Event",
                type="primary",
            )

        if submitted:

            db = SessionLocal()

            try:

                event = create_civil_event(
                    db=db,
                    data={
                        "event_type": event_type,
                        "citizen_id":
                            citizen_id.strip() or None,
                        "event_date": event_date,
                        "registration_centre":
                            registration_centre.strip() or None,
                        "document_number":
                            document_number.strip() or None,
                        "status": "Pending Review",
                        "notes": notes.strip() or None,
                    },
                    username="streamlit",
                )

                st.success(
                    f"{event_type} registration created: "
                    f"{event.reference_number}"
                )

            except Exception as exc:

                db.rollback()

                st.error(
                    f"Registration failed: {exc}"
                )

            finally:

                db.close()

    # ========================================================
    # RECORDS
    # ========================================================

    with tab_records:

        st.subheader("Civil Registration Records")

        event_filter = st.selectbox(
            "Filter by Event Type",
            ["All"] + EVENT_TYPES,
        )

        db = SessionLocal()

        try:

            events = list_civil_events(
                db=db,
                event_type=(
                    None
                    if event_filter == "All"
                    else event_filter
                ),
                limit=500,
            )

        finally:

            db.close()

        if events:

            st.dataframe(
                pd.DataFrame(
                    _event_rows(events)
                ),
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "No civil registration records found."
          )
