"""
Identity and document service.

Manages identity documents associated with citizens.
"""

from __future__ import annotations

from typing import Any, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from database.models import AuditLog, Document


def _generate_id() -> str:
    return f"DOC-{uuid4().hex[:12].upper()}"


def _audit(db: Session, action: str, entity_id: str, username: str = "system", details: Optional[str] = None) -> None:
    db.add(AuditLog(action=action, entity_type="Document", entity_id=entity_id, username=username, details=details))


def create_document(db: Session, data: dict[str, Any], username: str = "system") -> Document:
    document = Document(id=data.get("id") or _generate_id(), **{key: value for key, value in data.items() if key != "id"})
    db.add(document)
    db.flush()
    _audit(db, "CREATE", document.id, username, f"Identity document created: {document.document_type}")
    db.commit()
    db.refresh(document)
    return document


def get_document(db: Session, document_id: str) -> Optional[Document]:
    return db.query(Document).filter(Document.id == document_id).first()


def list_documents(db: Session, citizen_id: Optional[str] = None, document_type: Optional[str] = None, limit: int = 100, offset: int = 0) -> list[Document]:
    query = db.query(Document)
    if citizen_id:
        query = query.filter(Document.citizen_id == citizen_id)
    if document_type:
        query = query.filter(Document.document_type == document_type)
    return query.order_by(Document.created_at.desc()).offset(offset).limit(limit).all()


def update_document(db: Session, document_id: str, data: dict[str, Any], username: str = "system") -> Document:
    document = get_document(db, document_id)
    if not document:
        raise ValueError("Identity document was not found.")
    for key, value in data.items():
        if key in {"id", "created_at"} or not hasattr(document, key):
            continue
        setattr(document, key, value)
    if hasattr(document, "updated_at"):
        from datetime import datetime
        document.updated_at = datetime.utcnow()
    _audit(db, "UPDATE", document.id, username, f"Identity document updated: {document.document_type}")
    db.commit()
    db.refresh(document)
    return document


def delete_document(db: Session, document_id: str, username: str = "system") -> bool:
    document = get_document(db, document_id)
    if not document:
        return False
    entity_id = document.id
    document_type = document.document_type
    _audit(db, "DELETE", entity_id, username, f"Identity document deleted: {document_type}")
    db.delete(document)
    db.commit()
    return True
