"""
South Sudan National Registry
Module Registry

Central module loader for the Streamlit AI Studio.

Architecture:

    streamlit_app.py
          |
          v
    modules.registry
          |
    +-----+-------------------------------+
    |     |                               |
    v     v                               v
  Civil Identity   Elections ...   Administration
    |
    v
  services
    |
    v
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


# ============================================================
# REGISTRY MODULE
# ============================================================

@dataclass(frozen=True)
class RegistryModule:
    """
    Description of a Streamlit registry module.
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
# LOAD ONE MODULE
# ============================================================

def _load_module(
    definition: dict,
) -> RegistryModule:
    """
    Safely load one registry module.

    A failure in one module does not prevent the
    entire Streamlit application from starting.
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
    Load all configured registry modules.
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

def get_modules() -> list[RegistryModule]:
    """
    Return all registered modules.

    This is the primary function used by streamlit_app.py.

    Unavailable modules are included so the application can
    display their status instead of silently hiding them.
    """

    return list(
        MODULES.values()
    )


def get_available_modules() -> list[RegistryModule]:
    """
    Return only successfully loaded modules.
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


def get_module(
    key: str,
) -> Optional[RegistryModule]:
    """
    Return a registered module by key.
    """

    return MODULES.get(
        key
    )


def get_modules_by_category(
    category: str,
) -> list[RegistryModule]:
    """
    Return available modules belonging to a category.
    """

    return [
        module
        for module in get_available_modules()
        if module.category == category
    ]


def get_module_keys() -> list[str]:
    """
    Return all registered module keys.
    """

    return list(
        MODULES.keys()
    )


def is_module_available(
    key: str,
) -> bool:
    """
    Determine whether a module is available.
    """

    module = get_module(
        key
    )

    return bool(
        module
        and module.available
        and callable(module.render)
    )


# ============================================================
# RENDERING
# ============================================================

def render_module(
    key: str,
) -> object:
    """
    Render a module by key.

    Raises:
        KeyError:
            Unknown module.

        RuntimeError:
            Module unavailable.
    """

    module = get_module(
        key
    )

    if module is None:

        raise KeyError(
            f"Unknown registry module: {key}"
        )

    if not module.available:

        raise RuntimeError(
            f"Registry module '{key}' is unavailable. "
            f"{module.error or 'Unknown import error.'}"
        )

    if not callable(module.render):

        raise RuntimeError(
            f"Registry module '{key}' does not expose "
            "a callable render() function."
        )

    return module.render()


# ============================================================
# STATUS
# ============================================================

def module_status() -> list[dict[str, object]]:
    """
    Return registry module status.

    Suitable for administration/debugging screens.
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


def print_module_status() -> None:
    """
    Write module status to the application log.
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
