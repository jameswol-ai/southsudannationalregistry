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
# ============================================================

# This MUST be the first Streamlit command.

st.set_page_config(
    page_title="South Sudan National Registry",
    page_icon="SS",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# APPLICATION PATHS
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

    st.session_state.active_module = (
        "overview"
    )


if "dark_mode" not in st.session_state:

    st.session_state.dark_mode = True


if "database_connected" not in st.session_state:

    st.session_state.database_connected = False


if "database_error" not in st.session_state:

    st.session_state.database_error = None


# ============================================================
# SAFE EMBLEM LOADING
# ============================================================

@st.cache_data(
    show_spinner=False
)
def load_emblem() -> Any | None:
    """
    Safely load assets/south_sudan_emblem.png.

    A missing, empty, corrupt, or unsupported image will
    return None instead of crashing Streamlit with:

        PIL.UnidentifiedImageError
    """

    try:

        if not EMBLEM_PATH.exists():

            logger.warning(
                "Emblem not found: %s",
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


        from PIL import Image


        # First validate the image.

        with Image.open(
            io.BytesIO(image_bytes)
        ) as image:

            image.verify()


        # Open again after verify().

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
            "Unable to load emblem '%s': %s",
            EMBLEM_PATH,
            exc,
        )

        return None


# ============================================================
# DATABASE
# ============================================================

try:

    from database.database import init_db

except Exception as exc:

    init_db = None

    logger.warning(
        "Database module could not be imported: %s",
        exc,
    )


@st.cache_resource(
    show_spinner=False
)
def initialize_database() -> tuple[
    bool,
    str | None,
]:

    if init_db is None:

        return (
            False,
            "database.database.init_db could not be imported.",
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


st.session_state.database_connected = (
    database_connected
)

st.session_state.database_error = (
    database_error
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


        return list(
            modules
        )


    except Exception as exc:

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
# STATIC REGISTRY FEATURES
# ============================================================

FEATURES: dict[
    str,
    tuple[str, str],
] = {

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

p, label, span {{
    color: {theme["text"]};
}}


/* =========================================================
   SIDEBAR
   ========================================================= */

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


/* =========================================================
   HEADER
   ========================================================= */

.registry-header {{
    background: {theme["surface"]};
    border: 1px solid {theme["border"]};
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 20px;
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


/* =========================================================
   FALLBACK EMBLEM
   ========================================================= */

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


/* =========================================================
   PAGE CARD
   ========================================================= */

.page-card {{
    background: {theme["surface"]};
    border: 1px solid {theme["border"]};
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 18px;
}}


/* =========================================================
   KPI
   ========================================================= */

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


/* =========================================================
   CONTAINERS
   ========================================================= */

div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {theme["surface"]};
    border-color: {theme["border"]};
    border-radius: 14px;
}}


/* =========================================================
   FOOTER
   ========================================================= */

.registry-footer {{
    color: {theme["muted"]} !important;
    font-size: 11px;
}}


/* =========================================================
   STREAMLIT CHROME
   ========================================================= */

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

        st.rerun()


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
                '<div class="registry-emblem">SS</div>',
                unsafe_allow_html=True,
            )


        # ----------------------------------------------------
        # BRAND
        # ----------------------------------------------------

        st.subheader(
            "South Sudan National Registry"
        )

        st.caption(
            "National Population • Civil Registration • "
            "Identity • Elections"
        )


        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        if database_connected:

            st.success(
                "System Online"
            )

        else:

            # No icon argument.
            # This avoids the previous StreamlitAPIException.

            st.warning(
                "Database Attention Required"
            )


        st.divider()


        # ----------------------------------------------------
        # REGISTRY
        # ----------------------------------------------------

        st.markdown(
            "**Registry**"
        )


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


        # ----------------------------------------------------
        # OPERATIONS
        # ----------------------------------------------------

        st.markdown(
            "**Operations**"
        )


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


        # ----------------------------------------------------
        # ADMINISTRATION
        # ----------------------------------------------------

        st.markdown(
            "**Administration**"
        )


        sidebar_button(
            "administration",
            "Administration",
        )

        sidebar_button(
            "settings",
            "System Settings",
        )


        # ----------------------------------------------------
        # OTHER FEATURES
        # ----------------------------------------------------

        st.markdown(
            "**Other Features**"
        )


        sidebar_button(
            "statistics",
            "Statistics",
        )

        sidebar_button(
            "audit",
            "Audit & Activity",
        )


        st.divider()


        # ----------------------------------------------------
        # THEME
        # ----------------------------------------------------

        if st.session_state.dark_mode:

            theme_button_label = (
                "Switch to Light Mode"
            )

        else:

            theme_button_label = (
                "Switch to Dark Mode"
            )


        if st.button(
            theme_button_label,
            key="theme_button",
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
            key="refresh_button",
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

            st.title(
                "South Sudan National Registry"
            )

            st.caption(
                "National Population • Civil Registration • "
                "Identity • Elections"
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
    # KPI SECTION
    # --------------------------------------------------------

    st.subheader(
        "Registry Summary"
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

            render_service_card(
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
        "citizen and population database services are "
        "connected."
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
            "Population records will appear here after "
            "the population service is connected."
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
    """
    Attempt to render an existing module from
    modules.registry.

    Returns True when a module was found or handled.
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

        # Compatibility with a registry implementation
        # whose render_module() expects the module object.

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


# ============================================================
# ACTIVE PAGE
# ============================================================

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

    # First allow the existing module registry to handle it.

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
