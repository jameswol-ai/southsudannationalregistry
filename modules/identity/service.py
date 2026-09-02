"""
Identity Management services.
"""

from __future__ import annotations

from datetime import datetime


class IdentityValidationError(ValueError):
    pass


class IdentityService:
    def __init__(
        self,
        repository,
        Citizen,
        Document=None,
        AuditLog=None,
    ):
        self.repository = repository
        self.Citizen = Citizen
        self.Document = Document
        self.AuditLog = AuditLog

    def search_citizens(self, value):
        if not value:
            return self.repository.list_citizens()

        return self.repository.search_citizens(value)

    def get_citizen(self, citizen_id):
        return self.repository.get_citizen(citizen_id)

    def update_identity(self, citizen_id, data):
        citizen = self.get_citizen(citizen_id)

        if citizen is None:
            raise IdentityValidationError(
                "Citizen not found."
            )

        allowed = {
            c.name
            for c in citizen.__table__.columns
        }

        for key, value in data.items():
            if key in allowed and key != "id":
                setattr(citizen, key, value)

        if "updated_at" in allowed:
            citizen.updated_at = datetime.utcnow()

        self._audit(
            "UPDATE",
            "CitizenIdentity",
            citizen_id,
        )

        self.repository.save()

        return citizen

    def issue_document(self, data):
        if self.Document is None:
            raise IdentityValidationError(
                "Document model is unavailable."
            )

        document_type = str(
            data.get("document_type") or ""
        ).strip()

        if not document_type:
            raise IdentityValidationError(
                "Document type is required."
            )

        allowed = {
            c.name
            for c in self.Document.__table__.columns
        }

        clean = {
            key: value
            for key, value in data.items()
            if key in allowed
        }

        document = self.Document(**clean)

        if "created_at" in allowed:
            document.created_at = datetime.utcnow()

        self.repository.add_document(document)

        self._audit(
            "CREATE",
            "Document",
            getattr(document, "id", None),
        )

        self.repository.save()

        return document

    def _audit(self, action, entity_type, entity_id):
        if self.AuditLog is None:
            return

        try:
            columns = {
                c.name
                for c in self.AuditLog.__table__.columns
            }

            data = {}

            if "action" in columns:
                data["action"] = action

            if "entity_type" in columns:
                data["entity_type"] = entity_type

            if "entity_id" in columns:
                data["entity_id"] = str(entity_id)

            if data:
                self.repository.session.add(
                    self.AuditLog(**data)
                )

        except Exception:
            pass