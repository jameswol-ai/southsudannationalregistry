"""
Civil Registration module.

Handles registration, editing, review and deletion of civil events.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from database.database import SessionLocal
from services.registration_service import (
    create_civil_event,
    delete_civil_event,
    list_civil_events,
    update_civil_event,
)


EVENT_TYPES = ["Birth", "Death", "Marriage", "Divorce"]
STATUSES = ["Pending Review", "Registered", "Verified", "Rejected", "Cancelled"]


def _event_rows(events):
    return [
        {
            "Reference": event.reference_number,
            "Event Type": event.event_type,
            "Citizen ID": event.citizen_id or "",
            "Event Date": event.event_date,
            "Registration Centre": event.registration_centre or "",
            "Document Number": event.document_number or "",
            "Status": event.status,
        }
        for event in events
    ]


def render() -> None:
    st.title("Civil Registration")
    st.caption("Register and manage births, deaths, marriages and divorces.")

    tab_register, tab_records = st.tabs(["Register Event", "Civil Records"])

    with tab_register:
        _register_event()

    with tab_records:
        _records()


def _register_event() -> None:
    st.subheader("New Civil Registration")
    with st.form("civil_event_form"):
        event_type = st.selectbox("Event Type", EVENT_TYPES)
        citizen_id = st.text_input("Citizen ID", help="Optional until the event is linked to a citizen.")
        event_date = st.date_input("Event Date", value=date.today())
        registration_centre = st.text_input("Registration Centre")
        document_number = st.text_input("Document / Certificate Number")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Register Civil Event", type="primary")

    if not submitted:
        return

    db = SessionLocal()
    try:
        event = create_civil_event(
            db=db,
            data={
                "event_type": event_type,
                "citizen_id": citizen_id.strip() or None,
                "event_date": event_date,
                "registration_centre": registration_centre.strip() or None,
                "document_number": document_number.strip() or None,
                "status": "Pending Review",
                "notes": notes.strip() or None,
            },
            username="streamlit",
        )
        st.success(f"{event_type} registration created: {event.reference_number}")
        st.rerun()
    except Exception as exc:
        db.rollback()
        st.error(f"Registration failed: {exc}")
    finally:
        db.close()


def _records() -> None:
    st.subheader("Civil Registration Records")
    event_filter = st.selectbox("Filter by Event Type", ["All"] + EVENT_TYPES, key="civil_event_filter")

    db = SessionLocal()
    try:
        events = list_civil_events(db=db, event_type=None if event_filter == "All" else event_filter, limit=500)
    finally:
        db.close()

    if not events:
        st.info("No civil registration records found.")
        return

    st.dataframe(pd.DataFrame(_event_rows(events)), use_container_width=True, hide_index=True)

    selected_id = st.selectbox(
        "Select record",
        [event.id for event in events],
        format_func=lambda value: next((e.reference_number for e in events if e.id == value), value),
        key="civil_selected_record",
    )
    event = next(e for e in events if e.id == selected_id)

    with st.expander("Edit Civil Record", expanded=True):
        with st.form(f"edit_civil_event_{event.id}"):
            event_type = st.selectbox("Event Type", EVENT_TYPES, index=EVENT_TYPES.index(event.event_type) if event.event_type in EVENT_TYPES else 0)
            citizen_id = st.text_input("Citizen ID", value=event.citizen_id or "")
            event_date = st.date_input("Event Date", value=event.event_date or date.today())
            centre = st.text_input("Registration Centre", value=event.registration_centre or "")
            document_number = st.text_input("Document / Certificate Number", value=event.document_number or "")
            status = st.selectbox("Status", STATUSES, index=STATUSES.index(event.status) if event.status in STATUSES else 0)
            notes = st.text_area("Notes", value=getattr(event, "notes", "") or "")
            save = st.form_submit_button("Save Changes", type="primary")

        if save:
            db = SessionLocal()
            try:
                update_civil_event(db, event.id, {
                    "event_type": event_type,
                    "citizen_id": citizen_id.strip() or None,
                    "event_date": event_date,
                    "registration_centre": centre.strip() or None,
                    "document_number": document_number.strip() or None,
                    "status": status,
                    "notes": notes.strip() or None,
                }, username="streamlit")
                st.success("Civil record updated successfully.")
                st.rerun()
            except Exception as exc:
                db.rollback()
                st.error(f"Unable to update record: {exc}")
            finally:
                db.close()

    with st.expander("Delete Civil Record"):
        st.warning("Deletion permanently removes this civil event and its registry history entry.")
        confirm = st.checkbox("I understand this record will be permanently deleted.", key=f"confirm_delete_civil_{event.id}")
        if st.button("Delete Civil Record", disabled=not confirm, key=f"delete_civil_{event.id}"):
            db = SessionLocal()
            try:
                if delete_civil_event(db, event.id, username="streamlit"):
                    st.success("Civil record deleted successfully.")
                    st.rerun()
                else:
                    st.error("Civil record was not found.")
            except Exception as exc:
                db.rollback()
                st.error(f"Unable to delete record: {exc}")
            finally:
                db.close()
