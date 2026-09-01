"""
South Sudan National Registry
Registry Module System

Central module registry for the Streamlit Registry application.

Architecture:

    streamlit_app.py
          |
          v
    modules.registry
          |
          +---- Population
          +---- Civil Registration
          +---- Identity
          +---- Elections
          +---- Reports
          +---- Administration
          |
          v
    Module UI
          |
          v
    Module Service
          |
          v
    SQLAlchemy Models
          |
          v
    PostgreSQL / SQLite

The registry is responsible for module discovery and rendering only.
Business/database logic belongs inside each module's service.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


# ============================================================
# TYPES
# ============================================================

Renderer = Callable[[], None]
Loader = Callable[[], Renderer]


# ============================================================
# MODULE DEFINITION
# ============================================================

@dataclass
class RegistryModule:
    """
    Represents a Registry application module.
    """

    key: str
    label: str
    description: str

    # Renderer loaded from the module's __init__.py
    render: Renderer | None = None

    # Runtime availability
    available: bool = True

    # Error captured during module loading
    error: str | None = None


# ============================================================
# MODULE LOADERS
# ============================================================
#
# IMPORTANT:
#
# These functions intentionally import modules lazily.
#
# registry.py can therefore be imported even if one individual
# module has a dependency or coding error.
#
# The module is loaded only when the registry initializes it.
# ============================================================


def _load_population() -> Renderer:

    from modules.population import render

    return render


def _load_civil_registration() -> Renderer:

    from modules.civil_registration import render

    return render


def _load_identity() -> Renderer:

    from modules.identity import render

    return render


def _load_elections() -> Renderer:

    from modules.elections import render

    return render


def _load_reports() -> Renderer:

    from modules.reports import render

    return render


def _load_administration() -> Renderer:

    from modules.administration import render

    return render


# ============================================================
# MODULE DEFINITIONS
# ============================================================

_MODULE_DEFINITIONS: list[
    tuple[str, str, str, Loader]
] = [

    (
        "population",
        "Population Registry",
        (
            "Manage national population records, citizens, "
            "households and demographic information."
        ),
        _load_population,
    ),

    (
        "civil_registration",
        "Civil Registration",
        (
            "Register births, deaths, marriages, divorces "
            "and other civil events."
        ),
        _load_civil_registration,
    ),

    (
        "identity",
        "Identity Management",
        (
            "Manage national identity records, identity "
            "documents and identity services."
        ),
        _load_identity,
    ),

    (
        "elections",
        "Elections",
        (
            "Manage voter registration, constituencies, "
            "polling stations and electoral records."
        ),
        _load_elections,
    ),

    (
        "reports",
        "Reports & Analytics",
        (
            "Generate operational, demographic, civil "
            "registration and election reports."
        ),
        _load_reports,
    ),

    (
        "administration",
        "Administration",
        (
            "Manage users, roles, permissions, audit logs "
            "and system configuration."
        ),
        _load_administration,
    ),
]


# ============================================================
# REGISTRY STORAGE
# ============================================================

MODULES: dict[str, RegistryModule] = {}


# ============================================================
# MODULE REGISTRATION
# ============================================================

def _register(
    key: str,
    label: str,
    description: str,
    loader: Loader,
) -> RegistryModule:
    """
    Load and register a single module.

    A module failure is isolated so that the remaining Registry
    modules can continue to operate.
    """

    try:

        renderer = loader()

        if not callable(renderer):

            raise TypeError(
                f"Module '{key}' does not expose a callable "
                f"render function."
            )

        module = RegistryModule(
            key=key,
            label=label,
            description=description,
            render=renderer,
            available=True,
        )

    except Exception as exc:

        module = RegistryModule(
            key=key,
            label=label,
            description=description,
            render=None,
            available=False,
            error=(
                f"{type(exc).__name__}: {exc}"
            ),
        )

    MODULES[key] = module

    return module


# ============================================================
# INITIALIZE REGISTRY
# ============================================================

def initialize_registry() -> dict[str, RegistryModule]:
    """
    Initialize all Registry modules.

    Safe to call multiple times.
    """

    MODULES.clear()

    for (
        key,
        label,
        description,
        loader,
    ) in _MODULE_DEFINITIONS:

        _register(
            key=key,
            label=label,
            description=description,
            loader=loader,
        )

    return MODULES


# ============================================================
# INITIALIZE ON IMPORT
# ============================================================

initialize_registry()


# ============================================================
# PUBLIC API
# ============================================================

def get_module(
    key: str,
) -> RegistryModule | None:
    """
    Return a module by its registry key.
    """

    return MODULES.get(key)


def get_available_modules() -> list[RegistryModule]:
    """
    Return all modules that loaded successfully.
    """

    return [
        module
        for module in MODULES.values()
        if module.available
    ]


def get_unavailable_modules() -> list[RegistryModule]:
    """
    Return modules that failed to load.
    """

    return [
        module
        for module in MODULES.values()
        if not module.available
    ]


def get_all_modules() -> list[RegistryModule]:
    """
    Return every registered module.
    """

    return list(MODULES.values())


def module_exists(
    key: str,
) -> bool:
    """
    Check whether a module exists.
    """

    return key in MODULES


def module_is_available(
    key: str,
) -> bool:
    """
    Check whether a module exists and is available.
    """

    module = get_module(key)

    return (
        module is not None
        and module.available
        and module.render is not None
    )


# ============================================================
# MODULE RENDERING
# ============================================================

def render_module(
    module_or_key: str | RegistryModule,
) -> None:
    """
    Render a Registry module safely.

    Accepts either:

        render_module("population")

    or:

        render_module(module)
    """

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

    # --------------------------------------------------------
    # Module not found
    # --------------------------------------------------------

    if module is None:

        st.error(
            "Registry module not found."
        )

        return

    # --------------------------------------------------------
    # Module unavailable
    # --------------------------------------------------------

    if not module.available:

        st.error(
            f"{module.label} is currently unavailable."
        )

        if module.error:

            with st.expander(
                "Technical Details"
            ):

                st.code(
                    module.error
                )

        return

    # --------------------------------------------------------
    # Missing renderer
    # --------------------------------------------------------

    if module.render is None:

        st.warning(
            f"{module.label} does not currently "
            "have a render function."
        )

        return

    # --------------------------------------------------------
    # Render module
    # --------------------------------------------------------

    try:

        module.render()

    except Exception as exc:

        st.error(
            f"Unable to render {module.label}."
        )

        with st.expander(
            "Technical Details"
        ):

            st.exception(exc)


# ============================================================
# REGISTRY STATUS
# ============================================================

def get_registry_status() -> dict[str, int]:
    """
    Return simple registry health statistics.
    """

    total = len(MODULES)

    available = len(
        get_available_modules()
    )

    unavailable = len(
        get_unavailable_modules()
    )

    return {
        "total": total,
        "available": available,
        "unavailable": unavailable,
    }


# ============================================================
# DEBUG / DIAGNOSTICS
# ============================================================

def get_module_errors() -> dict[str, str]:
    """
    Return loading errors for unavailable modules.
    """

    return {
        module.key: module.error
        for module in get_unavailable_modules()
        if module.error
    }


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    "RegistryModule",
    "MODULES",
    "initialize_registry",
    "get_module",
    "get_available_modules",
    "get_unavailable_modules",
    "get_all_modules",
    "module_exists",
    "module_is_available",
    "render_module",
    "get_registry_status",
    "get_module_errors",
    ]
