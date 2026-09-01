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
# APPLICATION PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

EMBLEM_PATH = (
    ASSETS_DIR / "south_sudan_emblem.png"
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

# Do NOT give Streamlit the potentially corrupt PNG here.
# A bad image would cause PIL.UnidentifiedImageError.
#
# The emblem is validated later before st.image() receives it.

st.set_page_config(
    page_title="South Sudan National Registry",
    page_icon="🇸🇸",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
)

logger = logging.getLogger(
    "south_sudan_national_registry"
)


# ============================================================
# SAFE EMBLEM LOADER
# ============================================================

def load_emblem():
    """
    Safely load the Registry emblem.

    Returns:
        PIL.Image.Image or None.

    A corrupted/missing image will never terminate the app.
    """

    if not EMBLEM_PATH.exists():

        logger.warning(
            "Registry emblem not found: %s",
            EMBLEM_PATH,
        )

        return None

    try:

        from PIL import Image

        image_bytes = EMBLEM_PATH.read_bytes()

        if not image_bytes:

            logger.warning(
                "Registry emblem is empty: %s",
                EMBLEM_PATH,
            )

            return None

        # Validate the image.
        with Image.open(
            io.BytesIO(image_bytes)
        ) as test_image:

            test_image.verify()

        # Re-open after verify().
        image = Image.open(
            io.BytesIO(image_bytes)
        )

        # Normalize the image mode.
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
            "Invalid Registry emblem %s: %s",
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

    logger.exception(
        "Unable to import database initializer: %s",
        exc,
    )


@st.cache_resource
def initialize_database() -> bool:
    """
    Initialize the registry database once.
    """

    if init_db is None:

        raise RuntimeError(
            "database.database.init_db could not be imported."
        )

    init_db()

    return True


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
        "Unable to import registry module system."
    )

    get_available_modules = None
    get_module = None
    render_module = None


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

database_connected = False
database_error: Exception | None = None

try:

    initialize_database()

    database_connected = True

except Exception as exc:

    database_error = exc

    logger.exception(
        "Database initialization failed."
    )


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

/* ============================================================
   GLOBAL
   ============================================================ */

.stApp {{
    background: {theme["background"]};
    color: {theme["text"]};
}}

.block-container {{
    max-width: 1500px;
    padding-top: 1rem;
    padding-bottom: 5rem;
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


/* ============================================================
   REGISTRY HEADER
   ============================================================ */

.registry-header {{
    background: {theme["surface"]};
    border: 1px solid {theme["border"]};
    border-radius: 18px;

    padding: 18px 20px;
    margin-bottom: 20px;

    box-shadow:
        0 6px 20px rgba(0, 0, 0, 0.08);
}}

.registry-brand {{
    display: flex;
    flex-direction: column;
    justify-content: center;
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

    margin-right: 6px;

    border-radius: 50%;

    background: {theme["success"]};
}}

.registry-version {{
    color: {theme["muted"]};
    font-size: 11px;
    margin-top: 5px;
}}


/* ============================================================
   EMBLEM
   ============================================================ */

.registry-emblem-fallback {{
    width: 72px;
    height: 72px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 50%;

    background: {theme["accent"]};

    border: 3px solid #FBBF24;

    color: #FFFFFF;

    font-size: 20px;
    font-weight: 900;
}}


/* ============================================================
   PAGE HEADER
   ============================================================ */

.overview-card {{
    background: {theme["surface"]};

    border: 1px solid {theme["border"]};

    border-radius: 16px;

    padding: 22px;

    margin-bottom: 18px;
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

    line-height: 1.3;

    margin-top: 5px;
}}

.registry-description {{
    color: {theme["muted"]};

    font-size: 14px;

    line-height: 1.6;

    margin-top: 7px;

    max-width: 1000px;
}}


/* ============================================================
   KPI CARDS
   ============================================================ */

.kpi-card {{
    background: {theme["surface"]};

    border: 1px solid {theme["border"]};

    border-radius: 15px;

    padding: 18px;

    min-height: 125px;

    margin-bottom: 15px;
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

    margin-top: 6px;
}}


/* ============================================================
   MODULE CARDS
   ============================================================ */

.module-card {{
    background: {theme["surface"]};

    border: 1px solid {theme["border"]};

    border-radius: 14px;

    padding: 18px;

    min-height: 130px;

    margin-bottom: 15px;
}}

.module-name {{
    color: {theme["text"]};

    font-size: 16px;

    font-weight: 750;
}}

.module-description {{
    color: {theme["muted"]};

    font-size: 13px;

    line-height: 1.55;

    margin-top: 6px;
}}


/* ============================================================
   FOOTER
   ============================================================ */

.registry-footer {{
    color: {theme["muted"]};

    text-align: center;

    font-size: 11px;

    line-height: 1.5;

    padding: 15px;
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


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 768px) {{

    .registry-title {{
        font-size: 21px;
    }}

    .registry-status {{
        text-align: left;
        margin-top: 10px;
    }}

}}

</style>
        """,
        unsafe_allow_html=True,
    )


inject_css()


# ============================================================
# UI HELPERS
# ============================================================

def render_kpi_card(
    label: str,
    value: int | str,
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


# ============================================================
# REGISTRY HEADER
# ============================================================

def render_registry_header() -> None:

    emblem = load_emblem()

    with st.container():

        st.markdown(
            '<div class="registry-header">',
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(
            [1, 6, 2],
            vertical_alignment="center",
        )

        with col1:

            if emblem is not None:

                st.image(
                    emblem,
                    width=72,
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
<div class="registry-brand">

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

            st.markdown(
                """
<div class="registry-status">

    <div class="status-online">
        <span class="status-dot"></span>
        System Online
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


render_registry_header()


# ============================================================
# TOP CONTROLS
# ============================================================

control1, control2, control3 = st.columns(
    [8, 1, 1]
)

with control2:

    theme_label = (
        "Light"
        if st.session_state.dark_mode
        else "Dark"
    )

    if st.button(
        theme_label,
        key="theme_toggle",
        use_container_width=True,
    ):

        st.session_state.dark_mode = (
            not st.session_state.dark_mode
        )

        st.rerun()


with control3:

    if st.button(
        "Refresh",
        key="refresh_application",
        use_container_width=True,
    ):

        st.rerun()


# ============================================================
# DATABASE STATUS
# ============================================================

if not database_connected:

    st.warning(
        "The Registry interface is running, but the "
        "database is not connected."
    )

    if database_error:

        with st.expander(
            "Database technical details"
        ):

            st.exception(
                database_error
            )


# ============================================================
# MODULE HELPERS
# ============================================================

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

    key = getattr(
        module,
        "key",
        None,
    )

    if key:

        return str(key).replace(
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


# ============================================================
# LOAD MODULES
# ============================================================

def load_registry_modules() -> list[Any]:

    if get_available_modules is None:

        return []

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
            "Unable to load available modules."
        )

        return []


def load_all_registry_modules() -> list[Any]:

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

    return load_registry_modules()


all_modules = load_all_registry_modules()

available_modules = load_registry_modules()


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
# OVERVIEW
# ============================================================

def render_overview() -> None:

    render_page_header(
        "National Registry Overview",
        (
            "Centralized management platform for national "
            "population registration, civil records, identity "
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

        render_kpi_card(
            "Registered Population",
            0,
            "Population records",
        )


    with col2:

        render_kpi_card(
            "Civil Records",
            0,
            "Birth, death and civil events",
        )


    with col3:

        render_kpi_card(
            "Identity Records",
            0,
            "National identity records",
        )


    with col4:

        render_kpi_card(
            "Election Records",
            0,
            "Electoral records",
        )


    # --------------------------------------------------------
    # SERVICES
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

        render_kpi_card(
            "Registered Population",
            0,
            "Population records",
        )


    with col2:

        render_kpi_card(
            "Civil Records",
            0,
            "Birth, death and civil events",
        )


    with col3:

        render_kpi_card(
            "Identity Records",
            0,
            "National identity records",
        )


    with col4:

        render_kpi_card(
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
        "population registry database is connected."
    )


# ============================================================
# ACTIVE PAGE
# ============================================================

if (
    st.session_state.active_module
    == "overview"
):

    render_overview()

elif (
    st.session_state.active_module
    == "citizens"
):

    render_citizens()

else:

    if get_module is None:

        st.error(
            "The registry module system could not be loaded."
        )

    else:

        try:

            active_module = get_module(
                st.session_state.active_module
            )

        except Exception as exc:

            logger.exception(
                "Unable to retrieve registry module."
            )

            st.error(
                "The requested Registry module could not "
                "be loaded."
            )

            with st.expander(
                "Technical details"
            ):

                st.exception(exc)

            active_module = None


        if active_module is not None:

            render_page_header(
                get_module_label(
                    active_module
                ),
                get_module_description(
                    active_module
                )
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

            elif render_module is None:

                st.error(
                    "Registry module renderer is unavailable."
                )

            else:

                try:

                    render_module(
                        st.session_state.active_module
                    )

                except TypeError:

                    try:

                        render_module(
                            active_module
                        )

                    except Exception as exc:

                        logger.exception(
                            "Registry module failed."
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
                        "Registry module failed."
                    )

                    st.error(
                        "The selected Registry module "
                        "encountered a runtime error."
                    )

                    with st.expander(
                        "Technical details"
                    ):

                        st.exception(exc)

        else:

            st.error(
                "The requested Registry module "
                "could not be found."
            )


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

    <br><br>

    Registry data should be treated as authoritative
    only after appropriate verification and
    administrative approval.

</div>
    """,
    unsafe_allow_html=True,
    )
