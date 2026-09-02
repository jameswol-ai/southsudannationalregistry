from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from database.models import (
    CivilEvent,
    Citizen,
)


class CivilRegistrationRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def get_event(
        self,
        event_id: str,
    ) -> CivilEvent | None:

        return (
            self.db.query(CivilEvent)
            .filter(
                CivilEvent.id == event_id
            )
            .first()
        )

    def list_events(
        self,
        event_type: str | None = None,
        citizen_id: str | None = None,
        limit: int = 500,
    ) -> list[CivilEvent]:

        query = self.db.query(
            CivilEvent
        )

        if event_type:
            query = query.filter(
                CivilEvent.event_type
                == event_type
            )

        if citizen_id:
            query = query.filter(
                CivilEvent.citizen_id
                == citizen_id
            )

        return (
            query
            .order_by(
                CivilEvent.event_date.desc()
            )
            .limit(limit)
            .all()
        )

    def count_events(
        self,
        event_type: str | None = None,
    ) -> int:

        query = self.db.query(
            func.count(CivilEvent.id)
        )

        if event_type:
            query = query.filter(
                CivilEvent.event_type
                == event_type
            )

        return int(
            query.scalar() or 0
        )

    def add_event(
        self,
        event: CivilEvent,
    ) -> CivilEvent:

        self.db.add(event)
        self.db.flush()

        return event