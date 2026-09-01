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
from pathlib import Path
from typing import Any

import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# IMPORTANT:
# Must run before Streamlit UI/session-state operations.
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

EMBLEM_PATH = (
    ASSETS_DIR / "south_sudan_emblem.png"
)


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(
    "south_sudan_national_registry"
)

if not logger.handlers:

    logging.basicConfig(
        level=logging.INFO
    )


# ============================================================
# SESSION STATE
# ============================================================

if "active_module" not in st.session_state:

    st.session_state.active_module = "overview"


if "dark_mode" not in st.session_state:

    st.session_state.dark_mode = True


# ============================================================
# SAFE EMBLEM LOADING
# ============================================================

@st.cache_data(show_spinner=False)
def load_emblem_bytes() -> bytes | None:
    """
    Read and validate the Registry emblem.

    Returns:
        Valid image bytes or None.

    The application must never crash because the emblem is
    missing, empty, corrupted, or not actually an image.
    """

    if not EMBLEM_PATH.exists():

        logger.warning(
            "Registry emblem not found: %s",
            EMBLEM_PATH,
        )

        return None

    try:

        raw = EMBLEM_PATH.read_bytes()

        if not raw:

            logger.warning(
                "Registry emblem is empty: %s",
                EMBLEM_PATH,
            )

            return None


        # Validate using Pillow before passing anything to
        # Streamlit.
        from PIL import Image


        with Image.open(
            io.BytesIO(raw)
        ) as image:

            image.verify()


        return raw


    except Exception as exc:

        logger.warning(
            "Invalid Registry emblem '%s': %s",
            EMBLEM_PATH,
            exc,
        )

        return None


def get_emblem_image() -> Any | None:
    """
    Return a Pillow image suitable for st.image().
    """

    raw = load_emblem_bytes()

    if raw is None:

        return None

    try:

        from PIL import Image

        image = Image.open(
            io.BytesIO(raw)
        )

        if image.mode not in (
            "RGB",
            "RGBA",
        ):

            image = image.convert(
                "RGBA"
            )

        return image

    except Exception as exc:

        logger.warning(
            "Could not create Registry emblem image: %s",
            exc,
        )

        return None


# ============================================================
# DATABASE
# ============================================================

database_connected = False

database_error: Exception | None = None

init_db = None


try:

    from database.database import init_db

except Exception as exc:

    database_error = exc

    logger.exception(
        "Unable to import database.database.init_db."
    )


@st.cache_resource
def initialize_database() -> bool:
    """
    Initialize the database once per Streamlit process.
    """

    if init_db is None:

        raise RuntimeError(
            "database.database.init_db could not be imported."
        )

    init_db()

    return True


try:

    initialize_database()

    database_connected = True

except Exception as exc:

    database_error = exc

    logger.exception(
        "Database initialization failed."
    )


# ============================================================
# MODULE REGISTRY
# ============================================================

get_available_modules = None
get_module = None
render_module = None


try:

    from modules.registry import (
        get_available_modules,
        get_module,
        render_module,
    )

except Exception as exc:

    logger.exception(
        "Unable to import modules.registry."
    )


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

        "accent_dark": "#166534",

        "accent_soft": "#DCFCE7",

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

/* ============================================================
   GLOBAL
   ============================================================ */

html,
body,
[class*="css"] {{
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
    padding-top: 1.2rem;
    padding-bottom: 3rem;
}}

h1,
h2,
h3,
h4,
h5,
h6 {{
    color: {theme["text"]} !important;
}}

p,
label {{
    color: {theme["text"]};
}}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {{
    background: {theme["surface"]};
    border-right: 1px solid {theme["border"]};
}}

section[data-testid="stSidebar"] * {{
    color: {theme["text"]};
}}

.sidebar-title {{
    color: {theme["text"]};
    font-size: 18px;
    font-weight: 800;
    line-height: 1.25;
}}

.sidebar-subtitle {{
    color: {theme["muted"]};
    font-size: 11px;
    line-height: 1.5;
    margin-top: 5px;
}}

.sidebar-section {{
    color: {theme["accent"]};
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin-top: 17px;
    margin-bottom: 7px;
}}


/* ============================================================
   SIDEBAR BUTTONS
   ============================================================ */

section[data-testid="stSidebar"]
.stButton > button {{
    width: 100%;
    min-height: 38px;
    border-radius: 9px;
    text-align: left;
    font-weight: 600;
    border: 1px solid transparent;
}}

section[data-testid="stSidebar"]
.stButton > button:hover {{
    border-color: {theme["border"]};
}}


/* ============================================================
   MAIN REGISTRY BRAND
   ============================================================ */

.registry-header {{
    background: {theme["surface"]};
    border: 1px solid {theme["border"]};
    border-radius: 18px;
    padding: 18px 20px;
    margin-bottom: 20px;
}}

.registry-brand {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    width: 100%;
}}

.registry-title {{
    color: {theme["text"]};
    font-size: 28px;
    font-weight: 800;
    line-height: 1.2;
    letter-spacing: -0.02em;
}}

.registry-subtitle {{
    color: {theme["muted"]};
    font-size: 13px;
    font-weight: 500;
    line-height: 1.5;
    margin-top: 7px;
}}


/* ============================================================
   SIDEBAR BRAND
   ============================================================ */

.registry-brand-sidebar {{
    text-align: left;
    margin-top: 4px;
    margin-bottom: 12px;
}}

.registry-brand-sidebar .registry-title {{
    font-size: 18px;
    line-height: 1.25;
}}

.registry-brand-sidebar .registry-subtitle {{
    font-size: 11px;
    line-height: 1.45;
    margin-top: 5px;
}}


/* ============================================================
   STATUS
   ============================================================ */

.registry-status {{
    text-align: right;
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

.status-dot {{
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: {theme["success"]};
    margin-right: 5px;
}}

.status-dot-warning {{
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: {theme["warning"]};
    margin-right: 5px;
}}

.registry-version {{
    color: {theme["muted"]};
    font-size: 11px;
    margin-top: 4px;
}}


/* ============================================================
   EMBLEM FALLBACK
   ============================================================ */

.registry-emblem-fallback {{
    width: 65px;
    height: 65px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: {theme["accent"]};
    border: 3px solid #FBBF24;
    color: #FFFFFF;
    font-size: 19px;
    font-weight: 900;
}}


/* ============================================================
   OVERVIEW
   ============================================================ */

.overview-card {{
    background: {theme["surface"]};
    border: 1px solid {theme["border"]};
    border-radius: 15px;
    padding: 22px;
    margin-bottom: 18px;
}}

.registry-kicker {{
    color: {theme["accent"]};
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}

.registry-heading {{
    color: {theme["text"]};
    font-size: 23px;
    font-weight: 800;
    line-height: 1.3;
    margin-top: 5px;
}}

.registry-description {{
    color: {theme["muted"]};
    font-size: 14px;
    line-height: 1.6;
    margin-top: 7px;
}}


/* ============================================================
   KPI
   ============================================================ */

.kpi-card {{
    background: {theme["surface"]};
    border: 1px solid {theme["border"]};
    border-radius: 15px;
    padding: 18px;
    min-height: 120px;
}}

.kpi-label {{
    color: {theme["muted"]};
    font-size: 12px;
    font-weight: 700;
}}

.kpi-value {{
    color: {theme["text"]};
    font-size: 30px;
    font-weight: 800;
    line-height: 1.1;
    margin-top: 6px;
}}

.kpi-description {{
    color: {theme["muted"]};
    font-size: 11px;
    margin-top: 6px;
}}


/* ============================================================
   MODULE CARDS
   ============================================================ */

.module-card {{
    background: {theme["surface"]};
    border: 1px solid {theme["border"]};
    border-radius: 14px;
    padding: 18px;
    min-height: 125px;
    margin-bottom: 15px;
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
    margin-top: 6px;
}}


/* ============================================================
   METRICS
   ============================================================ */

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


/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {{
    border-radius: 10px;
    min-height: 40px;
    font-weight: 600;
}}


/* ============================================================
   INPUTS
   ============================================================ */

div[data-baseweb="select"] > div {{
    border-radius: 10px;
    border-color: {theme["border"]};
}}

input,
textarea {{
    border-radius: 10px !important;
}}


/* ============================================================
   FOOTER
   ============================================================ */

.registry-footer {{
    color: {theme["muted"]};
    font-size: 11px;
    line-height: 1.5;
}}


/* ============================================================
   STREAMLIT CHROME
   ============================================================ */

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
# BRANDING COMPONENT
# ============================================================

def render_registry_brand(
    sidebar: bool = False,
) -> None:
    """
    Render Registry branding.

    The same branding is used in the sidebar and main header.
    """

    if sidebar:

        st.markdown(
            """
<div class="registry-brand registry-brand-sidebar">

    <div class="registry-title">
        South Sudan National Registry
    </div>

    <div class="registry-subtitle">
        National Population • Civil Registration •
        Identity • Elections
    </div>

</div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            """
<div class="registry-brand">

    <div class="registry-title">
        South Sudan National Registry
    </div>

    <div class="registry-subtitle">
        National Population • Civil Registration •
        Identity • Elections
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

        # ----------------------------------------------------
        # Emblem
        # ----------------------------------------------------

        emblem = get_emblem_image()

        if emblem is not None:

            st.image(
                emblem,
                width=65,
            )

        else:

            st.markdown(
                """
<div class="registry-emblem-fallback">
    SS
</div>
                """,
                unsafe_allow_html=True,
            )


        # ----------------------------------------------------
        # Branding
        # ----------------------------------------------------

        render_registry_brand(
            sidebar=True
        )


        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        if database_connected:

            st.success(
                "System Online"
            )

        else:

            st.warning(
                "Database Attention Required"
            )


        st.divider()


        # ----------------------------------------------------
        # Registry
        # ----------------------------------------------------

        st.markdown(
            """
<div class="sidebar-section">
    Registry
</div>
            """,
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
                "population",
                "Population Registry",
            ),

            (
                "civil_registration",
                "Civil Registration",
            ),

            (
                "identity",
                "Identity Management",
            ),

            (
                "elections",
                "Elections",
            ),

        ]


        for key, label in registry_items:

            if st.button(
                label,
                key=f"sidebar_{key}",
                use_container_width=True,
            ):

                st.session_state.active_module = key

                st.rerun()


        # ----------------------------------------------------
        # Operations
        # ----------------------------------------------------

        st.markdown(
            """
<div class="sidebar-section">
    Operations
</div>
            """,
            unsafe_allow_html=True,
        )


        operations_items = [

            (
                "households",
                "Households",
            ),

            (
                "documents",
                "Documents",
            ),

            (
                "verification",
                "Verification",
            ),

            (
                "reports",
                "Reports & Analytics",
            ),

        ]


        for key, label in operations_items:

            if st.button(
                label,
                key=f"sidebar_{key}",
                use_container_width=True,
            ):

                st.session_state.active_module = key

                st.rerun()


        # ----------------------------------------------------
        # Administration
        # ----------------------------------------------------

        st.markdown(
            """
<div class="sidebar-section">
    Administration
</div>
            """,
            unsafe_allow_html=True,
        )


        administration_items = [

            (
                "administration",
                "Administration",
            ),

            (
                "settings",
                "System Settings",
            ),

        ]


        for key, label in administration_items:

            if st.button(
                label,
                key=f"sidebar_{key}",
                use_container_width=True,
            ):

                st.session_state.active_module = key

                st.rerun()


        # ----------------------------------------------------
        # Other Features
        # ----------------------------------------------------

        st.markdown(
            """
<div class="sidebar-section">
    Other Features
</div>
            """,
            unsafe_allow_html=True,
        )


        feature_items = [

            (
                "statistics",
                "Statistics",
            ),

            (
                "audit",
                "Audit & Activity",
            ),

        ]


        for key, label in feature_items:

            if st.button(
                label,
                key=f"sidebar_{key}",
                use_container_width=True,
            ):

                st.session_state.active_module = key

                st.rerun()


        # ----------------------------------------------------
        # System Controls
        # ----------------------------------------------------

        st.divider()


        if st.button(
            "Refresh Application",
            key="sidebar_refresh",
            use_container_width=True,
        ):

            st.rerun()


        theme_label = (
            "Switch to Light Mode"
            if st.session_state.dark_mode
            else "Switch to Dark Mode"
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


        st.divider()


        st.caption(
            "South Sudan National Registry"
        )

        st.caption(
            "Registry Platform"
        )

        st.caption(
            "Version 1.0.0"
        )


# ============================================================
# MAIN HEADER
# ============================================================

def render_header() -> None:

    emblem = get_emblem_image()

    st.markdown(
        '<div class="registry-header">',
        unsafe_allow_html=True,
    )


    col1, col2, col3 = st.columns(
        [1, 7, 2],
        vertical_alignment="center",
    )


    with col1:

        if emblem is not None:

            st.image(
                emblem,
                width=65,
            )

        else:

            st.markdown(
                """
<div class="registry-emblem-fallback">
    SS
</div>
                """,
                unsafe_allow_html=True,
            )


    with col2:

        render_registry_brand(
            sidebar=False
        )


    with col3:

        if database_connected:

            st.markdown(
                """
<div class="registry-status">

    <div class="status-online">
        <span class="status-dot"></span>
        System Online
    </div>

    <div class="registry-version">
        Registry Platform
    </div>

    <div class="registry-version">
        Version 1.0.0
    </div>

</div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                """
<div class="registry-status">

    <div class="status-warning">
        <span class="status-dot-warning"></span>
        Database Attention
    </div>

    <div class="registry-version">
        Registry Platform
    </div>

    <div class="registry-version">
        Version 1.0.0
    </div>

</div>
                """,
                unsafe_allow_html=True,
            )


    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# PAGE HEADER
# ============================================================

def render_page_header(
    title: str,
    description: str,
) -> None:

    st.markdown(
        f"""
<div class="overview-card">

    <div class="registry-kicker">
        South Sudan National Registry
    </div>

    <div class="registry-heading">
        {title}
    </div>

    <div class="registry-description">
        {description}
    </div>

</div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# KPI CARD
# ============================================================

def render_kpi(
    label: str,
    value: Any,
    description: str,
) -> None:

    st.markdown(
        f"""
<div class="kpi-card">

    <div class="kpi-label">
        {label}
    </div>

    <div class="kpi-value">
        {value}
    </div>

    <div class="kpi-description">
        {description}
    </div>

</div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MODULE CARD
# ============================================================

def render_module_card(
    title: str,
    description: str,
) -> None:

    st.markdown(
        f"""
<div class="module-card">

    <div class="module-name">
        {title}
    </div>

    <div class="module-description">
        {description}
    </div>

</div>
        """,
        unsafe_allow_html=True,
    )


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


    # --------------------------------------------------------
    # KPI ROW
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(
        4
    )


    with col1:

        render_kpi(
            "Registered Population",
            0,
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


    # --------------------------------------------------------
    # Registry Services
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "Registry Services"
    )


    services = [

        (
            "Population Registry",
            (
                "Manage national population records, "
                "households, persons and demographic information."
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
                "identification records and identity services."
            ),
        ),

        (
            "Elections",
            (
                "Manage electoral registration, voter records "
                "and election administration."
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


    columns = st.columns(
        3
    )


    for index, (
        title,
        description,
    ) in enumerate(services):

        with columns[
            index % 3
        ]:

            render_module_card(
                title,
                description,
            )


    # --------------------------------------------------------
    # System Status
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "System Status"
    )


    status_col1, status_col2 = st.columns(
        2
    )


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

        st.success(
            "Registry Interface Available"
        )


# ============================================================
# CITIZENS
# ============================================================

def render_citizens() -> None:

    render_page_header(
        "Citizens",
        (
            "Citizen population records and citizen "
            "registry management."
        ),
    )


    col1, col2, col3, col4 = st.columns(
        4
    )


    with col1:

        render_kpi(
            "Registered Population",
            0,
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
        "Citizen Registry"
    )


    st.info(
        "Citizen records will appear here when the "
        "citizen and population database services are connected."
    )


# ============================================================
# PLACEHOLDER FEATURES
# ============================================================

PLACEHOLDER_PAGES = {

    "population": (
        "Population Registry",
        (
            "Manage national population records, "
            "persons, households and demographic information."
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
            "Manage household records and "
            "household relationships."
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
            "Verify population, civil registration "
            "and identity records."
        ),
    ),

    "reports": (
        "Reports & Analytics",
        (
            "Generate operational reports, statistical "
            "summaries and Registry analytics."
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

    "statistics": (
        "Statistics",
        (
            "View national Registry statistics "
            "and demographic summaries."
        ),
    ),

    "audit": (
        "Audit & Activity",
        (
            "Review Registry activity, administrative "
            "events and audit information."
        ),
    ),

}


# ============================================================
# PLACEHOLDER RENDERER
# ============================================================

def render_placeholder(
    key: str,
) -> None:

    title, description = PLACEHOLDER_PAGES.get(
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


    st.info(
        f"{title} is ready for implementation."
    )


# ============================================================
# OPTIONAL MODULE REGISTRY
# ============================================================

def render_registered_module(
    active_key: str,
) -> bool:
    """
    Attempt to render an existing registered module.

    Returns:
        True if the registry module was found and handled.
        False if it does not exist.
    """

    if get_module is None:

        return False


    try:

        module = get_module(
            active_key
        )

    except Exception as exc:

        logger.exception(
            "Unable to retrieve Registry module '%s'.",
            active_key,
        )

        st.error(
            "Unable to load the requested Registry module."
        )

        with st.expander(
            "Technical details"
        ):

            st.exception(
                exc
            )

        return True


    if module is None:

        return False


    module_label = getattr(
        module,
        "label",
        active_key.replace(
            "_",
            " ",
        ).title(),
    )


    module_description = getattr(
        module,
        "description",
        "",
    )


    render_page_header(
        str(module_label),
        str(
            module_description
            or "Registry management module."
        ),
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
            active_key
        )

    except TypeError:

        # Compatibility with implementations that accept
        # a module object instead of a key.
        try:

            render_module(
                module
            )

        except Exception as exc:

            logger.exception(
                "Registry module '%s' failed.",
                active_key,
            )

            st.error(
                "The selected Registry module "
                "encountered a runtime error."
            )

            with st.expander(
                "Technical details"
            ):

                st.exception(
                    exc
                )


    except Exception as exc:

        logger.exception(
            "Registry module '%s' failed.",
            active_key,
        )

        st.error(
            "The selected Registry module "
            "encountered a runtime error."
        )

        with st.expander(
            "Technical details"
        ):

            st.exception(
                exc
            )


    return True


# ============================================================
# INITIALIZE CSS
# ============================================================

inject_css()


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

sidebar_navigation()


# ============================================================
# MAIN HEADER
# ============================================================

render_header()


# ============================================================
# ACTIVE PAGE
# ============================================================

active_key = str(
    st.session_state.active_module
)


if active_key == "overview":

    render_overview()


elif active_key == "citizens":

    render_citizens()


elif active_key in PLACEHOLDER_PAGES:

    render_placeholder(
        active_key
    )


else:

    handled = render_registered_module(
        active_key
    )


    if not handled:

        st.error(
            "The requested Registry module "
            "could not be found."
        )


# ============================================================
# DATABASE NOTICE
# ============================================================

if not database_connected:

    st.warning(
        "The Registry interface is running without "
        "a connected database."
    )


    if database_error:

        with st.expander(
            "Database technical details"
        ):

            st.exception(
                database_error
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()


footer_col1, footer_col2 = st.columns(
    2
)


with footer_col1:

    st.markdown(
        """
<div class="registry-footer">
    South Sudan National Registry •
    Registry Platform • Version 1.0.0
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
