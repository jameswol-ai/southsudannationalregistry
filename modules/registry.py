"""
South Sudan National Registry
Central Module Registry

The registry provides lazy module discovery and safe rendering.

Architecture:

    Streamlit
        |
        v
    Module Registry
        |
        +--> Population
        +--> Civil Registration
        +--> Identity
        +--> Elections
        +--> Reports
        +--> Administration
        |
        v
    Views
        |
        v
    Services
        |
        v
    Repositories
        |
        v
    SQLAlchemy Models
        |
        v
    PostgreSQL / SQLite
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


Renderer = Callable[[], None]
Loader = Callable[[], Renderer]


@dataclass
class RegistryModule:
    key: str
    label: str
    description: str

    loader: Loader | None = None
    render: Renderer | None = None

    available: bool = False
    loaded: bool = False
    error: str | None = None


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


_MODULE_DEFINITIONS: list[
    tuple[str, str, str, Loader]
] = [
    (
        "population",
        "Population Registry",
        (
            "Manage population records, demographic information, "
            "population statistics and household information."
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
            "Manage identity records, national identity documents, "
            "verification and document status."
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
            "Generate registry reports, statistics and analytics."
        ),
        _load_reports,
    ),
    (
        "administration",
        "Administration",
        (
            "Manage users, permissions, audit logs and "
            "system administration."
        ),
        _load_administration,
    ),
]


MODULES: dict[str, RegistryModule] = {}


def _register_definition(
    key: str,
    label: str,
    description: str,
    loader: Loader,
) -> RegistryModule:

    module = RegistryModule(
        key=key,
        label=label,
        description=description,
        loader=loader,
    )

    MODULES[key] = module
    return module


def initialize_registry() -> dict[str, RegistryModule]:
    MODULES.clear()

    for key, label, description, loader in _MODULE_DEFINITIONS:
        _register_definition(
            key=key,
            label=label,
            description=description,
            loader=loader,
        )

    return MODULES


def _load_module(
    module: RegistryModule,
) -> RegistryModule:

    if module.loaded:
        return module

    if module.loader is None:
        module.loaded = True
        module.available = False
        module.error = "No module loader registered."
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
        module.error = f"{type(exc).__name__}: {exc}"

    return module


def get_module(
    key: str,
) -> RegistryModule | None:

    module = MODULES.get(key)

    if module is None:
        return None

    return _load_module(module)


def get_available_modules() -> list[RegistryModule]:

    result: list[RegistryModule] = []

    for module in MODULES.values():
        loaded = _load_module(module)

        if loaded.available:
            result.append(loaded)

    return result


def get_unavailable_modules() -> list[RegistryModule]:

    result: list[RegistryModule] = []

    for module in MODULES.values():
        loaded = _load_module(module)

        if not loaded.available:
            result.append(loaded)

    return result


def get_all_modules() -> list[RegistryModule]:
    return list(MODULES.values())


def module_exists(key: str) -> bool:
    return key in MODULES


def module_is_available(key: str) -> bool:

    module = get_module(key)

    return bool(
        module
        and module.available
        and module.render
    )


def render_module(
    module_or_key: str | RegistryModule,
) -> None:

    import streamlit as st

    if isinstance(module_or_key, str):
        module = get_module(module_or_key)
    else:
        module = module_or_key

        if not module.loaded:
            module = _load_module(module)

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
        st.warning(
            f"{module.label} does not expose a render function."
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


def get_registry_status() -> dict[str, int]:

    modules = list(MODULES.values())

    available = 0
    unavailable = 0

    for module in modules:
        loaded = _load_module(module)

        if loaded.available:
            available += 1
        else:
            unavailable += 1

    return {
        "total": len(modules),
        "available": available,
        "unavailable": unavailable,
    }


def get_module_errors() -> dict[str, str]:

    errors: dict[str, str] = {}

    for module in MODULES.values():
        loaded = _load_module(module)

        if loaded.error:
            errors[loaded.key] = loaded.error

    return errors


initialize_registry()


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