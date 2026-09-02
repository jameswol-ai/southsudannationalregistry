"""
Identity Management Streamlit views.
"""

from __future__ import annotations

import streamlit as st

from .repository import IdentityRepository
from .service import (
    IdentityService,
    IdentityValidationError,
)


def _get_session():
    try:
        from database import SessionLocal
        return SessionLocal()
    except ImportError:
        pass

    try:
        from db import SessionLocal
        return SessionLocal()
    except ImportError:
        pass

    raise RuntimeError(
        "Database session provider not found."
    )


def _get_models():
    from models import Citizen

    try:
        from models import Document
    except ImportError:
        Document = None

    try:
        from models import AuditLog
    except ImportError:
        AuditLog = None

    return Citizen, Document, AuditLog


def render():
    st.title("Identity Management")
    st.caption(
        "Manage citizen identity records and documents."
    )

    Citizen, Document, AuditLog = _get_models()

    session = _get_session()

    try:
        repository = IdentityRepository(
            session,
            Citizen,
            Document,
        )

        service = IdentityService(
            repository,
            Citizen,
            Document,
            AuditLog,
        )

        tabs = st.tabs(
            [
                "Identity Search",
                "Update Identity",
                "Documents",
            ]
        )

        with tabs[0]:
            search = st.text_input(
                "Search by National ID, name or phone",
                key="identity_search",
            )

            citizens = service.search_citizens(search)

            if citizens:
                st.dataframe(
                    [
                        {
                            "ID": getattr(
                                citizen,
                                "id",
                                None,
                            ),
                            "National ID": getattr(
                                citizen,
                                "national_id",
                                "",
                            ),
                            "First Name": getattr(
                                citizen,
                                "first_name",
                                "",
                            ),
                            "Last Name": getattr(
                                citizen,
                                "last_name",
                                "",
                            ),
                            "Phone": getattr(
                                citizen,
                                "phone",
                                "",
                            ),
                        }
                        for citizen in citizens
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info(
                    "No identity records found."
                )

        with tabs[1]:
            citizen_id = st.number_input(
                "Citizen ID",
                min_value=1,
                step=1,
                key="identity_citizen_id",
            )

            citizen = service.get_citizen(
                int(citizen_id)
            )

            if citizen:
                st.write(
                    f"Current National ID: "
                    f"{getattr(citizen, 'national_id', '')}"
                )

                with st.form("identity_update_form"):
                    national_id = st.text_input(
                        "National ID",
                        value=getattr(
                            citizen,
                            "national_id",
                            "",
                        )
                        or "",
                    )

                    first_name = st.text_input(
                        "First name",
                        value=getattr(
                            citizen,
                            "first_name",
                            "",
                        )
                        or "",
                    )

                    last_name = st.text_input(
                        "Last name",
                        value=getattr(
                            citizen,
                            "last_name",
                            "",
                        )
                        or "",
                    )

                    submitted = st.form_submit_button(
                        "Update Identity",
                        type="primary",
                    )

                if submitted:
                    try:
                        service.update_identity(
                            int(citizen_id),
                            {
                                "national_id": national_id,
                                "first_name": first_name,
                                "last_name": last_name,
                            },
                        )

                        st.success(
                            "Identity record updated."
                        )
                        st.rerun()

                    except IdentityValidationError as exc:
                        session.rollback()
                        st.error(str(exc))

                    except Exception as exc:
                        session.rollback()
                        st.exception(exc)

            else:
                st.info(
                    "Citizen record not found."
                )

        with tabs[2]:
            documents = repository.list_documents()

            if documents:
                st.dataframe(
                    [
                        {
                            column.name: getattr(
                                document,
                                column.name,
                                None,
                            )
                            for column in document.__table__.columns
                        }
                        for document in documents
                    ],
                    use_container_width=True,
                    hide_index=True,
                )

            with st.expander("Issue Identity Document"):
                with st.form("issue_document_form"):
                    document_type = st.selectbox(
                        "Document type",
                        [
                            "National ID",
                            "Birth Certificate",
                            "Death Certificate",
                            "Other",
                        ],
                    )

                    document_number = st.text_input(
                        "Document number"
                    )

                    document_citizen_id = st.number_input(
                        "Citizen ID",
                        min_value=1,
                        step=1,
                    )

                    submitted = st.form_submit_button(
                        "Issue Document"
                    )

                if submitted:
                    try:
                        document = service.issue_document(
                            {
                                "document_type": document_type,
                                "document_number": document_number,
                                "citizen_id": document_citizen_id,
                            }
                        )

                        st.success(
                            f"Document issued. "
                            f"Record #{getattr(document, 'id', '')}"
                        )

                    except IdentityValidationError as exc:
                        session.rollback()
                        st.error(str(exc))

                    except Exception as exc:
                        session.rollback()
                        st.exception(exc)

    finally:
        session.close()