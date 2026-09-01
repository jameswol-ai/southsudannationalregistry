"""
South Sudan National Registry
Household Management Module
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

import streamlit as st

from database.database import SessionLocal

from models import (
    AuditLog,
    Citizen,
    Household,
)


logger = logging.getLogger(
    "south_sudan_national_registry.households"
)


# ============================================================
# CONSTANTS
# ============================================================

HOUSEHOLD_TYPES = [
    "Family",
    "Single Person",
    "Extended Family",
    "Institutional",
    "Other",
]

STATUS_OPTIONS = [
    "Pending Review",
    "Verified",
    "Suspended",
    "Archived",
]


# ============================================================
# SESSION STATE
# ============================================================

def initialize_state() -> None:

    if "household_editor_id" not in st.session_state:
        st.session_state.household_editor_id = None

    if "household_view_id" not in st.session_state:
        st.session_state.household_view_id = None


# ============================================================
# DATABASE
# ============================================================

def get_session():

    try:

        return SessionLocal()

    except Exception:

        logger.exception(
            "Unable to create database session."
        )

        return None


# ============================================================
# AUDIT
# ============================================================

def write_audit(
    db,
    action: str,
    entity_id: str | None,
    details: str,
) -> None:

    try:

        db.add(
            AuditLog(
                action=action,
                entity_type="Household",
                entity_id=entity_id,
                username="streamlit",
                created_at=datetime.utcnow(),
                details=details,
            )
        )

    except Exception:

        logger.exception(
            "Unable to write household audit log."
        )


# ============================================================
# LOAD
# ============================================================

def get_household(
    household_id: str,
) -> Household | None:

    db = get_session()

    if db is None:
        return None

    try:

        return (
            db.query(Household)
            .filter(
                Household.id == household_id
            )
            .first()
        )

    finally:

        db.close()


# ============================================================
# SEARCH
# ============================================================

def search_households(
    search_text: str = "",
    state: str = "",
) -> list[Household]:

    db = get_session()

    if db is None:
        return []

    try:

        query = db.query(
            Household
        )

        search_text = (
            search_text
            .strip()
        )

        if search_text:

            pattern = (
                f"%{search_text}%"
            )

            query = query.filter(
                Household.household_number.ilike(
                    pattern
                )
                |
                Household.community.ilike(
                    pattern
                )
                |
                Household.residential_address.ilike(
                    pattern
                )
            )

        if state:

            query = query.filter(
                Household.state_or_region
                == state
            )

        return (
            query
            .order_by(
                Household.created_at.desc()
            )
            .limit(500)
            .all()
        )

    finally:

        db.close()


# ============================================================
# SAVE
# ============================================================

def save_household(
    household: Household | None,
    household_number: str,
    head_citizen_id: str | None,
    state_or_region: str,
    county_or_payam: str | None,
    sub_county_or_boma: str | None,
    boma: str | None,
    community: str | None,
    residential_address: str | None,
) -> bool:

    db = get_session()

    if db is None:

        st.error(
            "Unable to connect to the database."
        )

        return False

    try:

        duplicate = (
            db.query(Household)
            .filter(
                Household.household_number
                == household_number
            )
        )

        if household is not None:

            duplicate = duplicate.filter(
                Household.id
                != household.id
            )

        if duplicate.first():

            st.error(
                "A household with this household number "
                "already exists."
            )

            return False

        # ----------------------------------------------------
        # Validate head
        # ----------------------------------------------------

        head = None

        if head_citizen_id:

            head = (
                db.query(Citizen)
                .filter(
                    Citizen.id
                    == head_citizen_id
                )
                .first()
            )

            if head is None:

                st.error(
                    "The selected household head "
                    "could not be found."
                )

                return False

        # ----------------------------------------------------
        # Create
        # ----------------------------------------------------

        if household is None:

            household = Household(
                id=str(
                    uuid.uuid4()
                ),
                household_number=(
                    household_number
                    .strip()
                ),
                head_citizen_id=(
                    head_citizen_id
                ),
                state_or_region=(
                    state_or_region.strip()
                ),
                county_or_payam=(
                    county_or_payam.strip()
                    or None
                ),
                sub_county_or_boma=(
                    sub_county_or_boma.strip()
                    or None
                ),
                boma=(
                    boma.strip()
                    or None
                ),
                community=(
                    community.strip()
                    or None
                ),
                residential_address=(
                    residential_address.strip()
                    or None
                ),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            db.add(
                household
            )

            action = "CREATE"

            message = (
                "Household registered successfully."
            )

        else:

            household.household_number = (
                household_number.strip()
            )

            household.head_citizen_id = (
                head_citizen_id
            )

            household.state_or_region = (
                state_or_region.strip()
            )

            household.county_or_payam = (
                county_or_payam.strip()
                or None
            )

            household.sub_county_or_boma = (
                sub_county_or_boma.strip()
                or None
            )

            household.boma = (
                boma.strip()
                or None
            )

            household.community = (
                community.strip()
                or None
            )

            household.residential_address = (
                residential_address.strip()
                or None
            )

            household.updated_at = (
                datetime.utcnow()
            )

            action = "UPDATE"

            message = (
                "Household updated successfully."
            )

        # ----------------------------------------------------
        # Commit
        # ----------------------------------------------------

        db.flush()

        write_audit(
            db=db,
            action=action,
            entity_id=str(
                household.id
            ),
            details=message,
        )

        db.commit()

        st.success(
            message
        )

        st.session_state.household_editor_id = None
        st.session_state.household_view_id = (
            str(household.id)
        )

        return True

    except Exception as exc:

        db.rollback()

        logger.exception(
            "Unable to save household."
        )

        st.error(
            "The household could not be saved."
        )

        with st.expander(
            "Technical details"
        ):

            st.exception(exc)

        return False

    finally:

        db.close()


# ============================================================
# ARCHIVE
# ============================================================

def archive_household(
    household_id: str,
) -> None:

    db = get_session()

    if db is None:

        st.error(
            "Unable to connect to the database."
        )

        return

    try:

        household = (
            db.query(Household)
            .filter(
                Household.id
                == household_id
            )
            .first()
        )

        if household is None:

            st.error(
                "Household not found."
            )

            return

        # Household currently has no status column.
        # Therefore archive is represented by a registry
        # audit event rather than mutating the household.

        write_audit(
            db=db,
            action="ARCHIVE",
            entity_id=str(
                household.id
            ),
            details=(
                "Household archived from the active "
                "Registry."
            ),
        )

        db.commit()

        st.success(
            "Household archived."
        )

        st.session_state.household_editor_id = None
        st.session_state.household_view_id = None

        st.rerun()

    except Exception as exc:

        db.rollback()

        logger.exception(
            "Unable to archive household."
        )

        st.error(
            "The household could not be archived."
        )

        with st.expander(
            "Technical details"
        ):

            st.exception(exc)

    finally:

        db.close()


# ============================================================
# CITIZEN SELECTOR
# ============================================================

def load_citizen_choices():

    db = get_session()

    if db is None:
        return []

    try:

        return (
            db.query(Citizen)
            .order_by(
                Citizen.full_name
            )
            .limit(5000)
            .all()
        )

    finally:

        db.close()


# ============================================================
# FORM
# ============================================================

def render_household_form(
    household: Household | None = None,
) -> None:

    editing = household is not None

    st.subheader(
        "Edit Household"
        if editing
        else "Register New Household"
    )

    if editing:

        st.caption(
            f"Household ID: {household.id}"
        )

    # --------------------------------------------------------
    # BASIC
    # --------------------------------------------------------

    st.markdown(
        "### Household Information"
    )

    household_number = st.text_input(
        "Household Number *",
        value=(
            household.household_number
            if editing
            else ""
        ),
        key=(
            "household_number_edit"
            if editing
            else "household_number_new"
        ),
    )

    citizens = load_citizen_choices()

    citizen_map = {
        "": None,
    }

    for citizen in citizens:

        citizen_map[
            f"{citizen.full_name} — "
            f"{citizen.national_id or citizen.id}"
        ] = citizen.id

    options = list(
        citizen_map.keys()
    )

    current_head = ""

    if editing and household.head_citizen_id:

        for label, citizen_id in citizen_map.items():

            if citizen_id == household.head_citizen_id:

                current_head = label
                break

    head_index = (
        options.index(current_head)
        if current_head in options
        else 0
    )

    selected_head = st.selectbox(
        "Household Head",
        options,
        index=head_index,
        key=(
            "household_head_edit"
            if editing
            else "household_head_new"
        ),
    )

    head_citizen_id = citizen_map[
        selected_head
    ]

    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    st.markdown(
        "### Location"
    )

    col1, col2 = st.columns(2)

    with col1:

        state_or_region = st.text_input(
            "State / Region *",
            value=(
                household.state_or_region
                if editing
                else ""
            ),
            key=(
                "household_state_edit"
                if editing
                else "household_state_new"
            ),
        )

    with col2:

        county_or_payam = st.text_input(
            "County / Payam",
            value=(
                household.county_or_payam
                if editing
                else ""
            )
            or "",
            key=(
                "household_county_edit"
                if editing
                else "household_county_new"
            ),
        )

    col1, col2 = st.columns(2)

    with col1:

        sub_county_or_boma = st.text_input(
            "Sub-County / Boma",
            value=(
                household.sub_county_or_boma
                if editing
                else ""
            )
            or "",
            key=(
                "household_subcounty_edit"
                if editing
                else "household_subcounty_new"
            ),
        )

    with col2:

        boma = st.text_input(
            "Boma",
            value=(
                household.boma
                if editing
                else ""
            )
            or "",
            key=(
                "household_boma_edit"
                if editing
                else "household_boma_new"
            ),
        )

    community = st.text_input(
        "Community",
        value=(
            household.community
            if editing
            else ""
        )
        or "",
        key=(
            "household_community_edit"
            if editing
            else "household_community_new"
        ),
    )

    residential_address = st.text_area(
        "Residential Address",
        value=(
            household.residential_address
            if editing
            else ""
        )
        or "",
        key=(
            "household_address_edit"
            if editing
            else "household_address_new"
        ),
    )

    # --------------------------------------------------------
    # ACTIONS
    # --------------------------------------------------------

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        save = st.button(
            "Update Household"
            if editing
            else "Register Household",
            use_container_width=True,
            key=(
                "save_household_edit"
                if editing
                else "save_household_new"
            ),
        )

    with col2:

        cancel = st.button(
            "Cancel",
            use_container_width=True,
            key=(
                "cancel_household_edit"
                if editing
                else "cancel_household_new"
            ),
        )

    with col3:

        archive = False

        if editing:

            archive = st.button(
                "Archive Household",
                use_container_width=True,
                key="archive_household",
            )

    if cancel:

        st.session_state.household_editor_id = None
        st.rerun()

    if archive and editing:

        archive_household(
            str(household.id)
        )

        return

    if not save:

        return

    errors = []

    if not household_number.strip():

        errors.append(
            "Household Number is required."
        )

    if not state_or_region.strip():

        errors.append(
            "State / Region is required."
        )

    if errors:

        for error in errors:
            st.error(error)

        return

    save_household(
        household=household,
        household_number=household_number,
        head_citizen_id=head_citizen_id,
        state_or_region=state_or_region,
        county_or_payam=county_or_payam,
        sub_county_or_boma=sub_county_or_boma,
        boma=boma,
        community=community,
        residential_address=residential_address,
    )


# ============================================================
# PROFILE
# ============================================================

def render_household_profile(
    household: Household,
) -> None:

    st.subheader(
        "Household Profile"
    )

    st.markdown(
        f"### Household {household.household_number}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Members",
            len(
                household.members
            ),
        )

    with col2:

        st.metric(
            "State / Region",
            household.state_or_region
            or "Not provided",
        )

    with col3:

        st.metric(
            "County / Payam",
            household.county_or_payam
            or "Not provided",
        )

    st.divider()

    st.markdown(
        "### Household Location"
    )

    st.write(
        f"**State / Region:** "
        f"{household.state_or_region or 'Not provided'}"
    )

    st.write(
        f"**County / Payam:** "
        f"{household.county_or_payam or 'Not provided'}"
    )

    st.write(
        f"**Sub-County / Boma:** "
        f"{household.sub_county_or_boma or 'Not provided'}"
    )

    st.write(
        f"**Boma:** "
        f"{household.boma or 'Not provided'}"
    )

    st.write(
        f"**Community:** "
        f"{household.community or 'Not provided'}"
    )

    st.write(
        f"**Address:** "
        f"{household.residential_address or 'Not provided'}"
    )

    st.divider()

    st.markdown(
        "### Household Head"
    )

    head = None

    if household.head_citizen_id:

        db = get_session()

        if db is not None:

            try:

                head = (
                    db.query(Citizen)
                    .filter(
                        Citizen.id
                        == household.head_citizen_id
                    )
                    .first()
                )

            finally:

                db.close()

    if head:

        st.write(
            f"**Name:** {head.full_name}"
        )

        st.write(
            f"**National ID:** "
            f"{head.national_id or 'Not provided'}"
        )

    else:

        st.info(
            "No household head has been assigned."
        )

    st.divider()

    st.markdown(
        "### Household Members"
    )

    if household.members:

        for member in household.members:

            with st.container(
                border=True
            ):

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.write(
                        f"**{member.full_name}**"
                    )

                with col2:

                    st.write(
                        member.household_role
                    )

                with col3:

                    st.write(
                        member.national_id
                        or "No National ID"
                    )

    else:

        st.info(
            "No citizens are currently assigned "
            "to this household."
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Edit Household",
            use_container_width=True,
            key="edit_household_profile",
        ):

            st.session_state.household_editor_id = (
                str(household.id)
            )

            st.session_state.household_view_id = None

            st.rerun()

    with col2:

        if st.button(
            "Back to Households",
            use_container_width=True,
            key="back_households",
        ):

            st.session_state.household_view_id = None

            st.rerun()


# ============================================================
# MAIN
# ============================================================

def render() -> None:

    initialize_state()

    st.subheader(
        "Households"
    )

    st.caption(
        "Manage household registration, household heads "
        "and household members."
    )

    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    if st.session_state.household_view_id:

        household = get_household(
            st.session_state.household_view_id
        )

        if household is None:

            st.error(
                "Household record not found."
            )

            st.session_state.household_view_id = None

        else:

            render_household_profile(
                household
            )

            return

    # --------------------------------------------------------
    # EDIT
    # --------------------------------------------------------

    if st.session_state.household_editor_id:

        household = get_household(
            st.session_state.household_editor_id
        )

        if household is None:

            st.error(
                "Household record not found."
            )

            st.session_state.household_editor_id = None

        else:

            render_household_form(
                household
            )

            return

    # --------------------------------------------------------
    # ACTION
    # --------------------------------------------------------

    if st.button(
        "Register New Household",
        key="new_household",
    ):

        st.session_state.household_editor_id = "NEW"

        st.rerun()

    if (
        st.session_state.household_editor_id
        == "NEW"
    ):

        render_household_form(
            None
        )

        return

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    search = st.text_input(
        "Search Households",
        placeholder=(
            "Household number, community or address"
        ),
        key="household_search",
    )

    records = search_households(
        search_text=search,
    )

    st.caption(
        f"{len(records)} household(s) found."
    )

    if not records:

        st.info(
            "No household records found."
        )

        return

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    for household in records:

        with st.container(
            border=True
        ):

            col1, col2, col3, col4 = st.columns(
                [4, 2, 2, 2]
            )

            with col1:

                st.markdown(
                    f"### {household.household_number}"
                )

                st.caption(
                    household.community
                    or "Community not provided"
                )

            with col2:

                st.write(
                    f"**State:** "
                    f"{household.state_or_region}"
                )

            with col3:

                st.write(
                    f"**Members:** "
                    f"{len(household.members)}"
                )

            with col4:

                if st.button(
                    "View",
                    key=f"view_household_{household.id}",
                    use_container_width=True,
                ):

                    st.session_state.household_view_id = (
                        str(household.id)
                    )

                    st.rerun()

                if st.button(
                    "Edit",
                    key=f"edit_household_{household.id}",
                    use_container_width=True,
                ):

                    st.session_state.household_editor_id = (
                        str(household.id)
                    )

                    st.rerun()
