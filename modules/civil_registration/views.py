"""
Civil Registration module views.

South Sudan National Registry
-----------------------------

Presentation layer for civil registration records.

Architecture:

    Streamlit
        |
        v
    views.py
        |
        v
    service.py
        |
        v
    repository.py
        |
        v
    SQLAlchemy models
"""

from __future__ import annotations

from datetime import date
from typing import Any, Optional

import streamlit as st

from modules.civil_registration.service import (
    archive_civil_event,
    create_civil_event,
    get_civil_event,
    get_civil_registration_summary,
    list_civil_events,
    search_citizens,
    update_civil_event,
)


# ============================================================
# CONSTANTS
# ============================================================

EVENT_TYPES = [
    "Birth",
    "Death",
    "Marriage",
    "Divorce",
    "Adoption",
    "Name Change",
    "Other",
]

EVENT_STATUSES = [
    "Pending Review",
    "Registered",
    "Verified",
    "Rejected",
    "Archived",
]

PAGE_SIZE = 25


# ============================================================
# HELPERS
# ============================================================

def _safe_text(value: Any) -> str:
    """Return a safely trimmed string."""
    if value is None:
        return ""
    return str(value).strip()


def _format_date(value: Any) -> str:
    """Format a date for display."""
    if value is None:
        return "Not recorded"

    if isinstance(value, date):
        return value.strftime("%d %b %Y")

    return str(value)


def _get_event_value(event: Any, field: str, default: Any = None) -> Any:
    """Safely retrieve a model attribute."""
    return getattr(event, field, default)


def _event_label(event: Any) -> str:
    """Build a compact event label."""
    reference = _safe_text(
        _get_event_value(event, "reference_number")
    )

    event_type = _safe_text(
        _get_event_value(event, "event_type")
    )

    event_date = _format_date(
        _get_event_value(event, "event_date")
    )

    if reference:
        return f"{reference} • {event_type} • {event_date}"

    return f"{event_type} • {event_date}"


def _show_message(
    message: Optional[str],
    message_type: str = "info",
) -> None:
    """Display a Streamlit message when supplied."""
    if not message:
        return

    if message_type == "success":
        st.success(message)
    elif message_type == "error":
        st.error(message)
    elif message_type == "warning":
        st.warning(message)
    else:
        st.info(message)


# ============================================================
# SUMMARY
# ============================================================

def _render_summary() -> None:
    """Render Civil Registration KPI cards."""

    summary = get_civil_registration_summary()

    total = int(summary.get("total", 0))
    births = int(summary.get("births", 0))
    deaths = int(summary.get("deaths", 0))
    marriages = int(summary.get("marriages", 0))
    divorces = int(summary.get("divorces", 0))
    pending = int(summary.get("pending", 0))
    verified = int(summary.get("verified", 0))

    st.markdown("### Civil Registration Overview")

    columns = st.columns(4)

    with columns[0]:
        st.metric(
            "Total Events",
            total,
        )

    with columns[1]:
        st.metric(
            "Birth Records",
            births,
        )

    with columns[2]:
        st.metric(
            "Death Records",
            deaths,
        )

    with columns[3]:
        st.metric(
            "Marriage Records",
            marriages,
        )

    columns = st.columns(3)

    with columns[0]:
        st.metric(
            "Divorce Records",
            divorces,
        )

    with columns[1]:
        st.metric(
            "Pending Review",
            pending,
        )

    with columns[2]:
        st.metric(
            "Verified",
            verified,
        )


# ============================================================
# EVENT FORM
# ============================================================

def _render_event_form(
    event: Any = None,
) -> None:
    """
    Render create/update civil registration form.

    If event is None, a new record is created.
    Otherwise the existing record is updated.
    """

    editing = event is not None

    title = (
        "Edit Civil Registration Record"
        if editing
        else "Register Civil Event"
    )

    st.markdown(f"### {title}")

    existing_reference = _safe_text(
        _get_event_value(event, "reference_number")
    )

    existing_event_type = _safe_text(
        _get_event_value(event, "event_type")
    )

    existing_citizen_id = _safe_text(
        _get_event_value(event, "citizen_id")
    )

    existing_event_date = _get_event_value(
        event,
        "event_date",
    )

    existing_registration_centre = _safe_text(
        _get_event_value(event, "registration_centre")
    )

    existing_document_number = _safe_text(
        _get_event_value(event, "document_number")
    )

    existing_status = _safe_text(
        _get_event_value(event, "status")
    ) or "Pending Review"

    existing_notes = _safe_text(
        _get_event_value(event, "notes")
    )

    with st.form(
        key=(
            "civil_registration_edit_form"
            if editing
            else "civil_registration_create_form"
        ),
        clear_on_submit=not editing,
    ):

        col1, col2 = st.columns(2)

        with col1:
            reference_number = st.text_input(
                "Reference Number *",
                value=existing_reference,
                placeholder="e.g. CR-2026-000001",
                disabled=editing,
            )

        with col2:
            event_type = st.selectbox(
                "Event Type *",
                EVENT_TYPES,
                index=(
                    EVENT_TYPES.index(existing_event_type)
                    if existing_event_type in EVENT_TYPES
                    else 0
                ),
            )

        col1, col2 = st.columns(2)

        with col1:
            event_date = st.date_input(
                "Event Date *",
                value=(
                    existing_event_date
                    if isinstance(existing_event_date, date)
                    else date.today()
                ),
            )

        with col2:
            status = st.selectbox(
                "Registration Status",
                EVENT_STATUSES,
                index=(
                    EVENT_STATUSES.index(existing_status)
                    if existing_status in EVENT_STATUSES
                    else 0
                ),
            )

        st.markdown("#### Citizen")

        citizen_query = st.text_input(
            "Search Citizen",
            placeholder=(
                "Enter National ID or citizen name"
            ),
        )

        selected_citizen_id = existing_citizen_id

        if citizen_query.strip():

            citizens = search_citizens(
                citizen_query.strip()
            )

            if citizens:

                options = {
                    (
                        f"{_safe_text(getattr(c, 'full_name', ''))}"
                        f" | "
                        f"{_safe_text(getattr(c, 'national_id', ''))}"
                    ): getattr(c, "id", None)
                    for c in citizens
                }

                labels = list(options.keys())

                selected_label = st.selectbox(
                    "Select Citizen",
                    labels,
                )

                selected_citizen_id = options.get(
                    selected_label
                )

            else:
                st.warning(
                    "No citizens were found for that search."
                )

        elif existing_citizen_id:
            st.caption(
                f"Linked Citizen ID: {existing_citizen_id}"
            )

        else:
            st.caption(
                "Search for a citizen to link this civil event."
            )

        col1, col2 = st.columns(2)

        with col1:
            registration_centre = st.text_input(
                "Registration Centre",
                value=existing_registration_centre,
                placeholder="Registration office / centre",
            )

        with col2:
            document_number = st.text_input(
                "Document Number",
                value=existing_document_number,
                placeholder="Certificate or document number",
            )

        notes = st.text_area(
            "Notes",
            value=existing_notes,
            placeholder=(
                "Additional information about this civil event"
            ),
        )

        submitted = st.form_submit_button(
            "Update Record"
            if editing
            else "Register Civil Event",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    if not reference_number.strip():
        st.error("Reference Number is required.")
        return

    if not event_type.strip():
        st.error("Event Type is required.")
        return

    if not event_date:
        st.error("Event Date is required.")
        return

    if editing:

        result = update_civil_event(
            event_id=str(
                _get_event_value(event, "id")
            ),
            reference_number=reference_number.strip(),
            event_type=event_type.strip(),
            citizen_id=selected_citizen_id or None,
            event_date=event_date,
            registration_centre=(
                registration_centre.strip()
                or None
            ),
            document_number=(
                document_number.strip()
                or None
            ),
            status=status.strip(),
            notes=notes.strip() or None,
        )

    else:

        result = create_civil_event(
            reference_number=reference_number.strip(),
            event_type=event_type.strip(),
            citizen_id=selected_citizen_id or None,
            event_date=event_date,
            registration_centre=(
                registration_centre.strip()
                or None
            ),
            document_number=(
                document_number.strip()
                or None
            ),
            status=status.strip(),
            notes=notes.strip() or None,
        )

    if result.get("success"):
        st.success(
            result.get(
                "message",
                "Civil registration record saved.",
            )
        )

        st.session_state[
            "civil_registration_selected_id"
        ] = None

        st.rerun()

    else:
        st.error(
            result.get(
                "message",
                "Unable to save the civil registration record.",
            )
        )


# ============================================================
# EVENT DETAILS
# ============================================================

def _render_event_details(event: Any) -> None:
    """Render details for a selected civil event."""

    if event is None:
        st.info("Select a civil registration record.")
        return

    event_id = _get_event_value(event, "id")

    st.markdown("### Registration Record")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Reference Number**")
        st.write(
            _safe_text(
                _get_event_value(
                    event,
                    "reference_number",
                )
            )
        )

    with col2:
        st.markdown("**Event Type**")
        st.write(
            _safe_text(
                _get_event_value(
                    event,
                    "event_type",
                )
            )
        )

    with col3:
        st.markdown("**Event Date**")
        st.write(
            _format_date(
                _get_event_value(
                    event,
                    "event_date",
                )
            )
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Status**")
        st.write(
            _safe_text(
                _get_event_value(
                    event,
                    "status",
                )
            )
        )

    with col2:
        st.markdown("**Registration Centre**")
        st.write(
            _safe_text(
                _get_event_value(
                    event,
                    "registration_centre",
                )
            )
            or "Not recorded"
        )

    with col3:
        st.markdown("**Document Number**")
        st.write(
            _safe_text(
                _get_event_value(
                    event,
                    "document_number",
                )
            )
            or "Not recorded"
        )

    citizen_id = _get_event_value(
        event,
        "citizen_id",
    )

    if citizen_id:
        st.markdown("**Linked Citizen ID**")
        st.code(str(citizen_id))

    notes = _safe_text(
        _get_event_value(
            event,
            "notes",
        )
    )

    if notes:
        st.markdown("**Notes**")
        st.write(notes)

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "Edit Record",
            key=f"edit_civil_event_{event_id}",
            use_container_width=True,
        ):
            st.session_state[
                "civil_registration_edit_id"
            ] = str(event_id)

            st.session_state[
                "civil_registration_selected_id"
            ] = None

            st.rerun()

    with col2:
        if st.button(
            "Archive Record",
            key=f"archive_civil_event_{event_id}",
            use_container_width=True,
        ):
            result = archive_civil_event(
                str(event_id)
            )

            if result.get("success"):
                st.success(
                    result.get(
                        "message",
                        "Record archived.",
                    )
                )
                st.session_state[
                    "civil_registration_selected_id"
                ] = None
                st.rerun()
            else:
                st.error(
                    result.get(
                        "message",
                        "Unable to archive record.",
                    )
                )

    with col3:
        if st.button(
            "Close",
            key=f"close_civil_event_{event_id}",
            use_container_width=True,
        ):
            st.session_state[
                "civil_registration_selected_id"
            ] = None
            st.rerun()


# ============================================================
# RECORD LIST
# ============================================================

def _render_event_list() -> None:
    """Render searchable civil registration records."""

    st.markdown("### Civil Registration Records")

    col1, col2, col3 = st.columns(
        [2, 1, 1]
    )

    with col1:
        search_term = st.text_input(
            "Search Records",
            placeholder=(
                "Reference, event type, "
                "document number or citizen ID"
            ),
            key="civil_registration_search",
        )

    with col2:
        event_type_filter = st.selectbox(
            "Event Type",
            ["All"] + EVENT_TYPES,
            key="civil_registration_event_filter",
        )

    with col3:
        status_filter = st.selectbox(
            "Status",
            ["All"] + EVENT_STATUSES,
            key="civil_registration_status_filter",
        )

    events = list_civil_events(
        search=search_term.strip() or None,
        event_type=(
            None
            if event_type_filter == "All"
            else event_type_filter
        ),
        status=(
            None
            if status_filter == "All"
            else status_filter
        ),
        limit=PAGE_SIZE,
    )

    if not events:
        st.info(
            "No civil registration records found."
        )
        return

    st.caption(
        f"Showing {len(events)} record(s)."
    )

    for event in events:

        event_id = _get_event_value(
            event,
            "id",
        )

        reference = _safe_text(
            _get_event_value(
                event,
                "reference_number",
            )
        )

        event_type = _safe_text(
            _get_event_value(
                event,
                "event_type",
            )
        )

        event_status = _safe_text(
            _get_event_value(
                event,
                "status",
            )
        )

        event_date = _format_date(
            _get_event_value(
                event,
                "event_date",
            )
        )

        with st.container(
            border=True,
        ):

            col1, col2, col3, col4 = st.columns(
                [2, 2, 2, 1]
            )

            with col1:
                st.markdown(
                    f"**{reference or 'No Reference'}**"
                )

            with col2:
                st.write(
                    event_type or "Unknown Event"
                )

            with col3:
                st.write(event_date)

            with col4:
                if st.button(
                    "View",
                    key=f"view_civil_event_{event_id}",
                    use_container_width=True,
                ):
                    st.session_state[
                        "civil_registration_selected_id"
                    ] = str(event_id)

                    st.session_state[
                        "civil_registration_edit_id"
                    ] = None

                    st.rerun()

            st.caption(
                f"Status: {event_status or 'Unknown'}"
            )


# ============================================================
# MAIN VIEW
# ============================================================

def render() -> None:
    """
    Render the Civil Registration module.

    This function is the public entry point expected by
    modules.registry.
    """

    st.title("Civil Registration")

    st.caption(
        "Registration and management of births, deaths, "
        "marriages, divorces and other civil events."
    )

    _render_summary()

    st.divider()

    selected_id = st.session_state.get(
        "civil_registration_selected_id"
    )

    edit_id = st.session_state.get(
        "civil_registration_edit_id"
    )

    if edit_id:

        event = get_civil_event(
            str(edit_id)
        )

        if event is None:
            st.error(
                "The selected civil registration record "
                "could not be found."
            )

            st.session_state[
                "civil_registration_edit_id"
            ] = None

        else:
            _render_event_form(event)

            if st.button(
                "Cancel Editing",
                use_container_width=True,
            ):
                st.session_state[
                    "civil_registration_edit_id"
                ] = None
                st.rerun()

            return

    if selected_id:

        event = get_civil_event(
            str(selected_id)
        )

        if event is None:
            st.error(
                "The selected civil registration record "
                "could not be found."
            )

            st.session_state[
                "civil_registration_selected_id"
            ] = None

            return

        _render_event_details(event)
        return

    create_tab, records_tab = st.tabs(
        [
            "Register Event",
            "Registration Records",
        ]
    )

    with create_tab:
        _render_event_form()

    with records_tab:
        _render_event_list()