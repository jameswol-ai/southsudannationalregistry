from __future__ import annotations

import pandas as pd
import streamlit as st

from .service import (
    get_election_summary,
    list_voters,
    record_vote,
    register_voter,
    update_voter,
)


def render() -> None:
    st.title("Elections")
    st.caption(
        "Voter registration, electoral records and polling administration."
    )

    summary = get_election_summary()

    c1, c2, c3 = st.columns(3)

    c1.metric("Voter Records", summary["total"])
    c2.metric("Active Voters", summary["active"])
    c3.metric("Recorded Votes", summary["voted"])

    tabs = st.tabs(
        [
            "Voters",
            "Register Voter",
        ]
    )

    with tabs[0]:
        _voters()

    with tabs[1]:
        _register()


def _voters() -> None:
    status = st.selectbox(
        "Voter Status",
        [
            "",
            "Active",
            "Inactive",
            "Suspended",
        ],
    )

    constituency = st.text_input(
        "Constituency"
    )

    voters = list_voters(
        status=status,
        constituency=constituency,
    )

    if not voters:
        st.info("No voter records found.")
        return

    data = pd.DataFrame(
        [
            {
                "Voter ID": voter.voter_id_number or "",
                "Citizen ID": voter.citizen_id,
                "Status": voter.voter_status,
                "Constituency": voter.constituency or "",
                "Polling Station": voter.polling_station_name or "",
                "Has Voted": voter.has_voted,
                "Voted At": voter.voted_at,
            }
            for voter in voters
        ]
    )

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True,
    )

    selected = st.selectbox(
        "Select voter",
        [voter.id for voter in voters],
        format_func=lambda value: next(
            (
                voter.voter_id_number or voter.id
                for voter in voters
                if voter.id == value
            ),
            value,
        ),
    )

    voter = next(
        voter for voter in voters
        if voter.id == selected
    )

    with st.expander("Manage Voter"):

        with st.form(f"edit_voter_{voter.id}"):

            voter_status = st.selectbox(
                "Status",
                [
                    "Active",
                    "Inactive",
                    "Suspended",
                ],
                index=(
                    [
                        "Active",
                        "Inactive",
                        "Suspended",
                    ].index(voter.voter_status)
                    if voter.voter_status in [
                        "Active",
                        "Inactive",
                        "Suspended",
                    ]
                    else 0
                ),
            )

            constituency_value = st.text_input(
                "Constituency",
                value=voter.constituency or "",
            )

            polling_station = st.text_input(
                "Polling Station",
                value=voter.polling_station_name or "",
            )

            submitted = st.form_submit_button(
                "Save Changes",
                type="primary",
            )

            if submitted:
                ok, message = update_voter(
                    voter.id,
                    {
                        "voter_status": voter_status,
                        "constituency": constituency_value,
                        "polling_station_name": polling_station,
                    },
                )

                if ok:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        if (
            voter.voter_status == "Active"
            and not voter.has_voted
        ):
            if st.button(
                "Record Vote",
                key=f"vote_{voter.id}",
            ):
                ok, message = record_vote(voter.id)

                if ok:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)


def _register() -> None:
    st.subheader("Register Voter")

    with st.form("register_voter"):

        citizen_id = st.text_input(
            "Citizen ID *"
        )

        voter_id_number = st.text_input(
            "Voter ID Number"
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

        if submitted:
            if not citizen_id.strip():
                st.error("Citizen ID is required.")
                return

            ok, message, _ = register_voter(
                {
                    "citizen_id": citizen_id,
                    "voter_id_number": voter_id_number,
                    "constituency": constituency,
                    "polling_station_id": polling_station_id,
                    "polling_station_name": polling_station_name,
                }
            )

            if ok:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
