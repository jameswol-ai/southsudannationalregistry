from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlalchemy import func, select

from database.database import SessionLocal
from models import (
    Citizen,
    CivilEvent,
    Document,
    Household,
    VoterRecord,
)


def render() -> None:
    st.title("Reports & Analytics")
    st.caption(
        "National Registry operational statistics and analytics."
    )

    _overview()
    st.divider()
    _population_report()
    st.divider()
    _civil_report()
    st.divider()
    _election_report()


def _overview() -> None:
    db = SessionLocal()

    try:
        values = {
            "Citizens": db.scalar(
                select(func.count(Citizen.id))
            ) or 0,
            "Households": db.scalar(
                select(func.count(Household.id))
            ) or 0,
            "Civil Events": db.scalar(
                select(func.count(CivilEvent.id))
            ) or 0,
            "Identity Documents": db.scalar(
                select(func.count(Document.id))
            ) or 0,
            "Voters": db.scalar(
                select(func.count(VoterRecord.id))
            ) or 0,
        }

    finally:
        db.close()

    columns = st.columns(5)

    for column, (label, value) in zip(
        columns,
        values.items(),
    ):
        column.metric(label, value)


def _population_report() -> None:
    st.subheader("Population Report")

    db = SessionLocal()

    try:
        rows = db.execute(
            select(
                Citizen.state_or_region,
                func.count(Citizen.id).label("population"),
            )
            .group_by(Citizen.state_or_region)
            .order_by(
                func.count(Citizen.id).desc()
            )
        ).all()

    finally:
        db.close()

    if not rows:
        st.info("No population data available.")
        return

    df = pd.DataFrame(
        [
            {
                "State / Region": row[0] or "Unspecified",
                "Population": row[1],
            }
            for row in rows
        ]
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.bar_chart(
        df.set_index("State / Region")
    )


def _civil_report() -> None:
    st.subheader("Civil Registration Report")

    db = SessionLocal()

    try:
        rows = db.execute(
            select(
                CivilEvent.event_type,
                func.count(CivilEvent.id).label("total"),
            )
            .group_by(CivilEvent.event_type)
            .order_by(
                func.count(CivilEvent.id).desc()
            )
        ).all()

    finally:
        db.close()

    if not rows:
        st.info("No civil registration data available.")
        return

    df = pd.DataFrame(
        [
            {
                "Event Type": row[0],
                "Total": row[1],
            }
            for row in rows
        ]
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.bar_chart(
        df.set_index("Event Type")
    )


def _election_report() -> None:
    st.subheader("Election Report")

    db = SessionLocal()

    try:
        rows = db.execute(
            select(
                VoterRecord.constituency,
                func.count(VoterRecord.id).label("voters"),
            )
            .group_by(VoterRecord.constituency)
            .order_by(
                func.count(VoterRecord.id).desc()
            )
        ).all()

    finally:
        db.close()

    if not rows:
        st.info("No voter data available.")
        return

    df = pd.DataFrame(
        [
            {
                "Constituency": row[0] or "Unspecified",
                "Voters": row[1],
            }
            for row in rows
        ]
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.bar_chart(
        df.set_index("Constituency")
    )
