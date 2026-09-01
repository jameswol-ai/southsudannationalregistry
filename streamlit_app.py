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

import io
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any

import streamlit as st


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

logger = logging.getLogger(
    "south_sudan_national_registry"
)

if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


# ============================================================
# SESSION STATE
# ============================================================

if "active_module" not in st.session_state:
    st.session_state.active_module = "overview"

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

if "database_connected" not in st.session_state:
    st.session_state.database_connected = False

if "database_error" not in st.session_state:
    st.session_state.database_error = None

if "citizen_editor_id" not in st.session_state:
    st.session_state.citizen_editor_id = None

if "citizen_view_id" not in st.session_state:
    st.session_state.citizen_view_id = None


# ============================================================
# SAFE EMBLEM LOADING
# ============================================================

@st.cache_data(show_spinner=False)
def load_emblem() -> Any | None:
    """
    Safely load the South Sudan emblem.

    Missing, empty, corrupt or unsupported image files
    return None instead of crashing Streamlit.
    """

    try:
        if not EMBLEM_PATH.exists():
            return None

        image_bytes = EMBLEM_PATH.read_bytes()

        if not image_bytes:
            return None

        from PIL import Image

        with Image.open(
            io.BytesIO(image_bytes)
        ) as image:
            image.verify()

        image = Image.open(
            io.BytesIO(image_bytes)
        )

        image.load()

        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA")

        return image

    except Exception as exc:
        logger.warning(
            "Unable to load emblem '%s': %s",
            EMBLEM_PATH,
            exc,
        )
        return None


# ============================================================
# DATABASE
# ============================================================

try:
    from database.database import (
        SessionLocal,
        init_db,
    )

    database_import_error = None

except Exception as exc:
    SessionLocal = None
    init_db = None
    database_import_error = (
        f"{type(exc).__name__}: {exc}"
    )


@st.cache_resource(show_spinner=False)
def initialize_database() -> tuple[
    bool,
    str | None,
]:

    if init_db is None:
        return (
            False,
            database_import_error
            or "Database initialization is unavailable.",
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
            f"{type(exc).__name__}: {exc}",
        )


(
    database_connected,
    database_error,
) = initialize_database()

st.session_state.database_connected = database_connected
st.session_state.database_error = database_error


# ============================================================
# MODELS
# ============================================================

try:
    from models import (
        AuditLog,
        Citizen,
    )

    models_available = True
    models_error = None

except Exception as exc:
    Citizen = None
    AuditLog = None
    models_available = False
    models_error = (
        f"{type(exc).__name__}: {exc}"
    )

    logger.warning(
        "Registry models unavailable: %s",
        exc,
    )


# ============================================================
# MODULE REGISTRY
# ============================================================

try:
    from modules.registry import (
        get_available_modules,
        get_module,
        render_module,
    )

    registry_available = True
    registry_error = None

except Exception as exc:

    get_available_modules = None
    get_module = None
    render_module = None

    registry_available = False

    registry_error = (
        f"{type(exc).__name__}: {exc}"
    )

    logger.warning(
        "Module registry unavailable: %s",
        exc,
    )


# ============================================================
# MODULE HELPERS
# ============================================================

def load_available_modules() -> list[Any]:

    if not registry_available:
        return []

    if get_available_modules is None:
        return []

    try:
        modules = get_available_modules()

        if modules is None:
            return []

        return list(modules)

    except Exception:
        logger.exception(
            "Unable to load available modules."
        )
        return []


def load_all_modules() -> list[Any]:

    try:
        from modules.registry import MODULES

        if isinstance(MODULES, dict):
            return list(MODULES.values())

    except Exception:
        pass

    return load_available_modules()


# ============================================================
# STATIC REGISTRY FEATURES
# ============================================================

FEATURES: dict[str, tuple[str, str]] = {

    "citizens": (
        "Citizens",
        (
            "Citizen population records and citizen "
            "registry management."
        ),
    ),

    "population": (
        "Population Registry",
        (
            "Manage national population records, "
            "households, persons and demographic "
            "information."
        ),
    ),

    "civil_registration": (
        "Civil Registration",
        (
            "Register births, deaths, marriages, "
            "certificates and other civil events."
        ),
    ),

    "identity": (
        "Identity Management",
        (
            "Manage national identity registration, "
            "identification records and identity services."
        ),
    ),

    "elections": (
        "Elections",
        (
            "Manage electoral registration, voter records "
            "and election administration."
        ),
    ),

    "households": (
        "Households",
        (
            "Manage household records and household "
            "relationships."
        ),
    ),

    "documents": (
        "Documents",
        (
            "Manage Registry documents, certificates "
            "and official records."
        ),
    ),

    "verification": (
        "Verification",
        (
            "Verify population, civil registration and "
            "identity records."
        ),
    ),

    "reports": (
        "Reports & Analytics",
        (
            "Generate operational reports, statistical "
            "summaries and Registry analytics."
        ),
    ),

    "statistics": (
        "Statistics",
        (
            "View national Registry statistics and "
            "demographic summaries."
        ),
    ),

    "audit": (
        "Audit & Activity",
        (
            "Review Registry activity, administrative "
            "events and audit information."
        ),
    ),

    "administration": (
        "Administration",
        (
            "Manage users, roles, permissions, "
            "configuration and system administration."
        ),
    ),

    "settings": (
        "System Settings",
        (
            "Configure Registry platform settings "
            "and system preferences."
        ),
    ),
}


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
            "success": "#22C55E",
            "warning": "#F59E0B",
            "danger": "#EF4444",
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
        "success": "#15803D",
        "warning": "#D97706",
        "danger": "#DC2626",
    }


# ============================================================
# CSS
# ============================================================

def inject_css() -> None:

    theme = get_theme()

    st.markdown(
        f"""
<style>

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

/* SIDEBAR */

section[data-testid="stSidebar"] {{
    background: {theme["surface"]};
    border-right: 1px solid {theme["border"]};
}}

section[data-testid="stSidebar"] * {{
    color: {theme["text"]};
}}

section[data-testid="stSidebar"] .stButton > button {{
    width: 100%;
    border-radius: 9px;
    min-height: 38px;
    text-align: left;
    font-weight: 600;
    background: transparent;
    border: 1px solid transparent;
}}

section[data-testid="stSidebar"] .stButton > button:hover {{
    background: {theme["surface_hover"]};
    border-color: {theme["border"]};
}}

/* HEADER */

.registry-header {{
    background: {theme["surface"]};
    border: 1px solid {theme["border"]};
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 20px;
}}

.registry-emblem {{
    width: 64px;
    height: 64px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: {theme["accent"]};
    border: 3px solid #FBBF24;
    color: #FFFFFF !important;
    font-size: 18px;
    font-weight: 900;
}}

.registry-brand-title {{
    font-size: 28px;
    font-weight: 800;
    line-height: 1.2;
}}

.registry-brand-subtitle {{
    margin-top: 6px;
    font-size: 13px;
    color: {theme["muted"]} !important;
}}

.registry-version {{
    font-size: 12px;
    color: {theme["muted"]} !important;
    margin-top: 3px;
}}

/* PAGE */

.page-card {{
    background: {theme["surface"]};
    border: 1px solid {theme["border"]};
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 18px;
}}

/* KPI */

div[data-testid="stMetric"] {{
    background: {theme["surface"]};
    border: 1px solid {theme["border"]};
    border-radius: 14px;
    padding: 15px;
}}

div[data-testid="stMetricLabel"] {{
    color: {theme["muted"]} !important;
}}

div[data-testid="stMetricValue"] {{
    color: {theme["text"]} !important;
}}

/* TABLE */

div[data-testid="stDataFrame"] {{
    border: 1px solid {theme["border"]};
    border-radius: 12px;
}}

/* BUTTONS */

.stButton > button {{
    border-radius: 9px;
    font-weight: 600;
    min-height: 38px;
}}

/* FOOTER */

.registry-footer {{
    color: {theme["muted"]} !important;
    font-size: 11px;
}}

/* STREAMLIT CHROME */

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


# ============================================================
# SIDEBAR
# ============================================================

def sidebar_button(
    key: str,
    label: str,
) -> None:

    if st.button(
        label,
        key=f"nav_{key}",
        use_container_width=True,
    ):

        st.session_state.active_module = key
        st.session_state.citizen_editor_id = None
        st.session_state.citizen_view_id = None

        st.rerun()


def render_sidebar() -> None:

    with st.sidebar:

        emblem = load_emblem()

        if emblem is not None:

            st.image(
                emblem,
                width=64,
            )

        else:

            st.markdown(
                '<div class="registry-emblem">SS</div>',
                unsafe_allow_html=True,
            )

        st.subheader(
            "South Sudan National Registry"
        )

        st.caption(
            "National Population • Civil Registration • "
            "Identity • Elections"
        )

        if database_connected:

            st.success(
                "System Online"
            )

        else:

            st.warning(
                "Database Attention Required"
            )

        st.divider()

        st.markdown("**Registry**")

        sidebar_button(
            "overview",
            "Overview",
        )

        sidebar_button(
            "citizens",
            "Citizens",
        )

        sidebar_button(
            "population",
            "Population Registry",
        )

        sidebar_button(
            "civil_registration",
            "Civil Registration",
        )

        sidebar_button(
            "identity",
            "Identity Management",
        )

        sidebar_button(
            "elections",
            "Elections",
        )

        st.markdown("**Operations**")

        sidebar_button(
            "households",
            "Households",
        )

        sidebar_button(
            "documents",
            "Documents",
        )

        sidebar_button(
            "verification",
            "Verification",
        )

        sidebar_button(
            "reports",
            "Reports & Analytics",
        )

        st.markdown("**Administration**")

        sidebar_button(
            "administration",
            "Administration",
        )

        sidebar_button(
            "settings",
            "System Settings",
        )

        st.markdown("**Other Features**")

        sidebar_button(
            "statistics",
            "Statistics",
        )

        sidebar_button(
            "audit",
            "Audit & Activity",
        )

        st.divider()

        theme_label = (
            "Switch to Light Mode"
            if st.session_state.dark_mode
            else "Switch to Dark Mode"
        )

        if st.button(
            theme_label,
            key="theme_button",
            use_container_width=True,
        ):

            st.session_state.dark_mode = (
                not st.session_state.dark_mode
            )

            st.rerun()

        if st.button(
            "Refresh Application",
            key="refresh_button",
            use_container_width=True,
        ):

            st.rerun()

        st.divider()

        st.caption("Registry Platform")
        st.caption("Version 1.0.0")


# ============================================================
# MAIN HEADER
# ============================================================

def render_header() -> None:

    emblem = load_emblem()

    with st.container(
        border=True
    ):

        col1, col2, col3 = st.columns(
            [1, 7, 2],
            vertical_alignment="center",
        )

        with col1:

            if emblem is not None:

                st.image(
                    emblem,
                    width=64,
                )

            else:

                st.markdown(
                    '<div class="registry-emblem">SS</div>',
                    unsafe_allow_html=True,
                )

        with col2:

            st.markdown(
                '<div class="registry-brand-title">'
                'South Sudan National Registry'
                '</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="registry-brand-subtitle">'
                'National Population • Civil Registration • '
                'Identity • Elections'
                '</div>',
                unsafe_allow_html=True,
            )

        with col3:

            if database_connected:

                st.success(
                    "System Online"
                )

            else:

                st.warning(
                    "Database Attention"
                )

            st.caption(
                "Registry Platform"
            )

            st.caption(
                "Version 1.0.0"
            )


# ============================================================
# PAGE HEADER
# ============================================================

def render_page_header(
    title: str,
    description: str,
) -> None:

    with st.container(
        border=True
    ):

        st.caption(
            "South Sudan National Registry"
        )

        st.header(
            title
        )

        st.write(
            description
        )


# ============================================================
# KPI
# ============================================================

def render_kpi(
    label: str,
    value: Any,
    description: str,
) -> None:

    with st.container(
        border=True
    ):

        st.metric(
            label=str(label),
            value=str(value),
        )

        st.caption(
            str(description)
        )


# ============================================================
# SERVICE CARD
# ============================================================

def render_service_card(
    title: str,
    description: str,
) -> None:

    with st.container(
        border=True
    ):

        st.subheader(
            title
        )

        st.caption(
            description
        )


# ============================================================
# DATABASE SESSION
# ============================================================

def get_session():
    """
    Create a SQLAlchemy database session.

    Returns None when the database layer is unavailable.
    """

    if not database_connected:
        return None

    if SessionLocal is None:
        return None

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
    entity_type: str,
    entity_id: str | None,
    details: str,
) -> None:

    if AuditLog is None:
        return

    try:

        audit = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            username="streamlit",
            created_at=datetime.utcnow(),
            details=details,
        )

        db.add(audit)

    except Exception:
        logger.exception(
            "Unable to create audit log."
        )


# ============================================================
# CITIZEN UTILITIES
# ============================================================

def calculate_age(
    birth_date: date | None,
) -> int:

    if birth_date is None:
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

    return max(
        0,
        age,
    )


def clean_optional(
    value: Any,
) -> str | None:

    if value is None:
        return None

    value = str(value).strip()

    return value or None


# ============================================================
# CITIZEN COUNT
# ============================================================

def get_citizen_count() -> int:

    if Citizen is None:
        return 0

    db = get_session()

    if db is None:
        return 0

    try:

        return int(
            db.query(Citizen).count()
        )

    except Exception:

        logger.exception(
            "Unable to count citizens."
        )

        return 0

    finally:

        db.close()


# ============================================================
# CITIZEN SEARCH
# ============================================================

def search_citizens(
    search_text: str = "",
    state: str = "",
    verification_status: str = "All",
) -> list[Any]:

    if Citizen is None:
        return []

    db = get_session()

    if db is None:
        return []

    try:

        query = db.query(Citizen)

        search_text = search_text.strip()

        if search_text:

            pattern = (
                f"%{search_text}%"
            )

            query = query.filter(
                (
                    Citizen.full_name.ilike(pattern)
                )
                |
                (
                    Citizen.national_id.ilike(pattern)
                )
                |
                (
                    Citizen.passport_number.ilike(pattern)
                )
                |
                (
                    Citizen.phone_number.ilike(pattern)
                )
            )

        if state:

            query = query.filter(
                Citizen.state_or_region == state
            )

        if (
            verification_status
            and verification_status != "All"
        ):

            query = query.filter(
                Citizen.verification_status
                == verification_status
            )

        return (
            query
            .order_by(
                Citizen.created_at.desc()
            )
            .limit(500)
            .all()
        )

    except Exception:

        logger.exception(
            "Unable to search citizens."
        )

        return []

    finally:

        db.close()


# ============================================================
# CITIZEN LOAD
# ============================================================

def get_citizen(
    citizen_id: str,
) -> Any | None:

    if Citizen is None:
        return None

    db = get_session()

    if db is None:
        return None

    try:

        return (
            db.query(Citizen)
            .filter(
                Citizen.id == citizen_id
            )
            .first()
        )

    except Exception:

        logger.exception(
            "Unable to load citizen."
        )

        return None

    finally:

        db.close()


# ============================================================
# CITIZEN FORM
# ============================================================

def render_citizen_form(
    citizen: Any | None = None,
) -> None:

    editing = citizen is not None

    if editing:

        st.subheader(
            "Edit Citizen"
        )

        st.caption(
            f"Citizen ID: {citizen.id}"
        )

    else:

        st.subheader(
            "Register New Citizen"
        )

        st.caption(
            "Create a new national population record."
        )


    # --------------------------------------------------------
    # BASIC IDENTITY
    # --------------------------------------------------------

    st.markdown("### Identity")

    col1, col2, col3 = st.columns(3)

    with col1:

        national_id = st.text_input(
            "National ID",
            value=(
                citizen.national_id
                if editing
                else ""
            )
            or "",
            key=(
                "citizen_national_id_edit"
                if editing
                else "citizen_national_id_new"
            ),
        )

    with col2:

        passport_number = st.text_input(
            "Passport Number",
            value=(
                citizen.passport_number
                if editing
                else ""
            )
            or "",
            key=(
                "citizen_passport_edit"
                if editing
                else "citizen_passport_new"
            ),
        )

    with col3:

        id_document_type = st.selectbox(
            "ID Document Type",
            [
                "",
                "National ID",
                "Passport",
                "Birth Certificate",
                "Other",
            ],
            index=(
                [
                    "",
                    "National ID",
                    "Passport",
                    "Birth Certificate",
                    "Other",
                ].index(
                    citizen.id_document_type
                )
                if editing
                and citizen.id_document_type
                in [
                    "",
                    "National ID",
                    "Passport",
                    "Birth Certificate",
                    "Other",
                ]
                else 0
            ),
            key=(
                "citizen_id_type_edit"
                if editing
                else "citizen_id_type_new"
            ),
        )


    full_name = st.text_input(
        "Full Name *",
        value=(
            citizen.full_name
            if editing
            else ""
        )
        or "",
        key=(
            "citizen_full_name_edit"
            if editing
            else "citizen_full_name_new"
        ),
    )


    col1, col2, col3 = st.columns(3)

    with col1:

        date_of_birth = st.date_input(
            "Date of Birth",
            value=(
                citizen.date_of_birth
                if editing
                and citizen.date_of_birth
                else date(
                    2000,
                    1,
                    1,
                )
            ),
            key=(
                "citizen_dob_edit"
                if editing
                else "citizen_dob_new"
            ),
        )

    with col2:

        gender_options = [
            "Male",
            "Female",
            "Other",
        ]

        gender = st.selectbox(
            "Gender",
            gender_options,
            index=(
                gender_options.index(
                    citizen.gender
                )
                if editing
                and citizen.gender in gender_options
                else 2
            ),
            key=(
                "citizen_gender_edit"
                if editing
                else "citizen_gender_new"
            ),
        )

    with col3:

        marital_options = [
            "Single",
            "Married",
            "Divorced",
            "Widowed",
            "Separated",
            "Other",
        ]

        marital_status = st.selectbox(
            "Marital Status",
            marital_options,
            index=(
                marital_options.index(
                    citizen.marital_status
                )
                if editing
                and citizen.marital_status
                in marital_options
                else 0
            ),
            key=(
                "citizen_marital_edit"
                if editing
                else "citizen_marital_new"
            ),
        )


    nationality = st.text_input(
        "Nationality",
        value=(
            citizen.nationality
            if editing
            else "South Sudanese"
        )
        or "South Sudanese",
        key=(
            "citizen_nationality_edit"
            if editing
            else "citizen_nationality_new"
        ),
    )


    # --------------------------------------------------------
    # CONTACT
    # --------------------------------------------------------

    st.markdown("### Contact")

    col1, col2 = st.columns(2)

    with col1:

        phone_number = st.text_input(
            "Phone Number",
            value=(
                citizen.phone_number
                if editing
                else ""
            )
            or "",
            key=(
                "citizen_phone_edit"
                if editing
                else "citizen_phone_new"
            ),
        )

    with col2:

        email_address = st.text_input(
            "Email Address",
            value=(
                citizen.email_address
                if editing
                else ""
            )
            or "",
            key=(
                "citizen_email_edit"
                if editing
                else "citizen_email_new"
            ),
        )


    col1, col2 = st.columns(2)

    with col1:

        emergency_contact_name = st.text_input(
            "Emergency Contact Name",
            value=(
                citizen.emergency_contact_name
                if editing
                else ""
            )
            or "",
            key=(
                "citizen_emergency_name_edit"
                if editing
                else "citizen_emergency_name_new"
            ),
        )

    with col2:

        emergency_contact_phone = st.text_input(
            "Emergency Contact Phone",
            value=(
                citizen.emergency_contact_phone
                if editing
                else ""
            )
            or "",
            key=(
                "citizen_emergency_phone_edit"
                if editing
                else "citizen_emergency_phone_new"
            ),
        )


    # --------------------------------------------------------
    # DEMOGRAPHICS
    # --------------------------------------------------------

    st.markdown("### Demographics")

    col1, col2 = st.columns(2)

    with col1:

        tribe = st.text_input(
            "Tribe",
            value=(
                citizen.tribe
                if editing
                else ""
            )
            or "",
            key=(
                "citizen_tribe_edit"
                if editing
                else "citizen_tribe_new"
            ),
        )

    with col2:

        sub_tribe_or_clan = st.text_input(
            "Sub-Tribe / Clan",
            value=(
                citizen.sub_tribe_or_clan
                if editing
                else ""
            )
            or "",
            key=(
                "citizen_clan_edit"
                if editing
                else "citizen_clan_new"
            ),
        )


    native_language = st.text_input(
        "Native Language",
        value=(
            citizen.native_language
            if editing
            else ""
        )
        or "",
        key=(
            "citizen_language_edit"
            if editing
            else "citizen_language_new"
        ),
    )


    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    st.markdown("### Location")

    col1, col2 = st.columns(2)

    with col1:

        state_or_region = st.text_input(
            "State / Region",
            value=(
                citizen.state_or_region
                if editing
                else ""
            )
            or "",
            key=(
                "citizen_state_edit"
                if editing
                else "citizen_state_new"
            ),
        )

    with col2:

        county_or_payam = st.text_input(
            "County / Payam",
            value=(
                citizen.county_or_payam
                if editing
                else ""
            )
            or "",
            key=(
                "citizen_county_edit"
                if editing
                else "citizen_county_new"
            ),
        )


    col1, col2 = st.columns(2)

    with col1:

        sub_county_or_boma = st.text_input(
            "Sub-County / Boma",
            value=(
                citizen.sub_county_or_boma
                if editing
                else ""
            )
            or "",
            key=(
                "citizen_subcounty_edit"
                if editing
                else "citizen_subcounty_new"
            ),
        )

    with col2:

        boma = st.text_input(
            "Boma",
            value=(
                citizen.boma
                if editing
                else ""
            )
            or "",
            key=(
                "citizen_boma_edit"
                if editing
                else "citizen_boma_new"
            ),
        )


    community = st.text_input(
        "Community",
        value=(
            citizen.community
            if editing
            else ""
        )
        or "",
        key=(
            "citizen_community_edit"
            if editing
            else "citizen_community_new"
        ),
    )


    residential_address = st.text_area(
        "Residential Address",
        value=(
            citizen.residential_address
            if editing
            else ""
        )
        or "",
        key=(
            "citizen_address_edit"
            if editing
            else "citizen_address_new"
        ),
    )


    duration_of_stay_years = st.number_input(
        "Duration of Stay (Years)",
        min_value=0.0,
        max_value=200.0,
        value=float(
            citizen.duration_of_stay_years
            if editing
            else 0.0
        ),
        step=0.5,
        key=(
            "citizen_stay_edit"
            if editing
            else "citizen_stay_new"
        ),
    )


    # --------------------------------------------------------
    # HOUSEHOLD
    # --------------------------------------------------------

    st.markdown("### Household")

    household_id = st.text_input(
        "Household ID",
        value=(
            citizen.household_id
            if editing
            else ""
        )
        or "",
        key=(
            "citizen_household_id_edit"
            if editing
            else "citizen_household_id_new"
        ),
    )


    household_role_options = [
        "Head of Household",
        "Spouse",
        "Child",
        "Parent",
        "Relative",
        "Other",
    ]

    household_role = st.selectbox(
        "Household Role",
        household_role_options,
        index=(
            household_role_options.index(
                citizen.household_role
            )
            if editing
            and citizen.household_role
            in household_role_options
            else 0
        ),
        key=(
            "citizen_household_role_edit"
            if editing
            else "citizen_household_role_new"
        ),
    )


    is_household_head = st.checkbox(
        "Is Head of Household",
        value=bool(
            citizen.is_household_head
            if editing
            else False
        ),
        key=(
            "citizen_household_head_edit"
            if editing
            else "citizen_household_head_new"
        ),
    )


    # --------------------------------------------------------
    # EDUCATION
    # --------------------------------------------------------

    st.markdown("### Education")

    education_options = [
        "None / Informal",
        "Primary",
        "Secondary",
        "Certificate",
        "Diploma",
        "Bachelor's",
        "Master's",
        "Doctorate",
        "Other",
    ]

    education_level = st.selectbox(
        "Education Level",
        education_options,
        index=(
            education_options.index(
                citizen.education_level
            )
            if editing
            and citizen.education_level
            in education_options
            else 0
        ),
        key=(
            "citizen_education_edit"
            if editing
            else "citizen_education_new"
        ),
    )


    is_literate = st.checkbox(
        "Literate",
        value=bool(
            citizen.is_literate
            if editing
            else False
        ),
        key=(
            "citizen_literate_edit"
            if editing
            else "citizen_literate_new"
        ),
    )


    # --------------------------------------------------------
    # EMPLOYMENT
    # --------------------------------------------------------

    st.markdown("### Employment")

    employment_options = [
        "Employed",
        "Self-Employed",
        "Farmer",
        "Student",
        "Unemployed / Seeking Work",
        "Retired",
        "Other",
    ]

    employment_status = st.selectbox(
        "Employment Status",
        employment_options,
        index=(
            employment_options.index(
                citizen.employment_status
            )
            if editing
            and citizen.employment_status
            in employment_options
            else 4
        ),
        key=(
            "citizen_employment_edit"
            if editing
            else "citizen_employment_new"
        ),
    )


    col1, col2 = st.columns(2)

    with col1:

        primary_occupation = st.text_input(
            "Primary Occupation",
            value=(
                citizen.primary_occupation
                if editing
                else ""
            )
            or "",
            key=(
                "citizen_occupation_edit"
                if editing
                else "citizen_occupation_new"
            ),
        )

    with col2:

        employer_or_business_name = st.text_input(
            "Employer / Business Name",
            value=(
                citizen.employer_or_business_name
                if editing
                else ""
            )
            or "",
            key=(
                "citizen_employer_edit"
                if editing
                else "citizen_employer_new"
            ),
        )


    industry_sector = st.text_input(
        "Industry Sector",
        value=(
            citizen.industry_sector
            if editing
            else ""
        )
        or "",
        key=(
            "citizen_industry_edit"
            if editing
            else "citizen_industry_new"
        ),
    )


    monthly_income_range = st.text_input(
        "Monthly Income Range",
        value=(
            citizen.monthly_income_range
            if editing
            else ""
        )
        or "",
        key=(
            "citizen_income_edit"
            if editing
            else "citizen_income_new"
        ),
    )


    # --------------------------------------------------------
    # SPECIAL NEEDS
    # --------------------------------------------------------

    st.markdown("### Special Needs")

    has_special_needs = st.checkbox(
        "Has Special Needs / Disability",
        value=bool(
            citizen.has_special_needs_or_disability
            if editing
            else False
        ),
        key=(
            "citizen_special_needs_edit"
            if editing
            else "citizen_special_needs_new"
        ),
    )


    disability_type = st.text_input(
        "Disability Type",
        value=(
            citizen.disability_type
            if editing
            else ""
        )
        or "",
        key=(
            "citizen_disability_edit"
            if editing
            else "citizen_disability_new"
        ),
    )


    col1, col2 = st.columns(2)

    with col1:

        mother_alive = st.selectbox(
            "Mother Alive",
            [
                "Unknown",
                "Yes",
                "No",
            ],
            index=(
                1
                if editing
                and citizen.mother_alive is True
                else 2
                if editing
                and citizen.mother_alive is False
                else 0
            ),
            key=(
                "citizen_mother_edit"
                if editing
                else "citizen_mother_new"
            ),
        )

    with col2:

        father_alive = st.selectbox(
            "Father Alive",
            [
                "Unknown",
                "Yes",
                "No",
            ],
            index=(
                1
                if editing
                and citizen.father_alive is True
                else 2
                if editing
                and citizen.father_alive is False
                else 0
            ),
            key=(
                "citizen_father_edit"
                if editing
                else "citizen_father_new"
            ),
        )


    # --------------------------------------------------------
    # ELECTIONS
    # --------------------------------------------------------

    st.markdown("### Elections")

    col1, col2 = st.columns(2)

    with col1:

        voter_id_number = st.text_input(
            "Voter ID Number",
            value=(
                citizen.voter_id_number
                if editing
                else ""
            )
            or "",
            key=(
                "citizen_voter_id_edit"
                if editing
                else "citizen_voter_id_new"
            ),
        )

    with col2:

        voter_status_options = [
            "",
            "Active",
            "Inactive",
            "Suspended",
            "Pending",
        ]

        voter_status = st.selectbox(
            "Voter Status",
            voter_status_options,
            index=(
                voter_status_options.index(
                    citizen.voter_status
                )
                if editing
                and citizen.voter_status
                in voter_status_options
                else 0
            ),
            key=(
                "citizen_voter_status_edit"
                if editing
                else "citizen_voter_status_new"
            ),
        )


    col1, col2 = st.columns(2)

    with col1:

        constituency = st.text_input(
            "Constituency",
            value=(
                citizen.constituency
                if editing
                else ""
            )
            or "",
            key=(
                "citizen_constituency_edit"
                if editing
                else "citizen_constituency_new"
            ),
        )

    with col2:

        polling_station_id = st.text_input(
            "Polling Station ID",
            value=(
                citizen.polling_station_id
                if editing
                else ""
            )
            or "",
            key=(
                "citizen_polling_id_edit"
                if editing
                else "citizen_polling_id_new"
            ),
        )


    polling_station_name = st.text_input(
        "Polling Station Name",
        value=(
            citizen.polling_station_name
            if editing
            else ""
        )
        or "",
        key=(
            "citizen_polling_name_edit"
            if editing
            else "citizen_polling_name_new"
        ),
    )


    has_voted = st.checkbox(
        "Has Voted",
        value=bool(
            citizen.has_voted
            if editing
            else False
        ),
        key=(
            "citizen_has_voted_edit"
            if editing
            else "citizen_has_voted_new"
        ),
    )


    # --------------------------------------------------------
    # ENUMERATION
    # --------------------------------------------------------

    st.markdown("### Enumeration")

    col1, col2 = st.columns(2)

    with col1:

        enumerator_name = st.text_input(
            "Enumerator Name",
            value=(
                citizen.enumerator_name
                if editing
                else ""
            )
            or "",
            key=(
                "citizen_enumerator_edit"
                if editing
                else "citizen_enumerator_new"
            ),
        )

    with col2:

        enumerator_badge_id = st.text_input(
            "Enumerator Badge ID",
            value=(
                citizen.enumerator_badge_id
                if editing
                else ""
            )
            or "",
            key=(
                "citizen_badge_edit"
                if editing
                else "citizen_badge_new"
            ),
        )


    enumeration_date = st.date_input(
        "Enumeration Date",
        value=(
            citizen.enumeration_date
            if editing
            and citizen.enumeration_date
            else date.today()
        ),
        key=(
            "citizen_enum_date_edit"
            if editing
            else "citizen_enum_date_new"
        ),
    )


    # --------------------------------------------------------
    # VERIFICATION
    # --------------------------------------------------------

    st.markdown("### Verification")

    verification_options = [
        "Pending Review",
        "Verified",
        "Rejected",
        "Suspended",
        "Archived",
    ]

    verification_status = st.selectbox(
        "Verification Status",
        verification_options,
        index=(
            verification_options.index(
                citizen.verification_status
            )
            if editing
            and citizen.verification_status
            in verification_options
            else 0
        ),
        key=(
            "citizen_verification_edit"
            if editing
            else "citizen_verification_new"
        ),
    )


    verification_notes = st.text_area(
        "Verification Notes",
        value=(
            citizen.verification_notes
            if editing
            else ""
        )
        or "",
        key=(
            "citizen_verification_notes_edit"
            if editing
            else "citizen_verification_notes_new"
        ),
    )


    notes = st.text_area(
        "Notes",
        value=(
            citizen.notes
            if editing
            else ""
        )
        or "",
        key=(
            "citizen_notes_edit"
            if editing
            else "citizen_notes_new"
        ),
    )


    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    st.divider()

    col1, col2, col3 = st.columns(
        3
    )


    with col1:

        save_label = (
            "Update Citizen"
            if editing
            else "Register Citizen"
        )

        save_clicked = st.button(
            save_label,
            key=(
                "save_citizen_edit"
                if editing
                else "save_citizen_new"
            ),
            use_container_width=True,
        )


    with col2:

        cancel_clicked = st.button(
            "Cancel",
            key=(
                "cancel_citizen_edit"
                if editing
                else "cancel_citizen_new"
            ),
            use_container_width=True,
        )


    with col3:

        if editing:

            archive_clicked = st.button(
                "Archive Citizen",
                key="archive_citizen",
                use_container_width=True,
            )

        else:

            archive_clicked = False


    if cancel_clicked:

        st.session_state.citizen_editor_id = None
        st.rerun()


    if archive_clicked and editing:

        archive_citizen(
            citizen.id
        )


    if not save_clicked:

        return


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    errors: list[str] = []


    if not full_name.strip():

        errors.append(
            "Full Name is required."
        )


    if date_of_birth > date.today():

        errors.append(
            "Date of Birth cannot be in the future."
        )


    if (
        has_special_needs
        and not disability_type.strip()
    ):

        errors.append(
            "Please specify the disability type."
        )


    if errors:

        for error in errors:

            st.error(
                error
            )

        return


    # --------------------------------------------------------
    # DATABASE WRITE
    # --------------------------------------------------------

    save_citizen(
        citizen=citizen,
        national_id=clean_optional(
            national_id
        ),
        passport_number=clean_optional(
            passport_number
        ),
        id_document_type=clean_optional(
            id_document_type
        ),
        full_name=full_name.strip(),
        date_of_birth=date_of_birth,
        gender=gender,
        marital_status=marital_status,
        nationality=nationality.strip()
        or "South Sudanese",
        phone_number=clean_optional(
            phone_number
        ),
        email_address=clean_optional(
            email_address
        ),
        emergency_contact_name=clean_optional(
            emergency_contact_name
        ),
        emergency_contact_phone=clean_optional(
            emergency_contact_phone
        ),
        tribe=tribe.strip(),
        sub_tribe_or_clan=clean_optional(
            sub_tribe_or_clan
        ),
        native_language=native_language.strip(),
        state_or_region=state_or_region.strip(),
        county_or_payam=county_or_payam.strip(),
        sub_county_or_boma=sub_county_or_boma.strip(),
        boma=clean_optional(
            boma
        ),
        community=community.strip(),
        residential_address=clean_optional(
            residential_address
        ),
        duration_of_stay_years=float(
            duration_of_stay_years
        ),
        household_id=clean_optional(
            household_id
        ),
        household_role=household_role,
        is_household_head=is_household_head,
        education_level=education_level,
        is_literate=is_literate,
        employment_status=employment_status,
        primary_occupation=clean_optional(
            primary_occupation
        ),
        employer_or_business_name=clean_optional(
            employer_or_business_name
        ),
        industry_sector=clean_optional(
            industry_sector
        ),
        monthly_income_range=clean_optional(
            monthly_income_range
        ),
        has_special_needs_or_disability=has_special_needs,
        disability_type=clean_optional(
            disability_type
        ),
        mother_alive=(
            True
            if mother_alive == "Yes"
            else False
            if mother_alive == "No"
            else None
        ),
        father_alive=(
            True
            if father_alive == "Yes"
            else False
            if father_alive == "No"
            else None
        ),
        voter_id_number=clean_optional(
            voter_id_number
        ),
        voter_status=clean_optional(
            voter_status
        ),
        constituency=clean_optional(
            constituency
        ),
        polling_station_id=clean_optional(
            polling_station_id
        ),
        polling_station_name=clean_optional(
            polling_station_name
        ),
        has_voted=has_voted,
        enumerator_name=enumerator_name.strip(),
        enumerator_badge_id=enumerator_badge_id.strip(),
        enumeration_date=enumeration_date,
        verification_status=verification_status,
        verification_notes=clean_optional(
            verification_notes
        ),
        notes=clean_optional(
            notes
        ),
    )


# ============================================================
# SAVE CITIZEN
# ============================================================

def save_citizen(
    citizen: Any | None,
    **values: Any,
) -> None:

    if not database_connected:

        st.error(
            "The database is not connected. "
            "Citizen records cannot be saved."
        )

        return


    if Citizen is None:

        st.error(
            "The Citizen database model is unavailable."
        )

        return


    db = get_session()

    if db is None:

        st.error(
            "Unable to open a database session."
        )

        return


    try:

        national_id = values.get(
            "national_id"
        )

        voter_id_number = values.get(
            "voter_id_number"
        )


        # ----------------------------------------------------
        # Duplicate National ID
        # ----------------------------------------------------

        if national_id:

            query = db.query(
                Citizen
            ).filter(
                Citizen.national_id
                == national_id
            )

            if citizen is not None:

                query = query.filter(
                    Citizen.id
                    != citizen.id
                )

            if query.first():

                st.error(
                    "A citizen with this National ID "
                    "already exists."
                )

                return


        # ----------------------------------------------------
        # Duplicate Voter ID
        # ----------------------------------------------------

        if voter_id_number:

            query = db.query(
                Citizen
            ).filter(
                Citizen.voter_id_number
                == voter_id_number
            )

            if citizen is not None:

                query = query.filter(
                    Citizen.id
                    != citizen.id
                )

            if query.first():

                st.error(
                    "A citizen with this Voter ID "
                    "already exists."
                )

                return


        # ----------------------------------------------------
        # CREATE
        # ----------------------------------------------------

        if citizen is None:

            import uuid

            citizen = Citizen(
                id=str(
                    uuid.uuid4()
                ),
                created_at=datetime.utcnow(),
            )

            db.add(
                citizen
            )

            action = "CREATE"

            message = (
                "Citizen record created."
            )


        # ----------------------------------------------------
        # UPDATE
        # ----------------------------------------------------

        else:

            action = "UPDATE"

            message = (
                "Citizen record updated."
            )


        # ----------------------------------------------------
        # Assign values
        # ----------------------------------------------------

        for field_name, value in values.items():

            if hasattr(
                citizen,
                field_name,
            ):

                setattr(
                    citizen,
                    field_name,
                    value,
                )


        citizen.age = calculate_age(
            values.get(
                "date_of_birth"
            )
        )

        citizen.updated_at = datetime.utcnow()


        # ----------------------------------------------------
        # Audit
        # ----------------------------------------------------

        write_audit(
            db=db,
            action=action,
            entity_type="Citizen",
            entity_id=str(
                citizen.id
            ),
            details=message,
        )


        db.commit()


        st.session_state.citizen_editor_id = None
        st.session_state.citizen_view_id = (
            str(citizen.id)
        )


        st.success(
            message
        )

        st.rerun()


    except Exception as exc:

        db.rollback()

        logger.exception(
            "Unable to save citizen."
        )

        st.error(
            "The citizen record could not be saved."
        )

        with st.expander(
            "Technical details"
        ):

            st.exception(exc)

    finally:

        db.close()


# ============================================================
# ARCHIVE CITIZEN
# ============================================================

def archive_citizen(
    citizen_id: str,
) -> None:

    if not database_connected:

        st.error(
            "The database is not connected."
        )

        return


    if Citizen is None:

        st.error(
            "The Citizen model is unavailable."
        )

        return


    db = get_session()

    if db is None:

        st.error(
            "Unable to open a database session."
        )

        return


    try:

        citizen = (
            db.query(Citizen)
            .filter(
                Citizen.id == citizen_id
            )
            .first()
        )


        if citizen is None:

            st.error(
                "Citizen record not found."
            )

            return


        citizen.verification_status = (
            "Archived"
        )

        citizen.updated_at = datetime.utcnow()


        write_audit(
            db=db,
            action="ARCHIVE",
            entity_type="Citizen",
            entity_id=str(
                citizen.id
            ),
            details=(
                "Citizen record archived from "
                "the active registry."
            ),
        )


        db.commit()


        st.session_state.citizen_editor_id = None
        st.session_state.citizen_view_id = None


        st.success(
            "Citizen record archived."
        )

        st.rerun()


    except Exception as exc:

        db.rollback()

        logger.exception(
            "Unable to archive citizen."
        )

        st.error(
            "The citizen record could not be archived."
        )

        with st.expander(
            "Technical details"
        ):

            st.exception(exc)

    finally:

        db.close()


# ============================================================
# CITIZEN PROFILE
# ============================================================

def render_citizen_profile(
    citizen: Any,
) -> None:

    st.subheader(
        "Citizen Profile"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Age",
            citizen.age or 0,
        )


    with col2:

        st.metric(
            "Verification",
            citizen.verification_status
            or "Pending Review",
        )


    with col3:

        st.metric(
            "Voter Status",
            citizen.voter_status
            or "Not Registered",
        )


    st.divider()


    st.markdown(
        f"### {citizen.full_name}"
    )


    identity_col1, identity_col2 = st.columns(2)


    with identity_col1:

        st.write(
            f"**National ID:** "
            f"{citizen.national_id or 'Not provided'}"
        )

        st.write(
            f"**Passport:** "
            f"{citizen.passport_number or 'Not provided'}"
        )

        st.write(
            f"**Date of Birth:** "
            f"{citizen.date_of_birth or 'Not provided'}"
        )

        st.write(
            f"**Gender:** "
            f"{citizen.gender}"
        )

        st.write(
            f"**Marital Status:** "
            f"{citizen.marital_status}"
        )

    with identity_col2:

        st.write(
            f"**Nationality:** "
            f"{citizen.nationality}"
        )

        st.write(
            f"**Phone:** "
            f"{citizen.phone_number or 'Not provided'}"
        )

        st.write(
            f"**Email:** "
            f"{citizen.email_address or 'Not provided'}"
        )

        st.write(
            f"**Tribe:** "
            f"{citizen.tribe or 'Not provided'}"
        )

        st.write(
            f"**Language:** "
            f"{citizen.native_language or 'Not provided'}"
        )


    st.divider()

    st.markdown(
        "### Location"
    )


    st.write(
        f"**State / Region:** "
        f"{citizen.state_or_region or 'Not provided'}"
    )

    st.write(
        f"**County / Payam:** "
        f"{citizen.county_or_payam or 'Not provided'}"
    )

    st.write(
        f"**Sub-County / Boma:** "
        f"{citizen.sub_county_or_boma or 'Not provided'}"
    )

    st.write(
        f"**Community:** "
        f"{citizen.community or 'Not provided'}"
    )

    st.write(
        f"**Address:** "
        f"{citizen.residential_address or 'Not provided'}"
    )


    st.divider()

    st.markdown(
        "### Household"
    )


    st.write(
        f"**Household ID:** "
        f"{citizen.household_id or 'Not assigned'}"
    )

    st.write(
        f"**Household Role:** "
        f"{citizen.household_role}"
    )

    st.write(
        f"**Head of Household:** "
        f"{'Yes' if citizen.is_household_head else 'No'}"
    )


    st.divider()

    st.markdown(
        "### Education & Employment"
    )


    col1, col2 = st.columns(2)


    with col1:

        st.write(
            f"**Education:** "
            f"{citizen.education_level}"
        )

        st.write(
            f"**Literate:** "
            f"{'Yes' if citizen.is_literate else 'No'}"
        )

    with col2:

        st.write(
            f"**Employment:** "
            f"{citizen.employment_status}"
        )

        st.write(
            f"**Occupation:** "
            f"{citizen.primary_occupation or 'Not provided'}"
        )


    st.divider()

    st.markdown(
        "### Electoral Information"
    )


    st.write(
        f"**Voter ID:** "
        f"{citizen.voter_id_number or 'Not registered'}"
    )

    st.write(
        f"**Constituency:** "
        f"{citizen.constituency or 'Not provided'}"
    )

    st.write(
        f"**Polling Station:** "
        f"{citizen.polling_station_name or 'Not assigned'}"
    )

    st.write(
        f"**Has Voted:** "
        f"{'Yes' if citizen.has_voted else 'No'}"
    )


    st.divider()

    st.markdown(
        "### Verification"
    )


    st.write(
        f"**Status:** "
        f"{citizen.verification_status}"
    )

    st.write(
        f"**Verification Notes:** "
        f"{citizen.verification_notes or 'None'}"
    )

    st.write(
        f"**Enumerator:** "
        f"{citizen.enumerator_name or 'Not provided'}"
    )

    st.write(
        f"**Enumeration Date:** "
        f"{citizen.enumeration_date or 'Not provided'}"
    )


    if citizen.notes:

        st.divider()

        st.markdown(
            "### Notes"
        )

        st.write(
            citizen.notes
        )


    st.divider()


    col1, col2 = st.columns(2)


    with col1:

        if st.button(
            "Edit Citizen",
            key="profile_edit_citizen",
            use_container_width=True,
        ):

            st.session_state.citizen_editor_id = (
                str(citizen.id)
            )

            st.session_state.citizen_view_id = None

            st.rerun()


    with col2:

        if st.button(
            "Back to Citizen Registry",
            key="profile_back_citizens",
            use_container_width=True,
        ):

            st.session_state.citizen_view_id = None

            st.rerun()


# ============================================================
# CITIZENS MODULE
# ============================================================

def render_citizens() -> None:

    render_page_header(
        "Citizens",
        (
            "Citizen population records and citizen "
            "registry management."
        ),
    )


    # --------------------------------------------------------
    # DATABASE STATUS
    # --------------------------------------------------------

    if not database_connected:

        st.warning(
            "The Registry database is currently unavailable. "
            "Citizen records cannot be edited until the "
            "database connection is restored."
        )

        if database_error:

            with st.expander(
                "Database technical details"
            ):

                st.code(
                    database_error
                )

        return


    if not models_available:

        st.error(
            "Citizen database models could not be loaded."
        )

        with st.expander(
            "Technical details"
        ):

            st.code(
                models_error
            )

        return


    # --------------------------------------------------------
    # VIEW PROFILE
    # --------------------------------------------------------

    if st.session_state.citizen_view_id:

        citizen = get_citizen(
            st.session_state.citizen_view_id
        )

        if citizen is None:

            st.error(
                "The requested citizen record could not be found."
            )

            st.session_state.citizen_view_id = None

        else:

            render_citizen_profile(
                citizen
            )

            return


    # --------------------------------------------------------
    # EDIT
    # --------------------------------------------------------

    if st.session_state.citizen_editor_id:

        citizen = get_citizen(
            st.session_state.citizen_editor_id
        )

        if citizen is None:

            st.error(
                "The requested citizen record could not be found."
            )

            st.session_state.citizen_editor_id = None

        else:

            render_citizen_form(
                citizen
            )

            return


    # --------------------------------------------------------
    # REGISTRY SUMMARY
    # --------------------------------------------------------

    total_citizens = get_citizen_count()


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        render_kpi(
            "Registered Population",
            total_citizens,
            "Citizen records",
        )


    with col2:

        st.metric(
            "Verified",
            len(
                search_citizens(
                    verification_status="Verified"
                )
            ),
        )


    with col3:

        st.metric(
            "Pending Review",
            len(
                search_citizens(
                    verification_status="Pending Review"
                )
            ),
        )


    with col4:

        st.metric(
            "Archived",
            len(
                search_citizens(
                    verification_status="Archived"
                )
            ),
        )


    st.divider()


    # --------------------------------------------------------
    # ACTIONS
    # --------------------------------------------------------

    action_col1, action_col2 = st.columns(
        2
    )


    with action_col1:

        if st.button(
            "Register New Citizen",
            key="open_new_citizen",
            use_container_width=True,
        ):

            st.session_state.citizen_editor_id = (
                "NEW"
            )

            st.rerun()


    with action_col2:

        if st.button(
            "Refresh Citizen Registry",
            key="refresh_citizen_registry",
            use_container_width=True,
        ):

            st.rerun()


    if (
        st.session_state.citizen_editor_id
        == "NEW"
    ):

        render_citizen_form(
            None
        )

        return


    st.divider()


    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    st.subheader(
        "Search Citizen Registry"
    )


    search_col1, search_col2, search_col3 = st.columns(
        3
    )


    with search_col1:

        search_text = st.text_input(
            "Search",
            placeholder=(
                "Name, National ID, Passport or phone"
            ),
            key="citizen_search",
        )


    # Get state choices.

    db = get_session()

    states: list[str] = []

    if db is not None:

        try:

            values = (
                db.query(
                    Citizen.state_or_region
                )
                .filter(
                    Citizen.state_or_region.isnot(None)
                )
                .distinct()
                .order_by(
                    Citizen.state_or_region
                )
                .all()
            )

            states = [
                row[0]
                for row in values
                if row[0]
            ]

        except Exception:

            logger.exception(
                "Unable to load citizen states."
            )

        finally:

            db.close()


    with search_col2:

        selected_state = st.selectbox(
            "State / Region",
            [""] + states,
            format_func=lambda value: (
                "All States"
                if value == ""
                else value
            ),
            key="citizen_state_filter",
        )


    with search_col3:

        verification_filter = st.selectbox(
            "Verification",
            [
                "All",
                "Pending Review",
                "Verified",
                "Rejected",
                "Suspended",
                "Archived",
            ],
            key="citizen_verification_filter",
        )


    records = search_citizens(
        search_text=search_text,
        state=selected_state,
        verification_status=verification_filter,
    )


    st.caption(
        f"{len(records)} record(s) found."
    )


    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    if not records:

        st.info(
            "No citizen records match the current search."
        )

        return


    for citizen in records:

        with st.container(
            border=True
        ):

            col1, col2, col3, col4 = st.columns(
                [4, 2, 2, 2]
            )


            with col1:

                st.markdown(
                    f"### {citizen.full_name}"
                )

                st.caption(
                    f"National ID: "
                    f"{citizen.national_id or 'Not provided'}"
                )


            with col2:

                st.write(
                    f"**Age:** {citizen.age}"
                )

                st.write(
                    f"**Gender:** {citizen.gender}"
                )


            with col3:

                st.write(
                    f"**State:** "
                    f"{citizen.state_or_region or 'Not provided'}"
                )

                st.write(
                    f"**Verification:** "
                    f"{citizen.verification_status}"
                )


            with col4:

                view_key = (
                    f"view_citizen_{citizen.id}"
                )

                edit_key = (
                    f"edit_citizen_{citizen.id}"
                )


                if st.button(
                    "View",
                    key=view_key,
                    use_container_width=True,
                ):

                    st.session_state.citizen_view_id = (
                        str(citizen.id)
                    )

                    st.rerun()


                if st.button(
                    "Edit",
                    key=edit_key,
                    use_container_width=True,
                ):

                    st.session_state.citizen_editor_id = (
                        str(citizen.id)
                    )

                    st.rerun()


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:

    render_page_header(
        "National Registry Overview",
        (
            "Centralized management platform for national "
            "population records, civil registration, identity "
            "management, households and electoral registration."
        ),
    )


    citizen_count = (
        get_citizen_count()
        if database_connected
        and models_available
        else 0
    )


    st.subheader(
        "Registry Summary"
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        render_kpi(
            "Registered Population",
            citizen_count,
            "Population records",
        )


    with col2:

        render_kpi(
            "Civil Records",
            0,
            "Birth, death and civil events",
        )


    with col3:

        render_kpi(
            "Identity Records",
            0,
            "National identity records",
        )


    with col4:

        render_kpi(
            "Election Records",
            0,
            "Electoral records",
        )


    st.divider()


    st.subheader(
        "Registry Services"
    )


    services = [

        (
            "Population Registry",
            (
                "Manage national population records, "
                "households, persons and demographic "
                "information."
            ),
        ),

        (
            "Civil Registration",
            (
                "Register births, deaths, marriages, "
                "certificates and other civil events."
            ),
        ),

        (
            "Identity Management",
            (
                "Manage national identity registration, "
                "identification records and identity "
                "services."
            ),
        ),

        (
            "Elections",
            (
                "Manage electoral registration, voter "
                "records and election administration."
            ),
        ),

        (
            "Reports & Analytics",
            (
                "Generate operational reports, statistical "
                "summaries and Registry analytics."
            ),
        ),

        (
            "Administration",
            (
                "Manage users, roles, permissions, "
                "configuration and system administration."
            ),
        ),
    ]


    service_columns = st.columns(3)


    for index, (
        title,
        description,
    ) in enumerate(services):

        with service_columns[
            index % 3
        ]:

            render_service_card(
                title,
                description,
            )


    st.divider()


    st.subheader(
        "System Status"
    )


    status_col1, status_col2 = st.columns(2)


    with status_col1:

        if database_connected:

            st.success(
                "Database Connected"
            )

        else:

            st.warning(
                "Database Attention Required"
            )


    with status_col2:

        if registry_available:

            st.success(
                "Registry Module System Available"
            )

        else:

            st.warning(
                "Registry Module System Unavailable"
            )


    if not database_connected:

        with st.expander(
            "Database technical details"
        ):

            st.code(
                database_error
                or
                "No database error information is available."
            )


    if not registry_available:

        with st.expander(
            "Module registry technical details"
        ):

            st.code(
                registry_error
            )


# ============================================================
# STATIC FEATURE PAGE
# ============================================================

def render_static_feature(
    key: str,
) -> None:

    title, description = FEATURES.get(
        key,
        (
            "Registry Feature",
            "Registry feature.",
        ),
    )


    render_page_header(
        title,
        description,
    )


    if key == "population":

        st.subheader(
            "Population Records"
        )

        st.info(
            "Population administration is available "
            "through the Citizens and Household registry."
        )


    elif key == "civil_registration":

        st.subheader(
            "Civil Events"
        )

        st.info(
            "Birth, death, marriage and certificate "
            "records will appear here."
        )


    elif key == "identity":

        st.subheader(
            "Identity Records"
        )

        st.info(
            "National identity records and identity "
            "services will appear here."
        )


    elif key == "elections":

        st.subheader(
            "Electoral Registration"
        )

        st.info(
            "Voter registration and election administration "
            "records will appear here."
        )


    elif key == "households":

        st.subheader(
            "Household Records"
        )

        st.info(
            "Household records and household relationships "
            "will appear here."
        )


    elif key == "documents":

        st.subheader(
            "Registry Documents"
        )

        st.info(
            "Registry certificates and official documents "
            "will appear here."
        )


    elif key == "verification":

        st.subheader(
            "Record Verification"
        )

        st.info(
            "Verification services will appear here."
        )


    elif key == "reports":

        st.subheader(
            "Reports & Analytics"
        )

        st.info(
            "Operational reports and Registry analytics "
            "will appear here."
        )


    elif key == "statistics":

        st.subheader(
            "Registry Statistics"
        )

        st.info(
            "National Registry statistics will appear here."
        )


    elif key == "audit":

        st.subheader(
            "Audit & Activity"
        )

        st.info(
            "Registry audit activity will appear here."
        )


    elif key == "administration":

        st.subheader(
            "Administration"
        )

        st.info(
            "User, role, permission and system "
            "administration tools will appear here."
        )


    elif key == "settings":

        st.subheader(
            "System Settings"
        )

        st.info(
            "Registry platform configuration will appear here."
        )


    else:

        st.info(
            "This Registry feature is ready for implementation."
        )


# ============================================================
# REGISTERED MODULE RENDERER
# ============================================================

def render_registered_module(
    key: str,
) -> bool:

    if not registry_available:
        return False

    if get_module is None:
        return False

    try:

        module = get_module(
            key
        )

    except Exception as exc:

        logger.exception(
            "Unable to retrieve module '%s'.",
            key,
        )

        st.error(
            "Unable to load the requested Registry module."
        )

        with st.expander(
            "Technical details"
        ):

            st.exception(exc)

        return True


    if module is None:
        return False


    label = getattr(
        module,
        "label",
        key.replace(
            "_",
            " ",
        ).title(),
    )


    description = getattr(
        module,
        "description",
        "Registry management module.",
    )


    render_page_header(
        str(label),
        str(description),
    )


    available = bool(
        getattr(
            module,
            "available",
            True,
        )
    )


    if not available:

        st.warning(
            "This Registry module is currently unavailable."
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
                    str(error)
                )


        return True


    if render_module is None:

        st.error(
            "The Registry module renderer is unavailable."
        )

        return True


    try:

        render_module(
            key
        )


    except TypeError:

        try:

            render_module(
                module
            )

        except Exception as exc:

            logger.exception(
                "Module '%s' failed.",
                key,
            )

            st.error(
                "The selected Registry module encountered "
                "a runtime error."
            )

            with st.expander(
                "Technical details"
            ):

                st.exception(exc)


    except Exception as exc:

        logger.exception(
            "Module '%s' failed.",
            key,
        )

        st.error(
            "The selected Registry module encountered "
            "a runtime error."
        )

        with st.expander(
            "Technical details"
        ):

            st.exception(exc)


    return True


# ============================================================
# APPLICATION
# ============================================================

inject_css()

render_sidebar()

render_header()


active = str(
    st.session_state.active_module
)


# ============================================================
# OVERVIEW
# ============================================================

if active == "overview":

    render_overview()


# ============================================================
# CITIZENS
# ============================================================

elif active == "citizens":

    render_citizens()


# ============================================================
# STATIC FEATURES
# ============================================================

elif active in FEATURES:

    handled = render_registered_module(
        active
    )

    if not handled:

        render_static_feature(
            active
        )


# ============================================================
# DYNAMIC REGISTRY MODULES
# ============================================================

else:

    handled = render_registered_module(
        active
    )

    if not handled:

        st.error(
            "The requested Registry module could not be found."
        )

        st.info(
            "Select another module from the sidebar."
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()


footer_col1, footer_col2 = st.columns(2)


with footer_col1:

    st.caption(
        "South Sudan National Registry • "
        "Registry Platform • Version 1.0.0"
    )


with footer_col2:

    st.caption(
        "Registry data should be treated as authoritative "
        "only after verification and appropriate "
        "administrative approval."
    )
