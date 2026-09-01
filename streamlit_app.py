"""
South Sudan National Registry
Streamlit AI Studio

National population, civil registration, identity,
household and electoral registry management platform.

Application entry point:

    streamlit run streamlit_app.py

This frontend is intentionally self-contained and uses the
SQLAlchemy models in models.py directly.

Supported database backends depend on database/database.py.
"""

from __future__ import annotations

import html
import logging
import os
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

import streamlit as st
from sqlalchemy import func, inspect, select
from sqlalchemy.exc import SQLAlchemyError


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
EMBLEM_PATH = ASSETS_DIR / "south_sudan_emblem.png"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

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
# DATABASE IMPORT
# ============================================================

DB_AVAILABLE = True
DB_IMPORT_ERROR: Optional[Exception] = None

try:
    from database.database import (
        Base,
        SessionLocal,
        engine,
        init_db,
    )

except Exception as exc:
    DB_AVAILABLE = False
    DB_IMPORT_ERROR = exc

    Base = None
    SessionLocal = None
    engine = None
    init_db = None


# ============================================================
# MODEL IMPORT
# ============================================================

MODELS_AVAILABLE = True
MODEL_IMPORT_ERROR: Optional[Exception] = None

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

except Exception as exc:
    MODELS_AVAILABLE = False
    MODEL_IMPORT_ERROR = exc

    AdministrativeUnit = None
    AuditLog = None
    Citizen = None
    CivilEvent = None
    Document = None
    Household = None
    VoterRecord = None


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "active_page": "Overview",
    "dark_mode": True,
    "database_ready": False,
    "flash_message": "",
}

for state_key, default_value in DEFAULT_STATE.items():

    if state_key not in st.session_state:
        st.session_state[state_key] = default_value


# ============================================================
# THEME
# ============================================================

def theme() -> dict[str, str]:

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
            "success": "#22C55E",
            "warning": "#F59E0B",
            "danger": "#EF4444",
            "info": "#38BDF8",
        }

    return {
        "background": "#F8FAFC",
        "surface": "#FFFFFF",
        "surface_alt": "#F1F5F9",
        "surface_hover": "#E2E8F0",
        "text": "#0F172A",
        "muted": "#64748B",
        "border": "#CBD5E1",
        "accent": "#15803D",
        "accent_dark": "#166534",
        "accent_soft": "#DCFCE7",
        "success": "#16A34A",
        "warning": "#D97706",
        "danger": "#DC2626",
        "info": "#0284C7",
    }


# ============================================================
# CSS
# ============================================================

def inject_css() -> None:

    t = theme()

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
            background: {t["background"]};
            color: {t["text"]};
        }}

        .block-container {{
            max-width: 1500px;
            padding-top: 1.2rem;
            padding-bottom: 5rem;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: {t["text"]} !important;
        }}

        p, label {{
            color: {t["text"]};
        }}

        /* ----------------------------------------------------
           SIDEBAR
           ---------------------------------------------------- */

        section[data-testid="stSidebar"] {{
            background: {t["surface"]};
            border-right: 1px solid {t["border"]};
        }}

        section[data-testid="stSidebar"] .block-container {{
            padding-top: 1rem;
            padding-bottom: 2rem;
        }}

        .sidebar-brand {{
            padding: 10px 4px 18px;
            border-bottom: 1px solid {t["border"]};
            margin-bottom: 16px;
        }}

        .sidebar-title {{
            font-size: 18px;
            font-weight: 800;
            line-height: 1.3;
            color: {t["text"]};
        }}

        .sidebar-subtitle {{
            font-size: 11px;
            line-height: 1.5;
            margin-top: 6px;
            color: {t["muted"]};
        }}

        .sidebar-section {{
            color: {t["accent"]};
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .08em;
            margin-top: 18px;
            margin-bottom: 7px;
        }}

        /* ----------------------------------------------------
           HEADER
           ---------------------------------------------------- */

        .registry-header {{
            display: flex;
            align-items: center;
            gap: 18px;
            padding: 8px 0 18px;
            margin-bottom: 10px;
        }}

        .header-emblem {{
            width: 72px;
            height: 72px;
            border-radius: 50%;
            object-fit: contain;
            border: 1px solid {t["border"]};
            background: {t["surface"]};
        }}

        .header-emblem-fallback {{
            width: 72px;
            height: 72px;
            min-width: 72px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: {t["accent"]};
            color: white;
            font-size: 22px;
            font-weight: 900;
            border: 3px solid {t["accent_soft"]};
        }}

        .registry-title {{
            font-size: 28px;
            font-weight: 850;
            line-height: 1.2;
            color: {t["text"]};
        }}

        .registry-subtitle {{
            color: {t["muted"]};
            font-size: 13px;
            line-height: 1.5;
            margin-top: 6px;
        }}

        .registry-version {{
            color: {t["muted"]};
            font-size: 11px;
            margin-top: 7px;
        }}

        .status-online {{
            display: inline-flex;
            align-items: center;
            gap: 7px;
            color: {t["success"]};
            font-size: 12px;
            font-weight: 700;
        }}

        .status-warning {{
            display: inline-flex;
            align-items: center;
            gap: 7px;
            color: {t["warning"]};
            font-size: 12px;
            font-weight: 700;
        }}

        .status-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: {t["success"]};
            display: inline-block;
        }}

        .status-dot-warning {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: {t["warning"]};
            display: inline-block;
        }}

        /* ----------------------------------------------------
           OVERVIEW
           ---------------------------------------------------- */

        .overview-card {{
            background: {t["surface"]};
            border: 1px solid {t["border"]};
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
        }}

        .registry-kicker {{
            color: {t["accent"]};
            font-size: 11px;
            font-weight: 850;
            text-transform: uppercase;
            letter-spacing: .09em;
            margin-bottom: 6px;
        }}

        .registry-heading {{
            color: {t["text"]};
            font-size: 23px;
            font-weight: 850;
            line-height: 1.3;
            margin-bottom: 7px;
        }}

        .registry-description {{
            color: {t["muted"]};
            font-size: 14px;
            line-height: 1.65;
            max-width: 1000px;
        }}

        /* ----------------------------------------------------
           KPI
           ---------------------------------------------------- */

        .kpi-card {{
            background: {t["surface"]};
            border: 1px solid {t["border"]};
            border-radius: 15px;
            padding: 18px;
            min-height: 125px;
        }}

        .kpi-label {{
            color: {t["muted"]};
            font-size: 12px;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: .04em;
        }}

        .kpi-value {{
            color: {t["text"]};
            font-size: 30px;
            font-weight: 850;
            margin-top: 7px;
        }}

        .kpi-description {{
            color: {t["muted"]};
            font-size: 12px;
            margin-top: 4px;
        }}

        /* ----------------------------------------------------
           MODULE CARDS
           ---------------------------------------------------- */

        .module-card {{
            background: {t["surface"]};
            border: 1px solid {t["border"]};
            border-radius: 14px;
            padding: 18px;
            min-height: 130px;
        }}

        .module-name {{
            color: {t["text"]};
            font-size: 16px;
            font-weight: 800;
        }}

        .module-description {{
            color: {t["muted"]};
            font-size: 13px;
            line-height: 1.55;
            margin-top: 7px;
        }}

        /* ----------------------------------------------------
           BUTTONS
           ---------------------------------------------------- */

        .stButton > button {{
            border-radius: 9px;
            min-height: 40px;
            font-weight: 650;
        }}

        /* ----------------------------------------------------
           FORMS
           ---------------------------------------------------- */

        div[data-baseweb="select"] > div {{
            border-radius: 9px;
        }}

        input,
        textarea {{
            border-radius: 9px !important;
        }}

        /* ----------------------------------------------------
           TABLES
           ---------------------------------------------------- */

        div[data-testid="stDataFrame"] {{
            border: 1px solid {t["border"]};
            border-radius: 12px;
            overflow: hidden;
        }}

        /* ----------------------------------------------------
           FOOTER
           ---------------------------------------------------- */

        .registry-footer {{
            color: {t["muted"]};
            font-size: 11px;
            line-height: 1.5;
        }}

        #MainMenu {{
            visibility: hidden;
        }}

        footer {{
            visibility: hidden;
        }}

        header[data-testid="stHeader"] {{
            background: transparent;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def safe_text(value: Any) -> str:

    if value is None:
        return ""

    return html.escape(str(value))


def model_available(model: Any) -> bool:

    return model is not None


def database_tables() -> set[str]:

    if engine is None:
        return set()

    try:
        return set(inspect(engine).get_table_names())

    except Exception:
        return set()


def database_is_usable() -> bool:

    if not DB_AVAILABLE:
        return False

    if engine is None:
        return False

    try:
        with engine.connect():
            return True

    except Exception:
        return False


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

@st.cache_resource
def initialize_database() -> tuple[bool, Optional[str]]:

    if not DB_AVAILABLE:

        return (
            False,
            str(DB_IMPORT_ERROR),
        )

    if init_db is None:

        return (
            False,
            "database.database.init_db is unavailable.",
        )

    try:

        init_db()

        return True, None

    except Exception as exc:

        logger.exception(
            "Database initialization failed."
        )

        return (
            False,
            str(exc),
        )


database_ready, database_error = initialize_database()

st.session_state.database_ready = database_ready


# ============================================================
# SESSION / DB HELPERS
# ============================================================

def get_session():

    if SessionLocal is None:
        return None

    return SessionLocal()


def commit_session(session) -> None:

    session.commit()


def rollback_session(session) -> None:

    try:
        session.rollback()
    except Exception:
        pass


def close_session(session) -> None:

    try:
        session.close()
    except Exception:
        pass


# ============================================================
# AUDIT
# ============================================================

def create_audit_log(
    session,
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    details: Optional[str] = None,
) -> None:

    if AuditLog is None:
        return

    try:

        record = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            username="streamlit",
            details=details,
        )

        session.add(record)

    except Exception:

        logger.exception(
            "Unable to create audit log."
        )


# ============================================================
# COUNTS
# ============================================================

def count_records(model: Any) -> int:

    if model is None:
        return 0

    session = get_session()

    if session is None:
        return 0

    try:

        result = session.execute(
            select(func.count()).select_from(model)
        )

        return int(result.scalar() or 0)

    except Exception:

        return 0

    finally:

        close_session(session)


def get_counts() -> dict[str, int]:

    return {
        "population": count_records(Citizen),
        "civil": count_records(CivilEvent),
        "identity": count_records(Document),
        "elections": count_records(VoterRecord),
        "households": count_records(Household),
        "administrative_units": count_records(
            AdministrativeUnit
        ),
    }


# ============================================================
# SAFE IMAGE SUPPORT
# ============================================================

def valid_emblem() -> bool:

    if not EMBLEM_PATH.exists():
        return False

    if EMBLEM_PATH.stat().st_size < 100:
        return False

    try:

        from PIL import Image

        with Image.open(EMBLEM_PATH) as image:

            image.verify()

        return True

    except Exception:

        logger.warning(
            "Invalid or unreadable emblem: %s",
            EMBLEM_PATH,
        )

        return False


# ============================================================
# HEADER
# ============================================================

def render_header() -> None:

    if valid_emblem():

        st.markdown(
            f"""
            <div class="registry-header">

                <img
                    class="header-emblem"
                    src="data:image/png;base64,"
                />

                <div>

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

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        # Streamlit handles the actual image safely.
        # This is deliberately separate from the HTML header.
        col1, col2, col3 = st.columns([1, 4, 1])

        with col1:
            st.image(
                str(EMBLEM_PATH),
                width=68,
            )

    else:

        st.markdown(
            """
            <div class="registry-header">

                <div class="header-emblem-fallback">
                    SS
                </div>

                <div>

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

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# SIDEBAR
# ============================================================

NAVIGATION = {
    "Registry": [
        "Overview",
        "Population Registry",
        "Households",
        "Civil Registration",
        "Identity Management",
        "Elections",
        "Administrative Units",
    ],
    "Operations": [
        "Documents",
        "Verification",
    ],
    "Administration": [
        "Reports & Analytics",
        "Audit Log",
        "Administration",
    ],
}


def sidebar_navigation() -> None:

    with st.sidebar:

        st.markdown(
            """
            <div class="sidebar-brand">

                <div class="sidebar-title">
                    South Sudan National Registry
                </div>

                <div class="sidebar-subtitle">
                    National Population • Civil Registration •
                    Identity • Elections
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if database_ready:

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
                    Database Attention Required
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

        for section, pages in NAVIGATION.items():

            st.markdown(
                f"""
                <div class="sidebar-section">
                    {safe_text(section)}
                </div>
                """,
                unsafe_allow_html=True,
            )

            for page in pages:

                if st.button(
                    page,
                    key=f"sidebar_nav_{page.lower().replace(' ', '_').replace('&', 'and')}",
                    use_container_width=True,
                ):

                    st.session_state.active_page = page
                    st.rerun()

        st.divider()

        theme_label = (
            "Use Light Theme"
            if st.session_state.dark_mode
            else "Use Dark Theme"
        )

        if st.button(
            theme_label,
            key="sidebar_theme",
            use_container_width=True,
        ):

            st.session_state.dark_mode = (
                not st.session_state.dark_mode
            )

            st.rerun()

        if st.button(
            "Refresh",
            key="sidebar_refresh",
            use_container_width=True,
        ):

            st.rerun()


sidebar_navigation()


# ============================================================
# HEADER
# ============================================================

render_header()


# ============================================================
# DATABASE STATUS
# ============================================================

if not database_ready:

    with st.expander(
        "Database technical details"
    ):

        if database_error:
            st.code(database_error)

        if DB_IMPORT_ERROR:
            st.exception(DB_IMPORT_ERROR)

        if MODEL_IMPORT_ERROR:
            st.exception(MODEL_IMPORT_ERROR)


# ============================================================
# KPI CARD
# ============================================================

def render_kpi_card(
    label: str,
    value: Any,
    description: str,
) -> None:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-label">
                {safe_text(label)}
            </div>

            <div class="kpi-value">
                {safe_text(value)}
            </div>

            <div class="kpi-description">
                {safe_text(description)}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MODULE CARD
# ============================================================

def render_module_card(
    name: str,
    description: str,
) -> None:

    st.markdown(
        f"""
        <div class="module-card">

            <div class="module-name">
                {safe_text(name)}
            </div>

            <div class="module-description">
                {safe_text(description)}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:

    counts = get_counts()

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

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_kpi_card(
            "Registered Population",
            counts["population"],
            "Population records",
        )

    with c2:
        render_kpi_card(
            "Civil Records",
            counts["civil"],
            "Birth, death and civil events",
        )

    with c3:
        render_kpi_card(
            "Identity Records",
            counts["identity"],
            "National identity records",
        )

    with c4:
        render_kpi_card(
            "Election Records",
            counts["elections"],
            "Electoral records",
        )

    st.divider()

    st.subheader("Registry Services")

    services = [
        (
            "Population Registry",
            "Manage national population records, households, persons and demographic information.",
        ),
        (
            "Elections",
            "Manage electoral registration, voter records and election administration.",
        ),
        (
            "Civil Registration",
            "Register births, deaths, marriages, certificates and other civil events.",
        ),
        (
            "Identity Management",
            "Manage national identity registration, identification records and identity services.",
        ),
        (
            "Households",
            "Manage households, household members, household locations and household heads.",
        ),
        (
            "Reports & Analytics",
            "Generate operational reports, statistical summaries and Registry analytics.",
        ),
        (
            "Administration",
            "Manage users, roles, permissions, configuration and system administration.",
        ),
    ]

    service_columns = st.columns(2)

    for index, (name, description) in enumerate(services):

        with service_columns[index % 2]:

            render_module_card(
                name,
                description,
            )

            if st.button(
                f"Open {name}",
                key=f"overview_open_{index}",
                use_container_width=True,
            ):

                st.session_state.active_page = name
                st.rerun()

    st.divider()

    st.subheader("System Status")

    if database_ready:

        st.success(
            "Registry database connected and available."
        )

    else:

        st.warning(
            "Registry interface is available, but the database is not currently connected."
        )


# ============================================================
# GENERIC DATAFRAME HELPER
# ============================================================

def rows_to_dicts(
    rows: list[Any],
    columns: list[str],
) -> list[dict[str, Any]]:

    output = []

    for row in rows:

        item = {}

        for column in columns:

            value = getattr(
                row,
                column,
                None,
            )

            if isinstance(value, (date, datetime)):

                value = value.isoformat()

            item[column] = value

        output.append(item)

    return output


# ============================================================
# POPULATION REGISTRY
# ============================================================

def render_population() -> None:

    st.title("Population Registry")

    st.caption(
        "Register, search, edit and manage national population records."
    )

    if Citizen is None:

        st.error(
            "Citizen model is unavailable."
        )

        return

    tab_list, tab_add, tab_edit = st.tabs(
        [
            "Records",
            "Register Citizen",
            "Edit Citizen",
        ]
    )

    with tab_list:

        search = st.text_input(
            "Search citizens",
            placeholder="Name, National ID, phone, county or community",
            key="citizen_search",
        )

        session = get_session()

        if session is None:

            st.error("Database session unavailable.")
            return

        try:

            stmt = select(Citizen).order_by(
                Citizen.created_at.desc()
            )

            if search.strip():

                term = f"%{search.strip()}%"

                stmt = stmt.where(
                    Citizen.full_name.ilike(term)
                    | Citizen.national_id.ilike(term)
                    | Citizen.phone_number.ilike(term)
                    | Citizen.county_or_payam.ilike(term)
                    | Citizen.community.ilike(term)
                )

            rows = session.execute(stmt).scalars().all()

            data = rows_to_dicts(
                rows,
                [
                    "id",
                    "national_id",
                    "full_name",
                    "date_of_birth",
                    "gender",
                    "nationality",
                    "state_or_region",
                    "county_or_payam",
                    "verification_status",
                ],
            )

            if data:
                st.dataframe(
                    data,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No citizen records found.")

        except Exception as exc:

            st.error(
                "Unable to load citizen records."
            )

            with st.expander("Technical details"):
                st.exception(exc)

        finally:
            close_session(session)

    with tab_add:

        render_citizen_form()

    with tab_edit:

        render_citizen_editor()


# ============================================================
# CITIZEN FORM
# ============================================================

def render_citizen_form(
    citizen: Optional[Any] = None,
) -> None:

    editing = citizen is not None

    st.subheader(
        "Edit Citizen" if editing else "Register Citizen"
    )

    with st.form(
        key=(
            "citizen_edit_form"
            if editing
            else "citizen_create_form"
        )
    ):

        c1, c2 = st.columns(2)

        with c1:

            full_name = st.text_input(
                "Full name *",
                value=getattr(
                    citizen,
                    "full_name",
                    "",
                ),
            )

            national_id = st.text_input(
                "National ID",
                value=getattr(
                    citizen,
                    "national_id",
                    "",
                )
                or "",
            )

            passport_number = st.text_input(
                "Passport number",
                value=getattr(
                    citizen,
                    "passport_number",
                    "",
                )
                or "",
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
                    ].index(
                        getattr(
                            citizen,
                            "gender",
                            "Other",
                        )
                    )
                    if getattr(
                        citizen,
                        "gender",
                        "Other",
                    )
                    in [
                        "Male",
                        "Female",
                        "Other",
                    ]
                    else 2
                ),
            )

            nationality = st.text_input(
                "Nationality",
                value=getattr(
                    citizen,
                    "nationality",
                    "South Sudanese",
                )
                or "South Sudanese",
            )

        with c2:

            dob = st.date_input(
                "Date of birth",
                value=getattr(
                    citizen,
                    "date_of_birth",
                    date.today(),
                )
                or date.today(),
            )

            marital_status = st.selectbox(
                "Marital status",
                [
                    "Single",
                    "Married",
                    "Divorced",
                    "Widowed",
                    "Other",
                ],
                index=(
                    [
                        "Single",
                        "Married",
                        "Divorced",
                        "Widowed",
                        "Other",
                    ].index(
                        getattr(
                            citizen,
                            "marital_status",
                            "Single",
                        )
                    )
                    if getattr(
                        citizen,
                        "marital_status",
                        "Single",
                    )
                    in [
                        "Single",
                        "Married",
                        "Divorced",
                        "Widowed",
                        "Other",
                    ]
                    else 0
                ),
            )

            phone = st.text_input(
                "Phone number",
                value=getattr(
                    citizen,
                    "phone_number",
                    "",
                )
                or "",
            )

            email = st.text_input(
                "Email address",
                value=getattr(
                    citizen,
                    "email_address",
                    "",
                )
                or "",
            )

            tribe = st.text_input(
                "Tribe",
                value=getattr(
                    citizen,
                    "tribe",
                    "",
                )
                or "",
            )

        st.subheader("Location")

        l1, l2, l3 = st.columns(3)

        with l1:

            state = st.text_input(
                "State / Region",
                value=getattr(
                    citizen,
                    "state_or_region",
                    "",
                )
                or "",
            )

        with l2:

            county = st.text_input(
                "County / Payam",
                value=getattr(
                    citizen,
                    "county_or_payam",
                    "",
                )
                or "",
            )

        with l3:

            boma = st.text_input(
                "Boma",
                value=getattr(
                    citizen,
                    "boma",
                    "",
                )
                or "",
            )

        community = st.text_input(
            "Community",
            value=getattr(
                citizen,
                "community",
                "",
            )
            or "",
        )

        address = st.text_area(
            "Residential address",
            value=getattr(
                citizen,
                "residential_address",
                "",
            )
            or "",
        )

        st.subheader("Verification")

        verification_options = [
            "Pending Review",
            "Verified",
            "Rejected",
        ]

        current_status = getattr(
            citizen,
            "verification_status",
            "Pending Review",
        )

        verification_status = st.selectbox(
            "Verification status",
            verification_options,
            index=(
                verification_options.index(
                    current_status
                )
                if current_status
                in verification_options
                else 0
            ),
        )

        notes = st.text_area(
            "Notes",
            value=getattr(
                citizen,
                "notes",
                "",
            )
            or "",
        )

        submitted = st.form_submit_button(
            "Update Citizen"
            if editing
            else "Register Citizen",
            use_container_width=True,
        )

    if not submitted:
        return

    if not full_name.strip():

        st.error(
            "Full name is required."
        )

        return

    session = get_session()

    if session is None:

        st.error(
            "Database session unavailable."
        )

        return

    try:

        if editing:

            record = session.get(
                Citizen,
                citizen.id,
            )

            if record is None:

                st.error(
                    "Citizen record no longer exists."
                )

                return

        else:

            record = Citizen(
                id=uuid.uuid4().hex,
            )

            session.add(record)

        record.full_name = full_name.strip()
        record.national_id = (
            national_id.strip() or None
        )
        record.passport_number = (
            passport_number.strip() or None
        )
        record.gender = gender
        record.nationality = nationality.strip()
        record.date_of_birth = dob

        if dob:

            today = date.today()

            age = (
                today.year
                - dob.year
                - (
                    (
                        today.month,
                        today.day,
                    )
                    < (
                        dob.month,
                        dob.day,
                    )
                )
            )

            record.age = max(age, 0)

        record.marital_status = marital_status
        record.phone_number = (
            phone.strip() or None
        )
        record.email_address = (
            email.strip() or None
        )
        record.tribe = tribe.strip()
        record.state_or_region = state.strip()
        record.county_or_payam = county.strip()
        record.boma = boma.strip() or None
        record.community = community.strip()
        record.residential_address = (
            address.strip() or None
        )
        record.verification_status = (
            verification_status
        )
        record.notes = notes.strip() or None

        create_audit_log(
            session,
            "UPDATE" if editing else "CREATE",
            "Citizen",
            record.id,
            "Citizen record maintained through Streamlit.",
        )

        commit_session(session)

        st.success(
            "Citizen record updated successfully."
            if editing
            else "Citizen registered successfully."
        )

        st.rerun()

    except SQLAlchemyError as exc:

        rollback_session(session)

        st.error(
            "The citizen record could not be saved."
        )

        with st.expander("Technical details"):
            st.exception(exc)

    except Exception as exc:

        rollback_session(session)

        st.error(
            "An unexpected error occurred."
        )

        with st.expander("Technical details"):
            st.exception(exc)

    finally:

        close_session(session)


# ============================================================
# CITIZEN EDITOR
# ============================================================

def render_citizen_editor() -> None:

    session = get_session()

    if session is None:

        st.error(
            "Database session unavailable."
        )

        return

    try:

        citizens = session.execute(
            select(Citizen)
            .order_by(Citizen.full_name)
        ).scalars().all()

        if not citizens:

            st.info(
                "There are no citizen records to edit."
            )

            return

        options = {
            f"{c.full_name} — {c.national_id or c.id}": c.id
            for c in citizens
        }

    finally:

        close_session(session)

    selected = st.selectbox(
        "Select citizen",
        list(options.keys()),
        key="citizen_editor_select",
    )

    selected_id = options[selected]

    session = get_session()

    if session is None:

        st.error(
            "Database session unavailable."
        )

        return

    try:

        citizen = session.get(
            Citizen,
            selected_id,
        )

        if citizen:

            # Detach the object before closing.
            session.expunge(citizen)

            render_citizen_form(
                citizen
            )

    finally:

        close_session(session)


# ============================================================
# HOUSEHOLDS
# ============================================================

def render_households() -> None:

    st.title("Households")

    st.caption(
        "Manage registered households and household locations."
    )

    if Household is None:

        st.error(
            "Household model is unavailable."
        )

        return

    tab1, tab2 = st.tabs(
        [
            "Households",
            "Add Household",
        ]
    )

    with tab1:

        session = get_session()

        if session is None:
            st.error("Database session unavailable.")
            return

        try:

            households = session.execute(
                select(Household)
                .order_by(
                    Household.household_number
                )
            ).scalars().all()

            data = rows_to_dicts(
                households,
                [
                    "id",
                    "household_number",
                    "state_or_region",
                    "county_or_payam",
                    "boma",
                    "community",
                    "head_citizen_id",
                ],
            )

            if data:
                st.dataframe(
                    data,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info(
                    "No households registered."
                )

        except Exception as exc:

            st.error(
                "Unable to load households."
            )

            with st.expander("Technical details"):
                st.exception(exc)

        finally:

            close_session(session)

    with tab2:

        with st.form("household_form"):

            number = st.text_input(
                "Household number *"
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
                "Residential address"
            )

            submitted = st.form_submit_button(
                "Register Household",
                use_container_width=True,
            )

        if submitted:

            if not number.strip():

                st.error(
                    "Household number is required."
                )

                return

            session = get_session()

            if session is None:
                st.error(
                    "Database session unavailable."
                )
                return

            try:

                household = Household(
                    id=uuid.uuid4().hex,
                    household_number=number.strip(),
                    state_or_region=state.strip(),
                    county_or_payam=county.strip() or None,
                    boma=boma.strip() or None,
                    community=community.strip() or None,
                    residential_address=address.strip() or None,
                )

                session.add(household)

                create_audit_log(
                    session,
                    "CREATE",
                    "Household",
                    household.id,
                )

                commit_session(session)

                st.success(
                    "Household registered successfully."
                )

                st.rerun()

            except Exception as exc:

                rollback_session(session)

                st.error(
                    "Unable to register household."
                )

                with st.expander("Technical details"):
                    st.exception(exc)

            finally:

                close_session(session)


# ============================================================
# CIVIL REGISTRATION
# ============================================================

def render_civil_registration() -> None:

    st.title("Civil Registration")

    st.caption(
        "Birth, death, marriage, divorce and other civil events."
    )

    if CivilEvent is None:

        st.error(
            "Civil Event model is unavailable."
        )

        return

    tab1, tab2 = st.tabs(
        [
            "Civil Events",
            "Register Event",
        ]
    )

    with tab1:

        session = get_session()

        if session is None:

            st.error(
                "Database session unavailable."
            )

            return

        try:

            events = session.execute(
                select(CivilEvent)
                .order_by(
                    CivilEvent.event_date.desc()
                )
            ).scalars().all()

            data = rows_to_dicts(
                events,
                [
                    "id",
                    "reference_number",
                    "event_type",
                    "citizen_id",
                    "event_date",
                    "registration_centre",
                    "document_number",
                    "status",
                ],
            )

            if data:

                st.dataframe(
                    data,
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.info(
                    "No civil registration events found."
                )

        except Exception as exc:

            st.error(
                "Unable to load civil events."
            )

            with st.expander("Technical details"):
                st.exception(exc)

        finally:

            close_session(session)

    with tab2:

        with st.form("civil_event_form"):

            reference = st.text_input(
                "Reference number *",
                value=f"CIV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            )

            event_type = st.selectbox(
                "Event type",
                [
                    "Birth",
                    "Death",
                    "Marriage",
                    "Divorce",
                    "Other",
                ],
            )

            event_date = st.date_input(
                "Event date",
                value=date.today(),
            )

            registration_centre = st.text_input(
                "Registration centre"
            )

            document_number = st.text_input(
                "Document number"
            )

            status = st.selectbox(
                "Status",
                [
                    "Pending Review",
                    "Registered",
                    "Verified",
                    "Rejected",
                ],
            )

            notes = st.text_area(
                "Notes"
            )

            submitted = st.form_submit_button(
                "Register Civil Event",
                use_container_width=True,
            )

        if submitted:

            session = get_session()

            if session is None:

                st.error(
                    "Database session unavailable."
                )

                return

            try:

                event = CivilEvent(
                    id=uuid.uuid4().hex,
                    reference_number=reference.strip(),
                    event_type=event_type,
                    event_date=event_date,
                    registration_centre=(
                        registration_centre.strip()
                        or None
                    ),
                    document_number=(
                        document_number.strip()
                        or None
                    ),
                    status=status,
                    notes=notes.strip() or None,
                )

                session.add(event)

                create_audit_log(
                    session,
                    "CREATE",
                    "CivilEvent",
                    event.id,
                )

                commit_session(session)

                st.success(
                    "Civil event registered successfully."
                )

                st.rerun()

            except Exception as exc:

                rollback_session(session)

                st.error(
                    "Unable to register civil event."
                )

                with st.expander("Technical details"):
                    st.exception(exc)

            finally:

                close_session(session)


# ============================================================
# IDENTITY MANAGEMENT
# ============================================================

def render_identity() -> None:

    st.title("Identity Management")

    st.caption(
        "Manage national identity documents and identity records."
    )

    if Document is None:

        st.error(
            "Document model is unavailable."
        )

        return

    tab1, tab2 = st.tabs(
        [
            "Identity Records",
            "Register Document",
        ]
    )

    with tab1:

        session = get_session()

        if session is None:

            st.error(
                "Database session unavailable."
            )

            return

        try:

            documents = session.execute(
                select(Document)
                .order_by(
                    Document.created_at.desc()
                )
            ).scalars().all()

            data = rows_to_dicts(
                documents,
                [
                    "id",
                    "document_number",
                    "document_type",
                    "citizen_id",
                    "status",
                    "issued_date",
                    "expiry_date",
                ],
            )

            if data:

                st.dataframe(
                    data,
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.info(
                    "No identity documents registered."
                )

        except Exception as exc:

            st.error(
                "Unable to load identity records."
            )

            with st.expander("Technical details"):
                st.exception(exc)

        finally:

            close_session(session)

    with tab2:

        with st.form("identity_form"):

            document_type = st.selectbox(
                "Document type",
                [
                    "National Identity Card",
                    "Passport",
                    "Birth Certificate",
                    "Residence Document",
                    "Other",
                ],
            )

            document_number = st.text_input(
                "Document number"
            )

            citizen_id = st.text_input(
                "Citizen ID"
            )

            issued_date = st.date_input(
                "Issued date",
                value=date.today(),
            )

            has_expiry = st.checkbox(
                "Has expiry date"
            )

            expiry_date = (
                st.date_input(
                    "Expiry date",
                    value=date.today(),
                )
                if has_expiry
                else None
            )

            status = st.selectbox(
                "Status",
                [
                    "Registered",
                    "Active",
                    "Expired",
                    "Cancelled",
                    "Pending Review",
                ],
            )

            submitted = st.form_submit_button(
                "Register Identity Document",
                use_container_width=True,
            )

        if submitted:

            session = get_session()

            if session is None:

                st.error(
                    "Database session unavailable."
                )

                return

            try:

                document = Document(
                    id=uuid.uuid4().hex,
                    document_number=(
                        document_number.strip()
                        or None
                    ),
                    document_type=document_type,
                    citizen_id=(
                        citizen_id.strip()
                        or None
                    ),
                    issued_date=issued_date,
                    expiry_date=expiry_date,
                    status=status,
                )

                session.add(document)

                create_audit_log(
                    session,
                    "CREATE",
                    "Document",
                    document.id,
                )

                commit_session(session)

                st.success(
                    "Identity document registered successfully."
                )

                st.rerun()

            except Exception as exc:

                rollback_session(session)

                st.error(
                    "Unable to register identity document."
                )

                with st.expander("Technical details"):
                    st.exception(exc)

            finally:

                close_session(session)


# ============================================================
# ELECTIONS
# ============================================================

def render_elections() -> None:

    st.title("Elections")

    st.caption(
        "Manage voter registration and electoral records."
    )

    if VoterRecord is None:

        st.error(
            "Voter Record model is unavailable."
        )

        return

    tab1, tab2 = st.tabs(
        [
            "Voter Records",
            "Register Voter",
        ]
    )

    with tab1:

        session = get_session()

        if session is None:

            st.error(
                "Database session unavailable."
            )

            return

        try:

            voters = session.execute(
                select(VoterRecord)
                .order_by(
                    VoterRecord.created_at.desc()
                )
            ).scalars().all()

            data = rows_to_dicts(
                voters,
                [
                    "id",
                    "citizen_id",
                    "voter_id_number",
                    "voter_status",
                    "constituency",
                    "polling_station_id",
                    "polling_station_name",
                    "has_voted",
                ],
            )

            if data:

                st.dataframe(
                    data,
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.info(
                    "No voter records found."
                )

        except Exception as exc:

            st.error(
                "Unable to load voter records."
            )

            with st.expander("Technical details"):
                st.exception(exc)

        finally:

            close_session(session)

    with tab2:

        with st.form("voter_form"):

            citizen_id = st.text_input(
                "Citizen ID *"
            )

            voter_id = st.text_input(
                "Voter ID number"
            )

            status = st.selectbox(
                "Voter status",
                [
                    "Active",
                    "Inactive",
                    "Suspended",
                    "Pending Review",
                ],
            )

            constituency = st.text_input(
                "Constituency"
            )

            polling_id = st.text_input(
                "Polling station ID"
            )

            polling_name = st.text_input(
                "Polling station name"
            )

            submitted = st.form_submit_button(
                "Register Voter",
                use_container_width=True,
            )

        if submitted:

            if not citizen_id.strip():

                st.error(
                    "Citizen ID is required."
                )

                return

            session = get_session()

            if session is None:

                st.error(
                    "Database session unavailable."
                )

                return

            try:

                voter = VoterRecord(
                    id=uuid.uuid4().hex,
                    citizen_id=citizen_id.strip(),
                    voter_id_number=(
                        voter_id.strip()
                        or None
                    ),
                    voter_status=status,
                    constituency=(
                        constituency.strip()
                        or None
                    ),
                    polling_station_id=(
                        polling_id.strip()
                        or None
                    ),
                    polling_station_name=(
                        polling_name.strip()
                        or None
                    ),
                )

                session.add(voter)

                create_audit_log(
                    session,
                    "CREATE",
                    "VoterRecord",
                    voter.id,
                )

                commit_session(session)

                st.success(
                    "Voter record registered successfully."
                )

                st.rerun()

            except Exception as exc:

                rollback_session(session)

                st.error(
                    "Unable to register voter."
                )

                with st.expander("Technical details"):
                    st.exception(exc)

            finally:

                close_session(session)


# ============================================================
# ADMINISTRATIVE UNITS
# ============================================================

def render_administrative_units() -> None:

    st.title("Administrative Units")

    st.caption(
        "Manage the administrative hierarchy of South Sudan."
    )

    if AdministrativeUnit is None:

        st.error(
            "Administrative Unit model is unavailable."
        )

        return

    tab1, tab2 = st.tabs(
        [
            "Units",
            "Add Unit",
        ]
    )

    with tab1:

        session = get_session()

        if session is None:

            st.error(
                "Database session unavailable."
            )

            return

        try:

            units = session.execute(
                select(AdministrativeUnit)
                .order_by(
                    AdministrativeUnit.name
                )
            ).scalars().all()

            data = rows_to_dicts(
                units,
                [
                    "id",
                    "unit_type",
                    "name",
                    "code",
                    "parent_id",
                    "state_or_region",
                    "administrator_name",
                    "headquarters",
                ],
            )

            if data:

                st.dataframe(
                    data,
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.info(
                    "No administrative units found."
                )

        except Exception as exc:

            st.error(
                "Unable to load administrative units."
            )

            with st.expander("Technical details"):
                st.exception(exc)

        finally:

            close_session(session)

    with tab2:

        with st.form("administrative_unit_form"):

            unit_type = st.selectbox(
                "Unit type",
                [
                    "Country",
                    "State",
                    "County",
                    "Payam",
                    "Boma",
                    "Other",
                ],
            )

            name = st.text_input(
                "Name *"
            )

            code = st.text_input(
                "Code *"
            )

            state = st.text_input(
                "State / Region"
            )

            administrator = st.text_input(
                "Administrator"
            )

            headquarters = st.text_input(
                "Headquarters"
            )

            target_population = st.number_input(
                "Target population",
                min_value=0,
                value=0,
                step=1,
            )

            notes = st.text_area(
                "Notes"
            )

            submitted = st.form_submit_button(
                "Add Administrative Unit",
                use_container_width=True,
            )

        if submitted:

            if not name.strip() or not code.strip():

                st.error(
                    "Name and code are required."
                )

                return

            session = get_session()

            if session is None:

                st.error(
                    "Database session unavailable."
                )

                return

            try:

                unit = AdministrativeUnit(
                    id=uuid.uuid4().hex,
                    unit_type=unit_type,
                    name=name.strip(),
                    code=code.strip(),
                    state_or_region=state.strip(),
                    administrator_name=(
                        administrator.strip()
                        or None
                    ),
                    headquarters=(
                        headquarters.strip()
                        or None
                    ),
                    target_population=(
                        int(target_population)
                        if target_population
                        else None
                    ),
                    notes=notes.strip() or None,
                )

                session.add(unit)

                create_audit_log(
                    session,
                    "CREATE",
                    "AdministrativeUnit",
                    unit.id,
                )

                commit_session(session)

                st.success(
                    "Administrative unit added successfully."
                )

                st.rerun()

            except Exception as exc:

                rollback_session(session)

                st.error(
                    "Unable to add administrative unit."
                )

                with st.expander("Technical details"):
                    st.exception(exc)

            finally:

                close_session(session)


# ============================================================
# DOCUMENTS
# ============================================================

def render_documents() -> None:

    st.title("Documents")

    st.caption(
        "Search registered identity and civil documents."
    )

    if Document is None:

        st.error(
            "Document model is unavailable."
        )

        return

    session = get_session()

    if session is None:

        st.error(
            "Database session unavailable."
        )

        return

    try:

        documents = session.execute(
            select(Document)
            .order_by(
                Document.created_at.desc()
            )
        ).scalars().all()

        data = rows_to_dicts(
            documents,
            [
                "id",
                "document_number",
                "document_type",
                "citizen_id",
                "status",
                "issued_date",
                "expiry_date",
                "created_at",
            ],
        )

        if data:

            st.dataframe(
                data,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "No documents registered."
            )

    except Exception as exc:

        st.error(
            "Unable to load documents."
        )

        with st.expander("Technical details"):
            st.exception(exc)

    finally:

        close_session(session)


# ============================================================
# VERIFICATION
# ============================================================

def render_verification() -> None:

    st.title("Verification")

    st.caption(
        "Review population records awaiting verification."
    )

    if Citizen is None:

        st.error(
            "Citizen model is unavailable."
        )

        return

    session = get_session()

    if session is None:

        st.error(
            "Database session unavailable."
        )

        return

    try:

        records = session.execute(
            select(Citizen)
            .where(
                Citizen.verification_status
                == "Pending Review"
            )
            .order_by(
                Citizen.created_at.desc()
            )
        ).scalars().all()

        if not records:

            st.success(
                "There are no citizen records awaiting verification."
            )

            return

        for citizen in records:

            with st.expander(
                f"{citizen.full_name} — {citizen.national_id or citizen.id}"
            ):

                st.write(
                    f"**Date of birth:** {citizen.date_of_birth or 'Not provided'}"
                )

                st.write(
                    f"**Location:** {citizen.state_or_region}, {citizen.county_or_payam}"
                )

                decision = st.radio(
                    "Verification decision",
                    [
                        "Pending Review",
                        "Verified",
                        "Rejected",
                    ],
                    key=f"verification_{citizen.id}",
                    horizontal=True,
                )

                notes = st.text_area(
                    "Verification notes",
                    value=citizen.verification_notes
                    or "",
                    key=f"verification_notes_{citizen.id}",
                )

                if st.button(
                    "Save Verification Decision",
                    key=f"verify_save_{citizen.id}",
                    use_container_width=True,
                ):

                    try:

                        citizen.verification_status = decision
                        citizen.verification_notes = (
                            notes.strip() or None
                        )

                        if decision == "Verified":

                            citizen.verified_at = datetime.utcnow()
                            citizen.verified_by = "streamlit"

                        create_audit_log(
                            session,
                            "VERIFY",
                            "Citizen",
                            citizen.id,
                            f"Verification status: {decision}",
                        )

                        commit_session(session)

                        st.success(
                            "Verification decision saved."
                        )

                        st.rerun()

                    except Exception as exc:

                        rollback_session(session)

                        st.error(
                            "Unable to save verification."
                        )

                        with st.expander(
                            "Technical details"
                        ):
                            st.exception(exc)

    except Exception as exc:

        st.error(
            "Unable to load verification queue."
        )

        with st.expander("Technical details"):
            st.exception(exc)

    finally:

        close_session(session)


# ============================================================
# REPORTS
# ============================================================

def render_reports() -> None:

    st.title("Reports & Analytics")

    st.caption(
        "Registry operational statistics and summary information."
    )

    counts = get_counts()

    r1, r2 = st.columns(2)

    with r1:

        st.subheader(
            "Registry Summary"
        )

        st.dataframe(
            [
                {
                    "Category": "Registered Population",
                    "Records": counts["population"],
                },
                {
                    "Category": "Civil Records",
                    "Records": counts["civil"],
                },
                {
                    "Category": "Identity Records",
                    "Records": counts["identity"],
                },
                {
                    "Category": "Election Records",
                    "Records": counts["elections"],
                },
                {
                    "Category": "Households",
                    "Records": counts["households"],
                },
                {
                    "Category": "Administrative Units",
                    "Records": counts["administrative_units"],
                },
            ],
            use_container_width=True,
            hide_index=True,
        )

    with r2:

        st.subheader(
            "Database Status"
        )

        if database_ready:

            st.success(
                "Database Connected"
            )

            tables = database_tables()

            st.metric(
                "Database Tables",
                len(tables),
            )

        else:

            st.warning(
                "Database Attention Required"
            )

            st.write(
                "The Registry interface is available without a connected database."
            )


# ============================================================
# AUDIT LOG
# ============================================================

def render_audit_log() -> None:

    st.title("Audit Log")

    st.caption(
        "Registry application activity."
    )

    if AuditLog is None:

        st.error(
            "Audit Log model is unavailable."
        )

        return

    session = get_session()

    if session is None:

        st.error(
            "Database session unavailable."
        )

        return

    try:

        logs = session.execute(
            select(AuditLog)
            .order_by(
                AuditLog.created_at.desc()
            )
            .limit(500)
        ).scalars().all()

        data = rows_to_dicts(
            logs,
            [
                "id",
                "action",
                "entity_type",
                "entity_id",
                "username",
                "created_at",
                "details",
            ],
        )

        if data:

            st.dataframe(
                data,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "No audit events recorded."
            )

    except Exception as exc:

        st.error(
            "Unable to load audit log."
        )

        with st.expander("Technical details"):
            st.exception(exc)

    finally:

        close_session(session)


# ============================================================
# ADMINISTRATION
# ============================================================

def render_administration() -> None:

    st.title("Administration")

    st.caption(
        "Registry configuration and system administration."
    )

    st.subheader(
        "System Information"
    )

    info = [
        {
            "Setting": "Application",
            "Value": "South Sudan National Registry",
        },
        {
            "Setting": "Platform",
            "Value": "Streamlit AI Studio",
        },
        {
            "Setting": "Version",
            "Value": "1.0.0",
        },
        {
            "Setting": "Database",
            "Value": (
                "Connected"
                if database_ready
                else "Attention Required"
            ),
        },
        {
            "Setting": "Emblem",
            "Value": (
                "Available"
                if valid_emblem()
                else "Fallback SS"
            ),
        },
    ]

    st.dataframe(
        info,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader(
        "Maintenance"
    )

    if st.button(
        "Reinitialize Database",
        key="admin_reinitialize_database",
    ):

        try:

            if init_db is None:

                st.error(
                    "Database initializer unavailable."
                )

            else:

                init_db()

                st.success(
                    "Database initialization completed."
                )

                st.rerun()

        except Exception as exc:

            st.error(
                "Database initialization failed."
            )

            with st.expander(
                "Technical details"
            ):
                st.exception(exc)


# ============================================================
# PAGE ROUTER
# ============================================================

PAGE_RENDERERS = {
    "Overview": render_overview,
    "Population Registry": render_population,
    "Households": render_households,
    "Civil Registration": render_civil_registration,
    "Identity Management": render_identity,
    "Elections": render_elections,
    "Administrative Units": render_administrative_units,
    "Documents": render_documents,
    "Verification": render_verification,
    "Reports & Analytics": render_reports,
    "Audit Log": render_audit_log,
    "Administration": render_administration,
}


# ============================================================
# ACTIVE PAGE
# ============================================================

active_page = st.session_state.active_page

if active_page not in PAGE_RENDERERS:

    active_page = "Overview"

    st.session_state.active_page = active_page


try:

    PAGE_RENDERERS[active_page]()

except Exception as exc:

    logger.exception(
        "Unhandled page error: %s",
        active_page,
    )

    st.error(
        "The selected Registry page encountered an error."
    )

    with st.expander(
        "Technical details"
    ):

        st.exception(exc)


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
