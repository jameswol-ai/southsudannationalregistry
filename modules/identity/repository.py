"""
Identity repository.
"""

from __future__ import annotations

from sqlalchemy import or_


class IdentityRepository:
    def __init__(
        self,
        session,
        Citizen,
        Document=None,
    ):
        self.session = session
        self.Citizen = Citizen
        self.Document = Document

    def list_citizens(self, limit=500):
        return (
            self.session.query(self.Citizen)
            .order_by(
                self.Citizen.id.desc()
            )
            .limit(limit)
            .all()
        )

    def search_citizens(self, value, limit=100):
        query = self.session.query(self.Citizen)

        filters = []

        for field in (
            "national_id",
            "first_name",
            "last_name",
            "phone",
        ):
            if hasattr(self.Citizen, field):
                filters.append(
                    getattr(self.Citizen, field).ilike(
                        f"%{value}%"
                    )
                )

        if filters:
            query = query.filter(or_(*filters))

        return (
            query.order_by(
                self.Citizen.id.desc()
            )
            .limit(limit)
            .all()
        )

    def get_citizen(self, citizen_id):
        return self.session.get(
            self.Citizen,
            citizen_id,
        )

    def list_documents(self, limit=500):
        if self.Document is None:
            return []

        return (
            self.session.query(self.Document)
            .order_by(
                self.Document.id.desc()
            )
            .limit(limit)
            .all()
        )

    def add_document(self, document):
        self.session.add(document)
        self.session.flush()
        return document

    def save(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()