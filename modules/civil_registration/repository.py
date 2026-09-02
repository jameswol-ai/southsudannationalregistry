"""
Civil Registration repository.
"""

from __future__ import annotations


class CivilRegistrationRepository:
    def __init__(
        self,
        session,
        CivilEvent,
        Document=None,
    ):
        self.session = session
        self.CivilEvent = CivilEvent
        self.Document = Document

    def list_events(self, limit=500):
        return (
            self.session.query(self.CivilEvent)
            .order_by(
                self.CivilEvent.id.desc()
            )
            .limit(limit)
            .all()
        )

    def get_event(self, event_id):
        return self.session.get(
            self.CivilEvent,
            event_id,
        )

    def add_event(self, event):
        self.session.add(event)
        self.session.flush()
        return event

    def save(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

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