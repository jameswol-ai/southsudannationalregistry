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
# st.set_page_config() must run before Streamlit UI work.
#
# IMPORTANT:
# Do NOT use the South Sudan emblem PNG here.
# A corrupt/invalid image can cause Streamlit/Pillow to fail
# before the application is able to render.
# ============================================================

st.set_page_config(
    page_title="South Sudan National Registry",
    page_icon="🇸🇸",
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
    Return available registry modules in a predictable list format.

    The function is deliberately defensive because registry
    implementations may return different iterable types.
    """

    try:
        modules = get_available_modules()

        if modules is None:
            return []

        if isinstance(modules, dict):
            return list(modules.values())

        return list(modules)

    except Exception:
        logger.exception(
            "Unable to load available registry modules."
        )

        return []


def load_all_registry_modules() -> list[Any]:
    """
    Return all configured registry modules where possible.

    This allows the Overview dashboard to display module
    availability without preventing the rest of the application
    from starting.
    """

    try:
        from modules.registry import MODULES

        if isinstance(MODULES, dict):
            return list(MODULES.values())

    except Exception:
        logger.debug(
            "MODULES registry was not available.",
            exc_info=True,
        )

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

        .stApp {{
            background: {theme["background"]};
            color: {theme["text"]};
        }}

        .block-container {{
            max-width: 1500px;
            padding-top: 0.8rem;
            padding-bottom: 7rem;
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
        label,
        span {{
            color: {theme["text"]};
        }}


        /* ====================================================
           REGISTRY HEADER
           ==================================================== */

        .registry-header {{
            width: 100%;
            text-align: center;

            padding: 18px 10px 14px;

            margin-bottom: 10px;
        }}

        .registry-brand {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}

        .registry-title {{
            font-size: 28px;
            font-weight: 800;
            line-height: 1.2;

            color: {theme["text"]};

            letter-spacing: -0.02em;
        }}

        .registry-subtitle {{
            color: {theme["muted"]};

            font-size: 13px;

            line-height: 1.5;

            margin-top: 7px;
        }}


        /* ====================================================
           CSS EMBLEM FALLBACK
           ==================================================== */

        .registry-emblem {{
            width: 72px;
            height: 72px;

            margin: 0 auto 12px;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 50%;

            background: {theme["accent"]};

            border: 4px solid #FBBF24;

            color: #FFFFFF;

            font-size: 20px;
            font-weight: 900;

            letter-spacing: 1px;

            box-shadow:
                0 5px 18px rgba(0, 0, 0, 0.18);
        }}


        /* ====================================================
           SYSTEM STATUS
           ==================================================== */

        .registry-system-status {{
            display: inline-flex;

            align-items: center;

            gap: 7px;

            margin-top: 10px;

            color: {theme["success"]};

            font-size: 12px;

            font-weight: 700;
        }}

        .status-dot {{
            width: 8px;
            height: 8px;

            border-radius: 50%;

            background: {theme["success"]};

            display: inline-block;
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

            box-shadow:
                0 2px 8px rgba(0, 0, 0, 0.05);
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
           KPI CARDS
           ==================================================== */

        .kpi-card {{
            background: {theme["surface"]};

            border: 1px solid {theme["border"]};

            border-radius: 14px;

            padding: 18px;

            min-height: 125px;

            margin-bottom: 14px;

            box-shadow:
                0 2px 8px rgba(0, 0, 0, 0.04);

            box-sizing: border-box;
        }}

        .kpi-label {{
            color: {theme["muted"]};

            font-size: 12px;

            font-weight: 700;

            margin-bottom: 8px;
        }}

        .kpi-value {{
            color: {theme["text"]};

            font-size: 30px;

            font-weight: 800;

            line-height: 1;
        }}

        .kpi-description {{
            color: {theme["muted"]};

            font-size: 11px;

            margin-top: 9px;

            line-height: 1.4;
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

            min-height: 130px;

            box-sizing: border-box;

            box-shadow:
                0 2px 8px rgba(0, 0, 0, 0.04);
        }}

        .module-name {{
            color: {theme["text"]};

            font-size: 16px;

            font-weight: 750;

            line-height: 1.3;
        }}

        .module-description {{
            color: {theme["muted"]};

            font-size: 13px;

            line-height: 1.5;

            margin-top: 6px;
        }}


        /* ====================================================
           MODULE STATUS
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
           STREAMLIT METRICS
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

            border: 1px solid {theme["border"]};

            background: {theme["surface"]};

            color: {theme["text"]};
        }}

        .stButton > button:hover {{
            border-color: {theme["accent"]};

            color: {theme["accent"]};
        }}


        /* ====================================================
           SELECTBOX
           ==================================================== */

        div[data-baseweb="select"] > div {{
            border-radius: 10px;

            border-color: {theme["border"]};

            background: {theme["surface"]};
        }}


        /* ====================================================
           SIDEBAR
           ==================================================== */

        section[data-testid="stSidebar"] {{
            background: {theme["surface"]};

            border-right: 1px solid {theme["border"]};
        }}


        /* ====================================================
           FOOTER
           ==================================================== */

        .registry-footer {{
            color: {theme["muted"]};

            font-size: 11px;

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


        /* ====================================================
           MOBILE
           ==================================================== */

        @media (max-width: 768px) {{

            .registry-title {{
                font-size: 21px;
            }}

            .registry-subtitle {{
                font-size: 11px;
            }}

            .registry-emblem {{
                width: 60px;
                height: 60px;

                font-size: 17px;
            }}

            .block-container {{
                padding-left: 1rem;
                padding-right: 1rem;
                padding-bottom: 6rem;
            }}

        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()


# ============================================================
# REGISTRY HEADER
# ============================================================

st.markdown(
    """
    <div class="registry-header">

        <div class="registry-emblem">
            SS
        </div>

        <div class="registry-brand">

            <div class="registry-title">
                South Sudan National Registry
            </div>

            <div class="registry-subtitle">
                National Population • Civil Registration •
                Identity • Elections
            </div>

            <div class="registry-system-status">
                <span class="status-dot"></span>
                System Online
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
# HELPER FUNCTIONS
# ============================================================

def get_module_key(
    module: Any,
) -> str | None:
    """
    Safely obtain a module key.
    """

    key = getattr(
        module,
        "key",
        None,
    )

    if key is None:
        return None

    return str(key)


def get_module_label(
    module: Any,
) -> str:
    """
    Safely obtain a module display label.
    """

    label = getattr(
        module,
        "label",
        None,
    )

    if label:

        return str(label)

    key = get_module_key(module)

    if key:

        return key.replace(
            "_",
            " ",
        ).title()

    return "Registry Module"


def get_module_description(
    module: Any,
) -> str:
    """
    Safely obtain a module description.
    """

    description = getattr(
        module,
        "description",
        "",
    )

    return str(
        description or ""
    )


def module_is_available(
    module: Any,
) -> bool:
    """
    Determine whether a registry module is operational.

    If the registry object does not expose an explicit
    availability attribute, assume it is operational.
    """

    available = getattr(
        module,
        "available",
        None,
    )

    if available is None:

        return True

    return bool(
        available
    )


def get_module_error(
    module: Any,
) -> str:
    """
    Return a human-readable module error.
    """

    error = getattr(
        module,
        "error",
        None,
    )

    if error:

        return str(error)

    return "Unknown module error."


def kpi_card(
    label: str,
    value: str | int,
    description: str,
) -> None:
    """
    Render a KPI card.

    All HTML is intentionally contained inside st.markdown().
    """

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


def module_card(
    title: str,
    description: str,
) -> None:
    """
    Render a Registry module card.
    """

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


def page_header(
    title: str,
    description: str,
) -> None:
    """
    Render a standard module page header.
    """

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
# OVERVIEW
# ============================================================

def render_overview() -> None:
    """
    Render the Registry Overview dashboard.
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
                Centralized management platform for national
                population registration, civil records,
                identity management, households, electoral
                registration and registry services.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        kpi_card(
            "Registered Population",
            0,
            "Population records",
        )


    with col2:

        kpi_card(
            "Civil Records",
            0,
            "Birth, death and civil events",
        )


    with col3:

        kpi_card(
            "Identity Records",
            0,
            "National identity records",
        )


    with col4:

        kpi_card(
            "Election Records",
            0,
            "Electoral records",
        )


    # --------------------------------------------------------
    # SYSTEM STATUS
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "System Status"
    )


    total_modules = len(
        all_modules
    )


    operational_modules = sum(
        1
        for module in all_modules
        if module_is_available(module)
    )


    unavailable_modules = max(
        total_modules - operational_modules,
        0,
    )


    status_col1, status_col2, status_col3 = st.columns(
        3
    )


    with status_col1:

        st.metric(
            "Registry Modules",
            total_modules,
        )


    with status_col2:

        st.metric(
            "Operational",
            operational_modules,
        )


    with status_col3:

        st.metric(
            "Attention Required",
            unavailable_modules,
        )


    # --------------------------------------------------------
    # SERVICES
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "Registry Services"
    )


    service_modules = [
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


    col1, col2, col3 = st.columns(3)


    for index, (
        title,
        description,
    ) in enumerate(service_modules):

        target_column = (
            col1
            if index % 3 == 0
            else col2
            if index % 3 == 1
            else col3
        )


        with target_column:

            module_card(
                title,
                description,
            )


    # --------------------------------------------------------
    # CONFIGURED MODULES
    # --------------------------------------------------------

    if all_modules:

        st.divider()

        st.subheader(
            "Configured Modules"
        )


        for module in all_modules:

            name = get_module_label(
                module
            )

            description = get_module_description(
                module
            )

            available = module_is_available(
                module
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

                with st.expander(
                    f"Technical details — {name}"
                ):

                    st.code(
                        get_module_error(module)
                    )


    # --------------------------------------------------------
    # ARCHITECTURE
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
# NAVIGATION
# ============================================================

navigation_items: list[
    tuple[str, str]
] = [
    (
        "overview",
        "Overview",
    )
]


for module in available_modules:

    key = get_module_key(
        module
    )

    if not key:

        continue

    label = get_module_label(
        module
    )

    if not any(
        existing_key == key
        for existing_key, _
        in navigation_items
    ):

        navigation_items.append(
            (
                key,
                label,
            )
        )


# ============================================================
# VALID NAVIGATION KEYS
# ============================================================

valid_navigation_keys = {
    key
    for key, _
    in navigation_items
}


if (
    st.session_state.active_module
    not in valid_navigation_keys
):

    st.session_state.active_module = (
        "overview"
    )


# ============================================================
# MODULE NAVIGATION
# ============================================================

st.divider()

navigation_labels = [
    label
    for _, label
    in navigation_items
]


current_label = next(
    (
        label
        for key, label
        in navigation_items
        if key
        == st.session_state.active_module
    ),
    "Overview",
)


selected_label = st.radio(
    "Registry Navigation",
    navigation_labels,
    index=(
        navigation_labels.index(
            current_label
        )
        if current_label
        in navigation_labels
        else 0
    ),
    horizontal=True,
    label_visibility="collapsed",
    key="registry_navigation",
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
# ACTIVE PAGE
# ============================================================

if (
    st.session_state.active_module
    == "overview"
):

    render_overview()

else:

    active_module = get_module(
        st.session_state.active_module
    )


    if active_module is None:

        st.error(
            "The requested Registry module "
            "could not be found."
        )


    else:

        module_name = get_module_label(
            active_module
        )

        module_description = get_module_description(
            active_module
        )


        page_header(
            module_name,
            module_description
            or (
                "Registry management module."
            ),
        )


        if not module_is_available(
            active_module
        ):

            st.error(
                "This Registry module is currently unavailable."
            )


            with st.expander(
                "Technical details"
            ):

                st.code(
                    get_module_error(
                        active_module
                    )
                )


        else:

            try:

                render_module(
                    st.session_state.active_module
                )

            except TypeError:

                # Compatibility fallback for registry
                # implementations whose render_module()
                # expects the module object instead of its key.

                try:

                    render_module(
                        active_module
                    )

                except Exception as exc:

                    logger.exception(
                        "Runtime error in module '%s'.",
                        st.session_state.active_module,
                    )

                    st.error(
                        "The selected Registry module "
                        "encountered a runtime error."
                    )

                    with st.expander(
                        "Technical details"
                    ):

                        st.exception(exc)

            except Exception as exc:

                logger.exception(
                    "Runtime error in module '%s'.",
                    st.session_state.active_module,
                )

                st.error(
                    "The selected Registry module "
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

            South Sudan National Registry
            <br>

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
            Identity • Elections

        </div>
        """,
        unsafe_allow_html=True,
)
