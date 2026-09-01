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

import io
import logging
from pathlib import Path
from typing import Any

import streamlit as st


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

ASSETS_DIR = BASE_DIR / "assets"

EMBLEM_PATH = (
    ASSETS_DIR / "south_sudan_emblem.png"
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

# IMPORTANT:
# Do not pass EMBLEM_PATH directly to page_icon.
#
# Streamlit internally opens image files with Pillow.
# If the repository asset is corrupt, the entire application
# can fail before the UI renders.
#
# Use the emoji during startup. The real emblem is loaded
# safely later after validation.

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
# SAFE EMBLEM LOADING
# ============================================================

def load_valid_emblem() -> Any | None:
    """
    Safely load the South Sudan National Emblem.

    Returns:
        PIL.Image.Image when the PNG is valid.
        None when the file is missing or invalid.

    This prevents a corrupt PNG from crashing Streamlit.
    """

    if not EMBLEM_PATH.exists():

        logger.warning(
            "Registry emblem not found: %s",
            EMBLEM_PATH,
        )

        return None


    try:

        from PIL import Image

        # Read the complete file into memory first.
        image_bytes = EMBLEM_PATH.read_bytes()

        if not image_bytes:

            logger.warning(
                "Registry emblem is empty: %s",
                EMBLEM_PATH,
            )

            return None


        # Open the image.
        image = Image.open(
            io.BytesIO(image_bytes)
        )


        # Verify the image contents.
        image.verify()


        # Re-open after verify().
        image = Image.open(
            io.BytesIO(image_bytes)
        )


        # Convert to a Streamlit-safe mode.
        if image.mode not in (
            "RGB",
            "RGBA",
        ):

            image = image.convert(
                "RGBA"
            )


        return image


    except Exception:

        logger.exception(
            "Invalid Registry emblem: %s",
            EMBLEM_PATH,
        )

        return None


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
# MODULE HELPERS
# ============================================================

def load_registry_modules() -> list[Any]:
    """
    Return available registry modules.
    """

    try:

        modules = get_available_modules()

        if modules is None:
            return []

        if isinstance(
            modules,
            dict,
        ):

            return list(
                modules.values()
            )

        return list(modules)

    except Exception:

        logger.exception(
            "Unable to load registry modules."
        )

        return []


def load_all_registry_modules() -> list[Any]:
    """
    Return all configured modules where possible.
    """

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

        logger.debug(
            "MODULES registry unavailable.",
            exc_info=True,
        )

    return load_registry_modules()


# ============================================================
# SESSION STATE
# ============================================================

if "active_module" not in st.session_state:

    st.session_state.active_module = (
        "overview"
    )


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
        label {{
            color: {theme["text"]};
        }}


        /* ====================================================
           REGISTRY HEADER
           ==================================================== */

        .registry-header {{
            width: 100%;

            background: {theme["surface"]};

            border: 1px solid {theme["border"]};

            border-radius: 16px;

            padding: 18px;

            margin-bottom: 18px;

            display: flex;

            align-items: center;

            gap: 18px;

            box-shadow:
                0 3px 12px rgba(0,0,0,0.08);
        }}


        .registry-emblem {{
            width: 78px;
            height: 78px;

            min-width: 78px;

            display: flex;

            align-items: center;

            justify-content: center;

            border-radius: 50%;

            overflow: hidden;

            background: {theme["accent"]};

            border: 3px solid #FBBF24;
        }}


        .registry-emblem img {{
            width: 100%;
            height: 100%;

            object-fit: contain;
        }}


        .registry-emblem-fallback {{
            color: white;

            font-size: 20px;

            font-weight: 900;

            letter-spacing: 1px;
        }}


        .registry-brand {{
            flex: 1;

            display: flex;

            flex-direction: column;
        }}


        .registry-title {{
            color: {theme["text"]};

            font-size: 27px;

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

            min-width: 130px;
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

            margin-top: 5px;
        }}


        /* ====================================================
           KPI
           ==================================================== */

        .kpi-card {{
            background: {theme["surface"]};

            border: 1px solid {theme["border"]};

            border-radius: 14px;

            padding: 18px;

            min-height: 125px;

            margin-bottom: 14px;
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

            margin-top: 7px;
        }}


        .kpi-description {{
            color: {theme["muted"]};

            font-size: 11px;

            margin-top: 7px;
        }}


        /* ====================================================
           MODULE
           ==================================================== */

        .module-card {{
            background: {theme["surface"]};

            border: 1px solid {theme["border"]};

            border-radius: 14px;

            padding: 18px;

            min-height: 130px;

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

            margin-top: 6px;
        }}


        /* ====================================================
           FOOTER
           ==================================================== */

        .registry-footer {{
            color: {theme["muted"]};

            font-size: 11px;

            line-height: 1.5;

            text-align: center;
        }}


        /* ====================================================
           STREAMLIT
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

            .registry-header {{
                flex-direction: column;

                text-align: center;
            }}

            .registry-brand {{
                align-items: center;
            }}

            .registry-status {{
                text-align: center;
            }}

            .registry-title {{
                font-size: 21px;
            }}

        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()


# ============================================================
# EMBLEM
# ============================================================

emblem = load_valid_emblem()


# ============================================================
# HEADER
# ============================================================

if emblem is not None:

    # Streamlit receives an already validated PIL image.
    # The corrupt file can therefore never reach st.image().

    header_col1, header_col2, header_col3 = st.columns(
        [1, 5, 2]
    )


    with header_col1:

        st.image(
            emblem,
            width=78,
        )


    with header_col2:

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

                <div class="status-online">
                    <span class="status-dot"></span>
                    System Online
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    with header_col3:

        st.markdown(
            """
            <div class="registry-status">

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

    # Safe fallback if the PNG is missing or corrupt.

    st.markdown(
        """
        <div class="registry-header">

            <div class="registry-emblem">

                <div class="registry-emblem-fallback">
                    SS
                </div>

            </div>

            <div class="registry-brand">

                <div class="registry-title">
                    South Sudan National Registry
                </div>

                <div class="registry-subtitle">
                    National Population • Civil Registration •
                    Identity • Elections
                </div>

                <div class="status-online">
                    <span class="status-dot"></span>
                    System Online
                </div>

            </div>

            <div class="registry-status">

                <div class="registry-version">
                    Registry Platform
                </div>

                <div class="registry-version">
                    Version 1.0.0
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    st.warning(
        "Registry emblem asset could not be loaded. "
        "The application is running using the built-in fallback."
    )


# ============================================================
# TOP CONTROLS
# ============================================================

control_col1, control_col2, control_col3 = st.columns(
    [8, 1, 1]
)


with control_col2:

    if st.button(
        "Light"
        if st.session_state.dark_mode
        else "Dark",
        use_container_width=True,
        key="theme_toggle",
    ):

        st.session_state.dark_mode = (
            not st.session_state.dark_mode
        )

        st.rerun()


with control_col3:

    if st.button(
        "Refresh",
        use_container_width=True,
        key="refresh",
    ):

        st.rerun()


# ============================================================
# LOAD MODULES
# ============================================================

all_modules = load_all_registry_modules()

available_modules = load_registry_modules()


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:

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
    # MODULES
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


    columns = st.columns(3)


    for index, (
        title,
        description,
    ) in enumerate(services):

        with columns[index % 3]:

            module_card(
                title,
                description,
            )


    # --------------------------------------------------------
    # MODULE STATUS
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


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_module_key(
    module: Any,
) -> str | None:

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

    label = getattr(
        module,
        "label",
        None,
    )

    if label:

        return str(label)

    key = get_module_key(
        module
    )

    if key:

        return key.replace(
            "_",
            " ",
        ).title()

    return "Registry Module"


def get_module_description(
    module: Any,
) -> str:

    return str(
        getattr(
            module,
            "description",
            "",
        )
        or ""
    )


def module_is_available(
    module: Any,
) -> bool:

    value = getattr(
        module,
        "available",
        None,
    )

    if value is None:

        return True

    return bool(value)


def kpi_card(
    label: str,
    value: str | int,
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


def module_card(
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


def page_header(
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
# VALIDATE ACTIVE MODULE
# ============================================================

valid_keys = {
    key
    for key, _
    in navigation_items
}


if (
    st.session_state.active_module
    not in valid_keys
):

    st.session_state.active_module = (
        "overview"
    )


# ============================================================
# NAVIGATION BAR
# ============================================================

labels = [
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
    labels,
    index=(
        labels.index(
            current_label
        )
        if current_label in labels
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
# ACTIVE MODULE
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
            or "Registry management module.",
        )


        if not module_is_available(
            active_module
        ):

            st.error(
                "This Registry module is currently unavailable."
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
                    str(
                        error
                        or "Unknown module error."
                    )
                )

        else:

            try:

                render_module(
                    st.session_state.active_module
                )

            except TypeError:

                # Compatibility with registries that expect
                # the module object rather than the module key.

                try:

                    render_module(
                        active_module
                    )

                except Exception as exc:

                    logger.exception(
                        "Module rendering failed."
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
                    "Module rendering failed."
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

st.markdown(
    """
    <div class="registry-footer">

        South Sudan National Registry
        <br>

        National Population • Civil Registration •
        Identity • Elections

    </div>
    """,
    unsafe_allow_html=True,
        )
