"""
South Sudan National Registry
Module Registry

Central module loader for the Streamlit AI Studio.

Architecture:

    streamlit_app.py
          |
          ▼
    modules.registry
          |
    ┌─────┼───────────────────────────┐
    ▼     ▼                           ▼
  Civil Identity   Elections ...   Administration
    |
    ▼
  services
    |
    ▼
  database
"""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass
from types import ModuleType
from typing import Callable, Optional


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(
    "south_sudan_registry.modules"
)


# ============================================================
# TYPES
# ============================================================

RenderFunction = Callable[[], object]


@dataclass(frozen=True)
class RegistryModule:
    """
    Description of a Streamlit application module.
    """

    key: str
    label: str
    module_path: str
    category: str
    icon: str = ""
    description: str = ""
    render: Optional[RenderFunction] = None
    available: bool = False
    error: Optional[str] = None


# ============================================================
# MODULE DEFINITIONS
# ============================================================

MODULE_DEFINITIONS = [
    {
        "key": "civil_registration",
        "label": "Civil Registration",
        "module_path": "modules.civil_registration",
        "category": "Registry",
        "icon": "Civil",
        "description": (
            "Birth, death, marriage and divorce "
            "registration."
        ),
    },
    {
        "key": "identity",
        "label": "Identity",
        "module_path": "modules.identity",
        "category": "Registry",
        "icon": "ID",
        "description": (
            "National identity registration and "
            "identity management."
        ),
    },
    {
        "key": "elections",
        "label": "Elections",
        "module_path": "modules.elections",
        "category": "Electoral",
        "icon": "Election",
        "description": (
            "Voter registration, electoral roll and "
            "polling operations."
        ),
    },
    {
        "key": "documents",
        "label": "Documents",
        "module_path": "modules.documents",
        "category": "Registry",
        "icon": "Docs",
        "description": (
            "Identity and civil registration documents."
        ),
    },
    {
        "key": "verification",
        "label": "Verification",
        "module_path": "modules.verification",
        "category": "Registry",
        "icon": "Verify",
        "description": (
            "Citizen and document verification workflows."
        ),
    },
    {
        "key": "reports",
        "label": "Reports",
        "module_path": "modules.reports",
        "category": "Analytics",
        "icon": "Reports",
        "description": (
            "Registry statistics, analytics and reports."
        ),
    },
    {
        "key": "ai_studio",
        "label": "AI Studio",
        "module_path": "modules.ai_studio",
        "category": "AI",
        "icon": "AI",
        "description": (
            "AI-assisted registry analysis and "
            "administrative workflows."
        ),
    },
    {
        "key": "administration",
        "label": "Administration",
        "module_path": "modules.administration",
        "category": "Administration",
        "icon": "Admin",
        "description": (
            "Users, permissions, administrative units "
            "and system configuration."
        ),
    },
]


# ============================================================
# MODULE LOADER
# ============================================================

def _load_module(
    definition: dict,
) -> RegistryModule:
    """
    Safely import one registry module.

    A failure in one module must not prevent the rest of
    the Streamlit application from starting.
    """

    key = definition["key"]
    label = definition["label"]
    module_path = definition["module_path"]
    category = definition["category"]
    icon = definition.get("icon", "")
    description = definition.get(
        "description",
        "",
    )

    try:

        module: ModuleType = importlib.import_module(
            module_path
        )

    except Exception as exc:

        error = (
            f"{type(exc).__name__}: {exc}"
        )

        logger.exception(
            "Unable to import registry module '%s'",
            module_path,
        )

        return RegistryModule(
            key=key,
            label=label,
            module_path=module_path,
            category=category,
            icon=icon,
            description=description,
            render=None,
            available=False,
            error=error,
        )

    render = getattr(
        module,
        "render",
        None,
    )

    if not callable(render):

        error = (
            f"Module '{module_path}' does not expose "
            "a callable render() function."
        )

        logger.error(error)

        return RegistryModule(
            key=key,
            label=label,
            module_path=module_path,
            category=category,
            icon=icon,
            description=description,
            render=None,
            available=False,
            error=error,
        )

    return RegistryModule(
        key=key,
        label=label,
        module_path=module_path,
        category=category,
        icon=icon,
        description=description,
        render=render,
        available=True,
        error=None,
    )


# ============================================================
# LOAD ALL MODULES
# ============================================================

def _load_modules() -> dict[str, RegistryModule]:
    """
    Load all configured modules.

    Returns a dictionary keyed by module key.
    """

    modules: dict[str, RegistryModule] = {}

    for definition in MODULE_DEFINITIONS:

        module = _load_module(
            definition
        )

        modules[module.key] = module

    return modules


MODULES = _load_modules()


# ============================================================
# PUBLIC API
# ============================================================

def get_module(
    key: str,
) -> Optional[RegistryModule]:
    """
    Return a module by key.
    """

    return MODULES.get(key)


def get_available_modules() -> list[RegistryModule]:
    """
    Return modules that successfully loaded.
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


def get_modules_by_category(
    category: str,
) -> list[RegistryModule]:
    """
    Return available modules in a category.
    """

    return [
        module
        for module in get_available_modules()
        if module.category == category
    ]


def get_module_keys() -> list[str]:
    """
    Return all configured module keys.
    """

    return list(MODULES.keys())


def is_module_available(
    key: str,
) -> bool:
    """
    Determine whether a module is available.
    """

    module = get_module(key)

    return bool(
        module
        and module.available
        and module.render
    )


def render_module(
    key: str,
) -> object:
    """
    Render a registry module.

    Raises:
        KeyError:
            If the module does not exist.

        RuntimeError:
            If the module is unavailable.
    """

    module = get_module(key)

    if module is None:

        raise KeyError(
            f"Unknown registry module: {key}"
        )

    if not module.available:

        raise RuntimeError(
            f"Registry module '{key}' is unavailable. "
            f"{module.error or ''}".strip()
        )

    if module.render is None:

        raise RuntimeError(
            f"Registry module '{key}' has no render() function."
        )

    return module.render()


# ============================================================
# MODULE STATUS
# ============================================================

def module_status() -> list[dict[str, object]]:
    """
    Return module status information suitable for
    Streamlit administration/debugging views.
    """

    return [
        {
            "key": module.key,
            "label": module.label,
            "category": module.category,
            "module_path": module.module_path,
            "available": module.available,
            "error": module.error,
        }
        for module in MODULES.values()
    ]


# ============================================================
# DEBUGGING
# ============================================================

def print_module_status() -> None:
    """
    Print module status to the application logs.
    """

    for module in MODULES.values():

        if module.available:

            logger.info(
                "Registry module available: %s",
                module.key,
            )

        else:

            logger.warning(
                "Registry module unavailable: %s — %s",
                module.key,
                module.error,
        )
