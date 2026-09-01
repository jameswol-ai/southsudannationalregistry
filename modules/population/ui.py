from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from .service import (
    create_citizen,
    create_household,
    delete_citizen,
    get_population_summary,
    list_households,
    search_citizens,
    update_citizen,
)


def render() -> None:
    st.title("Population Registry")
    st.caption(
        "National population, citizen and household management."
    )

    summary = get_population_summary()

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Citizens", summary["total"])
    c2.metric("Male", summary["male"])
    c3.metric("Female", summary["female"])
    c4.metric("Verified", summary["verified"])
    c5.metric("Households", summary["households"])

    tabs = st.tabs(
        [
            "Citizen Records",
            "Register Citizen",
            "Households",
        ]
    )

    with tabs[0]:
        _citizen_records()

    with tabs[1]:
        _register_citizen()

    with tabs[2]:
        _households()


def _citizen_records() -> None:
    st.subheader("Citizen Records")

    c1, c2, c3 = st.columns(3)

    with c1:
        search = st.text_input(
            "Search",
            placeholder="Name, National ID, passport or phone",
        )

    with c2:
        state = st.text_input("State / Region")

    with c3:
        status = st.selectbox(
            "Verification Status",
            [
                "",
                "Pending Review",
                "Verified",
                "Rejected",
            ],
        )

    records = search_citizens(
        search=search,
        state=state,
        status=status,
    )

    if not records:
        st.info("No citizen records found.")
        return

    table = pd.DataFrame(
        [
            {
                "ID": citizen.id,
                "Name": citizen.full_name,
                "National ID": citizen.national_id or "",
                "Gender": citizen.gender,
                "Nationality": citizen.nationality,
                "State": citizen.state_or_region,
                "County": citizen.county_or_payam,
                "Status": citizen.verification_status,
            }
            for citizen in records
        ]
    )

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
    )

    selected_id = st.selectbox(
        "Select citizen",
        [citizen.id for citizen in records],
        format_func=lambda value: next(
            (
                citizen.full_name
                for citizen in records
                if citizen.id == value
            ),
            value,
        ),
    )

    selected = next(
        citizen for citizen in records
        if citizen.id == selected_id
    )

    with st.expander("View / Edit Citizen", expanded=True):
        _edit_citizen(selected)

    with st.expander("Delete Citizen"):
        st.warning(
            "Deleting a citizen permanently removes the citizen "
            "record and related dependent records configured "
            "with cascade delete."
        )

        if st.button(
            "Delete Citizen",
            type="secondary",
            key=f"delete_{selected.id}",
        ):
            ok, message = delete_citizen(selected.id)

            if ok:
                st.success(message)
                st.rerun()
            else:
                st.error(message)


def _edit_citizen(citizen) -> None:
    with st.form(f"edit_citizen_{citizen.id}"):

        c1, c2 = st.columns(2)

        with c1:
            full_name = st.text_input(
                "Full Name",
                value=citizen.full_name,
            )

            national_id = st.text_input(
                "National ID",
                value=citizen.national_id or "",
            )

            passport_number = st.text_input(
                "Passport Number",
                value=citizen.passport_number or "",
            )

            phone = st.text_input(
                "Phone Number",
                value=citizen.phone_number or "",
            )

            email = st.text_input(
                "Email",
                value=citizen.email_address or "",
            )

        with c2:
            gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other"],
                index=(
                    ["Male", "Female", "Other"].index(citizen.gender)
                    if citizen.gender in ["Male", "Female", "Other"]
                    else 2
                ),
            )

            nationality = st.text_input(
                "Nationality",
                value=citizen.nationality,
            )

            state = st.text_input(
                "State / Region",
                value=citizen.state_or_region,
            )

            county = st.text_input(
                "County / Payam",
                value=citizen.county_or_payam,
            )

            verification_status = st.selectbox(
                "Verification Status",
                [
                    "Pending Review",
                    "Verified",
                    "Rejected",
                ],
                index=(
                    [
                        "Pending Review",
                        "Verified",
                        "Rejected",
                    ].index(citizen.verification_status)
                    if citizen.verification_status
                    in [
                        "Pending Review",
                        "Verified",
                        "Rejected",
                    ]
                    else 0
                ),
            )

        submitted = st.form_submit_button(
            "Save Changes",
            type="primary",
        )

        if submitted:
            if not full_name.strip():
                st.error("Full name is required.")
                return

            ok, message = update_citizen(
                citizen.id,
                {
                    "full_name": full_name.strip(),
                    "national_id": national_id.strip() or None,
                    "passport_number": passport_number.strip() or None,
                    "phone_number": phone.strip() or None,
                    "email_address": email.strip() or None,
                    "gender": gender,
                    "nationality": nationality.strip(),
                    "state_or_region": state.strip(),
                    "county_or_payam": county.strip(),
                    "verification_status": verification_status,
                },
            )

            if ok:
                st.success(message)
                st.rerun()
            else:
                st.error(message)


def _register_citizen() -> None:
    st.subheader("Register New Citizen")

    with st.form("register_citizen"):

        c1, c2 = st.columns(2)

        with c1:
            full_name = st.text_input("Full Name *")
            national_id = st.text_input("National ID")
            passport_number = st.text_input("Passport Number")

            dob = st.date_input(
                "Date of Birth",
                value=date(2000, 1, 1),
                min_value=date(1900, 1, 1),
                max_value=date.today(),
            )

            gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other"],
            )

            marital_status = st.selectbox(
                "Marital Status",
                [
                    "Single",
                    "Married",
                    "Divorced",
                    "Widowed",
                    "Separated",
                ],
            )

            nationality = st.text_input(
                "Nationality",
                value="South Sudanese",
            )

        with c2:
            phone = st.text_input("Phone Number")
            email = st.text_input("Email Address")

            tribe = st.text_input("Tribe")
            clan = st.text_input("Sub-Tribe / Clan")
            language = st.text_input("Native Language")

            state = st.text_input("State / Region")
            county = st.text_input("County / Payam")
            boma = st.text_input("Boma")
            community = st.text_input("Community")

        st.divider()

        c1, c2 = st.columns(2)

        with c1:
            education = st.selectbox(
                "Education Level",
                [
                    "None / Informal",
                    "Primary",
                    "Secondary",
                    "Certificate",
                    "Diploma",
                    "Bachelor's",
                    "Master's",
                    "Doctorate",
                ],
            )

            employment = st.selectbox(
                "Employment Status",
                [
                    "Employed",
                    "Self-Employed",
                    "Unemployed / Seeking Work",
                    "Student",
                    "Retired",
                    "Other",
                ],
            )

            occupation = st.text_input(
                "Primary Occupation"
            )

        with c2:
            disability = st.checkbox(
                "Has Special Needs / Disability"
            )

            disability_type = st.text_input(
                "Disability Type"
            )

            address = st.text_area(
                "Residential Address"
            )

        notes = st.text_area("Notes")

        submitted = st.form_submit_button(
            "Register Citizen",
            type="primary",
        )

        if submitted:
            if not full_name.strip():
                st.error("Full name is required.")
                return

            today = date.today()
            age = (
                today.year
                - dob.year
                - (
                    (today.month, today.day)
                    < (dob.month, dob.day)
                )
            )

            ok, message, citizen_id = create_citizen(
                {
                    "full_name": full_name,
                    "national_id": national_id,
                    "passport_number": passport_number,
                    "date_of_birth": dob,
                    "age": age,
                    "gender": gender,
                    "marital_status": marital_status,
                    "nationality": nationality,
                    "phone_number": phone,
                    "email_address": email,
                    "tribe": tribe,
                    "sub_tribe_or_clan": clan,
                    "native_language": language,
                    "state_or_region": state,
                    "county_or_payam": county,
                    "boma": boma,
                    "community": community,
                    "residential_address": address,
                    "education_level": education,
                    "employment_status": employment,
                    "primary_occupation": occupation,
                    "has_special_needs_or_disability": disability,
                    "disability_type": disability_type,
                    "notes": notes,
                }
            )

            if ok:
                st.success(
                    f"{message} Citizen ID: {citizen_id}"
                )
                st.rerun()
            else:
                st.error(message)


def _households() -> None:
    st.subheader("Household Management")

    with st.form("create_household"):
        c1, c2 = st.columns(2)

        with c1:
            household_number = st.text_input(
                "Household Number *"
            )
            state = st.text_input(
                "State / Region *"
            )
            county = st.text_input(
                "County / Payam"
            )

        with c2:
            sub_county = st.text_input(
                "Sub-County / Boma"
            )
            boma = st.text_input("Boma")
            community = st.text_input("Community")

        address = st.text_area(
            "Residential Address"
        )

        submitted = st.form_submit_button(
            "Create Household",
            type="primary",
        )

        if submitted:
            if not household_number.strip():
                st.error("Household number is required.")
                return

            if not state.strip():
                st.error("State / Region is required.")
                return

            ok, message, _ = create_household(
                household_number,
                state,
                county,
                sub_county,
                boma,
                community,
                address,
            )

            if ok:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    households = list_households()

    if not households:
        st.info("No households registered.")
        return

    data = pd.DataFrame(
        [
            {
                "Household Number": h.household_number,
                "State": h.state_or_region,
                "County": h.county_or_payam or "",
                "Boma": h.boma or "",
                "Community": h.community or "",
                "Address": h.residential_address or "",
            }
            for h in households
        ]
    )

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True,
          )
