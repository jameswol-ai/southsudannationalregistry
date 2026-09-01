"""
Documents module.

Central document register for the national registry.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from database.database import SessionLocal
from services.identity_service import list_documents


def render() -> None:

    st.title("Documents")

    st.caption(
        "Central registry document repository and document status."
    )

    db = SessionLocal()

    try:

        documents = list_documents(
            db=db,
            limit=1000,
        )

    finally:

        db.close()

    if not documents:

        st.info(
            "No documents are currently registered."
        )

        return

    rows = [
        {
            "Document ID":
                document.id,
            "Citizen ID":
                document.citizen_id or "",
            "Document Number":
                document.document_number or "",
            "Document Type":
                document.document_type,
            "File Reference":
                document.file_name or "",
            "Status":
                document.status,
            "Created":
                document.created_at,
        }
        for document in documents
    ]

    df = pd.DataFrame(rows)

    # ========================================================
    # SUMMARY
    # ========================================================

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Documents",
            f"{len(df):,}",
        )

    with col2:

        verified = (
            df["Status"]
            .eq("Verified")
            .sum()
        )

        st.metric(
            "Verified",
            f"{verified:,}",
        )

    with col3:

        pending = (
            df["Status"]
            .eq("Pending Verification")
            .sum()
        )

        st.metric(
            "Pending Verification",
            f"{pending:,}",
        )

    st.divider()

    # ========================================================
    # FILTER
    # ========================================================

    status_filter = st.selectbox(
        "Status",
        [
            "All",
            *sorted(
                df["Status"]
                .dropna()
                .unique()
                .tolist()
            ),
        ],
    )

    if status_filter != "All":

        df = df[
            df["Status"]
            == status_filter
        ]

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )
