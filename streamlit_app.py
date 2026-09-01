"""
South Sudan National Registry
Streamlit Application

National Population • Civil Registration • Identity • Elections

Application entry point:

    streamlit run streamlit_app.py

Architecture:

    streamlit_app.py
          |
          v
    modules.registry
          |
          +---- Population
          +---- Civil Registration
          +---- Identity
          +---- Elections
          +---- Reports
          +---- Administration
          |
          v
    Module UI
          |
          v
    Service Layer
          |
          v
    SQLAlchemy
          |
          v
    PostgreSQL / SQLite
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
    page_icon="SS",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# APPLICATION CONSTANTS
# ============================================================

APP_NAME = "South Sudan National Registry"
APP_VERSION = "1.0.0 Alpha"

APP_SUBTITLE = (
    "National Population • Civil Registration • "
    "Identity • Elections"
)

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

def initialize_session_state() -> None:
    """
    Initialize all application session state.

    This function is intentionally called before rendering
    widgets so that every navigation value has a predictable
    default.
    """

    defaults: dict[str, Any] = {
        "active_module": "overview",
        "dark_mode": True,
        "database_connected": False,
        "database_error": None,
        "citizen_editor_id": None,
        "citizen_view_id": None,
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


initialize_session_state()


# ============================================================
# SAFE EMBLEM LOADING
# ============================================================

@st.cache_data(show_spinner=False)
def load_emblem() -> Any | None:
    """
    Safely load the South Sudan emblem.

    Missing or invalid image files never crash the app.
    """

    try:

        if not EMBLEM_PATH.exists():
            return None

        image_bytes = EMBLEM_PATH.read_bytes()

        if not image_bytes:
            return None

        from PIL import Image

        with Image.open(
            io.BytesIO(image_bytes)
        ) as image:

            image.verify()

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

SessionLocal = None
init_db = None
database_import_error: str | None = None

try:

    from database.database import (
        SessionLocal,
        init_db,
    )

except Exception as exc:

    database_import_error = (
        f"{type(exc).__name__}: {exc}"
    )

    logger.warning(
        "Database import failed: %s",
        exc,
    )


@st.cache_resource(show_spinner=False)
def initialize_database() -> tuple[
    bool,
    str | None,
]:
    """
    Initialize the application database.

    Returns:

        (True, None)

    or:

        (False, error_message)
    """

    if init_db is None:

        return (
            False,
            database_import_error
            or
            "Database initialization is unavailable.",
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
# MODELS
# ============================================================

Citizen = None
AuditLog = None

models_available = False
models_error: str | None = None

try:

    from models import (
        AuditLog,
        Citizen,
    )

    models_available = True

except Exception as exc:

    models_error = (
        f"{type(exc).__name__}: {exc}"
    )

    logger.warning(
        "Registry models unavailable: %s",
        exc,
    )


# ============================================================
# MODULE REGISTRY
# ============================================================

registry_available = False
registry_error: str | None = None

get_all_modules = None
get_available_modules = None
get_module = None
get_module_errors = None
get_registry_status = None
module_exists = None
render_module = None

try:

    from modules.registry import (
        get_all_modules,
        get_available_modules,
        get_module,
        get_module_errors,
        get_registry_status,
        module_exists,
        render_module,
    )

    registry_available = True

except Exception as exc:

    registry_error = (
        f"{type(exc).__name__}: {exc}"
    )

    logger.warning(
        "Module registry unavailable: %s",
        exc,
    )


# ============================================================
# REGISTRY HELPERS
# ============================================================

def load_all_modules() -> list[Any]:
    """
    Return all registered modules safely.
    """

    if not registry_available:
        return []

    if get_all_modules is None:
        return []

    try:

        result = get_all_modules()

        if result is None:
            return []

        return list(result)

    except Exception as exc:

        logger.exception(
            "Unable to retrieve Registry modules."
        )

        return []


def load_available_modules() -> list[Any]:
    """
    Return successfully loaded modules.
    """

    if not registry_available:
        return []

    if get_available_modules is None:
        return []

    try:

        result = get_available_modules()

        if result is None:
            return []

        return list(result)

    except Exception:

        logger.exception(
            "Unable to retrieve available modules."
        )

        return []


def registry_health() -> dict[str, int]:
    """
    Return Registry health information.
    """

    default = {
        "total": 0,
        "available": 0,
        "unavailable": 0,
    }

    if not registry_available:
        return default

    if get_registry_status is None:
        return default

    try:

        status = get_registry_status()

        if not isinstance(
            status,
            dict,
        ):
            return default

        return {
            "total": int(
                status.get(
                    "total",
                    0,
                )
            ),
            "available": int(
                status.get(
                    "available",
                    0,
                )
            ),
            "unavailable": int(
                status.get(
                    "unavailable",
                    0,
                )
            ),
        }

    except Exception:

        logger.exception(
            "Unable to determine Registry health."
        )

        return default


# ============================================================
# STATIC FEATURES
# ============================================================

FEATURES: dict[
    str,
    tuple[str, str],
] = {

    "households": (
        "Households",
        (
            "Manage household records, household "
            "members and relationships."
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
            "Verify population, civil registration "
            "and identity records."
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

    "settings": (
        "System Settings",
        (
            "Configure Registry platform settings "
            "and system preferences."
        ),
    ),
}


# ============================================================
# NAVIGATION DEFINITIONS
# ============================================================

NAVIGATION_GROUPS: list[
    tuple[str, list[tuple[str, str]]]
] = [

    (
        "Home",
        [
            (
                "overview",
                "Overview",
            ),
        ],
    ),

    (
        "Registry",
        [
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
        ],
    ),

    (
        "Operations",
        [
            (
                "households",
                "Households",
            ),
            (
                "documents",
                "Documents",
            ),
            (
                "verification",
                "Verification",
            ),
            (
                "statistics",
                "Statistics",
            ),
            (
                "reports",
                "Reports & Analytics",
            ),
        ],
    ),

    (
        "Administration",
        [
            (
                "administration",
                "Administration",
            ),
            (
                "audit",
                "Audit & Activity",
            ),
            (
                "settings",
                "System Settings",
            ),
        ],
    ),
]


# ============================================================
# THEME
# ============================================================

def get_theme() -> dict[str, str]:
    """
    Return the active application colour palette.
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
    """
    Inject application-wide CSS.
    """

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

/* ========================================================
   SIDEBAR
   ======================================================== */

section[data-testid="stSidebar"] {{
    background: {theme["surface"]};
    border-right: 1px solid {theme["border"]};
}}

section[data-testid="stSidebar"] * {{
    color: {theme["text"]};
}}

section[data-testid="stSidebar"]
.stButton > button {{
    width: 100%;
    min-height: 38px;
    border-radius: 9px;
    text-align: left;
    font-weight: 600;
    background: transparent;
    border: 1px solid transparent;
}}

section[data-testid="stSidebar"]
.stButton > button:hover {{
    background: {theme["surface_hover"]};
    border-color: {theme["border"]};
}}

/* ========================================================
   HEADER
   ======================================================== */

.registry-header {{
    background: {theme["surface"]};
    border: 1px solid {theme["border"]};
    border-radius: 18px;
    padding: 20px;
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

.registry-version {{
    margin-top: 3px;
    font-size: 12px;
    color: {theme["muted"]} !important;
}}

/* ========================================================
   EMBLEM
   ======================================================== */

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

/* ========================================================
   PAGE CARDS
   ======================================================== */

.page-card {{
    background: {theme["surface"]};
    border: 1px solid {theme["border"]};
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 18px;
}}

.page-title {{
    font-size: 28px;
    font-weight: 800;
    color: {theme["text"]};
}}

.page-description {{
    color: {theme["muted"]} !important;
    margin-top: 5px;
}}

/* ========================================================
   METRICS
   ======================================================== */

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

/* ========================================================
   DATAFRAMES
   ======================================================== */

div[data-testid="stDataFrame"] {{
    border: 1px solid {theme["border"]};
    border-radius: 12px;
}}

/* ========================================================
   BUTTONS
   ======================================================== */

.stButton > button {{
    border-radius: 9px;
    font-weight: 600;
    min-height: 38px;
}}

/* ========================================================
   FOOTER
   ======================================================== */

.registry-footer {{
    color: {theme["muted"]} !important;
    font-size: 11px;
    text-align: center;
    margin-top: 30px;
}}

/* ========================================================
   STREAMLIT CHROME
   ======================================================== */

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
# NAVIGATION
# ============================================================

def navigate_to(key: str) -> None:
    """
    Navigate to an application route.
    """

    st.session_state.active_module = str(key)

    st.session_state.citizen_editor_id = None
    st.session_state.citizen_view_id = None

    st.rerun()


def sidebar_button(
    key: str,
    label: str,
    widget_id: str | None = None,
) -> None:
    """
    Render a navigation button using a guaranteed unique
    Streamlit widget key.

    IMPORTANT:
    The route key and widget key are intentionally separate.

    Example:

        route:
            administration

        widget:
            sidebar_administration_001

    This prevents StreamlitDuplicateElementKey when the same
    route is rendered by different parts of the navigation.
    """

    if widget_id is None:

        widget_id = (
            f"sidebar_{key}"
        )

    safe_widget_key = (
        f"registry_navigation_{widget_id}"
    )

    if st.button(
        label,
        key=safe_widget_key,
        use_container_width=True,
    ):

        navigate_to(key)


def render_sidebar() -> None:
    """
    Render the complete application sidebar.

    Every button receives a unique widget key.
    """

    with st.sidebar:

        # ----------------------------------------------------
        # BRANDING
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

        st.markdown(
            "### South Sudan National Registry"
        )

        st.caption(
            APP_SUBTITLE
        )

        st.divider()

        # ----------------------------------------------------
        # DATABASE STATUS
        # ----------------------------------------------------

        if st.session_state.database_connected:

            st.success(
                "System Online"
            )

        else:

            st.warning(
                "Database Attention Required"
            )

        # ----------------------------------------------------
        # NAVIGATION
        # ----------------------------------------------------

        for group_index, (
            group_name,
            items,
        ) in enumerate(
            NAVIGATION_GROUPS
        ):

            st.markdown(
                f"**{group_name}**"
            )

            for item_index, (
                key,
                label,
            ) in enumerate(items):

                sidebar_button(
                    key=key,
                    label=label,
                    widget_id=(
                        f"{group_index}_"
                        f"{item_index}_"
                        f"{key}"
                    ),
                )

        st.divider()

        # ----------------------------------------------------
        # THEME
        # ----------------------------------------------------

        theme_label = (
            "Light Mode"
            if st.session_state.dark_mode
            else "Dark Mode"
        )

        theme_key = (
            "registry_theme_toggle"
        )

        if st.button(
            theme_label,
            key=theme_key,
            use_container_width=True,
        ):

            st.session_state.dark_mode = (
                not st.session_state.dark_mode
            )

            st.rerun()

        # ----------------------------------------------------
        # VERSION
        # ----------------------------------------------------

        st.caption(
            f"{APP_NAME} • v{APP_VERSION}"
        )


# ============================================================
# HEADER
# ============================================================

def render_header() -> None:
    """
    Render application header.
    """

    emblem = load_emblem()

    left, middle, right = st.columns(
        [0.12, 0.68, 0.20],
        vertical_alignment="center",
    )

    with left:

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

    with middle:

        st.markdown(
            (
                '<div class="registry-brand-title">'
                f"{APP_NAME}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            (
                '<div class="registry-brand-subtitle">'
                f"{APP_SUBTITLE}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            (
                '<div class="registry-version">'
                f"Version {APP_VERSION}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

    with right:

        if database_connected:

            st.success(
                "Database Online"
            )

        else:

            st.error(
                "Database Attention Required"
            )


# ============================================================
# PAGE HEADER
# ============================================================

def render_page_header(
    title: str,
    description: str = "",
) -> None:
    """
    Render a standard application page header.
    """

    st.markdown(
        (
            '<div class="page-card">'
            f'<div class="page-title">{title}</div>'
            f'<div class="page-description">'
            f"{description}"
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:
    """
    Render the Registry Overview dashboard.
    """

    render_page_header(
        "Overview",
        (
            "National Registry operational dashboard "
            "and system status."
        ),
    )

    health = registry_health()

    # --------------------------------------------------------
    # KPI ROW
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Registry Modules",
            health["total"],
        )

    with col2:

        st.metric(
            "Available Modules",
            health["available"],
        )

    with col3:

        st.metric(
            "Unavailable Modules",
            health["unavailable"],
        )

    with col4:

        st.metric(
            "Database",
            (
                "Online"
                if database_connected
                else "Attention"
            ),
        )

    st.write("")

    # --------------------------------------------------------
    # SYSTEM STATUS
    # --------------------------------------------------------

    left, right = st.columns(2)

    with left:

        st.markdown(
            '<div class="page-card">',
            unsafe_allow_html=True,
        )

        st.subheader(
            "System Status"
        )

        if database_connected:

            st.success(
                "Database connection is available."
            )

        else:

            st.warning(
                "Database initialization requires attention."
            )

            if database_error:

                with st.expander(
                    "Database Technical Details"
                ):

                    st.code(
                        str(database_error)
                    )

        if registry_available:

            st.success(
                "Module registry is available."
            )

        else:

            st.error(
                "Module registry is unavailable."
            )

            if registry_error:

                with st.expander(
                    "Registry Technical Details"
                ):

                    st.code(
                        str(registry_error)
                    )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    with right:

        st.markdown(
            '<div class="page-card">',
            unsafe_allow_html=True,
        )

        st.subheader(
            "Registry Modules"
        )

        modules = load_all_modules()

        if not modules:

            st.info(
                "No Registry modules are currently loaded."
            )

        else:

            for module in modules:

                label = getattr(
                    module,
                    "label",
                    getattr(
                        module,
                        "key",
                        "Module",
                    ),
                )

                if getattr(
                    module,
                    "available",
                    False,
                ):

                    st.success(
                        str(label)
                    )

                else:

                    st.warning(
                        str(label)
                    )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


# ============================================================
# CITIZENS
# ============================================================

def render_citizens() -> None:
    """
    Render the Citizens page.

    This implementation deliberately avoids assuming a fixed
    Citizen model schema beyond SQLAlchemy's mapped attributes.
    """

    render_page_header(
        "Citizens",
        (
            "National population and citizen registry "
            "records."
        ),
    )

    if Citizen is None:

        st.warning(
            "Citizen model is unavailable."
        )

        if models_error:

            with st.expander(
                "Technical Details"
            ):

                st.code(
                    models_error
                )

        return

    if SessionLocal is None:

        st.warning(
            "Database session is unavailable."
        )

        return

    # --------------------------------------------------------
    # DATABASE READ
    # --------------------------------------------------------

    session = None

    try:

        session = SessionLocal()

        records = (
            session.query(Citizen)
            .limit(100)
            .all()
        )

        if not records:

            st.info(
                "No citizen records are currently available."
            )

            return

        rows: list[dict[str, Any]] = []

        for record in records:

            row: dict[str, Any] = {}

            mapper = getattr(
                Citizen,
                "__mapper__",
                None,
            )

            if mapper is not None:

                for column in mapper.columns:

                    value = getattr(
                        record,
                        column.key,
                        None,
                    )

                    if value is None:
                        row[column.key] = ""
                    else:
                        row[column.key] = str(
                            value
                        )

            else:

                row["id"] = str(
                    getattr(
                        record,
                        "id",
                        "",
                    )
                )

            rows.append(row)

        if rows:

            st.dataframe(
                rows,
                use_container_width=True,
                hide_index=True,
            )

    except Exception as exc:

        logger.exception(
            "Unable to load citizen records."
        )

        st.error(
            "Unable to load citizen records."
        )

        with st.expander(
            "Technical Details"
        ):

            st.exception(exc)

    finally:

        if session is not None:

            try:
                session.close()
            except Exception:
                pass


# ============================================================
# STATIC FEATURE PAGE
# ============================================================

def render_static_feature(
    key: str,
) -> None:
    """
    Render a safe placeholder page for a static feature.
    """

    title, description = FEATURES.get(
        key,
        (
            key.replace(
                "_",
                " ",
            ).title(),
            "Registry feature.",
        ),
    )

    render_page_header(
        title,
        description,
    )

    st.info(
        (
            f"The {title} interface is registered "
            "and ready for its service layer."
        )
    )

    st.markdown(
        """
### Module Status

This section is part of the South Sudan National Registry
application architecture.

The production implementation should connect this interface
to its corresponding service layer and SQLAlchemy models.
"""
    )


# ============================================================
# REGISTERED MODULE PAGE
# ============================================================

def render_registered_module(
    key: str,
) -> bool:
    """
    Render a module registered by modules.registry.

    Returns True when the requested route was handled.
    """

    if not registry_available:
        return False

    if module_exists is None:
        return False

    try:

        if not module_exists(key):
            return False

    except Exception as exc:

        logger.exception(
            "Registry lookup failed for '%s'.",
            key,
        )

        st.error(
            "Unable to inspect the Registry module."
        )

        with st.expander(
            "Technical Details"
        ):

            st.exception(exc)

        return True

    module = None

    if get_module is not None:

        try:

            module = get_module(key)

        except Exception as exc:

            logger.exception(
                "Unable to retrieve module '%s'.",
                key,
            )

            st.error(
                "Unable to retrieve the Registry module."
            )

            with st.expander(
                "Technical Details"
            ):

                st.exception(exc)

            return True

    if module is None:

        st.error(
            f"Registry module '{key}' could not be loaded."
        )

        return True

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

    if not getattr(
        module,
        "available",
        False,
    ):

        st.warning(
            f"{label} is currently unavailable."
        )

        error = getattr(
            module,
            "error",
            None,
        )

        if error:

            with st.expander(
                "Technical Details"
            ):

                st.code(
                    str(error)
                )

        return True

    renderer = getattr(
        module,
        "render",
        None,
    )

    if renderer is None:

        st.warning(
            f"{label} does not currently expose "
            "a render function."
        )

        return True

    if not callable(renderer):

        st.error(
            f"{label} has an invalid render function."
        )

        return True

    try:

        renderer()

    except Exception as exc:

        logger.exception(
            "Registry module '%s' failed during rendering.",
            key,
        )

        st.error(
            f"Unable to render {label}."
        )

        with st.expander(
            "Technical Details"
        ):

            st.exception(exc)

    return True


# ============================================================
# REGISTRY DIAGNOSTICS
# ============================================================

def render_registry_diagnostics() -> None:
    """
    Render Registry diagnostics when requested.
    """

    health = registry_health()

    st.subheader(
        "Registry Health"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total",
            health["total"],
        )

    with col2:
        st.metric(
            "Available",
            health["available"],
        )

    with col3:
        st.metric(
            "Unavailable",
            health["unavailable"],
        )

    unavailable = []

    for module in load_all_modules():

        if not getattr(
            module,
            "available",
            False,
        ):

            unavailable.append(
                module
            )

    if unavailable:

        st.subheader(
            "Unavailable Modules"
        )

        for module in unavailable:

            label = getattr(
                module,
                "label",
                getattr(
                    module,
                    "key",
                    "Unknown Module",
                ),
            )

            error = getattr(
                module,
                "error",
                None,
            )

            st.warning(
                str(label)
            )

            if error:

                with st.expander(
                    f"{label} Technical Details"
                ):

                    st.code(
                        str(error)
                    )


# ============================================================
# UNKNOWN ROUTE
# ============================================================

def render_unknown_route(
    key: str,
) -> None:
    """
    Render an unknown-route error.
    """

    render_page_header(
        "Page Not Found",
        "The requested Registry page does not exist.",
    )

    st.error(
        f"Unknown Registry route: {key}"
    )

    if registry_available:

        st.info(
            "Use the navigation menu to select "
            "a registered Registry module."
        )


# ============================================================
# FOOTER
# ============================================================

def render_footer() -> None:
    """
    Render application footer.
    """

    st.markdown(
        (
            '<div class="registry-footer">'
            f"{APP_NAME} • Version {APP_VERSION}"
            "<br>"
            "National Registry Management Platform"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


# ============================================================
# APPLICATION ROUTER
# ============================================================

def route_application() -> None:
    """
    Route the active application page.
    """

    active = str(
        st.session_state.get(
            "active_module",
            "overview",
        )
    )

    # --------------------------------------------------------
    # HOME
    # --------------------------------------------------------

    if active == "overview":

        render_overview()

        return

    # --------------------------------------------------------
    # CITIZENS
    # --------------------------------------------------------

    if active == "citizens":

        render_citizens()

        return

    # --------------------------------------------------------
    # REGISTERED MODULES
    # --------------------------------------------------------

    if registry_available:

        try:

            if (
                module_exists is not None
                and module_exists(active)
            ):

                render_registered_module(
                    active
                )

                return

        except Exception as exc:

            logger.exception(
                "Registry routing failed for '%s'.",
                active,
            )

            st.error(
                "Registry routing failed."
            )

            with st.expander(
                "Technical Details"
            ):

                st.exception(exc)

            return

    # --------------------------------------------------------
    # STATIC FEATURES
    # --------------------------------------------------------

    if active in FEATURES:

        render_static_feature(
            active
        )

        return

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    render_unknown_route(
        active
    )


# ============================================================
# MAIN APPLICATION
# ============================================================

def main() -> None:
    """
    Main Streamlit application entry point.
    """

    inject_css()

    render_sidebar()

    render_header()

    route_application()

    render_footer()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
