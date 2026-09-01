"""
South Sudan National Registry
AI Studio — Streamlit Application

National Identity, Civil Registration & Population Registry Platform

Company / Institution:
Republic of South Sudan

Application:
South Sudan National Registry

Version:
1.0.0 Alpha
"""

from __future__ import annotations

import datetime as dt
from typing import Optional

import pandas as pd
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
# APPLICATION CONSTANTS
# ============================================================

APP_NAME = "South Sudan National Registry"
APP_SHORT_NAME = "SSNR"
APP_VERSION = "1.0.0 Alpha"

PRIMARY_NAV = [
    "Overview",
    "Citizens",
    "Households",
    "Civil Registration",
    "Identity",
    "Locations",
    "Documents",
    "Verification",
    "Reports",
    "AI Studio",
    "Administration",
]


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "active_tab": "Overview",
    "theme": "light",
    "search_query": "",
    "selected_citizen": None,
    "selected_household": None,
    "authenticated": True,
}


for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------------
       GLOBAL
    -------------------------------------------------------- */

    .stApp {
        background: #f8fafc;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 5rem;
        max-width: 1500px;
    }

    /* --------------------------------------------------------
       TOP BRAND
       -------------------------------------------------------- */

    .ssnr-brand {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 8px 0 18px 0;
    }

    .ssnr-logo {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: linear-gradient(
            135deg,
            #0f5132,
            #198754
        );
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 25px;
        font-weight: 800;
        box-shadow: 0 8px 20px rgba(0,0,0,0.10);
    }

    .ssnr-title {
        font-size: 22px;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.1;
    }

    .ssnr-subtitle {
        color: #64748b;
        font-size: 12px;
        margin-top: 4px;
    }

    /* --------------------------------------------------------
       NAVIGATION
       -------------------------------------------------------- */

    .nav-container {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 6px;
        margin-bottom: 22px;
        box-shadow: 0 3px 12px rgba(15,23,42,0.04);
    }

    /* --------------------------------------------------------
       PAGE HEADERS
       -------------------------------------------------------- */

    .page-title {
        font-size: 30px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 4px;
    }

    .page-description {
        color: #64748b;
        margin-bottom: 22px;
    }

    /* --------------------------------------------------------
       KPI CARDS
       -------------------------------------------------------- */

    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px;
        min-height: 135px;
        box-shadow: 0 3px 12px rgba(15,23,42,0.04);
    }

    .metric-label {
        color: #64748b;
        font-size: 13px;
        font-weight: 600;
    }

    .metric-value {
        color: #0f172a;
        font-size: 30px;
        font-weight: 800;
        margin-top: 8px;
    }

    .metric-change {
        color: #198754;
        font-size: 12px;
        margin-top: 6px;
    }

    /* --------------------------------------------------------
       SECTION CARDS
       -------------------------------------------------------- */

    .section-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px;
        margin-top: 18px;
        margin-bottom: 18px;
    }

    .section-title {
        font-size: 18px;
        font-weight: 750;
        color: #0f172a;
        margin-bottom: 5px;
    }

    .section-description {
        font-size: 13px;
        color: #64748b;
        margin-bottom: 15px;
    }

    /* --------------------------------------------------------
       AI STUDIO
       -------------------------------------------------------- */

    .ai-panel {
        background: linear-gradient(
            135deg,
            #0f172a,
            #1e293b
        );
        border-radius: 18px;
        padding: 25px;
        color: white;
        margin-bottom: 20px;
    }

    .ai-title {
        font-size: 23px;
        font-weight: 800;
    }

    .ai-description {
        color: #cbd5e1;
        margin-top: 5px;
    }

    /* --------------------------------------------------------
       STATUS
       -------------------------------------------------------- */

    .status-online {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        background: #dcfce7;
        color: #166534;
        font-size: 12px;
        font-weight: 700;
    }

    .status-warning {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        background: #fef3c7;
        color: #92400e;
        font-size: 12px;
        font-weight: 700;
    }

    /* --------------------------------------------------------
       FOOTER
       -------------------------------------------------------- */

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 11px;
        padding: 35px 0 10px 0;
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
    <div class="ssnr-brand">
        <div class="ssnr-logo">SS</div>
        <div>
            <div class="ssnr-title">
                South Sudan National Registry
            </div>
            <div class="ssnr-subtitle">
                National Identity • Civil Registration • Population Registry
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# NAVIGATION
# ============================================================

st.markdown('<div class="nav-container">', unsafe_allow_html=True)

nav_columns = st.columns(len(PRIMARY_NAV))

for index, item in enumerate(PRIMARY_NAV):

    with nav_columns[index]:

        if st.button(
            item,
            key=f"nav_{item}",
            use_container_width=True,
        ):
            st.session_state.active_tab = item
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)


active_tab = st.session_state.active_tab


# ============================================================
# SAMPLE DATA
# ============================================================

def sample_citizens() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "National ID": "SS-000001",
                "First Name": "John",
                "Last Name": "Deng",
                "Gender": "Male",
                "County": "Juba",
                "State": "Central Equatoria",
                "Status": "Verified",
            },
            {
                "National ID": "SS-000002",
                "First Name": "Mary",
                "Last Name": "Nyankol",
                "Gender": "Female",
                "County": "Yei",
                "State": "Central Equatoria",
                "Status": "Verified",
            },
            {
                "National ID": "SS-000003",
                "First Name": "Peter",
                "Last Name": "Bol",
                "Gender": "Male",
                "County": "Bor",
                "State": "Jonglei",
                "Status": "Pending",
            },
        ]
    )


def sample_households() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Household ID": "HH-000001",
                "Head": "John Deng",
                "Members": 5,
                "State": "Central Equatoria",
                "County": "Juba",
            },
            {
                "Household ID": "HH-000002",
                "Head": "Mary Nyankol",
                "Members": 4,
                "State": "Central Equatoria",
                "County": "Yei",
            },
        ]
    )


# ============================================================
# PAGE HEADER FUNCTION
# ============================================================

def page_header(
    title: str,
    description: str,
) -> None:

    st.markdown(
        f"""
        <div class="page-title">{title}</div>
        <div class="page-description">
            {description}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:

    page_header(
        "National Registry Overview",
        "National population, identity and civil registration management.",
    )

    cols = st.columns(5)

    metrics = [
        ("Registered Citizens", "2,847,392", "+8.4%"),
        ("Households", "613,482", "+5.2%"),
        ("Verified Identities", "2,431,820", "+11.7%"),
        ("Pending Registrations", "18,492", "-4.1%"),
        ("Registration Centres", "142", "+6.0%"),
    ]

    for col, (label, value, change) in zip(cols, metrics):

        with col:

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">
                        {label}
                    </div>
                    <div class="metric-value">
                        {value}
                    </div>
                    <div class="metric-change">
                        {change} from previous period
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    left, right = st.columns(2)

    with left:

        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">
                    Registration Activity
                </div>
                <div class="section-description">
                    Monthly citizen registrations.
                </div>
            """,
            unsafe_allow_html=True,
        )

        activity = pd.DataFrame(
            {
                "Month": [
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                ],
                "Registrations": [
                    18400,
                    22100,
                    24700,
                    26100,
                    29400,
                    31700,
                ],
            }
        )

        st.bar_chart(
            activity.set_index("Month")
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with right:

        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">
                    Registry Status
                </div>
                <div class="section-description">
                    Current national registry processing status.
                </div>
            """,
            unsafe_allow_html=True,
        )

        registry_status = pd.DataFrame(
            {
                "Category": [
                    "Verified",
                    "Pending",
                    "Under Review",
                    "Rejected",
                ],
                "Records": [
                    2431820,
                    18492,
                    6120,
                    2840,
                ],
            }
        )

        st.bar_chart(
            registry_status.set_index("Category")
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">
                System Status
            </div>
            <div class="section-description">
                Core National Registry services.
            </div>
        """,
        unsafe_allow_html=True,
    )

    status_cols = st.columns(4)

    systems = [
        ("Citizen Registry", "Operational"),
        ("Identity Verification", "Operational"),
        ("Document Services", "Operational"),
        ("Reporting Engine", "Operational"),
    ]

    for col, (name, status) in zip(status_cols, systems):

        with col:

            st.markdown(
                f"""
                <strong>{name}</strong><br>
                <span class="status-online">
                    {status}
                </span>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# CITIZENS
# ============================================================

def render_citizens() -> None:

    page_header(
        "Citizen Registry",
        "Register, search and manage national citizen records.",
    )

    tabs = st.tabs(
        [
            "Citizen Directory",
            "Register Citizen",
            "Citizen Search",
        ]
    )

    citizens = sample_citizens()

    with tabs[0]:

        st.dataframe(
            citizens,
            use_container_width=True,
            hide_index=True,
        )

    with tabs[1]:

        with st.form("citizen_registration"):

            col1, col2 = st.columns(2)

            with col1:

                first_name = st.text_input(
                    "First Name"
                )

                middle_name = st.text_input(
                    "Middle Name"
                )

                last_name = st.text_input(
                    "Last Name"
                )

                gender = st.selectbox(
                    "Gender",
                    [
                        "Male",
                        "Female",
                        "Other",
                    ],
                )

            with col2:

                date_of_birth = st.date_input(
                    "Date of Birth"
                )

                nationality = st.text_input(
                    "Nationality",
                    value="South Sudanese",
                )

                state = st.selectbox(
                    "State",
                    [
                        "Central Equatoria",
                        "Eastern Equatoria",
                        "Western Equatoria",
                        "Jonglei",
                        "Upper Nile",
                        "Unity",
                        "Lakes",
                        "Warrap",
                        "Northern Bahr el Ghazal",
                        "Western Bahr el Ghazal",
                        "Abyei Administrative Area",
                    ],
                )

                county = st.text_input(
                    "County"
                )

            submitted = st.form_submit_button(
                "Register Citizen",
                use_container_width=True,
            )

            if submitted:

                if not first_name or not last_name:

                    st.error(
                        "First Name and Last Name are required."
                    )

                else:

                    st.success(
                        "Citizen registration submitted successfully."
                    )

    with tabs[2]:

        query = st.text_input(
            "Search by National ID, name or location"
        )

        if query:

            result = citizens[
                citizens.astype(str)
                .apply(
                    lambda row:
                    row.str.contains(
                        query,
                        case=False,
                        na=False,
                    ).any(),
                    axis=1,
                )
            ]

            st.dataframe(
                result,
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# HOUSEHOLDS
# ============================================================

def render_households() -> None:

    page_header(
        "Household Registry",
        "Manage household composition, residence and demographic information.",
    )

    households = sample_households()

    st.dataframe(
        households,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader("Register Household")

    col1, col2 = st.columns(2)

    with col1:

        st.text_input(
            "Household Head"
        )

        st.number_input(
            "Number of Members",
            min_value=1,
            value=1,
        )

    with col2:

        st.selectbox(
            "State",
            [
                "Central Equatoria",
                "Eastern Equatoria",
                "Western Equatoria",
                "Jonglei",
                "Upper Nile",
                "Unity",
                "Lakes",
                "Warrap",
                "Northern Bahr el Ghazal",
                "Western Bahr el Ghazal",
            ],
        )

        st.text_input(
            "County"
        )

    if st.button(
        "Create Household",
        type="primary",
    ):

        st.success(
            "Household registration submitted."
        )


# ============================================================
# CIVIL REGISTRATION
# ============================================================

def render_civil_registration() -> None:

    page_header(
        "Civil Registration",
        "Birth, death, marriage and other civil-status registration services.",
    )

    registration_type = st.selectbox(
        "Registration Service",
        [
            "Birth Registration",
            "Death Registration",
            "Marriage Registration",
            "Divorce Registration",
            "Adoption Registration",
            "Other Civil Event",
        ],
    )

    st.markdown(
        '<div class="section-card">',
        unsafe_allow_html=True,
    )

    st.subheader(registration_type)

    col1, col2 = st.columns(2)

    with col1:

        st.text_input(
            "Person / Applicant Name"
        )

        st.date_input(
            "Event Date"
        )

    with col2:

        st.text_input(
            "Registration Centre"
        )

        st.text_input(
            "Supporting Document Number"
        )

    notes = st.text_area(
        "Additional Information"
    )

    if st.button(
        "Submit Registration",
        type="primary",
    ):

        st.success(
            f"{registration_type} submitted for processing."
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# IDENTITY
# ============================================================

def render_identity() -> None:

    page_header(
        "National Identity",
        "National identification, biometric identity and verification services.",
    )

    cols = st.columns(3)

    with cols[0]:

        st.metric(
            "Identity Records",
            "2.48M",
        )

    with cols[1]:

        st.metric(
            "Biometric Enrolments",
            "2.21M",
        )

    with cols[2]:

        st.metric(
            "Verified",
            "98.1%",
        )

    st.divider()

    st.subheader("Identity Verification")

    national_id = st.text_input(
        "National ID Number"
    )

    if st.button(
        "Verify Identity",
        type="primary",
    ):

        if national_id:

            st.success(
                "Identity verification request submitted."
            )

        else:

            st.warning(
                "Enter a National ID Number."
            )


# ============================================================
# LOCATIONS
# ============================================================

def render_locations() -> None:

    page_header(
        "Administrative Locations",
        "Manage states, counties, payams, bomas and registration centres.",
    )

    location_type = st.selectbox(
        "Location Type",
        [
            "State",
            "County",
            "Payam",
            "Boma",
            "Registration Centre",
        ],
    )

    st.info(
        f"Location management interface: {location_type}"
    )

    locations = pd.DataFrame(
        [
            {
                "State": "Central Equatoria",
                "Counties": 6,
                "Registration Centres": 31,
            },
            {
                "State": "Jonglei",
                "Counties": 11,
                "Registration Centres": 24,
            },
            {
                "State": "Upper Nile",
                "Counties": 13,
                "Registration Centres": 21,
            },
        ]
    )

    st.dataframe(
        locations,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# DOCUMENTS
# ============================================================

def render_documents() -> None:

    page_header(
        "Document Management",
        "Secure registry documents, certificates and supporting records.",
    )

    uploaded_file = st.file_uploader(
        "Upload Registry Document",
        type=[
            "pdf",
            "png",
            "jpg",
            "jpeg",
        ],
    )

    document_type = st.selectbox(
        "Document Type",
        [
            "Birth Certificate",
            "Death Certificate",
            "Marriage Certificate",
            "National ID Document",
            "Passport",
            "Other",
        ],
    )

    if uploaded_file:

        st.success(
            f"{uploaded_file.name} ready for processing."
        )

        if st.button(
            "Register Document"
        ):

            st.success(
                "Document registered successfully."
            )


# ============================================================
# VERIFICATION
# ============================================================

def render_verification() -> None:

    page_header(
        "Registry Verification",
        "Review, validate and approve registry records.",
    )

    queue = pd.DataFrame(
        [
            {
                "Reference": "REG-2026-00021",
                "Applicant": "Peter Bol",
                "Type": "Citizen",
                "Status": "Pending",
            },
            {
                "Reference": "REG-2026-00022",
                "Applicant": "Sarah Deng",
                "Type": "Birth",
                "Status": "Pending",
            },
        ]
    )

    st.dataframe(
        queue,
        use_container_width=True,
        hide_index=True,
    )

    reference = st.text_input(
        "Verification Reference"
    )

    if reference:

        col1, col2, col3 = st.columns(3)

        with col1:

            if st.button(
                "Approve",
                use_container_width=True,
            ):

                st.success(
                    "Record approved."
                )

        with col2:

            if st.button(
                "Request Review",
                use_container_width=True,
            ):

                st.warning(
                    "Record sent for additional review."
                )

        with col3:

            if st.button(
                "Reject",
                use_container_width=True,
            ):

                st.error(
                    "Record rejected."
                )


# ============================================================
# REPORTS
# ============================================================

def render_reports() -> None:

    page_header(
        "Registry Reports",
        "Population, registration, identity and administrative reporting.",
    )

    report_type = st.selectbox(
        "Report",
        [
            "Population by State",
            "Citizen Registration",
            "Birth Registration",
            "Death Registration",
            "Marriage Registration",
            "National Identity",
            "Household Statistics",
        ],
    )

    report = pd.DataFrame(
        {
            "State": [
                "Central Equatoria",
                "Jonglei",
                "Upper Nile",
                "Unity",
                "Western Equatoria",
            ],
            "Registered": [
                520000,
                480000,
                390000,
                310000,
                260000,
            ],
        }
    )

    st.dataframe(
        report,
        use_container_width=True,
        hide_index=True,
    )

    st.bar_chart(
        report.set_index("State")
    )

    st.download_button(
        "Download Report",
        report.to_csv(index=False),
        file_name="registry_report.csv",
        mime="text/csv",
    )


# ============================================================
# AI STUDIO
# ============================================================

def render_ai_studio() -> None:

    st.markdown(
        """
        <div class="ai-panel">
            <div class="ai-title">
                AI Studio
            </div>
            <div class="ai-description">
                Intelligent assistance for National Registry
                operations, analytics and decision support.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs(
        [
            "AI Assistant",
            "Registry Analytics",
            "Data Quality",
            "Insights",
        ]
    )

    with tabs[0]:

        st.subheader(
            "Registry AI Assistant"
        )

        prompt = st.chat_input(
            "Ask about registry operations..."
        )

        if prompt:

            with st.chat_message("user"):

                st.write(prompt)

            with st.chat_message("assistant"):

                st.write(
                    "AI Assistant is ready to connect "
                    "to the National Registry intelligence "
                    "engine."
                )

    with tabs[1]:

        st.subheader(
            "AI Registry Analytics"
        )

        st.info(
            "This workspace can connect to an AI analytics "
            "engine for population trends, registration "
            "patterns and operational forecasting."
        )

    with tabs[2]:

        st.subheader(
            "Data Quality Intelligence"
        )

        quality = pd.DataFrame(
            {
                "Quality Metric": [
                    "Duplicate Records",
                    "Missing Birth Dates",
                    "Incomplete Addresses",
                    "Unverified Identity",
                ],
                "Records": [
                    421,
                    1280,
                    3942,
                    6120,
                ],
            }
        )

        st.dataframe(
            quality,
            use_container_width=True,
            hide_index=True,
        )

    with tabs[3]:

        st.subheader(
            "Registry Intelligence"
        )

        st.info(
            "AI-generated national registry insights "
            "will appear here when the intelligence "
            "engine is connected."
        )


# ============================================================
# ADMINISTRATION
# ============================================================

def render_administration() -> None:

    page_header(
        "Administration",
        "System configuration, users, roles and registry governance.",
    )

    tabs = st.tabs(
        [
            "Users",
            "Roles",
            "System",
            "Audit Log",
        ]
    )

    with tabs[0]:

        st.subheader(
            "Registry Users"
        )

        users = pd.DataFrame(
            [
                {
                    "User": "System Administrator",
                    "Role": "Administrator",
                    "Status": "Active",
                },
                {
                    "User": "Registration Officer",
                    "Role": "Registration Officer",
                    "Status": "Active",
                },
            ]
        )

        st.dataframe(
            users,
            use_container_width=True,
            hide_index=True,
        )

    with tabs[1]:

        st.subheader(
            "Roles & Permissions"
        )

        st.checkbox(
            "Administrator"
        )

        st.checkbox(
            "Registration Officer"
        )

        st.checkbox(
            "Verification Officer"
        )

        st.checkbox(
            "Reporting Officer"
        )

    with tabs[2]:

        st.subheader(
            "System Configuration"
        )

        st.text_input(
            "Registry Name",
            value=APP_NAME,
        )

        st.text_input(
            "Application Version",
            value=APP_VERSION,
            disabled=True,
        )

        st.toggle(
            "Enable AI Services",
            value=True,
        )

    with tabs[3]:

        st.subheader(
            "Audit Log"
        )

        audit = pd.DataFrame(
            [
                {
                    "Time": "2026-09-01 02:20",
                    "User": "Administrator",
                    "Action": "Citizen Verification",
                },
                {
                    "Time": "2026-09-01 02:14",
                    "User": "Registration Officer",
                    "Action": "Birth Registration",
                },
            ]
        )

        st.dataframe(
            audit,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# ROUTER
# ============================================================

ROUTES = {
    "Overview": render_overview,
    "Citizens": render_citizens,
    "Households": render_households,
    "Civil Registration": render_civil_registration,
    "Identity": render_identity,
    "Locations": render_locations,
    "Documents": render_documents,
    "Verification": render_verification,
    "Reports": render_reports,
    "AI Studio": render_ai_studio,
    "Administration": render_administration,
}


render_function = ROUTES.get(
    active_tab,
    render_overview,
)

render_function()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    f"""
    <div class="footer">
        {APP_NAME} · {APP_VERSION}
        <br>
        National Identity • Civil Registration • Population Registry
    </div>
    """,
    unsafe_allow_html=True,
)
