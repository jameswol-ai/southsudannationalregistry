"""
South Sudan National Registry
Registry Module System
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class RegistryModule:
    key: str
    label: str
    description: str
    render: Callable | None = None
    available: bool = True
    error: str | None = None


# ============================================================
# MODULE LOADING
# ============================================================

def _load_population():
    from modules.population import render
    return render


def _load_civil_registration():
    from modules.civil_registration import render
    return render


def _load_identity():
    from modules.identity import render
    return render


def _load_elections():
    from modules.elections import render
    return render


def _load_reports():
    from modules.reports import render
    return render


def _load_administration():
    from modules.administration import render
    return render


# ============================================================
# REGISTRY
# ============================================================

MODULES: dict[str, RegistryModule] = {}


def _register(
    key: str,
    label: str,
    description: str,
    loader: Callable,
) -> None:

    try:
        renderer = loader()

        MODULES[key] = RegistryModule(
            key=key,
            label=label,
            description=description,
            render=renderer,
            available=True,
        )

    except Exception as exc:

        MODULES[key] = RegistryModule(
            key=key,
            label=label,
            description=description,
            render=None,
            available=False,
            error=str(exc),
        )


_register(
    "population",
    "Population Registry",
    (
        "Manage national population records, "
        "citizens, households and demographic information."
    ),
    _load_population,
)

_register(
    "civil_registration",
    "Civil Registration",
    (
        "Register births, deaths, marriages, "
        "divorces and other civil events."
    ),
    _load_civil_registration,
)

_register(
    "identity",
    "Identity Management",
    (
        "Manage national identity records, "
        "passports and identity documents."
    ),
    _load_identity,
)

_register(
    "elections",
    "Elections",
    (
        "Manage voter registration, "
        "constituencies and polling stations."
    ),
    _load_elections,
)

_register(
    "reports",
    "Reports & Analytics",
    (
        "Generate operational, demographic, "
        "civil registration and election reports."
    ),
    _load_reports,
)

_register(
    "administration",
    "Administration",
    (
        "Manage system administration, "
        "audit monitoring and configuration."
    ),
    _load_administration,
)


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

    return list(MODULES.values())


def render_module(
    module_or_key,
) -> None:

    import streamlit as st

    if isinstance(module_or_key, str):
        module = get_module(module_or_key)
    else:
        module = module_or_key

    if module is None:
        st.error("Registry module not found.")
        return

    if not module.available:
        st.error(
            f"{module.label} is currently unavailable."
        )

        if module.error:
            with st.expander("Technical Details"):
                st.code(module.error)

        return

    if module.render is None:
        st.info(
            "This Registry module has not yet been implemented."
        )
        return

    try:
        module.render()

    except Exception as exc:
        st.error(
            f"Unable to render {module.label}."
        )

        with st.expander("Technical Details"):
            st.exception(exc)
