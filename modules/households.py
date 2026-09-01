"""
Household Registry module.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from database.database import SessionLocal
from database.models import Citizen
from services.household_service import (
    create_household,
    get_household,
    list_households,
)


def render() -> None:

    st.title("Households")
    st.caption(
        "Manage households and household registration."
    )

    tab_register, tab_records, tab_members = st.tabs(
        [
            "Register Household",
            "Households",
            "Members",
        ]
    )

    # ========================================================
    # REGISTER
    # ========================================================

    with tab_register:

        st.subheader("Register Household")

        with st.form("household_form"):

            household_number = st.text_input(
                "Household Number *"
            )

            state = st.text_input(
                "State / Region"
            )

            county = st.text_input(
                "County / Payam"
            )

            boma = st.text_input(
                "Boma"
            )

            community = st.text_input(
                "Community"
            )

            address = st.text_area(
                "Residential Address"
            )

            submitted = st.form_submit_button(
                "Register Household",
                type="primary",
            )

        if submitted:

            if not household_number.strip():

                st.error(
                    "Household Number is required."
                )

            else:

                db = SessionLocal()

                try:

                    household = create_household(
                        db=db,
                        data={
                            "household_number":
                                household_number.strip(),
                            "state_or_region":
                                state.strip(),
                            "county_or_payam":
                                county.strip(),
                            "boma":
                                boma.strip(),
                            "community":
                                community.strip(),
                            "residential_address":
                                address.strip() or None,
                        },
                        username="streamlit",
                    )

                    st.success(
                        f"Household registered: "
                        f"{household.household_number}"
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

        st.subheader("Registered Households")

        db = SessionLocal()

        try:

            households = list_households(
                db=db,
                limit=200,
            )

            rows = []

            for household in households:

                member_count = (
                    db.query(Citizen)
                    .filter(
                        Citizen.household_id
                        == household.id
                    )
                    .count()
                )

                rows.append(
                    {
                        "Household ID": household.id,
                        "Household Number":
                            household.household_number,
                        "State":
                            household.state_or_region,
                        "County / Payam":
                            household.county_or_payam or "",
                        "Boma":
                            household.boma or "",
                        "Community":
                            household.community or "",
                        "Members":
                            member_count,
                    }
                )

        finally:

            db.close()

        if rows:

            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "No households have been registered."
            )

    # ========================================================
    # MEMBERS
    # ========================================================

    with tab_members:

        st.subheader("Household Members")

        household_id = st.text_input(
            "Household ID"
        )

        if household_id.strip():

            db = SessionLocal()

            try:

                household = get_household(
                    db=db,
                    household_id=household_id.strip(),
                )

                if not household:

                    st.error(
                        "Household was not found."
                    )

                else:

                    members = (
                        db.query(Citizen)
                        .filter(
                            Citizen.household_id
                            == household.id
                        )
                        .all()
                    )

                    st.write(
                        f"**{household.household_number}**"
                    )

                    if members:

                        st.dataframe(
                            pd.DataFrame(
                                [
                                    {
                                        "Citizen ID":
                                            member.id,
                                        "Name":
                                            member.full_name,
                                        "Role":
                                            member.household_role,
                                        "Gender":
                                            member.gender,
                                        "Verification":
                                            member.verification_status,
                                    }
                                    for member in members
                                ]
                            ),
                            use_container_width=True,
                            hide_index=True,
                        )

                    else:

                        st.info(
                            "No members are currently linked "
                            "to this household."
                        )

            finally:

                db.close()
