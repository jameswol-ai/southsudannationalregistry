from __future__ import annotations

import pandas as pd
import streamlit as st

from .service import (
    create_civil_event,
    delete_civil_event,
    get_event_summary,
    list_civil_events,
    update_civil_event,
)

EVENT_TYPES = ["Birth", "Death", "Marriage", "Divorce", "Other"]
STATUSES = ["Pending Review", "Registered", "Approved", "Rejected"]


def render() -> None:
    st.title("Civil Registration")
    st.caption("Birth, death, marriage and other civil event registration.")
    summary = get_event_summary()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Events", summary["total"])
    c2.metric("Births", summary["births"])
    c3.metric("Deaths", summary["deaths"])
    c4.metric("Marriages", summary["marriages"])
    c5.metric("Pending", summary["pending"])
    tabs = st.tabs(["Events", "Register Event"])
    with tabs[0]:
        _events()
    with tabs[1]:
        _register()


def _events() -> None:
    c1, c2 = st.columns(2)
    with c1:
        event_type = st.selectbox("Event Type", [""] + EVENT_TYPES, key="civil_event_filter_type")
    with c2:
        status = st.selectbox("Status", [""] + STATUSES, key="civil_event_filter_status")

    events = list_civil_events(event_type=event_type, status=status)
    if not events:
        st.info("No civil events found.")
        return

    st.dataframe(pd.DataFrame([{
        "Reference": e.reference_number,
        "Type": e.event_type,
        "Date": e.event_date,
        "Citizen ID": e.citizen_id or "",
        "Registration Centre": e.registration_centre or "",
        "Document": e.document_number or "",
        "Status": e.status,
    } for e in events]), use_container_width=True, hide_index=True)

    selected = st.selectbox(
        "Select event",
        [e.id for e in events],
        format_func=lambda value: next((e.reference_number for e in events if e.id == value), value),
        key="selected_civil_event",
    )
    event = next(e for e in events if e.id == selected)

    with st.expander("Edit Event", expanded=True):
        with st.form(f"edit_civil_event_{event.id}"):
            c1, c2 = st.columns(2)
            with c1:
                event_type_value = st.selectbox("Event Type", EVENT_TYPES, index=EVENT_TYPES.index(event.event_type) if event.event_type in EVENT_TYPES else 0)
                event_date = st.date_input("Event Date", value=event.event_date)
                citizen_id = st.text_input("Citizen ID", value=event.citizen_id or "")
            with c2:
                registration_centre = st.text_input("Registration Centre", value=event.registration_centre or "")
                document_number = st.text_input("Document Number", value=event.document_number or "")
                status_value = st.selectbox("Status", STATUSES, index=STATUSES.index(event.status) if event.status in STATUSES else 0)
            notes = st.text_area("Notes", value=event.notes or "")
            save = st.form_submit_button("Save Changes", type="primary")
        if save:
            ok, message = update_civil_event(event.id, {
                "event_type": event_type_value,
                "event_date": event_date,
                "citizen_id": citizen_id.strip() or None,
                "registration_centre": registration_centre.strip() or None,
                "document_number": document_number.strip() or None,
                "status": status_value,
                "notes": notes.strip() or None,
            })
            if ok:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with st.expander("Delete Event"):
        st.warning("Deletion permanently removes this civil registration event.")
        confirm = st.checkbox("Confirm permanent deletion", key=f"confirm_delete_civil_{event.id}")
        if st.button("Delete Event", disabled=not confirm, key=f"delete_civil_{event.id}"):
            ok, message = delete_civil_event(event.id)
            if ok:
                st.success(message)
                st.rerun()
            else:
                st.error(message)


def _register() -> None:
    st.subheader("Register Civil Event")
    with st.form("register_civil_event"):
        reference = st.text_input("Reference Number *")
        event_type = st.selectbox("Event Type", EVENT_TYPES)
        event_date = st.date_input("Event Date")
        citizen_id = st.text_input("Citizen ID", help="Optional existing Citizen ID.")
        registration_centre = st.text_input("Registration Centre")
        document_number = st.text_input("Document Number")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Register Event", type="primary")
    if submitted:
        if not reference.strip():
            st.error("Reference number is required.")
            return
        ok, message, _ = create_civil_event({
            "reference_number": reference,
            "event_type": event_type,
            "event_date": event_date,
            "citizen_id": citizen_id.strip() or None,
            "registration_centre": registration_centre,
            "document_number": document_number,
            "notes": notes,
        })
        if ok:
            st.success(message)
            st.rerun()
        else:
            st.error(message)
