"""
Identity and document service.

Manages identity documents associated with citizens.
"""

from __future__ import annotations

from typing import Any, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from database.models import AuditLog, Document


# ============================================================
# HELPERS
# ============================================================

def _generate_id() -> str:
    return f"DOC-{uuid4().hex[:12].upper()}"


def _audit(
    db: Session,
    action: str,
    entity_id: str,
    username: str = "system",
    details: Optional[str] = None,
) -> None:

    db.add(
        AuditLog(
            action=action,
            entity_type="Document",
            entity_id=entity_id,
            username=username,
            details=details,
        )
    )


# ============================================================
# CREATE
# ============================================================

def create_document(
    db: Session,
    data: dict[str, Any],
    username: str = "system",
) -> Document:

    document = Document(
        id=data.get("id") or _generate_id(),
        **{
            key: value
            for key, value in data.items()
            if key != "id"
        },
    )

    db.add(document)

    db.flush()

    _audit(
        db=db,
        action="CREATE",
        entity_id=document.id,
        username=username,
        details=(
            f"Identity document created: "
            f"{document.document_type}"
        ),
    )

    db.commit()

    db.refresh(document)

    return document


# ============================================================
# GET
# ============================================================

def get_document(
    db: Session,
    document_id: str,
) -> Optional[Document]:

    return (
        db.query(Document)
        .filter(
            Document.id == document_id,
        )
        .first()
    )


# ============================================================
# LIST
# ============================================================

def list_documents(
    db: Session,
    citizen_id: Optional[str] = None,
    document_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Document]:

    query = db.query(Document)

    if citizen_id:
        query = query.filter(
            Document.citizen_id
            == citizen_id,
        )

    if document_type:
        query = query.filter(
            Document.document_type
            == document_type,
        )

    return (
        query
        .order_by(
            Document.created_at.desc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )


# ============================================================
# UPDATE
# ============================================================

def update_document(
    db: Session,
    document_id: str,
    data: dict[str, Any],
    username: str = "system",
) -> Document:

    document = get_document(
        db=db,
        document_id=document_id,
    )

    if not document:
        raise ValueError(
            "Identity document was not found."
        )

    protected_fields = {
        "id",
        "created_at",
    }

    for key, value in data.items():

        if key in protected_fields:
            continue

        if not hasattr(document, key):
            continue

        setattr(
            document,
            key,
            value,
        )

    _audit(
        db=db,
        action="UPDATE",
        entity_id=document.id,
        username=username,
        details=(
            f"Identity document updated: "
            f"{document.document_type}"
        ),
    )

    db.commit()

    db.refresh(document)

    return document
