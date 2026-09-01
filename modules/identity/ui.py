from __future__ import annotations

import pandas as pd
import streamlit as st

from .service import (
    create_document,
    get_identity_summary,
    list_documents,
    update_document,
)


def render() -> None:
    st.title("Identity Management")
    st.caption(
        "National identity and identity-document management."
    )

    summary = get_identity_summary()

    c1, c2, c3 = st.columns(3)

    c1.metric("Documents", summary["total"])
    c2.metric("Registered", summary["registered"])
    c3.metric("Expired", summary["expired"])

    tabs = st.tabs(
        [
            "Identity Documents",
            "Register Document",
        ]
    )

    with tabs[0]:
        _documents()

    with tabs[1]:
        _register()


def _documents() -> None:
    document_type = st.selectbox(
        "Document Type",
        [
            "",
            "National ID",
            "Passport",
            "Birth Certificate",
            "Marriage Certificate",
            "Other",
        ],
    )

    status = st.selectbox(
        "Status",
        [
            "",
            "Registered",
            "Active",
            "Expired",
            "Cancelled",
        ],
    )

    documents = list_documents(
        document_type=document_type,
        status=status,
    )

    if not documents:
        st.info("No identity documents found.")
        return

    data = pd.DataFrame(
        [
            {
                "Document Number": doc.document_number or "",
                "Type": doc.document_type,
                "Citizen ID": doc.citizen_id or "",
                "Status": doc.status,
                "Issued": doc.issued_date,
                "Expiry": doc.expiry_date,
            }
            for doc in documents
        ]
    )

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True,
    )

    selected = st.selectbox(
        "Select document",
        [doc.id for doc in documents],
        format_func=lambda value: next(
            (
                doc.document_number or doc.id
                for doc in documents
                if doc.id == value
            ),
            value,
        ),
    )

    document = next(
        doc for doc in documents
        if doc.id == selected
    )

    with st.expander("Update Document"):
        with st.form(f"edit_document_{document.id}"):

            status = st.selectbox(
                "Status",
                [
                    "Registered",
                    "Active",
                    "Expired",
                    "Cancelled",
                ],
                index=(
                    [
                        "Registered",
                        "Active",
                        "Expired",
                        "Cancelled",
                    ].index(document.status)
                    if document.status in [
                        "Registered",
                        "Active",
                        "Expired",
                        "Cancelled",
                    ]
                    else 0
                ),
            )

            submitted = st.form_submit_button(
                "Save Changes",
                type="primary",
            )

            if submitted:
                ok, message = update_document(
                    document.id,
                    {"status": status},
                )

                if ok:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)


def _register() -> None:
    st.subheader("Register Identity Document")

    with st.form("register_identity_document"):

        document_type = st.selectbox(
            "Document Type",
            [
                "National ID",
                "Passport",
                "Birth Certificate",
                "Marriage Certificate",
                "Other",
            ],
        )

        document_number = st.text_input(
            "Document Number"
        )

        citizen_id = st.text_input(
            "Citizen ID"
        )

        issued_date = st.date_input(
            "Issued Date"
        )

        expiry_date = st.date_input(
            "Expiry Date"
        )

        submitted = st.form_submit_button(
            "Register Document",
            type="primary",
        )

        if submitted:
            ok, message, _ = create_document(
                {
                    "document_type": document_type,
                    "document_number": document_number,
                    "citizen_id": citizen_id,
                    "issued_date": issued_date,
                    "expiry_date": expiry_date,
                }
            )

            if ok:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
