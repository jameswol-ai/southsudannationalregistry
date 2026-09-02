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
    Module Views
          |
          v
    Module Services
          |
          v
    SQLAlchemy Models
          |
          v
    PostgreSQL / SQLite

The registry is responsible for module discovery and rendering.

Business and database logic belongs inside each module's
service.py / repository.py.

Important:
    Modules are loaded lazily.

A broken optional module therefore does not prevent the main
application or other Registry modules from starting.
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
    Represents one application module.

    The renderer is intentionally optional because modules are
    loaded lazily.
    """

    key: str
    label: str
    description: str

    loader: Loader | None = None

    render: Renderer | None = None

    available: bool = False

    loaded: bool = False

    error: str | None = None


# ============================================================
# MODULE LOADERS
# ============================================================

def _load_population() -> Renderer:
    """
    Load the Population module renderer.
    """

    from modules.population import render

    return render


def _load_civil_registration() -> Renderer:
    """
    Load the Civil Registration module renderer.
    """

    from modules.civil_registration import render

    return render


def _load_identity() -> Renderer:
    """
    Load the Identity module renderer.
    """

    from modules.identity import render

    return render


def _load_elections() -> Renderer:
    """
    Load the Elections module renderer.
    """

    from modules.elections import render

    return render


def _load_reports() -> Renderer:
    """
    Load the Reports module renderer.
    """

    from modules.reports import render

    return render


def _load_administration() -> Renderer:
    """
    Load the Administration module renderer.
    """

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
            "Manage population records, demographic information, "
            "population statistics and population-related services."
        ),
        _load_population,
    ),

    (
        "civil_registration",
        "Civil Registration",
        (
            "Register and manage births, deaths, marriages, "
            "divorces and other civil events."
        ),
        _load_civil_registration,
    ),

    (
        "identity",
        "Identity Management",
        (
            "Manage national identity records, identity documents, "
            "identity verification and related services."
        ),
        _load_identity,
    ),

    (
        "elections",
        "Elections",
        (
            "Manage voter registration, voter records, "
            "constituencies and polling stations."
        ),
        _load_elections,
    ),

    (
        "reports",
        "Reports & Analytics",
        (
            "Generate population, civil registration, identity, "
            "election and operational reports."
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
# REGISTER MODULE DEFINITIONS
# ============================================================

def _register_definition(
    key: str,
    label: str,
    description: str,
    loader: Loader,
) -> RegistryModule:
    """
    Register a module definition without importing the module.

    This is the core of the lazy-loading architecture.
    """

    module = RegistryModule(
        key=key,
        label=label,
        description=description,
        loader=loader,
        render=None,
        available=False,
        loaded=False,
        error=None,
    )

    MODULES[key] = module

    return module


# ============================================================
# INITIALIZE REGISTRY
# ============================================================

def initialize_registry() -> dict[str, RegistryModule]:
    """
    Initialize the registry definitions.

    This function does NOT import application modules.

    It is safe to call repeatedly.
    """

    MODULES.clear()

    for (
        key,
        label,
        description,
        loader,
    ) in _MODULE_DEFINITIONS:

        _register_definition(
            key=key,
            label=label,
            description=description,
            loader=loader,
        )

    return MODULES


# ============================================================
# LAZY MODULE LOADING
# ============================================================

def _load_module(
    module: RegistryModule,
) -> RegistryModule:
    """
    Load a module only when it is actually requested.

    Any import or initialization error is captured inside the
    module record instead of crashing the entire application.
    """

    if module.loaded:
        return module

    if module.loader is None:

        module.loaded = True
        module.available = False
        module.error = (
            "No module loader has been registered."
        )

        return module

    try:

        renderer = module.loader()

        if not callable(renderer):

            raise TypeError(
                f"Module '{module.key}' does not expose "
                "a callable render() function."
            )

        module.render = renderer
        module.available = True
        module.loaded = True
        module.error = None

    except Exception as exc:

        module.render = None
        module.available = False
        module.loaded = True

        module.error = (
            f"{type(exc).__name__}: {exc}"
        )

    return module


# ============================================================
# GET MODULE
# ============================================================

def get_module(
    key: str,
) -> RegistryModule | None:
    """
    Return a module by key.

    The module is loaded lazily when requested.
    """

    module = MODULES.get(key)

    if module is None:
        return None

    return _load_module(module)


# ============================================================
# GET AVAILABLE MODULES
# ============================================================

def get_available_modules() -> list[RegistryModule]:
    """
    Load and return all modules that are available.

    This intentionally evaluates every module because the caller
    is explicitly asking for availability information.
    """

    available: list[RegistryModule] = []

    for module in MODULES.values():

        loaded = _load_module(module)

        if loaded.available:
            available.append(loaded)

    return available


# ============================================================
# GET UNAVAILABLE MODULES
# ============================================================

def get_unavailable_modules() -> list[RegistryModule]:
    """
    Load all modules and return those that are unavailable.
    """

    unavailable: list[RegistryModule] = []

    for module in MODULES.values():

        loaded = _load_module(module)

        if not loaded.available:
            unavailable.append(loaded)

    return unavailable


# ============================================================
# GET ALL MODULES
# ============================================================

def get_all_modules() -> list[RegistryModule]:
    """
    Return all registered module definitions.

    Unlike get_available_modules(), this does not force module
    imports.
    """

    return list(MODULES.values())


# ============================================================
# MODULE EXISTS
# ============================================================

def module_exists(
    key: str,
) -> bool:
    """
    Check whether a module key is registered.

    Does not import the module.
    """

    return key in MODULES


# ============================================================
# MODULE AVAILABILITY
# ============================================================

def module_is_available(
    key: str,
) -> bool:
    """
    Check whether a module exists and loads successfully.
    """

    module = get_module(key)

    return (
        module is not None
        and module.available
        and module.render is not None
    )


# ============================================================
# RENDER MODULE
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

        if not module.loaded:
            module = _load_module(module)

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
    # Renderer missing
    # --------------------------------------------------------

    if module.render is None:

        st.warning(
            f"{module.label} does not currently "
            "provide a render function."
        )

        return

    # --------------------------------------------------------
    # Render
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
    Return Registry health statistics.

    This loads each module because availability cannot be known
    without attempting the import.
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
# MODULE ERRORS
# ============================================================

def get_module_errors() -> dict[str, str]:
    """
    Return loading errors for modules that failed.
    """

    errors: dict[str, str] = {}

    for module in MODULES.values():

        loaded = _load_module(module)

        if (
            not loaded.available
            and loaded.error
        ):

            errors[
                loaded.key
            ] = loaded.error

    return errors


# ============================================================
# REGISTER DEFAULT MODULES
# ============================================================

initialize_registry()


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