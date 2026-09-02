from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from .service import (
    create_document,
    delete_document,
    get_identity_summary,
    list_documents,
    update_document,
)

DOCUMENT_TYPES = ["National ID", "Passport", "Birth Certificate", "Marriage Certificate", "Other"]
STATUSES = ["Registered", "Active", "Expired", "Cancelled"]


def render() -> None:
    st.title("Identity Management")
    st.caption("National identity and identity-document management.")
    summary = get_identity_summary()
    c1, c2, c3 = st.columns(3)
    c1.metric("Documents", summary["total"])
    c2.metric("Registered", summary["registered"])
    c3.metric("Expired", summary["expired"])

    tabs = st.tabs(["Identity Documents", "Register Document"])
    with tabs[0]:
        _documents()
    with tabs[1]:
        _register()


def _documents() -> None:
    c1, c2 = st.columns(2)
    with c1:
        document_type_filter = st.selectbox("Document Type", [""] + DOCUMENT_TYPES, key="identity_type_filter")
    with c2:
        status_filter = st.selectbox("Status", [""] + STATUSES, key="identity_status_filter")

    documents = list_documents(document_type=document_type_filter, status=status_filter)
    if not documents:
        st.info("No identity documents found.")
        return

    st.dataframe(pd.DataFrame([
        {"ID": doc.id, "Document Number": doc.document_number or "", "Type": doc.document_type,
         "Citizen ID": doc.citizen_id or "", "Status": doc.status, "Issued": doc.issued_date,
         "Expiry": doc.expiry_date}
        for doc in documents
    ]), use_container_width=True, hide_index=True)

    selected_id = st.selectbox(
        "Select document",
        [doc.id for doc in documents],
        format_func=lambda value: next((doc.document_number or doc.id for doc in documents if doc.id == value), value),
        key="identity_selected_document",
    )
    document = next(doc for doc in documents if doc.id == selected_id)

    with st.expander("Edit Identity Document", expanded=True):
        with st.form(f"edit_identity_document_{document.id}"):
            document_type = st.selectbox("Document Type", DOCUMENT_TYPES, index=DOCUMENT_TYPES.index(document.document_type) if document.document_type in DOCUMENT_TYPES else 0)
            document_number = st.text_input("Document Number", value=document.document_number or "")
            citizen_id = st.text_input("Citizen ID", value=document.citizen_id or "")
            status = st.selectbox("Status", STATUSES, index=STATUSES.index(document.status) if document.status in STATUSES else 0)
            issued_date = st.date_input("Issued Date", value=document.issued_date or date.today())
            expiry_date = st.date_input("Expiry Date", value=document.expiry_date or date.today())
            save = st.form_submit_button("Save Changes", type="primary")
        if save:
            ok, message = update_document(document.id, {
                "document_type": document_type,
                "document_number": document_number.strip() or None,
                "citizen_id": citizen_id.strip() or None,
                "status": status,
                "issued_date": issued_date,
                "expiry_date": expiry_date,
            })
            if ok:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with st.expander("Delete Identity Document"):
        st.warning("This permanently deletes the selected identity document record.")
        confirm = st.checkbox("Confirm permanent deletion", key=f"confirm_delete_document_{document.id}")
        if st.button("Delete Document", disabled=not confirm, key=f"delete_document_{document.id}"):
            ok, message = delete_document(document.id)
            if ok:
                st.success(message)
                st.rerun()
            else:
                st.error(message)


def _register() -> None:
    st.subheader("Register Identity Document")
    with st.form("register_identity_document"):
        document_type = st.selectbox("Document Type", DOCUMENT_TYPES)
        document_number = st.text_input("Document Number")
        citizen_id = st.text_input("Citizen ID")
        issued_date = st.date_input("Issued Date", value=date.today())
        expiry_date = st.date_input("Expiry Date", value=date.today())
        status = st.selectbox("Initial Status", STATUSES, index=0)
        submitted = st.form_submit_button("Register Document", type="primary")

    if submitted:
        ok, message, _ = create_document({
            "document_type": document_type,
            "document_number": document_number.strip() or None,
            "citizen_id": citizen_id.strip() or None,
            "issued_date": issued_date,
            "expiry_date": expiry_date,
            "status": status,
        })
        if ok:
            st.success(message)
            st.rerun()
        else:
            st.error(message)
