from __future__ import annotations

import pandas as pd
import streamlit as st

from database.database import (
    check_database_health,
    database_backend,
    database_url_configured,
    IS_POSTGRESQL,
)

from .service import (
    get_audit_actions,
    list_audit_logs,
)


def render() -> None:
    st.title("Administration")
    st.caption(
        "System administration, database status, configuration and audit monitoring."
    )

    tabs = st.tabs(
        [
            "Audit Logs",
            "Database",
            "System Information",
        ]
    )

    with tabs[0]:
        _audit_logs()

    with tabs[1]:
        _database_status()

    with tabs[2]:
        _system_information()


def _audit_logs() -> None:
    st.subheader("Audit Logs")

    actions = [""] + get_audit_actions()

    action = st.selectbox(
        "Action",
        actions,
    )

    username = st.text_input(
        "Username"
    )

    logs = list_audit_logs(
        username=username,
        action=action,
    )

    if not logs:
        st.info("No audit logs found.")
        return

    data = pd.DataFrame(
        [
            {
                "Date": log.created_at,
                "Username": log.username,
                "Action": log.action,
                "Entity": log.entity_type,
                "Entity ID": log.entity_id or "",
                "Details": log.details or "",
            }
            for log in logs
        ]
    )

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True,
    )


def _database_status() -> None:
    st.subheader("Database Status")
    st.caption("Live connectivity check for the registry database.")

    status = check_database_health()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Connection",
            "Healthy" if status["ok"] else "Unavailable",
        )

    with col2:
        st.metric(
            "Backend",
            "Neon PostgreSQL" if IS_POSTGRESQL else database_backend(),
        )

    with col3:
        st.metric(
            "Production URL",
            "Configured" if database_url_configured() else "Not configured",
        )

    if status["ok"]:
        st.success(status["message"])
    else:
        st.error(status["message"])

    st.info(
        "Production deployments should use Neon PostgreSQL through the "
        "DATABASE_URL secret. SQLite is retained for local development."
    )


def _system_information() -> None:
    st.subheader("System Information")

    st.info(
        "User management, roles and permissions can be "
        "connected here when the corresponding authentication "
        "models are introduced."
    )

    st.write(
        {
            "Application": "South Sudan National Registry",
            "Architecture": "Streamlit + SQLAlchemy",
            "Database Layer": database_backend(),
            "Audit Logging": "Enabled",
            "Database Health Check": "Enabled",
            "Production Database": "Neon PostgreSQL"
            if IS_POSTGRESQL
            else "Not configured; using local SQLite",
        }
    )
