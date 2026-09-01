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


# ============================================================
# PAGE CONFIGURATION
# IMPORTANT:
# This MUST happen before any st.session_state access.
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

from database.database import init_db


@st.cache_resource
def initialize_database() -> bool:
    """
    Initialize database tables once per Streamlit process.
    """

    init_db()

    return True


initialize_database()


# ============================================================
# MODULE REGISTRY
# ============================================================

from modules.registry import (
    get_module,
    get_modules,
)


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

        html, body, [class*="css"] {{
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
            padding-bottom: 4rem;
        }}

        h1, h2, h3 {{
            color: {text};
        }}

        p, label {{
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

        div[data-testid="stMetric"] {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 14px;
            padding: 12px;
        }}

        .bottom-nav {{
            position: fixed;
            bottom: 12px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 999;
            background: {surface};
            border: 1px solid {border};
            border-radius: 18px;
            padding: 8px;
            box-shadow:
                0 12px 35px rgba(0, 0, 0, 0.18);
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
                    National Population • Civil Registration • Identity • Elections
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

        st.rerun()


# ============================================================
# NAVIGATION
# ============================================================

modules = get_modules()

module_labels = [
    module.label
    for module in modules
]

active_module = get_module(
    st.session_state.active_module
)

active_label = (
    active_module.label
    if active_module
    else "Overview"
)

selected_label = st.selectbox(
    "Module",
    module_labels,
    index=(
        module_labels.index(active_label)
        if active_label in module_labels
        else 0
    ),
    label_visibility="collapsed",
)

selected_module = next(
    (
        module
        for module in modules
        if module.label == selected_label
    ),
    modules[0],
)

if (
    selected_module.key
    != st.session_state.active_module
):

    st.session_state.active_module = (
        selected_module.key
    )


# ============================================================
# MODULE DESCRIPTION
# ============================================================

st.caption(
    selected_module.description
)


# ============================================================
# RENDER ACTIVE MODULE
# ============================================================

try:

    selected_module.render()

except Exception as exc:

    st.error(
        "The selected registry module encountered an error."
    )

    with st.expander(
        "Technical details"
    ):

        st.exception(exc)


# ============================================================
# FOOTER
# ============================================================

st.divider()

footer_col1, footer_col2 = st.columns(2)

with footer_col1:

    st.caption(
        "South Sudan National Registry • Streamlit AI Studio"
    )

with footer_col2:

    st.caption(
        "Registry data should be treated as authoritative only "
        "after verification and appropriate administrative approval."
    )
