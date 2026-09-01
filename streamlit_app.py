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
    initial_sidebar_state="collapsed",
)


# ============================================================
# APPLICATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

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


if st.session_state.active_page not in PAGES:
    st.session_state.active_page = "Overview"


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
        padding-top: 1.2rem;
        padding-bottom: 3rem;
    }


    /* ========================================================
       REGISTRY HEADER
       ======================================================== */

    .registry-header {
        width: 100%;

        display: flex;
        align-items: center;

        gap: 18px;

        padding: 18px 22px;

        margin-bottom: 18px;

        background: #ffffff;

        border: 1px solid #e2e8f0;

        border-radius: 14px;

        box-shadow:
            0 2px 8px rgba(15, 23, 42, 0.05);

        box-sizing: border-box;
    }


    .registry-emblem {
        width: 72px;
        height: 72px;

        min-width: 72px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 50%;

        background: #00843d;

        border: 4px solid #fbbf24;

        color: #ffffff;

        font-size: 21px;

        font-weight: 900;

        letter-spacing: 1px;

        box-shadow:
            0 4px 12px rgba(15, 23, 42, 0.12);
    }


    .registry-brand {
        display: flex;

        flex-direction: column;

        justify-content: center;

        min-width: 0;
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


    .registry-status {
        margin-left: auto;

        min-width: 125px;

        text-align: right;
    }


    .status-online {
        display: inline-flex;

        align-items: center;

        gap: 6px;

        color: #15803d;

        font-size: 12px;

        font-weight: 700;
    }


    .status-dot {
        width: 8px;

        height: 8px;

        border-radius: 50%;

        background: #22c55e;
    }


    .registry-version {
        margin-top: 5px;

        color: #94a3b8;

        font-size: 11px;
    }


    /* ========================================================
       NAVIGATION
       ======================================================== */

    div[data-testid="stRadio"] > div {
        gap: 6px;
    }


    div[data-testid="stRadio"] label {
        border-radius: 8px;

        padding: 7px 12px;

        font-size: 13px;
    }


    /* ========================================================
       PAGE
       ======================================================== */

    .page-title {
        margin-top: 12px;

        margin-bottom: 4px;

        font-size: 30px;

        font-weight: 800;

        color: #172033;
    }


    .page-description {
        margin-bottom: 22px;

        font-size: 14px;

        color: #64748b;
    }


    /* ========================================================
       KPI
       ======================================================== */

    .kpi-card {
        min-height: 125px;

        padding: 18px;

        background: #ffffff;

        border: 1px solid #e2e8f0;

        border-radius: 12px;

        box-shadow:
            0 2px 8px rgba(15, 23, 42, 0.04);

        box-sizing: border-box;
    }


    .kpi-label {
        margin-bottom: 8px;

        color: #64748b;

        font-size: 12px;
    }


    .kpi-value {
        color: #172033;

        font-size: 30px;

        font-weight: 800;

        line-height: 1;
    }


    .kpi-description {
        margin-top: 8px;

        color: #94a3b8;

        font-size: 11px;
    }


    /* ========================================================
       MODULE CARDS
       ======================================================== */

    .module-card {
        min-height: 145px;

        padding: 20px;

        margin-bottom: 15px;

        background: #ffffff;

        border: 1px solid #e2e8f0;

        border-radius: 12px;

        box-shadow:
            0 2px 8px rgba(15, 23, 42, 0.04);

        box-sizing: border-box;
    }


    .module-title {
        margin-bottom: 8px;

        color: #172033;

        font-size: 17px;

        font-weight: 700;
    }


    .module-description {
        color: #64748b;

        font-size: 13px;

        line-height: 1.55;
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .registry-footer {
        margin-top: 45px;

        padding-top: 18px;

        border-top: 1px solid #e2e8f0;

        color: #94a3b8;

        font-size: 11px;

        text-align: center;
    }


    /* ========================================================
       MOBILE
       ======================================================== */

    @media (max-width: 768px) {

        .registry-header {
            gap: 12px;

            padding: 14px;
        }

        .registry-emblem {
            width: 58px;
            height: 58px;

            min-width: 58px;

            font-size: 17px;
        }

        .registry-title {
            font-size: 19px;
        }

        .registry-subtitle {
            font-size: 10px;
        }

        .registry-status {
            display: none;
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

        </div>

        <div class="registry-status">

            <div class="status-online">
                <span class="status-dot"></span>
                System Online
            </div>

            <div class="registry-version">
                Version 1.0.0
            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# NAVIGATION
# ============================================================

selected_page = st.radio(
    "Registry Navigation",
    PAGES,
    index=PAGES.index(st.session_state.active_page),
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

    st.markdown("## Registry")

    st.caption(
        "South Sudan National Registry"
    )

    st.divider()

    st.markdown("### System")

    st.success(
        "Application Online"
    )

    st.markdown("### Active Module")

    st.write(
        st.session_state.active_page
    )

    st.divider()

    st.caption(
        "National Population • Civil Registration • "
        "Identity • Elections"
    )


# ============================================================
# HELPERS
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


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:

    page_header(
        "Overview",
        (
            "National Registry system overview, "
            "services and operational status."
        ),
    )


    # --------------------------------------------------------
    # KPIs
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


    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )


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
                "households, persons and demographic "
                "information."
            ),
        )

        module_card(
            "Identity Management",
            (
                "Manage national identity registration, "
                "identification records and identity "
                "services."
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
                "Manage electoral registration, voter "
                "records and election administration."
            ),
        )


    with col3:

        module_card(
            "Reports & Analytics",
            (
                "Generate operational reports, statistical "
                "summaries and Registry analytics."
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
            "System users, roles, permissions, "
            "security and configuration."
        ),
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
