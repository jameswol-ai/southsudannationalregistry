"""
South Sudan National Registry
Streamlit AI Studio

National population, civil registration, identity,
household and electoral registry management platform.

Application entry point:

    streamlit run streamlit_app.py

This version provides:

    - Registry dashboard
    - Sidebar navigation
    - Database-backed CRUD
    - Add / View / Edit / Delete
    - Search
    - Pagination
    - Type-aware database forms
    - Safe database error handling
    - Audit logging
    - Safe emblem handling
"""

from __future__ import annotations

import logging
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any

import streamlit as st

from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session


# ============================================================
# APPLICATION CONSTANTS
# ============================================================

APP_NAME = "South Sudan National Registry"
APP_VERSION = "1.0.0"
APP_PLATFORM = "Registry Platform"


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

EMBLEM_PATH = ASSETS_DIR / "south_sudan_emblem.png"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

# IMPORTANT:
# Must execute before session state or Streamlit UI work.

st.set_page_config(
    page_title=APP_NAME,
    page_icon="SS",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
)

logger = logging.getLogger(
    "south_sudan_national_registry"
)


# ============================================================
# DATABASE IMPORT
# ============================================================

try:

    from database.database import (
        Base,
        init_db,
    )

except Exception:

    Base = None

    from database.database import init_db


# ============================================================
# MODELS
# ============================================================

try:

    from models import (
        Citizen,
        Household,
        CivilEvent,
        Document,
        VoterRecord,
        AdministrativeUnit,
        AuditLog,
    )

except ImportError:

    try:

        from database.models import (
            Citizen,
            Household,
            CivilEvent,
            Document,
            VoterRecord,
            AdministrativeUnit,
            AuditLog,
        )

    except ImportError:

        Citizen = None
        Household = None
        CivilEvent = None
        Document = None
        VoterRecord = None
        AdministrativeUnit = None
        AuditLog = None


# ============================================================
# SESSION FACTORY
# ============================================================

def get_session_factory():
    """
    Locate the existing SQLAlchemy session factory.

    Different versions of the project may expose the factory
    under different names. This function supports the common
    names without requiring the database.py file to be changed.
    """

    try:

        import database.database as database_module

    except Exception as exc:

        logger.exception(
            "Unable to import database module."
        )

        raise RuntimeError(
            "The database module could not be imported."
        ) from exc

    candidate_names = (
        "SessionLocal",
        "session_factory",
        "SessionFactory",
        "Session",
        "sessionmaker",
    )

    for name in candidate_names:

        candidate = getattr(
            database_module,
            name,
            None,
        )

        if candidate is None:
            continue

        if callable(candidate):
            return candidate

    raise RuntimeError(
        "No SQLAlchemy session factory was found "
        "in database/database.py. Expected one of: "
        + ", ".join(candidate_names)
    )


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

@st.cache_resource
def initialize_database() -> bool:
    """
    Initialize database tables once per Streamlit process.
    """

    init_db()

    return True


# ============================================================
# DATABASE STARTUP
# ============================================================

database_available = False
database_error: Exception | None = None

try:

    initialize_database()

    database_available = True

except Exception as exc:

    database_error = exc

    logger.exception(
        "Database initialization failed."
    )


# ============================================================
# SESSION STATE
# ============================================================

if "active_module" not in st.session_state:

    st.session_state.active_module = "overview"


if "dark_mode" not in st.session_state:

    st.session_state.dark_mode = True


if "records_per_page" not in st.session_state:

    st.session_state.records_per_page = 25


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
            "white": "#FFFFFF",
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
        "white": "#FFFFFF",
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
            padding-bottom: 3rem;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: {theme["text"]} !important;
        }}

        p, label {{
            color: {theme["text"]};
        }}

        /* ----------------------------------------------------
           HEADER
           ---------------------------------------------------- */

        .registry-header {{
            padding: 8px 0 18px;
            text-align: center;
        }}

        .registry-emblem {{
            width: 72px;
            height: 72px;
            border-radius: 50%;
            margin: 0 auto 12px;

            display: flex;
            align-items: center;
            justify-content: center;

            background: {theme["accent"]};
            color: white;

            font-size: 26px;
            font-weight: 800;

            border: 3px solid rgba(255,255,255,.25);
        }}

        .registry-brand {{
            display: flex;
            flex-direction: column;
            align-items: center;
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
            margin-top: 7px;
            line-height: 1.5;
        }}

        .registry-status {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 15px;
            margin-top: 12px;
        }}

        .status-online {{
            color: {theme["success"]};
            font-size: 12px;
            font-weight: 700;
        }}

        .status-warning {{
            color: {theme["warning"]};
            font-size: 12px;
            font-weight: 700;
        }}

        .status-dot,
        .status-dot-warning {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 5px;
            background: {theme["success"]};
        }}

        .status-dot-warning {{
            background: {theme["warning"]};
        }}

        .registry-version {{
            color: {theme["muted"]};
            font-size: 12px;
        }}

        /* ----------------------------------------------------
           SIDEBAR
           ---------------------------------------------------- */

        section[data-testid="stSidebar"] {{
            background: {theme["surface"]};
            border-right: 1px solid {theme["border"]};
        }}

        .sidebar-title {{
            color: {theme["text"]};
            font-size: 18px;
            font-weight: 800;
            line-height: 1.3;
        }}

        .sidebar-subtitle {{
            color: {theme["muted"]};
            font-size: 11px;
            line-height: 1.5;
            margin-top: 5px;
            margin-bottom: 16px;
        }}

        .sidebar-section {{
            color: {theme["accent"]};
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .08em;
            margin-top: 18px;
            margin-bottom: 6px;
        }}

        /* ----------------------------------------------------
           CARDS
           ---------------------------------------------------- */

        .overview-card,
        .module-card,
        .editor-card {{
            background: {theme["surface"]};
            border: 1px solid {theme["border"]};
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 16px;
        }}

        .registry-kicker {{
            color: {theme["accent"]};
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .08em;
            margin-bottom: 5px;
        }}

        .registry-heading {{
            color: {theme["text"]};
            font-size: 22px;
            font-weight: 800;
            margin-bottom: 6px;
        }}

        .registry-description {{
            color: {theme["muted"]};
            font-size: 14px;
            line-height: 1.6;
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

        /* ----------------------------------------------------
           KPI
           ---------------------------------------------------- */

        .kpi-card {{
            background: {theme["surface"]};
            border: 1px solid {theme["border"]};
            border-radius: 14px;
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
            font-weight: 800;
            margin-top: 7px;
        }}

        .kpi-description {{
            color: {theme["muted"]};
            font-size: 11px;
            margin-top: 5px;
        }}

        /* ----------------------------------------------------
           STREAMLIT METRICS
           ---------------------------------------------------- */

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

        /* ----------------------------------------------------
           BUTTONS
           ---------------------------------------------------- */

        .stButton > button {{
            border-radius: 9px;
            min-height: 40px;
            font-weight: 650;
        }}

        /* ----------------------------------------------------
           INPUTS
           ---------------------------------------------------- */

        input,
        textarea {{
            border-radius: 9px !important;
        }}

        /* ----------------------------------------------------
           TABLE
           ---------------------------------------------------- */

        [data-testid="stDataFrame"] {{
            border: 1px solid {theme["border"]};
            border-radius: 12px;
            overflow: hidden;
        }}

        /* ----------------------------------------------------
           FOOTER
           ---------------------------------------------------- */

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

def humanize(value: str) -> str:

    return (
        value.replace("_", " ")
        .replace("-", " ")
        .strip()
        .title()
    )


def safe_string(value: Any) -> str:

    if value is None:
        return ""

    return str(value)


def model_label(model: Any) -> str:

    labels = {
        "Citizen": "Citizens",
        "Household": "Households",
        "CivilEvent": "Civil Registration",
        "Document": "Documents",
        "VoterRecord": "Elections",
        "AdministrativeUnit": "Administrative Units",
        "AuditLog": "Audit & Activity",
    }

    return labels.get(
        getattr(model, "__name__", ""),
        humanize(
            getattr(
                model,
                "__name__",
                "Registry Records",
            )
        ),
    )


def get_model_columns(model: Any) -> list[Any]:

    mapper = inspect(model)

    return list(
        mapper.columns
    )


def get_primary_keys(model: Any) -> list[Any]:

    return [
        column
        for column in get_model_columns(model)
        if column.primary_key
    ]


def get_column_type_name(column: Any) -> str:

    return type(
        column.type
    ).__name__.lower()


def is_boolean_column(column: Any) -> bool:

    return isinstance(
        column.type,
        __import__("sqlalchemy").Boolean,
    )


def is_date_column(column: Any) -> bool:

    return isinstance(
        column.type,
        __import__("sqlalchemy").Date,
    )


def is_datetime_column(column: Any) -> bool:

    return isinstance(
        column.type,
        __import__("sqlalchemy").DateTime,
    )


def is_integer_column(column: Any) -> bool:

    return isinstance(
        column.type,
        __import__("sqlalchemy").Integer,
    )


def is_float_column(column: Any) -> bool:

    return isinstance(
        column.type,
        __import__("sqlalchemy").Float,
    )


def is_text_column(column: Any) -> bool:

    type_name = get_column_type_name(
        column
    )

    return type_name in {
        "text",
        "string",
        "varchar",
        "nvarchar",
        "char",
    }


def format_value(value: Any) -> str:

    if value is None:
        return ""

    if isinstance(value, datetime):
        return value.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    if isinstance(value, date):
        return value.isoformat()

    return str(value)


# ============================================================
# SAFE EMBLEM
# ============================================================

def render_emblem() -> None:
    """
    Render the emblem only if it is a valid image.

    A missing or corrupt PNG will never terminate the app.
    """

    if not EMBLEM_PATH.exists():

        st.markdown(
            """
            <div class="registry-emblem">
                SS
            </div>
            """,
            unsafe_allow_html=True,
        )

        return

    try:

        from PIL import Image

        image = Image.open(
            EMBLEM_PATH
        )

        image.verify()

        image = Image.open(
            EMBLEM_PATH
        )

        col1, col2, col3 = st.columns(
            [1, 1, 1]
        )

        with col2:

            st.image(
                image,
                width=78,
            )

    except Exception as exc:

        logger.warning(
            "Invalid South Sudan emblem: %s",
            exc,
        )

        st.markdown(
            """
            <div class="registry-emblem">
                SS
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# HEADER
# ============================================================

def render_header() -> None:

    render_emblem()

    st.markdown(
        f"""
        <div class="registry-header">

            <div class="registry-brand">

                <div class="registry-title">
                    {APP_NAME}
                </div>

                <div class="registry-subtitle">
                    National Population • Civil Registration •
                    Identity • Elections
                </div>

            </div>

            <div class="registry-status">

                <div class="{
                    "status-online"
                    if database_available
                    else "status-warning"
                }">

                    <span class="{
                        "status-dot"
                        if database_available
                        else "status-dot-warning"
                    }"></span>

                    {
                        "System Online"
                        if database_available
                        else "Database Attention"
                    }

                </div>

                <div class="registry-version">
                    {APP_PLATFORM}
                </div>

                <div class="registry-version">
                    Version {APP_VERSION}
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


render_header()


# ============================================================
# SIDEBAR MODEL REGISTRY
# ============================================================

MODEL_REGISTRY: dict[str, Any] = {}

if Citizen is not None:
    MODEL_REGISTRY["citizens"] = Citizen

if Household is not None:
    MODEL_REGISTRY["households"] = Household

if CivilEvent is not None:
    MODEL_REGISTRY["civil_events"] = CivilEvent

if Document is not None:
    MODEL_REGISTRY["documents"] = Document

if VoterRecord is not None:
    MODEL_REGISTRY["voter_records"] = VoterRecord

if AdministrativeUnit is not None:
    MODEL_REGISTRY["administrative_units"] = (
        AdministrativeUnit
    )

if AuditLog is not None:
    MODEL_REGISTRY["audit_logs"] = AuditLog


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

def sidebar_navigation() -> None:

    with st.sidebar:

        st.markdown(
            f"""
            <div class="sidebar-title">
                {APP_NAME}
            </div>

            <div class="sidebar-subtitle">
                National Population • Civil Registration •
                Identity • Elections
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------
        # REGISTRY
        # ----------------------------------------------------

        st.markdown(
            '<div class="sidebar-section">Registry</div>',
            unsafe_allow_html=True,
        )

        registry_items = [
            (
                "overview",
                "Overview",
            ),
            (
                "citizens",
                "Citizens",
            ),
            (
                "households",
                "Households",
            ),
            (
                "civil_events",
                "Civil Registration",
            ),
            (
                "documents",
                "Identity & Documents",
            ),
            (
                "voter_records",
                "Elections",
            ),
            (
                "administrative_units",
                "Administrative Units",
            ),
        ]

        for key, label in registry_items:

            if (
                key != "overview"
                and key not in MODEL_REGISTRY
            ):
                continue

            if st.button(
                label,
                key=f"sidebar_{key}",
                use_container_width=True,
            ):

                st.session_state.active_module = key

                st.rerun()

        # ----------------------------------------------------
        # OPERATIONS
        # ----------------------------------------------------

        st.markdown(
            '<div class="sidebar-section">Operations</div>',
            unsafe_allow_html=True,
        )

        operation_items = [
            (
                "search",
                "Global Search",
            ),
            (
                "reports",
                "Reports & Analytics",
            ),
            (
                "verification",
                "Verification",
            ),
        ]

        for key, label in operation_items:

            if st.button(
                label,
                key=f"sidebar_operation_{key}",
                use_container_width=True,
            ):

                st.session_state.active_module = key

                st.rerun()

        # ----------------------------------------------------
        # ADMINISTRATION
        # ----------------------------------------------------

        st.markdown(
            '<div class="sidebar-section">Administration</div>',
            unsafe_allow_html=True,
        )

        admin_items = [
            (
                "administration",
                "Administration",
            ),
            (
                "audit_logs",
                "Audit & Activity",
            ),
            (
                "system_settings",
                "System Settings",
            ),
        ]

        for key, label in admin_items:

            if (
                key == "audit_logs"
                and key not in MODEL_REGISTRY
            ):
                continue

            if st.button(
                label,
                key=f"sidebar_admin_{key}",
                use_container_width=True,
            ):

                st.session_state.active_module = key

                st.rerun()

        # ----------------------------------------------------
        # OTHER FEATURES
        # ----------------------------------------------------

        st.markdown(
            '<div class="sidebar-section">Other Features</div>',
            unsafe_allow_html=True,
        )

        other_items = [
            (
                "statistics",
                "Statistics",
            ),
            (
                "help",
                "Help & Information",
            ),
        ]

        for key, label in other_items:

            if st.button(
                label,
                key=f"sidebar_other_{key}",
                use_container_width=True,
            ):

                st.session_state.active_module = key

                st.rerun()

        # ----------------------------------------------------
        # DATABASE STATUS
        # ----------------------------------------------------

        st.divider()

        if database_available:

            st.success(
                "Database Connected"
            )

        else:

            st.warning(
                "Database Attention Required"
            )

            st.caption(
                "The Registry interface is available, "
                "but database operations are disabled."
            )

        # ----------------------------------------------------
        # THEME
        # ----------------------------------------------------

        st.divider()

        theme_label = (
            "Use Light Theme"
            if st.session_state.dark_mode
            else "Use Dark Theme"
        )

        if st.button(
            theme_label,
            use_container_width=True,
        ):

            st.session_state.dark_mode = (
                not st.session_state.dark_mode
            )

            st.rerun()

        if st.button(
            "Refresh Application",
            use_container_width=True,
        ):

            st.rerun()


sidebar_navigation()


# ============================================================
# DATABASE SESSION
# ============================================================

def get_db_session() -> Session:

    if not database_available:

        raise RuntimeError(
            "Database is not available."
        )

    factory = get_session_factory()

    session = factory()

    return session


# ============================================================
# AUDIT LOG
# ============================================================

def create_audit_log(
    session: Session,
    action: str,
    entity_type: str,
    entity_id: str | None,
    details: str | None = None,
) -> None:

    if AuditLog is None:
        return

    try:

        audit = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            username="streamlit",
            details=details,
        )

        session.add(audit)

    except Exception:

        logger.exception(
            "Unable to create audit log."
        )


# ============================================================
# DATABASE COUNT
# ============================================================

def count_records(model: Any) -> int:

    if not database_available:
        return 0

    session: Session | None = None

    try:

        session = get_db_session()

        result = session.query(model).count()

        return int(result)

    except Exception:

        logger.exception(
            "Unable to count records for %s.",
            model,
        )

        return 0

    finally:

        if session is not None:
            session.close()


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
                Centralized management platform for national
                population records, civil registration,
                identity management, households and
                electoral registration.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # KPI COUNTS
    # --------------------------------------------------------

    population_count = (
        count_records(Citizen)
        if Citizen is not None
        else 0
    )

    civil_count = (
        count_records(CivilEvent)
        if CivilEvent is not None
        else 0
    )

    identity_count = (
        count_records(Document)
        if Document is not None
        else 0
    )

    election_count = (
        count_records(VoterRecord)
        if VoterRecord is not None
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
            <div class="kpi-card">

                <div class="kpi-label">
                    Registered Population
                </div>

                <div class="kpi-value">
                    {population_count:,}
                </div>

                <div class="kpi-description">
                    Population records
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            f"""
            <div class="kpi-card">

                <div class="kpi-label">
                    Civil Records
                </div>

                <div class="kpi-value">
                    {civil_count:,}
                </div>

                <div class="kpi-description">
                    Birth, death and civil events
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:

        st.markdown(
            f"""
            <div class="kpi-card">

                <div class="kpi-label">
                    Identity Records
                </div>

                <div class="kpi-value">
                    {identity_count:,}
                </div>

                <div class="kpi-description">
                    National identity records
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:

        st.markdown(
            f"""
            <div class="kpi-card">

                <div class="kpi-label">
                    Election Records
                </div>

                <div class="kpi-value">
                    {election_count:,}
                </div>

                <div class="kpi-description">
                    Electoral records
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # SERVICES
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "Registry Services"
    )

    services = [
        (
            "Population Registry",
            "Manage national population records, households, "
            "persons and demographic information.",
        ),
        (
            "Elections",
            "Manage electoral registration, voter records "
            "and election administration.",
        ),
        (
            "Civil Registration",
            "Register births, deaths, marriages, certificates "
            "and other civil events.",
        ),
        (
            "Identity Management",
            "Manage national identity registration, "
            "identification records and identity services.",
        ),
        (
            "Reports & Analytics",
            "Generate operational reports, statistical "
            "summaries and Registry analytics.",
        ),
        (
            "Administration",
            "Manage users, roles, permissions, configuration "
            "and system administration.",
        ),
    ]

    for index in range(
        0,
        len(services),
        2,
    ):

        cols = st.columns(2)

        for offset, column in enumerate(cols):

            service_index = index + offset

            if service_index >= len(services):
                continue

            name, description = services[
                service_index
            ]

            with column:

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

    # --------------------------------------------------------
    # SYSTEM STATUS
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "System Status"
    )

    if database_available:

        st.success(
            "Database Connected"
        )

        st.caption(
            "Registry interface and database services are available."
        )

    else:

        st.warning(
            "Database Attention Required"
        )

        st.caption(
            "The Registry interface is running without "
            "a connected database."
        )

        if database_error is not None:

            with st.expander(
                "Database technical details"
            ):

                st.exception(
                    database_error
                )


# ============================================================
# COLUMN EDITOR
# ============================================================

def render_column_input(
    column: Any,
    value: Any,
    key_prefix: str,
    allow_edit: bool = True,
) -> Any:
    """
    Render an appropriate Streamlit widget based on SQLAlchemy
    column type.
    """

    column_name = column.name
    widget_key = (
        f"{key_prefix}_{column_name}"
    )

    label = humanize(
        column_name
    )

    disabled = not allow_edit

    # --------------------------------------------------------
    # BOOLEAN
    # --------------------------------------------------------

    if is_boolean_column(column):

        return st.checkbox(
            label,
            value=(
                bool(value)
                if value is not None
                else False
            ),
            key=widget_key,
            disabled=disabled,
        )

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    if is_date_column(column):

        if isinstance(
            value,
            datetime,
        ):

            default_value = value.date()

        elif isinstance(
            value,
            date,
        ):

            default_value = value

        else:

            default_value = date.today()

        return st.date_input(
            label,
            value=default_value,
            key=widget_key,
            disabled=disabled,
        )

    # --------------------------------------------------------
    # DATETIME
    # --------------------------------------------------------

    if is_datetime_column(column):

        if isinstance(
            value,
            datetime,
        ):

            default_value = value

        else:

            default_value = datetime.now()

        return st.datetime_input(
            label,
            value=default_value,
            key=widget_key,
            disabled=disabled,
        )

    # --------------------------------------------------------
    # INTEGER
    # --------------------------------------------------------

    if is_integer_column(column):

        try:

            numeric_value = (
                int(value)
                if value is not None
                else 0
            )

        except Exception:

            numeric_value = 0

        return st.number_input(
            label,
            value=numeric_value,
            step=1,
            key=widget_key,
            disabled=disabled,
        )

    # --------------------------------------------------------
    # FLOAT
    # --------------------------------------------------------

    if is_float_column(column):

        try:

            numeric_value = (
                float(value)
                if value is not None
                else 0.0
            )

        except Exception:

            numeric_value = 0.0

        return st.number_input(
            label,
            value=numeric_value,
            step=0.1,
            key=widget_key,
            key=widget_key,
            disabled=disabled,
        )

    # --------------------------------------------------------
    # TEXT
    # --------------------------------------------------------

    text_value = (
        ""
        if value is None
        else str(value)
    )

    is_long_text = (
        get_column_type_name(column)
        == "text"
        or len(text_value) > 180
    )

    if is_long_text:

        return st.text_area(
            label,
            value=text_value,
            key=widget_key,
            disabled=disabled,
        )

    return st.text_input(
        label,
        value=text_value,
        key=widget_key,
        disabled=disabled,
    )


# ============================================================
# NORMALIZE INPUT
# ============================================================

def normalize_input(
    column: Any,
    value: Any,
) -> Any:
    """
    Convert Streamlit widget output into a value SQLAlchemy
    can persist.
    """

    if value is None:
        return None

    # --------------------------------------------------------
    # STRING
    # --------------------------------------------------------

    if is_text_column(column):

        if isinstance(value, str):

            cleaned = value.strip()

            if cleaned == "":
                return None

            return cleaned

        return str(value)

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    if is_date_column(column):

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        return None

    # --------------------------------------------------------
    # DATETIME
    # --------------------------------------------------------

    if is_datetime_column(column):

        if isinstance(value, datetime):
            return value

        return None

    # --------------------------------------------------------
    # INTEGER
    # --------------------------------------------------------

    if is_integer_column(column):

        return int(value)

    # --------------------------------------------------------
    # FLOAT
    # --------------------------------------------------------

    if is_float_column(column):

        return float(value)

    # --------------------------------------------------------
    # BOOLEAN
    # --------------------------------------------------------

    if is_boolean_column(column):

        return bool(value)

    return value


# ============================================================
# CREATE RECORD
# ============================================================

def render_create_form(
    model: Any,
) -> None:

    st.subheader(
        f"Add {model_label(model)}"
    )

    columns = get_model_columns(
        model
    )

    primary_keys = {
        column.name
        for column in get_primary_keys(
            model
        )
    }

    with st.form(
        key=f"create_{model.__name__}",
        clear_on_submit=True,
    ):

        values: dict[str, Any] = {}

        for index, column in enumerate(columns):

            # ------------------------------------------------
            # AUTO INTEGER PRIMARY KEY
            # ------------------------------------------------

            if (
                column.primary_key
                and is_integer_column(column)
                and column.autoincrement
            ):

                continue

            # ------------------------------------------------
            # AUTO STRING PRIMARY KEY
            # ------------------------------------------------

            if (
                column.primary_key
                and is_text_column(column)
            ):

                generated_id = str(
                    uuid.uuid4()
                )

                values[
                    column.name
                ] = generated_id

                st.text_input(
                    humanize(
                        column.name
                    ),
                    value=generated_id,
                    disabled=True,
                    key=(
                        f"create_preview_"
                        f"{model.__name__}_"
                        f"{column.name}"
                    ),
                )

                continue

            # ------------------------------------------------
            # DEFAULT CREATED/UPDATED FIELDS
            # ------------------------------------------------

            if column.name in {
                "created_at",
                "updated_at",
                "verified_at",
            }:

                if column.default is not None:

                    st.caption(
                        f"{humanize(column.name)} "
                        "will be generated automatically."
                    )

                    continue

            default_value = None

            if column.default is not None:

                try:

                    if callable(
                        column.default.arg
                    ):

                        default_value = (
                            column.default.arg()
                        )

                    else:

                        default_value = (
                            column.default.arg
                        )

                except Exception:

                    default_value = None

            values[
                column.name
            ] = render_column_input(
                column,
                default_value,
                f"create_{model.__name__}_{index}",
            )

        submitted = st.form_submit_button(
            "Create Record",
            use_container_width=True,
        )

    if not submitted:
        return

    # --------------------------------------------------------
    # BUILD OBJECT
    # --------------------------------------------------------

    session: Session | None = None

    try:

        session = get_db_session()

        payload: dict[str, Any] = {}

        for column in columns:

            name = column.name

            if (
                column.primary_key
                and is_integer_column(column)
                and column.autoincrement
            ):
                continue

            if name in {
                "created_at",
                "updated_at",
                "verified_at",
            }:
                continue

            if name not in values:
                continue

            payload[
                name
            ] = normalize_input(
                column,
                values[name],
            )

        # Ensure string PK exists.
        for column in get_primary_keys(model):

            if (
                is_text_column(column)
                and column.name not in payload
            ):

                payload[
                    column.name
                ] = str(
                    uuid.uuid4()
                )

        record = model(
            **payload
        )

        session.add(
            record
        )

        session.flush()

        record_id = get_record_identifier(
            record
        )

        create_audit_log(
            session=session,
            action="CREATE",
            entity_type=model.__name__,
            entity_id=record_id,
            details=(
                f"Created {model_label(model)} "
                f"record."
            ),
        )

        session.commit()

        st.success(
            f"{model_label(model)} record created successfully."
        )

        st.rerun()

    except IntegrityError as exc:

        if session is not None:
            session.rollback()

        st.error(
            "The record could not be created because "
            "a database constraint was violated."
        )

        with st.expander(
            "Database details"
        ):

            st.exception(exc)

    except Exception as exc:

        if session is not None:
            session.rollback()

        logger.exception(
            "Create operation failed."
        )

        st.error(
            "The record could not be created."
        )

        with st.expander(
            "Technical details"
        ):

            st.exception(exc)

    finally:

        if session is not None:
            session.close()


# ============================================================
# RECORD IDENTIFIER
# ============================================================

def get_record_identifier(
    record: Any,
) -> str:

    primary_keys = get_primary_keys(
        type(record)
    )

    values = []

    for column in primary_keys:

        values.append(
            safe_string(
                getattr(
                    record,
                    column.name,
                    None,
                )
            )
        )

    return ":".join(
        values
    )


# ============================================================
# RECORD QUERY
# ============================================================

def query_records(
    model: Any,
    search_term: str = "",
    limit: int = 25,
    offset: int = 0,
) -> tuple[list[Any], int]:

    session: Session | None = None

    try:

        session = get_db_session()

        stmt = select(model)

        columns = get_model_columns(
            model
        )

        if search_term.strip():

            search_value = (
                f"%{search_term.strip()}%"
            )

            search_conditions = []

            for column in columns:

                if is_text_column(column):

                    search_conditions.append(
                        column.ilike(
                            search_value
                        )
                    )

            if search_conditions:

                from sqlalchemy import or_

                stmt = stmt.where(
                    or_(
                        *search_conditions
                    )
                )

        primary_keys = get_primary_keys(
            model
        )

        if primary_keys:

            stmt = stmt.order_by(
                primary_keys[0]
            )

        total_stmt = select(
            __import__("sqlalchemy").func.count()
        ).select_from(
            stmt.subquery()
        )

        total = int(
            session.execute(
                total_stmt
            ).scalar_one()
        )

        stmt = (
            stmt
            .offset(offset)
            .limit(limit)
        )

        records = list(
            session.execute(
                stmt
            ).scalars().all()
        )

        return records, total

    finally:

        if session is not None:
            session.close()


# ============================================================
# RECORD TABLE
# ============================================================

def render_record_table(
    model: Any,
    records: list[Any],
) -> None:

    if not records:

        st.info(
            "No records found."
        )

        return

    columns = get_model_columns(
        model
    )

    rows: list[dict[str, Any]] = []

    for record in records:

        row: dict[str, Any] = {}

        for column in columns:

            value = getattr(
                record,
                column.name,
                None,
            )

            row[
                humanize(column.name)
            ] = format_value(
                value
            )

        rows.append(
            row
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# GET RECORD BY ID
# ============================================================

def get_record_by_identifier(
    model: Any,
    identifier: str,
) -> Any | None:

    session: Session | None = None

    try:

        session = get_db_session()

        primary_keys = get_primary_keys(
            model
        )

        if not primary_keys:
            return None

        if len(primary_keys) == 1:

            column = primary_keys[0]

            value: Any = identifier

            if is_integer_column(column):

                value = int(identifier)

            return session.get(
                model,
                value,
            )

        # Composite primary key.
        parts = identifier.split(":")

        if len(parts) != len(
            primary_keys
        ):

            return None

        conditions = []

        for column, value in zip(
            primary_keys,
            parts,
        ):

            if is_integer_column(column):

                value = int(value)

            conditions.append(
                column == value
            )

        stmt = select(
            model
        ).where(
            *conditions
        )

        return session.execute(
            stmt
        ).scalars().first()

    except Exception:

        logger.exception(
            "Unable to retrieve record."
        )

        return None

    finally:

        if session is not None:
            session.close()


# ============================================================
# EDIT RECORD
# ============================================================

def render_edit_form(
    model: Any,
    identifier: str,
) -> None:

    session: Session | None = None

    try:

        session = get_db_session()

        primary_keys = get_primary_keys(
            model
        )

        if not primary_keys:

            st.error(
                "This model does not have a primary key."
            )

            return

        record = get_record_by_identifier(
            model,
            identifier,
        )

        if record is None:

            st.error(
                "The selected record could not be found."
            )

            return

        st.subheader(
            f"Edit {model_label(model)}"
        )

        st.caption(
            f"Record ID: {identifier}"
        )

        columns = get_model_columns(
            model
        )

        with st.form(
            key=(
                f"edit_"
                f"{model.__name__}_"
                f"{identifier}"
            )
        ):

            values: dict[str, Any] = {}

            for index, column in enumerate(
                columns
            ):

                current_value = getattr(
                    record,
                    column.name,
                    None,
                )

                # --------------------------------------------
                # PRIMARY KEY
                # --------------------------------------------

                if column.primary_key:

                    st.text_input(
                        humanize(
                            column.name
                        ),
                        value=format_value(
                            current_value
                        ),
                        disabled=True,
                        key=(
                            f"edit_pk_"
                            f"{model.__name__}_"
                            f"{identifier}_"
                            f"{column.name}"
                        ),
                    )

                    continue

                # --------------------------------------------
                # CREATED AT
                # --------------------------------------------

                if column.name == "created_at":

                    st.text_input(
                        humanize(
                            column.name
                        ),
                        value=format_value(
                            current_value
                        ),
                        disabled=True,
                        key=(
                            f"edit_created_"
                            f"{model.__name__}_"
                            f"{identifier}"
                        ),
                    )

                    continue

                values[
                    column.name
                ] = render_column_input(
                    column,
                    current_value,
                    (
                        f"edit_"
                        f"{model.__name__}_"
                        f"{identifier}_"
                        f"{index}"
                    ),
                )

            save_col, cancel_col = st.columns(
                2
            )

            with save_col:

                save_clicked = st.form_submit_button(
                    "Save Changes",
                    use_container_width=True,
                )

            with cancel_col:

                cancel_clicked = st.form_submit_button(
                    "Cancel",
                    use_container_width=True,
                )

        if cancel_clicked:

            st.session_state.pop(
                "editing_record",
                None,
            )

            st.rerun()

        if not save_clicked:
            return

        # ----------------------------------------------------
        # UPDATE RECORD
        # ----------------------------------------------------

        for column in columns:

            name = column.name

            if (
                column.primary_key
                or name == "created_at"
            ):
                continue

            if name not in values:
                continue

            normalized = normalize_input(
                column,
                values[name],
            )

            setattr(
                record,
                name,
                normalized,
            )

        if hasattr(
            record,
            "updated_at",
        ):

            record.updated_at = (
                datetime.utcnow()
            )

        create_audit_log(
            session=session,
            action="UPDATE",
            entity_type=model.__name__,
            entity_id=identifier,
            details=(
                f"Updated {model_label(model)} "
                f"record."
            ),
        )

        session.commit()

        st.session_state.pop(
            "editing_record",
            None,
        )

        st.success(
            "Record updated successfully."
        )

        st.rerun()

    except IntegrityError as exc:

        if session is not None:
            session.rollback()

        st.error(
            "The record could not be updated because "
            "a database constraint was violated."
        )

        with st.expander(
            "Database details"
        ):

            st.exception(exc)

    except Exception as exc:

        if session is not None:
            session.rollback()

        logger.exception(
            "Update operation failed."
        )

        st.error(
            "The record could not be updated."
        )

        with st.expander(
            "Technical details"
        ):

            st.exception(exc)

    finally:

        if session is not None:
            session.close()


# ============================================================
# DELETE RECORD
# ============================================================

def delete_record(
    model: Any,
    identifier: str,
) -> bool:

    session: Session | None = None

    try:

        session = get_db_session()

        record = get_record_by_identifier(
            model,
            identifier,
        )

        if record is None:

            st.error(
                "The record could not be found."
            )

            return False

        session.delete(
            record
        )

        create_audit_log(
            session=session,
            action="DELETE",
            entity_type=model.__name__,
            entity_id=identifier,
            details=(
                f"Deleted {model_label(model)} "
                f"record."
            ),
        )

        session.commit()

        return True

    except IntegrityError as exc:

        if session is not None:
            session.rollback()

        st.error(
            "The record could not be deleted because "
            "other records depend on it."
        )

        with st.expander(
            "Database details"
        ):

            st.exception(exc)

        return False

    except Exception as exc:

        if session is not None:
            session.rollback()

        logger.exception(
            "Delete operation failed."
        )

        st.error(
            "The record could not be deleted."
        )

        with st.expander(
            "Technical details"
        ):

            st.exception(exc)

        return False

    finally:

        if session is not None:
            session.close()


# ============================================================
# CRUD MODULE
# ============================================================

def render_crud_module(
    model: Any,
) -> None:

    label = model_label(
        model
    )

    st.markdown(
        f"""
        <div class="overview-card">

            <div class="registry-kicker">
                Registry Management
            </div>

            <div class="registry-heading">
                {label}
            </div>

            <div class="registry-description">
                View, search, create, edit and delete
                {label.lower()} records.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    if not database_available:

        st.warning(
            "Database Attention Required"
        )

        st.info(
            "The Registry interface is available, "
            "but database editing is disabled until "
            "the database connection is restored."
        )

        if database_error is not None:

            with st.expander(
                "Database technical details"
            ):

                st.exception(
                    database_error
                )

        return

    # --------------------------------------------------------
    # TABS
    # --------------------------------------------------------

    view_tab, add_tab, edit_tab, delete_tab = st.tabs(
        [
            "Records",
            "Add New",
            "Edit",
            "Delete",
        ]
    )

    # ========================================================
    # RECORDS
    # ========================================================

    with view_tab:

        search_col, page_col = st.columns(
            [4, 1]
        )

        with search_col:

            search_term = st.text_input(
                "Search",
                placeholder=(
                    f"Search {label.lower()}..."
                ),
                key=(
                    f"search_{model.__name__}"
                ),
            )

        with page_col:

            page_size = st.selectbox(
                "Records per page",
                [10, 25, 50, 100],
                index=1,
                key=(
                    f"page_size_"
                    f"{model.__name__}"
                ),
            )

        if "page" not in st.session_state:

            st.session_state.page = 1

        current_page = st.session_state.page

        offset = (
            current_page - 1
        ) * page_size

        try:

            records, total = query_records(
                model,
                search_term=search_term,
                limit=page_size,
                offset=offset,
            )

        except Exception as exc:

            st.error(
                "Unable to load registry records."
            )

            with st.expander(
                "Technical details"
            ):

                st.exception(exc)

            return

        total_pages = max(
            1,
            (
                total + page_size - 1
            ) // page_size,
        )

        if current_page > total_pages:

            st.session_state.page = (
                total_pages
            )

            st.rerun()

        st.caption(
            f"Showing {len(records)} of "
            f"{total:,} records"
        )

        render_record_table(
            model,
            records,
        )

        if total_pages > 1:

            previous_col, page_info_col, next_col = (
                st.columns(
                    [1, 2, 1]
                )
            )

            with previous_col:

                if st.button(
                    "Previous",
                    disabled=(
                        current_page <= 1
                    ),
                    key=(
                        f"previous_"
                        f"{model.__name__}"
                    ),
                    use_container_width=True,
                ):

                    st.session_state.page -= 1

                    st.rerun()

            with page_info_col:

                st.markdown(
                    f"""
                    <div style="text-align:center;">
                        Page {current_page}
                        of {total_pages}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with next_col:

                if st.button(
                    "Next",
                    disabled=(
                        current_page >= total_pages
                    ),
                    key=(
                        f"next_"
                        f"{model.__name__}"
                    ),
                    use_container_width=True,
                ):

                    st.session_state.page += 1

                    st.rerun()

    # ========================================================
    # ADD
    # ========================================================

    with add_tab:

        render_create_form(
            model
        )

    # ========================================================
    # EDIT
    # ========================================================

    with edit_tab:

        primary_keys = get_primary_keys(
            model
        )

        if not primary_keys:

            st.error(
                "This model cannot be edited because "
                "it has no primary key."
            )

        else:

            records, total = query_records(
                model,
                limit=500,
                offset=0,
            )

            if not records:

                st.info(
                    "There are no records to edit."
                )

            else:

                record_options = {}

                for record in records:

                    identifier = (
                        get_record_identifier(
                            record
                        )
                    )

                    record_options[
                        identifier
                    ] = record

                selected_id = st.selectbox(
                    "Select record to edit",
                    list(
                        record_options.keys()
                    ),
                    key=(
                        f"edit_selector_"
                        f"{model.__name__}"
                    ),
                )

                selected_record = (
                    record_options[
                        selected_id
                    ]
                )

                st.caption(
                    f"Selected record: {selected_id}"
                )

                render_edit_form(
                    model,
                    selected_id,
                )

    # ========================================================
    # DELETE
    # ========================================================

    with delete_tab:

        primary_keys = get_primary_keys(
            model
        )

        if not primary_keys:

            st.error(
                "This model cannot be deleted because "
                "it has no primary key."
            )

        else:

            records, total = query_records(
                model,
                limit=500,
                offset=0,
            )

            if not records:

                st.info(
                    "There are no records to delete."
                )

            else:

                delete_options = {}

                for record in records:

                    identifier = (
                        get_record_identifier(
                            record
                        )
                    )

                    delete_options[
                        identifier
                    ] = record

                selected_id = st.selectbox(
                    "Select record to delete",
                    list(
                        delete_options.keys()
                    ),
                    key=(
                        f"delete_selector_"
                        f"{model.__name__}"
                    ),
                )

                st.warning(
                    "Deleting a registry record is "
                    "a permanent database operation."
                )

                confirm = st.checkbox(
                    "I understand that this record will be permanently deleted.",
                    key=(
                        f"confirm_delete_"
                        f"{model.__name__}"
                    ),
                )

                if st.button(
                    "Delete Record",
                    type="primary",
                    disabled=not confirm,
                    key=(
                        f"delete_button_"
                        f"{model.__name__}"
                    ),
                    use_container_width=True,
                ):

                    if delete_record(
                        model,
                        selected_id,
                    ):

                        st.success(
                            "Record deleted successfully."
                        )

                        st.rerun()


# ============================================================
# GLOBAL SEARCH
# ============================================================

def render_global_search() -> None:

    st.title(
        "Global Registry Search"
    )

    st.caption(
        "Search across registry entities."
    )

    if not database_available:

        st.warning(
            "Database Attention Required"
        )

        return

    search_term = st.text_input(
        "Search registry",
        placeholder=(
            "Enter a name, number, code or reference..."
        ),
    )

    if not search_term.strip():

        st.info(
            "Enter a search term to begin."
        )

        return

    for key, model in MODEL_REGISTRY.items():

        if model is AuditLog:

            continue

        try:

            records, total = query_records(
                model,
                search_term=search_term,
                limit=10,
                offset=0,
            )

        except Exception:

            continue

        if not records:
            continue

        st.subheader(
            model_label(model)
        )

        render_record_table(
            model,
            records,
        )

        if total > len(records):

            st.caption(
                f"{total:,} matching records found."
            )


# ============================================================
# REPORTS
# ============================================================

def render_reports() -> None:

    st.title(
        "Reports & Analytics"
    )

    st.caption(
        "Registry operational statistics."
    )

    if not database_available:

        st.warning(
            "Database Attention Required"
        )

        return

    report_rows = []

    for key, model in MODEL_REGISTRY.items():

        if model is AuditLog:
            continue

        report_rows.append(
            {
                "Registry Entity": model_label(model),
                "Records": count_records(model),
            }
        )

    if report_rows:

        st.dataframe(
            report_rows,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No registry entities are available."
        )


# ============================================================
# STATISTICS
# ============================================================

def render_statistics() -> None:

    st.title(
        "Registry Statistics"
    )

    if not database_available:

        st.warning(
            "Database Attention Required"
        )

        return

    cols = st.columns(
        min(
            4,
            max(
                1,
                len(MODEL_REGISTRY),
            ),
        )
    )

    index = 0

    for key, model in MODEL_REGISTRY.items():

        if model is AuditLog:
            continue

        with cols[
            index % len(cols)
        ]:

            st.metric(
                model_label(model),
                f"{count_records(model):,}",
            )

        index += 1


# ============================================================
# VERIFICATION
# ============================================================

def render_verification() -> None:

    st.title(
        "Verification"
    )

    st.caption(
        "Review registry verification status."
    )

    if Citizen is None:

        st.info(
            "Citizen model is not available."
        )

        return

    if not database_available:

        st.warning(
            "Database Attention Required"
        )

        return

    session: Session | None = None

    try:

        session = get_db_session()

        stmt = select(
            Citizen
        ).order_by(
            Citizen.updated_at.desc()
        )

        records = list(
            session.execute(
                stmt.limit(100)
            ).scalars().all()
        )

        if not records:

            st.info(
                "No citizen records are available for verification."
            )

            return

        rows = []

        for citizen in records:

            rows.append(
                {
                    "ID": citizen.id,
                    "National ID": citizen.national_id,
                    "Full Name": citizen.full_name,
                    "Status": citizen.verification_status,
                    "Verified By": citizen.verified_by,
                    "Verified At": format_value(
                        citizen.verified_at
                    ),
                }
            )

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )

    except Exception as exc:

        st.error(
            "Unable to load verification records."
        )

        with st.expander(
            "Technical details"
        ):

            st.exception(exc)

    finally:

        if session is not None:
            session.close()


# ============================================================
# ADMINISTRATION
# ============================================================

def render_administration() -> None:

    st.title(
        "Administration"
    )

    st.caption(
        "System administration and registry configuration."
    )

    st.info(
        "Administrative user, role and permission management "
        "can be connected here when the corresponding "
        "authentication models are enabled."
    )

    st.subheader(
        "Available Database Models"
    )

    rows = []

    for key, model in MODEL_REGISTRY.items():

        rows.append(
            {
                "Model": model.__name__,
                "Registry Area": model_label(model),
                "Records": count_records(model),
            }
        )

    if rows:

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# SYSTEM SETTINGS
# ============================================================

def render_system_settings() -> None:

    st.title(
        "System Settings"
    )

    st.caption(
        "Application configuration."
    )

    st.subheader(
        "Interface"
    )

    dark_mode = st.toggle(
        "Dark Mode",
        value=st.session_state.dark_mode,
    )

    if dark_mode != st.session_state.dark_mode:

        st.session_state.dark_mode = dark_mode

        st.rerun()

    st.subheader(
        "Application"
    )

    st.write(
        f"Application: {APP_NAME}"
    )

    st.write(
        f"Platform: {APP_PLATFORM}"
    )

    st.write(
        f"Version: {APP_VERSION}"
    )

    st.write(
        f"Database: "
        f"{'Connected' if database_available else 'Attention Required'}"
    )


# ============================================================
# HELP
# ============================================================

def render_help() -> None:

    st.title(
        "Help & Information"
    )

    st.markdown(
        """
        ### South Sudan National Registry

        The Registry Platform provides centralized management
        of population, civil registration, identity,
        household and electoral information.

        ### Record management

        Registry modules provide:

        - View records
        - Search records
        - Add records
        - Edit records
        - Delete records

        ### Data governance

        Registry data should be treated as authoritative only
        after appropriate verification and administrative
        approval.

        Database changes should be performed by authorized
        personnel.
        """
    )


# ============================================================
# ACTIVE MODULE
# ============================================================

active_module = st.session_state.active_module


# ============================================================
# OVERVIEW
# ============================================================

if active_module == "overview":

    render_overview()


# ============================================================
# CRUD MODULES
# ============================================================

elif active_module in MODEL_REGISTRY:

    render_crud_module(
        MODEL_REGISTRY[
            active_module
        ]
    )


# ============================================================
# SEARCH
# ============================================================

elif active_module == "search":

    render_global_search()


# ============================================================
# REPORTS
# ============================================================

elif active_module == "reports":

    render_reports()


# ============================================================
# VERIFICATION
# ============================================================

elif active_module == "verification":

    render_verification()


# ============================================================
# ADMINISTRATION
# ============================================================

elif active_module == "administration":

    render_administration()


# ============================================================
# SYSTEM SETTINGS
# ============================================================

elif active_module == "system_settings":

    render_system_settings()


# ============================================================
# STATISTICS
# ============================================================

elif active_module == "statistics":

    render_statistics()


# ============================================================
# HELP
# ============================================================

elif active_module == "help":

    render_help()


# ============================================================
# FALLBACK
# ============================================================

else:

    st.session_state.active_module = (
        "overview"
    )

    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

footer_col1, footer_col2 = st.columns(
    2
)

with footer_col1:

    st.markdown(
        f"""
        <div class="registry-footer">
            {APP_NAME} • {APP_PLATFORM} • Version {APP_VERSION}
        </div>
        """,
        unsafe_allow_html=True,
    )

with footer_col2:

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
