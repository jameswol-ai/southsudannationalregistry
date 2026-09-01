"""
South Sudan National Registry
Service layer.

The service layer contains business operations that are shared by:

    - Streamlit AI Studio
    - Registry API
    - Next.js AI Studio

UI and API code should call these services rather than manipulating
SQLAlchemy models directly.
"""

from .citizen_service import (
    create_citizen,
    delete_citizen,
    get_citizen,
    list_citizens,
    search_citizens,
    update_citizen,
)

from .household_service import (
    create_household,
    delete_household,
    get_household,
    list_households,
    update_household,
)

from .registration_service import (
    create_civil_event,
    get_civil_event,
    list_civil_events,
    update_civil_event,
)

from .identity_service import (
    create_document,
    get_document,
    list_documents,
    update_document,
)

from .verification_service import (
    get_verification_queue,
    verify_citizen,
    reject_citizen,
)

from .reporting_service import (
    get_dashboard_summary,
    get_citizen_statistics,
    get_household_statistics,
    get_civil_registration_statistics,
    get_verification_statistics,
)

__all__ = [
    "create_citizen",
    "delete_citizen",
    "get_citizen",
    "list_citizens",
    "search_citizens",
    "update_citizen",
    "create_household",
    "delete_household",
    "get_household",
    "list_households",
    "update_household",
    "create_civil_event",
    "get_civil_event",
    "list_civil_events",
    "update_civil_event",
    "create_document",
    "get_document",
    "list_documents",
    "update_document",
    "get_verification_queue",
    "verify_citizen",
    "reject_citizen",
    "get_dashboard_summary",
    "get_citizen_statistics",
    "get_household_statistics",
    "get_civil_registration_statistics",
    "get_verification_statistics",
]
