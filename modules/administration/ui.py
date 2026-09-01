from __future__ import annotations

import pandas as pd
import streamlit as st

from .service import (
    get_audit_actions,
    list_audit_logs,
)


def render() -> None:
    st.title("Administration")
    st.caption(
        "System administration, configuration and audit monitoring."
    )

    tabs = st.tabs(
        [
            "Audit Logs",
            "System Information",
        ]
    )

    with tabs[0]:
        _audit_logs()

    with tabs[1]:
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
            "Database Layer": "PostgreSQL / SQLite compatible",
            "Audit Logging": "Enabled",
        }
    )
