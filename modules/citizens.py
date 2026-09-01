"""
Citizen Registry module.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from database.database import SessionLocal
from services.citizen_service import (
    create_citizen,
    list_citizens,
    search_citizens,
)


def _citizen_rows(citizens):

    return [
        {
            "ID": citizen.id,
            "National ID": citizen.national_id or "",
            "Name": citizen.full_name,
            "Gender": citizen.gender,
            "Date of Birth": citizen.date_of_birth,
            "Nationality": citizen.nationality,
            "State": citizen.state_or_region,
            "County / Payam": citizen.county_or_payam,
            "Verification": citizen.verification_status,
        }
        for citizen in citizens
    ]


def render() -> None:

    st.title("Citizens")
    st.caption(
        "Register, search and review citizens in the national registry."
    )

    tab_register, tab_search, tab_records = st.tabs(
        [
            "Register Citizen",
            "Search",
            "Records",
        ]
    )

    # ========================================================
    # REGISTER
    # ========================================================

    with tab_register:

        st.subheader("New Citizen Registration")

        with st.form("citizen_registration_form"):

            col1, col2 = st.columns(2)

            with col1:

                full_name = st.text_input(
                    "Full Name *"
                )

                national_id = st.text_input(
                    "National ID"
                )

                date_of_birth = st.date_input(
                    "Date of Birth",
                    value=date(
                        1990,
                        1,
                        1,
                    ),
                )

                gender = st.selectbox(
                    "Gender",
                    [
                        "Male",
                        "Female",
                        "Other",
                    ],
                )

                marital_status = st.selectbox(
                    "Marital Status",
                    [
                        "Single",
                        "Married",
                        "Divorced",
                        "Widowed",
                    ],
                )

            with col2:

                phone_number = st.text_input(
                    "Phone Number"
                )

                nationality = st.text_input(
                    "Nationality",
                    value="South Sudanese",
                )

                state = st.text_input(
                    "State / Region"
                )

                county = st.text_input(
                    "County / Payam"
                )

                community = st.text_input(
                    "Community"
                )

            submitted = st.form_submit_button(
                "Register Citizen",
                type="primary",
            )

        if submitted:

            if not full_name.strip():

                st.error(
                    "Full Name is required."
                )

            else:

                db = SessionLocal()

                try:

                    citizen = create_citizen(
                        db=db,
                        data={
                            "full_name": full_name.strip(),
                            "national_id": (
                                national_id.strip()
                                or None
                            ),
                            "date_of_birth": date_of_birth,
                            "gender": gender,
                            "marital_status": marital_status,
                            "nationality": nationality.strip()
                            or "South Sudanese",
                            "phone_number": phone_number.strip()
                            or None,
                            "state_or_region": state.strip(),
                            "county_or_payam": county.strip(),
                            "community": community.strip(),
                        },
                        username="streamlit",
                    )

                    st.success(
                        f"Citizen registered successfully: "
                        f"{citizen.id}"
                    )

                except Exception as exc:

                    db.rollback()

                    st.error(
                        f"Registration failed: {exc}"
                    )

                finally:

                    db.close()

    # ========================================================
    # SEARCH
    # ========================================================

    with tab_search:

        st.subheader("Citizen Search")

        query = st.text_input(
            "Search by name, National ID, voter ID, phone or community",
            key="citizen_search",
        )

        if query.strip():

            db = SessionLocal()

            try:

                results = search_citizens(
                    db=db,
                    search_term=query,
                )

            finally:

                db.close()

            if not results:

                st.info(
                    "No matching citizens found."
                )

            else:

                st.dataframe(
                    pd.DataFrame(
                        _citizen_rows(results)
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

    # ========================================================
    # RECORDS
    # ========================================================

    with tab_records:

        st.subheader("Citizen Records")

        db = SessionLocal()

        try:

            citizens = list_citizens(
                db=db,
                limit=200,
            )

        finally:

            db.close()

        if citizens:

            st.dataframe(
                pd.DataFrame(
                    _citizen_rows(citizens)
                ),
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "No citizen records are currently available."
            )
