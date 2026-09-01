"""
South Sudan National Registry
AI Studio — Streamlit Operational Console

Version: 1.0.0 Alpha

Architecture
------------
Streamlit UI
    -> Registry service functions
    -> SQLite/PostgreSQL-compatible database

The application is intentionally database-first:
records are persisted and are not stored in Streamlit session state.

Production deployment should use PostgreSQL through DATABASE_URL.
Local development falls back to SQLite.
"""

from __future__ import annotations

import csv
import io
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterator

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

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB = BASE_DIR / "data" / "registry.db"

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

NAVIGATION = [
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

STATES = [
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
    "Ruweng Administrative Area",
    "Abyei Administrative Area",
    "Pibor Administrative Area",
    "Other",
]

GENDERS = ["Male", "Female", "Other"]

MARITAL_STATUSES = [
    "Single",
    "Married",
    "Widowed",
    "Divorced",
    "Separated",
]

HOUSEHOLD_ROLES = [
    "Head of Household",
    "Spouse",
    "Son / Daughter",
    "Parent / Parent-in-law",
    "Grandchild",
    "Other Relative",
    "Non-Relative / Resident",
]

VERIFICATION_STATUSES = [
    "Verified",
    "Pending Review",
    "Flagged",
]

IDENTIFICATION_TYPES = [
    "National ID",
    "Passport",
    "Birth Certificate",
    "Refugee / Alien Registration",
    "Voter Card",
    "Other",
]

EDUCATION_LEVELS = [
    "None / Informal",
    "Primary Education",
    "Secondary Education",
    "Vocational / Diploma",
    "Tertiary / Bachelor Degree",
    "Post-Graduate (Master/PhD)",
]

EMPLOYMENT_STATUSES = [
    "Employed (Private Sector)",
    "Employed (Public/Civil Service)",
    "Self-Employed / Business",
    "Agriculture & Farming",
    "Pastoralism & Livestock",
    "Artisan / Trade",
    "Student",
    "Unemployed / Seeking Work",
    "Homemaker / Caregiver",
    "Retired / Pensioner",
]


# ============================================================
# SESSION STATE
# ============================================================

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Overview"

if "selected_citizen_id" not in st.session_state:
    st.session_state.selected_citizen_id = None

if "authenticated" not in st.session_state:
    st.session_state.authenticated = True


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
        .stApp {
            background: #f8fafc;
        }

        .block-container {
            max-width: 1500px;
            padding-top: 1rem;
            padding-bottom: 5rem;
        }

        .brand {
            display:flex;
            align-items:center;
            gap:14px;
            padding:8px 0 18px;
        }

        .brand-mark {
            width:50px;
            height:50px;
            border-radius:14px;
            background:#0f5132;
            color:white;
            display:flex;
            align-items:center;
            justify-content:center;
            font-weight:800;
            font-size:22px;
        }

        .brand-title {
            font-size:23px;
            font-weight:800;
            color:#0f172a;
        }

        .brand-subtitle {
            color:#64748b;
            font-size:12px;
            margin-top:3px;
        }

        .page-title {
            font-size:30px;
            font-weight:800;
            color:#0f172a;
            margin-bottom:4px;
        }

        .page-description {
            color:#64748b;
            margin-bottom:20px;
        }

        .card {
            background:white;
            border:1px solid #e2e8f0;
            border-radius:16px;
            padding:20px;
            margin-bottom:18px;
            box-shadow:0 3px 12px rgba(15,23,42,.04);
        }

        .kpi {
            background:white;
            border:1px solid #e2e8f0;
            border-radius:16px;
            padding:18px;
            min-height:120px;
        }

        .kpi-label {
            color:#64748b;
            font-size:12px;
            font-weight:700;
        }

        .kpi-value {
            color:#0f172a;
            font-size:28px;
            font-weight:800;
            margin-top:8px;
        }

        .kpi-note {
            color:#198754;
            font-size:11px;
            margin-top:4px;
        }

        .ai-panel {
            background:#0f172a;
            border-radius:18px;
            padding:26px;
            color:white;
            margin-bottom:20px;
        }

        .ai-title {
            font-size:25px;
            font-weight:800;
        }

        .ai-subtitle {
            color:#cbd5e1;
            margin-top:5px;
        }

        .footer {
            text-align:center;
            color:#94a3b8;
            font-size:11px;
            padding:35px 0 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE
# ============================================================

def sqlite_path() -> Path:
    DEFAULT_DB.parent.mkdir(parents=True, exist_ok=True)
    return DEFAULT_DB


@contextmanager
def db_connection() -> Iterator[sqlite3.Connection]:
    """
    SQLite development connection.

    DATABASE_URL is intentionally recognized so that the application
    can later switch to PostgreSQL without changing the UI/service API.
    """

    if DATABASE_URL and DATABASE_URL.startswith(("postgres://", "postgresql://")):
        raise RuntimeError(
            "PostgreSQL DATABASE_URL detected. "
            "Install/configure the PostgreSQL adapter before production use."
        )

    connection = sqlite3.connect(
        sqlite_path(),
        timeout=30,
        check_same_thread=False,
    )

    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database() -> None:
    with db_connection() as conn:

        conn.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS citizens (
                id TEXT PRIMARY KEY,
                national_id TEXT UNIQUE,
                passport_number TEXT,
                id_document_type TEXT,

                full_name TEXT NOT NULL,
                date_of_birth TEXT,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                marital_status TEXT NOT NULL,

                phone_number TEXT,
                email_address TEXT,
                emergency_contact_name TEXT,
                emergency_contact_phone TEXT,

                tribe TEXT NOT NULL DEFAULT '',
                sub_tribe_or_clan TEXT,
                native_language TEXT NOT NULL DEFAULT '',
                nationality TEXT NOT NULL DEFAULT 'South Sudanese',

                community TEXT NOT NULL DEFAULT '',
                boma TEXT,
                sub_county_or_boma TEXT NOT NULL DEFAULT '',
                county_or_payam TEXT NOT NULL DEFAULT '',
                state_or_region TEXT NOT NULL DEFAULT '',
                residential_address TEXT,
                duration_of_stay_years REAL DEFAULT 0,

                household_id TEXT,
                household_role TEXT NOT NULL DEFAULT 'Head of Household',
                is_household_head INTEGER NOT NULL DEFAULT 0,

                education_level TEXT NOT NULL DEFAULT 'None / Informal',
                is_literate INTEGER NOT NULL DEFAULT 0,

                employment_status TEXT NOT NULL DEFAULT 'Unemployed / Seeking Work',
                primary_occupation TEXT,
                employer_or_business_name TEXT,
                industry_sector TEXT,
                monthly_income_range TEXT,

                has_special_needs_or_disability INTEGER NOT NULL DEFAULT 0,
                disability_type TEXT,

                mother_alive INTEGER,
                father_alive INTEGER,

                voter_id_number TEXT UNIQUE,
                voter_status TEXT,
                constituency TEXT,
                polling_station_id TEXT,
                polling_station_name TEXT,
                has_voted INTEGER NOT NULL DEFAULT 0,
                voted_at TEXT,

                enumerator_name TEXT NOT NULL DEFAULT '',
                enumerator_badge_id TEXT NOT NULL DEFAULT '',
                enumeration_date TEXT NOT NULL,

                verification_status TEXT NOT NULL DEFAULT 'Pending Review',
                notes TEXT,

                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS households (
                id TEXT PRIMARY KEY,
                household_number TEXT UNIQUE NOT NULL,
                head_citizen_id TEXT,
                state_or_region TEXT NOT NULL,
                county_or_payam TEXT,
                sub_county_or_boma TEXT,
                boma TEXT,
                community TEXT,
                residential_address TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                FOREIGN KEY(head_citizen_id)
                    REFERENCES citizens(id)
                    ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS civil_events (
                id TEXT PRIMARY KEY,
                reference_number TEXT UNIQUE NOT NULL,
                event_type TEXT NOT NULL,
                citizen_id TEXT,
                event_date TEXT NOT NULL,
                registration_centre TEXT,
                document_number TEXT,
                status TEXT NOT NULL DEFAULT 'Pending Review',
                notes TEXT,
                created_at TEXT NOT NULL,

                FOREIGN KEY(citizen_id)
                    REFERENCES citizens(id)
                    ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                document_number TEXT,
                document_type TEXT NOT NULL,
                citizen_id TEXT,
                file_name TEXT,
                status TEXT NOT NULL DEFAULT 'Registered',
                created_at TEXT NOT NULL,

                FOREIGN KEY(citizen_id)
                    REFERENCES citizens(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS administrative_units (
                id TEXT PRIMARY KEY,
                unit_type TEXT NOT NULL,
                name TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                parent_id TEXT,
                state_or_region TEXT NOT NULL,
                administrator_name TEXT,
                headquarters TEXT,
                target_population INTEGER,
                notes TEXT,

                FOREIGN KEY(parent_id)
                    REFERENCES administrative_units(id)
                    ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT,
                username TEXT NOT NULL DEFAULT 'streamlit-user',
                created_at TEXT NOT NULL,
                details TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_citizen_name
                ON citizens(full_name);

            CREATE INDEX IF NOT EXISTS idx_citizen_state
                ON citizens(state_or_region);

            CREATE INDEX IF NOT EXISTS idx_citizen_household
                ON citizens(household_id);

            CREATE INDEX IF NOT EXISTS idx_citizen_status
                ON citizens(verification_status);

            CREATE INDEX IF NOT EXISTS idx_civil_status
                ON civil_events(status);
            """
        )


initialize_database()


# ============================================================
# DATABASE HELPERS
# ============================================================

def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12].upper()}"


def audit(
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    details: str = "",
) -> None:

    with db_connection() as conn:

        conn.execute(
            """
            INSERT INTO audit_log
            (action, entity_type, entity_id, username, created_at, details)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                action,
                entity_type,
                entity_id,
                "streamlit-user",
                now_iso(),
                details,
            ),
        )


def fetch_dataframe(
    query: str,
    params: tuple[Any, ...] = (),
) -> pd.DataFrame:

    with db_connection() as conn:
        return pd.read_sql_query(
            query,
            conn,
            params=params,
        )


def scalar(
    query: str,
    params: tuple[Any, ...] = (),
) -> Any:

    with db_connection() as conn:
        row = conn.execute(
            query,
            params,
        ).fetchone()

        return row[0] if row else 0


# ============================================================
# CITIZEN SERVICES
# ============================================================

def citizen_count() -> int:
    return int(
        scalar(
            "SELECT COUNT(*) FROM citizens"
        )
    )


def household_count() -> int:
    return int(
        scalar(
            "SELECT COUNT(*) FROM households"
        )
    )


def verified_count() -> int:
    return int(
        scalar(
            """
            SELECT COUNT(*)
            FROM citizens
            WHERE verification_status = 'Verified'
            """
        )
    )


def pending_count() -> int:
    return int(
        scalar(
            """
            SELECT COUNT(*)
            FROM citizens
            WHERE verification_status = 'Pending Review'
            """
        )
    )


def create_citizen(data: dict[str, Any]) -> str:

    citizen_id = new_id("CEN")
    timestamp = now_iso()

    with db_connection() as conn:

        conn.execute(
            """
            INSERT INTO citizens (
                id,
                national_id,
                passport_number,
                id_document_type,
                full_name,
                date_of_birth,
                age,
                gender,
                marital_status,
                phone_number,
                email_address,
                emergency_contact_name,
                emergency_contact_phone,
                tribe,
                sub_tribe_or_clan,
                native_language,
                nationality,
                community,
                boma,
                sub_county_or_boma,
                county_or_payam,
                state_or_region,
                residential_address,
                duration_of_stay_years,
                household_id,
                household_role,
                is_household_head,
                education_level,
                is_literate,
                employment_status,
                primary_occupation,
                employer_or_business_name,
                industry_sector,
                monthly_income_range,
                has_special_needs_or_disability,
                disability_type,
                mother_alive,
                father_alive,
                voter_id_number,
                voter_status,
                constituency,
                polling_station_id,
                polling_station_name,
                has_voted,
                voted_at,
                enumerator_name,
                enumerator_badge_id,
                enumeration_date,
                verification_status,
                notes,
                created_at,
                updated_at
            )
            VALUES (
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                ?,?,?,?
            )
            """,
            (
                citizen_id,
                data.get("national_id"),
                data.get("passport_number"),
                data.get("id_document_type"),
                data["full_name"],
                data.get("date_of_birth"),
                data["age"],
                data["gender"],
                data["marital_status"],
                data.get("phone_number"),
                data.get("email_address"),
                data.get("emergency_contact_name"),
                data.get("emergency_contact_phone"),
                data.get("tribe", ""),
                data.get("sub_tribe_or_clan"),
                data.get("native_language", ""),
                data.get("nationality", "South Sudanese"),
                data.get("community", ""),
                data.get("boma"),
                data.get("sub_county_or_boma", ""),
                data.get("county_or_payam", ""),
                data.get("state_or_region", ""),
                data.get("residential_address"),
                data.get("duration_of_stay_years", 0),
                data.get("household_id"),
                data.get("household_role", "Head of Household"),
                int(data.get("is_household_head", False)),
                data.get("education_level", "None / Informal"),
                int(data.get("is_literate", False)),
                data.get("employment_status", "Unemployed / Seeking Work"),
                data.get("primary_occupation"),
                data.get("employer_or_business_name"),
                data.get("industry_sector"),
                data.get("monthly_income_range"),
                int(data.get("has_special_needs_or_disability", False)),
                data.get("disability_type"),
                data.get("mother_alive"),
                data.get("father_alive"),
                data.get("voter_id_number"),
                data.get("voter_status"),
                data.get("constituency"),
                data.get("polling_station_id"),
                data.get("polling_station_name"),
                int(data.get("has_voted", False)),
                data.get("voted_at"),
                data.get("enumerator_name", ""),
                data.get("enumerator_badge_id", ""),
                data.get("enumeration_date", str(date.today())),
                data.get("verification_status", "Pending Review"),
                data.get("notes"),
                timestamp,
                timestamp,
            ),
        )

    audit(
        "CREATE",
        "Citizen",
        citizen_id,
        data["full_name"],
    )

    return citizen_id


def update_citizen(
    citizen_id: str,
    fields: dict[str, Any],
) -> None:

    if not fields:
        return

    fields["updated_at"] = now_iso()

    assignments = ", ".join(
        f"{key} = ?"
        for key in fields
    )

    values = list(fields.values())
    values.append(citizen_id)

    with db_connection() as conn:

        conn.execute(
            f"""
            UPDATE citizens
            SET {assignments}
            WHERE id = ?
            """,
            values,
        )

    audit(
        "UPDATE",
        "Citizen",
        citizen_id,
        str(fields),
    )


def get_citizen(
    citizen_id: str,
) -> dict[str, Any] | None:

    with db_connection() as conn:

        row = conn.execute(
            """
            SELECT *
            FROM citizens
            WHERE id = ?
            """,
            (citizen_id,),
        ).fetchone()

    return dict(row) if row else None


# ============================================================
# HOUSEHOLD SERVICES
# ============================================================

def create_household(
    data: dict[str, Any],
) -> str:

    household_id = new_id("HH")
    household_number = f"HH-{uuid.uuid4().hex[:6].upper()}"
    timestamp = now_iso()

    with db_connection() as conn:

        conn.execute(
            """
            INSERT INTO households (
                id,
                household_number,
                head_citizen_id,
                state_or_region,
                county_or_payam,
                sub_county_or_boma,
                boma,
                community,
                residential_address,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                household_id,
                household_number,
                data.get("head_citizen_id"),
                data["state_or_region"],
                data.get("county_or_payam"),
                data.get("sub_county_or_boma"),
                data.get("boma"),
                data.get("community"),
                data.get("residential_address"),
                timestamp,
                timestamp,
            ),
        )

    audit(
        "CREATE",
        "Household",
        household_id,
        household_number,
    )

    return household_id


# ============================================================
# CIVIL REGISTRATION
# ============================================================

def create_civil_event(
    event_type: str,
    citizen_id: str | None,
    event_date: str,
    registration_centre: str,
    document_number: str,
    notes: str,
) -> str:

    event_id = new_id("CER")
    reference = f"REG-{datetime.utcnow().year}-{uuid.uuid4().hex[:8].upper()}"

    with db_connection() as conn:

        conn.execute(
            """
            INSERT INTO civil_events (
                id,
                reference_number,
                event_type,
                citizen_id,
                event_date,
                registration_centre,
                document_number,
                status,
                notes,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                reference,
                event_type,
                citizen_id,
                event_date,
                registration_centre,
                document_number,
                "Pending Review",
                notes,
                now_iso(),
            ),
        )

    audit(
        "CREATE",
        "Civil Event",
        event_id,
        reference,
    )

    return reference


# ============================================================
# DOCUMENT SERVICES
# ============================================================

def register_document(
    document_type: str,
    citizen_id: str | None,
    document_number: str,
    file_name: str | None,
) -> str:

    document_id = new_id("DOC")

    with db_connection() as conn:

        conn.execute(
            """
            INSERT INTO documents (
                id,
                document_number,
                document_type,
                citizen_id,
                file_name,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                document_id,
                document_number,
                document_type,
                citizen_id,
                file_name,
                "Registered",
                now_iso(),
            ),
        )

    audit(
        "CREATE",
        "Document",
        document_id,
        document_type,
    )

    return document_id


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="brand">
        <div class="brand-mark">SS</div>
        <div>
            <div class="brand-title">
                South Sudan National Registry
            </div>
            <div class="brand-subtitle">
                AI Studio • National Identity • Civil Registration • Population Registry
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# NAVIGATION
# ============================================================

nav_cols = st.columns(len(NAVIGATION))

for index, item in enumerate(NAVIGATION):

    with nav_cols[index]:

        if st.button(
            item,
            key=f"nav_{index}",
            use_container_width=True,
        ):
            st.session_state.active_tab = item
            st.rerun()


active_tab = st.session_state.active_tab

st.divider()


# ============================================================
# PAGE HEADER
# ============================================================

def page_header(
    title: str,
    description: str,
) -> None:

    st.markdown(
        f"""
        <div class="page-title">{title}</div>
        <div class="page-description">{description}</div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:

    page_header(
        "National Registry Overview",
        "Live operational view of the persistent registry database.",
    )

    metrics = [
        (
            "Registered Citizens",
            f"{citizen_count():,}",
            "Persistent",
        ),
        (
            "Households",
            f"{household_count():,}",
            "Persistent",
        ),
        (
            "Verified Citizens",
            f"{verified_count():,}",
            "Verified",
        ),
        (
            "Pending Review",
            f"{pending_count():,}",
            "Requires action",
        ),
    ]

    cols = st.columns(4)

    for col, (label, value, note) in zip(
        cols,
        metrics,
    ):

        with col:

            st.markdown(
                f"""
                <div class="kpi">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                    <div class="kpi-note">{note}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    left, right = st.columns(2)

    with left:

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True,
        )

        st.subheader("Population by State")

        df = fetch_dataframe(
            """
            SELECT
                state_or_region AS State,
                COUNT(*) AS Citizens
            FROM citizens
            GROUP BY state_or_region
            ORDER BY Citizens DESC
            """
        )

        if df.empty:
            st.info("No citizen records have been registered yet.")
        else:
            st.bar_chart(
                df.set_index("State")
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with right:

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True,
        )

        st.subheader("Verification Status")

        df = fetch_dataframe(
            """
            SELECT
                verification_status AS Status,
                COUNT(*) AS Records
            FROM citizens
            GROUP BY verification_status
            """
        )

        if df.empty:
            st.info("No verification records yet.")
        else:
            st.bar_chart(
                df.set_index("Status")
            )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True,
    )

    st.subheader("Recent Registry Activity")

    activity = fetch_dataframe(
        """
        SELECT
            created_at AS Time,
            action AS Action,
            entity_type AS Type,
            entity_id AS Reference,
            username AS User
        FROM audit_log
        ORDER BY id DESC
        LIMIT 15
        """
    )

    if activity.empty:
        st.info("No registry activity yet.")
    else:
        st.dataframe(
            activity,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# CITIZENS
# ============================================================

def render_citizens() -> None:

    page_header(
        "Citizen Registry",
        "Register, search, inspect and manage persistent citizen records.",
    )

    tabs = st.tabs(
        [
            "Directory",
            "Register Citizen",
            "Search",
            "Citizen Profile",
            "Export",
        ]
    )

    with tabs[0]:

        df = fetch_dataframe(
            """
            SELECT
                id AS "Census ID",
                national_id AS "National ID",
                full_name AS "Full Name",
                age AS Age,
                gender AS Gender,
                marital_status AS "Marital Status",
                state_or_region AS State,
                county_or_payam AS County,
                household_id AS "Household ID",
                verification_status AS Status,
                created_at AS "Created At"
            FROM citizens
            ORDER BY created_at DESC
            """
        )

        if df.empty:
            st.info("No citizens have been registered.")
        else:
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )

    with tabs[1]:

        with st.form("citizen_registration_form"):

            st.subheader("Identification")

            c1, c2, c3 = st.columns(3)

            with c1:

                id_document_type = st.selectbox(
                    "Identification Type",
                    IDENTIFICATION_TYPES,
                )

                national_id = st.text_input(
                    "National ID",
                )

            with c2:

                passport_number = st.text_input(
                    "Passport Number",
                )

                full_name = st.text_input(
                    "Full Name *",
                )

            with c3:

                dob = st.date_input(
                    "Date of Birth",
                    value=date(2000, 1, 1),
                )

                gender = st.selectbox(
                    "Gender",
                    GENDERS,
                )

            age = max(
                0,
                date.today().year - dob.year
                - (
                    (date.today().month, date.today().day)
                    < (dob.month, dob.day)
                ),
            )

            marital_status = st.selectbox(
                "Marital Status",
                MARITAL_STATUSES,
            )

            st.subheader("Contact")

            c1, c2 = st.columns(2)

            with c1:

                phone = st.text_input(
                    "Phone Number",
                )

                email = st.text_input(
                    "Email Address",
                )

            with c2:

                emergency_name = st.text_input(
                    "Emergency Contact Name",
                )

                emergency_phone = st.text_input(
                    "Emergency Contact Phone",
                )

            st.subheader("Location")

            c1, c2, c3 = st.columns(3)

            with c1:

                state = st.selectbox(
                    "State / Region",
                    STATES,
                )

                county = st.text_input(
                    "County / Payam",
                )

            with c2:

                payam = st.text_input(
                    "Payam / Sub-County",
                )

                boma = st.text_input(
                    "Boma",
                )

            with c3:

                community = st.text_input(
                    "Community / Settlement",
                )

                address = st.text_input(
                    "Residential Address",
                )

            st.subheader("Household")

            c1, c2, c3 = st.columns(3)

            with c1:

                household_id = st.text_input(
                    "Household ID",
                )

            with c2:

                household_role = st.selectbox(
                    "Household Role",
                    HOUSEHOLD_ROLES,
                )

            with c3:

                household_head = st.checkbox(
                    "Is Head of Household",
                )

            st.subheader("Demographics & Socioeconomic Data")

            c1, c2 = st.columns(2)

            with c1:

                tribe = st.text_input(
                    "Tribe / Ethnicity",
                )

                clan = st.text_input(
                    "Sub-Tribe / Clan",
                )

                native_language = st.text_input(
                    "Native Language",
                )

                education = st.selectbox(
                    "Education Level",
                    EDUCATION_LEVELS,
                )

                literate = st.checkbox(
                    "Literate",
                )

            with c2:

                employment = st.selectbox(
                    "Employment Status",
                    EMPLOYMENT_STATUSES,
                )

                occupation = st.text_input(
                    "Primary Occupation",
                )

                employer = st.text_input(
                    "Employer / Business",
                )

                income = st.text_input(
                    "Monthly Income Range",
                )

                special_needs = st.checkbox(
                    "Special Needs / Disability",
                )

            disability_type = ""

            if special_needs:

                disability_type = st.text_input(
                    "Disability / Special Needs Details",
                )

            st.subheader("Enumeration & Verification")

            c1, c2, c3 = st.columns(3)

            with c1:

                enumerator = st.text_input(
                    "Enumerator Name",
                )

            with c2:

                badge = st.text_input(
                    "Enumerator Badge ID",
                )

            with c3:

                verification = st.selectbox(
                    "Verification Status",
                    VERIFICATION_STATUSES,
                )

            notes = st.text_area(
                "Notes",
            )

            submitted = st.form_submit_button(
                "Register Citizen",
                type="primary",
                use_container_width=True,
            )

            if submitted:

                if not full_name.strip():

                    st.error(
                        "Full Name is required."
                    )

                else:

                    try:

                        citizen_id = create_citizen(
                            {
                                "national_id": national_id or None,
                                "passport_number": passport_number or None,
                                "id_document_type": id_document_type,
                                "full_name": full_name.strip(),
                                "date_of_birth": dob.isoformat(),
                                "age": age,
                                "gender": gender,
                                "marital_status": marital_status,
                                "phone_number": phone or None,
                                "email_address": email or None,
                                "emergency_contact_name": emergency_name or None,
                                "emergency_contact_phone": emergency_phone or None,
                                "tribe": tribe,
                                "sub_tribe_or_clan": clan or None,
                                "native_language": native_language,
                                "nationality": "South Sudanese",
                                "community": community,
                                "boma": boma or None,
                                "sub_county_or_boma": payam,
                                "county_or_payam": county,
                                "state_or_region": state,
                                "residential_address": address or None,
                                "household_id": household_id or None,
                                "household_role": household_role,
                                "is_household_head": household_head,
                                "education_level": education,
                                "is_literate": literate,
                                "employment_status": employment,
                                "primary_occupation": occupation or None,
                                "employer_or_business_name": employer or None,
                                "monthly_income_range": income or None,
                                "has_special_needs_or_disability": special_needs,
                                "disability_type": disability_type or None,
                                "enumerator_name": enumerator,
                                "enumerator_badge_id": badge,
                                "enumeration_date": date.today().isoformat(),
                                "verification_status": verification,
                                "notes": notes or None,
                            }
                        )

                        st.success(
                            f"Citizen registered successfully: {citizen_id}"
                        )

                    except sqlite3.IntegrityError as exc:

                        st.error(
                            f"Registry constraint error: {exc}"
                        )

    with tabs[2]:

        query = st.text_input(
            "Search citizens",
            placeholder="Name, National ID, household, county or state...",
        )

        if query.strip():

            search = f"%{query.strip()}%"

            df = fetch_dataframe(
                """
                SELECT
                    id AS "Census ID",
                    national_id AS "National ID",
                    full_name AS "Full Name",
                    age AS Age,
                    gender AS Gender,
                    state_or_region AS State,
                    county_or_payam AS County,
                    household_id AS "Household ID",
                    verification_status AS Status
                FROM citizens
                WHERE
                    full_name LIKE ?
                    OR national_id LIKE ?
                    OR household_id LIKE ?
                    OR county_or_payam LIKE ?
                    OR state_or_region LIKE ?
                ORDER BY full_name
                """,
                (
                    search,
                    search,
                    search,
                    search,
                    search,
                ),
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )

    with tabs[3]:

        profile_id = st.text_input(
            "Citizen Census ID",
            value=st.session_state.selected_citizen_id or "",
        )

        if profile_id:

            citizen = get_citizen(
                profile_id.strip()
            )

            if not citizen:

                st.warning(
                    "Citizen record not found."
                )

            else:

                st.subheader(
                    citizen["full_name"]
                )

                c1, c2, c3, c4 = st.columns(4)

                with c1:
                    st.metric(
                        "Age",
                        citizen["age"],
                    )

                with c2:
                    st.metric(
                        "Gender",
                        citizen["gender"],
                    )

                with c3:
                    st.metric(
                        "State",
                        citizen["state_or_region"],
                    )

                with c4:
                    st.metric(
                        "Verification",
                        citizen["verification_status"],
                    )

                st.json(citizen)

                new_status = st.selectbox(
                    "Update Verification Status",
                    VERIFICATION_STATUSES,
                    index=VERIFICATION_STATUSES.index(
                        citizen["verification_status"]
                    )
                    if citizen["verification_status"]
                    in VERIFICATION_STATUSES
                    else 1,
                )

                if st.button(
                    "Save Verification Status",
                    type="primary",
                ):

                    update_citizen(
                        profile_id.strip(),
                        {
                            "verification_status": new_status,
                        },
                    )

                    st.success(
                        "Citizen verification status updated."
                    )

    with tabs[4]:

        df = fetch_dataframe(
            "SELECT * FROM citizens ORDER BY created_at"
        )

        if df.empty:

            st.info(
                "No citizen records available for export."
            )

        else:

            csv_buffer = io.StringIO()

            df.to_csv(
                csv_buffer,
                index=False,
            )

            st.download_button(
                "Download Citizen Registry CSV",
                csv_buffer.getvalue(),
                file_name=(
                    f"citizen_registry_"
                    f"{date.today().isoformat()}.csv"
                ),
                mime="text/csv",
                use_container_width=True,
            )


# ============================================================
# HOUSEHOLDS
# ============================================================

def render_households() -> None:

    page_header(
        "Household Registry",
        "Manage household units and their relationship to citizens.",
    )

    tabs = st.tabs(
        [
            "Household Directory",
            "Create Household",
            "Household Members",
        ]
    )

    with tabs[0]:

        df = fetch_dataframe(
            """
            SELECT
                h.household_number AS "Household ID",
                h.state_or_region AS State,
                h.county_or_payam AS County,
                h.community AS Community,
                h.residential_address AS Address,
                COUNT(c.id) AS Members
            FROM households h
            LEFT JOIN citizens c
                ON c.household_id = h.household_number
            GROUP BY h.id
            ORDER BY h.created_at DESC
            """
        )

        if df.empty:
            st.info(
                "No households registered."
            )
        else:
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )

    with tabs[1]:

        with st.form("household_form"):

            c1, c2 = st.columns(2)

            with c1:

                state = st.selectbox(
                    "State / Region",
                    STATES,
                )

                county = st.text_input(
                    "County / Payam",
                )

                payam = st.text_input(
                    "Payam / Sub-County",
                )

                boma = st.text_input(
                    "Boma",
                )

            with c2:

                community = st.text_input(
                    "Community",
                )

                address = st.text_input(
                    "Residential Address",
                )

                head = st.text_input(
                    "Head Citizen ID",
                )

            submitted = st.form_submit_button(
                "Create Household",
                type="primary",
                use_container_width=True,
            )

            if submitted:

                household_id = create_household(
                    {
                        "state_or_region": state,
                        "county_or_payam": county,
                        "sub_county_or_boma": payam,
                        "boma": boma,
                        "community": community,
                        "residential_address": address,
                        "head_citizen_id": head or None,
                    }
                )

                st.success(
                    f"Household created: {household_id}"
                )

    with tabs[2]:

        household = st.text_input(
            "Household ID"
        )

        if household:

            df = fetch_dataframe(
                """
                SELECT
                    id AS "Census ID",
                    full_name AS "Full Name",
                    age AS Age,
                    gender AS Gender,
                    household_role AS "Household Role",
                    state_or_region AS State,
                    verification_status AS Status
                FROM citizens
                WHERE household_id = ?
                ORDER BY is_household_head DESC, full_name
                """,
                (household,),
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# CIVIL REGISTRATION
# ============================================================

def render_civil_registration() -> None:

    page_header(
        "Civil Registration",
        "Register and track birth, death, marriage and other civil events.",
    )

    with st.form("civil_event_form"):

        event_type = st.selectbox(
            "Event Type",
            [
                "Birth Registration",
                "Death Registration",
                "Marriage Registration",
                "Divorce Registration",
                "Adoption Registration",
                "Other Civil Event",
            ],
        )

        c1, c2 = st.columns(2)

        with c1:

            citizen_id = st.text_input(
                "Citizen Census ID",
            )

            event_date = st.date_input(
                "Event Date",
                value=date.today(),
            )

        with c2:

            centre = st.text_input(
                "Registration Centre",
            )

            document_number = st.text_input(
                "Supporting Document Number",
            )

        notes = st.text_area(
            "Notes"
        )

        submitted = st.form_submit_button(
            "Submit Civil Registration",
            type="primary",
            use_container_width=True,
        )

        if submitted:

            reference = create_civil_event(
                event_type,
                citizen_id or None,
                event_date.isoformat(),
                centre,
                document_number,
                notes,
            )

            st.success(
                f"Registration submitted: {reference}"
            )

    st.divider()

    df = fetch_dataframe(
        """
        SELECT
            reference_number AS Reference,
            event_type AS "Event Type",
            citizen_id AS "Citizen ID",
            event_date AS "Event Date",
            registration_centre AS Centre,
            status AS Status,
            created_at AS Created
        FROM civil_events
        ORDER BY created_at DESC
        """
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# IDENTITY
# ============================================================

def render_identity() -> None:

    page_header(
        "National Identity",
        "Identity lookup, document registration and verification.",
    )

    tabs = st.tabs(
        [
            "Identity Search",
            "Register Document",
        ]
    )

    with tabs[0]:

        national_id = st.text_input(
            "National ID"
        )

        if national_id:

            df = fetch_dataframe(
                """
                SELECT
                    id AS "Census ID",
                    national_id AS "National ID",
                    full_name AS "Full Name",
                    date_of_birth AS "Date of Birth",
                    gender AS Gender,
                    nationality AS Nationality,
                    state_or_region AS State,
                    verification_status AS Status
                FROM citizens
                WHERE national_id = ?
                """,
                (national_id,),
            )

            if df.empty:
                st.warning(
                    "No identity record found."
                )
            else:
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                )

    with tabs[1]:

        with st.form("document_form"):

            document_type = st.selectbox(
                "Document Type",
                IDENTIFICATION_TYPES,
            )

            citizen_id = st.text_input(
                "Citizen Census ID",
            )

            document_number = st.text_input(
                "Document Number",
            )

            uploaded = st.file_uploader(
                "Supporting File",
                type=["pdf", "png", "jpg", "jpeg"],
            )

            submitted = st.form_submit_button(
                "Register Document",
                type="primary",
            )

            if submitted:

                document_id = register_document(
                    document_type,
                    citizen_id or None,
                    document_number,
                    uploaded.name if uploaded else None,
                )

                st.success(
                    f"Document registered: {document_id}"
                )


# ============================================================
# LOCATIONS
# ============================================================

def render_locations() -> None:

    page_header(
        "Administrative Locations",
        "Manage the administrative geography used by registry records.",
    )

    tabs = st.tabs(
        [
            "States",
            "Administrative Units",
            "Population by State",
        ]
    )

    with tabs[0]:

        df = fetch_dataframe(
            """
            SELECT
                state_or_region AS State,
                COUNT(*) AS Citizens,
                COUNT(
                    DISTINCT household_id
                ) AS Households
            FROM citizens
            GROUP BY state_or_region
            ORDER BY Citizens DESC
            """
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    with tabs[1]:

        with st.form("admin_unit_form"):

            unit_type = st.selectbox(
                "Unit Type",
                [
                    "State",
                    "County",
                    "Payam",
                    "Boma",
                ],
            )

            name = st.text_input(
                "Name"
            )

            code = st.text_input(
                "Code"
            )

            state = st.selectbox(
                "State / Region",
                STATES,
            )

            administrator = st.text_input(
                "Administrator"
            )

            headquarters = st.text_input(
                "Headquarters"
            )

            submitted = st.form_submit_button(
                "Register Administrative Unit",
                type="primary",
            )

            if submitted:

                unit_id = new_id("ADM")

                with db_connection() as conn:

                    conn.execute(
                        """
                        INSERT INTO administrative_units (
                            id,
                            unit_type,
                            name,
                            code,
                            state_or_region,
                            administrator_name,
                            headquarters
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            unit_id,
                            unit_type,
                            name,
                            code,
                            state,
                            administrator,
                            headquarters,
                        ),
                    )

                audit(
                    "CREATE",
                    "Administrative Unit",
                    unit_id,
                    name,
                )

                st.success(
                    f"Administrative unit created: {unit_id}"
                )

        units = fetch_dataframe(
            """
            SELECT
                unit_type AS Type,
                name AS Name,
                code AS Code,
                state_or_region AS State,
                administrator_name AS Administrator
            FROM administrative_units
            ORDER BY unit_type, name
            """
        )

        st.dataframe(
            units,
            use_container_width=True,
            hide_index=True,
        )

    with tabs[2]:

        df = fetch_dataframe(
            """
            SELECT
                state_or_region AS State,
                COUNT(*) AS Citizens
            FROM citizens
            GROUP BY state_or_region
            ORDER BY Citizens DESC
            """
        )

        if not df.empty:

            st.bar_chart(
                df.set_index("State")
            )


# ============================================================
# DOCUMENTS
# ============================================================

def render_documents() -> None:

    page_header(
        "Document Management",
        "Registry document inventory and document status.",
    )

    df = fetch_dataframe(
        """
        SELECT
            d.id AS "Document ID",
            d.document_number AS "Document Number",
            d.document_type AS "Document Type",
            d.citizen_id AS "Citizen ID",
            d.file_name AS "File",
            d.status AS Status,
            d.created_at AS Created
        FROM documents d
        ORDER BY d.created_at DESC
        """
    )

    if df.empty:
        st.info(
            "No documents registered."
        )
    else:
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# VERIFICATION
# ============================================================

def render_verification() -> None:

    page_header(
        "Registry Verification",
        "Review and approve citizen records.",
    )

    status = st.selectbox(
        "Queue",
        VERIFICATION_STATUSES,
    )

    df = fetch_dataframe(
        """
        SELECT
            id AS "Census ID",
            national_id AS "National ID",
            full_name AS "Full Name",
            state_or_region AS State,
            county_or_payam AS County,
            verification_status AS Status,
            created_at AS Created
        FROM citizens
        WHERE verification_status = ?
        ORDER BY created_at
        """,
        (status,),
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    citizen_id = st.text_input(
        "Citizen Census ID to review"
    )

    if citizen_id:

        citizen = get_citizen(
            citizen_id
        )

        if not citizen:

            st.error(
                "Citizen not found."
            )

        else:

            st.json(citizen)

            c1, c2, c3 = st.columns(3)

            with c1:

                if st.button(
                    "Approve",
                    use_container_width=True,
                ):

                    update_citizen(
                        citizen_id,
                        {
                            "verification_status": "Verified"
                        },
                    )

                    st.success(
                        "Citizen approved."
                    )

            with c2:

                if st.button(
                    "Flag",
                    use_container_width=True,
                ):

                    update_citizen(
                        citizen_id,
                        {
                            "verification_status": "Flagged"
                        },
                    )

                    st.warning(
                        "Citizen record flagged."
                    )

            with c3:

                if st.button(
                    "Return for Review",
                    use_container_width=True,
                ):

                    update_citizen(
                        citizen_id,
                        {
                            "verification_status": "Pending Review"
                        },
                    )

                    st.info(
                        "Citizen returned to review queue."
                    )


# ============================================================
# REPORTS
# ============================================================

def render_reports() -> None:

    page_header(
        "Registry Reports",
        "Operational and population reports generated directly from the database.",
    )

    report = st.selectbox(
        "Report",
        [
            "Population by State",
            "Gender Distribution",
            "Age Distribution",
            "Verification Status",
            "Household Size",
            "Employment Status",
            "Education Level",
        ],
    )

    if report == "Population by State":

        df = fetch_dataframe(
            """
            SELECT
                state_or_region AS State,
                COUNT(*) AS Citizens
            FROM citizens
            GROUP BY state_or_region
            ORDER BY Citizens DESC
            """
        )

    elif report == "Gender Distribution":

        df = fetch_dataframe(
            """
            SELECT
                gender AS Gender,
                COUNT(*) AS Citizens
            FROM citizens
            GROUP BY gender
            """
        )

    elif report == "Age Distribution":

        df = fetch_dataframe(
            """
            SELECT
                CASE
                    WHEN age < 18 THEN '0-17'
                    WHEN age < 30 THEN '18-29'
                    WHEN age < 45 THEN '30-44'
                    WHEN age < 60 THEN '45-59'
                    ELSE '60+'
                END AS "Age Group",
                COUNT(*) AS Citizens
            FROM citizens
            GROUP BY "Age Group"
            ORDER BY
                CASE "Age Group"
                    WHEN '0-17' THEN 1
                    WHEN '18-29' THEN 2
                    WHEN '30-44' THEN 3
                    WHEN '45-59' THEN 4
                    ELSE 5
                END
            """
        )

    elif report == "Verification Status":

        df = fetch_dataframe(
            """
            SELECT
                verification_status AS Status,
                COUNT(*) AS Citizens
            FROM citizens
            GROUP BY verification_status
            """
        )

    elif report == "Household Size":

        df = fetch_dataframe(
            """
            SELECT
                household_id AS "Household ID",
                COUNT(*) AS Members
            FROM citizens
            WHERE household_id IS NOT NULL
            GROUP BY household_id
            ORDER BY Members DESC
            """
        )

    elif report == "Employment Status":

        df = fetch_dataframe(
            """
            SELECT
                employment_status AS Status,
                COUNT(*) AS Citizens
            FROM citizens
            GROUP BY employment_status
            ORDER BY Citizens DESC
            """
        )

    else:

        df = fetch_dataframe(
            """
            SELECT
                education_level AS Education,
                COUNT(*) AS Citizens
            FROM citizens
            GROUP BY education_level
            ORDER BY Citizens DESC
            """
        )

    if df.empty:

        st.info(
            "No data available for this report."
        )

    else:

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        if len(df.columns) >= 2:

            st.bar_chart(
                df.set_index(df.columns[0])
            )

        csv_data = df.to_csv(
            index=False
        )

        st.download_button(
            "Download CSV",
            csv_data,
            file_name=(
                "registry_report_"
                f"{date.today().isoformat()}.csv"
            ),
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
            <div class="ai-subtitle">
                Intelligent analysis and operational assistance
                for the South Sudan National Registry.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs(
        [
            "AI Assistant",
            "Registry Intelligence",
            "Data Quality",
        ]
    )

    with tabs[0]:

        st.subheader(
            "Registry AI Assistant"
        )

        prompt = st.chat_input(
            "Ask a question about registry operations..."
        )

        if prompt:

            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):

                st.write(
                    "The AI service layer is ready to be connected "
                    "to the registry intelligence provider. "
                    "The assistant will use database-derived "
                    "statistics rather than fabricated figures."
                )

    with tabs[1]:

        st.subheader(
            "Live Registry Intelligence"
        )

        total = citizen_count()
        verified = verified_count()
        pending = pending_count()

        verification_rate = (
            (verified / total) * 100
            if total
            else 0
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Citizens",
                f"{total:,}",
            )

        with c2:
            st.metric(
                "Verification Rate",
                f"{verification_rate:.1f}%",
            )

        with c3:
            st.metric(
                "Pending",
                f"{pending:,}",
            )

        if total:

            st.info(
                "AI insight: registry verification coverage "
                f"is currently {verification_rate:.1f}% based on "
                "persistent registry records."
            )

        else:

            st.info(
                "Register citizens first to activate "
                "database-derived registry intelligence."
            )

    with tabs[2]:

        st.subheader(
            "Data Quality"
        )

        missing_national_id = scalar(
            """
            SELECT COUNT(*)
            FROM citizens
            WHERE national_id IS NULL
               OR TRIM(national_id) = ''
            """
        )

        missing_location = scalar(
            """
            SELECT COUNT(*)
            FROM citizens
            WHERE state_or_region IS NULL
               OR TRIM(state_or_region) = ''
            """
        )

        pending = pending_count()

        quality = pd.DataFrame(
            {
                "Quality Check": [
                    "Missing National ID",
                    "Missing State / Region",
                    "Pending Verification",
                ],
                "Records": [
                    missing_national_id,
                    missing_location,
                    pending,
                ],
            }
        )

        st.dataframe(
            quality,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# ADMINISTRATION
# ============================================================

def render_administration() -> None:

    page_header(
        "Administration",
        "Registry system configuration, database status and audit history.",
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Application",
            APP_SHORT_NAME,
        )

    with c2:
        st.metric(
            "Version",
            APP_VERSION,
        )

    with c3:
        st.metric(
            "Database",
            "SQLite",
        )

    st.divider()

    st.subheader(
        "Database Location"
    )

    st.code(
        str(sqlite_path())
    )

    st.subheader(
        "Audit Log"
    )

    audit_df = fetch_dataframe(
        """
        SELECT
            created_at AS Time,
            username AS User,
            action AS Action,
            entity_type AS Type,
            entity_id AS Reference,
            details AS Details
        FROM audit_log
        ORDER BY id DESC
        LIMIT 100
        """
    )

    st.dataframe(
        audit_df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader(
        "Database Maintenance"
    )

    if st.button(
        "Refresh Database Statistics"
    ):

        st.success(
            "Database statistics refreshed."
        )

        st.rerun()


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


render_page = ROUTES.get(
    active_tab,
    render_overview,
)

render_page()


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
