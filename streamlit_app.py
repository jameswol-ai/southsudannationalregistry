"""
South Sudan National Registry
Streamlit AI Studio

National population, civil registration, identity,
household and electoral registry management platform.

Application entry point:

    streamlit run streamlit_app.py

Expected project structure:

    southsudannationalregistry/
    │
    ├── streamlit_app.py
    │
    ├── assets/
    │   └── south_sudan_emblem.png
    │
    ├── database/
    │   ├── __init__.py
    │   └── database.py
    │
    └── modules/
        ├── __init__.py
        └── registry.py

The application is deliberately defensive:
- Missing/corrupt emblem does not crash the application.
- Database initialization failure does not crash the UI.
- Missing optional modules do not crash the application.
- Invalid Streamlit icons are not used.
- Registry pages remain available even when backend services
  are not yet connected.
"""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Any

import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

# IMPORTANT:
# st.set_page_config() must be the first Streamlit command.

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


if "database_connected" not in st.session_state:

    st.session_state.database_connected = False


if "database_error" not in st.session_state:

    st.session_state.database_error = None


# ============================================================
# SAFE EMBLEM LOADER
# ============================================================

@st.cache_data(show_spinner=False)
def load_emblem_bytes() -> bytes | None:
    """
    Load and validate the South Sudan National Emblem.

    A missing, empty, corrupt or unsupported image will return
    None instead of raising PIL.UnidentifiedImageError.
    """

    try:

        if not EMBLEM_PATH.exists():

            logger.warning(
                "Emblem file not found: %s",
                EMBLEM_PATH,
            )

            return None


        image_bytes = EMBLEM_PATH.read_bytes()


        if not image_bytes:

            logger.warning(
                "Emblem file is empty: %s",
                EMBLEM_PATH,
            )

            return None


        # Validate the image before giving it to Streamlit.

        from PIL import Image

        with Image.open(
            io.BytesIO(image_bytes)
        ) as image:

            image.verify()


        return image_bytes


    except Exception as exc:

        logger.warning(
            "Unable to validate emblem '%s': %s",
            EMBLEM_PATH,
            exc,
        )

        return None


@st.cache_data(show_spinner=False)
def load_emblem() -> Any | None:
    """
    Return a Pillow image suitable for st.image().
    """

    image_bytes = load_emblem_bytes()


    if image_bytes is None:

        return None


    try:

        from PIL import Image

        image = Image.open(
            io.BytesIO(image_bytes)
        )

        image.load()


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
            "Unable to load validated emblem: %s",
            exc,
        )

        return None


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

        "success": "#15803D",

        "warning": "#D97706",

        "danger": "#DC2626",

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

:root {{

    --registry-background:
        {theme["background"]};

    --registry-surface:
        {theme["surface"]};

    --registry-surface-alt:
        {theme["surface_alt"]};

    --registry-surface-hover:
        {theme["surface_hover"]};

    --registry-text:
        {theme["text"]};

    --registry-muted:
        {theme["muted"]};

    --registry-border:
        {theme["border"]};

    --registry-accent:
        {theme["accent"]};

    --registry-accent-dark:
        {theme["accent_dark"]};

    --registry-success:
        {theme["success"]};

    --registry-warning:
        {theme["warning"]};

    --registry-danger:
        {theme["danger"]};
}}


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

    background:
        var(--registry-background);

    color:
        var(--registry-text);
}}


.block-container {{

    max-width:
        1500px;

    padding-top:
        1.2rem;

    padding-bottom:
        3rem;
}}


h1,
h2,
h3,
h4,
h5,
h6 {{

    color:
        var(--registry-text)
        !important;
}}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {{

    background:
        var(--registry-surface);

    border-right:
        1px solid
        var(--registry-border);
}}


section[data-testid="stSidebar"] * {{

    color:
        var(--registry-text);
}}


.sidebar-brand-title {{

    font-size:
        19px;

    font-weight:
        800;

    line-height:
        1.25;

    color:
        var(--registry-text);
}}


.sidebar-brand-subtitle {{

    margin-top:
        6px;

    font-size:
        11px;

    line-height:
        1.5;

    color:
        var(--registry-muted);
}}


.sidebar-section {{

    margin-top:
        18px;

    margin-bottom:
        7px;

    color:
        var(--registry-accent);

    font-size:
        10px;

    font-weight:
        800;

    text-transform:
        uppercase;

    letter-spacing:
        0.09em;
}}


section[data-testid="stSidebar"]
.stButton > button {{

    width:
        100%;

    min-height:
        38px;

    border-radius:
        9px;

    text-align:
        left;

    font-weight:
        600;

    border:
        1px solid transparent;

    background:
        transparent;

    color:
        var(--registry-text);
}}


section[data-testid="stSidebar"]
.stButton > button:hover {{

    border-color:
        var(--registry-border);

    background:
        var(--registry-surface-hover);
}}


/* ============================================================
   MAIN HEADER
   ============================================================ */

.registry-header {{

    background:
        var(--registry-surface);

    border:
        1px solid
        var(--registry-border);

    border-radius:
        18px;

    padding:
        18px 20px;

    margin-bottom:
        20px;
}}


.registry-title {{

    font-size:
        28px;

    font-weight:
        800;

    line-height:
        1.2;

    letter-spacing:
        -0.02em;

    color:
        var(--registry-text);
}}


.registry-subtitle {{

    margin-top:
        6px;

    font-size:
        13px;

    line-height:
        1.5;

    color:
        var(--registry-muted);
}}


/* ============================================================
   EMBLEM FALLBACK
   ============================================================ */

.registry-emblem-fallback {{

    width:
        64px;

    height:
        64px;

    border-radius:
        50%;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    background:
        var(--registry-accent);

    border:
        3px solid #FBBF24;

    color:
        #FFFFFF;

    font-size:
        18px;

    font-weight:
        900;
}}


/* ============================================================
   STATUS
   ============================================================ */

.status-online {{

    color:
        var(--registry-success);

    font-size:
        12px;

    font-weight:
        700;
}}


.status-warning {{

    color:
        var(--registry-warning);

    font-size:
        12px;

    font-weight:
        700;
}}


.status-dot {{

    display:
        inline-block;

    width:
        8px;

    height:
        8px;

    border-radius:
        50%;

    margin-right:
        5px;

    background:
        var(--registry-success);
}}


.status-dot-warning {{

    display:
        inline-block;

    width:
        8px;

    height:
        8px;

    border-radius:
        50%;

    margin-right:
        5px;

    background:
        var(--registry-warning);
}}


.registry-version {{

    margin-top:
        4px;

    color:
        var(--registry-muted);

    font-size:
        11px;
}}


/* ============================================================
   PAGE HEADER
   ============================================================ */

.page-card {{

    background:
        var(--registry-surface);

    border:
        1px solid
        var(--registry-border);

    border-radius:
        16px;

    padding:
        22px;

    margin-bottom:
        18px;
}}


.registry-kicker {{

    color:
        var(--registry-accent);

    font-size:
        11px;

    font-weight:
        800;

    text-transform:
        uppercase;

    letter-spacing:
        0.08em;
}}


.registry-heading {{

    margin-top:
        5px;

    color:
        var(--registry-text);

    font-size:
        23px;

    font-weight:
        800;

    line-height:
        1.3;
}}


.registry-description {{

    margin-top:
        7px;

    max-width:
        1000px;

    color:
        var(--registry-muted);

    font-size:
        14px;

    line-height:
        1.6;
}}


/* ============================================================
   KPI
   ============================================================ */

.kpi-card {{

    min-height:
        120px;

    padding:
        18px;

    background:
        var(--registry-surface);

    border:
        1px solid
        var(--registry-border);

    border-radius:
        15px;
}}


.kpi-label {{

    color:
        var(--registry-muted);

    font-size:
        12px;

    font-weight:
        700;
}}


.kpi-value {{

    margin-top:
        6px;

    color:
        var(--registry-text);

    font-size:
        30px;

    font-weight:
        800;

    line-height:
        1.1;
}}


.kpi-description {{

    margin-top:
        6px;

    color:
        var(--registry-muted);

    font-size:
        11px;
}}


/* ============================================================
   MODULE CARD
   ============================================================ */

.module-card {{

    min-height:
        125px;

    padding:
        18px;

    margin-bottom:
        15px;

    background:
        var(--registry-surface);

    border:
        1px solid
        var(--registry-border);

    border-radius:
        14px;
}}


.module-name {{

    color:
        var(--registry-text);

    font-size:
        16px;

    font-weight:
        750;
}}


.module-description {{

    margin-top:
        6px;

    color:
        var(--registry-muted);

    font-size:
        13px;

    line-height:
        1.5;
}}


/* ============================================================
   STREAMLIT METRICS
   ============================================================ */

div[data-testid="stMetric"] {{

    background:
        var(--registry-surface);

    border:
        1px solid
        var(--registry-border);

    border-radius:
        14px;

    padding:
        14px;
}}


div[data-testid="stMetricLabel"] {{

    color:
        var(--registry-muted)
        !important;
}}


div[data-testid="stMetricValue"] {{

    color:
        var(--registry-text)
        !important;
}}


/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {{

    border-radius:
        10px;

    min-height:
        40px;

    font-weight:
        600;
}}


/* ============================================================
   INPUTS
   ============================================================ */

div[data-baseweb="select"] > div {{

    border-radius:
        10px;

    border-color:
        var(--registry-border);
}}


input,
textarea {{

    border-radius:
        10px !important;
}}


/* ============================================================
   FOOTER
   ============================================================ */

.registry-footer {{

    color:
        var(--registry-muted);

    font-size:
        11px;

    line-height:
        1.5;
}}


/* ============================================================
   STREAMLIT CHROME
   ============================================================ */

#MainMenu {{

    visibility:
        hidden;
}}


footer {{

    visibility:
        hidden;
}}


header[data-testid="stHeader"] {{

    background:
        transparent;
}}

</style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DATABASE
# ============================================================

database_init_function = None


try:

    from database.database import init_db

    database_init_function = init_db

except Exception as exc:

    logger.warning(
        "Could not import database initializer: %s",
        exc,
    )

    database_init_function = None


@st.cache_resource(show_spinner=False)
def initialize_database() -> tuple[bool, str | None]:

    if database_init_function is None:

        return (
            False,
            "database.database.init_db could not be imported.",
        )


    try:

        database_init_function()

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


database_connected, database_error_text = (
    initialize_database()
)


st.session_state.database_connected = (
    database_connected
)

st.session_state.database_error = (
    database_error_text
)


# ============================================================
# MODULE REGISTRY
# ============================================================

registry_available = False

registry_import_error: str | None = None

get_available_modules = None

get_module = None

render_module = None


try:

    from modules.registry import (
        get_available_modules,
        get_module,
        render_module,
    )

    registry_available = True


except Exception as exc:

    registry_import_error = (
        f"{type(exc).__name__}: {exc}"
    )

    logger.warning(
        "Could not import modules.registry: %s",
        exc,
    )


def load_available_modules() -> list[Any]:

    if not registry_available:
        return []


    if get_available_modules is None:
        return []


    try:

        modules = get_available_modules()

        return list(
            modules or []
        )


    except Exception:

        logger.exception(
            "Unable to load available modules."
        )

        return []


def load_all_modules() -> list[Any]:

    try:

        from modules.registry import MODULES

        if isinstance(
            MODULES,
            dict,
        ):

            return list(
                MODULES.values()
            )


    except Exception:

        pass


    return load_available_modules()


# ============================================================
# PAGE DESCRIPTIONS
# ============================================================

PAGE_DEFINITIONS: dict[
    str,
    tuple[str, str],
] = {

    "overview": (
        "National Registry Overview",
        (
            "Centralized management platform for national "
            "population records, civil registration, identity "
            "management, households and electoral registration."
        ),
    ),

    "citizens": (
        "Citizens",
        (
            "Citizen population records and citizen registry "
            "management."
        ),
    ),

    "population": (
        "Population Registry",
        (
            "Manage national population records, households, "
            "persons and demographic information."
        ),
    ),

    "civil_registration": (
        "Civil Registration",
        (
            "Register births, deaths, marriages, certificates "
            "and other civil events."
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
            "Manage users, roles, permissions, configuration "
            "and system administration."
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
# SIDEBAR NAVIGATION
# ============================================================

def set_active_module(
    key: str,
) -> None:

    st.session_state.active_module = key

    st.rerun()


def sidebar_nav_button(
    key: str,
    label: str,
) -> None:

    if st.button(
        label,
        key=f"sidebar_button_{key}",
        use_container_width=True,
    ):

        set_active_module(key)


def render_sidebar() -> None:

    with st.sidebar:

        # ----------------------------------------------------
        # EMBLEM
        # ----------------------------------------------------

        emblem = load_emblem()


        if emblem is not None:

            st.image(
                emblem,
                width=64,
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
        # BRAND
        # ----------------------------------------------------

        st.markdown(
            "### South Sudan National Registry"
        )

        st.caption(
            "National Population • Civil Registration • "
            "Identity • Elections"
        )


        # ----------------------------------------------------
        # SYSTEM STATUS
        # ----------------------------------------------------

        if database_connected:

            st.success(
                "System Online"
            )

        else:

            # IMPORTANT:
            # No icon parameter is used here.
            # This prevents the StreamlitAPIException caused
            # by icon="!".

            st.warning(
                "Database Attention Required"
            )


        st.divider()


        # ----------------------------------------------------
        # REGISTRY
        # ----------------------------------------------------

        st.markdown(
            "Registry"
        )

        sidebar_nav_button(
            "overview",
            "Overview",
        )

        sidebar_nav_button(
            "citizens",
            "Citizens",
        )

        sidebar_nav_button(
            "population",
            "Population Registry",
        )

        sidebar_nav_button(
            "civil_registration",
            "Civil Registration",
        )

        sidebar_nav_button(
            "identity",
            "Identity Management",
        )

        sidebar_nav_button(
            "elections",
            "Elections",
        )


        # ----------------------------------------------------
        # OPERATIONS
        # ----------------------------------------------------

        st.markdown(
            "Operations"
        )

        sidebar_nav_button(
            "households",
            "Households",
        )

        sidebar_nav_button(
            "documents",
            "Documents",
        )

        sidebar_nav_button(
            "verification",
            "Verification",
        )

        sidebar_nav_button(
            "reports",
            "Reports & Analytics",
        )


        # ----------------------------------------------------
        # ADMINISTRATION
        # ----------------------------------------------------

        st.markdown(
            "Administration"
        )

        sidebar_nav_button(
            "administration",
            "Administration",
        )

        sidebar_nav_button(
            "settings",
            "System Settings",
        )


        # ----------------------------------------------------
        # OTHER FEATURES
        # ----------------------------------------------------

        st.markdown(
            "Other Features"
        )

        sidebar_nav_button(
            "statistics",
            "Statistics",
        )

        sidebar_nav_button(
            "audit",
            "Audit & Activity",
        )


        st.divider()


        # ----------------------------------------------------
        # THEME
        # ----------------------------------------------------

        theme_label = (
            "Switch to Light Mode"
            if st.session_state.dark_mode
            else "Switch to Dark Mode"
        )


        if st.button(
            theme_label,
            key="sidebar_theme_button",
            use_container_width=True,
        ):

            st.session_state.dark_mode = (
                not st.session_state.dark_mode
            )

            st.rerun()


        # ----------------------------------------------------
        # REFRESH
        # ----------------------------------------------------

        if st.button(
            "Refresh Application",
            key="sidebar_refresh_button",
            use_container_width=True,
        ):

            st.rerun()


        st.divider()


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

    emblem = load_emblem()


    st.markdown(
        '<div class="registry-header">',
        unsafe_allow_html=True,
    )


    col1, col2, col3 = st.columns(
        [1, 7, 2],
        vertical_alignment="center",
    )


    # --------------------------------------------------------
    # EMBLEM
    # --------------------------------------------------------

    with col1:

        if emblem is not None:

            st.image(
                emblem,
                width=64,
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


    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    with col2:

        st.markdown(
            "## South Sudan National Registry"
        )

        st.caption(
            "National Population • Civil Registration • "
            "Identity • Elections"
        )


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

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
        '<div class="page-card">',
        unsafe_allow_html=True,
    )


    st.caption(
        "South Sudan National Registry"
    )


    st.subheader(
        title
    )


    st.write(
        description
    )


    st.markdown(
        "</div>",
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
    # KPI
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


    st.divider()


    # --------------------------------------------------------
    # REGISTRY SERVICES
    # --------------------------------------------------------

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


    service_columns = st.columns(
        3
    )


    for index, (
        title,
        description,
    ) in enumerate(services):

        with service_columns[
            index % 3
        ]:

            render_module_card(
                title,
                description,
            )


    st.divider()


    # --------------------------------------------------------
    # SYSTEM STATUS
    # --------------------------------------------------------

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

        if registry_available:

            st.success(
                "Registry Module System Available"
            )

        else:

            st.warning(
                "Registry Module System Unavailable"
            )


    # --------------------------------------------------------
    # DATABASE TECHNICAL DETAILS
    # --------------------------------------------------------

    if not database_connected:

        with st.expander(
            "Database technical details"
        ):

            if database_error_text:

                st.code(
                    database_error_text
                )

            else:

                st.write(
                    "No database error information is available."
                )


    # --------------------------------------------------------
    # MODULE TECHNICAL DETAILS
    # --------------------------------------------------------

    if not registry_available:

        with st.expander(
            "Module registry technical details"
        ):

            st.code(
                registry_import_error
                or "Unknown module registry error."
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
# PLACEHOLDER PAGE
# ============================================================

def render_placeholder(
    key: str,
) -> None:

    title, description = PAGE_DEFINITIONS.get(
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


    # Basic empty state

    st.subheader(
        "Records"
    )


    st.caption(
        "No records are currently available."
    )


# ============================================================
# REGISTERED MODULE
# ============================================================

def try_render_registered_module(
    key: str,
) -> bool:
    """
    Attempt to render an existing module from modules.registry.

    Returns:
        True  -> module was found/handled
        False -> module was not found
    """

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


    title = getattr(
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
        str(title),
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

        # Compatibility with registries whose renderer expects
        # the module object rather than its key.

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
# APPLICATION START
# ============================================================

inject_css()

render_sidebar()

render_header()


# ============================================================
# ACTIVE MODULE
# ============================================================

active_module = str(
    st.session_state.active_module
)


# ============================================================
# OVERVIEW
# ============================================================

if active_module == "overview":

    render_overview()


# ============================================================
# CITIZENS
# ============================================================

elif active_module == "citizens":

    render_citizens()


# ============================================================
# STATIC APPLICATION PAGES
# ============================================================

elif active_module in PAGE_DEFINITIONS:

    render_placeholder(
        active_module
    )


# ============================================================
# EXISTING MODULE REGISTRY
# ============================================================

else:

    handled = try_render_registered_module(
        active_module
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


footer_col1, footer_col2 = st.columns(
    2
)


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
