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
    |                                     |
    v                                     v
Registry Modules                      Module Status
    |                                     |
    +----------------+--------------------+
                     |
                     v
                 services
                     |
                     v
                  database


Design goals
------------
1. A broken module must not crash Streamlit startup.
2. Every module is loaded independently.
3. Every module must expose a callable render() function.
4. The registry exposes both:
       get_modules()
       get_available_modules()
       get_unavailable_modules()
       get_module()
       render_module()
5. Import errors are captured and displayed as module status.
6. The registry does not import application modules eagerly.
"""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Callable, Optional


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(
    "south_sudan_registry.modules"
)


# ============================================================
# TYPES
# ============================================================

RenderFunction = Callable[[], Any]


# ============================================================
# MODULE DATA MODEL
# ============================================================

@dataclass(frozen=True)
class RegistryModule:
    """
    Metadata and runtime information for one registry module.
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

MODULE_DEFINITIONS: list[dict[str, str]] = [

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
            "Citizen and document verification "
            "workflows."
        ),
    },

    {
        "key": "reports",
        "label": "Reports",
        "module_path": "modules.reports",
        "category": "Analytics",
        "icon": "Reports",
        "description": (
            "Registry statistics, analytics and "
            "reports."
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
    definition: dict[str, str],
) -> RegistryModule:
    """
    Safely import one registry module.

    IMPORTANT:
    Any exception raised by the module is captured here.
    The exception therefore cannot prevent the rest of
    the registry from loading.
    """

    key = definition["key"]

    label = definition["label"]

    module_path = definition["module_path"]

    category = definition["category"]

    icon = definition.get(
        "icon",
        "",
    )

    description = definition.get(
        "description",
        "",
    )


    # --------------------------------------------------------
    # IMPORT MODULE
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # FIND render()
    # --------------------------------------------------------

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

        logger.error(
            error
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


    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    logger.info(
        "Registry module loaded: %s",
        module_path,
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
    Load every configured registry module independently.

    Returns
    -------
    dict
        Dictionary keyed by module key.
    """

    modules: dict[str, RegistryModule] = {}


    for definition in MODULE_DEFINITIONS:

        try:

            module = _load_module(
                definition
            )

            modules[module.key] = module

        except Exception as exc:

            # This is an additional defensive layer.
            #
            # _load_module() already catches normal import
            # failures, but this protects the registry from
            # unexpected loader failures.

            key = definition.get(
                "key",
                "unknown",
            )

            error = (
                f"{type(exc).__name__}: {exc}"
            )

            logger.exception(
                "Unexpected error loading module '%s'",
                key,
            )

            modules[key] = RegistryModule(
                key=key,
                label=definition.get(
                    "label",
                    key,
                ),
                module_path=definition.get(
                    "module_path",
                    "",
                ),
                category=definition.get(
                    "category",
                    "Registry",
                ),
                icon=definition.get(
                    "icon",
                    "",
                ),
                description=definition.get(
                    "description",
                    "",
                ),
                render=None,
                available=False,
                error=error,
            )


    return modules


# ============================================================
# GLOBAL MODULE REGISTRY
# ============================================================

MODULES: dict[str, RegistryModule] = (
    _load_modules()
)


# ============================================================
# PUBLIC API
# ============================================================

def get_modules() -> list[RegistryModule]:
    """
    Return all configured registry modules.

    The order follows MODULE_DEFINITIONS.
    """

    return list(
        MODULES.values()
    )


def get_available_modules() -> list[RegistryModule]:
    """
    Return only modules that successfully imported
    and expose a callable render() function.
    """

    return [
        module
        for module in MODULES.values()
        if module.available
        and callable(module.render)
    ]


def get_unavailable_modules() -> list[RegistryModule]:
    """
    Return modules that failed to load or do not expose
    a valid render() function.
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
    Return one registry module by key.

    Example
    -------
    get_module("identity")
    """

    return MODULES.get(
        key
    )


def get_module_by_label(
    label: str,
) -> Optional[RegistryModule]:
    """
    Return a module by display label.
    """

    normalized = label.strip().lower()

    for module in MODULES.values():

        if module.label.strip().lower() == normalized:

            return module

    return None


def get_modules_by_category(
    category: str,
) -> list[RegistryModule]:
    """
    Return available modules belonging to a category.
    """

    normalized = category.strip().lower()

    return [
        module
        for module in get_available_modules()
        if module.category.strip().lower()
        == normalized
    ]


def get_module_keys() -> list[str]:
    """
    Return all configured module keys.
    """

    return list(
        MODULES.keys()
    )


def get_module_labels() -> list[str]:
    """
    Return all configured display labels.
    """

    return [
        module.label
        for module in MODULES.values()
    ]


def is_module_available(
    key: str,
) -> bool:
    """
    Determine whether a module is operational.
    """

    module = get_module(
        key
    )

    if module is None:

        return False

    return bool(
        module.available
        and callable(module.render)
    )


# ============================================================
# RENDERING
# ============================================================

def render_module(
    key: str,
) -> Any:
    """
    Render a registry module.

    Parameters
    ----------
    key:
        Registry module key.

    Raises
    ------
    KeyError
        If the module does not exist.

    RuntimeError
        If the module is unavailable.

    Exception
        Any runtime exception raised by the module's
        render() function is propagated to the caller.
        streamlit_app.py is responsible for presenting
        the error to the user.
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
            (
                f"Registry module '{key}' is unavailable. "
                f"{module.error or 'No error information available.'}"
            )
        )


    if not callable(module.render):

        raise RuntimeError(
            (
                f"Registry module '{key}' does not "
                "have a callable render() function."
            )
        )


    return module.render()


# ============================================================
# MODULE STATUS
# ============================================================

def module_status() -> list[dict[str, Any]]:
    """
    Return module status information.

    Suitable for:
        - Streamlit administration
        - debugging
        - API responses
        - system health dashboards
    """

    return [
        {
            "key": module.key,
            "label": module.label,
            "module_path": module.module_path,
            "category": module.category,
            "icon": module.icon,
            "available": module.available,
            "error": module.error,
        }
        for module in MODULES.values()
    ]


def get_module_status(
    key: str,
) -> Optional[dict[str, Any]]:
    """
    Return status information for one module.
    """

    module = get_module(
        key
    )

    if module is None:

        return None

    return {
        "key": module.key,
        "label": module.label,
        "module_path": module.module_path,
        "category": module.category,
        "icon": module.icon,
        "available": module.available,
        "error": module.error,
    }


# ============================================================
# REGISTRY HEALTH
# ============================================================

def registry_health() -> dict[str, Any]:
    """
    Return overall registry health information.
    """

    modules = get_modules()

    available = [
        module
        for module in modules
        if module.available
    ]

    unavailable = [
        module
        for module in modules
        if not module.available
    ]


    total = len(
        modules
    )

    operational = len(
        available
    )

    failed = len(
        unavailable
    )


    if total == 0:

        status = "empty"

    elif failed == 0:

        status = "healthy"

    elif operational > 0:

        status = "degraded"

    else:

        status = "unavailable"


    return {
        "status": status,
        "total_modules": total,
        "operational_modules": operational,
        "unavailable_modules": failed,
        "modules": module_status(),
    }


# ============================================================
# DEBUGGING
# ============================================================

def print_module_status() -> None:
    """
    Print module status to application logs.
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


# ============================================================
# REFRESH
# ============================================================

def reload_modules() -> dict[str, RegistryModule]:
    """
    Reload all configured registry modules.

    This is primarily useful during development.

    The global MODULES dictionary is replaced with a
    freshly loaded registry.
    """

    global MODULES

    MODULES = _load_modules()

    return MODULES


# ============================================================
# OPTIONAL STARTUP DIAGNOSTICS
# ============================================================

if __name__ == "__main__":

    print(
        "South Sudan National Registry"
    )

    print(
        "Module Registry Status"
    )

    print(
        "======================="
    )

    for module in get_modules():

        status = (
            "AVAILABLE"
            if module.available
            else "UNAVAILABLE"
        )

        print(
            f"{module.key:25} "
            f"{status:12} "
            f"{module.module_path}"
        )

        if module.error:

            print(
                f"    ERROR: {module.error}"
            )
