"""
Population Registry Views.

Streamlit presentation layer for citizen registration, search,
editing, and population statistics.
"""

from __future__ import annotations

from datetime import date
from typing import Any

import streamlit as st

from database.database import SessionLocal

from .service import PopulationService, PopulationValidationError


EDIT_FORM_KEY = "population_citizen_edit_form"
REGISTER_FORM_KEY = "population_citizen_register_form"


def _get_username() -> str:
    return str(st.session_state.get("username", "system"))


def _session():
    return SessionLocal()


def _citizen_to_dict(citizen) -> dict[str, Any]:
    return {
        "id": citizen.id,
        "national_id": citizen.national_id,
        "full_name": citizen.full_name,
        "date_of_birth": citizen.date_of_birth,
        "age": citizen.age,
        "gender": citizen.gender,
        "marital_status": citizen.marital_status,
        "nationality": citizen.nationality,
        "phone_number": citizen.phone_number,
        "email_address": citizen.email_address,
        "state_or_region": citizen.state_or_region,
        "county_or_payam": citizen.county_or_payam,
        "boma": citizen.boma,
        "community": citizen.community,
        "verification_status": citizen.verification_status,
        "voter_id_number": citizen.voter_id_number,
    }


def _render_citizen_form(
    service: PopulationService,
    citizen=None,
    form_key: str = REGISTER_FORM_KEY,
) -> None:
    """Render the citizen create/edit form.

    A unique form key is required because Streamlit executes all tab
    contents during a run. The edit form and register form therefore
    cannot share the same widget identity.
    """
    editing = citizen is not None

    st.subheader("Edit Citizen" if editing else "Register Citizen")

    gender_options = ["Male", "Female", "Other"]
    marital_options = [
        "Single",
        "Married",
        "Divorced",
        "Widowed",
        "Separated",
        "Unknown",
    ]
    verification_options = [
        "Pending Review",
        "Verified",
        "Rejected",
        "Archived",
    ]

    current_gender = citizen.gender if citizen else None
    current_marital = citizen.marital_status if citizen else None
    current_verification = citizen.verification_status if citizen else None

    with st.form(form_key, clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input(
                "Full Name *",
                value=citizen.full_name if citizen else "",
            )
            national_id = st.text_input(
                "National ID",
                value=(citizen.national_id or "") if citizen else "",
            )
            passport_number = st.text_input(
                "Passport Number",
                value=(citizen.passport_number or "") if citizen else "",
            )
            gender = st.selectbox(
                "Gender",
                gender_options,
                index=(
                    gender_options.index(current_gender)
                    if current_gender in gender_options
                    else 2
                ),
            )
            marital_status = st.selectbox(
                "Marital Status",
                marital_options,
                index=(
                    marital_options.index(current_marital)
                    if current_marital in marital_options
                    else 0
                ),
            )

        with col2:
            dob_default = (
                citizen.date_of_birth
                if citizen and citizen.date_of_birth
                else date(2000, 1, 1)
            )
            date_of_birth = st.date_input("Date of Birth", value=dob_default)
            nationality = st.text_input(
                "Nationality",
                value=citizen.nationality if citizen else "South Sudanese",
            )
            phone_number = st.text_input(
                "Phone Number",
                value=(citizen.phone_number or "") if citizen else "",
            )
            email_address = st.text_input(
                "Email Address",
                value=(citizen.email_address or "") if citizen else "",
            )
            tribe = st.text_input(
                "Tribe",
                value=citizen.tribe if citizen else "",
            )

        st.markdown("### Residence")
        col1, col2, col3 = st.columns(3)

        with col1:
            state = st.text_input(
                "State / Region",
                value=citizen.state_or_region if citizen else "",
            )
        with col2:
            county = st.text_input(
                "County / Payam",
                value=citizen.county_or_payam if citizen else "",
            )
        with col3:
            boma = st.text_input(
                "Boma",
                value=(citizen.boma or "") if citizen else "",
            )

        community = st.text_input(
            "Community",
            value=citizen.community if citizen else "",
        )
        address = st.text_area(
            "Residential Address",
            value=(citizen.residential_address or "") if citizen else "",
        )

        st.markdown("### Education & Employment")
        col1, col2 = st.columns(2)

        with col1:
            education_level = st.text_input(
                "Education Level",
                value=(
                    citizen.education_level
                    if citizen
                    else "None / Informal"
                ),
            )
            is_literate = st.checkbox(
                "Literate",
                value=citizen.is_literate if citizen else False,
            )

        with col2:
            employment_status = st.text_input(
                "Employment Status",
                value=(
                    citizen.employment_status
                    if citizen
                    else "Unemployed / Seeking Work"
                ),
            )
            occupation = st.text_input(
                "Primary Occupation",
                value=(citizen.primary_occupation or "") if citizen else "",
            )

        st.markdown("### Electoral Information")
        col1, col2 = st.columns(2)

        with col1:
            voter_id = st.text_input(
                "Voter ID Number",
                value=(citizen.voter_id_number or "") if citizen else "",
            )
            voter_status = st.text_input(
                "Voter Status",
                value=(citizen.voter_status or "") if citizen else "",
            )

        with col2:
            constituency = st.text_input(
                "Constituency",
                value=(citizen.constituency or "") if citizen else "",
            )
            polling_station = st.text_input(
                "Polling Station",
                value=(citizen.polling_station_name or "") if citizen else "",
            )

        st.markdown("### Verification")
        verification_status = st.selectbox(
            "Verification Status",
            verification_options,
            index=(
                verification_options.index(current_verification)
                if current_verification in verification_options
                else 0
            ),
        )
        verification_notes = st.text_area(
            "Verification Notes",
            value=(citizen.verification_notes or "") if citizen else "",
        )

        submitted = st.form_submit_button(
            "Update Citizen" if editing else "Register Citizen",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    values = {
        "full_name": full_name.strip(),
        "national_id": national_id.strip() or None,
        "passport_number": passport_number.strip() or None,
        "gender": gender,
        "marital_status": marital_status,
        "nationality": nationality.strip() or "South Sudanese",
        "date_of_birth": date_of_birth,
        "phone_number": phone_number.strip() or None,
        "email_address": email_address.strip() or None,
        "tribe": tribe.strip(),
        "state_or_region": state.strip(),
        "county_or_payam": county.strip(),
        "boma": boma.strip() or None,
        "community": community.strip(),
        "residential_address": address.strip() or None,
        "education_level": education_level.strip(),
        "is_literate": is_literate,
        "employment_status": employment_status.strip(),
        "primary_occupation": occupation.strip() or None,
        "voter_id_number": voter_id.strip() or None,
        "voter_status": voter_status.strip() or None,
        "constituency": constituency.strip() or None,
        "polling_station_name": polling_station.strip() or None,
        "verification_status": verification_status,
        "verification_notes": verification_notes.strip() or None,
    }

    try:
        if editing:
            updated = service.update_citizen(citizen.id, values)
            st.session_state["population_selected_id"] = updated.id
            st.session_state.pop("population_edit_id", None)
            st.success(
                f"Citizen record updated successfully. Record ID: {updated.id}"
            )
        else:
            created = service.create_citizen(values)
            st.session_state["population_selected_id"] = created.id
            st.success(
                f"Citizen registered successfully. Record ID: {created.id}"
            )
            st.info("The record has been committed to the database and can now be found in Citizen Registry.")
            st.rerun()

    except PopulationValidationError as exc:
        st.error(str(exc))

    except Exception as exc:
        st.error(f"Unable to save citizen: {type(exc).__name__}: {exc}")
        with st.expander("Technical error details"):
            st.exception(exc)


def _render_dashboard(service: PopulationService) -> None:
    stats = service.dashboard_statistics()

    total = stats["total_citizens"]
    households = stats["total_households"]
    gender = stats["by_gender"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registered Citizens", f"{total:,}")
    c2.metric("Households", f"{households:,}")
    c3.metric("Male", f"{gender.get('Male', 0):,}")
    c4.metric("Female", f"{gender.get('Female', 0):,}")

    st.markdown("### Population by State")
    by_state = stats["by_state"]
    if by_state:
        st.bar_chart(by_state)
    else:
        st.info("No population data has been registered yet.")

    st.markdown("### Verification Status")
    status = stats["by_verification_status"]
    if status:
        st.dataframe(
            [{"Status": key, "Records": value} for key, value in status.items()],
            use_container_width=True,
            hide_index=True,
        )


def _render_search(service: PopulationService) -> None:
    st.subheader("Citizen Registry")

    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input(
            "Search",
            placeholder="Name, National ID, phone...",
            key="population_search_text",
        )
    with col2:
        state = st.text_input("State / Region", key="population_search_state")
    with col3:
        gender = st.selectbox(
            "Gender",
            ["All", "Male", "Female", "Other"],
            key="population_search_gender",
        )

    status = st.selectbox(
        "Verification Status",
        ["All", "Pending Review", "Verified", "Rejected", "Archived"],
        key="population_search_status",
    )

    citizens = service.search_citizens(
        search=search.strip() or None,
        state=state.strip() or None,
        gender=None if gender == "All" else gender,
        verification_status=None if status == "All" else status,
    )

    st.caption(f"{len(citizens)} record(s) found")

    if not citizens:
        st.info("No citizen records match the search.")
        return

    for citizen in citizens:
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

            with col1:
                st.write(f"**{citizen.full_name}**")
                st.caption(citizen.national_id or "National ID not assigned")
            with col2:
                st.write(citizen.state_or_region or "Location not recorded")
            with col3:
                st.write(citizen.verification_status)
            with col4:
                if st.button(
                    "View",
                    key=f"population_view_{citizen.id}",
                    use_container_width=True,
                ):
                    st.session_state["population_selected_id"] = citizen.id
                    st.session_state.pop("population_edit_id", None)
                    st.rerun()

                if st.button(
                    "Edit",
                    key=f"population_edit_{citizen.id}",
                    use_container_width=True,
                ):
                    st.session_state["population_edit_id"] = citizen.id
                    st.session_state.pop("population_selected_id", None)
                    st.rerun()

    selected_id = st.session_state.get("population_selected_id")
    edit_id = st.session_state.get("population_edit_id")

    if selected_id:
        selected = service.get_citizen(selected_id)
        if selected:
            st.divider()
            st.subheader("Citizen Profile")
            st.json(_citizen_to_dict(selected))

    if edit_id:
        selected = service.get_citizen(edit_id)
        if selected:
            st.divider()
            _render_citizen_form(
                service,
                selected,
                form_key=EDIT_FORM_KEY,
            )


def render() -> None:
    st.title("Population Registry")
    st.caption(
        "National population registration and demographic management"
    )

    db = _session()
    try:
        service = PopulationService(db, username=_get_username())

        tab1, tab2, tab3 = st.tabs(
            ["Dashboard", "Citizen Registry", "Register Citizen"]
        )

        with tab1:
            _render_dashboard(service)

        with tab2:
            _render_search(service)

        with tab3:
            _render_citizen_form(
                service,
                form_key=REGISTER_FORM_KEY,
            )
    finally:
        db.close()
