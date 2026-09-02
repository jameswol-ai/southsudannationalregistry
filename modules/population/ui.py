from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from .service import (
    create_citizen,
    create_household,
    delete_citizen,
    delete_household,
    get_population_summary,
    list_households,
    search_citizens,
    update_citizen,
    update_household,
)


def render() -> None:
    st.title("Population Registry")
    st.caption("National population, citizen and household management.")
    summary = get_population_summary()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Citizens", summary["total"])
    c2.metric("Male", summary["male"])
    c3.metric("Female", summary["female"])
    c4.metric("Verified", summary["verified"])
    c5.metric("Households", summary["households"])
    tabs = st.tabs(["Citizen Records", "Register Citizen", "Households"])
    with tabs[0]: _citizen_records()
    with tabs[1]: _register_citizen()
    with tabs[2]: _households()


def _citizen_records() -> None:
    st.subheader("Citizen Records")
    c1, c2, c3 = st.columns(3)
    with c1: search = st.text_input("Search", placeholder="Name, National ID, passport or phone", key="population_search")
    with c2: state = st.text_input("State / Region", key="population_state_filter")
    with c3: status = st.selectbox("Verification Status", ["", "Pending Review", "Verified", "Rejected"], key="population_status_filter")
    records = search_citizens(search=search, state=state, status=status)
    if not records:
        st.info("No citizen records found."); return
    st.dataframe(pd.DataFrame([{
        "ID": c.id, "Name": c.full_name, "National ID": c.national_id or "", "Gender": c.gender,
        "Nationality": c.nationality, "State": c.state_or_region, "County": c.county_or_payam, "Status": c.verification_status
    } for c in records]), use_container_width=True, hide_index=True)
    selected_id = st.selectbox("Select citizen", [c.id for c in records], format_func=lambda value: next((c.full_name for c in records if c.id == value), value), key="population_selected_citizen")
    citizen = next(c for c in records if c.id == selected_id)
    with st.expander("View / Edit Citizen", expanded=True):
        with st.form(f"edit_citizen_{citizen.id}"):
            c1, c2 = st.columns(2)
            with c1:
                full_name = st.text_input("Full Name", value=citizen.full_name)
                national_id = st.text_input("National ID", value=citizen.national_id or "")
                passport_number = st.text_input("Passport Number", value=citizen.passport_number or "")
                phone = st.text_input("Phone Number", value=citizen.phone_number or "")
                email = st.text_input("Email", value=citizen.email_address or "")
            with c2:
                genders = ["Male", "Female", "Other"]
                gender = st.selectbox("Gender", genders, index=genders.index(citizen.gender) if citizen.gender in genders else 2)
                nationality = st.text_input("Nationality", value=citizen.nationality or "")
                state_value = st.text_input("State / Region", value=citizen.state_or_region or "")
                county = st.text_input("County / Payam", value=citizen.county_or_payam or "")
                statuses = ["Pending Review", "Verified", "Rejected"]
                verification_status = st.selectbox("Verification Status", statuses, index=statuses.index(citizen.verification_status) if citizen.verification_status in statuses else 0)
            save = st.form_submit_button("Save Changes", type="primary")
        if save:
            if not full_name.strip(): st.error("Full name is required.")
            else:
                ok, message = update_citizen(citizen.id, {
                    "full_name": full_name.strip(), "national_id": national_id.strip() or None,
                    "passport_number": passport_number.strip() or None, "phone_number": phone.strip() or None,
                    "email_address": email.strip() or None, "gender": gender, "nationality": nationality.strip(),
                    "state_or_region": state_value.strip(), "county_or_payam": county.strip(), "verification_status": verification_status,
                })
                if ok: st.success(message); st.rerun()
                else: st.error(message)
    with st.expander("Delete Citizen"):
        st.warning("Deleting a citizen permanently removes the citizen record and dependent records configured with cascade delete.")
        confirm = st.checkbox("Confirm permanent deletion", key=f"confirm_delete_citizen_{citizen.id}")
        if st.button("Delete Citizen", disabled=not confirm, key=f"delete_citizen_{citizen.id}"):
            ok, message = delete_citizen(citizen.id)
            if ok: st.success(message); st.rerun()
            else: st.error(message)


def _register_citizen() -> None:
    st.subheader("Register New Citizen")
    with st.form("register_citizen"):
        c1, c2 = st.columns(2)
        with c1:
            full_name = st.text_input("Full Name *")
            national_id = st.text_input("National ID")
            passport_number = st.text_input("Passport Number")
            dob = st.date_input("Date of Birth", value=date(2000, 1, 1), min_value=date(1900, 1, 1), max_value=date.today())
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            marital_status = st.selectbox("Marital Status", ["Single", "Married", "Divorced", "Widowed", "Separated"])
            nationality = st.text_input("Nationality", value="South Sudanese")
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
            education = st.selectbox("Education Level", ["None / Informal", "Primary", "Secondary", "Certificate", "Diploma", "Bachelor's", "Master's", "Doctorate"])
            employment = st.selectbox("Employment Status", ["Employed", "Self-Employed", "Unemployed / Seeking Work", "Student", "Retired", "Other"])
            occupation = st.text_input("Primary Occupation")
        with c2:
            disability = st.checkbox("Has Special Needs / Disability")
            disability_type = st.text_input("Disability Type")
            address = st.text_area("Residential Address")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Register Citizen", type="primary")
    if submitted:
        if not full_name.strip(): st.error("Full name is required."); return
        today = date.today(); age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        ok, message, citizen_id = create_citizen({
            "full_name": full_name, "national_id": national_id, "passport_number": passport_number,
            "date_of_birth": dob, "age": age, "gender": gender, "marital_status": marital_status,
            "nationality": nationality, "phone_number": phone, "email_address": email, "tribe": tribe,
            "sub_tribe_or_clan": clan, "native_language": language, "state_or_region": state,
            "county_or_payam": county, "boma": boma, "community": community, "residential_address": address,
            "education_level": education, "employment_status": employment, "primary_occupation": occupation,
            "has_special_needs_or_disability": disability, "disability_type": disability_type, "notes": notes,
        })
        if ok: st.success(f"{message} Citizen ID: {citizen_id}"); st.rerun()
        else: st.error(message)


def _households() -> None:
    st.subheader("Household Management")
    with st.form("create_household"):
        c1, c2 = st.columns(2)
        with c1:
            household_number = st.text_input("Household Number *")
            state = st.text_input("State / Region *")
            county = st.text_input("County / Payam")
        with c2:
            sub_county = st.text_input("Sub-County / Boma")
            boma = st.text_input("Boma")
            community = st.text_input("Community")
        address = st.text_area("Residential Address")
        submitted = st.form_submit_button("Create Household", type="primary")
    if submitted:
        if not household_number.strip(): st.error("Household number is required."); return
        if not state.strip(): st.error("State / Region is required."); return
        ok, message, _ = create_household(household_number, state, county, sub_county, boma, community, address)
        if ok: st.success(message); st.rerun()
        else: st.error(message)

    households = list_households()
    if not households: st.info("No households registered."); return
    st.dataframe(pd.DataFrame([{
        "ID": h.id, "Household Number": h.household_number, "State": h.state_or_region,
        "County": h.county_or_payam or "", "Boma": h.boma or "", "Community": h.community or "",
        "Address": h.residential_address or ""
    } for h in households]), use_container_width=True, hide_index=True)

    selected_id = st.selectbox("Select household", [h.id for h in households], format_func=lambda value: next((h.household_number for h in households if h.id == value), value), key="selected_household")
    household = next(h for h in households if h.id == selected_id)
    with st.expander("Edit Household", expanded=True):
        with st.form(f"edit_household_{household.id}"):
            household_number = st.text_input("Household Number", value=household.household_number or "")
            state = st.text_input("State / Region", value=household.state_or_region or "")
            county = st.text_input("County / Payam", value=household.county_or_payam or "")
            sub_county = st.text_input("Sub-County / Boma", value=household.sub_county_or_boma or "")
            boma = st.text_input("Boma", value=household.boma or "")
            community = st.text_input("Community", value=household.community or "")
            address = st.text_area("Residential Address", value=household.residential_address or "")
            save = st.form_submit_button("Save Changes", type="primary")
        if save:
            if not household_number.strip() or not state.strip(): st.error("Household number and State / Region are required.")
            else:
                ok, message = update_household(household.id, {
                    "household_number": household_number.strip(), "state_or_region": state.strip(),
                    "county_or_payam": county.strip() or None, "sub_county_or_boma": sub_county.strip() or None,
                    "boma": boma.strip() or None, "community": community.strip() or None, "residential_address": address.strip() or None,
                })
                if ok: st.success(message); st.rerun()
                else: st.error(message)
    with st.expander("Delete Household"):
        st.warning("A household containing registered citizens cannot be deleted.")
        confirm = st.checkbox("Confirm permanent deletion", key=f"confirm_delete_household_{household.id}")
        if st.button("Delete Household", disabled=not confirm, key=f"delete_household_{household.id}"):
            ok, message = delete_household(household.id)
            if ok: st.success(message); st.rerun()
            else: st.error(message)
