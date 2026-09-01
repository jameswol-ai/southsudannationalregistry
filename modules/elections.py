"""
Elections module.

Provides basic voter registration and electoral record management.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from database.database import SessionLocal
from database.models import Citizen, VoterRecord


def render() -> None:

    st.title("Elections")

    st.caption(
        "Voter registration and electoral information management."
    )

    tab_register, tab_records = st.tabs(
        [
            "Voter Registration",
            "Voter Records",
        ]
    )

    # ========================================================
    # VOTER REGISTRATION
    # ========================================================

    with tab_register:

        st.subheader("Register Voter")

        with st.form("voter_registration_form"):

            citizen_id = st.text_input(
                "Citizen ID *"
            )

            voter_id = st.text_input(
                "Voter ID Number"
            )

            voter_status = st.selectbox(
                "Voter Status",
                [
                    "Active",
                    "Suspended",
                    "Inactive",
                ],
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

                st.error(
                    "Citizen ID is required."
                )

            else:

                db = SessionLocal()

                try:

                    citizen = (
                        db.query(Citizen)
                        .filter(
                            Citizen.id
                            == citizen_id.strip()
                        )
                        .first()
                    )

                    if not citizen:

                        st.error(
                            "Citizen was not found."
                        )

                    else:

                        existing = (
                            db.query(VoterRecord)
                            .filter(
                                VoterRecord.citizen_id
                                == citizen.id
                            )
                            .first()
                        )

                        if existing:

                            st.error(
                                "This citizen already has a voter record."
                            )

                        else:

                            voter = VoterRecord(
                                id=(
                                    f"VOTER-{citizen.id}"
                                ),
                                citizen_id=citizen.id,
                                voter_id_number=(
                                    voter_id.strip()
                                    or None
                                ),
                                voter_status=voter_status,
                                constituency=(
                                    constituency.strip()
                                    or None
                                ),
                                polling_station_id=(
                                    polling_station_id.strip()
                                    or None
                                ),
                                polling_station_name=(
                                    polling_station_name.strip()
                                    or None
                                ),
                            )

                            citizen.voter_id_number = (
                                voter.voter_id_number
                            )

                            citizen.voter_status = (
                                voter.voter_status
                            )

                            citizen.constituency = (
                                voter.constituency
                            )

                            citizen.polling_station_id = (
                                voter.polling_station_id
                            )

                            citizen.polling_station_name = (
                                voter.polling_station_name
                            )

                            db.add(voter)

                            db.commit()

                            st.success(
                                "Voter registered successfully."
                            )

                except Exception as exc:

                    db.rollback()

                    st.error(
                        f"Voter registration failed: {exc}"
                    )

                finally:

                    db.close()

    # ========================================================
    # RECORDS
    # ========================================================

    with tab_records:

        st.subheader("Voter Records")

        db = SessionLocal()

        try:

            records = (
                db.query(
                    VoterRecord,
                    Citizen,
                )
                .join(
                    Citizen,
                    Citizen.id
                    == VoterRecord.citizen_id,
                )
                .order_by(
                    Citizen.full_name.asc(),
                )
                .limit(500)
                .all()
            )

        finally:

            db.close()

        if records:

            rows = []

            for voter, citizen in records:

                rows.append(
                    {
                        "Citizen ID":
                            citizen.id,
                        "Citizen":
                            citizen.full_name,
                        "Voter ID":
                            voter.voter_id_number or "",
                        "Status":
                            voter.voter_status,
                        "Constituency":
                            voter.constituency or "",
                        "Polling Station":
                            voter.polling_station_name or "",
                        "Voted":
                            "Yes"
                            if voter.has_voted
                            else "No",
                    }
                )

            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "No voter records have been registered."
                          )
