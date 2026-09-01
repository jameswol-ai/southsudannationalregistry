"""
South Sudan National Registry
Streamlit AI Studio

National population, civil registration, identity,
household and electoral registry management platform.

Application entry point:

    streamlit run streamlit_app.py

This frontend is intentionally defensive:
- A missing/corrupt emblem cannot crash the application.
- Database failures are reported without crashing the UI.
- Registry modules are handled independently.
- CRUD forms use unique Streamlit widget keys.
"""

from __future__ import annotations

import logging
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

import streamlit as st
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError


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
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
EMBLEM_PATH = ASSETS_DIR / "south_sudan_emblem.png"


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

DATABASE_AVAILABLE = True
DATABASE_IMPORT_ERROR: Optional[Exception] = None

try:
    from database.database import (
        SessionLocal,
        init_db,
    )

except Exception as exc:
    DATABASE_AVAILABLE = False
    DATABASE_IMPORT_ERROR = exc

    SessionLocal = None
    init_db = None

    logger.exception(
        "Unable to import database layer."
    )


# ============================================================
# MODEL IMPORTS
# ============================================================

MODELS_AVAILABLE = True
MODELS_IMPORT_ERROR: Optional[Exception] = None

try:
    from models.models import (
        AdministrativeUnit,
        AuditLog,
        Citizen,
        CivilEvent,
        Document,
        Household,
        VoterRecord,
    )

except Exception:

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
        MODELS_IMPORT_ERROR = exc

        AdministrativeUnit = None
        AuditLog = None
        Citizen = None
        CivilEvent = None
        Document = None
        Household = None
        VoterRecord = None

        logger.exception(
            "Unable to import registry models."
        )


# ============================================================
# MODULE REGISTRY IMPORT
# ============================================================

MODULE_REGISTRY_AVAILABLE = True
MODULE_REGISTRY_ERROR: Optional[Exception] = None

try:

    from modules.registry import (
        get_available_modules,
        get_module,
        render_module,
    )

except Exception as exc:

    MODULE_REGISTRY_AVAILABLE = False
    MODULE_REGISTRY_ERROR = exc

    get_available_modules = None
    get_module = None
    render_module = None

    logger.warning(
        "Optional module registry unavailable: %s",
        exc,
    )


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_SESSION_STATE = {
    "active_page": "overview",
    "dark_mode": True,
    "database_ready": False,
    "database_error": None,
    "editing_citizen_id": None,
    "editing_household_id": None,
    "editing_civil_event_id": None,
    "editing_document_id": None,
    "editing_voter_id": None,
    "editing_admin_unit_id": None,
}


for state_key, default_value in DEFAULT_SESSION_STATE.items():

    if state_key not in st.session_state:

        st.session_state[state_key] = default_value


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

@st.cache_resource
def initialize_database() -> tuple[bool, Optional[str]]:
    """
    Initialize the database once per Streamlit process.

    Returns:
        (success, error_message)
    """

    if not DATABASE_AVAILABLE:

        return (
            False,
            str(DATABASE_IMPORT_ERROR),
        )

    if init_db is None:

        return (
            False,
            "Database initialization function is unavailable.",
        )

    try:

        init_db()

        return (
            True,
            None,
        )

    except Exception as exc:

        logger.exception(
            "Database initialization failed."
        )

        return (
            False,
            str(exc),
        )


database_ready, database_error = (
    initialize_database()
)

st.session_state.database_ready = database_ready
st.session_state.database_error = database_error


# ============================================================
# DATABASE SESSION
# ============================================================

def get_db():
    """
    Return a new SQLAlchemy database session.

    The caller is responsible for closing it.
    """

    if not DATABASE_AVAILABLE:
        return None

    if SessionLocal is None:
        return None

    return SessionLocal()


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def new_id() -> str:
    """
    Generate a registry UUID.
    """

    return str(uuid.uuid4())


def safe_text(value: Any) -> str:
    """
    Convert values safely to text.
    """

    if value is None:
        return ""

    return str(value)


def calculate_age(
    birth_date: Optional[date],
) -> int:
    """
    Calculate age from date of birth.
    """

    if not birth_date:
        return 0

    today = date.today()

    age = (
        today.year
        - birth_date.year
        - (
            (today.month, today.day)
            < (birth_date.month, birth_date.day)
        )
    )

    return max(age, 0)


def commit_session(db) -> tuple[bool, Optional[str]]:
    """
    Commit a database transaction safely.
    """

    try:

        db.commit()

        return True, None

    except IntegrityError as exc:

        db.rollback()

        logger.exception(
            "Database integrity error."
        )

        return (
            False,
            f"Database constraint error: {exc}",
        )

    except Exception as exc:

        db.rollback()

        logger.exception(
            "Database transaction failed."
        )

        return (
            False,
            str(exc),
        )


def model_columns(model) -> list[str]:
    """
    Return SQLAlchemy column names.
    """

    try:

        return [
            column.name
            for column in model.__table__.columns
        ]

    except Exception:

        return []


def count_records(model) -> int:
    """
    Count records safely.
    """

    if not database_ready or model is None:
        return 0

    db = get_db()

    if db is None:
        return 0

    try:

        result = db.execute(
            select(func.count()).select_from(model)
        )

        return int(result.scalar() or 0)

    except Exception as exc:

        logger.warning(
            "Unable to count %s: %s",
            getattr(model, "__name__", "records"),
            exc,
        )

        return 0

    finally:

        db.close()


def get_record(model, record_id: str):
    """
    Retrieve a single record by primary key.
    """

    if not database_ready or model is None:
        return None

    db = get_db()

    if db is None:
        return None

    try:

        return db.get(
            model,
            record_id,
        )

    except Exception as exc:

        logger.warning(
            "Unable to retrieve record: %s",
            exc,
        )

        return None

    finally:

        db.close()


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
        "danger": "#DC2626",
        "warning": "#D97706",
        "success": "#15803D",
    }


# ============================================================
# CSS
# ============================================================

def inject_css() -> None:

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
    padding-bottom: 4rem;
}}

h1, h2, h3, h4, h5, h6 {{
    color: {theme["text"]} !important;
}}

p, label, span {{
    color: {theme["text"]};
}}


/* ==========================================================
   HEADER
   ========================================================== */

.registry-header {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 18px;
    padding: 12px 10px 18px;
    margin-bottom: 10px;
}}

.header-emblem-fallback {{
    width: 72px;
    height: 72px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: {theme["accent"]};
    color: #FFFFFF;
    font-size: 25px;
    font-weight: 900;
    border: 3px solid {theme["accent_soft"]};
    box-shadow: 0 5px 18px rgba(0,0,0,.20);
}}

.registry-brand {{
    text-align: left;
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


/* ==========================================================
   STATUS
   ========================================================== */

.status-online,
.status-warning {{
    display: inline-flex;
    align-items: center;
    gap: 7px;
    font-weight: 700;
    font-size: 13px;
}}

.status-online {{
    color: {theme["success"]};
}}

.status-warning {{
    color: {theme["warning"]};
}}

.status-dot,
.status-dot-warning {{
    width: 9px;
    height: 9px;
    border-radius: 50%;
    display: inline-block;
}}

.status-dot {{
    background: {theme["success"]};
}}

.status-dot-warning {{
    background: {theme["warning"]};
}}


/* ==========================================================
   SIDEBAR
   ========================================================== */

section[data-testid="stSidebar"] {{
    background: {theme["surface"]};
    border-right: 1px solid {theme["border"]};
}}

.sidebar-title {{
    font-size: 19px;
    font-weight: 800;
    color: {theme["text"]};
    line-height: 1.3;
}}

.sidebar-subtitle {{
    color: {theme["muted"]};
    font-size: 11px;
    line-height: 1.5;
    margin-top: 6px;
}}


/* ==========================================================
   DASHBOARD
   ========================================================== */

.overview-card {{
    background: {theme["surface"]};
    border: 1px solid {theme["border"]};
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 18px;
}}

.registry-kicker {{
    color: {theme["accent"]};
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .08em;
    margin-bottom: 6px;
}}

.registry-heading {{
    color: {theme["text"]};
    font-size: 23px;
    font-weight: 800;
    line-height: 1.3;
}}

.registry-description {{
    color: {theme["muted"]};
    font-size: 14px;
    line-height: 1.6;
    margin-top: 8px;
    max-width: 1000px;
}}


/* ==========================================================
   KPI
   ========================================================== */

.kpi-card {{
    background: {theme["surface"]};
    border: 1px solid {theme["border"]};
    border-radius: 15px;
    padding: 18px;
    min-height: 125px;
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
    margin-top: 8px;
}}

.kpi-description {{
    color: {theme["muted"]};
    font-size: 12px;
    margin-top: 4px;
}}


/* ==========================================================
   MODULE CARDS
   ========================================================== */

.module-card {{
    background: {theme["surface"]};
    border: 1px solid {theme["border"]};
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 12px;
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


/* ==========================================================
   BUTTONS
   ========================================================== */

.stButton > button {{
    border-radius: 9px;
    min-height: 40px;
    font-weight: 650;
}}


/* ==========================================================
   METRICS
   ========================================================== */

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


/* ==========================================================
   TABLES
   ========================================================== */

div[data-testid="stDataFrame"] {{
    border-radius: 12px;
    overflow: hidden;
}}


/* ==========================================================
   STREAMLIT CHROME
   ========================================================== */

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
# HEADER
# ============================================================

st.markdown(
    """
<div class="registry-header">

    <div class="header-emblem-fallback">
        SS
    </div>

    <div class="registry-brand">

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

def sidebar_navigation() -> None:

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

        st.divider()

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
    Database Attention
</div>
                """,
                unsafe_allow_html=True,
            )

            st.warning(
                "Database Attention Required"
            )

        st.divider()

        pages = {
            "Registry": [
                ("overview", "Overview"),
                ("citizens", "Citizens"),
                ("households", "Households"),
                ("civil_registration", "Civil Registration"),
                ("identity", "Identity Management"),
                ("elections", "Elections"),
            ],
            "Operations": [
                (
                    "administrative_units",
                    "Administrative Units",
                ),
            ],
            "Reports & Analytics": [
                ("reports", "Reports & Analytics"),
            ],
            "Administration": [
                ("audit_logs", "Audit Logs"),
                ("system", "System Administration"),
            ],
            "Other Features": [
                ("module_registry", "Module Registry"),
            ],
        }

        for section_name, section_pages in pages.items():

            st.markdown(
                f"**{section_name}**"
            )

            for page_key, page_label in section_pages:

                is_current = (
                    st.session_state.active_page
                    == page_key
                )

                button_label = (
                    f"● {page_label}"
                    if is_current
                    else page_label
                )

                if st.button(
                    button_label,
                    key=f"sidebar_{page_key}",
                    use_container_width=True,
                ):

                    st.session_state.active_page = (
                        page_key
                    )

                    st.rerun()

        st.divider()

        st.markdown("**Appearance**")

        theme_label = (
            "Use Light Mode"
            if st.session_state.dark_mode
            else "Use Dark Mode"
        )

        if st.button(
            theme_label,
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
# GENERIC DATA TABLE
# ============================================================

def show_records(
    model,
    title: str,
    columns: list[str],
    limit: int = 100,
) -> list[Any]:

    if not database_ready:

        st.warning(
            "The database is not connected."
        )

        return []

    if model is None:

        st.error(
            f"{title} model is unavailable."
        )

        return []

    db = get_db()

    if db is None:

        st.error(
            "Unable to create a database session."
        )

        return []

    try:

        result = db.execute(
            select(model).limit(limit)
        )

        records = list(
            result.scalars().all()
        )

        rows = []

        for record in records:

            row = {}

            for column in columns:

                row[column] = getattr(
                    record,
                    column,
                    None,
                )

            rows.append(row)

        if rows:

            st.dataframe(
                rows,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                f"No {title.lower()} records have been registered."
            )

        return records

    except Exception as exc:

        st.error(
            f"Unable to load {title.lower()}."
        )

        with st.expander(
            "Technical details"
        ):

            st.exception(exc)

        return []

    finally:

        db.close()


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:

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
        Centralized management platform for national population
        records, civil registration, identity management,
        households and electoral registration.
    </div>

</div>
        """,
        unsafe_allow_html=True,
    )

    population_count = count_records(
        Citizen
    )

    civil_count = count_records(
        CivilEvent
    )

    identity_count = count_records(
        Document
    )

    election_count = count_records(
        VoterRecord
    )

    columns = st.columns(4)

    kpis = [
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
    ) in zip(columns, kpis):

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
            "Manage national population records, households, persons and demographic information.",
            "citizens",
        ),
        (
            "Elections",
            "Manage electoral registration, voter records and election administration.",
            "elections",
        ),
        (
            "Civil Registration",
            "Register births, deaths, marriages, certificates and other civil events.",
            "civil_registration",
        ),
        (
            "Reports & Analytics",
            "Generate operational reports, statistical summaries and Registry analytics.",
            "reports",
        ),
        (
            "Identity Management",
            "Manage national identity registration, identification records and identity services.",
            "identity",
        ),
        (
            "Administration",
            "Manage system administration, audit records and registry configuration.",
            "system",
        ),
    ]

    service_columns = st.columns(2)

    for index, (
        name,
        description,
        page_key,
    ) in enumerate(services):

        with service_columns[index % 2]:

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
                key=f"overview_open_{page_key}",
                use_container_width=True,
            ):

                st.session_state.active_page = (
                    page_key
                )

                st.rerun()

    st.divider()

    st.subheader(
        "System Status"
    )

    status_col1, status_col2 = st.columns(2)

    with status_col1:

        if database_ready:

            st.success(
                "Database Connected"
            )

        else:

            st.warning(
                "Database Attention Required"
            )

    with status_col2:

        st.success(
            "Registry Interface Available"
        )

    if not database_ready:

        with st.expander(
            "Database technical details"
        ):

            st.code(
                database_error
                or "Unknown database error."
            )


# ============================================================
# CITIZENS
# ============================================================

def citizen_form(
    existing: Optional[Citizen] = None,
) -> None:

    editing = existing is not None

    st.subheader(
        "Edit Citizen"
        if editing
        else "Register Citizen"
    )

    with st.form(
        key=(
            "citizen_edit_form"
            if editing
            else "citizen_create_form"
        )
    ):

        col1, col2 = st.columns(2)

        with col1:

            full_name = st.text_input(
                "Full Name",
                value=safe_text(
                    getattr(existing, "full_name", "")
                ),
            )

            national_id = st.text_input(
                "National ID",
                value=safe_text(
                    getattr(existing, "national_id", "")
                ),
            )

            passport_number = st.text_input(
                "Passport Number",
                value=safe_text(
                    getattr(existing, "passport_number", "")
                ),
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
                            existing,
                            "gender",
                            "Other",
                        )
                    )
                    if getattr(
                        existing,
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

            marital_status = st.selectbox(
                "Marital Status",
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
                            existing,
                            "marital_status",
                            "Single",
                        )
                    )
                    if getattr(
                        existing,
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

            dob = st.date_input(
                "Date of Birth",
                value=getattr(
                    existing,
                    "date_of_birth",
                    date(2000, 1, 1),
                )
                or date(2000, 1, 1),
            )

        with col2:

            nationality = st.text_input(
                "Nationality",
                value=safe_text(
                    getattr(
                        existing,
                        "nationality",
                        "South Sudanese",
                    )
                ),
            )

            phone_number = st.text_input(
                "Phone Number",
                value=safe_text(
                    getattr(
                        existing,
                        "phone_number",
                        "",
                    )
                ),
            )

            email_address = st.text_input(
                "Email Address",
                value=safe_text(
                    getattr(
                        existing,
                        "email_address",
                        "",
                    )
                ),
            )

            tribe = st.text_input(
                "Tribe",
                value=safe_text(
                    getattr(
                        existing,
                        "tribe",
                        "",
                    )
                ),
            )

            native_language = st.text_input(
                "Native Language",
                value=safe_text(
                    getattr(
                        existing,
                        "native_language",
                        "",
                    )
                ),
            )

            state_or_region = st.text_input(
                "State / Region",
                value=safe_text(
                    getattr(
                        existing,
                        "state_or_region",
                        "",
                    )
                ),
            )

        st.divider()

        col3, col4 = st.columns(2)

        with col3:

            county_or_payam = st.text_input(
                "County / Payam",
                value=safe_text(
                    getattr(
                        existing,
                        "county_or_payam",
                        "",
                    )
                ),
            )

            sub_county_or_boma = st.text_input(
                "Sub-county / Boma",
                value=safe_text(
                    getattr(
                        existing,
                        "sub_county_or_boma",
                        "",
                    )
                ),
            )

            boma = st.text_input(
                "Boma",
                value=safe_text(
                    getattr(
                        existing,
                        "boma",
                        "",
                    )
                ),
            )

            community = st.text_input(
                "Community",
                value=safe_text(
                    getattr(
                        existing,
                        "community",
                        "",
                    )
                ),
            )

            residential_address = st.text_area(
                "Residential Address",
                value=safe_text(
                    getattr(
                        existing,
                        "residential_address",
                        "",
                    )
                ),
            )

        with col4:

            education_level = st.selectbox(
                "Education Level",
                [
                    "None / Informal",
                    "Primary",
                    "Secondary",
                    "Certificate",
                    "Diploma",
                    "Bachelor",
                    "Postgraduate",
                    "Other",
                ],
                index=0,
            )

            employment_status = st.selectbox(
                "Employment Status",
                [
                    "Employed",
                    "Self-employed",
                    "Unemployed / Seeking Work",
                    "Student",
                    "Retired",
                    "Other",
                ],
                index=2,
            )

            primary_occupation = st.text_input(
                "Primary Occupation",
                value=safe_text(
                    getattr(
                        existing,
                        "primary_occupation",
                        "",
                    )
                ),
            )

            employer_or_business_name = st.text_input(
                "Employer / Business",
                value=safe_text(
                    getattr(
                        existing,
                        "employer_or_business_name",
                        "",
                    )
                ),
            )

            verification_status = st.selectbox(
                "Verification Status",
                [
                    "Pending Review",
                    "Verified",
                    "Rejected",
                    "Requires Correction",
                ],
                index=0,
            )

        st.divider()

        notes = st.text_area(
            "Notes",
            value=safe_text(
                getattr(
                    existing,
                    "notes",
                    "",
                )
            ),
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
            "Full Name is required."
        )

        return

    db = get_db()

    if db is None:

        st.error(
            "Database is not available."
        )

        return

    try:

        if editing:

            citizen = db.get(
                Citizen,
                existing.id,
            )

            if citizen is None:

                st.error(
                    "Citizen record could not be found."
                )

                return

        else:

            citizen = Citizen(
                id=new_id(),
            )

            db.add(citizen)

        citizen.full_name = full_name.strip()
        citizen.national_id = (
            national_id.strip()
            or None
        )
        citizen.passport_number = (
            passport_number.strip()
            or None
        )
        citizen.gender = gender
        citizen.marital_status = marital_status
        citizen.nationality = nationality.strip()
        citizen.date_of_birth = dob
        citizen.age = calculate_age(dob)
        citizen.phone_number = (
            phone_number.strip()
            or None
        )
        citizen.email_address = (
            email_address.strip()
            or None
        )
        citizen.tribe = tribe.strip()
        citizen.native_language = (
            native_language.strip()
        )
        citizen.state_or_region = (
            state_or_region.strip()
        )
        citizen.county_or_payam = (
            county_or_payam.strip()
        )
        citizen.sub_county_or_boma = (
            sub_county_or_boma.strip()
        )
        citizen.boma = (
            boma.strip()
            or None
        )
        citizen.community = (
            community.strip()
        )
        citizen.residential_address = (
            residential_address.strip()
            or None
        )
        citizen.education_level = (
            education_level
        )
        citizen.employment_status = (
            employment_status
        )
        citizen.primary_occupation = (
            primary_occupation.strip()
            or None
        )
        citizen.employer_or_business_name = (
            employer_or_business_name.strip()
            or None
        )
        citizen.verification_status = (
            verification_status
        )
        citizen.notes = (
            notes.strip()
            or None
        )

        success, error = commit_session(db)

        if success:

            st.success(
                "Citizen record saved successfully."
            )

            st.session_state.editing_citizen_id = None

            st.rerun()

        else:

            st.error(
                error
                or "Unable to save citizen."
            )

    finally:

        db.close()


def render_citizens() -> None:

    st.title(
        "Citizens"
    )

    st.caption(
        "National population and citizen registry management."
    )

    if not database_ready:

        st.warning(
            "The citizen registry requires a connected database."
        )

        return

    if (
        st.session_state.editing_citizen_id
        is not None
    ):

        citizen = get_record(
            Citizen,
            st.session_state.editing_citizen_id,
        )

        if citizen:

            if st.button(
                "Back to Citizen Registry",
                key="citizen_back_from_edit",
            ):

                st.session_state.editing_citizen_id = None
                st.rerun()

            citizen_form(
                citizen
            )

            return

        st.session_state.editing_citizen_id = None

    st.subheader(
        "Register New Citizen"
    )

    citizen_form()

    st.divider()

    st.subheader(
        "Citizen Records"
    )

    db = get_db()

    if db is None:
        return

    try:

        citizens = list(
            db.execute(
                select(Citizen)
                .order_by(
                    Citizen.created_at.desc()
                )
                .limit(200)
            ).scalars().all()
        )

        if not citizens:

            st.info(
                "No citizen records found."
            )

            return

        for citizen in citizens:

            col1, col2, col3 = st.columns(
                [5, 2, 1]
            )

            with col1:

                st.markdown(
                    f"**{safe_text(citizen.full_name)}**"
                )

                st.caption(
                    f"National ID: "
                    f"{safe_text(citizen.national_id) or 'Not assigned'} "
                    f"• {safe_text(citizen.state_or_region)}"
                )

            with col2:

                st.write(
                    safe_text(
                        citizen.verification_status
                    )
                )

            with col3:

                if st.button(
                    "Edit",
                    key=f"edit_citizen_{citizen.id}",
                ):

                    st.session_state.editing_citizen_id = (
                        citizen.id
                    )

                    st.rerun()

            st.divider()

    finally:

        db.close()


# ============================================================
# HOUSEHOLDS
# ============================================================

def render_households() -> None:

    st.title(
        "Households"
    )

    st.caption(
        "Household registration and residential management."
    )

    if not database_ready:

        st.warning(
            "The household registry requires a connected database."
        )

        return

    editing = (
        st.session_state.editing_household_id
        is not None
    )

    existing = None

    if editing:

        existing = get_record(
            Household,
            st.session_state.editing_household_id,
        )

    if editing and existing is None:

        st.session_state.editing_household_id = None
        editing = False

    with st.form(
        key=(
            "household_edit_form"
            if editing
            else "household_create_form"
        )
    ):

        household_number = st.text_input(
            "Household Number",
            value=safe_text(
                getattr(
                    existing,
                    "household_number",
                    "",
                )
            ),
        )

        head_citizen_id = st.text_input(
            "Head Citizen ID",
            value=safe_text(
                getattr(
                    existing,
                    "head_citizen_id",
                    "",
                )
            ),
        )

        col1, col2 = st.columns(2)

        with col1:

            state_or_region = st.text_input(
                "State / Region",
                value=safe_text(
                    getattr(
                        existing,
                        "state_or_region",
                        "",
                    )
                ),
            )

            county_or_payam = st.text_input(
                "County / Payam",
                value=safe_text(
                    getattr(
                        existing,
                        "county_or_payam",
                        "",
                    )
                ),
            )

            sub_county_or_boma = st.text_input(
                "Sub-county / Boma",
                value=safe_text(
                    getattr(
                        existing,
                        "sub_county_or_boma",
                        "",
                    )
                ),
            )

        with col2:

            boma = st.text_input(
                "Boma",
                value=safe_text(
                    getattr(
                        existing,
                        "boma",
                        "",
                    )
                ),
            )

            community = st.text_input(
                "Community",
                value=safe_text(
                    getattr(
                        existing,
                        "community",
                        "",
                    )
                ),
            )

            residential_address = st.text_area(
                "Residential Address",
                value=safe_text(
                    getattr(
                        existing,
                        "residential_address",
                        "",
                    )
                ),
            )

        submitted = st.form_submit_button(
            "Update Household"
            if editing
            else "Register Household",
            use_container_width=True,
        )

    if submitted:

        if not household_number.strip():

            st.error(
                "Household Number is required."
            )

        else:

            db = get_db()

            if db:

                try:

                    if editing:

                        household = db.get(
                            Household,
                            existing.id,
                        )

                    else:

                        household = Household(
                            id=new_id()
                        )

                        db.add(household)

                    household.household_number = (
                        household_number.strip()
                    )

                    household.head_citizen_id = (
                        head_citizen_id.strip()
                        or None
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

                    success, error = commit_session(
                        db
                    )

                    if success:

                        st.success(
                            "Household saved successfully."
                        )

                        st.session_state.editing_household_id = None

                        st.rerun()

                    else:

                        st.error(
                            error
                            or "Unable to save household."
                        )

                finally:

                    db.close()

    st.divider()

    show_records(
        Household,
        "Households",
        [
            "id",
            "household_number",
            "head_citizen_id",
            "state_or_region",
            "county_or_payam",
            "community",
        ],
    )


# ============================================================
# CIVIL REGISTRATION
# ============================================================

def render_civil_registration() -> None:

    st.title(
        "Civil Registration"
    )

    st.caption(
        "Birth, death, marriage, divorce and other civil events."
    )

    if not database_ready:

        st.warning(
            "Civil registration requires a connected database."
        )

        return

    editing = (
        st.session_state.editing_civil_event_id
        is not None
    )

    existing = None

    if editing:

        existing = get_record(
            CivilEvent,
            st.session_state.editing_civil_event_id,
        )

    if editing and existing is None:

        st.session_state.editing_civil_event_id = None
        editing = False

    with st.form(
        key=(
            "civil_event_edit_form"
            if editing
            else "civil_event_create_form"
        )
    ):

        reference_number = st.text_input(
            "Reference Number",
            value=safe_text(
                getattr(
                    existing,
                    "reference_number",
                    f"CR-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                )
            ),
        )

        event_type = st.selectbox(
            "Event Type",
            [
                "Birth",
                "Death",
                "Marriage",
                "Divorce",
                "Other",
            ],
            index=0,
        )

        citizen_id = st.text_input(
            "Citizen ID",
            value=safe_text(
                getattr(
                    existing,
                    "citizen_id",
                    "",
                )
            ),
        )

        event_date = st.date_input(
            "Event Date",
            value=getattr(
                existing,
                "event_date",
                date.today(),
            )
            or date.today(),
        )

        registration_centre = st.text_input(
            "Registration Centre",
            value=safe_text(
                getattr(
                    existing,
                    "registration_centre",
                    "",
                )
            ),
        )

        document_number = st.text_input(
            "Document Number",
            value=safe_text(
                getattr(
                    existing,
                    "document_number",
                    "",
                )
            ),
        )

        status = st.selectbox(
            "Status",
            [
                "Pending Review",
                "Registered",
                "Verified",
                "Rejected",
            ],
            index=0,
        )

        notes = st.text_area(
            "Notes",
            value=safe_text(
                getattr(
                    existing,
                    "notes",
                    "",
                )
            ),
        )

        submitted = st.form_submit_button(
            "Update Civil Event"
            if editing
            else "Register Civil Event",
            use_container_width=True,
        )

    if submitted:

        if not reference_number.strip():

            st.error(
                "Reference Number is required."
            )

            return

        db = get_db()

        if db is None:
            return

        try:

            if editing:

                event = db.get(
                    CivilEvent,
                    existing.id,
                )

            else:

                event = CivilEvent(
                    id=new_id()
                )

                db.add(event)

            event.reference_number = (
                reference_number.strip()
            )

            event.event_type = event_type

            event.citizen_id = (
                citizen_id.strip()
                or None
            )

            event.event_date = event_date

            event.registration_centre = (
                registration_centre.strip()
                or None
            )

            event.document_number = (
                document_number.strip()
                or None
            )

            event.status = status

            event.notes = (
                notes.strip()
                or None
            )

            success, error = commit_session(
                db
            )

            if success:

                st.success(
                    "Civil registration record saved."
                )

                st.session_state.editing_civil_event_id = None

                st.rerun()

            else:

                st.error(
                    error
                    or "Unable to save civil event."
                )

        finally:

            db.close()

    st.divider()

    show_records(
        CivilEvent,
        "Civil Events",
        [
            "id",
            "reference_number",
            "event_type",
            "citizen_id",
            "event_date",
            "status",
        ],
    )


# ============================================================
# IDENTITY
# ============================================================

def render_identity() -> None:

    st.title(
        "Identity Management"
    )

    st.caption(
        "National identity and identity document management."
    )

    if not database_ready:

        st.warning(
            "Identity management requires a connected database."
        )

        return

    editing = (
        st.session_state.editing_document_id
        is not None
    )

    existing = None

    if editing:

        existing = get_record(
            Document,
            st.session_state.editing_document_id,
        )

    if editing and existing is None:

        st.session_state.editing_document_id = None
        editing = False

    with st.form(
        key=(
            "identity_edit_form"
            if editing
            else "identity_create_form"
        )
    ):

        document_number = st.text_input(
            "Document Number",
            value=safe_text(
                getattr(
                    existing,
                    "document_number",
                    "",
                )
            ),
        )

        document_type = st.selectbox(
            "Document Type",
            [
                "National Identity Card",
                "Passport",
                "Birth Certificate",
                "Other",
            ],
        )

        citizen_id = st.text_input(
            "Citizen ID",
            value=safe_text(
                getattr(
                    existing,
                    "citizen_id",
                    "",
                )
            ),
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
        )

        col1, col2 = st.columns(2)

        with col1:

            issued_date = st.date_input(
                "Issued Date",
                value=getattr(
                    existing,
                    "issued_date",
                    date.today(),
                )
                or date.today(),
            )

        with col2:

            expiry_date = st.date_input(
                "Expiry Date",
                value=getattr(
                    existing,
                    "expiry_date",
                    date.today(),
                )
                or date.today(),
            )

        file_name = st.text_input(
            "File Name",
            value=safe_text(
                getattr(
                    existing,
                    "file_name",
                    "",
                )
            ),
        )

        submitted = st.form_submit_button(
            "Update Identity Document"
            if editing
            else "Register Identity Document",
            use_container_width=True,
        )

    if submitted:

        db = get_db()

        if db is None:
            return

        try:

            if editing:

                document = db.get(
                    Document,
                    existing.id,
                )

            else:

                document = Document(
                    id=new_id()
                )

                db.add(document)

            document.document_number = (
                document_number.strip()
                or None
            )

            document.document_type = (
                document_type
            )

            document.citizen_id = (
                citizen_id.strip()
                or None
            )

            document.status = status

            document.issued_date = issued_date

            document.expiry_date = expiry_date

            document.file_name = (
                file_name.strip()
                or None
            )

            success, error = commit_session(
                db
            )

            if success:

                st.success(
                    "Identity document saved."
                )

                st.session_state.editing_document_id = None

                st.rerun()

            else:

                st.error(
                    error
                    or "Unable to save identity document."
                )

        finally:

            db.close()

    st.divider()

    show_records(
        Document,
        "Identity Documents",
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


# ============================================================
# ELECTIONS
# ============================================================

def render_elections() -> None:

    st.title(
        "Elections"
    )

    st.caption(
        "Electoral registration and voter administration."
    )

    if not database_ready:

        st.warning(
            "Election management requires a connected database."
        )

        return

    editing = (
        st.session_state.editing_voter_id
        is not None
    )

    existing = None

    if editing:

        existing = get_record(
            VoterRecord,
            st.session_state.editing_voter_id,
        )

    if editing and existing is None:

        st.session_state.editing_voter_id = None
        editing = False

    with st.form(
        key=(
            "voter_edit_form"
            if editing
            else "voter_create_form"
        )
    ):

        citizen_id = st.text_input(
            "Citizen ID",
            value=safe_text(
                getattr(
                    existing,
                    "citizen_id",
                    "",
                )
            ),
        )

        voter_id_number = st.text_input(
            "Voter ID Number",
            value=safe_text(
                getattr(
                    existing,
                    "voter_id_number",
                    "",
                )
            ),
        )

        voter_status = st.selectbox(
            "Voter Status",
            [
                "Active",
                "Pending",
                "Suspended",
                "Transferred",
                "Removed",
            ],
        )

        constituency = st.text_input(
            "Constituency",
            value=safe_text(
                getattr(
                    existing,
                    "constituency",
                    "",
                )
            ),
        )

        polling_station_id = st.text_input(
            "Polling Station ID",
            value=safe_text(
                getattr(
                    existing,
                    "polling_station_id",
                    "",
                )
            ),
        )

        polling_station_name = st.text_input(
            "Polling Station Name",
            value=safe_text(
                getattr(
                    existing,
                    "polling_station_name",
                    "",
                )
            ),
        )

        has_voted = st.checkbox(
            "Marked as Voted",
            value=bool(
                getattr(
                    existing,
                    "has_voted",
                    False,
                )
            ),
        )

        submitted = st.form_submit_button(
            "Update Voter Record"
            if editing
            else "Register Voter",
            use_container_width=True,
        )

    if submitted:

        if not citizen_id.strip():

            st.error(
                "Citizen ID is required."
            )

            return

        db = get_db()

        if db is None:
            return

        try:

            if editing:

                voter = db.get(
                    VoterRecord,
                    existing.id,
                )

            else:

                voter = VoterRecord(
                    id=new_id()
                )

                db.add(voter)

            voter.citizen_id = (
                citizen_id.strip()
            )

            voter.voter_id_number = (
                voter_id_number.strip()
                or None
            )

            voter.voter_status = (
                voter_status
            )

            voter.constituency = (
                constituency.strip()
                or None
            )

            voter.polling_station_id = (
                polling_station_id.strip()
                or None
            )

            voter.polling_station_name = (
                polling_station_name.strip()
                or None
            )

            voter.has_voted = has_voted

            if has_voted:

                voter.voted_at = (
                    getattr(
                        existing,
                        "voted_at",
                        None,
                    )
                    or datetime.utcnow()
                )

            else:

                voter.voted_at = None

            success, error = commit_session(
                db
            )

            if success:

                st.success(
                    "Voter record saved."
                )

                st.session_state.editing_voter_id = None

                st.rerun()

            else:

                st.error(
                    error
                    or "Unable to save voter record."
                )

        finally:

            db.close()

    st.divider()

    show_records(
        VoterRecord,
        "Voter Records",
        [
            "id",
            "citizen_id",
            "voter_id_number",
            "voter_status",
            "constituency",
            "polling_station_name",
            "has_voted",
        ],
    )


# ============================================================
# ADMINISTRATIVE UNITS
# ============================================================

def render_administrative_units() -> None:

    st.title(
        "Administrative Units"
    )

    st.caption(
        "States, counties, payams, bomas and other administrative areas."
    )

    if not database_ready:

        st.warning(
            "Administrative management requires a connected database."
        )

        return

    editing = (
        st.session_state.editing_admin_unit_id
        is not None
    )

    existing = None

    if editing:

        existing = get_record(
            AdministrativeUnit,
            st.session_state.editing_admin_unit_id,
        )

    if editing and existing is None:

        st.session_state.editing_admin_unit_id = None
        editing = False

    with st.form(
        key=(
            "admin_unit_edit_form"
            if editing
            else "admin_unit_create_form"
        )
    ):

        unit_type = st.selectbox(
            "Unit Type",
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
            "Name",
            value=safe_text(
                getattr(
                    existing,
                    "name",
                    "",
                )
            ),
        )

        code = st.text_input(
            "Code",
            value=safe_text(
                getattr(
                    existing,
                    "code",
                    "",
                )
            ),
        )

        parent_id = st.text_input(
            "Parent Unit ID",
            value=safe_text(
                getattr(
                    existing,
                    "parent_id",
                    "",
                )
            ),
        )

        state_or_region = st.text_input(
            "State / Region",
            value=safe_text(
                getattr(
                    existing,
                    "state_or_region",
                    "",
                )
            ),
        )

        administrator_name = st.text_input(
            "Administrator",
            value=safe_text(
                getattr(
                    existing,
                    "administrator_name",
                    "",
                )
            ),
        )

        headquarters = st.text_input(
            "Headquarters",
            value=safe_text(
                getattr(
                    existing,
                    "headquarters",
                    "",
                )
            ),
        )

        target_population = st.number_input(
            "Target Population",
            min_value=0,
            value=int(
                getattr(
                    existing,
                    "target_population",
                    0,
                )
                or 0
            ),
        )

        notes = st.text_area(
            "Notes",
            value=safe_text(
                getattr(
                    existing,
                    "notes",
                    "",
                )
            ),
        )

        submitted = st.form_submit_button(
            "Update Administrative Unit"
            if editing
            else "Create Administrative Unit",
            use_container_width=True,
        )

    if submitted:

        if not name.strip():

            st.error(
                "Name is required."
            )

            return

        if not code.strip():

            st.error(
                "Code is required."
            )

            return

        db = get_db()

        if db is None:
            return

        try:

            if editing:

                unit = db.get(
                    AdministrativeUnit,
                    existing.id,
                )

            else:

                unit = AdministrativeUnit(
                    id=new_id()
                )

                db.add(unit)

            unit.unit_type = unit_type
            unit.name = name.strip()
            unit.code = code.strip()
            unit.parent_id = (
                parent_id.strip()
                or None
            )
            unit.state_or_region = (
                state_or_region.strip()
            )
            unit.administrator_name = (
                administrator_name.strip()
                or None
            )
            unit.headquarters = (
                headquarters.strip()
                or None
            )
            unit.target_population = (
                int(target_population)
                if target_population
                else None
            )
            unit.notes = (
                notes.strip()
                or None
            )

            success, error = commit_session(
                db
            )

            if success:

                st.success(
                    "Administrative unit saved."
                )

                st.session_state.editing_admin_unit_id = None

                st.rerun()

            else:

                st.error(
                    error
                    or "Unable to save administrative unit."
                )

        finally:

            db.close()

    st.divider()

    show_records(
        AdministrativeUnit,
        "Administrative Units",
        [
            "id",
            "unit_type",
            "name",
            "code",
            "parent_id",
            "state_or_region",
        ],
    )


# ============================================================
# REPORTS
# ============================================================

def render_reports() -> None:

    st.title(
        "Reports & Analytics"
    )

    st.caption(
        "Registry statistics and operational summaries."
    )

    population = count_records(
        Citizen
    )

    households = count_records(
        Household
    )

    civil_events = count_records(
        CivilEvent
    )

    identity_documents = count_records(
        Document
    )

    voters = count_records(
        VoterRecord
    )

    units = count_records(
        AdministrativeUnit
    )

    cols = st.columns(3)

    report_metrics = [
        (
            "Population",
            population,
        ),
        (
            "Households",
            households,
        ),
        (
            "Civil Events",
            civil_events,
        ),
        (
            "Identity Documents",
            identity_documents,
        ),
        (
            "Voter Records",
            voters,
        ),
        (
            "Administrative Units",
            units,
        ),
    ]

    for index, (
        label,
        value,
    ) in enumerate(report_metrics):

        with cols[index % 3]:

            st.metric(
                label,
                f"{value:,}",
            )

    st.divider()

    st.subheader(
        "Population by State / Region"
    )

    if database_ready and Citizen:

        db = get_db()

        if db:

            try:

                result = db.execute(
                    select(
                        Citizen.state_or_region,
                        func.count(Citizen.id),
                    )
                    .group_by(
                        Citizen.state_or_region
                    )
                    .order_by(
                        func.count(Citizen.id).desc()
                    )
                )

                rows = [
                    {
                        "State / Region":
                            state or "Not Specified",
                        "Population":
                            count,
                    }
                    for state, count
                    in result.all()
                ]

                if rows:

                    st.dataframe(
                        rows,
                        use_container_width=True,
                        hide_index=True,
                    )

                else:

                    st.info(
                        "No population analytics are available yet."
                    )

            finally:

                db.close()


# ============================================================
# AUDIT LOGS
# ============================================================

def render_audit_logs() -> None:

    st.title(
        "Audit Logs"
    )

    st.caption(
        "Registry activity and administrative audit records."
    )

    show_records(
        AuditLog,
        "Audit Logs",
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


# ============================================================
# SYSTEM ADMINISTRATION
# ============================================================

def render_system() -> None:

    st.title(
        "System Administration"
    )

    st.caption(
        "Registry platform configuration and system status."
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "Application"
        )

        st.write(
            "South Sudan National Registry"
        )

        st.write(
            "Version 1.0.0"
        )

        st.write(
            "Streamlit AI Studio"
        )

    with col2:

        st.subheader(
            "Database"
        )

        if database_ready:

            st.success(
                "Connected"
            )

        else:

            st.warning(
                "Attention Required"
            )

    st.divider()

    st.subheader(
        "Database Diagnostics"
    )

    if database_ready:

        st.success(
            "Database initialization completed successfully."
        )

    else:

        st.error(
            "Database initialization failed."
        )

        with st.expander(
            "Technical details"
        ):

            st.code(
                database_error
                or "Unknown error."
            )

    st.divider()

    st.subheader(
        "Model Availability"
    )

    model_status = {
        "Citizen": Citizen,
        "Household": Household,
        "CivilEvent": CivilEvent,
        "Document": Document,
        "VoterRecord": VoterRecord,
        "AdministrativeUnit": AdministrativeUnit,
        "AuditLog": AuditLog,
    }

    for name, model in model_status.items():

        if model is not None:

            st.success(
                f"{name}: Available"
            )

        else:

            st.error(
                f"{name}: Unavailable"
            )


# ============================================================
# MODULE REGISTRY
# ============================================================

def render_module_registry() -> None:

    st.title(
        "Module Registry"
    )

    st.caption(
        "Configured operational modules available to the Registry platform."
    )

    if not MODULE_REGISTRY_AVAILABLE:

        st.info(
            "The optional module registry is not available. "
            "Core Registry modules remain available."
        )

        if MODULE_REGISTRY_ERROR:

            with st.expander(
                "Technical details"
            ):

                st.exception(
                    MODULE_REGISTRY_ERROR
                )

        return

    try:

        modules = list(
            get_available_modules()
            or []
        )

    except Exception as exc:

        st.error(
            "Unable to load registry modules."
        )

        with st.expander(
            "Technical details"
        ):

            st.exception(exc)

        return

    if not modules:

        st.info(
            "No external registry modules are configured."
        )

        return

    for module in modules:

        label = getattr(
            module,
            "label",
            getattr(
                module,
                "key",
                "Registry Module",
            ),
        )

        description = getattr(
            module,
            "description",
            "",
        )

        available = bool(
            getattr(
                module,
                "available",
                False,
            )
        )

        st.markdown(
            f"""
<div class="module-card">

    <div class="module-name">
        {safe_text(label)}
    </div>

    <div class="module-description">
        {safe_text(description)}
    </div>

</div>
            """,
            unsafe_allow_html=True,
        )

        if available:

            st.success(
                "Operational"
            )

        else:

            st.warning(
                "Unavailable"
            )


# ============================================================
# OPTIONAL EXTERNAL MODULE
# ============================================================

def render_external_module(
    page_key: str,
) -> None:

    if not MODULE_REGISTRY_AVAILABLE:

        st.error(
            "The requested module is unavailable."
        )

        return

    try:

        module = get_module(
            page_key
        )

    except Exception as exc:

        st.error(
            "Unable to locate the requested module."
        )

        with st.expander(
            "Technical details"
        ):

            st.exception(exc)

        return

    if module is None:

        st.error(
            "The requested registry module could not be found."
        )

        return

    available = bool(
        getattr(
            module,
            "available",
            False,
        )
    )

    if not available:

        st.warning(
            "This registry module is currently unavailable."
        )

        error = getattr(
            module,
            "error",
            None,
        )

        if error:

            with st.expander(
                "Technical details"
            ):

                st.code(
                    safe_text(error)
                )

        return

    try:

        render_module(
            page_key
        )

    except Exception as exc:

        logger.exception(
            "External module failed: %s",
            page_key,
        )

        st.error(
            "The selected module encountered a runtime error."
        )

        with st.expander(
            "Technical details"
        ):

            st.exception(exc)


# ============================================================
# PAGE ROUTER
# ============================================================

PAGE_RENDERERS = {
    "overview": render_overview,
    "citizens": render_citizens,
    "households": render_households,
    "civil_registration": render_civil_registration,
    "identity": render_identity,
    "elections": render_elections,
    "administrative_units": render_administrative_units,
    "reports": render_reports,
    "audit_logs": render_audit_logs,
    "system": render_system,
    "module_registry": render_module_registry,
}


# ============================================================
# MAIN APPLICATION
# ============================================================

active_page = st.session_state.active_page

renderer = PAGE_RENDERERS.get(
    active_page
)

if renderer is not None:

    renderer()

else:

    render_external_module(
        active_page
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

footer_col1, footer_col2 = st.columns(2)

with footer_col1:

    st.markdown(
        """
<div class="registry-version">
    South Sudan National Registry •
    Registry Platform • Version 1.0.0
</div>
        """,
        unsafe_allow_html=True,
    )

with footer_col2:

    st.markdown(
        """
<div class="registry-version">
    Registry data should be treated as authoritative only
    after verification and appropriate administrative approval.
</div>
        """,
        unsafe_allow_html=True,
)
