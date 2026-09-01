"""
South Sudan National Registry
Streamlit AI Studio

National population, civil registration, identity,
household and electoral registry management platform.

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

Application entry point:

    streamlit run streamlit_app.py
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# IMPORTANT:
# Must be executed before Streamlit UI/session-state access.
# ============================================================

st.set_page_config(
    page_title="South Sudan National Registry",
    page_icon="🇸🇸",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

ASSETS_DIR = BASE_DIR / "assets"

LOGO_PATH = (
    ASSETS_DIR
    / "south_sudan_emblem.png"
)


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(
    "south_sudan_national_registry"
)


# ============================================================
# DATABASE
# ============================================================

from database.database import init_db


@st.cache_resource
def initialize_database() -> bool:
    """
    Initialize the registry database once per Streamlit process.
    """

    init_db()

    return True


# ============================================================
# MODULE REGISTRY
# ============================================================

from modules.registry import (
    get_available_modules,
    get_module,
    render_module,
)


# ============================================================
# MODULE LOADING
# ============================================================

def load_available_modules() -> list[Any]:
    """
    Load modules that successfully imported and expose
    a callable render() function.
    """

    try:

        modules = get_available_modules()

        if modules is None:
            return []

        return list(modules)

    except Exception as exc:

        logger.exception(
            "Unable to load available registry modules."
        )

        return []


def load_all_modules() -> list[Any]:
    """
    Load all configured modules, including unavailable modules.

    This allows the Overview dashboard to show module health.
    """

    try:

        from modules.registry import MODULES

        if isinstance(MODULES, dict):

            return list(
                MODULES.values()
            )

    except Exception as exc:

        logger.warning(
            "Unable to load complete module registry: %s",
            exc,
        )

    return load_available_modules()


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

try:

    initialize_database()

except Exception as exc:

    st.error(
        "The South Sudan National Registry database "
        "could not be initialized."
    )

    with st.expander(
        "Technical details"
    ):

        st.exception(exc)

    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

if "active_module" not in st.session_state:

    st.session_state.active_module = "overview"


if "dark_mode" not in st.session_state:

    st.session_state.dark_mode = True


# ============================================================
# THEME
# ============================================================

def get_theme() -> dict[str, str]:
    """
    Return application colors for the active theme.
    """

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
# GLOBAL CSS
# ============================================================

def inject_css() -> None:
    """
    Inject global application styling.
    """

    theme = get_theme()

    st.markdown(
        f"""
        <style>

        /* ====================================================
           GLOBAL
           ==================================================== */

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
            padding-top: 0.5rem;
            padding-bottom: 8rem;
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


        /* ====================================================
           NATIONAL REGISTRY HEADER
           ==================================================== */

        .registry-header {{
            width: 100%;

            text-align: center;

            padding:
                18px 10px 20px;

            margin-bottom: 8px;
        }}

        .registry-brand {{
            display: flex;

            flex-direction: column;

            align-items: center;

            justify-content: center;
        }}

        .registry-logo {{
            display: block;

            width: 150px;

            max-width: 40vw;

            height: auto;

            object-fit: contain;

            margin:
                0 auto 12px auto;
        }}

        .registry-title {{
            color: {theme["text"]};

            font-size: 28px;

            font-weight: 850;

            line-height: 1.25;

            margin: 0;
        }}

        .registry-subtitle {{
            color: {theme["muted"]};

            font-size: 13px;

            font-weight: 500;

            line-height: 1.5;

            margin-top: 7px;

            max-width: 800px;

            margin-left: auto;

            margin-right: auto;
        }}


        /* ====================================================
           OVERVIEW
           ==================================================== */

        .overview-card {{
            background: {theme["surface"]};

            border:
                1px solid {theme["border"]};

            border-radius: 16px;

            padding: 22px;

            margin-bottom: 18px;
        }}

        .registry-kicker {{
            color: {theme["accent"]};

            font-size: 12px;

            font-weight: 800;

            text-transform: uppercase;

            letter-spacing: 0.08em;

            margin-bottom: 6px;
        }}

        .registry-heading {{
            color: {theme["text"]};

            font-size: 22px;

            font-weight: 800;

            line-height: 1.3;

            margin-bottom: 7px;
        }}

        .registry-description {{
            color: {theme["muted"]};

            font-size: 14px;

            line-height: 1.6;

            max-width: 1000px;
        }}


        /* ====================================================
           MODULE STATUS
           ==================================================== */

        .module-card {{
            background: {theme["surface"]};

            border:
                1px solid {theme["border"]};

            border-radius: 14px;

            padding: 17px;

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

            margin-top: 4px;
        }}


        /* ====================================================
           METRICS
           ==================================================== */

        div[data-testid="stMetric"] {{
            background: {theme["surface"]};

            border:
                1px solid {theme["border"]};

            border-radius: 14px;

            padding: 14px;
        }}

        div[data-testid="stMetricLabel"] {{
            color: {theme["muted"]} !important;
        }}

        div[data-testid="stMetricValue"] {{
            color: {theme["text"]} !important;
        }}


        /* ====================================================
           BUTTONS
           ==================================================== */

        .stButton > button {{
            border-radius: 10px;

            min-height: 40px;

            font-weight: 600;
        }}


        /* ====================================================
           SELECT BOX
           ==================================================== */

        div[data-baseweb="select"] > div {{
            border-radius: 10px;

            border-color:
                {theme["border"]};
        }}


        /* ====================================================
           INPUTS
           ==================================================== */

        input,
        textarea {{
            border-radius: 10px !important;
        }}


        /* ====================================================
           BOTTOM NAVIGATION
           ==================================================== */

        .bottom-nav {{
            position: fixed;

            left: 50%;

            bottom: 12px;

            transform:
                translateX(-50%);

            z-index: 999;

            width:
                min(96vw, 1200px);

            background:
                {theme["surface"]};

            border:
                1px solid {theme["border"]};

            border-radius: 18px;

            padding: 8px;

            box-shadow:
                0 12px 35px
                rgba(0, 0, 0, 0.18);
        }}


        /* ====================================================
           FOOTER
           ==================================================== */

        .registry-footer {{
            color: {theme["muted"]};

            font-size: 12px;

            line-height: 1.5;
        }}


        /* ====================================================
           STREAMLIT UI
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
# NATIONAL HEADER
# ============================================================

st.markdown(
    """
    <div class="registry-header">

        <div class="registry-brand">
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# NATIONAL EMBLEM
# ------------------------------------------------------------

if LOGO_PATH.exists():

    st.image(
        str(LOGO_PATH),
        width=150,
    )

else:

    st.warning(
        "National emblem not found. "
        "Place the logo at "
        "assets/south_sudan_emblem.png"
    )


# ------------------------------------------------------------
# BRAND TEXT
# ------------------------------------------------------------

st.markdown(
    """
        <div class="registry-title">
            South Sudan National Registry
        </div>

        <div class="registry-subtitle">
            National Population • Civil Registration •
            Identity • Elections
        </div>

        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TOP CONTROLS
# ============================================================

control_col1, control_col2, control_col3 = st.columns(
    [8, 1, 1]
)


with control_col2:

    if st.button(
        (
            "Light"
            if st.session_state.dark_mode
            else "Dark"
        ),
        key="theme_toggle",
        use_container_width=True,
    ):

        st.session_state.dark_mode = (
            not st.session_state.dark_mode
        )

        st.rerun()


with control_col3:

    if st.button(
        "Refresh",
        key="refresh_application",
        use_container_width=True,
    ):

        st.rerun()


# ============================================================
# LOAD MODULES
# ============================================================

all_modules = load_all_modules()

available_modules = load_available_modules()


# ============================================================
# NAVIGATION ITEMS
# ============================================================

navigation_items: list[tuple[str, str]] = [
    (
        "overview",
        "Overview",
    )
]


for module in available_modules:

    key = getattr(
        module,
        "key",
        None,
    )

    label = getattr(
        module,
        "label",
        None,
    )


    if not key:

        continue


    if not label:

        label = (
            str(key)
            .replace("_", " ")
            .title()
        )


    navigation_items.append(
        (
            str(key),
            str(label),
        )
    )


# ============================================================
# VALID ACTIVE MODULE
# ============================================================

valid_keys = {
    key
    for key, _ in navigation_items
}


if (
    st.session_state.active_module
    not in valid_keys
):

    st.session_state.active_module = (
        "overview"
    )


# ============================================================
# MODULE SELECTOR
# ============================================================

navigation_labels = [
    label
    for _, label
    in navigation_items
]


current_key = (
    st.session_state.active_module
)


current_label = next(
    (
        label
        for key, label
        in navigation_items
        if key == current_key
    ),
    "Overview",
)


selected_label = st.selectbox(
    "Registry module",
    navigation_labels,
    index=(
        navigation_labels.index(
            current_label
        )
        if current_label
        in navigation_labels
        else 0
    ),
    label_visibility="collapsed",
    key="registry_module_selector",
)


selected_key = next(
    (
        key
        for key, label
        in navigation_items
        if label == selected_label
    ),
    "overview",
)


if (
    selected_key
    != st.session_state.active_module
):

    st.session_state.active_module = (
        selected_key
    )

    st.rerun()


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:
    """
    Render the national registry control centre.
    """

    # --------------------------------------------------------
    # INTRODUCTION
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="overview-card">

            <div class="registry-kicker">
                Registry Control Centre
            </div>

            <div class="registry-heading">
                National Registry Overview
            </div>

            <div class="registry-description">
                Centralized management platform for population
                registration, civil records, national identity,
                households, electoral registration, documents
                and verification.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # MODULE KPIs
    # --------------------------------------------------------

    total_modules = len(
        all_modules
    )

    operational_modules = len(
        [
            module
            for module in all_modules
            if bool(
                getattr(
                    module,
                    "available",
                    False,
                )
            )
        ]
    )

    unavailable_modules = (
        total_modules
        - operational_modules
    )


    col1, col2, col3, col4 = st.columns(
        4
    )


    with col1:

        st.metric(
            "Registry Modules",
            total_modules,
        )


    with col2:

        st.metric(
            "Operational",
            operational_modules,
        )


    with col3:

        st.metric(
            "Attention Required",
            unavailable_modules,
        )


    with col4:

        st.metric(
            "Database",
            "Connected",
        )


    # --------------------------------------------------------
    # MODULE STATUS
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "Registry Modules"
    )


    if not all_modules:

        st.info(
            "No registry modules are currently configured."
        )

    else:

        for module in all_modules:

            name = getattr(
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

            left, right = st.columns(
                [5, 1]
            )


            with left:

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


            with right:

                if available:

                    st.success(
                        "Operational"
                    )

                else:

                    st.error(
                        "Unavailable"
                    )

                    error = getattr(
                        module,
                        "error",
                        None,
                    )

                    if error:

                        with st.expander(
                            "Details"
                        ):

                            st.code(
                                error
                            )


    # --------------------------------------------------------
    # SYSTEM ARCHITECTURE
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "System Architecture"
    )

    architecture_col1, architecture_col2 = (
        st.columns(2)
    )


    with architecture_col1:

        st.markdown(
            """
            ### Application Layer

            **Next.js AI Studio**

            National Registry web interface,
            administration and AI-assisted workflows.

            **Streamlit AI Studio**

            Operational registry control centre,
            analytics and administrative tools.
            """
        )


    with architecture_col2:

        st.markdown(
            """
            ### Data Layer

            **Registry API**

            Application programming interface connecting
            the frontend applications to the backend.

            **Service Layer**

            Business logic for citizens, households,
            registration, identity, verification and
            reporting.

            **SQLAlchemy**

            Database abstraction layer supporting
            PostgreSQL and SQLite.
            """
        )


    st.divider()

    st.caption(
        "Registry data should be treated as authoritative "
        "only after verification and appropriate "
        "administrative approval."
    )


# ============================================================
# ACTIVE MODULE DESCRIPTION
# ============================================================

if selected_key != "overview":

    active_module = get_module(
        selected_key
    )

    if active_module:

        description = getattr(
            active_module,
            "description",
            "",
        )

        if description:

            st.markdown(
                f"""
                <div class="overview-card">

                    <div class="registry-kicker">
                        Registry Module
                    </div>

                    <div class="registry-heading">
                        {active_module.label}
                    </div>

                    <div class="registry-description">
                        {description}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# RENDER ACTIVE MODULE
# ============================================================

if selected_key == "overview":

    render_overview()

else:

    active_module = get_module(
        selected_key
    )


    if active_module is None:

        st.error(
            "The requested registry module "
            "could not be found."
        )


    else:

        available = bool(
            getattr(
                active_module,
                "available",
                False,
            )
        )


        if not available:

            st.error(
                "This registry module is currently unavailable."
            )

            error = getattr(
                active_module,
                "error",
                None,
            )

            with st.expander(
                "Technical details"
            ):

                st.code(
                    error
                    or "No technical details available."
                )


        else:

            try:

                render_module(
                    selected_key
                )

            except Exception as exc:

                logger.exception(
                    "Runtime error in registry module '%s'",
                    selected_key,
                )

                st.error(
                    "The selected registry module "
                    "encountered a runtime error."
                )

                with st.expander(
                    "Technical details"
                ):

                    st.exception(exc)


# ============================================================
# BOTTOM NAVIGATION
# ============================================================

st.markdown(
    '<div class="bottom-nav">',
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Display first six navigation items.
# Full navigation remains available above.
# ------------------------------------------------------------

visible_navigation = navigation_items[:6]


if visible_navigation:

    nav_columns = st.columns(
        len(visible_navigation)
    )


    for index, (
        key,
        label,
    ) in enumerate(
        visible_navigation
    ):

        with nav_columns[index]:

            is_active = (
                key
                == st.session_state.active_module
            )


            button_label = (
                f"● {label}"
                if is_active
                else label
            )


            if st.button(
                button_label,
                key=(
                    f"bottom_navigation_{key}"
                ),
                use_container_width=True,
            ):

                if (
                    st.session_state.active_module
                    != key
                ):

                    st.session_state.active_module = (
                        key
                    )

                    st.rerun()


st.markdown(
    "</div>",
    unsafe_allow_html=True,
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
            Streamlit AI Studio
        </div>
        """,
        unsafe_allow_html=True,
    )


with footer_col2:

    st.markdown(
        """
        <div class="registry-footer">
            National Population • Civil Registration •
            Identity • Households • Elections •
            Documents • Verification
        </div>
        """,
        unsafe_allow_html=True,
)
