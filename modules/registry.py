"""
South Sudan National Registry
Registry Module System
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


# ============================================================
# MODULE DEFINITION
# ============================================================

@dataclass
class RegistryModule:

    key: str

    label: str

    description: str

    render: Callable | None = None

    available: bool = True

    error: str | None = None


# ============================================================
# MODULE RENDERERS
# ============================================================

def render_population() -> None:

    import streamlit as st

    st.subheader(
        "Population Registry"
    )

    st.info(
        "Population registry management is ready for "
        "database integration."
    )


def render_civil_registration() -> None:

    import streamlit as st

    st.subheader(
        "Civil Registration"
    )

    st.info(
        "Birth, death, marriage and certificate "
        "registration will be managed here."
    )


def render_identity() -> None:

    import streamlit as st

    st.subheader(
        "Identity Management"
    )

    st.info(
        "National identity registration and "
        "identity services will be managed here."
    )


def render_elections() -> None:

    import streamlit as st

    st.subheader(
        "Elections"
    )

    st.info(
        "Electoral registration and voter management "
        "will be managed here."
    )


def render_reports() -> None:

    import streamlit as st

    st.subheader(
        "Reports & Analytics"
    )

    st.info(
        "Registry reports, statistics and analytics "
        "will appear here."
    )


def render_administration() -> None:

    import streamlit as st

    st.subheader(
        "Administration"
    )

    st.info(
        "Users, roles, permissions and system "
        "configuration will be managed here."
    )


# ============================================================
# MODULE REGISTRY
# ============================================================

MODULES: dict[str, RegistryModule] = {

    "population": RegistryModule(
        key="population",
        label="Population Registry",
        description=(
            "Manage national population records, "
            "households, persons and demographic information."
        ),
        render=render_population,
    ),

    "civil_registration": RegistryModule(
        key="civil_registration",
        label="Civil Registration",
        description=(
            "Register births, deaths, marriages, "
            "certificates and other civil events."
        ),
        render=render_civil_registration,
    ),

    "identity": RegistryModule(
        key="identity",
        label="Identity Management",
        description=(
            "Manage national identity registration, "
            "identification records and identity services."
        ),
        render=render_identity,
    ),

    "elections": RegistryModule(
        key="elections",
        label="Elections",
        description=(
            "Manage electoral registration, voter records "
            "and election administration."
        ),
        render=render_elections,
    ),

    "reports": RegistryModule(
        key="reports",
        label="Reports & Analytics",
        description=(
            "Generate operational reports, statistical "
            "summaries and Registry analytics."
        ),
        render=render_reports,
    ),

    "administration": RegistryModule(
        key="administration",
        label="Administration",
        description=(
            "Manage users, roles, permissions, "
            "configuration and system administration."
        ),
        render=render_administration,
    ),
}


# ============================================================
# PUBLIC API
# ============================================================

def get_module(
    key: str,
) -> RegistryModule | None:

    return MODULES.get(
        key
    )


def get_available_modules() -> list[RegistryModule]:

    return [
        module
        for module in MODULES.values()
        if module.available
    ]


def get_all_modules() -> list[RegistryModule]:

    return list(
        MODULES.values()
    )


def render_module(
    module_or_key,
) -> None:

    import streamlit as st

    # --------------------------------------------------------
    # Resolve module
    # --------------------------------------------------------

    if isinstance(
        module_or_key,
        str,
    ):

        module = get_module(
            module_or_key
        )

    else:

        module = module_or_key


    if module is None:

        st.error(
            "Registry module not found."
        )

        return


    # --------------------------------------------------------
    # Availability
    # --------------------------------------------------------

    if not module.available:

        st.error(
            "This Registry module is currently unavailable."
        )

        if module.error:

            st.code(
                module.error
            )

        return


    # --------------------------------------------------------
    # Renderer
    # --------------------------------------------------------

    if module.render is None:

        st.info(
            "This Registry module has not yet "
            "been implemented."
        )

        return


    module.render()
