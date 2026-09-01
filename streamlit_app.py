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
# DATABASE INITIALIZATION
# ============================================================

@st.cache_resource
def initialize_database() -> bool:
    """
    Initialize the registry database once per
    Streamlit process.
    """

    init_db()

    return True


try:

    initialize_database()

except Exception as exc:

    st.error(
        "The registry database could not be initialized."
    )

    with st.expander(
        "Database error"
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
# GLOBAL CSS
# ============================================================

def inject_css() -> None:
    """
    Apply global application styling.
    """

    dark = st.session_state.dark_mode

    if dark:

        background = "#0B1220"
        surface = "#111827"
        surface_alt = "#172033"
        text = "#F8FAFC"
        muted = "#94A3B8"
        border = "#263247"
        accent = "#16A34A"

    else:

        background = "#F8FAFC"
        surface = "#FFFFFF"
        surface_alt = "#F1F5F9"
        text = "#0F172A"
        muted = "#64748B"
        border = "#E2E8F0"
        accent = "#15803D"

    st.markdown(
        f"""
        <style>

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
            background: {background};
            color: {text};
        }}

        .block-container {{
            max-width: 1500px;
            padding-top: 1.2rem;
            padding-bottom: 5rem;
        }}

        h1,
        h2,
        h3,
        h4 {{
            color: {text};
        }}

        p,
        label {{
            color: {text};
        }}

        .registry-header {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 16px;
            padding: 18px 22px;
            margin-bottom: 18px;
        }}

        .registry-brand {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}

        .registry-emblem {{
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: {accent};
            color: white;
            font-weight: 800;
            font-size: 17px;
        }}

        .registry-title {{
            font-size: 21px;
            font-weight: 800;
            line-height: 1.2;
            color: {text};
        }}

        .registry-subtitle {{
            color: {muted};
            font-size: 13px;
            margin-top: 4px;
        }}

        .module-card {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 14px;
            padding: 18px;
            margin-bottom: 14px;
        }}

        .overview-card {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 16px;
        }}

        .status-card {{
            background: {surface_alt};
            border: 1px solid {border};
            border-radius: 12px;
            padding: 14px;
        }}

        div[data-testid="stMetric"] {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 14px;
            padding: 12px;
        }}

        .stButton > button {{
            border-radius: 10px;
            min-height: 40px;
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

            <div>

                <div class="registry-title">
                    South Sudan National Registry
                </div>

                <div class="registry-subtitle">
                    National Population • Civil Registration •
                    Identity • Elections
                </div>

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
    [7, 1, 1]
)

with control_col2:

    if st.button(
        "Light" if st.session_state.dark_mode else "Dark",
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
# LOAD MODULES
# ============================================================

all_modules = get_modules()

available_modules = get_available_modules()


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:
    """
    Render the Registry Home / Overview page.
    """

    st.title(
        "Registry Overview"
    )

    st.caption(
        "South Sudan National Registry — Streamlit AI Studio"
    )

    st.divider()

    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    total_modules = len(
        all_modules
    )

    available_count = len(
        available_modules
    )

    unavailable_count = (
        total_modules
        - available_count
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
            available_count,
        )

    with col3:

        st.metric(
            "Attention Required",
            unavailable_count,
        )

    with col4:

        st.metric(
            "Database",
            "Connected",
        )

    st.divider()

    # --------------------------------------------------------
    # SYSTEM DESCRIPTION
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="overview-card">

            <h3>
                National Registry Platform
            </h3>

            <p>
                Centralized platform for population
                registration, civil records, national
                identity, household information,
                electoral registration, document
                management and verification.
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # MODULE STATUS
    # --------------------------------------------------------

    st.subheader(
        "Module Status"
    )

    for module in all_modules:

        status_col1, status_col2 = st.columns(
            [4, 1]
        )

        with status_col1:

            st.write(
                f"**{module.label}**"
            )

            st.caption(
                module.description
            )

        with status_col2:

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


# ------------------------------------------------------------
# Determine current selection
# ------------------------------------------------------------

current_key = st.session_state.active_module

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
# RENDER ACTIVE PAGE
# ============================================================

if selected_key == "overview":

    render_overview()

else:

    selected_module = get_module(
        selected_key
    )

    if selected_module is None:

        st.error(
            "The requested registry module could not be found."
        )

    elif not selected_module.available:

        st.error(
            f"{selected_module.label} is currently unavailable."
        )

        if selected_module.error:

            with st.expander(
                "Technical details"
            ):

                st.code(
                    selected_module.error
                )

    else:

        st.caption(
            selected_module.description
        )

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

    st.caption(
        "South Sudan National Registry • "
        "Streamlit AI Studio"
    )

with footer_col2:

    st.caption(
        "Registry data should be treated as authoritative "
        "only after verification and appropriate "
        "administrative approval."
    )
