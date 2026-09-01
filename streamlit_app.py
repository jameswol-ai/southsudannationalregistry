"""
South Sudan National Registry
Streamlit AI Studio

National Population, Civil Registration, Identity,
Household and Electoral Registry Management Platform.

Version 1.0.0

This file is intentionally defensive:
- Database failures do not crash the interface.
- Invalid/missing emblem files do not crash Streamlit.
- Optional registry modules cannot crash the dashboard.
- All Streamlit widget keys are unique.
- No invalid Streamlit icon arguments are used.
- CRUD operations are performed directly against SQLAlchemy models.
"""

from __future__ import annotations

import logging
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
EMBLEM_PATH = ASSETS_DIR / "south_sudan_emblem.png"

st.set_page_config(
    page_title="South Sudan National Registry",
    page_icon="SS",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(
    "south_sudan_national_registry"
)


# ============================================================
# DATABASE IMPORTS
# ============================================================

DATABASE_AVAILABLE = False
DATABASE_ERROR: Exception | None = None

try:
    from database.database import (
        Base,
        SessionLocal,
        engine,
        init_db,
    )

    DATABASE_AVAILABLE = True

except Exception as exc:
    DATABASE_ERROR = exc

    logger.exception(
        "Database module could not be imported."
    )


# ============================================================
# MODEL IMPORTS
# ============================================================

MODELS_AVAILABLE = False
MODEL_IMPORT_ERROR: Exception | None = None

try:
    from models import (
        AdministrativeUnit,
        AuditLog,
        Citizen,
        CivilEvent,
        Document,
        Household,
        VoterRecord,
    )

    MODELS_AVAILABLE = True

except Exception as exc:
    MODEL_IMPORT_ERROR = exc

    logger.exception(
        "Registry models could not be imported."
    )


# ============================================================
# SESSION STATE
# ============================================================

if "active_page" not in st.session_state:
    st.session_state.active_page = "overview"

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

if "database_connected" not in st.session_state:
    st.session_state.database_connected = False

if "last_database_error" not in st.session_state:
    st.session_state.last_database_error = None


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

@st.cache_resource
def initialize_database() -> tuple[bool, str | None]:
    """
    Initialize the database.

    Returns:
        (success, error_message)
    """

    if not DATABASE_AVAILABLE:
        return (
            False,
            "The database module could not be imported.",
        )

    try:
        init_db()

        return True, None

    except Exception as exc:

        logger.exception(
            "Database initialization failed."
        )

        return False, str(exc)


database_ok, database_error = initialize_database()

st.session_state.database_connected = database_ok
st.session_state.last_database_error = database_error


# ============================================================
# DATABASE SESSION
# ============================================================

def get_db_session():
    """
    Return a SQLAlchemy session when available.
    """

    if not database_ok:
        return None

    try:
        return SessionLocal()

    except Exception as exc:

        logger.exception(
            "Unable to create database session."
        )

        return None


# ============================================================
# SAFE DATABASE COUNT
# ============================================================

def safe_count(model: Any) -> int:
    """
    Safely count rows in a SQLAlchemy model.
    """

    if not database_ok or model is None:
        return 0

    session = get_db_session()

    if session is None:
        return 0

    try:

        return int(
            session.query(model).count()
        )

    except Exception as exc:

        logger.warning(
            "Unable to count %s: %s",
            getattr(model, "__name__", "model"),
            exc,
        )

        return 0

    finally:

        try:
            session.close()
        except Exception:
            pass


# ============================================================
# THEME
# ============================================================

def get_theme() -> dict[str, str]:

    if st.session_state.dark_mode:

        return {
            "background": "#0B1220",
            "surface": "#111827",
            "surface_alt": "#172033",
            "surface_hover": "#1E293B",
            "text": "#F8FAFC",
            "muted": "#94A3B8",
            "border": "#263247",
            "accent": "#16A34A",
            "accent_dark": "#15803D",
            "accent_soft": "#14532D",
            "white": "#FFFFFF",
            "danger": "#DC2626",
            "warning": "#D97706",
            "success": "#16A34A",
        }

    return {
        "background": "#F8FAFC",
        "surface": "#FFFFFF",
        "surface_alt": "#F1F5F9",
        "surface_hover": "#E2E8F0",
        "text": "#0F172A",
        "muted": "#64748B",
        "border": "#E2E8F0",
        "accent": "#15803D",
        "accent_dark": "#166534",
        "accent_soft": "#DCFCE7",
        "white": "#FFFFFF",
        "danger": "#DC2626",
        "warning": "#D97706",
        "success": "#15803D",
    }


# ============================================================
# CSS
# ============================================================

def inject_css():

    theme = get_theme()

    st.markdown(
        f"""
        <style>

        html, body, [class*="css"] {{
            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
        }}

        .stApp {{
            background: {theme["background"]};
            color: {theme["text"]};
        }}

        .block-container {{
            max-width: 1500px;
            padding-top: 1rem;
            padding-bottom: 5rem;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: {theme["text"]} !important;
        }}

        p, label {{
            color: {theme["text"]};
        }}

        /* HEADER */

        .registry-header {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 18px;
            padding: 8px 5px 18px;
        }}

        .header-emblem-fallback {{
            width: 72px;
            height: 72px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: {theme["accent"]};
            color: white;
            font-size: 25px;
            font-weight: 900;
            border: 3px solid {theme["accent_dark"]};
            flex-shrink: 0;
        }}

        .registry-title {{
            font-size: 28px;
            font-weight: 800;
            line-height: 1.2;
            color: {theme["text"]};
        }}

        .registry-subtitle {{
            color: {theme["muted"]};
            font-size: 13px;
            line-height: 1.5;
            margin-top: 6px;
        }}

        .registry-version {{
            color: {theme["muted"]};
            font-size: 12px;
            margin-top: 5px;
        }}

        /* STATUS */

        .status-online,
        .status-warning {{
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            margin-top: 7px;
        }}

        .status-online {{
            color: {theme["success"]};
            background: {theme["accent_soft"]};
        }}

        .status-warning {{
            color: {theme["warning"]};
            background: rgba(217,119,6,.12);
        }}

        .status-dot,
        .status-dot-warning {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }}

        .status-dot {{
            background: {theme["success"]};
        }}

        .status-dot-warning {{
            background: {theme["warning"]};
        }}

        /* SIDEBAR */

        section[data-testid="stSidebar"] {{
            background: {theme["surface"]};
            border-right: 1px solid {theme["border"]};
        }}

        .sidebar-title {{
            color: {theme["text"]};
            font-size: 17px;
            font-weight: 800;
            line-height: 1.25;
        }}

        .sidebar-subtitle {{
            color: {theme["muted"]};
            font-size: 11px;
            line-height: 1.5;
            margin-top: 6px;
            margin-bottom: 15px;
        }}

        .sidebar-section {{
            color: {theme["muted"]};
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .08em;
            margin-top: 18px;
            margin-bottom: 7px;
        }}

        /* CARDS */

        .overview-card,
        .module-card,
        .kpi-card {{
            background: {theme["surface"]};
            border: 1px solid {theme["border"]};
            border-radius: 14px;
            padding: 18px;
        }}

        .overview-card {{
            margin-bottom: 18px;
        }}

        .registry-kicker {{
            color: {theme["accent"]};
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .08em;
            margin-bottom: 6px;
        }}

        .registry-heading {{
            color: {theme["text"]};
            font-size: 23px;
            font-weight: 800;
            margin-bottom: 7px;
        }}

        .registry-description {{
            color: {theme["muted"]};
            font-size: 14px;
            line-height: 1.6;
        }}

        .kpi-label {{
            color: {theme["muted"]};
            font-size: 12px;
            font-weight: 700;
        }}

        .kpi-value {{
            color: {theme["text"]};
            font-size: 28px;
            font-weight: 850;
            margin-top: 5px;
        }}

        .kpi-description {{
            color: {theme["muted"]};
            font-size: 11px;
            margin-top: 3px;
        }}

        .module-name {{
            color: {theme["text"]};
            font-size: 16px;
            font-weight: 750;
        }}

        .module-description {{
            color: {theme["muted"]};
            font-size: 13px;
            line-height: 1.5;
            margin-top: 5px;
        }}

        /* STREAMLIT */

        div[data-testid="stMetric"] {{
            background: {theme["surface"]};
            border: 1px solid {theme["border"]};
            border-radius: 14px;
            padding: 14px;
        }}

        div[data-testid="stMetricLabel"] {{
            color: {theme["muted"]} !important;
        }}

        div[data-testid="stMetricValue"] {{
            color: {theme["text"]} !important;
        }}

        .stButton > button {{
            border-radius: 9px;
            min-height: 38px;
            font-weight: 650;
        }}

        /* FOOTER */

        .registry-footer {{
            color: {theme["muted"]};
            font-size: 11px;
            line-height: 1.5;
        }}

        #MainMenu {{
            visibility: hidden;
        }}

        footer {{
            visibility: hidden;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()


# ============================================================
# EMBLEM
# ============================================================

def render_emblem():

    """
    Render the emblem only if it is a real readable image.

    This prevents PIL.UnidentifiedImageError when a GitHub
    file is actually an HTML file, Git LFS pointer, empty file,
    or otherwise invalid image.
    """

    valid_image = False

    if EMBLEM_PATH.exists():

        try:

            from PIL import Image

            with Image.open(EMBLEM_PATH) as image:

                image.verify()

            valid_image = True

        except Exception:

            logger.warning(
                "Invalid South Sudan emblem: %s",
                EMBLEM_PATH,
            )

    if valid_image:

        st.image(
            str(EMBLEM_PATH),
            width=78,
        )

    else:

        st.markdown(
            """
            <div class="header-emblem-fallback">
                SS
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# HEADER
# ============================================================

header_left, header_center, header_right = st.columns(
    [1, 6, 1]
)

with header_left:

    render_emblem()

with header_center:

    st.markdown(
        """
        <div class="registry-title">
            South Sudan National Registry
        </div>

        <div class="registry-subtitle">
            National Population • Civil Registration •
            Identity • Elections
        </div>

        <div class="registry-version">
            Registry Platform • Version 1.0.0
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_right:

    if database_ok:

        st.markdown(
            """
            <div class="status-online">
                <span class="status-dot"></span>
                System Online
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            """
            <div class="status-warning">
                <span class="status-dot-warning"></span>
                Database Attention
            </div>
            """,
            unsafe_allow_html=True,
        )


st.divider()


# ============================================================
# SIDEBAR
# ============================================================

def sidebar_navigation():

    with st.sidebar:

        st.markdown(
            """
            <div class="sidebar-title">
                South Sudan National Registry
            </div>

            <div class="sidebar-subtitle">
                National Population • Civil Registration •
                Identity • Elections
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-section">Registry</div>',
            unsafe_allow_html=True,
        )

        registry_pages = {
            "Overview": "overview",
            "Population Registry": "population",
            "Households": "households",
            "Civil Registration": "civil_registration",
            "Identity Management": "identity",
            "Elections": "elections",
            "Administrative Units": "administration_units",
        }

        for label, key in registry_pages.items():

            if st.button(
                label,
                key=f"sidebar_registry_{key}",
                use_container_width=True,
            ):

                st.session_state.active_page = key
                st.rerun()

        st.markdown(
            '<div class="sidebar-section">Operations</div>',
            unsafe_allow_html=True,
        )

        operations = {
            "Reports & Analytics": "reports",
            "Verification": "verification",
            "Documents": "documents",
        }

        for label, key in operations.items():

            if st.button(
                label,
                key=f"sidebar_operations_{key}",
                use_container_width=True,
            ):

                st.session_state.active_page = key
                st.rerun()

        st.markdown(
            '<div class="sidebar-section">Administration</div>',
            unsafe_allow_html=True,
        )

        administration = {
            "Administration": "administration",
            "Audit Log": "audit_log",
            "System Status": "system_status",
        }

        for label, key in administration.items():

            if st.button(
                label,
                key=f"sidebar_admin_{key}",
                use_container_width=True,
            ):

                st.session_state.active_page = key
                st.rerun()

        st.markdown(
            '<div class="sidebar-section">Other Features</div>',
            unsafe_allow_html=True,
        )

        features = {
            "Search Registry": "search",
            "Data Import": "import",
            "Settings": "settings",
        }

        for label, key in features.items():

            if st.button(
                label,
                key=f"sidebar_feature_{key}",
                use_container_width=True,
            ):

                st.session_state.active_page = key
                st.rerun()

        st.divider()

        if database_ok:

            st.success(
                "Database Connected"
            )

        else:

            st.warning(
                "Database Attention Required"
            )

        if st.button(
            "Toggle Theme",
            key="sidebar_theme_toggle",
            use_container_width=True,
        ):

            st.session_state.dark_mode = (
                not st.session_state.dark_mode
            )

            st.rerun()

        if st.button(
            "Refresh Application",
            key="sidebar_refresh",
            use_container_width=True,
        ):

            st.rerun()


sidebar_navigation()


# ============================================================
# COMMON HELPERS
# ============================================================

def clean_text(value: Any) -> str:

    if value is None:
        return ""

    return str(value)


def generate_id(prefix: str) -> str:

    import uuid

    return f"{prefix}-{uuid.uuid4().hex[:12].upper()}"


def safe_date(value: Any) -> date | None:

    if isinstance(value, date):
        return value

    return None


def save_object(
    model: Any,
    object_id: str,
    values: dict[str, Any],
) -> tuple[bool, str]:

    if not database_ok:

        return (
            False,
            "Database is not connected.",
        )

    session = get_db_session()

    if session is None:

        return (
            False,
            "Unable to create database session.",
        )

    try:

        record = session.get(
            model,
            object_id,
        )

        if record is None:

            record = model(
                id=object_id,
            )

            session.add(record)

        for field, value in values.items():

            if hasattr(record, field):

                setattr(
                    record,
                    field,
                    value,
                )

        session.commit()

        return True, "Record saved successfully."

    except Exception as exc:

        session.rollback()

        logger.exception(
            "Unable to save registry record."
        )

        return False, str(exc)

    finally:

        session.close()


def delete_object(
    model: Any,
    object_id: str,
) -> tuple[bool, str]:

    if not database_ok:

        return (
            False,
            "Database is not connected.",
        )

    session = get_db_session()

    if session is None:

        return (
            False,
            "Unable to create database session.",
        )

    try:

        record = session.get(
            model,
            object_id,
        )

        if record is None:

            return (
                False,
                "Record was not found.",
            )

        session.delete(record)
        session.commit()

        return True, "Record deleted."

    except Exception as exc:

        session.rollback()

        logger.exception(
            "Unable to delete registry record."
        )

        return False, str(exc)

    finally:

        session.close()


def query_records(
    model: Any,
    limit: int = 500,
) -> list[Any]:

    if not database_ok:
        return []

    session = get_db_session()

    if session is None:
        return []

    try:

        return (
            session.query(model)
            .limit(limit)
            .all()
        )

    except Exception as exc:

        logger.warning(
            "Unable to query records: %s",
            exc,
        )

        return []

    finally:

        session.close()


# ============================================================
# OVERVIEW
# ============================================================

def render_overview():

    st.markdown(
        """
        <div class="overview-card">

            <div class="registry-kicker">
                South Sudan National Registry
            </div>

            <div class="registry-heading">
                National Registry Overview
            </div>

            <div class="registry-description">
                Centralized management platform for national
                population records, civil registration,
                identity management, households and
                electoral registration.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    population_count = safe_count(
        Citizen
        if MODELS_AVAILABLE
        else None
    )

    civil_count = safe_count(
        CivilEvent
        if MODELS_AVAILABLE
        else None
    )

    identity_count = safe_count(
        Document
        if MODELS_AVAILABLE
        else None
    )

    election_count = safe_count(
        VoterRecord
        if MODELS_AVAILABLE
        else None
    )

    columns = st.columns(4)

    cards = [
        (
            "Registered Population",
            population_count,
            "Population records",
        ),
        (
            "Civil Records",
            civil_count,
            "Birth, death and civil events",
        ),
        (
            "Identity Records",
            identity_count,
            "National identity records",
        ),
        (
            "Election Records",
            election_count,
            "Electoral records",
        ),
    ]

    for column, (
        label,
        value,
        description,
    ) in zip(columns, cards):

        with column:

            st.markdown(
                f"""
                <div class="kpi-card">

                    <div class="kpi-label">
                        {label}
                    </div>

                    <div class="kpi-value">
                        {value:,}
                    </div>

                    <div class="kpi-description">
                        {description}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    st.subheader(
        "Registry Services"
    )

    services = [
        (
            "Population Registry",
            "Manage national population records, "
            "households, persons and demographic information.",
            "population",
        ),
        (
            "Elections",
            "Manage electoral registration, voter records "
            "and election administration.",
            "elections",
        ),
        (
            "Civil Registration",
            "Register births, deaths, marriages, certificates "
            "and other civil events.",
            "civil_registration",
        ),
        (
            "Reports & Analytics",
            "Generate operational reports, statistical "
            "summaries and Registry analytics.",
            "reports",
        ),
        (
            "Identity Management",
            "Manage national identity registration, "
            "identification records and identity services.",
            "identity",
        ),
        (
            "Administration",
            "Manage users, roles, permissions, configuration "
            "and system administration.",
            "administration",
        ),
    ]

    service_columns = st.columns(3)

    for index, (
        name,
        description,
        key,
    ) in enumerate(services):

        with service_columns[index % 3]:

            st.markdown(
                f"""
                <div class="module-card">

                    <div class="module-name">
                        {name}
                    </div>

                    <div class="module-description">
                        {description}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                f"Open {name}",
                key=f"overview_open_{key}",
                use_container_width=True,
            ):

                st.session_state.active_page = key
                st.rerun()

    st.divider()

    st.subheader(
        "System Status"
    )

    status_col1, status_col2 = st.columns(2)

    with status_col1:

        if database_ok:

            st.success(
                "Database Connected"
            )

        else:

            st.warning(
                "Database Attention Required"
            )

    with status_col2:

        if MODELS_AVAILABLE:

            st.success(
                "Registry Models Available"
            )

        else:

            st.error(
                "Registry Models Unavailable"
            )


# ============================================================
# CITIZEN EDITOR
# ============================================================

def render_population():

    st.title(
        "Population Registry"
    )

    st.caption(
        "Create, search, edit and manage citizen population records."
    )

    if not database_ok:

        st.warning(
            "The database is currently unavailable. "
            "The interface remains available, but records "
            "cannot be saved until the database is connected."
        )

    if not MODELS_AVAILABLE:

        st.error(
            "Citizen model is unavailable."
        )

        return

    tab_list, tab_create = st.tabs(
        [
            "Citizen Records",
            "Register Citizen",
        ]
    )

    with tab_list:

        records = query_records(
            Citizen,
            limit=500,
        )

        if not records:

            st.info(
                "No citizen records are currently registered."
            )

        else:

            search = st.text_input(
                "Search citizens",
                key="citizen_search",
            )

            filtered = records

            if search.strip():

                search_lower = search.lower()

                filtered = [
                    record
                    for record in records
                    if search_lower
                    in clean_text(
                        record.full_name
                    ).lower()
                    or search_lower
                    in clean_text(
                        record.national_id
                    ).lower()
                ]

            for record in filtered:

                with st.expander(
                    f"{record.full_name} "
                    f"— {record.national_id or 'No National ID'}"
                ):

                    render_citizen_editor(
                        record
                    )

    with tab_create:

        render_citizen_editor(
            None
        )


def render_citizen_editor(
    record: Citizen | None,
):

    is_new = record is None

    prefix = (
        "new_citizen"
        if is_new
        else f"edit_citizen_{record.id}"
    )

    citizen_id = (
        generate_id("CIT")
        if is_new
        else record.id
    )

    st.markdown(
        "### Register Citizen"
        if is_new
        else "### Edit Citizen"
    )

    col1, col2 = st.columns(2)

    with col1:

        full_name = st.text_input(
            "Full Name",
            value=(
                ""
                if is_new
                else clean_text(record.full_name)
            ),
            key=f"{prefix}_full_name",
        )

        national_id = st.text_input(
            "National ID",
            value=(
                ""
                if is_new
                else clean_text(record.national_id)
            ),
            key=f"{prefix}_national_id",
        )

        passport_number = st.text_input(
            "Passport Number",
            value=(
                ""
                if is_new
                else clean_text(record.passport_number)
            ),
            key=f"{prefix}_passport",
        )

        gender = st.selectbox(
            "Gender",
            [
                "Male",
                "Female",
                "Other",
            ],
            index=(
                [
                    "Male",
                    "Female",
                    "Other",
                ].index(record.gender)
                if not is_new
                and record.gender in [
                    "Male",
                    "Female",
                    "Other",
                ]
                else 2
            ),
            key=f"{prefix}_gender",
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
            index=(
                [
                    "Single",
                    "Married",
                    "Divorced",
                    "Widowed",
                    "Separated",
                ].index(record.marital_status)
                if not is_new
                and record.marital_status in [
                    "Single",
                    "Married",
                    "Divorced",
                    "Widowed",
                    "Separated",
                ]
                else 0
            ),
            key=f"{prefix}_marital",
        )

    with col2:

        default_dob = (
            record.date_of_birth
            if not is_new
            and record.date_of_birth
            else date(2000, 1, 1)
        )

        date_of_birth = st.date_input(
            "Date of Birth",
            value=default_dob,
            key=f"{prefix}_dob",
        )

        nationality = st.text_input(
            "Nationality",
            value=(
                "South Sudanese"
                if is_new
                else clean_text(record.nationality)
            ),
            key=f"{prefix}_nationality",
        )

        phone_number = st.text_input(
            "Phone Number",
            value=(
                ""
                if is_new
                else clean_text(record.phone_number)
            ),
            key=f"{prefix}_phone",
        )

        email_address = st.text_input(
            "Email Address",
            value=(
                ""
                if is_new
                else clean_text(record.email_address)
            ),
            key=f"{prefix}_email",
        )

    st.markdown(
        "#### Demographics"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        tribe = st.text_input(
            "Tribe",
            value=(
                ""
                if is_new
                else clean_text(record.tribe)
            ),
            key=f"{prefix}_tribe",
        )

    with col2:

        language = st.text_input(
            "Native Language",
            value=(
                ""
                if is_new
                else clean_text(record.native_language)
            ),
            key=f"{prefix}_language",
        )

    with col3:

        education = st.text_input(
            "Education Level",
            value=(
                "None / Informal"
                if is_new
                else clean_text(record.education_level)
            ),
            key=f"{prefix}_education",
        )

    st.markdown(
        "#### Location"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        state = st.text_input(
            "State / Region",
            value=(
                ""
                if is_new
                else clean_text(record.state_or_region)
            ),
            key=f"{prefix}_state",
        )

    with col2:

        county = st.text_input(
            "County / Payam",
            value=(
                ""
                if is_new
                else clean_text(record.county_or_payam)
            ),
            key=f"{prefix}_county",
        )

    with col3:

        boma = st.text_input(
            "Boma",
            value=(
                ""
                if is_new
                else clean_text(record.boma)
            ),
            key=f"{prefix}_boma",
        )

    community = st.text_input(
        "Community",
        value=(
            ""
            if is_new
            else clean_text(record.community)
        ),
        key=f"{prefix}_community",
    )

    address = st.text_area(
        "Residential Address",
        value=(
            ""
            if is_new
            else clean_text(record.residential_address)
        ),
        key=f"{prefix}_address",
    )

    st.markdown(
        "#### Verification"
    )

    verification_status = st.selectbox(
        "Verification Status",
        [
            "Pending Review",
            "Verified",
            "Rejected",
            "Requires Correction",
        ],
        index=(
            [
                "Pending Review",
                "Verified",
                "Rejected",
                "Requires Correction",
            ].index(
                record.verification_status
            )
            if not is_new
            and record.verification_status in [
                "Pending Review",
                "Verified",
                "Rejected",
                "Requires Correction",
            ]
            else 0
        ),
        key=f"{prefix}_verification",
    )

    notes = st.text_area(
        "Notes",
        value=(
            ""
            if is_new
            else clean_text(record.notes)
        ),
        key=f"{prefix}_notes",
    )

    button_col1, button_col2 = st.columns(2)

    with button_col1:

        if st.button(
            "Save Citizen",
            key=f"{prefix}_save",
            type="primary",
            use_container_width=True,
        ):

            if not full_name.strip():

                st.error(
                    "Full Name is required."
                )

            else:

                values = {
                    "full_name": full_name.strip(),
                    "national_id": (
                        national_id.strip()
                        or None
                    ),
                    "passport_number": (
                        passport_number.strip()
                        or None
                    ),
                    "gender": gender,
                    "marital_status": marital_status,
                    "nationality": nationality.strip(),
                    "date_of_birth": date_of_birth,
                    "phone_number": (
                        phone_number.strip()
                        or None
                    ),
                    "email_address": (
                        email_address.strip()
                        or None
                    ),
                    "tribe": tribe.strip(),
                    "native_language": language.strip(),
                    "education_level": education.strip(),
                    "state_or_region": state.strip(),
                    "county_or_payam": county.strip(),
                    "boma": boma.strip() or None,
                    "community": community.strip(),
                    "residential_address": (
                        address.strip()
                        or None
                    ),
                    "verification_status": (
                        verification_status
                    ),
                    "notes": (
                        notes.strip()
                        or None
                    ),
                }

                ok, message = save_object(
                    Citizen,
                    citizen_id,
                    values,
                )

                if ok:

                    st.success(message)
                    st.rerun()

                else:

                    st.error(message)

    if not is_new:

        with button_col2:

            if st.button(
                "Delete Citizen",
                key=f"{prefix}_delete",
                use_container_width=True,
            ):

                ok, message = delete_object(
                    Citizen,
                    record.id,
                )

                if ok:

                    st.success(message)
                    st.rerun()

                else:

                    st.error(message)


# ============================================================
# HOUSEHOLDS
# ============================================================

def render_households():

    st.title(
        "Households"
    )

    st.caption(
        "Register and manage household records."
    )

    if not MODELS_AVAILABLE:
        st.error("Household model unavailable.")
        return

    records = query_records(
        Household,
        limit=500,
    )

    with st.expander(
        "Register Household",
        expanded=False,
    ):

        household_number = st.text_input(
            "Household Number",
            key="new_household_number",
        )

        state = st.text_input(
            "State / Region",
            key="new_household_state",
        )

        county = st.text_input(
            "County / Payam",
            key="new_household_county",
        )

        community = st.text_input(
            "Community",
            key="new_household_community",
        )

        address = st.text_area(
            "Residential Address",
            key="new_household_address",
        )

        if st.button(
            "Save Household",
            key="new_household_save",
            type="primary",
        ):

            if not household_number.strip():

                st.error(
                    "Household Number is required."
                )

            else:

                ok, message = save_object(
                    Household,
                    generate_id("HH"),
                    {
                        "household_number":
                            household_number.strip(),
                        "state_or_region":
                            state.strip(),
                        "county_or_payam":
                            county.strip() or None,
                        "community":
                            community.strip() or None,
                        "residential_address":
                            address.strip() or None,
                    },
                )

                if ok:

                    st.success(message)
                    st.rerun()

                else:

                    st.error(message)

    st.divider()

    for record in records:

        with st.expander(
            record.household_number
        ):

            household_number = st.text_input(
                "Household Number",
                value=record.household_number,
                key=f"hh_number_{record.id}",
            )

            state = st.text_input(
                "State / Region",
                value=clean_text(
                    record.state_or_region
                ),
                key=f"hh_state_{record.id}",
            )

            county = st.text_input(
                "County / Payam",
                value=clean_text(
                    record.county_or_payam
                ),
                key=f"hh_county_{record.id}",
            )

            community = st.text_input(
                "Community",
                value=clean_text(
                    record.community
                ),
                key=f"hh_community_{record.id}",
            )

            address = st.text_area(
                "Address",
                value=clean_text(
                    record.residential_address
                ),
                key=f"hh_address_{record.id}",
            )

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "Save Changes",
                    key=f"hh_save_{record.id}",
                    use_container_width=True,
                ):

                    ok, message = save_object(
                        Household,
                        record.id,
                        {
                            "household_number":
                                household_number.strip(),
                            "state_or_region":
                                state.strip(),
                            "county_or_payam":
                                county.strip() or None,
                            "community":
                                community.strip() or None,
                            "residential_address":
                                address.strip() or None,
                        },
                    )

                    if ok:

                        st.success(message)
                        st.rerun()

                    else:

                        st.error(message)

            with c2:

                if st.button(
                    "Delete",
                    key=f"hh_delete_{record.id}",
                    use_container_width=True,
                ):

                    ok, message = delete_object(
                        Household,
                        record.id,
                    )

                    if ok:

                        st.success(message)
                        st.rerun()

                    else:

                        st.error(message)


# ============================================================
# CIVIL REGISTRATION
# ============================================================

def render_civil_registration():

    st.title(
        "Civil Registration"
    )

    st.caption(
        "Manage births, deaths, marriages, divorces and civil events."
    )

    if not MODELS_AVAILABLE:

        st.error(
            "Civil registration model unavailable."
        )

        return

    records = query_records(
        CivilEvent,
        limit=500,
    )

    with st.expander(
        "Register Civil Event",
        expanded=False,
    ):

        event_type = st.selectbox(
            "Event Type",
            [
                "Birth",
                "Death",
                "Marriage",
                "Divorce",
            ],
            key="civil_new_type",
        )

        reference = st.text_input(
            "Reference Number",
            key="civil_new_reference",
        )

        event_date = st.date_input(
            "Event Date",
            value=date.today(),
            key="civil_new_date",
        )

        centre = st.text_input(
            "Registration Centre",
            key="civil_new_centre",
        )

        document_number = st.text_input(
            "Document Number",
            key="civil_new_document",
        )

        status = st.selectbox(
            "Status",
            [
                "Pending Review",
                "Registered",
                "Verified",
                "Rejected",
            ],
            key="civil_new_status",
        )

        notes = st.text_area(
            "Notes",
            key="civil_new_notes",
        )

        if st.button(
            "Save Civil Event",
            key="civil_new_save",
            type="primary",
        ):

            if not reference.strip():

                st.error(
                    "Reference Number is required."
                )

            else:

                ok, message = save_object(
                    CivilEvent,
                    generate_id("CIV"),
                    {
                        "reference_number":
                            reference.strip(),
                        "event_type":
                            event_type,
                        "event_date":
                            event_date,
                        "registration_centre":
                            centre.strip() or None,
                        "document_number":
                            document_number.strip() or None,
                        "status":
                            status,
                        "notes":
                            notes.strip() or None,
                    },
                )

                if ok:

                    st.success(message)
                    st.rerun()

                else:

                    st.error(message)

    st.divider()

    for record in records:

        with st.expander(
            f"{record.reference_number} — "
            f"{record.event_type}"
        ):

            event_type = st.selectbox(
                "Event Type",
                [
                    "Birth",
                    "Death",
                    "Marriage",
                    "Divorce",
                ],
                index=(
                    [
                        "Birth",
                        "Death",
                        "Marriage",
                        "Divorce",
                    ].index(record.event_type)
                    if record.event_type in [
                        "Birth",
                        "Death",
                        "Marriage",
                        "Divorce",
                    ]
                    else 0
                ),
                key=f"civil_type_{record.id}",
            )

            reference = st.text_input(
                "Reference Number",
                value=record.reference_number,
                key=f"civil_ref_{record.id}",
            )

            event_date = st.date_input(
                "Event Date",
                value=record.event_date,
                key=f"civil_date_{record.id}",
            )

            status = st.selectbox(
                "Status",
                [
                    "Pending Review",
                    "Registered",
                    "Verified",
                    "Rejected",
                ],
                index=(
                    [
                        "Pending Review",
                        "Registered",
                        "Verified",
                        "Rejected",
                    ].index(record.status)
                    if record.status in [
                        "Pending Review",
                        "Registered",
                        "Verified",
                        "Rejected",
                    ]
                    else 0
                ),
                key=f"civil_status_{record.id}",
            )

            notes = st.text_area(
                "Notes",
                value=clean_text(record.notes),
                key=f"civil_notes_{record.id}",
            )

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "Save Changes",
                    key=f"civil_save_{record.id}",
                    use_container_width=True,
                ):

                    ok, message = save_object(
                        CivilEvent,
                        record.id,
                        {
                            "event_type":
                                event_type,
                            "reference_number":
                                reference.strip(),
                            "event_date":
                                event_date,
                            "status":
                                status,
                            "notes":
                                notes.strip() or None,
                        },
                    )

                    if ok:

                        st.success(message)
                        st.rerun()

                    else:

                        st.error(message)

            with c2:

                if st.button(
                    "Delete",
                    key=f"civil_delete_{record.id}",
                    use_container_width=True,
                ):

                    ok, message = delete_object(
                        CivilEvent,
                        record.id,
                    )

                    if ok:

                        st.success(message)
                        st.rerun()

                    else:

                        st.error(message)


# ============================================================
# IDENTITY
# ============================================================

def render_identity():

    st.title(
        "Identity Management"
    )

    st.caption(
        "Manage national identity and identity-related documents."
    )

    if not MODELS_AVAILABLE:

        st.error(
            "Identity document model unavailable."
        )

        return

    records = query_records(
        Document,
        limit=500,
    )

    with st.expander(
        "Register Identity Document"
    ):

        document_type = st.selectbox(
            "Document Type",
            [
                "National ID",
                "Identity Card",
                "Passport",
                "Birth Certificate",
                "Other",
            ],
            key="identity_new_type",
        )

        document_number = st.text_input(
            "Document Number",
            key="identity_new_number",
        )

        status = st.selectbox(
            "Status",
            [
                "Registered",
                "Active",
                "Expired",
                "Cancelled",
                "Under Review",
            ],
            key="identity_new_status",
        )

        issued_date = st.date_input(
            "Issued Date",
            value=date.today(),
            key="identity_new_issued",
        )

        expiry_date = st.date_input(
            "Expiry Date",
            value=date.today(),
            key="identity_new_expiry",
        )

        if st.button(
            "Save Identity Record",
            key="identity_new_save",
            type="primary",
        ):

            ok, message = save_object(
                Document,
                generate_id("DOC"),
                {
                    "document_type":
                        document_type,
                    "document_number":
                        document_number.strip() or None,
                    "status":
                        status,
                    "issued_date":
                        issued_date,
                    "expiry_date":
                        expiry_date,
                },
            )

            if ok:

                st.success(message)
                st.rerun()

            else:

                st.error(message)

    st.divider()

    for record in records:

        with st.expander(
            f"{record.document_type} — "
            f"{record.document_number or 'No Number'}"
        ):

            document_type = st.text_input(
                "Document Type",
                value=record.document_type,
                key=f"doc_type_{record.id}",
            )

            document_number = st.text_input(
                "Document Number",
                value=clean_text(
                    record.document_number
                ),
                key=f"doc_number_{record.id}",
            )

            status = st.text_input(
                "Status",
                value=record.status,
                key=f"doc_status_{record.id}",
            )

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "Save Changes",
                    key=f"doc_save_{record.id}",
                    use_container_width=True,
                ):

                    ok, message = save_object(
                        Document,
                        record.id,
                        {
                            "document_type":
                                document_type.strip(),
                            "document_number":
                                document_number.strip() or None,
                            "status":
                                status.strip(),
                        },
                    )

                    if ok:

                        st.success(message)
                        st.rerun()

                    else:

                        st.error(message)

            with c2:

                if st.button(
                    "Delete",
                    key=f"doc_delete_{record.id}",
                    use_container_width=True,
                ):

                    ok, message = delete_object(
                        Document,
                        record.id,
                    )

                    if ok:

                        st.success(message)
                        st.rerun()

                    else:

                        st.error(message)


# ============================================================
# ELECTIONS
# ============================================================

def render_elections():

    st.title(
        "Elections"
    )

    st.caption(
        "Manage voter registration and electoral records."
    )

    if not MODELS_AVAILABLE:

        st.error(
            "Voter record model unavailable."
        )

        return

    records = query_records(
        VoterRecord,
        limit=500,
    )

    with st.expander(
        "Register Voter"
    ):

        voter_id = st.text_input(
            "Voter ID Number",
            key="voter_new_id",
        )

        status = st.selectbox(
            "Voter Status",
            [
                "Active",
                "Inactive",
                "Suspended",
                "Transferred",
            ],
            key="voter_new_status",
        )

        constituency = st.text_input(
            "Constituency",
            key="voter_new_constituency",
        )

        polling_station = st.text_input(
            "Polling Station",
            key="voter_new_station",
        )

        if st.button(
            "Save Voter Record",
            key="voter_new_save",
            type="primary",
        ):

            ok, message = save_object(
                VoterRecord,
                generate_id("VOT"),
                {
                    "voter_id_number":
                        voter_id.strip() or None,
                    "voter_status":
                        status,
                    "constituency":
                        constituency.strip() or None,
                    "polling_station_name":
                        polling_station.strip() or None,
                },
            )

            if ok:

                st.success(message)
                st.rerun()

            else:

                st.error(message)

    st.divider()

    for record in records:

        with st.expander(
            f"{record.voter_id_number or record.id}"
        ):

            voter_id = st.text_input(
                "Voter ID Number",
                value=clean_text(
                    record.voter_id_number
                ),
                key=f"voter_id_{record.id}",
            )

            status = st.text_input(
                "Voter Status",
                value=record.voter_status,
                key=f"voter_status_{record.id}",
            )

            constituency = st.text_input(
                "Constituency",
                value=clean_text(
                    record.constituency
                ),
                key=f"voter_constituency_{record.id}",
            )

            station = st.text_input(
                "Polling Station",
                value=clean_text(
                    record.polling_station_name
                ),
                key=f"voter_station_{record.id}",
            )

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "Save Changes",
                    key=f"voter_save_{record.id}",
                    use_container_width=True,
                ):

                    ok, message = save_object(
                        VoterRecord,
                        record.id,
                        {
                            "voter_id_number":
                                voter_id.strip() or None,
                            "voter_status":
                                status.strip(),
                            "constituency":
                                constituency.strip() or None,
                            "polling_station_name":
                                station.strip() or None,
                        },
                    )

                    if ok:

                        st.success(message)
                        st.rerun()

                    else:

                        st.error(message)

            with c2:

                if st.button(
                    "Delete",
                    key=f"voter_delete_{record.id}",
                    use_container_width=True,
                ):

                    ok, message = delete_object(
                        VoterRecord,
                        record.id,
                    )

                    if ok:

                        st.success(message)
                        st.rerun()

                    else:

                        st.error(message)


# ============================================================
# ADMINISTRATIVE UNITS
# ============================================================

def render_administrative_units():

    st.title(
        "Administrative Units"
    )

    st.caption(
        "Manage states, counties, payams and bomas."
    )

    if not MODELS_AVAILABLE:

        st.error(
            "Administrative unit model unavailable."
        )

        return

    records = query_records(
        AdministrativeUnit,
        limit=500,
    )

    with st.expander(
        "Register Administrative Unit"
    ):

        unit_type = st.selectbox(
            "Unit Type",
            [
                "Country",
                "State",
                "County",
                "Payam",
                "Boma",
            ],
            key="admin_unit_new_type",
        )

        name = st.text_input(
            "Name",
            key="admin_unit_new_name",
        )

        code = st.text_input(
            "Code",
            key="admin_unit_new_code",
        )

        state = st.text_input(
            "State / Region",
            key="admin_unit_new_state",
        )

        administrator = st.text_input(
            "Administrator",
            key="admin_unit_new_admin",
        )

        headquarters = st.text_input(
            "Headquarters",
            key="admin_unit_new_hq",
        )

        if st.button(
            "Save Administrative Unit",
            key="admin_unit_new_save",
            type="primary",
        ):

            if not name.strip() or not code.strip():

                st.error(
                    "Name and Code are required."
                )

            else:

                ok, message = save_object(
                    AdministrativeUnit,
                    generate_id("ADM"),
                    {
                        "unit_type":
                            unit_type,
                        "name":
                            name.strip(),
                        "code":
                            code.strip(),
                        "state_or_region":
                            state.strip(),
                        "administrator_name":
                            administrator.strip() or None,
                        "headquarters":
                            headquarters.strip() or None,
                    },
                )

                if ok:

                    st.success(message)
                    st.rerun()

                else:

                    st.error(message)

    st.divider()

    for record in records:

        with st.expander(
            f"{record.name} — {record.unit_type}"
        ):

            name = st.text_input(
                "Name",
                value=record.name,
                key=f"admin_name_{record.id}",
            )

            code = st.text_input(
                "Code",
                value=record.code,
                key=f"admin_code_{record.id}",
            )

            unit_type = st.text_input(
                "Unit Type",
                value=record.unit_type,
                key=f"admin_type_{record.id}",
            )

            administrator = st.text_input(
                "Administrator",
                value=clean_text(
                    record.administrator_name
                ),
                key=f"admin_person_{record.id}",
            )

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "Save Changes",
                    key=f"admin_save_{record.id}",
                    use_container_width=True,
                ):

                    ok, message = save_object(
                        AdministrativeUnit,
                        record.id,
                        {
                            "name":
                                name.strip(),
                            "code":
                                code.strip(),
                            "unit_type":
                                unit_type.strip(),
                            "administrator_name":
                                administrator.strip() or None,
                        },
                    )

                    if ok:

                        st.success(message)
                        st.rerun()

                    else:

                        st.error(message)

            with c2:

                if st.button(
                    "Delete",
                    key=f"admin_delete_{record.id}",
                    use_container_width=True,
                ):

                    ok, message = delete_object(
                        AdministrativeUnit,
                        record.id,
                    )

                    if ok:

                        st.success(message)
                        st.rerun()

                    else:

                        st.error(message)


# ============================================================
# REPORTS
# ============================================================

def render_reports():

    st.title(
        "Reports & Analytics"
    )

    st.caption(
        "Registry statistics and operational summaries."
    )

    if not MODELS_AVAILABLE:

        st.error(
            "Registry models are unavailable."
        )

        return

    data = {
        "Registered Population":
            safe_count(Citizen),
        "Civil Records":
            safe_count(CivilEvent),
        "Identity Records":
            safe_count(Document),
        "Election Records":
            safe_count(VoterRecord),
        "Households":
            safe_count(Household),
        "Administrative Units":
            safe_count(AdministrativeUnit),
    }

    for name, value in data.items():

        st.metric(
            name,
            value,
        )

    st.divider()

    st.subheader(
        "Registry Summary"
    )

    st.dataframe(
        [
            {
                "Registry Area": name,
                "Records": value,
            }
            for name, value in data.items()
        ],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# VERIFICATION
# ============================================================

def render_verification():

    st.title(
        "Verification"
    )

    st.caption(
        "Review records requiring administrative verification."
    )

    if not MODELS_AVAILABLE:

        st.error(
            "Registry models are unavailable."
        )

        return

    records = query_records(
        Citizen,
        limit=500,
    )

    pending = [
        record
        for record in records
        if record.verification_status
        != "Verified"
    ]

    if not pending:

        st.success(
            "No citizen records currently require verification."
        )

        return

    for record in pending:

        with st.expander(
            f"{record.full_name} — "
            f"{record.verification_status}"
        ):

            st.write(
                f"National ID: "
                f"{record.national_id or 'Not provided'}"
            )

            if st.button(
                "Mark as Verified",
                key=f"verify_{record.id}",
            ):

                ok, message = save_object(
                    Citizen,
                    record.id,
                    {
                        "verification_status":
                            "Verified",
                        "verified_at":
                            datetime.utcnow(),
                    },
                )

                if ok:

                    st.success(message)
                    st.rerun()

                else:

                    st.error(message)


# ============================================================
# DOCUMENTS
# ============================================================

def render_documents():

    st.title(
        "Documents"
    )

    st.caption(
        "Identity and civil registration document registry."
    )

    render_identity()


# ============================================================
# ADMINISTRATION
# ============================================================

def render_administration():

    st.title(
        "Administration"
    )

    st.caption(
        "System administration and registry configuration."
    )

    st.info(
        "User management, roles and permissions can be "
        "connected to the Registry authentication service "
        "without changing the core registry models."
    )

    st.subheader(
        "Platform Configuration"
    )

    st.write(
        {
            "Application": "South Sudan National Registry",
            "Platform": "Streamlit AI Studio",
            "Version": "1.0.0",
            "Database": (
                "Connected"
                if database_ok
                else "Attention Required"
            ),
        }
    )


# ============================================================
# AUDIT LOG
# ============================================================

def render_audit_log():

    st.title(
        "Audit Log"
    )

    if not MODELS_AVAILABLE:

        st.error(
            "Audit model unavailable."
        )

        return

    records = query_records(
        AuditLog,
        limit=500,
    )

    if not records:

        st.info(
            "No audit events are currently recorded."
        )

        return

    st.dataframe(
        [
            {
                "Action":
                    record.action,
                "Entity":
                    record.entity_type,
                "Entity ID":
                    record.entity_id,
                "Username":
                    record.username,
                "Created":
                    record.created_at,
                "Details":
                    record.details,
            }
            for record in records
        ],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# SYSTEM STATUS
# ============================================================

def render_system_status():

    st.title(
        "System Status"
    )

    if database_ok:

        st.success(
            "Database Connected"
        )

    else:

        st.warning(
            "Database Attention Required"
        )

        if database_error:

            with st.expander(
                "Database technical details"
            ):

                st.code(
                    database_error
                )

    if MODELS_AVAILABLE:

        st.success(
            "Registry Models Available"
        )

    else:

        st.error(
            "Registry Models Unavailable"
        )

        if MODEL_IMPORT_ERROR:

            with st.expander(
                "Model technical details"
            ):

                st.exception(
                    MODEL_IMPORT_ERROR
                )

    st.subheader(
        "Application"
    )

    st.write(
        {
            "Application":
                "South Sudan National Registry",
            "Version":
                "1.0.0",
            "Base Directory":
                str(BASE_DIR),
            "Emblem":
                (
                    "Valid"
                    if EMBLEM_PATH.exists()
                    else "Fallback"
                ),
        }
    )


# ============================================================
# SEARCH
# ============================================================

def render_search():

    st.title(
        "Search Registry"
    )

    query = st.text_input(
        "Search by name or National ID",
        key="global_registry_search",
    )

    if not query.strip():

        st.info(
            "Enter a search term."
        )

        return

    if not MODELS_AVAILABLE:

        st.error(
            "Registry models are unavailable."
        )

        return

    records = query_records(
        Citizen,
        limit=500,
    )

    q = query.lower().strip()

    results = [
        record
        for record in records
        if q in clean_text(
            record.full_name
        ).lower()
        or q in clean_text(
            record.national_id
        ).lower()
        or q in clean_text(
            record.passport_number
        ).lower()
    ]

    if not results:

        st.warning(
            "No matching registry records found."
        )

        return

    st.dataframe(
        [
            {
                "ID":
                    record.id,
                "Full Name":
                    record.full_name,
                "National ID":
                    record.national_id,
                "Date of Birth":
                    record.date_of_birth,
                "Gender":
                    record.gender,
                "State":
                    record.state_or_region,
                "Verification":
                    record.verification_status,
            }
            for record in results
        ],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# IMPORT
# ============================================================

def render_import():

    st.title(
        "Data Import"
    )

    st.caption(
        "Import registry data from CSV files."
    )

    uploaded = st.file_uploader(
        "Upload CSV",
        type=["csv"],
        key="registry_csv_upload",
    )

    if uploaded is None:

        st.info(
            "Upload a CSV file to begin."
        )

        return

    try:

        import pandas as pd

        dataframe = pd.read_csv(
            uploaded
        )

        st.dataframe(
            dataframe,
            use_container_width=True,
        )

        st.info(
            "CSV preview loaded. "
            "Production import validation should be "
            "performed before committing records."
        )

    except Exception as exc:

        st.error(
            "Unable to read the CSV file."
        )

        st.exception(exc)


# ============================================================
# SETTINGS
# ============================================================

def render_settings():

    st.title(
        "Settings"
    )

    st.checkbox(
        "Dark Mode",
        value=st.session_state.dark_mode,
        key="settings_dark_mode",
    )

    if (
        st.session_state.settings_dark_mode
        != st.session_state.dark_mode
    ):

        st.session_state.dark_mode = (
            st.session_state.settings_dark_mode
        )

        st.rerun()

    st.text_input(
        "Registry Platform Name",
        value="South Sudan National Registry",
        disabled=True,
    )

    st.text_input(
        "Version",
        value="1.0.0",
        disabled=True,
    )


# ============================================================
# DATABASE ATTENTION BANNER
# ============================================================

if not database_ok:

    st.warning(
        "Database Attention Required"
    )

    st.caption(
        "The Registry interface is running without a connected "
        "database. Dashboard values are shown as zero until "
        "the database connection is restored."
    )


# ============================================================
# PAGE ROUTER
# ============================================================

page = st.session_state.active_page


if page == "overview":

    render_overview()

elif page == "population":

    render_population()

elif page == "households":

    render_households()

elif page == "civil_registration":

    render_civil_registration()

elif page == "identity":

    render_identity()

elif page == "elections":

    render_elections()

elif page == "administration_units":

    render_administrative_units()

elif page == "reports":

    render_reports()

elif page == "verification":

    render_verification()

elif page == "documents":

    render_documents()

elif page == "administration":

    render_administration()

elif page == "audit_log":

    render_audit_log()

elif page == "system_status":

    render_system_status()

elif page == "search":

    render_search()

elif page == "import":

    render_import()

elif page == "settings":

    render_settings()

else:

    st.session_state.active_page = "overview"

    render_overview()


# ============================================================
# FOOTER
# ============================================================

st.divider()

footer_left, footer_right = st.columns(2)

with footer_left:

    st.markdown(
        """
        <div class="registry-footer">
            South Sudan National Registry •
            Registry Platform • Version 1.0.0
        </div>
        """,
        unsafe_allow_html=True,
    )

with footer_right:

    st.markdown(
        """
        <div class="registry-footer">
            Registry data should be treated as authoritative
            only after verification and appropriate
            administrative approval.
        </div>
        """,
        unsafe_allow_html=True,
)
