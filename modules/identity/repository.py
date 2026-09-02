from __future__ import annotations

from sqlalchemy.orm import Session

from database.models import (
    Citizen,
    Document,
)


class IdentityRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def get_citizen(
        self,
        citizen_id: str,
    ) -> Citizen | None:

        return (
            self.db.query(Citizen)
            .filter(
                Citizen.id == citizen_id
            )
            .first()
        )

    def get_document(
        self,
        document_id: str,
    ) -> Document | None:

        return (
            self.db.query(Document)
            .filter(
                Document.id == document_id
            )
            .first()
        )

    def list_documents(
        self,
        citizen_id: str | None = None,
        limit: int = 500,
    ) -> list[Document]:

        query = self.db.query(
            Document
        )

        if citizen_id:
            query = query.filter(
                Document.citizen_id
                == citizen_id
            )

        return (
            query
            .order_by(
                Document.created_at.desc()
            )
            .limit(limit)
            .all()
        )

    def add_document(
        self,
        document: Document,
    ) -> Document:

        self.db.add(document)
        self.db.flush()

        return document