"""
South Sudan National Registry
National Population • Civil Registration • Identity • Elections

Streamlit Application
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import streamlit as st
from PIL import Image, UnidentifiedImageError


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
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

ASSETS_DIR = BASE_DIR / "assets"

EMBLEM_PATH = ASSETS_DIR / "south_sudan_emblem.png"


# ============================================================
# APPLICATION CONSTANTS
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

if "theme" not in st.session_state:
    st.session_state.theme = "Light"


# ============================================================
# SAFE IMAGE LOADER
# ============================================================

def load_valid_image(path: Path) -> Optional[Image.Image]:
    """
    Safely load an image.

    Returns:
        PIL.Image.Image if valid.
        None if the file is missing, corrupt, or not an image.

    This prevents PIL.UnidentifiedImageError from crashing
    the entire Streamlit application.
    """

    if not path.exists():
        return None

    if not path.is_file():
        return None

    try:
        # First validate the file.
        with Image.open(path) as image:
            image.verify()

        # verify() invalidates the image object, so reopen it.
        with Image.open(path) as image:
            return image.convert("RGBA")

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
    ):
        return None


# ============================================================
# EMBLEM
# ============================================================

@st.cache_data(show_spinner=False)
def get_emblem() -> Optional[bytes]:
    """
    Load the Registry emblem as bytes.

    Returning bytes allows Streamlit to handle the image
    independently of the original file object.
    """

    image = load_valid_image(EMBLEM_PATH)

    if image is None:
        return None

    from io import BytesIO

    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG",
    )

    return buffer.getvalue()


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------------
       GLOBAL
    -------------------------------------------------------- */

    .stApp {
        background: #f6f8fa;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }


    /* --------------------------------------------------------
       REGISTRY HEADER
    -------------------------------------------------------- */

    .registry-header {
        display: flex;
        align-items: center;
        gap: 18px;

        padding: 18px 24px;

        background: white;

        border: 1px solid #e2e8f0;
        border-radius: 14px;

        box-shadow:
            0 2px 8px rgba(15, 23, 42, 0.05);

        margin-bottom: 18px;
    }


    .registry-emblem {
        width: 78px;
        height: 78px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 50%;

        background: #f8fafc;

        border: 1px solid #e2e8f0;

        overflow: hidden;

        flex-shrink: 0;
    }


    .registry-fallback {
        width: 68px;
        height: 68px;

        border-radius: 50%;

        display: flex;
        align-items: center;
        justify-content: center;

        background: #00843d;

        color: white;

        font-size: 20px;
        font-weight: 800;

        border: 4px solid #fbbf24;
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
        margin-left: auto;

        font-size: 11px;

        color: #64748b;

        white-space: nowrap;
    }


    /* --------------------------------------------------------
       PAGE TITLE
    -------------------------------------------------------- */

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


    /* --------------------------------------------------------
       KPI CARDS
    -------------------------------------------------------- */

    .kpi-card {
        background: white;

        border: 1px solid #e2e8f0;

        border-radius: 12px;

        padding: 18px;

        min-height: 125px;

        box-shadow:
            0 2px 8px rgba(15, 23, 42, 0.04);
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


    /* --------------------------------------------------------
       MODULE CARDS
    -------------------------------------------------------- */

    .module-card {
        background: white;

        border: 1px solid #e2e8f0;

        border-radius: 12px;

        padding: 20px;

        min-height: 150px;

        box-shadow:
            0 2px 8px rgba(15, 23, 42, 0.04);

        margin-bottom: 15px;
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


    /* --------------------------------------------------------
       STATUS
    -------------------------------------------------------- */

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


    /* --------------------------------------------------------
       FOOTER
    -------------------------------------------------------- */

    .registry-footer {
        margin-top: 40px;

        padding-top: 18px;

        border-top: 1px solid #e2e8f0;

        text-align: center;

        font-size: 11px;

        color: #94a3b8;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

header_left, header_brand, header_version = st.columns(
    [0.12, 0.73, 0.15],
    vertical_alignment="center",
)


with header_left:

    emblem_bytes = get_emblem()

    if emblem_bytes:

        st.image(
            emblem_bytes,
            width=78,
        )

    else:

        st.markdown(
            """
            <div class="registry-fallback">
                SS
            </div>
            """,
            unsafe_allow_html=True,
        )


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


with header_version:

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

pages = [
    "Overview",
    "Population",
    "Civil Registration",
    "Identity",
    "Elections",
    "Reports",
    "Administration",
]


selected_page = st.radio(
    "Navigation",
    pages,
    index=pages.index(st.session_state.active_page),
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

    st.markdown(
        "### Registry"

    )

    st.caption(
        "National information management platform"
    )

    st.divider()

    st.markdown(
        "#### System Status"
    )

    st.success(
        "Registry services operational"
    )

    st.info(
        "Database connection ready"
    )

    st.divider()

    st.markdown(
        "#### Current Module"
    )

    st.write(
        st.session_state.active_page
    )


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:

    st.markdown(
        '<div class="page-title">Overview</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="page-description">
            National Registry system overview and operational status.
        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.markdown(
            """
            <div class="kpi-card">

                <div class="kpi-label">
                    Registered Population
                </div>

                <div class="kpi-value">
                    0
                </div>

                <div class="kpi-description">
                    Population records
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    with col2:

        st.markdown(
            """
            <div class="kpi-card">

                <div class="kpi-label">
                    Civil Records
                </div>

                <div class="kpi-value">
                    0
                </div>

                <div class="kpi-description">
                    Birth, death and civil events
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    with col3:

        st.markdown(
            """
            <div class="kpi-card">

                <div class="kpi-label">
                    Identity Records
                </div>

                <div class="kpi-value">
                    0
                </div>

                <div class="kpi-description">
                    National identity records
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    with col4:

        st.markdown(
            """
            <div class="kpi-card">

                <div class="kpi-label">
                    Election Records
                </div>

                <div class="kpi-value">
                    0
                </div>

                <div class="kpi-description">
                    Electoral records
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    st.markdown("<br>", unsafe_allow_html=True)


    # --------------------------------------------------------
    # MODULES
    # --------------------------------------------------------

    st.subheader("Registry Services")


    col1, col2, col3 = st.columns(3)


    with col1:

        st.markdown(
            """
            <div class="module-card">

                <div class="module-title">
                    Population Registry
                </div>

                <div class="module-description">
                    Manage national population records,
                    households, persons and demographic information.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


        st.markdown(
            """
            <div class="module-card">

                <div class="module-title">
                    Identity Management
                </div>

                <div class="module-description">
                    Manage national identity registration,
                    identification records and identity services.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    with col2:

        st.markdown(
            """
            <div class="module-card">

                <div class="module-title">
                    Civil Registration
                </div>

                <div class="module-description">
                    Register births, deaths, marriages,
                    certificates and other civil events.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


        st.markdown(
            """
            <div class="module-card">

                <div class="module-title">
                    Elections
                </div>

                <div class="module-description">
                    Manage electoral registration,
                    voter records and election administration.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    with col3:

        st.markdown(
            """
            <div class="module-card">

                <div class="module-title">
                    Reports & Analytics
                </div>

                <div class="module-description">
                    Generate operational reports,
                    statistical summaries and registry analytics.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


        st.markdown(
            """
            <div class="module-card">

                <div class="module-title">
                    Administration
                </div>

                <div class="module-description">
                    Manage users, roles, permissions,
                    configuration and system administration.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# POPULATION
# ============================================================

def render_population() -> None:

    st.markdown(
        '<div class="page-title">Population Registry</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="page-description">
            National population registration and demographic records.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "Population Registry module is ready for database integration."
    )

    st.dataframe(
        [],
        use_container_width=True,
    )


# ============================================================
# CIVIL REGISTRATION
# ============================================================

def render_civil_registration() -> None:

    st.markdown(
        '<div class="page-title">Civil Registration</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="page-description">
            Birth, death, marriage and civil-status registration.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "Civil Registration module is ready for database integration."
    )


# ============================================================
# IDENTITY
# ============================================================

def render_identity() -> None:

    st.markdown(
        '<div class="page-title">Identity Management</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="page-description">
            National identity registration and identity management.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "Identity Management module is ready for database integration."
    )


# ============================================================
# ELECTIONS
# ============================================================

def render_elections() -> None:

    st.markdown(
        '<div class="page-title">Elections</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="page-description">
            Electoral registration and election administration.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "Elections module is ready for database integration."
    )


# ============================================================
# REPORTS
# ============================================================

def render_reports() -> None:

    st.markdown(
        '<div class="page-title">Reports & Analytics</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="page-description">
            Registry statistics, operational reporting and analytics.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "Reporting module is ready for database integration."
    )


# ============================================================
# ADMINISTRATION
# ============================================================

def render_administration() -> None:

    st.markdown(
        '<div class="page-title">Administration</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="page-description">
            System users, roles, permissions and configuration.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "Administration module is ready for database integration."
    )


# ============================================================
# ROUTER
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
