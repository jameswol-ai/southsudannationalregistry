"""
Identity module.

Provides identity document registration and lookup.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from database.database import SessionLocal
from services.identity_service import (
    create_document,
    list_documents,
)


DOCUMENT_TYPES = [
    "National ID",
    "Passport",
    "Birth Certificate",
    "Death Certificate",
    "Marriage Certificate",
    "Divorce Certificate",
    "Other",
]


def render() -> None:

    st.title("Identity")

    st.caption(
        "Manage citizen identity records and identity documents."
    )

    tab_register, tab_search, tab_records = st.tabs(
        [
            "Register Document",
            "Citizen Documents",
            "All Documents",
        ]
    )

    # ========================================================
    # REGISTER
    # ========================================================

    with tab_register:

        st.subheader("Register Identity Document")

        with st.form("identity_document_form"):

            citizen_id = st.text_input(
                "Citizen ID *"
            )

            document_type = st.selectbox(
                "Document Type",
                DOCUMENT_TYPES,
            )

            document_number = st.text_input(
                "Document Number"
            )

            file_name = st.text_input(
                "File / Scan Reference"
            )

            status = st.selectbox(
                "Status",
                [
                    "Registered",
                    "Pending Verification",
                    "Verified",
                    "Expired",
                    "Cancelled",
                ],
            )

            submitted = st.form_submit_button(
                "Register Document",
                type="primary",
            )

        if submitted:

            if not citizen_id.strip():

                st.error(
                    "Citizen ID is required."
                )

            else:

                db = SessionLocal()

                try:

                    document = create_document(
                        db=db,
                        data={
                            "citizen_id":
                                citizen_id.strip(),
                            "document_type":
                                document_type,
                            "document_number":
                                document_number.strip()
                                or None,
                            "file_name":
                                file_name.strip()
                                or None,
                            "status":
                                status,
                        },
                        username="streamlit",
                    )

                    st.success(
                        f"Document registered: "
                        f"{document.id}"
                    )

                except Exception as exc:

                    db.rollback()

                    st.error(
                        f"Document registration failed: {exc}"
                    )

                finally:

                    db.close()

    # ========================================================
    # CITIZEN SEARCH
    # ========================================================

    with tab_search:

        st.subheader("Citizen Documents")

        citizen_id = st.text_input(
            "Citizen ID",
            key="identity_citizen_id",
        )

        if citizen_id.strip():

            db = SessionLocal()

            try:

                documents = list_documents(
                    db=db,
                    citizen_id=citizen_id.strip(),
                    limit=200,
                )

            finally:

                db.close()

            if documents:

                st.dataframe(
                    pd.DataFrame(
                        [
                            {
                                "Document ID":
                                    document.id,
                                "Type":
                                    document.document_type,
                                "Number":
                                    document.document_number
                                    or "",
                                "Status":
                                    document.status,
                                "Created":
                                    document.created_at,
                            }
                            for document in documents
                        ]
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.info(
                    "No documents found for this citizen."
                )

    # ========================================================
    # ALL DOCUMENTS
    # ========================================================

    with tab_records:

        st.subheader("Identity Documents")

        db = SessionLocal()

        try:

            documents = list_documents(
                db=db,
                limit=500,
            )

        finally:

            db.close()

        if documents:

            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Document ID":
                                document.id,
                            "Citizen ID":
                                document.citizen_id or "",
                            "Type":
                                document.document_type,
                            "Number":
                                document.document_number or "",
                            "Status":
                                document.status,
                            "Created":
                                document.created_at,
                        }
                        for document in documents
                    ]
                ),
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "No identity documents have been registered."
          )
