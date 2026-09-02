"""
Elections Streamlit views.

Presentation layer for voter registration
and election administration.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .repository import ElectionsRepository
from .service import ElectionsService


STATUSES = [
    "Active",
    "Inactive",
    "Suspended",
]


def _get_session():
    try:
        from database import SessionLocal

        return SessionLocal()

    except ImportError:
        pass

    try:
        from database.database import SessionLocal

        return SessionLocal()

    except ImportError:
        pass

    try:
        from db import SessionLocal

        return SessionLocal()

    except ImportError:
        pass

    raise RuntimeError(
        "Database session provider not found."
    )


def _get_models():
    from models import Citizen, VoterRecord

    return Citizen, VoterRecord


def render() -> None:
    st.title("Elections")

    st.caption(
        "Voter registration, electoral records "
        "and polling administration."
    )

    Citizen, VoterRecord = _get_models()

    session = _get_session()

    try:
        repository = ElectionsRepository(
            session=session,
            VoterRecord=VoterRecord,
            Citizen=Citizen,
        )

        service = ElectionsService(
            repository=repository,
            VoterRecord=VoterRecord,
            Citizen=Citizen,
        )

        _render_dashboard(service)

        tabs = st.tabs(
            [
                "Voters",
                "Register Voter",
            ]
        )

        with tabs[0]:
            _render_voters(service)

        with tabs[1]:
            _render_register(service)

    finally:
        session.close()


# =============================================================
# DASHBOARD
# =============================================================

def _render_dashboard(service):
    summary = service.get_election_summary()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Voter Records",
        summary["total"],
    )

    c2.metric(
        "Active Voters",
        summary["active"],
    )

    c3.metric(
        "Recorded Votes",
        summary["voted"],
    )


# =============================================================
# VOTERS
# =============================================================

def _render_voters(service):
    st.subheader("Voter Records")

    c1, c2 = st.columns(2)

    with c1:
        status = st.selectbox(
            "Voter Status",
            [""] + STATUSES,
            key="elections_voter_status",
        )

    with c2:
        constituency = st.text_input(
            "Constituency",
            key="elections_constituency",
        )

    voters = service.list_voters(
        status=status,
        constituency=constituency.strip(),
    )

    if not voters:
        st.info(
            "No voter records found."
        )
        return

    rows = []

    for voter in voters:
        rows.append(
            {
                "ID": getattr(
                    voter,
                    "id",
                    "",
                ),
                "Voter ID": getattr(
                    voter,
                    "voter_id_number",
                    "",
                )
                or "",
                "Citizen ID": getattr(
                    voter,
                    "citizen_id",
                    "",
                ),
                "Status": getattr(
                    voter,
                    "voter_status",
                    "",
                ),
                "Constituency": getattr(
                    voter,
                    "constituency",
                    "",
                )
                or "",
                "Polling Station": getattr(
                    voter,
                    "polling_station_name",
                    "",
                )
                or "",
                "Has Voted": getattr(
                    voter,
                    "has_voted",
                    False,
                ),
                "Voted At": getattr(
                    voter,
                    "voted_at",
                    None,
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )

    voter_ids = [
        voter.id
        for voter in voters
    ]

    selected_id = st.selectbox(
        "Select voter",
        voter_ids,
        format_func=lambda value: (
            next(
                (
                    v.voter_id_number
                    or str(v.id)
                    for v in voters
                    if v.id == value
                ),
                str(value),
            )
        ),
        key="elections_selected_voter",
    )

    voter = next(
        voter
        for voter in voters
        if voter.id == selected_id
    )

    _render_edit_voter(
        service,
        voter,
    )

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        if (
            voter.voter_status == "Active"
            and not voter.has_voted
        ):
            if st.button(
                "Record Vote",
                key=f"record_vote_{voter.id}",
                type="primary",
            ):
                ok, message = service.record_vote(
                    voter.id
                )

                if ok:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    with c2:
        with st.popover(
            "Delete Voter"
        ):
            st.warning(
                "This permanently removes "
                "the voter record."
            )

            confirm = st.checkbox(
                "Confirm deletion",
                key=(
                    f"confirm_delete_"
                    f"{voter.id}"
                ),
            )

            if st.button(
                "Permanently Delete",
                disabled=not confirm,
                key=(
                    f"delete_voter_"
                    f"{voter.id}"
                ),
            ):
                ok, message = service.delete_voter(
                    voter.id
                )

                if ok:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)


# =============================================================
# EDIT VOTER
# =============================================================

def _render_edit_voter(
    service,
    voter,
):
    with st.expander(
        "Edit Voter",
        expanded=True,
    ):
        with st.form(
            f"edit_voter_{voter.id}"
        ):
            voter_id_number = st.text_input(
                "Voter ID Number",
                value=(
                    voter.voter_id_number
                    or ""
                ),
            )

            current_status = (
                voter.voter_status
                if voter.voter_status in STATUSES
                else "Active"
            )

            voter_status = st.selectbox(
                "Status",
                STATUSES,
                index=STATUSES.index(
                    current_status
                ),
            )

            constituency = st.text_input(
                "Constituency",
                value=(
                    voter.constituency
                    or ""
                ),
            )

            polling_station_id = st.text_input(
                "Polling Station ID",
                value=(
                    voter.polling_station_id
                    or ""
                ),
            )

            polling_station_name = st.text_input(
                "Polling Station",
                value=(
                    voter.polling_station_name
                    or ""
                ),
            )

            submitted = st.form_submit_button(
                "Save Changes",
                type="primary",
            )

        if submitted:
            ok, message = service.update_voter(
                voter.id,
                {
                    "voter_id_number": (
                        voter_id_number.strip()
                        or None
                    ),
                    "voter_status": voter_status,
                    "constituency": (
                        constituency.strip()
                        or None
                    ),
                    "polling_station_id": (
                        polling_station_id.strip()
                        or None
                    ),
                    "polling_station_name": (
                        polling_station_name.strip()
                        or None
                    ),
                },
            )

            if ok:
                st.success(message)
                st.rerun()
            else:
                st.error(message)


# =============================================================
# REGISTER VOTER
# =============================================================

def _render_register(service):
    st.subheader(
        "Register Voter"
    )

    with st.form(
        "elections_register_voter"
    ):
        citizen_id = st.text_input(
            "Citizen ID *"
        )

        voter_id_number = st.text_input(
            "Voter ID Number"
        )

        voter_status = st.selectbox(
            "Status",
            STATUSES,
        )

        constituency = st.text_input(
            "Constituency"
        )

        polling_station_id = st.text_input(
            "Polling Station ID"
        )

        polling_station_name = st.text_input(
            "Polling Station Name"
        )

        submitted = st.form_submit_button(
            "Register Voter",
            type="primary",
        )

    if not submitted:
        return

    citizen_id = citizen_id.strip()

    if not citizen_id:
        st.error(
            "Citizen ID is required."
        )
        return

    ok, message, voter_id = (
        service.register_voter(
            {
                "citizen_id": citizen_id,
                "voter_id_number": (
                    voter_id_number.strip()
                    or None
                ),
                "voter_status": voter_status,
                "constituency": (
                    constituency.strip()
                    or None
                ),
                "polling_station_id": (
                    polling_station_id.strip()
                    or None
                ),
                "polling_station_name": (
                    polling_station_name.strip()
                    or None
                ),
            }
        )
    )

    if ok:
        st.success(
            f"{message} "
            f"Voter ID: {voter_id}"
        )
        st.rerun()
    else:
        st.error(message)


__all__ = ["render"]