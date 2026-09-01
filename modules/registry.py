"""
South Sudan National Registry
Registry Module System

Database-backed Registry modules.
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
# MODULE LOADER
# ============================================================

def _load_renderer(
    module_name: str,
    function_name: str = "render",
):
    """
    Safely import a module renderer.

    A failed module does not prevent the rest of
    the Registry from starting.
    """

    try:

        module = __import__(
            f"modules.{module_name}",
            fromlist=[function_name],
        )

        renderer = getattr(
            module,
            function_name,
        )

        if not callable(renderer):
            raise TypeError(
                f"{function_name} is not callable."
            )

        return renderer, None

    except Exception as exc:

        return (
            None,
            f"{type(exc).__name__}: {exc}",
        )


# ============================================================
# LOAD RENDERERS
# ============================================================

population_renderer, population_error = (
    _load_renderer("population")
)

civil_renderer, civil_error = (
    _load_renderer("civil_registration")
)

identity_renderer, identity_error = (
    _load_renderer("identity")
)

elections_renderer, elections_error = (
    _load_renderer("elections")
)

households_renderer, households_error = (
    _load_renderer("households")
)

documents_renderer, documents_error = (
    _load_renderer("documents")
)

reports_renderer, reports_error = (
    _load_renderer("reports")
)

administration_renderer, administration_error = (
    _load_renderer("administration")
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
        render=population_renderer,
        available=population_renderer is not None,
        error=population_error,
    ),

    "households": RegistryModule(
        key="households",
        label="Households",
        description=(
            "Manage household registration, household "
            "members and household heads."
        ),
        render=households_renderer,
        available=households_renderer is not None,
        error=households_error,
    ),

    "civil_registration": RegistryModule(
        key="civil_registration",
        label="Civil Registration",
        description=(
            "Register births, deaths, marriages and "
            "other civil events."
        ),
        render=civil_renderer,
        available=civil_renderer is not None,
        error=civil_error,
    ),

    "identity": RegistryModule(
        key="identity",
        label="Identity Management",
        description=(
            "Manage national identity information and "
            "identity verification."
        ),
        render=identity_renderer,
        available=identity_renderer is not None,
        error=identity_error,
    ),

    "elections": RegistryModule(
        key="elections",
        label="Elections",
        description=(
            "Manage voter registration, constituencies "
            "and polling station information."
        ),
        render=elections_renderer,
        available=elections_renderer is not None,
        error=elections_error,
    ),

    "documents": RegistryModule(
        key="documents",
        label="Documents",
        description=(
            "Register and manage Registry documents, "
            "certificates and official records."
        ),
        render=documents_renderer,
        available=documents_renderer is not None,
        error=documents_error,
    ),

    "reports": RegistryModule(
        key="reports",
        label="Reports & Analytics",
        description=(
            "Generate operational reports, statistical "
            "summaries and Registry analytics."
        ),
        render=reports_renderer,
        available=reports_renderer is not None,
        error=reports_error,
    ),

    "administration": RegistryModule(
        key="administration",
        label="Administration",
        description=(
            "Manage users, roles, permissions and "
            "system administration."
        ),
        render=administration_renderer,
        available=administration_renderer is not None,
        error=administration_error,
    ),
}


# ============================================================
# PUBLIC API
# ============================================================

def get_module(
    key: str,
) -> RegistryModule | None:

    return MODULES.get(key)


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

    if not module.available:

        st.error(
            "This Registry module is currently unavailable."
        )

        if module.error:

            with st.expander(
                "Technical details"
            ):

                st.code(
                    module.error
                )

        return

    if module.render is None:

        st.info(
            "This Registry module has not yet "
            "been implemented."
        )

        return

    module.render()
