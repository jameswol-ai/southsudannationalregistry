"""
Administration module.

Provides system information and audit-log visibility.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from database.database import SessionLocal
from database.models import AuditLog
from database.database import DATABASE_URL


def render() -> None:

    st.title("Administration")

    st.caption(
        "System administration, database status and audit activity."
    )

    # ========================================================
    # SYSTEM STATUS
    # ========================================================

    st.subheader("System Status")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Application",
            "Operational",
        )

    with col2:

        if DATABASE_URL.startswith("postgresql"):

            database_type = "PostgreSQL"

        elif DATABASE_URL.startswith("sqlite"):

            database_type = "SQLite"

        else:

            database_type = "Configured Database"

        st.metric(
            "Database",
            database_type,
        )

    st.code(
        DATABASE_URL.split("@")[-1]
        if "@" in DATABASE_URL
        else DATABASE_URL
    )

    st.divider()

    # ========================================================
    # AUDIT LOG
    # ========================================================

    st.subheader("Audit Log")

    db = SessionLocal()

    try:

        logs = (
            db.query(AuditLog)
            .order_by(
                AuditLog.created_at.desc()
            )
            .limit(500)
            .all()
        )

    finally:

        db.close()

    if logs:

        df = pd.DataFrame(
            [
                {
                    "Time":
                        log.created_at,
                    "Action":
                        log.action,
                    "Entity":
                        log.entity_type,
                    "Entity ID":
                        log.entity_id or "",
                    "User":
                        log.username,
                    "Details":
                        log.details or "",
                }
                for log in logs
            ]
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No audit events have been recorded yet."
        )
