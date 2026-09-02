"""
Shared database helpers for registry modules.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from database.database import get_session


@contextmanager
def module_session() -> Generator[
    Session,
    None,
    None,
]:
    """
    Provide a safe database session to modules.

    Automatically closes the session.
    """

    db = get_session()

    try:
        yield db

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()