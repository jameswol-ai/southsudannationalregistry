"""
South Sudan National Registry
Streamlit Application

National Population • Civil Registration • Identity • Elections

Application entry point:
    streamlit run streamlit_app.py

The application shell is deliberately thin. CRUD and business rules
belong to the registered module UI/service layers.
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
APP_SUBTITLE = "National Population • Civil Registration • Identity • Elections"

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
EMBLEM_PATH = ASSETS_DIR / "south_sudan_emblem.png"

logger = logging.getLogger("south_sudan_national_registry")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


# ============================================================
# SESSION STATE
# ============================================================


def initialize_session_state() -> None:
    defaults: dict[str, Any] = {
        "active_module": "overview",
        "dark_mode": True,
        "database_connected": False,
        "database_error": None,
        "last_action": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_session_state()


# ============================================================
# EMBLEM
# ============================================================


@st.cache_data(show_spinner=False)
def load_emblem() -> Any | None:
    try:
        if not EMBLEM_PATH.exists():
            return None

        data = EMBLEM_PATH.read_bytes()
        if not data:
            return None

        from PIL import Image

        with Image.open(io.BytesIO(data)) as image:
            image.verify()

        image = Image.open(io.BytesIO(data))
        image.load()

        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA")

        return image
    except Exception as exc:
        logger.warning("Unable to load emblem: %s", exc)
        return None


# ============================================================
# DATABASE
# ============================================================

SessionLocal = None
init_db = None
database_import_error: str | None = None

try:
    from database.database import SessionLocal, init_db
except Exception as exc:
    database_import_error = f"{type(exc).__name__}: {exc}"
    logger.warning("Database import failed: %s", exc)


@st.cache_resource(show_spinner=False)
def initialize_database() -> tuple[bool, str | None]:
    if init_db is None:
        return False, database_import_error or "Database initialization is unavailable."

    try:
        init_db()
        return True, None
    except Exception as exc:
        logger.exception("Database initialization failed.")
        return False, f"{type(exc).__name__}: {exc}"


_db_ok, _db_error = initialize_database()
st.session_state.database_connected = _db_ok
st.session_state.database_error = _db_error


# ============================================================
# MODULE REGISTRY
# ============================================================

registry_available = False
registry_error: str | None = None

get_all_modules = None
get_available_modules = None
get_module = None
get_registry_status = None
module_exists = None

try:
    from modules.registry import (
        get_all_modules,
        get_available_modules,
        get_module,
        get_registry_status,
        module_exists,
    )

    registry_available = True
except Exception as exc:
    registry_error = f"{type(exc).__name__}: {exc}"
    logger.warning("Module registry unavailable: %s", exc)


# ============================================================
# NAVIGATION
# ============================================================

NAVIGATION_GROUPS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "Home",
        [("overview", "Overview")],
    ),
    (
        "Registry",
        [
            ("population", "Population Registry"),
            ("civil_registration", "Civil Registration"),
            ("identity", "Identity Management"),
            ("elections", "Elections"),
        ],
    ),
    (
        "Operations",
        [
            ("reports", "Reports & Analytics"),
            ("administration", "Administration"),
        ],
    ),
]


# ============================================================
# THEME
# ============================================================


def get_theme() -> dict[str, str]:
    if st.session_state.dark_mode:
        return {
            "background": "#0B1220",
            "surface": "#111827",
            "surface_alt": "#172033",
            "hover": "#1E293B",
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
        "hover": "#E2E8F0",
        "text": "#0F172A",
        "muted": "#64748B",
        "border": "#E2E8F0",
        "accent": "#15803D",
        "success": "#15803D",
        "warning": "#D97706",
        "danger": "#DC2626",
    }


def inject_css() -> None:
    theme = get_theme()

    st.markdown(
        f"""
<style>
.stApp {{
    background: {theme['background']};
    color: {theme['text']};
}}

.block-container {{
    max-width: 1500px;
    padding-top: 1rem;
    padding-bottom: 3rem;
}}

h1, h2, h3, h4, h5, h6 {{
    color: {theme['text']} !important;
}}

p, label, span {{
    color: {theme['text']};
}}

section[data-testid="stSidebar"] {{
    background: {theme['surface']};
    border-right: 1px solid {theme['border']};
}}

section[data-testid="stSidebar"] * {{
    color: {theme['text']};
}}

section[data-testid="stSidebar"] .stButton > button {{
    width: 100%;
    min-height: 38px;
    border-radius: 9px;
    text-align: left;
    font-weight: 600;
    background: transparent;
    border: 1px solid transparent;
}}

section[data-testid="stSidebar"] .stButton > button:hover {{
    background: {theme['hover']};
    border-color: {theme['border']};
}}

.registry-header, .page-card {{
    background: {theme['surface']};
    border: 1px solid {theme['border']};
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 18px;
}}

.registry-brand-title {{
    font-size: 28px;
    font-weight: 800;
    line-height: 1.2;
}}

.registry-brand-subtitle, .registry-version, .page-description {{
    color: {theme['muted']} !important;
}}

.registry-brand-subtitle {{
    margin-top: 5px;
    font-size: 13px;
}}

.registry-version {{
    margin-top: 3px;
    font-size: 12px;
}}

.registry-emblem {{
    width: 64px;
    height: 64px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: {theme['accent']};
    border: 3px solid #FBBF24;
    color: #FFFFFF !important;
    font-size: 18px;
    font-weight: 900;
}}

.page-title {{
    font-size: 28px;
    font-weight: 800;
}}

div[data-testid="stMetric"] {{
    background: {theme['surface']};
    border: 1px solid {theme['border']};
    border-radius: 14px;
    padding: 15px;
}}

div[data-testid="stMetricLabel"] {{
    color: {theme['muted']} !important;
}}

div[data-testid="stMetricValue"] {{
    color: {theme['text']} !important;
}}

div[data-testid="stDataFrame"] {{
    border: 1px solid {theme['border']};
    border-radius: 12px;
}}

.stButton > button {{
    border-radius: 9px;
    font-weight: 600;
    min-height: 38px;
}}

.registry-footer {{
    color: {theme['muted']} !important;
    font-size: 11px;
    text-align: center;
    margin-top: 30px;
}}

#MainMenu, footer {{
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
# SAFE REGISTRY HELPERS
# ============================================================


def all_modules() -> list[Any]:
    if not registry_available or get_all_modules is None:
        return []

    try:
        return list(get_all_modules() or [])
    except Exception:
        logger.exception("Unable to retrieve Registry modules.")
        return []


def available_modules() -> list[Any]:
    if not registry_available or get_available_modules is None:
        return []

    try:
        return list(get_available_modules() or [])
    except Exception:
        logger.exception("Unable to retrieve available modules.")
        return []


def registry_health() -> dict[str, int]:
    default = {"total": 0, "available": 0, "unavailable": 0}

    if not registry_available or get_registry_status is None:
        return default

    try:
        status = get_registry_status()
        if not isinstance(status, dict):
            return default

        return {
            "total": int(status.get("total", 0)),
            "available": int(status.get("available", 0)),
            "unavailable": int(status.get("unavailable", 0)),
        }
    except Exception:
        logger.exception("Unable to determine Registry health.")
        return default


# ============================================================
# NAVIGATION ACTIONS
# ============================================================


def navigate_to(route: str) -> None:
    st.session_state.active_module = route
    st.session_state.last_action = None
    st.rerun()


def navigation_button(route: str, label: str, group_index: int, item_index: int) -> None:
    widget_key = f"registry_nav_{group_index}_{item_index}_{route}"

    if st.button(
        label,
        key=widget_key,
        use_container_width=True,
    ):
        navigate_to(route)


# ============================================================
# SIDEBAR
# ============================================================


def render_sidebar() -> None:
    with st.sidebar:
        emblem = load_emblem()

        if emblem is not None:
            st.image(emblem, width=64)
        else:
            st.markdown('<div class="registry-emblem">SS</div>', unsafe_allow_html=True)

        st.markdown("### South Sudan National Registry")
        st.caption(APP_SUBTITLE)
        st.divider()

        if st.session_state.database_connected:
            st.success("System Online")
        else:
            st.warning("Database Attention Required")

        for group_index, (group_name, items) in enumerate(NAVIGATION_GROUPS):
            st.markdown(f"**{group_name}**")

            for item_index, (route, label) in enumerate(items):
                navigation_button(route, label, group_index, item_index)

        st.divider()

        theme_label = "Light Mode" if st.session_state.dark_mode else "Dark Mode"
        if st.button(
            theme_label,
            key="registry_theme_toggle",
            use_container_width=True,
        ):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

        if st.button(
            "Refresh Application",
            key="registry_refresh_application",
            use_container_width=True,
        ):
            st.cache_data.clear()
            st.rerun()

        st.caption(f"{APP_NAME} • v{APP_VERSION}")


# ============================================================
# HEADER
# ============================================================


def render_header() -> None:
    emblem = load_emblem()
    left, middle, right = st.columns([0.10, 0.70, 0.20], vertical_alignment="center")

    with left:
        if emblem is not None:
            st.image(emblem, width=58)
        else:
            st.markdown('<div class="registry-emblem">SS</div>', unsafe_allow_html=True)

    with middle:
        st.markdown(
            f'<div class="registry-brand-title">{APP_NAME}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="registry-brand-subtitle">{APP_SUBTITLE}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="registry-version">Version {APP_VERSION}</div>',
            unsafe_allow_html=True,
        )

    with right:
        if st.session_state.database_connected:
            st.success("Database Online")
        else:
            st.error("Database Attention Required")


# ============================================================
# PAGE HEADER
# ============================================================


def render_page_header(title: str, description: str = "") -> None:
    st.markdown(
        (
            '<div class="page-card">'
            f'<div class="page-title">{title}</div>'
            f'<div class="page-description">{description}</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


# ============================================================
# OVERVIEW
# ============================================================


def render_overview() -> None:
    render_page_header(
        "Overview",
        "National Registry operational dashboard and system status.",
    )

    health = registry_health()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Registry Modules", health["total"])
    with col2:
        st.metric("Available Modules", health["available"])
    with col3:
        st.metric("Unavailable Modules", health["unavailable"])
    with col4:
        st.metric(
            "Database",
            "Online" if st.session_state.database_connected else "Attention",
        )

    left, right = st.columns(2)

    with left:
        st.markdown('<div class="page-card">', unsafe_allow_html=True)
        st.subheader("System Status")

        if st.session_state.database_connected:
            st.success("Database connection is available.")
        else:
            st.warning("Database initialization requires attention.")
            if st.session_state.database_error:
                with st.expander("Database Technical Details"):
                    st.code(str(st.session_state.database_error))

        if registry_available:
            st.success("Module registry is available.")
        else:
            st.error("Module registry is unavailable.")
            if registry_error:
                with st.expander("Registry Technical Details"):
                    st.code(registry_error)

        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="page-card">', unsafe_allow_html=True)
        st.subheader("Registry Modules")

        modules = all_modules()
        if not modules:
            st.info("No Registry modules are currently loaded.")
        else:
            for module in modules:
                label = getattr(module, "label", getattr(module, "key", "Module"))
                if getattr(module, "available", False):
                    st.success(str(label))
                else:
                    st.warning(str(label))

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="page-card">', unsafe_allow_html=True)
    st.subheader("Operational Workflow")
    st.write(
        "Population registration → household management → civil registration "
        "→ identity documents → voter registration → verification → reports."
    )
    st.caption(
        "Use the Registry modules for record creation, editing, saving and controlled deletion."
    )
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# MODULE RENDERING
# ============================================================


def render_module_route(route: str) -> bool:
    if not registry_available or module_exists is None or get_module is None:
        return False

    try:
        if not module_exists(route):
            return False

        module = get_module(route)
        if module is None:
            st.error(f"Registry module '{route}' could not be loaded.")
            return True

        label = getattr(module, "label", route.replace("_", " ").title())
        description = getattr(module, "description", "Registry management module.")
        renderer = getattr(module, "render", None)

        if not getattr(module, "available", False):
            render_page_header(str(label), str(description))
            st.warning(f"{label} is currently unavailable.")
            error = getattr(module, "error", None)
            if error:
                with st.expander("Technical Details"):
                    st.code(str(error))
            return True

        if not callable(renderer):
            render_page_header(str(label), str(description))
            st.error(f"{label} does not expose a valid render function.")
            return True

        renderer()
        return True

    except Exception as exc:
        logger.exception("Registry module '%s' failed during rendering.", route)
        st.error(f"Unable to render the {route.replace('_', ' ')} module.")
        with st.expander("Technical Details"):
            st.exception(exc)
        return True


# ============================================================
# REGISTRY DIAGNOSTICS
# ============================================================


def render_registry_diagnostics() -> None:
    health = registry_health()
    st.subheader("Registry Health")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total", health["total"])
    with c2:
        st.metric("Available", health["available"])
    with c3:
        st.metric("Unavailable", health["unavailable"])

    for module in all_modules():
        if not getattr(module, "available", False):
            label = getattr(module, "label", getattr(module, "key", "Unknown Module"))
            st.warning(str(label))
            error = getattr(module, "error", None)
            if error:
                st.code(str(error))


# ============================================================
# ROUTER
# ============================================================


def route_application() -> None:
    active = str(st.session_state.get("active_module", "overview"))

    if active == "overview":
        render_overview()
        return

    if active == "diagnostics":
        render_page_header("Registry Diagnostics", "Module health and loading diagnostics.")
        render_registry_diagnostics()
        return

    if render_module_route(active):
        return

    render_page_header(
        "Page Not Found",
        "The requested Registry page does not exist.",
    )
    st.error(f"Unknown Registry route: {active}")


# ============================================================
# FOOTER
# ============================================================


def render_footer() -> None:
    st.markdown(
        (
            '<div class="registry-footer">'
            f"{APP_NAME} • Version {APP_VERSION}"
            "<br>National Registry Management Platform"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


# ============================================================
# MAIN
# ============================================================


def main() -> None:
    inject_css()
    render_sidebar()
    render_header()
    route_application()
    render_footer()


if __name__ == "__main__":
    main()
