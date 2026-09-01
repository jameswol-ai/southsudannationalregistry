"""
AI Studio module.

AI orchestration is intentionally separated from the registry
database. This module provides the Streamlit interface that can
later consume the Registry API / AI service.
"""

from __future__ import annotations

import streamlit as st

from database.database import SessionLocal
from services.reporting_service import get_dashboard_summary


def render() -> None:

    st.title("AI Studio")

    st.caption(
        "AI-assisted analysis and operational intelligence "
        "for the South Sudan National Registry."
    )

    st.info(
        "AI Studio is connected to the registry dashboard layer. "
        "The production AI provider will be connected through "
        "the Registry API rather than storing AI credentials in Streamlit."
    )

    # ========================================================
    # REGISTRY CONTEXT
    # ========================================================

    db = SessionLocal()

    try:

        summary = get_dashboard_summary(db)

    finally:

        db.close()

    st.subheader("Registry Context")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Citizens",
            f"{summary['total_citizens']:,}",
        )

    with col2:

        st.metric(
            "Households",
            f"{summary['total_households']:,}",
        )

    with col3:

        st.metric(
            "Civil Events",
            f"{summary['total_civil_events']:,}",
        )

    st.divider()

    # ========================================================
    # ASSISTANT
    # ========================================================

    st.subheader("Registry Assistant")

    prompt = st.text_area(
        "Ask a registry question",
        placeholder=(
            "Example: Summarize the current verification workload."
        ),
    )

    if st.button(
        "Analyze",
        type="primary",
    ):

        if not prompt.strip():

            st.warning(
                "Enter a question first."
            )

        else:

            st.session_state[
                "ai_last_prompt"
            ] = prompt.strip()

            st.info(
                "AI request prepared. "
                "Connect this interface to the Registry API "
                "and AI provider for production inference."
            )

            st.write(
                "**Requested analysis:**"
            )

            st.write(
                prompt.strip()
            )

    # ========================================================
    # FUTURE AI FUNCTIONS
    # ========================================================

    st.divider()

    st.subheader("Planned AI Capabilities")

    capabilities = [
        "Natural-language registry search",
        "Citizen record summarization",
        "Verification prioritization",
        "Data-quality anomaly detection",
        "Population analytics",
        "Civil registration trend analysis",
        "Operational reporting",
        "Administrative decision support",
    ]

    for capability in capabilities:

        st.write(
            f"• {capability}"
        )
