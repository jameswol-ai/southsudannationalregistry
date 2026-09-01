"""
Central module registry for the South Sudan National Registry.

Each module exposes:

    render()

The Streamlit application discovers modules through this registry.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class ModuleDefinition:
    """Definition of a Streamlit application module."""

    key: str
    label: str
    description: str
    icon: str
    render: Callable


def _load_modules() -> list[ModuleDefinition]:
    """Load all application modules."""

    from .administration import render as administration
    from .ai_studio import render as ai_studio
    from .citizens import render as citizens
    from .civil_registration import render as civil_registration
    from .documents import render as documents
    from .elections import render as elections
    from .households import render as households
    from .identity import render as identity
    from .overview import render as overview
    from .reports import render as reports
    from .verification import render as verification

    return [
        ModuleDefinition(
            key="overview",
            label="Overview",
            description="National registry operational dashboard.",
            icon="⌂",
            render=overview,
        ),
        ModuleDefinition(
            key="citizens",
            label="Citizens",
            description="Citizen registration and records.",
            icon="C",
            render=citizens,
        ),
        ModuleDefinition(
            key="households",
            label="Households",
            description="Household registration and membership.",
            icon="H",
            render=households,
        ),
        ModuleDefinition(
            key="civil_registration",
            label="Civil Registration",
            description="Birth, death, marriage and divorce records.",
            icon="CR",
            render=civil_registration,
        ),
        ModuleDefinition(
            key="identity",
            label="Identity",
            description="Identity registration and identity records.",
            icon="ID",
            render=identity,
        ),
        ModuleDefinition(
            key="elections",
            label="Elections",
            description="Voter registration and electoral records.",
            icon="E",
            render=elections,
        ),
        ModuleDefinition(
            key="documents",
            label="Documents",
            description="Registry and identity documents.",
            icon="D",
            render=documents,
        ),
        ModuleDefinition(
            key="verification",
            label="Verification",
            description="Citizen verification workflow.",
            icon="V",
            render=verification,
        ),
        ModuleDefinition(
            key="reports",
            label="Reports",
            description="Registry analytics and reporting.",
            icon="R",
            render=reports,
        ),
        ModuleDefinition(
            key="ai_studio",
            label="AI Studio",
            description="AI-assisted registry analysis.",
            icon="AI",
            render=ai_studio,
        ),
        ModuleDefinition(
            key="administration",
            label="Administration",
            description="System administration and audit.",
            icon="A",
            render=administration,
        ),
    ]


MODULES = _load_modules()


def get_modules() -> list[ModuleDefinition]:
    """Return all registered modules."""

    return MODULES.copy()


def get_module(
    key: str,
) -> ModuleDefinition | None:
    """Return a module by key."""

    normalized = key.strip().lower()

    for module in MODULES:

        if module.key == normalized:
            return module

    return None


def get_module_labels() -> list[str]:
    """Return module labels for navigation."""

    return [
        module.label
        for module in MODULES
    ]


def get_module_by_label(
    label: str,
) -> ModuleDefinition | None:
    """Return a module using its display label."""

    normalized = label.strip().lower()

    for module in MODULES:

        if module.label.lower() == normalized:
            return module

    return None
