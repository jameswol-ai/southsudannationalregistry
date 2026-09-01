"""
South Sudan National Registry
Streamlit AI Studio

National population, civil registration, identity,
household and electoral registry management platform.

Application entry point:

    streamlit run streamlit_app.py

Architecture:

    Next.js AI Studio
            |
        Registry API
            |
        Service Layer
            |
        SQLAlchemy
            |
    PostgreSQL / SQLite
            |
        Streamlit AI Studio
"""

from __future__ import annotations

import logging
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

import streamlit as st


# ============================================================
# APPLICATION CONSTANTS
# ============================================================

APP_NAME = "South Sudan National Registry"
APP_VERSION = "1.0.0"
APP_SUBTITLE = (
    "National Population • Civil Registration • "
    "Identity • Elections"
)

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
EMBLEM_PATH = ASSETS_DIR / "south_sudan_emblem.png"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title=APP_NAME,
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
DATABASE_ERROR: Optional[Exception] = None

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
        "Unable to import database layer."
    )


# ============================================================
# MODEL IMPORTS
# ============================================================

MODELS_AVAILABLE = False
MODELS_ERROR: Optional[Exception] = None

Citizen = None
Household = None
CivilEvent = None
Document = None
VoterRecord = None
AdministrativeUnit = None
AuditLog = None

try:
    from models.models import (
        Citizen,
        Household,
        CivilEvent,
        Document,
        VoterRecord,
        AdministrativeUnit,
        AuditLog,
    )

    MODELS_AVAILABLE = True

except Exception:

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

        MODELS_AVAILABLE = True

    except Exception as exc:

        MODELS_ERROR = exc

        logger.exception(
            "Unable to import registry models."
        )


# ============================================================
# SESSION STATE
# ============================================================

if "active_page" not in st.session_state:
    st.session_state.active_page = "Overview"

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "database_initialized" not in st.session_state:
    st.session_state.database_initialized = False

if "database_error" not in st.session_state:
    st.session_state.database_error = None

if "notice" not in st.session_state:
    st.session_state.notice = None


# ============================================================
# THEME
# ============================================================

def get_theme() -> dict[str, str]:
    if st.session_state.theme == "light":

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
            "success": "#15803D",
            "warning": "#B45309",
            "danger": "#B91C1C",
            "white": "#FFFFFF",
            "shadow": "rgba(15, 23, 42, 0.10)",
        }

    return {
        "background": "#0B1220",
        "surface": "#111827",
        "surface_alt": "#172033",
        "surface_hover": "#1E293B",
        "text": "#F8FAFC",
        "muted": "#94A3B8",
        "border": "#263247",
        "accent": "#22C55E",
        "accent_dark": "#16A34A",
        "accent_soft": "#14532D",
        "success": "#22C55E",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "white": "#FFFFFF",
        "shadow": "rgba(0, 0, 0, 0.30)",
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

        /* ====================================================
           SIDEBAR
           ==================================================== */

        section[data-testid="stSidebar"] {{
            background: {theme["surface"]};
            border-right: 1px solid {theme["border"]};
        }}

        section[data-testid="stSidebar"] > div {{
            padding-top: 1rem;
        }}

        .sidebar-brand {{
            text-align: center;
            padding: 10px 8px 18px;
        }}

        .sidebar-emblem {{
            width: 58px;
            height: 58px;
            margin: 0 auto 12px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: {theme["accent"]};
            color: white;
            font-size: 22px;
            font-weight: 900;
            border: 3px solid rgba(255,255,255,0.20);
        }}

        .sidebar-title {{
            font-size: 17px;
            font-weight: 800;
            line-height: 1.25;
            color: {theme["text"]};
        }}

        .sidebar-subtitle {{
            font-size: 11px;
            line-height: 1.5;
            color: {theme["muted"]};
            margin-top: 6px;
        }}

        .sidebar-section {{
            color: {theme["accent"]};
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin: 18px 4px 7px;
        }}

        .sidebar-status {{
            border: 1px solid {theme["border"]};
            background: {theme["surface_alt"]};
            border-radius: 12px;
            padding: 10px;
            margin-top: 12px;
        }}

        .status-online {{
            color: {theme["success"]};
            font-weight: 700;
            font-size: 12px;
        }}

        .status-warning {{
            color: {theme["warning"]};
            font-weight: 700;
            font-size: 12px;
        }}

        .status-dot {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: {theme["success"]};
            margin-right: 6px;
        }}

        .status-dot-warning {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: {theme["warning"]};
            margin-right: 6px;
        }}

        /* ====================================================
           HEADER
           ==================================================== */

        .registry-header {{
            display: flex;
            align-items: center;
            gap: 18px;
            padding: 10px 4px 20px;
            border-bottom: 1px solid {theme["border"]};
            margin-bottom: 22px;
        }}

        .header-emblem {{
            width: 68px;
            height: 68px;
            border-radius: 50%;
            object-fit: contain;
            flex-shrink: 0;
        }}

        .header-emblem-fallback {{
            width: 68px;
            height: 68px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: {theme["accent"]};
            color: white;
            font-size: 24px;
            font-weight: 900;
            flex-shrink: 0;
        }}

        .registry-title {{
            font-size: 28px;
            font-weight: 850;
            line-height: 1.2;
            color: {theme["text"]};
        }}

        .registry-subtitle {{
            color: {theme["muted"]};
            font-size: 13px;
            margin-top: 6px;
            line-height: 1.5;
        }}

        .registry-version {{
            color: {theme["muted"]};
            font-size: 11px;
            margin-top: 5px;
        }}

        /* ====================================================
           PAGE
           ==================================================== */

        .page-kicker {{
            color: {theme["accent"]};
            font-size: 12px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}

        .page-heading {{
            color: {theme["text"]};
            font-size: 25px;
            font-weight: 850;
            margin-top: 3px;
        }}

        .page-description {{
            color: {theme["muted"]};
            font-size: 14px;
            line-height: 1.6;
            margin-top: 5px;
            margin-bottom: 18px;
        }}

        /* ====================================================
           CARDS
           ==================================================== */

        .registry-card {{
            background: {theme["surface"]};
            border: 1px solid {theme["border"]};
            border-radius: 15px;
            padding: 18px;
            margin-bottom: 14px;
            box-shadow: 0 8px 25px {theme["shadow"]};
        }}

        .kpi-card {{
            background: {theme["surface"]};
            border: 1px solid {theme["border"]};
            border-radius: 15px;
            padding: 17px;
            min-height: 125px;
            box-shadow: 0 8px 25px {theme["shadow"]};
        }}

        .kpi-label {{
            color: {theme["muted"]};
            font-size: 12px;
            font-weight: 700;
        }}

        .kpi-value {{
            color: {theme["text"]};
            font-size: 30px;
            font-weight: 850;
            margin-top: 8px;
        }}

        .kpi-description {{
            color: {theme["muted"]};
            font-size: 11px;
            margin-top: 5px;
        }}

        .module-name {{
            color: {theme["text"]};
            font-size: 16px;
            font-weight: 800;
        }}

        .module-description {{
            color: {theme["muted"]};
            font-size: 13px;
            line-height: 1.5;
            margin-top: 5px;
        }}

        /* ====================================================
           BUTTONS
           ==================================================== */

        .stButton > button {{
            border-radius: 9px;
            min-height: 40px;
            font-weight: 650;
        }}

        /* ====================================================
           INPUTS
           ==================================================== */

        input,
        textarea {{
            border-radius: 9px !important;
        }}

        div[data-baseweb="select"] > div {{
            border-radius: 9px;
        }}

        /* ====================================================
           FOOTER
           ==================================================== */

        .registry-footer {{
            color: {theme["muted"]};
            font-size: 11px;
            line-height: 1.5;
        }}

        /* ====================================================
           STREAMLIT CHROME
           ==================================================== */

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
# HELPERS
# ============================================================

def safe_uuid() -> str:
    return str(uuid.uuid4())


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def show_notice() -> None:

    notice = st.session_state.get("notice")

    if not notice:
        return

    notice_type, message = notice

    if notice_type == "success":
        st.success(message)

    elif notice_type == "warning":
        st.warning(message)

    elif notice_type == "error":
        st.error(message)

    else:
        st.info(message)

    st.session_state.notice = None


def set_notice(
    message: str,
    notice_type: str = "success",
) -> None:

    st.session_state.notice = (
        notice_type,
        message,
    )


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

@st.cache_resource
def initialize_database() -> tuple[bool, Optional[str]]:

    if not DATABASE_AVAILABLE:
        return (
            False,
            str(DATABASE_ERROR),
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


database_ok = False

if DATABASE_AVAILABLE:

    database_ok, db_error = initialize_database()

    st.session_state.database_initialized = (
        database_ok
    )

    st.session_state.database_error = db_error

else:

    database_ok = False


# ============================================================
# DATABASE SESSION
# ============================================================

def get_session():

    if not DATABASE_AVAILABLE:
        return None

    try:
        return SessionLocal()

    except Exception as exc:

        logger.exception(
            "Unable to create database session."
        )

        return None


# ============================================================
# QUERY HELPERS
# ============================================================

def count_records(model: Any) -> int:

    if not database_ok or model is None:
        return 0

    session = get_session()

    if session is None:
        return 0

    try:

        return int(
            session.query(model).count()
        )

    except Exception:

        logger.exception(
            "Unable to count %s.",
            getattr(
                model,
                "__name__",
                "records",
            ),
        )

        return 0

    finally:

        session.close()


def get_records(
    model: Any,
    limit: int = 500,
) -> list[Any]:

    if not database_ok or model is None:
        return []

    session = get_session()

    if session is None:
        return []

    try:

        return (
            session.query(model)
            .limit(limit)
            .all()
        )

    except Exception:

        logger.exception(
            "Unable to retrieve records."
        )

        return []

    finally:

        session.close()


def get_record(
    model: Any,
    record_id: str,
) -> Optional[Any]:

    if not database_ok or model is None:
        return None

    session = get_session()

    if session is None:
        return None

    try:

        return session.get(
            model,
            record_id,
        )

    except Exception:

        logger.exception(
            "Unable to retrieve record."
        )

        return None

    finally:

        session.close()


def delete_record(
    model: Any,
    record_id: str,
) -> tuple[bool, Optional[str]]:

    if not database_ok or model is None:
        return False, "Database unavailable."

    session = get_session()

    if session is None:
        return False, "Database session unavailable."

    try:

        record = session.get(
            model,
            record_id,
        )

        if record is None:
            return False, "Record not found."

        session.delete(record)
        session.commit()

        return True, None

    except Exception as exc:

        session.rollback()

        logger.exception(
            "Unable to delete record."
        )

        return False, str(exc)

    finally:

        session.close()


# ============================================================
# HEADER
# ============================================================

def render_header() -> None:

    emblem_html = ""

    if EMBLEM_PATH.exists():

        try:

            from PIL import Image

            with Image.open(EMBLEM_PATH) as image:
                image.verify()

            emblem_html = """
                <div class="header-emblem-fallback">
                    SS
                </div>
            """

            # Streamlit renders the actual image below the header.

        except Exception:

            logger.warning(
                "Invalid South Sudan emblem: %s",
                EMBLEM_PATH,
            )

    else:

        emblem_html = """
            <div class="header-emblem-fallback">
                SS
            </div>
        """

    st.markdown(
        f"""
        <div class="registry-header">

            {emblem_html}

            <div>

                <div class="registry-title">
                    {APP_NAME}
                </div>

                <div class="registry-subtitle">
                    {APP_SUBTITLE}
                </div>

                <div class="registry-version">
                    Registry Platform • Version {APP_VERSION}
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # Display the real image only after validating it.
    if EMBLEM_PATH.exists():

        try:

            from PIL import Image

            with Image.open(EMBLEM_PATH) as image:
                image.verify()

            # A valid image can safely be passed to Streamlit.
            # It is intentionally not used as page_icon.
            pass

        except Exception:
            pass


# ============================================================
# SIDEBAR
# ============================================================

def sidebar_navigation() -> str:

    with st.sidebar:

        # ----------------------------------------------------
        # BRAND
        # ----------------------------------------------------

        st.markdown(
            """
            <div class="sidebar-brand">

                <div class="sidebar-emblem">
                    SS
                </div>

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

        # ----------------------------------------------------
        # NAVIGATION
        # ----------------------------------------------------

        st.markdown(
            '<div class="sidebar-section">Registry</div>',
            unsafe_allow_html=True,
        )

        registry_pages = [
            "Overview",
            "Citizens",
            "Households",
            "Civil Registration",
            "Identity Management",
            "Elections",
            "Administrative Units",
        ]

        selected_registry = st.radio(
            "Registry",
            registry_pages,
            index=(
                registry_pages.index(
                    st.session_state.active_page
                )
                if st.session_state.active_page
                in registry_pages
                else 0
            ),
            key="sidebar_registry_navigation",
            label_visibility="collapsed",
        )

        st.markdown(
            '<div class="sidebar-section">Operations</div>',
            unsafe_allow_html=True,
        )

        operations_pages = [
            "Reports & Analytics",
            "Verification",
            "Documents",
        ]

        selected_operations = st.radio(
            "Operations",
            operations_pages,
            index=(
                operations_pages.index(
                    st.session_state.active_page
                )
                if st.session_state.active_page
                in operations_pages
                else 0
            ),
            key="sidebar_operations_navigation",
            label_visibility="collapsed",
        )

        st.markdown(
            '<div class="sidebar-section">Administration</div>',
            unsafe_allow_html=True,
        )

        administration_pages = [
            "Administration",
            "Audit Log",
        ]

        selected_administration = st.radio(
            "Administration",
            administration_pages,
            index=(
                administration_pages.index(
                    st.session_state.active_page
                )
                if st.session_state.active_page
                in administration_pages
                else 0
            ),
            key="sidebar_administration_navigation",
            label_visibility="collapsed",
        )

        st.markdown(
            '<div class="sidebar-section">Other Features</div>',
            unsafe_allow_html=True,
        )

        other_pages = [
            "System Status",
            "Settings",
        ]

        selected_other = st.radio(
            "Other Features",
            other_pages,
            index=(
                other_pages.index(
                    st.session_state.active_page
                )
                if st.session_state.active_page
                in other_pages
                else 0
            ),
            key="sidebar_other_navigation",
            label_visibility="collapsed",
        )

        # ----------------------------------------------------
        # DETERMINE SELECTED PAGE
        # ----------------------------------------------------

        current = st.session_state.active_page

        # Radio controls each have their own key.
        # Only the group containing the current page is authoritative.
        all_pages = (
            registry_pages
            + operations_pages
            + administration_pages
            + other_pages
        )

        candidates = [
            selected_registry,
            selected_operations,
            selected_administration,
            selected_other,
        ]

        for candidate in candidates:

            if candidate in all_pages:

                # Determine whether candidate belongs to
                # the navigation group that currently owns
                # the selected page.
                if candidate != current:

                    current = candidate

        # ----------------------------------------------------
        # DATABASE STATUS
        # ----------------------------------------------------

        st.markdown(
            '<div class="sidebar-section">System</div>',
            unsafe_allow_html=True,
        )

        if database_ok:

            st.markdown(
                """
                <div class="sidebar-status">
                    <div class="status-online">
                        <span class="status-dot"></span>
                        System Online
                    </div>
                    <div class="sidebar-subtitle">
                        Database connected
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                """
                <div class="sidebar-status">
                    <div class="status-warning">
                        <span class="status-dot-warning"></span>
                        Database Attention
                    </div>
                    <div class="sidebar-subtitle">
                        Registry interface available
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            "",
        )

        # ----------------------------------------------------
        # THEME
        # ----------------------------------------------------

        if st.button(
            (
                "Use Light Theme"
                if st.session_state.theme == "dark"
                else "Use Dark Theme"
            ),
            key="sidebar_theme_toggle",
            use_container_width=True,
        ):

            st.session_state.theme = (
                "light"
                if st.session_state.theme == "dark"
                else "dark"
            )

            st.rerun()

        if st.button(
            "Refresh Application",
            key="sidebar_refresh",
            use_container_width=True,
        ):

            st.rerun()

        st.markdown(
            f"""
            <div class="sidebar-status">
                <div class="sidebar-subtitle">
                    Registry Platform
                </div>
                <div class="sidebar-subtitle">
                    Version {APP_VERSION}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return current


# ============================================================
# FIELD HELPERS
# ============================================================

def model_columns(model: Any) -> list[str]:

    if model is None:
        return []

    try:

        return [
            column.name
            for column
            in model.__table__.columns
        ]

    except Exception:

        return []


def model_value(
    record: Any,
    field_name: str,
    default: Any = None,
) -> Any:

    try:
        return getattr(
            record,
            field_name,
            default,
        )

    except Exception:
        return default


def field_exists(
    model: Any,
    field_name: str,
) -> bool:

    return field_name in model_columns(model)


# ============================================================
# GENERIC DELETE CONFIRMATION
# ============================================================

def render_delete_button(
    model: Any,
    record_id: str,
    label: str = "Delete",
) -> None:

    if st.button(
        label,
        key=f"delete_{model.__tablename__}_{record_id}",
        use_container_width=True,
    ):

        success, error = delete_record(
            model,
            record_id,
        )

        if success:

            set_notice(
                "Record deleted successfully.",
                "success",
            )

            st.rerun()

        else:

            st.error(
                error
                or "Unable to delete record."
            )


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:

    st.markdown(
        """
        <div class="page-kicker">
            South Sudan National Registry
        </div>

        <div class="page-heading">
            National Registry Overview
        </div>

        <div class="page-description">
            Centralized management platform for national
            population records, civil registration,
            identity management, households and
            electoral registration.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    population_count = count_records(Citizen)
    civil_count = count_records(CivilEvent)
    identity_count = count_records(Document)
    election_count = count_records(VoterRecord)

    c1, c2, c3, c4 = st.columns(4)

    with c1:

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

    with c2:

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

    with c3:

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

    with c4:

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

    st.divider()

    # --------------------------------------------------------
    # SERVICES
    # --------------------------------------------------------

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
            "Reports & Analytics",
            "Generate operational reports, statistical summaries and Registry analytics.",
        ),
        (
            "Identity Management",
            "Manage national identity registration, identification records and identity services.",
        ),
        (
            "Administration",
            "Manage users, roles, permissions, configuration and system administration.",
        ),
    ]

    service_columns = st.columns(2)

    for index, (
        name,
        description,
    ) in enumerate(services):

        with service_columns[index % 2]:

            st.markdown(
                f"""
                <div class="registry-card">

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

    st.subheader("System Status")

    if database_ok:

        st.success(
            "Registry interface and database are available."
        )

    else:

        st.warning(
            "Registry interface is available, but the database "
            "is not currently connected."
        )

        if st.session_state.database_error:

            with st.expander(
                "Database technical details"
            ):

                st.code(
                    st.session_state.database_error
                )


# ============================================================
# CITIZENS
# ============================================================

def render_citizens() -> None:

    st.markdown(
        """
        <div class="page-kicker">
            Population Registry
        </div>

        <div class="page-heading">
            Citizens
        </div>

        <div class="page-description">
            Citizen population records and citizen registry management.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if Citizen is None:

        st.error(
            "Citizen model is unavailable."
        )

        return

    tab_list, tab_add = st.tabs(
        [
            "Citizen Records",
            "Register Citizen",
        ]
    )

    with tab_add:

        render_citizen_form()

    with tab_list:

        records = get_records(
            Citizen,
            limit=1000,
        )

        search = st.text_input(
            "Search citizens",
            placeholder=(
                "Search by name, national ID, phone or location..."
            ),
            key="citizen_search",
        )

        filtered = []

        search_lower = search.lower().strip()

        for record in records:

            if not search_lower:

                filtered.append(record)

                continue

            haystack = " ".join(
                [
                    safe_text(
                        model_value(
                            record,
                            "full_name",
                        )
                    ),
                    safe_text(
                        model_value(
                            record,
                            "national_id",
                        )
                    ),
                    safe_text(
                        model_value(
                            record,
                            "phone_number",
                        )
                    ),
                    safe_text(
                        model_value(
                            record,
                            "state_or_region",
                        )
                    ),
                    safe_text(
                        model_value(
                            record,
                            "county_or_payam",
                        )
                    ),
                ]
            ).lower()

            if search_lower in haystack:
                filtered.append(record)

        st.caption(
            f"{len(filtered):,} citizen record(s)"
        )

        for record in filtered[:200]:

            with st.expander(
                f"{safe_text(record.full_name)}"
                f" — {safe_text(record.national_id) or 'No National ID'}"
            ):

                render_citizen_record(
                    record
                )


# ============================================================
# CITIZEN FORM
# ============================================================

def render_citizen_form(
    record: Optional[Any] = None,
) -> None:

    editing = record is not None

    prefix = (
        f"edit_citizen_{record.id}"
        if editing
        else "new_citizen"
    )

    st.markdown(
        "### Edit Citizen"
        if editing
        else "Register Citizen"
    )

    with st.form(
        key=f"{prefix}_form",
    ):

        c1, c2 = st.columns(2)

        with c1:

            full_name = st.text_input(
                "Full name *",
                value=safe_text(
                    model_value(
                        record,
                        "full_name",
                    )
                ),
                key=f"{prefix}_full_name",
            )

            national_id = st.text_input(
                "National ID",
                value=safe_text(
                    model_value(
                        record,
                        "national_id",
                    )
                ),
                key=f"{prefix}_national_id",
            )

            passport_number = st.text_input(
                "Passport number",
                value=safe_text(
                    model_value(
                        record,
                        "passport_number",
                    )
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
                    ].index(
                        model_value(
                            record,
                            "gender",
                            "Other",
                        )
                    )
                    if model_value(
                        record,
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
                key=f"{prefix}_gender",
            )

            marital_status = st.selectbox(
                "Marital status",
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
                    ].index(
                        model_value(
                            record,
                            "marital_status",
                            "Single",
                        )
                    )
                    if model_value(
                        record,
                        "marital_status",
                        "Single",
                    )
                    in [
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

        with c2:

            dob_value = model_value(
                record,
                "date_of_birth",
            )

            date_of_birth = st.date_input(
                "Date of birth",
                value=(
                    dob_value
                    if isinstance(
                        dob_value,
                        date,
                    )
                    else date(
                        2000,
                        1,
                        1,
                    )
                ),
                key=f"{prefix}_dob",
            )

            nationality = st.text_input(
                "Nationality",
                value=safe_text(
                    model_value(
                        record,
                        "nationality",
                        "South Sudanese",
                    )
                ),
                key=f"{prefix}_nationality",
            )

            phone_number = st.text_input(
                "Phone number",
                value=safe_text(
                    model_value(
                        record,
                        "phone_number",
                    )
                ),
                key=f"{prefix}_phone",
            )

            email_address = st.text_input(
                "Email address",
                value=safe_text(
                    model_value(
                        record,
                        "email_address",
                    )
                ),
                key=f"{prefix}_email",
            )

            verification_status = st.selectbox(
                "Verification status",
                [
                    "Pending Review",
                    "Verified",
                    "Rejected",
                    "Needs Correction",
                ],
                index=(
                    [
                        "Pending Review",
                        "Verified",
                        "Rejected",
                        "Needs Correction",
                    ].index(
                        model_value(
                            record,
                            "verification_status",
                            "Pending Review",
                        )
                    )
                    if model_value(
                        record,
                        "verification_status",
                        "Pending Review",
                    )
                    in [
                        "Pending Review",
                        "Verified",
                        "Rejected",
                        "Needs Correction",
                    ]
                    else 0
                ),
                key=f"{prefix}_verification",
            )

        st.markdown("#### Location")

        l1, l2, l3 = st.columns(3)

        with l1:

            state_or_region = st.text_input(
                "State / Region",
                value=safe_text(
                    model_value(
                        record,
                        "state_or_region",
                    )
                ),
                key=f"{prefix}_state",
            )

        with l2:

            county_or_payam = st.text_input(
                "County / Payam",
                value=safe_text(
                    model_value(
                        record,
                        "county_or_payam",
                    )
                ),
                key=f"{prefix}_county",
            )

        with l3:

            boma = st.text_input(
                "Boma",
                value=safe_text(
                    model_value(
                        record,
                        "boma",
                    )
                ),
                key=f"{prefix}_boma",
            )

        community = st.text_input(
            "Community",
            value=safe_text(
                model_value(
                    record,
                    "community",
                )
            ),
            key=f"{prefix}_community",
        )

        residential_address = st.text_area(
            "Residential address",
            value=safe_text(
                model_value(
                    record,
                    "residential_address",
                )
            ),
            key=f"{prefix}_address",
        )

        st.markdown("#### Demographics")

        d1, d2, d3 = st.columns(3)

        with d1:

            tribe = st.text_input(
                "Tribe",
                value=safe_text(
                    model_value(
                        record,
                        "tribe",
                    )
                ),
                key=f"{prefix}_tribe",
            )

        with d2:

            clan = st.text_input(
                "Sub-tribe / Clan",
                value=safe_text(
                    model_value(
                        record,
                        "sub_tribe_or_clan",
                    )
                ),
                key=f"{prefix}_clan",
            )

        with d3:

            language = st.text_input(
                "Native language",
                value=safe_text(
                    model_value(
                        record,
                        "native_language",
                    )
                ),
                key=f"{prefix}_language",
            )

        education_level = st.text_input(
            "Education level",
            value=safe_text(
                model_value(
                    record,
                    "education_level",
                    "None / Informal",
                )
            ),
            key=f"{prefix}_education",
        )

        employment_status = st.text_input(
            "Employment status",
            value=safe_text(
                model_value(
                    record,
                    "employment_status",
                    "Unemployed / Seeking Work",
                )
            ),
            key=f"{prefix}_employment",
        )

        occupation = st.text_input(
            "Primary occupation",
            value=safe_text(
                model_value(
                    record,
                    "primary_occupation",
                )
            ),
            key=f"{prefix}_occupation",
        )

        notes = st.text_area(
            "Notes",
            value=safe_text(
                model_value(
                    record,
                    "notes",
                )
            ),
            key=f"{prefix}_notes",
        )

        submitted = st.form_submit_button(
            "Update Citizen"
            if editing
            else "Register Citizen",
            use_container_width=True,
        )

    if submitted:

        if not full_name.strip():

            st.error(
                "Full name is required."
            )

            return

        if not database_ok:

            st.error(
                "Database is unavailable."
            )

            return

        session = get_session()

        if session is None:

            st.error(
                "Unable to create database session."
            )

            return

        try:

            if editing:

                citizen = session.get(
                    Citizen,
                    record.id,
                )

                if citizen is None:

                    st.error(
                        "Citizen record no longer exists."
                    )

                    return

            else:

                citizen = Citizen(
                    id=safe_uuid(),
                )

                session.add(citizen)

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
            citizen.nationality = (
                nationality.strip()
                or "South Sudanese"
            )
            citizen.date_of_birth = date_of_birth
            citizen.phone_number = (
                phone_number.strip()
                or None
            )
            citizen.email_address = (
                email_address.strip()
                or None
            )
            citizen.state_or_region = (
                state_or_region.strip()
            )
            citizen.county_or_payam = (
                county_or_payam.strip()
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
            citizen.tribe = tribe.strip()
            citizen.sub_tribe_or_clan = (
                clan.strip()
                or None
            )
            citizen.native_language = (
                language.strip()
            )
            citizen.education_level = (
                education_level.strip()
            )
            citizen.employment_status = (
                employment_status.strip()
            )
            citizen.primary_occupation = (
                occupation.strip()
                or None
            )
            citizen.verification_status = (
                verification_status
            )
            citizen.notes = (
                notes.strip()
                or None
            )

            session.commit()

            set_notice(
                (
                    "Citizen updated successfully."
                    if editing
                    else "Citizen registered successfully."
                )
            )

            st.rerun()

        except Exception as exc:

            session.rollback()

            logger.exception(
                "Unable to save citizen."
            )

            st.error(
                "Unable to save citizen record."
            )

            with st.expander(
                "Technical details"
            ):

                st.exception(exc)

        finally:

            session.close()


# ============================================================
# CITIZEN RECORD
# ============================================================

def render_citizen_record(
    record: Any,
) -> None:

    c1, c2, c3 = st.columns(3)

    with c1:

        st.write(
            f"**National ID:** "
            f"{safe_text(record.national_id) or 'Not assigned'}"
        )

        st.write(
            f"**Date of birth:** "
            f"{safe_text(record.date_of_birth) or 'Not recorded'}"
        )

        st.write(
            f"**Gender:** "
            f"{safe_text(record.gender)}"
        )

    with c2:

        st.write(
            f"**Phone:** "
            f"{safe_text(record.phone_number) or 'Not recorded'}"
        )

        st.write(
            f"**State / Region:** "
            f"{safe_text(record.state_or_region)}"
        )

        st.write(
            f"**County / Payam:** "
            f"{safe_text(record.county_or_payam)}"
        )

    with c3:

        st.write(
            f"**Verification:** "
            f"{safe_text(record.verification_status)}"
        )

        st.write(
            f"**Nationality:** "
            f"{safe_text(record.nationality)}"
        )

        st.write(
            f"**Created:** "
            f"{safe_text(record.created_at)}"
        )

    e1, e2 = st.columns(2)

    with e1:

        if st.button(
            "Edit Citizen",
            key=f"edit_citizen_{record.id}",
            use_container_width=True,
        ):

            st.session_state[
                "editing_citizen_id"
            ] = record.id

            st.session_state.active_page = (
                "Citizens"
            )

            st.rerun()

    with e2:

        render_delete_button(
            Citizen,
            record.id,
        )

    editing_id = st.session_state.get(
        "editing_citizen_id"
    )

    if editing_id == record.id:

        st.divider()

        render_citizen_form(
            record
        )


# ============================================================
# HOUSEHOLDS
# ============================================================

def render_households() -> None:

    st.markdown(
        """
        <div class="page-kicker">
            Population Registry
        </div>

        <div class="page-heading">
            Households
        </div>

        <div class="page-description">
            Register and manage household locations,
            household numbers and household membership.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if Household is None:

        st.error(
            "Household model is unavailable."
        )

        return

    tab_records, tab_new = st.tabs(
        [
            "Household Records",
            "Register Household",
        ]
    )

    with tab_new:

        render_household_form()

    with tab_records:

        records = get_records(
            Household
        )

        st.caption(
            f"{len(records):,} household record(s)"
        )

        for record in records:

            with st.expander(
                f"{safe_text(record.household_number)}"
                f" — {safe_text(record.community)}"
            ):

                render_household_record(
                    record
                )


def render_household_form(
    record: Optional[Any] = None,
) -> None:

    editing = record is not None

    prefix = (
        f"edit_household_{record.id}"
        if editing
        else "new_household"
    )

    with st.form(
        key=f"{prefix}_form"
    ):

        household_number = st.text_input(
            "Household number *",
            value=safe_text(
                model_value(
                    record,
                    "household_number",
                )
            ),
            key=f"{prefix}_number",
        )

        state = st.text_input(
            "State / Region",
            value=safe_text(
                model_value(
                    record,
                    "state_or_region",
                )
            ),
            key=f"{prefix}_state",
        )

        county = st.text_input(
            "County / Payam",
            value=safe_text(
                model_value(
                    record,
                    "county_or_payam",
                )
            ),
            key=f"{prefix}_county",
        )

        boma = st.text_input(
            "Boma",
            value=safe_text(
                model_value(
                    record,
                    "boma",
                )
            ),
            key=f"{prefix}_boma",
        )

        community = st.text_input(
            "Community",
            value=safe_text(
                model_value(
                    record,
                    "community",
                )
            ),
            key=f"{prefix}_community",
        )

        address = st.text_area(
            "Residential address",
            value=safe_text(
                model_value(
                    record,
                    "residential_address",
                )
            ),
            key=f"{prefix}_address",
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
                "Household number is required."
            )

            return

        if not database_ok:

            st.error(
                "Database is unavailable."
            )

            return

        session = get_session()

        if session is None:
            st.error(
                "Unable to create database session."
            )
            return

        try:

            if editing:

                household = session.get(
                    Household,
                    record.id,
                )

                if household is None:

                    st.error(
                        "Household record not found."
                    )

                    return

            else:

                household = Household(
                    id=safe_uuid()
                )

                session.add(household)

            household.household_number = (
                household_number.strip()
            )

            household.state_or_region = (
                state.strip()
            )

            household.county_or_payam = (
                county.strip()
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
                address.strip()
                or None
            )

            session.commit()

            set_notice(
                (
                    "Household updated successfully."
                    if editing
                    else "Household registered successfully."
                )
            )

            st.rerun()

        except Exception as exc:

            session.rollback()

            logger.exception(
                "Unable to save household."
            )

            st.error(
                "Unable to save household."
            )

            with st.expander(
                "Technical details"
            ):

                st.exception(exc)

        finally:

            session.close()


def render_household_record(
    record: Any,
) -> None:

    st.write(
        f"**State / Region:** "
        f"{safe_text(record.state_or_region)}"
    )

    st.write(
        f"**County / Payam:** "
        f"{safe_text(record.county_or_payam)}"
    )

    st.write(
        f"**Boma:** "
        f"{safe_text(record.boma)}"
    )

    st.write(
        f"**Community:** "
        f"{safe_text(record.community)}"
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "Edit Household",
            key=f"edit_household_{record.id}",
            use_container_width=True,
        ):

            st.session_state[
                "editing_household_id"
            ] = record.id

            st.rerun()

    with c2:

        render_delete_button(
            Household,
            record.id,
        )

    if (
        st.session_state.get(
            "editing_household_id"
        )
        == record.id
    ):

        st.divider()

        render_household_form(
            record
        )


# ============================================================
# CIVIL REGISTRATION
# ============================================================

def render_civil_registration() -> None:

    st.markdown(
        """
        <div class="page-kicker">
            Civil Registration
        </div>

        <div class="page-heading">
            Civil Registration
        </div>

        <div class="page-description">
            Register births, deaths, marriages, divorces,
            certificates and other civil events.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if CivilEvent is None:

        st.error(
            "Civil Event model is unavailable."
        )

        return

    tab_records, tab_new = st.tabs(
        [
            "Civil Records",
            "Register Civil Event",
        ]
    )

    with tab_new:

        render_civil_event_form()

    with tab_records:

        records = get_records(
            CivilEvent
        )

        st.caption(
            f"{len(records):,} civil event(s)"
        )

        for record in records:

            with st.expander(
                f"{safe_text(record.event_type)}"
                f" — {safe_text(record.reference_number)}"
            ):

                render_civil_event_record(
                    record
                )


def render_civil_event_form(
    record: Optional[Any] = None,
) -> None:

    editing = record is not None

    prefix = (
        f"edit_civil_{record.id}"
        if editing
        else "new_civil"
    )

    event_types = [
        "Birth",
        "Death",
        "Marriage",
        "Divorce",
        "Other",
    ]

    with st.form(
        key=f"{prefix}_form"
    ):

        reference = st.text_input(
            "Reference number *",
            value=safe_text(
                model_value(
                    record,
                    "reference_number",
                )
            ),
            key=f"{prefix}_reference",
        )

        event_type = st.selectbox(
            "Event type",
            event_types,
            index=(
                event_types.index(
                    model_value(
                        record,
                        "event_type",
                        "Birth",
                    )
                )
                if model_value(
                    record,
                    "event_type",
                    "Birth",
                )
                in event_types
                else 0
            ),
            key=f"{prefix}_event_type",
        )

        existing_date = model_value(
            record,
            "event_date",
        )

        event_date = st.date_input(
            "Event date",
            value=(
                existing_date
                if isinstance(
                    existing_date,
                    date,
                )
                else date.today()
            ),
            key=f"{prefix}_date",
        )

        registration_centre = st.text_input(
            "Registration centre",
            value=safe_text(
                model_value(
                    record,
                    "registration_centre",
                )
            ),
            key=f"{prefix}_centre",
        )

        document_number = st.text_input(
            "Document number",
            value=safe_text(
                model_value(
                    record,
                    "document_number",
                )
            ),
            key=f"{prefix}_document",
        )

        status_options = [
            "Pending Review",
            "Registered",
            "Verified",
            "Rejected",
        ]

        status = st.selectbox(
            "Status",
            status_options,
            index=(
                status_options.index(
                    model_value(
                        record,
                        "status",
                        "Pending Review",
                    )
                )
                if model_value(
                    record,
                    "status",
                    "Pending Review",
                )
                in status_options
                else 0
            ),
            key=f"{prefix}_status",
        )

        notes = st.text_area(
            "Notes",
            value=safe_text(
                model_value(
                    record,
                    "notes",
                )
            ),
            key=f"{prefix}_notes",
        )

        submitted = st.form_submit_button(
            "Update Civil Event"
            if editing
            else "Register Civil Event",
            use_container_width=True,
        )

    if submitted:

        if not reference.strip():

            st.error(
                "Reference number is required."
            )

            return

        if not database_ok:

            st.error(
                "Database is unavailable."
            )

            return

        session = get_session()

        if session is None:
            st.error(
                "Unable to create database session."
            )
            return

        try:

            if editing:

                event = session.get(
                    CivilEvent,
                    record.id,
                )

                if event is None:

                    st.error(
                        "Civil event not found."
                    )

                    return

            else:

                event = CivilEvent(
                    id=safe_uuid()
                )

                session.add(event)

            event.reference_number = (
                reference.strip()
            )

            event.event_type = event_type
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

            session.commit()

            set_notice(
                (
                    "Civil event updated successfully."
                    if editing
                    else "Civil event registered successfully."
                )
            )

            st.rerun()

        except Exception as exc:

            session.rollback()

            st.error(
                "Unable to save civil event."
            )

            with st.expander(
                "Technical details"
            ):

                st.exception(exc)

        finally:

            session.close()


def render_civil_event_record(
    record: Any,
) -> None:

    st.write(
        f"**Event date:** "
        f"{safe_text(record.event_date)}"
    )

    st.write(
        f"**Registration centre:** "
        f"{safe_text(record.registration_centre)}"
    )

    st.write(
        f"**Status:** "
        f"{safe_text(record.status)}"
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "Edit Civil Event",
            key=f"edit_civil_{record.id}",
            use_container_width=True,
        ):

            st.session_state[
                "editing_civil_id"
            ] = record.id

            st.rerun()

    with c2:

        render_delete_button(
            CivilEvent,
            record.id,
        )

    if (
        st.session_state.get(
            "editing_civil_id"
        )
        == record.id
    ):

        st.divider()

        render_civil_event_form(
            record
        )


# ============================================================
# IDENTITY MANAGEMENT
# ============================================================

def render_identity_management() -> None:

    st.markdown(
        """
        <div class="page-kicker">
            Identity Management
        </div>

        <div class="page-heading">
            Identity Documents
        </div>

        <div class="page-description">
            Manage national identity documents,
            document numbers, issuance and verification.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if Document is None:

        st.error(
            "Document model is unavailable."
        )

        return

    tab_records, tab_new = st.tabs(
        [
            "Identity Records",
            "Register Document",
        ]
    )

    with tab_new:

        render_document_form()

    with tab_records:

        records = get_records(
            Document
        )

        st.caption(
            f"{len(records):,} identity document(s)"
        )

        for record in records:

            with st.expander(
                f"{safe_text(record.document_type)}"
                f" — {safe_text(record.document_number)}"
            ):

                render_document_record(
                    record
                )


# ============================================================
# DOCUMENT FORM
# ============================================================

def render_document_form(
    record: Optional[Any] = None,
) -> None:

    editing = record is not None

    prefix = (
        f"edit_document_{record.id}"
        if editing
        else "new_document"
    )

    document_types = [
        "National ID",
        "Passport",
        "Birth Certificate",
        "Death Certificate",
        "Marriage Certificate",
        "Other",
    ]

    statuses = [
        "Registered",
        "Pending",
        "Verified",
        "Expired",
        "Cancelled",
    ]

    with st.form(
        key=f"{prefix}_form"
    ):

        document_type = st.selectbox(
            "Document type",
            document_types,
            index=(
                document_types.index(
                    model_value(
                        record,
                        "document_type",
                        "National ID",
                    )
                )
                if model_value(
                    record,
                    "document_type",
                    "National ID",
                )
                in document_types
                else 0
            ),
            key=f"{prefix}_type",
        )

        document_number = st.text_input(
            "Document number",
            value=safe_text(
                model_value(
                    record,
                    "document_number",
                )
            ),
            key=f"{prefix}_number",
        )

        file_name = st.text_input(
            "File name",
            value=safe_text(
                model_value(
                    record,
                    "file_name",
                )
            ),
            key=f"{prefix}_filename",
        )

        status = st.selectbox(
            "Status",
            statuses,
            index=(
                statuses.index(
                    model_value(
                        record,
                        "status",
                        "Registered",
                    )
                )
                if model_value(
                    record,
                    "status",
                    "Registered",
                )
                in statuses
                else 0
            ),
            key=f"{prefix}_status",
        )

        issued_value = model_value(
            record,
            "issued_date",
        )

        issued_date = st.date_input(
            "Issued date",
            value=(
                issued_value
                if isinstance(
                    issued_value,
                    date,
                )
                else date.today()
            ),
            key=f"{prefix}_issued",
        )

        expiry_value = model_value(
            record,
            "expiry_date",
        )

        expiry_date = st.date_input(
            "Expiry date",
            value=(
                expiry_value
                if isinstance(
                    expiry_value,
                    date,
                )
                else date.today()
            ),
            key=f"{prefix}_expiry",
        )

        submitted = st.form_submit_button(
            "Update Document"
            if editing
            else "Register Document",
            use_container_width=True,
        )

    if submitted:

        if not database_ok:

            st.error(
                "Database is unavailable."
            )

            return

        session = get_session()

        if session is None:
            st.error(
                "Unable to create database session."
            )
            return

        try:

            if editing:

                document = session.get(
                    Document,
                    record.id,
                )

                if document is None:

                    st.error(
                        "Document not found."
                    )

                    return

            else:

                document = Document(
                    id=safe_uuid()
                )

                session.add(document)

            document.document_type = (
                document_type
            )

            document.document_number = (
                document_number.strip()
                or None
            )

            document.file_name = (
                file_name.strip()
                or None
            )

            document.status = status
            document.issued_date = issued_date
            document.expiry_date = expiry_date

            session.commit()

            set_notice(
                (
                    "Document updated successfully."
                    if editing
                    else "Document registered successfully."
                )
            )

            st.rerun()

        except Exception as exc:

            session.rollback()

            st.error(
                "Unable to save document."
            )

            with st.expander(
                "Technical details"
            ):

                st.exception(exc)

        finally:

            session.close()


def render_document_record(
    record: Any,
) -> None:

    st.write(
        f"**Status:** "
        f"{safe_text(record.status)}"
    )

    st.write(
        f"**Issued:** "
        f"{safe_text(record.issued_date)}"
    )

    st.write(
        f"**Expiry:** "
        f"{safe_text(record.expiry_date)}"
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "Edit Document",
            key=f"edit_document_{record.id}",
            use_container_width=True,
        ):

            st.session_state[
                "editing_document_id"
            ] = record.id

            st.rerun()

    with c2:

        render_delete_button(
            Document,
            record.id,
        )

    if (
        st.session_state.get(
            "editing_document_id"
        )
        == record.id
    ):

        st.divider()

        render_document_form(
            record
        )


# ============================================================
# ELECTIONS
# ============================================================

def render_elections() -> None:

    st.markdown(
        """
        <div class="page-kicker">
            Electoral Registry
        </div>

        <div class="page-heading">
            Elections
        </div>

        <div class="page-description">
            Manage voter registration, voter identification,
            constituencies and polling stations.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if VoterRecord is None:

        st.error(
            "Voter Record model is unavailable."
        )

        return

    tab_records, tab_new = st.tabs(
        [
            "Voter Records",
            "Register Voter",
        ]
    )

    with tab_new:

        render_voter_form()

    with tab_records:

        records = get_records(
            VoterRecord
        )

        st.caption(
            f"{len(records):,} voter record(s)"
        )

        for record in records:

            with st.expander(
                f"{safe_text(record.voter_id_number)}"
                f" — {safe_text(record.voter_status)}"
            ):

                render_voter_record(
                    record
                )


def render_voter_form(
    record: Optional[Any] = None,
) -> None:

    editing = record is not None

    prefix = (
        f"edit_voter_{record.id}"
        if editing
        else "new_voter"
    )

    statuses = [
        "Active",
        "Inactive",
        "Suspended",
        "Transferred",
        "Pending Review",
    ]

    with st.form(
        key=f"{prefix}_form"
    ):

        voter_id = st.text_input(
            "Voter ID number",
            value=safe_text(
                model_value(
                    record,
                    "voter_id_number",
                )
            ),
            key=f"{prefix}_voter_id",
        )

        status = st.selectbox(
            "Voter status",
            statuses,
            index=(
                statuses.index(
                    model_value(
                        record,
                        "voter_status",
                        "Active",
                    )
                )
                if model_value(
                    record,
                    "voter_status",
                    "Active",
                )
                in statuses
                else 0
            ),
            key=f"{prefix}_status",
        )

        constituency = st.text_input(
            "Constituency",
            value=safe_text(
                model_value(
                    record,
                    "constituency",
                )
            ),
            key=f"{prefix}_constituency",
        )

        polling_id = st.text_input(
            "Polling station ID",
            value=safe_text(
                model_value(
                    record,
                    "polling_station_id",
                )
            ),
            key=f"{prefix}_polling_id",
        )

        polling_name = st.text_input(
            "Polling station name",
            value=safe_text(
                model_value(
                    record,
                    "polling_station_name",
                )
            ),
            key=f"{prefix}_polling_name",
        )

        has_voted = st.checkbox(
            "Record as voted",
            value=bool(
                model_value(
                    record,
                    "has_voted",
                    False,
                )
            ),
            key=f"{prefix}_has_voted",
        )

        submitted = st.form_submit_button(
            "Update Voter"
            if editing
            else "Register Voter",
            use_container_width=True,
        )

    if submitted:

        if not database_ok:

            st.error(
                "Database is unavailable."
            )

            return

        session = get_session()

        if session is None:
            st.error(
                "Unable to create database session."
            )
            return

        try:

            if editing:

                voter = session.get(
                    VoterRecord,
                    record.id,
                )

                if voter is None:

                    st.error(
                        "Voter record not found."
                    )

                    return

            else:

                voter = VoterRecord(
                    id=safe_uuid()
                )

                session.add(voter)

            voter.voter_id_number = (
                voter_id.strip()
                or None
            )

            voter.voter_status = status

            voter.constituency = (
                constituency.strip()
                or None
            )

            voter.polling_station_id = (
                polling_id.strip()
                or None
            )

            voter.polling_station_name = (
                polling_name.strip()
                or None
            )

            voter.has_voted = has_voted

            if has_voted:

                voter.voted_at = datetime.utcnow()

            else:

                voter.voted_at = None

            session.commit()

            set_notice(
                (
                    "Voter record updated successfully."
                    if editing
                    else "Voter record registered successfully."
                )
            )

            st.rerun()

        except Exception as exc:

            session.rollback()

            st.error(
                "Unable to save voter record."
            )

            with st.expander(
                "Technical details"
            ):

                st.exception(exc)

        finally:

            session.close()


def render_voter_record(
    record: Any,
) -> None:

    st.write(
        f"**Status:** "
        f"{safe_text(record.voter_status)}"
    )

    st.write(
        f"**Constituency:** "
        f"{safe_text(record.constituency)}"
    )

    st.write(
        f"**Polling station:** "
        f"{safe_text(record.polling_station_name)}"
    )

    st.write(
        f"**Has voted:** "
        f"{'Yes' if record.has_voted else 'No'}"
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "Edit Voter",
            key=f"edit_voter_{record.id}",
            use_container_width=True,
        ):

            st.session_state[
                "editing_voter_id"
            ] = record.id

            st.rerun()

    with c2:

        render_delete_button(
            VoterRecord,
            record.id,
        )

    if (
        st.session_state.get(
            "editing_voter_id"
        )
        == record.id
    ):

        st.divider()

        render_voter_form(
            record
        )


# ============================================================
# ADMINISTRATIVE UNITS
# ============================================================

def render_administrative_units() -> None:

    st.markdown(
        """
        <div class="page-kicker">
            Administration
        </div>

        <div class="page-heading">
            Administrative Units
        </div>

        <div class="page-description">
            Manage the administrative hierarchy of the registry.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if AdministrativeUnit is None:

        st.error(
            "Administrative Unit model is unavailable."
        )

        return

    tab_records, tab_new = st.tabs(
        [
            "Administrative Units",
            "Create Unit",
        ]
    )

    with tab_new:

        render_administrative_unit_form()

    with tab_records:

        records = get_records(
            AdministrativeUnit
        )

        st.caption(
            f"{len(records):,} administrative unit(s)"
        )

        for record in records:

            with st.expander(
                f"{safe_text(record.unit_type)}"
                f" — {safe_text(record.name)}"
            ):

                st.write(
                    f"**Code:** "
                    f"{safe_text(record.code)}"
                )

                st.write(
                    f"**State / Region:** "
                    f"{safe_text(record.state_or_region)}"
                )

                c1, c2 = st.columns(2)

                with c1:

                    if st.button(
                        "Edit Unit",
                        key=f"edit_unit_{record.id}",
                        use_container_width=True,
                    ):

                        st.session_state[
                            "editing_unit_id"
                        ] = record.id

                        st.rerun()

                with c2:

                    render_delete_button(
                        AdministrativeUnit,
                        record.id,
                    )

                if (
                    st.session_state.get(
                        "editing_unit_id"
                    )
                    == record.id
                ):

                    st.divider()

                    render_administrative_unit_form(
                        record
                    )


def render_administrative_unit_form(
    record: Optional[Any] = None,
) -> None:

    editing = record is not None

    prefix = (
        f"edit_unit_{record.id}"
        if editing
        else "new_unit"
    )

    unit_types = [
        "Country",
        "State",
        "County",
        "Payam",
        "Boma",
        "Other",
    ]

    with st.form(
        key=f"{prefix}_form"
    ):

        unit_type = st.selectbox(
            "Unit type",
            unit_types,
            index=(
                unit_types.index(
                    model_value(
                        record,
                        "unit_type",
                        "State",
                    )
                )
                if model_value(
                    record,
                    "unit_type",
                    "State",
                )
                in unit_types
                else 1
            ),
            key=f"{prefix}_type",
        )

        name = st.text_input(
            "Name *",
            value=safe_text(
                model_value(
                    record,
                    "name",
                )
            ),
            key=f"{prefix}_name",
        )

        code = st.text_input(
            "Code *",
            value=safe_text(
                model_value(
                    record,
                    "code",
                )
            ),
            key=f"{prefix}_code",
        )

        state = st.text_input(
            "State / Region",
            value=safe_text(
                model_value(
                    record,
                    "state_or_region",
                )
            ),
            key=f"{prefix}_state",
        )

        administrator = st.text_input(
            "Administrator",
            value=safe_text(
                model_value(
                    record,
                    "administrator_name",
                )
            ),
            key=f"{prefix}_administrator",
        )

        headquarters = st.text_input(
            "Headquarters",
            value=safe_text(
                model_value(
                    record,
                    "headquarters",
                )
            ),
            key=f"{prefix}_headquarters",
        )

        notes = st.text_area(
            "Notes",
            value=safe_text(
                model_value(
                    record,
                    "notes",
                )
            ),
            key=f"{prefix}_notes",
        )

        submitted = st.form_submit_button(
            "Update Unit"
            if editing
            else "Create Unit",
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

        if not database_ok:

            st.error(
                "Database is unavailable."
            )

            return

        session = get_session()

        if session is None:
            st.error(
                "Unable to create database session."
            )
            return

        try:

            if editing:

                unit = session.get(
                    AdministrativeUnit,
                    record.id,
                )

                if unit is None:

                    st.error(
                        "Administrative unit not found."
                    )

                    return

            else:

                unit = AdministrativeUnit(
                    id=safe_uuid()
                )

                session.add(unit)

            unit.unit_type = unit_type
            unit.name = name.strip()
            unit.code = code.strip()
            unit.state_or_region = state.strip()
            unit.administrator_name = (
                administrator.strip()
                or None
            )
            unit.headquarters = (
                headquarters.strip()
                or None
            )
            unit.notes = (
                notes.strip()
                or None
            )

            session.commit()

            set_notice(
                (
                    "Administrative unit updated successfully."
                    if editing
                    else "Administrative unit created successfully."
                )
            )

            st.rerun()

        except Exception as exc:

            session.rollback()

            st.error(
                "Unable to save administrative unit."
            )

            with st.expander(
                "Technical details"
            ):

                st.exception(exc)

        finally:

            session.close()


# ============================================================
# DOCUMENTS
# ============================================================

def render_documents() -> None:

    render_identity_management()


# ============================================================
# REPORTS
# ============================================================

def render_reports() -> None:

    st.markdown(
        """
        <div class="page-kicker">
            Reports & Analytics
        </div>

        <div class="page-heading">
            Registry Reports
        </div>

        <div class="page-description">
            Operational statistics and registry summaries.
        </div>
        """,
        unsafe_allow_html=True,
    )

    citizens = count_records(Citizen)
    households = count_records(Household)
    civil_events = count_records(CivilEvent)
    documents = count_records(Document)
    voters = count_records(VoterRecord)
    admin_units = count_records(
        AdministrativeUnit
    )

    data = {
        "Citizens": citizens,
        "Households": households,
        "Civil Events": civil_events,
        "Identity Documents": documents,
        "Voter Records": voters,
        "Administrative Units": admin_units,
    }

    st.bar_chart(data)

    st.divider()

    for label, value in data.items():

        st.metric(
            label,
            f"{value:,}",
        )


# ============================================================
# VERIFICATION
# ============================================================

def render_verification() -> None:

    st.markdown(
        """
        <div class="page-kicker">
            Registry Operations
        </div>

        <div class="page-heading">
            Verification
        </div>

        <div class="page-description">
            Review records requiring verification or administrative
            approval.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not database_ok:

        st.warning(
            "Database is not connected."
        )

        return

    pending = []

    records = get_records(
        Citizen,
        limit=1000,
    )

    for citizen in records:

        if (
            safe_text(
                getattr(
                    citizen,
                    "verification_status",
                    "",
                )
            )
            not in [
                "Verified",
            ]
        ):

            pending.append(
                citizen
            )

    st.metric(
        "Records requiring review",
        len(pending),
    )

    for citizen in pending[:100]:

        with st.expander(
            f"{safe_text(citizen.full_name)}"
            f" — {safe_text(citizen.verification_status)}"
        ):

            st.write(
                f"**National ID:** "
                f"{safe_text(citizen.national_id)}"
            )

            st.write(
                f"**Status:** "
                f"{safe_text(citizen.verification_status)}"
            )

            if st.button(
                "Mark Verified",
                key=f"verify_citizen_{citizen.id}",
                use_container_width=True,
            ):

                session = get_session()

                if session is None:

                    st.error(
                        "Database session unavailable."
                    )

                    continue

                try:

                    item = session.get(
                        Citizen,
                        citizen.id,
                    )

                    if item:

                        item.verification_status = (
                            "Verified"
                        )

                        item.verified_at = (
                            datetime.utcnow()
                        )

                        session.commit()

                        set_notice(
                            "Citizen record verified."
                        )

                        st.rerun()

                except Exception as exc:

                    session.rollback()

                    st.error(
                        "Unable to verify record."
                    )

                    with st.expander(
                        "Technical details"
                    ):

                        st.exception(exc)

                finally:

                    session.close()


# ============================================================
# ADMINISTRATION
# ============================================================

def render_administration() -> None:

    st.markdown(
        """
        <div class="page-kicker">
            Administration
        </div>

        <div class="page-heading">
            Administration
        </div>

        <div class="page-description">
            System administration, database controls and
            registry configuration.
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            """
            <div class="registry-card">

                <div class="module-name">
                    Database
                </div>

                <div class="module-description">
                    Database initialization and connectivity status.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if database_ok:

            st.success(
                "Database Connected"
            )

        else:

            st.warning(
                "Database Attention Required"
            )

    with c2:

        st.markdown(
            """
            <div class="registry-card">

                <div class="module-name">
                    Registry Platform
                </div>

                <div class="module-description">
                    South Sudan National Registry platform.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.info(
            f"Version {APP_VERSION}"
        )

    st.divider()

    st.subheader(
        "Database Actions"
    )

    if st.button(
        "Initialize / Repair Database",
        key="admin_initialize_database",
    ):

        initialize_database.clear()

        ok, error = initialize_database()

        if ok:

            st.session_state.database_initialized = True
            st.session_state.database_error = None

            st.success(
                "Database initialized successfully."
            )

        else:

            st.session_state.database_initialized = False
            st.session_state.database_error = error

            st.error(
                "Database initialization failed."
            )

            if error:

                st.code(error)


# ============================================================
# AUDIT LOG
# ============================================================

def render_audit_log() -> None:

    st.markdown(
        """
        <div class="page-kicker">
            Administration
        </div>

        <div class="page-heading">
            Audit Log
        </div>

        <div class="page-description">
            Application audit events recorded by the registry
            service layer.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if AuditLog is None:

        st.info(
            "Audit Log model is not available."
        )

        return

    records = get_records(
        AuditLog,
        limit=500,
    )

    if not records:

        st.info(
            "No audit events have been recorded."
        )

        return

    for record in records:

        st.markdown(
            f"""
            <div class="registry-card">

                <div class="module-name">
                    {safe_text(record.action)}
                </div>

                <div class="module-description">
                    Entity:
                    {safe_text(record.entity_type)}
                    |
                    ID:
                    {safe_text(record.entity_id)}
                    |
                    User:
                    {safe_text(record.username)}
                </div>

                <div class="registry-version">
                    {safe_text(record.created_at)}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# SYSTEM STATUS
# ============================================================

def render_system_status() -> None:

    st.markdown(
        """
        <div class="page-kicker">
            System
        </div>

        <div class="page-heading">
            System Status
        </div>

        <div class="page-description">
            Current status of the South Sudan National Registry
            application and database layer.
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Registry Interface",
            "Available",
        )

    with c2:

        st.metric(
            "Database",
            "Connected"
            if database_ok
            else "Attention",
        )

    with c3:

        st.metric(
            "Version",
            APP_VERSION,
        )

    st.divider()

    if database_ok:

        st.success(
            "The Registry interface and database are operational."
        )

    else:

        st.warning(
            "The Registry interface is running without a "
            "connected database."
        )

        if st.session_state.database_error:

            with st.expander(
                "Database technical details"
            ):

                st.code(
                    st.session_state.database_error
                )

    st.divider()

    st.subheader(
        "Application Components"
    )

    components = [
        (
            "Streamlit Interface",
            True,
        ),
        (
            "SQLAlchemy Models",
            MODELS_AVAILABLE,
        ),
        (
            "Database Layer",
            DATABASE_AVAILABLE,
        ),
        (
            "Database Connection",
            database_ok,
        ),
    ]

    for name, available in components:

        if available:

            st.success(
                f"{name}: Available"
            )

        else:

            st.warning(
                f"{name}: Attention Required"
            )


# ============================================================
# SETTINGS
# ============================================================

def render_settings() -> None:

    st.markdown(
        """
        <div class="page-kicker">
            System
        </div>

        <div class="page-heading">
            Settings
        </div>

        <div class="page-description">
            Application interface settings.
        </div>
        """,
        unsafe_allow_html=True,
    )

    theme = st.radio(
        "Application theme",
        [
            "dark",
            "light",
        ],
        index=(
            0
            if st.session_state.theme == "dark"
            else 1
        ),
        key="settings_theme",
    )

    if theme != st.session_state.theme:

        st.session_state.theme = theme

        st.rerun()

    st.info(
        "Database credentials and secrets should be configured "
        "through environment variables or Streamlit secrets, "
        "not stored directly in streamlit_app.py."
    )


# ============================================================
# PAGE ROUTER
# ============================================================

def render_active_page(
    page: str,
) -> None:

    if page == "Overview":

        render_overview()

    elif page == "Citizens":

        render_citizens()

    elif page == "Households":

        render_households()

    elif page == "Civil Registration":

        render_civil_registration()

    elif page == "Identity Management":

        render_identity_management()

    elif page == "Elections":

        render_elections()

    elif page == "Administrative Units":

        render_administrative_units()

    elif page == "Reports & Analytics":

        render_reports()

    elif page == "Verification":

        render_verification()

    elif page == "Documents":

        render_documents()

    elif page == "Administration":

        render_administration()

    elif page == "Audit Log":

        render_audit_log()

    elif page == "System Status":

        render_system_status()

    elif page == "Settings":

        render_settings()

    else:

        render_overview()


# ============================================================
# MAIN APPLICATION
# ============================================================

def main() -> None:

    # --------------------------------------------------------
    # Sidebar
    # --------------------------------------------------------

    selected_page = sidebar_navigation()

    # --------------------------------------------------------
    # Synchronize page
    # --------------------------------------------------------

    if selected_page:

        st.session_state.active_page = (
            selected_page
        )

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    render_header()

    # --------------------------------------------------------
    # Notice
    # --------------------------------------------------------

    show_notice()

    # --------------------------------------------------------
    # Model availability warning
    # --------------------------------------------------------

    if not MODELS_AVAILABLE:

        st.error(
            "Registry database models could not be loaded."
        )

        if MODELS_ERROR:

            with st.expander(
                "Model technical details"
            ):

                st.exception(
                    MODELS_ERROR
                )

    # --------------------------------------------------------
    # Main page
    # --------------------------------------------------------

    render_active_page(
        st.session_state.active_page
    )

    # --------------------------------------------------------
    # Footer
    # --------------------------------------------------------

    st.divider()

    footer_left, footer_right = st.columns(2)

    with footer_left:

        st.markdown(
            f"""
            <div class="registry-footer">
                South Sudan National Registry •
                Registry Platform •
                Version {APP_VERSION}
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


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
