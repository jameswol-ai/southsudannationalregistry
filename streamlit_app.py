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
from typing import Any

import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# IMPORTANT:
# This must be executed before Streamlit UI/session-state work.
# ============================================================

st.set_page_config(
    page_title="South Sudan National Registry",
    page_icon="SS",
    layout="wide",
    initial_sidebar_state="collapsed",
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

    SQLite is used automatically when DATABASE_URL is not supplied.
    PostgreSQL can be supplied through DATABASE_URL.
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
# REGISTRY COMPATIBILITY
# ============================================================

def load_registry_modules() -> list[Any]:
    """
    Return registry modules in a predictable list format.

    The application primarily uses get_available_modules().

    A compatibility fallback is included for registry versions
    that expose MODULES but do not yet expose get_modules().
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


def load_all_registry_modules() -> list[Any]:
    """
    Return all configured registry modules where possible.

    This is used by the Overview dashboard to show operational
    and unavailable modules.
    """

    try:

        from modules.registry import MODULES

        if isinstance(MODULES, dict):

            return list(MODULES.values())

    except Exception:

        pass

    return load_registry_modules()


# ============================================================
# SESSION STATE
# ============================================================

if "active_module" not in st.session_state:

    st.session_state.active_module = "overview"


if "dark_mode" not in st.session_state:

    st.session_state.dark_mode = True


# ============================================================
# DATABASE STARTUP
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
# THEME
# ============================================================

def get_theme() -> dict[str, str]:
    """
    Return the current application theme.
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
# CSS
# ============================================================

def inject_css() -> None:
    """
    Inject global Streamlit styling.
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
            padding-top: 0.8rem;
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
           HEADER
           ==================================================== */

        .registry-header {{
            background: transparent;
            border: none;
            padding: 22px 10px 14px;
            margin-bottom: 4px;
            text-align: center;
        }}

        .registry-brand {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}

        .registry-emblem {{
            width: 58px;
            height: 58px;
            border-radius: 14px;

            display: flex;
            align-items: center;
            justify-content: center;

            background: {theme["accent"]};
            color: #FFFFFF;

            font-weight: 900;
            font-size: 19px;
            letter-spacing: 0.5px;

            margin-bottom: 12px;

            box-shadow:
                0 8px 24px rgba(22, 163, 74, 0.20);
        }}

        .registry-title {{
            font-size: 26px;
            font-weight: 800;
            line-height: 1.2;
            color: {theme["text"]};
        }}

        .registry-subtitle {{
            color: {theme["muted"]};
            font-size: 13px;
            line-height: 1.5;
            margin-top: 7px;
        }}


        /* ====================================================
           OVERVIEW
           ==================================================== */

        .overview-card {{
            background: {theme["surface"]};
            border: 1px solid {theme["border"]};
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

            max-width: 950px;
        }}


        /* ====================================================
           MODULE CARDS
           ==================================================== */

        .module-card {{
            background: {theme["surface"]};
            border: 1px solid {theme["border"]};
            border-radius: 14px;

            padding: 18px;
            margin-bottom: 14px;
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


        /* ====================================================
           STATUS
           ==================================================== */

        .status-operational {{
            color: {theme["success"]};
            font-weight: 700;
        }}

        .status-unavailable {{
            color: {theme["danger"]};
            font-weight: 700;
        }}


        /* ====================================================
           METRICS
           ==================================================== */

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


        /* ====================================================
           BUTTONS
           ==================================================== */

        .stButton > button {{
            border-radius: 10px;
            min-height: 40px;
            font-weight: 600;
        }}


        /* ====================================================
           INPUTS
           ==================================================== */

        div[data-baseweb="select"] > div {{
            border-radius: 10px;
            border-color: {theme["border"]};
        }}

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

            transform: translateX(-50%);

            z-index: 999;

            width: min(96vw, 1200px);

            background: {theme["surface"]};

            border: 1px solid {theme["border"]};

            border-radius: 18px;

            padding: 8px;

            box-shadow:
                0 12px 35px rgba(0, 0, 0, 0.18);
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
# HEADER
# ============================================================

st.markdown(
    """
    <div class="registry-header">

        <div class="registry-brand">

            <div class="registry-emblem">
                SS
            </div>

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

    theme_button = (
        "Light"
        if st.session_state.dark_mode
        else "Dark"
    )

    if st.button(
        theme_button,
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

all_modules = load_all_registry_modules()

available_modules = load_registry_modules()


# ============================================================
# OVERVIEW RENDERER
# ============================================================

def render_overview() -> None:
    """
    Render the national registry home dashboard.
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
    # SYSTEM KPIs
    # --------------------------------------------------------

    total_modules = len(
        all_modules
    )

    operational_modules = len(
        [
            module
            for module in all_modules
            if getattr(
                module,
                "available",
                False,
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
                    <div class="module-name">
                        {name}
                    </div>

                    <div class="module-description">
                        {description}
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


            if not available:

                error = getattr(
                    module,
                    "error",
                    None,
                )

                with st.expander(
                    f"Technical details — {name}"
                ):

                    st.code(
                        error
                        or "Unknown module error."
                    )


    # --------------------------------------------------------
    # PLATFORM ARCHITECTURE
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "Platform Architecture"
    )

    st.code(
        """
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
        """.strip(),
        language="text",
    )


# ============================================================
# NAVIGATION MODEL
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

        label = str(key).replace(
            "_",
            " ",
        ).title()

    navigation_items.append(
        (
            str(key),
            str(label),
        )
    )


# ============================================================
# ENSURE ACTIVE MODULE IS VALID
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
    for _, label in navigation_items
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
        if current_label in navigation_labels
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

            st.caption(
                description
            )


# ============================================================
# ACTIVE MODULE CONTENT
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

        is_available = bool(
            getattr(
                active_module,
                "available",
                False,
            )
        )


        if not is_available:

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
                    or "Unknown module error."
                )


        else:

            try:

                render_module(
                    selected_key
                )

            except Exception as exc:

                logger.exception(
                    "Runtime error in registry module '%s'.",
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


# Keep the number of visible buttons manageable.
# The selectbox remains available for the complete module list.

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
                key=f"bottom_navigation_{key}",
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
            Registry data should be treated as authoritative
            only after verification and appropriate
            administrative approval.
        </div>
        """,
        unsafe_allow_html=True,
    )
