"""
South Sudan National Registry
National Population • Civil Registration • Identity • Elections

Streamlit Application
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="South Sudan National Registry",
    page_icon="🇸🇸",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# APPLICATION PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

EMBLEM_PATH = ASSETS_DIR / "south_sudan_emblem.png"


# ============================================================
# APPLICATION INFORMATION
# ============================================================

APP_TITLE = "South Sudan National Registry"

APP_SUBTITLE = (
    "National Population • Civil Registration • Identity • Elections"
)

APP_VERSION = "1.0.0"


# ============================================================
# SESSION STATE
# ============================================================

if "active_page" not in st.session_state:
    st.session_state.active_page = "Overview"


# ============================================================
# SAFE EMBLEM HANDLING
# ============================================================

def get_valid_emblem_bytes() -> bytes | None:
    """
    Safely read the Registry emblem.

    The application deliberately does not use Pillow here.

    A valid PNG begins with:
        89 50 4E 47 0D 0A 1A 0A

    If the file is missing, empty, corrupt, or not actually a
    PNG, None is returned and the application uses the SS
    fallback emblem.
    """

    try:
        if not EMBLEM_PATH.exists():
            return None

        if not EMBLEM_PATH.is_file():
            return None

        data = EMBLEM_PATH.read_bytes()

        if not data:
            return None

        png_signature = b"\x89PNG\r\n\x1a\n"

        if not data.startswith(png_signature):
            return None

        return data

    except (OSError, IOError):
        return None


def render_registry_emblem() -> None:
    """
    Render the Registry emblem safely.

    A bad image file can never terminate the application.
    """

    emblem = get_valid_emblem_bytes()

    if emblem is not None:
        try:
            st.image(
                emblem,
                width=78,
            )
            return
        except Exception:
            pass

    st.markdown(
        """
        <div class="registry-fallback">
            SS
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    .stApp {
        background: #f6f8fa;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }


    /* ========================================================
       REGISTRY HEADER
       ======================================================== */

    .registry-header {
        display: flex;
        align-items: center;
        gap: 18px;

        padding: 18px 24px;

        background: #ffffff;

        border: 1px solid #e2e8f0;
        border-radius: 14px;

        box-shadow:
            0 2px 8px rgba(15, 23, 42, 0.05);

        margin-bottom: 18px;
    }


    .registry-fallback {
        width: 68px;
        height: 68px;

        border-radius: 50%;

        display: flex;
        align-items: center;
        justify-content: center;

        background: #00843d;

        color: #ffffff;

        font-size: 20px;
        font-weight: 800;

        border: 4px solid #fbbf24;

        box-sizing: border-box;
    }


    .registry-brand {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }


    .registry-title {
        font-size: 26px;
        font-weight: 800;

        color: #172033;

        line-height: 1.2;

        margin-bottom: 5px;
    }


    .registry-subtitle {
        font-size: 13px;

        color: #64748b;

        line-height: 1.5;
    }


    .registry-version {
        font-size: 11px;

        color: #64748b;

        margin-top: 4px;

        white-space: nowrap;
    }


    /* ========================================================
       SYSTEM STATUS
       ======================================================== */

    .status-online {
        display: inline-flex;

        align-items: center;

        gap: 6px;

        font-size: 12px;

        font-weight: 600;

        color: #15803d;
    }


    .status-dot {
        width: 8px;
        height: 8px;

        border-radius: 50%;

        background: #22c55e;
    }


    /* ========================================================
       PAGE TITLES
       ======================================================== */

    .page-title {
        font-size: 30px;

        font-weight: 800;

        color: #172033;

        margin-top: 10px;

        margin-bottom: 4px;
    }


    .page-description {
        color: #64748b;

        font-size: 14px;

        margin-bottom: 20px;
    }


    /* ========================================================
       KPI CARDS
       ======================================================== */

    .kpi-card {
        background: #ffffff;

        border: 1px solid #e2e8f0;

        border-radius: 12px;

        padding: 18px;

        min-height: 125px;

        box-shadow:
            0 2px 8px rgba(15, 23, 42, 0.04);

        box-sizing: border-box;
    }


    .kpi-label {
        font-size: 12px;

        color: #64748b;

        margin-bottom: 8px;
    }


    .kpi-value {
        font-size: 30px;

        font-weight: 800;

        color: #172033;
    }


    .kpi-description {
        font-size: 11px;

        color: #94a3b8;

        margin-top: 5px;
    }


    /* ========================================================
       MODULE CARDS
       ======================================================== */

    .module-card {
        background: #ffffff;

        border: 1px solid #e2e8f0;

        border-radius: 12px;

        padding: 20px;

        min-height: 150px;

        box-shadow:
            0 2px 8px rgba(15, 23, 42, 0.04);

        margin-bottom: 15px;

        box-sizing: border-box;
    }


    .module-title {
        font-size: 17px;

        font-weight: 700;

        color: #172033;

        margin-bottom: 7px;
    }


    .module-description {
        font-size: 13px;

        line-height: 1.5;

        color: #64748b;
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .registry-footer {
        margin-top: 40px;

        padding-top: 18px;

        border-top: 1px solid #e2e8f0;

        text-align: center;

        font-size: 11px;

        color: #94a3b8;
    }


    /* ========================================================
       MOBILE
       ======================================================== */

    @media (max-width: 768px) {

        .registry-title {
            font-size: 20px;
        }

        .registry-subtitle {
            font-size: 11px;
        }

        .page-title {
            font-size: 24px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

header_left, header_brand, header_status = st.columns(
    [0.12, 0.68, 0.20],
    vertical_alignment="center",
)


with header_left:
    render_registry_emblem()


with header_brand:
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


with header_status:
    st.markdown(
        f"""
        <div style="text-align:right">

            <div class="status-online">
                <span class="status-dot"></span>
                System Online
            </div>

            <div class="registry-version">
                Version {APP_VERSION}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# NAVIGATION
# ============================================================

PAGES = [
    "Overview",
    "Population",
    "Civil Registration",
    "Identity",
    "Elections",
    "Reports",
    "Administration",
]


current_page = st.session_state.active_page

if current_page not in PAGES:
    current_page = "Overview"
    st.session_state.active_page = current_page


selected_page = st.radio(
    "Registry Navigation",
    PAGES,
    index=PAGES.index(current_page),
    horizontal=True,
    label_visibility="collapsed",
)


if selected_page != st.session_state.active_page:
    st.session_state.active_page = selected_page
    st.rerun()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("### Registry")

    st.caption(
        "National information management platform"
    )

    st.divider()

    st.markdown("#### System Status")

    st.success(
        "Registry services operational"
    )

    st.info(
        "Application running"
    )

    st.divider()

    st.markdown("#### Current Module")

    st.write(
        st.session_state.active_page
    )


# ============================================================
# PAGE HELPERS
# ============================================================

def page_header(
    title: str,
    description: str,
) -> None:

    st.markdown(
        f"""
        <div class="page-title">
            {title}
        </div>

        <div class="page-description">
            {description}
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

            <div class="module-title">
                {title}
            </div>

            <div class="module-description">
                {description}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(
    label: str,
    value: str,
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


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:

    page_header(
        "Overview",
        "National Registry system overview and operational status.",
    )


    # --------------------------------------------------------
    # KPI SECTION
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)


    with col1:
        kpi_card(
            "Registered Population",
            "0",
            "Population records",
        )


    with col2:
        kpi_card(
            "Civil Records",
            "0",
            "Birth, death and civil events",
        )


    with col3:
        kpi_card(
            "Identity Records",
            "0",
            "National identity records",
        )


    with col4:
        kpi_card(
            "Election Records",
            "0",
            "Electoral records",
        )


    st.markdown("<br>", unsafe_allow_html=True)


    # --------------------------------------------------------
    # SERVICES
    # --------------------------------------------------------

    st.subheader("Registry Services")


    col1, col2, col3 = st.columns(3)


    with col1:

        module_card(
            "Population Registry",
            (
                "Manage national population records, "
                "households, persons and demographic information."
            ),
        )

        module_card(
            "Identity Management",
            (
                "Manage national identity registration, "
                "identification records and identity services."
            ),
        )


    with col2:

        module_card(
            "Civil Registration",
            (
                "Register births, deaths, marriages, "
                "certificates and other civil events."
            ),
        )

        module_card(
            "Elections",
            (
                "Manage electoral registration, "
                "voter records and election administration."
            ),
        )


    with col3:

        module_card(
            "Reports & Analytics",
            (
                "Generate operational reports, "
                "statistical summaries and registry analytics."
            ),
        )

        module_card(
            "Administration",
            (
                "Manage users, roles, permissions, "
                "configuration and system administration."
            ),
        )


# ============================================================
# POPULATION
# ============================================================

def render_population() -> None:

    page_header(
        "Population Registry",
        (
            "National population registration and "
            "demographic records."
        ),
    )

    st.info(
        "Population Registry module is ready for database integration."
    )


# ============================================================
# CIVIL REGISTRATION
# ============================================================

def render_civil_registration() -> None:

    page_header(
        "Civil Registration",
        (
            "Birth, death, marriage and civil-status "
            "registration."
        ),
    )

    st.info(
        "Civil Registration module is ready for database integration."
    )


# ============================================================
# IDENTITY
# ============================================================

def render_identity() -> None:

    page_header(
        "Identity Management",
        (
            "National identity registration and "
            "identity management."
        ),
    )

    st.info(
        "Identity Management module is ready for database integration."
    )


# ============================================================
# ELECTIONS
# ============================================================

def render_elections() -> None:

    page_header(
        "Elections",
        (
            "Electoral registration and "
            "election administration."
        ),
    )

    st.info(
        "Elections module is ready for database integration."
    )


# ============================================================
# REPORTS
# ============================================================

def render_reports() -> None:

    page_header(
        "Reports & Analytics",
        (
            "Registry statistics, operational reporting "
            "and analytics."
        ),
    )

    st.info(
        "Reporting module is ready for database integration."
    )


# ============================================================
# ADMINISTRATION
# ============================================================

def render_administration() -> None:

    page_header(
        "Administration",
        (
            "System users, roles, permissions "
            "and configuration."
        ),
    )

    st.info(
        "Administration module is ready for database integration."
    )


# ============================================================
# PAGE ROUTER
# ============================================================

if st.session_state.active_page == "Overview":

    render_overview()

elif st.session_state.active_page == "Population":

    render_population()

elif st.session_state.active_page == "Civil Registration":

    render_civil_registration()

elif st.session_state.active_page == "Identity":

    render_identity()

elif st.session_state.active_page == "Elections":

    render_elections()

elif st.session_state.active_page == "Reports":

    render_reports()

elif st.session_state.active_page == "Administration":

    render_administration()

else:

    st.session_state.active_page = "Overview"
    st.rerun()


# ============================================================
# FOOTER
# ============================================================

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
