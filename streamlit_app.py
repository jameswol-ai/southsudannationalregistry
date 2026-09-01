"""
South Sudan National Registry
Streamlit AI Studio

National population, civil registration, identity,
household and electoral registry management platform.

Application entry point:
    streamlit run streamlit_app.py
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

st.set_page_config(
    page_title="South Sudan National Registry",
    page_icon="🇸🇸",
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
# SAFE EMBLEM LOADER
# ============================================================

def load_emblem():
    """
    Safely load assets/south_sudan_emblem.png.

    A missing, empty, corrupted, or invalid image must
    never crash the application.

    Returns:
        PIL Image or None.
    """

    if not EMBLEM_PATH.exists():

        logger.warning(
            "South Sudan emblem not found: %s",
            EMBLEM_PATH,
        )

        return None

    try:

        from PIL import Image

        raw = EMBLEM_PATH.read_bytes()

        if not raw:

            logger.warning(
                "South Sudan emblem is empty: %s",
                EMBLEM_PATH,
            )

            return None

        # Validate the image.
        with Image.open(
            io.BytesIO(raw)
        ) as image:

            image.verify()

        # verify() invalidates the object, so reopen it.
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
            "Invalid emblem image '%s': %s",
            EMBLEM_PATH,
            exc,
        )

        return None


# ============================================================
# DATABASE
# ============================================================

database_connected = False

database_error: Exception | None = None

try:

    from database.database import init_db

except Exception as exc:

    init_db = None

    database_error = exc

    logger.exception(
        "Could not import database.database.init_db."
    )


@st.cache_resource
def initialize_database() -> bool:

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

try:

    from modules.registry import (
        get_available_modules,
        get_module,
        render_module,
    )

except Exception as exc:

    logger.exception(
        "Could not load modules.registry."
    )

    get_available_modules = None
    get_module = None
    render_module = None


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
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 18px;
    margin-bottom: 8px;
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
}}


/* ============================================================
   HEADER
   ============================================================ */

.registry-header {{
    background: {theme["surface"]};
    border: 1px solid {theme["border"]};
    border-radius: 18px;
    padding: 18px 20px;
    margin-bottom: 20px;
}}

.registry-title {{
    color: {theme["text"]};
    font-size: 28px;
    font-weight: 800;
    line-height: 1.2;
}}

.registry-subtitle {{
    color: {theme["muted"]};
    font-size: 13px;
    line-height: 1.5;
    margin-top: 6px;
}}

.registry-status {{
    text-align: right;
}}

.status-online {{
    color: {theme["success"]};
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
   CARDS
   ============================================================ */

.overview-card,
.module-card,
.kpi-card {{
    background: {theme["surface"]};
    border: 1px solid {theme["border"]};
    border-radius: 15px;
}}

.overview-card {{
    padding: 22px;
    margin-bottom: 18px;
}}

.module-card {{
    padding: 18px;
    min-height: 125px;
    margin-bottom: 15px;
}}

.kpi-card {{
    padding: 18px;
    min-height: 120px;
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
    margin-top: 5px;
}}

.registry-description {{
    color: {theme["muted"]};
    font-size: 14px;
    line-height: 1.6;
    margin-top: 7px;
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

.kpi-label {{
    color: {theme["muted"]};
    font-size: 12px;
    font-weight: 700;
}}

.kpi-value {{
    color: {theme["text"]};
    font-size: 30px;
    font-weight: 800;
    margin-top: 6px;
}}

.kpi-description {{
    color: {theme["muted"]};
    font-size: 11px;
    margin-top: 5px;
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


inject_css()


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

def sidebar_navigation() -> None:

    emblem = load_emblem()

    with st.sidebar:

        # ----------------------------------------------------
        # Branding
        # ----------------------------------------------------

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


        st.markdown(
            """
<div>

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
        # DATABASE STATUS
        #
        # IMPORTANT:
        # No icon= argument is used here.
        # This avoids Streamlit emoji validation errors.
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
        # REGISTRY
        # ----------------------------------------------------

        st.markdown(
            '<div class="sidebar-section">Registry</div>',
            unsafe_allow_html=True,
        )


        registry_navigation = [
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


        for key, label in registry_navigation:

            if st.button(
                label,
                key=f"nav_{key}",
                use_container_width=True,
            ):

                st.session_state.active_module = key

                st.rerun()


        # ----------------------------------------------------
        # PLATFORM
        # ----------------------------------------------------

        st.markdown(
            '<div class="sidebar-section">Platform</div>',
            unsafe_allow_html=True,
        )


        platform_navigation = [
            (
                "reports",
                "Reports & Analytics",
            ),
            (
                "administration",
                "Administration",
            ),
        ]


        for key, label in platform_navigation:

            if st.button(
                label,
                key=f"nav_{key}",
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


        other_navigation = [
            (
                "documents",
                "Documents",
            ),
            (
                "verification",
                "Verification",
            ),
            (
                "households",
                "Households",
            ),
            (
                "statistics",
                "Statistics",
            ),
        ]


        for key, label in other_navigation:

            if st.button(
                label,
                key=f"nav_{key}",
                use_container_width=True,
            ):

                st.session_state.active_module = key

                st.rerun()


        # ----------------------------------------------------
        # SYSTEM
        # ----------------------------------------------------

        st.markdown(
            '<div class="sidebar-section">System</div>',
            unsafe_allow_html=True,
        )


        if st.button(
            "Settings",
            key="nav_settings",
            use_container_width=True,
        ):

            st.session_state.active_module = (
                "settings"
            )

            st.rerun()


        if st.button(
            "Refresh Application",
            key="nav_refresh",
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
            key="nav_theme",
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
            "Version 1.0.0"
        )


sidebar_navigation()


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

        st.markdown(
            """
<div>

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


    with col3:

        if database_connected:

            status_text = "System Online"

        else:

            status_text = "Database Attention"


        st.markdown(
            f"""
<div class="registry-status">

    <div class="status-online">
        <span class="status-dot"></span>
        {status_text}
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


render_header()


# ============================================================
# PAGE HELPERS
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
    # KPIs
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


# ============================================================
# CITIZENS
# ============================================================

def render_citizens() -> None:

    render_page_header(
        "Citizens",
        (
            "Citizen population records and citizen registry "
            "management."
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

    "households": (
        "Households",
        (
            "Manage household records and "
            "household relationships."
        ),
    ),

    "statistics": (
        "Statistics",
        (
            "View national Registry statistics "
            "and demographic summaries."
        ),
    ),

    "settings": (
        "System Settings",
        (
            "Configure Registry platform settings "
            "and system preferences."
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
}


def render_placeholder(
    key: str,
) -> None:

    title, description = (
        PLACEHOLDER_PAGES.get(
            key,
            (
                "Registry Feature",
                "Registry feature.",
            ),
        )
    )

    render_page_header(
        title,
        description,
    )

    st.info(
        f"{title} is ready for implementation."
    )


# ============================================================
# ACTIVE PAGE
# ============================================================

active_key = (
    st.session_state.active_module
)


# ------------------------------------------------------------
# Overview
# ------------------------------------------------------------

if active_key == "overview":

    render_overview()


# ------------------------------------------------------------
# Citizens
# ------------------------------------------------------------

elif active_key == "citizens":

    render_citizens()


# ------------------------------------------------------------
# Placeholder pages
# ------------------------------------------------------------

elif active_key in PLACEHOLDER_PAGES:

    render_placeholder(
        active_key
    )


# ------------------------------------------------------------
# Registry modules
# ------------------------------------------------------------

else:

    if get_module is None:

        st.error(
            "The Registry module system could not be loaded."
        )

    else:

        try:

            module = get_module(
                active_key
            )

        except Exception as exc:

            logger.exception(
                "Could not retrieve Registry module '%s'.",
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

            module = None


        if module is None:

            st.error(
                "The requested Registry module was not found."
            )

        else:

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


            elif render_module is None:

                st.error(
                    "The Registry module renderer is unavailable."
                )


            else:

                try:

                    render_module(
                        active_key
                    )

                except TypeError:

                    # Compatibility with registries whose
                    # render_module() expects a module object.
                    try:

                        render_module(
                            module
                        )

                    except Exception as exc:

                        logger.exception(
                            "Module '%s' failed.",
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
                        "Module '%s' failed.",
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


# ============================================================
# DATABASE WARNING
# ============================================================

if not database_connected:

    st.warning(
        "Registry interface is running without a connected database."
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

st.caption(
    "South Sudan National Registry • "
    "National Population • Civil Registration • "
    "Identity • Elections • Version 1.0.0"
    )
