from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select

from database.database import SessionLocal
from models import AuditLog


def create_audit_log(
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    username: str = "system",
    details: Optional[str] = None,
) -> bool:
    db = SessionLocal()

    try:
        log = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            username=username,
            details=details,
            created_at=datetime.utcnow(),
        )

        db.add(log)
        db.commit()

        return True

    except Exception:
        db.rollback()
        return False

    finally:
        db.close()


def list_audit_logs(
    username: str = "",
    action: str = "",
    limit: int = 200,
) -> list[AuditLog]:
    db = SessionLocal()

    try:
        stmt = (
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )

        if username:
            stmt = stmt.where(
                AuditLog.username == username
            )

        if action:
            stmt = stmt.where(
                AuditLog.action == action
            )

        return list(
            db.scalars(stmt).all()
        )

    finally:
        db.close()


def get_audit_actions() -> list[str]:
    db = SessionLocal()

    try:
        rows = db.execute(
            select(AuditLog.action)
            .distinct()
            .order_by(AuditLog.action)
        ).all()

        return [
            row[0]
            for row in rows
            if row[0]
        ]

    finally:
        db.close()
