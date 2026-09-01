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
"""

from __future__ import annotations

import streamlit as st

from database.database import init_db
from modules.registry import (
    get_available_modules,
    get_module,
    get_modules,
    render_module,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="South Sudan National Registry",
    page_icon="SS",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# SESSION STATE
# ============================================================

if "active_module" not in st.session_state:
    st.session_state.active_module = "overview"

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True


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


try:
    initialize_database()

except Exception as exc:

    st.error(
        "The South Sudan National Registry database "
        "could not be initialized."
    )

    with st.expander("Technical details"):

        st.exception(exc)

    st.stop()


# ============================================================
# THEME
# ============================================================

def get_theme() -> dict[str, str]:
    """
    Return the active application theme.
    """

    if st.session_state.dark_mode:

        return {
            "background": "#0B1220",
            "surface": "#111827",
            "surface_alt": "#172033",
            "text": "#F8FAFC",
            "muted": "#94A3B8",
            "border": "#263247",
            "accent": "#16A34A",
            "accent_dark": "#15803D",
            "white": "#FFFFFF",
        }

    return {
        "background": "#F8FAFC",
        "surface": "#FFFFFF",
        "surface_alt": "#F1F5F9",
        "text": "#0F172A",
        "muted": "#64748B",
        "border": "#E2E8F0",
        "accent": "#15803D",
        "accent_dark": "#166534",
        "white": "#FFFFFF",
    }


# ============================================================
# GLOBAL CSS
# ============================================================

def inject_css() -> None:
    """
    Inject application-wide styling.
    """

    theme = get_theme()

    st.markdown(
        f"""
        <style>

        /* ==================================================
           GLOBAL
           ================================================== */

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
            padding-top: 1rem;
            padding-bottom: 7rem;
        }}

        h1,
        h2,
        h3,
        h4,
        h5 {{
            color: {theme["text"]};
        }}

        p,
        label,
        span {{
            color: {theme["text"]};
        }}

        /* ==================================================
           HEADER
           ================================================== */

        .registry-header {{
            background: transparent;
            border: none;
            padding: 22px 10px 12px;
            margin-bottom: 8px;
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
            color: {theme["white"]};
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
            margin-top: 7px;
        }}

        /* ==================================================
           SECTION CARDS
           ================================================== */

        .overview-card {{
            background: {theme["surface"]};
            border: 1px solid {theme["border"]};
            border-radius: 16px;
            padding: 22px;
            margin-bottom: 16px;
        }}

        .module-card {{
            background: {theme["surface"]};
            border: 1px solid {theme["border"]};
            border-radius: 14px;
            padding: 18px;
            margin-bottom: 14px;
        }}

        .status-card {{
            background: {theme["surface_alt"]};
            border: 1px solid {theme["border"]};
            border-radius: 12px;
            padding: 14px;
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
            margin-bottom: 6px;
        }}

        .registry-description {{
            color: {theme["muted"]};
            font-size: 14px;
            line-height: 1.6;
        }}

        /* ==================================================
           METRICS
           ================================================== */

        div[data-testid="stMetric"] {{
            background: {theme["surface"]};
            border: 1px solid {theme["border"]};
            border-radius: 14px;
            padding: 14px;
        }}

        div[data-testid="stMetricLabel"] {{
            color: {theme["muted"]};
        }}

        div[data-testid="stMetricValue"] {{
            color: {theme["text"]};
        }}

        /* ==================================================
           BUTTONS
           ================================================== */

        .stButton > button {{
            border-radius: 10px;
            min-height: 40px;
            font-weight: 600;
        }}

        /* ==================================================
           SELECTBOX
           ================================================== */

        div[data-baseweb="select"] > div {{
            border-radius: 10px;
            border-color: {theme["border"]};
        }}

        /* ==================================================
           BOTTOM NAVIGATION
           ================================================== */

        .bottom-nav {{
            position: fixed;
            left: 50%;
            bottom: 12px;
            transform: translateX(-50%);
            z-index: 999;
            width: min(96vw, 1100px);
            background: {theme["surface"]};
            border: 1px solid {theme["border"]};
            border-radius: 18px;
            padding: 8px;
            box-shadow:
                0 12px 35px rgba(0, 0, 0, 0.18);
        }}

        /* ==================================================
           FOOTER
           ================================================== */

        .registry-footer {{
            color: {theme["muted"]};
            font-size: 12px;
            line-height: 1.5;
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

    theme_label = (
        "Light"
        if st.session_state.dark_mode
        else "Dark"
    )

    if st.button(
        theme_label,
        use_container_width=True,
    ):

        st.session_state.dark_mode = (
            not st.session_state.dark_mode
        )

        st.rerun()


with control_col3:

    if st.button(
        "Refresh",
        use_container_width=True,
    ):

        st.cache_resource.clear()

        st.rerun()


# ============================================================
# MODULE REGISTRY
# ============================================================

all_modules = get_modules()

available_modules = get_available_modules()


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:
    """
    Render the Registry Home / Overview dashboard.
    """

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
                Centralized management platform for
                population registration, civil records,
                national identity, households, electoral
                registration, documents and verification.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    total_modules = len(
        all_modules
    )

    operational_modules = len(
        available_modules
    )

    attention_modules = (
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
            attention_modules,
        )

    with col4:

        st.metric(
            "Database",
            "Connected",
        )

    st.divider()

    # --------------------------------------------------------
    # OPERATIONAL MODULES
    # --------------------------------------------------------

    st.subheader(
        "Registry Modules"
    )

    if not all_modules:

        st.info(
            "No registry modules are currently configured."
        )

        return

    for module in all_modules:

        left, right = st.columns(
            [5, 1]
        )

        with left:

            st.markdown(
                f"**{module.label}**"
            )

            st.caption(
                module.description
            )

        with right:

            if module.available:

                st.success(
                    "Operational"
                )

            else:

                st.error(
                    "Unavailable"
                )

        if not module.available:

            with st.expander(
                f"Technical details — {module.label}"
            ):

                st.code(
                    module.error
                    or "Unknown module error."
                )

    # --------------------------------------------------------
    # PLATFORM ARCHITECTURE
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "Platform Architecture"
    )

    st.markdown(
        """
        ```text
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
        ```
        """
    )


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

navigation_options = [
    (
        "overview",
        "Overview",
    )
]

navigation_options.extend(
    (
        module.key,
        module.label,
    )
    for module in available_modules
)

navigation_labels = [
    label
    for _, label in navigation_options
]


# ============================================================
# CURRENT NAVIGATION
# ============================================================

current_key = (
    st.session_state.active_module
)

current_label = next(
    (
        label
        for key, label
        in navigation_options
        if key == current_key
    ),
    "Overview",
)


selected_label = st.selectbox(
    "Registry module",
    navigation_labels,
    index=navigation_labels.index(
        current_label
    ),
    label_visibility="collapsed",
)


selected_key = next(
    (
        key
        for key, label
        in navigation_options
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
# BOTTOM NAVIGATION
# ============================================================

if navigation_labels:

    st.markdown(
        '<div class="bottom-nav">',
        unsafe_allow_html=True,
    )

    nav_columns = st.columns(
        min(
            len(navigation_options),
            6,
        )
    )

    for index, (
        key,
        label,
    ) in enumerate(
        navigation_options
    ):

        column = nav_columns[
            index % len(nav_columns)
        ]

        with column:

            if st.button(
                label,
                key=f"bottom_nav_{key}",
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
# ACTIVE MODULE DESCRIPTION
# ============================================================

if selected_key != "overview":

    selected_module = get_module(
        selected_key
    )

    if selected_module:

        st.caption(
            selected_module.description
        )


# ============================================================
# RENDER ACTIVE MODULE
# ============================================================

if selected_key == "overview":

    render_overview()

else:

    selected_module = get_module(
        selected_key
    )

    if selected_module is None:

        st.error(
            "The requested registry module "
            "could not be found."
        )

    elif not selected_module.available:

        st.error(
            f"{selected_module.label} "
            "is currently unavailable."
        )

        with st.expander(
            "Technical details"
        ):

            st.code(
                selected_module.error
                or "Unknown module error."
            )

    else:

        try:

            render_module(
                selected_key
            )

        except Exception as exc:

            st.error(
                "The selected registry module "
                "encountered a runtime error."
            )

            with st.expander(
                "Technical details"
            ):

                st.exception(exc)


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
            Registry data should be treated as
            authoritative only after verification
            and appropriate administrative approval.
        </div>
        """,
        unsafe_allow_html=True,
    )
