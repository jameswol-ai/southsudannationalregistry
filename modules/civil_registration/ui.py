from __future__ import annotations

import pandas as pd
import streamlit as st

from .service import (
    create_civil_event,
    get_event_summary,
    list_civil_events,
    update_civil_event,
)


def render() -> None:
    st.title("Civil Registration")
    st.caption(
        "Birth, death, marriage and other civil event registration."
    )

    summary = get_event_summary()

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Total Events", summary["total"])
    c2.metric("Births", summary["births"])
    c3.metric("Deaths", summary["deaths"])
    c4.metric("Marriages", summary["marriages"])
    c5.metric("Pending", summary["pending"])

    tabs = st.tabs(
        [
            "Events",
            "Register Event",
        ]
    )

    with tabs[0]:
        _events()

    with tabs[1]:
        _register()


def _events() -> None:
    event_type = st.selectbox(
        "Event Type",
        [
            "",
            "Birth",
            "Death",
            "Marriage",
            "Divorce",
            "Other",
        ],
    )

    status = st.selectbox(
        "Status",
        [
            "",
            "Pending Review",
            "Registered",
            "Approved",
            "Rejected",
        ],
    )

    events = list_civil_events(
        event_type=event_type,
        status=status,
    )

    if not events:
        st.info("No civil events found.")
        return

    data = pd.DataFrame(
        [
            {
                "Reference": event.reference_number,
                "Type": event.event_type,
                "Date": event.event_date,
                "Citizen ID": event.citizen_id or "",
                "Registration Centre": (
                    event.registration_centre or ""
                ),
                "Document": event.document_number or "",
                "Status": event.status,
            }
            for event in events
        ]
    )

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True,
    )

    selected = st.selectbox(
        "Select event",
        [event.id for event in events],
        format_func=lambda value: next(
            (
                event.reference_number
                for event in events
                if event.id == value
            ),
            value,
        ),
    )

    event = next(
        event for event in events
        if event.id == selected
    )

    with st.expander("Update Event"):
        with st.form(f"edit_event_{event.id}"):

            status = st.selectbox(
                "Status",
                [
                    "Pending Review",
                    "Registered",
                    "Approved",
                    "Rejected",
                ],
                index=(
                    [
                        "Pending Review",
                        "Registered",
                        "Approved",
                        "Rejected",
                    ].index(event.status)
                    if event.status in [
                        "Pending Review",
                        "Registered",
                        "Approved",
                        "Rejected",
                    ]
                    else 0
                ),
            )

            notes = st.text_area(
                "Notes",
                value=event.notes or "",
            )

            submitted = st.form_submit_button(
                "Save Changes",
                type="primary",
            )

            if submitted:
                ok, message = update_civil_event(
                    event.id,
                    {
                        "status": status,
                        "notes": notes or None,
                    },
                )

                if ok:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)


def _register() -> None:
    st.subheader("Register Civil Event")

    with st.form("register_civil_event"):

        reference = st.text_input(
            "Reference Number *"
        )

        event_type = st.selectbox(
            "Event Type",
            [
                "Birth",
                "Death",
                "Marriage",
                "Divorce",
                "Other",
            ],
        )

        event_date = st.date_input(
            "Event Date"
        )

        citizen_id = st.text_input(
            "Citizen ID",
            help="Optional existing Citizen ID.",
        )

        registration_centre = st.text_input(
            "Registration Centre"
        )

        document_number = st.text_input(
            "Document Number"
        )

        notes = st.text_area("Notes")

        submitted = st.form_submit_button(
            "Register Event",
            type="primary",
        )

        if submitted:
            if not reference.strip():
                st.error("Reference number is required.")
                return

            ok, message, _ = create_civil_event(
                {
                    "reference_number": reference,
                    "event_type": event_type,
                    "event_date": event_date,
                    "citizen_id": citizen_id,
                    "registration_centre": registration_centre,
                    "document_number": document_number,
                    "notes": notes,
                }
            )

            if ok:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
