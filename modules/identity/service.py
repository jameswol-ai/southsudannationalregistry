from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from database.database import SessionLocal
from models import Citizen, Document


def _session():
    return SessionLocal()


def _generate_id(prefix: str) -> str:
    return f"{prefix}-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"


def get_identity_summary() -> dict[str, int]:
    db = _session()
    try:
        total = db.scalar(select(func.count(Document.id))) or 0
        registered = db.scalar(select(func.count(Document.id)).where(Document.status == "Registered")) or 0
        expired = db.scalar(select(func.count(Document.id)).where(Document.status == "Expired")) or 0
        return {"total": total, "registered": registered, "expired": expired}
    finally:
        db.close()


def list_documents(document_type: str = "", status: str = "", limit: int = 200) -> list[Document]:
    db = _session()
    try:
        stmt = select(Document).order_by(Document.created_at.desc()).limit(limit)
        if document_type:
            stmt = stmt.where(Document.document_type == document_type)
        if status:
            stmt = stmt.where(Document.status == status)
        return list(db.scalars(stmt).all())
    finally:
        db.close()


def create_document(data: dict[str, Any]) -> tuple[bool, str, str | None]:
    db = _session()
    try:
        citizen_id = data.get("citizen_id")
        if citizen_id and db.get(Citizen, citizen_id) is None:
            return False, "Citizen not found.", None
        document_id = _generate_id("DOC")
        document = Document(
            id=document_id,
            document_number=data.get("document_number") or None,
            document_type=data["document_type"],
            citizen_id=citizen_id or None,
            file_name=data.get("file_name") or None,
            file_path=data.get("file_path") or None,
            status=data.get("status") or "Registered",
            issued_date=data.get("issued_date"),
            expiry_date=data.get("expiry_date"),
        )
        db.add(document)
        db.commit()
        return True, "Identity document registered.", document_id
    except IntegrityError:
        db.rollback()
        return False, "Document information conflicts with an existing record.", None
    except Exception as exc:
        db.rollback()
        return False, f"Unable to register document: {exc}", None
    finally:
        db.close()


def update_document(document_id: str, data: dict[str, Any]) -> tuple[bool, str]:
    db = _session()
    try:
        document = db.get(Document, document_id)
        if document is None:
            return False, "Document not found."
        for key, value in data.items():
            if key in {"id", "created_at"} or not hasattr(document, key):
                continue
            setattr(document, key, value)
        if hasattr(document, "updated_at"):
            document.updated_at = datetime.utcnow()
        db.commit()
        return True, "Identity document updated."
    except Exception as exc:
        db.rollback()
        return False, f"Unable to update document: {exc}"
    finally:
        db.close()


def delete_document(document_id: str) -> tuple[bool, str]:
    db = _session()
    try:
        document = db.get(Document, document_id)
        if document is None:
            return False, "Document not found."
        db.delete(document)
        db.commit()
        return True, "Identity document deleted."
    except Exception as exc:
        db.rollback()
        return False, f"Unable to delete document: {exc}"
    finally:
        db.close()
