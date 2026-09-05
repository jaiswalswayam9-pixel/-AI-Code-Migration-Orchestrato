"""
Migration Planner Agent (spec section 13).

Analyzes project dependencies and architecture to produce an ordered,
dependency-aware step-by-step execution plan.
"""
from typing import Any
from app.ir.models import IRProject


def create_migration_plan(ir: IRProject, architecture: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Produces an ordered list of migration steps based on topological
    dependencies (enums/models first, then repos, services, controllers, tests).
    """
    layers = (architecture or {}).get("layers", {})
    models = set(layers.get("models", []))
    repos = set(layers.get("repositories", []))
    services = set(layers.get("services", []))
    controllers = set(layers.get("controllers", []))

    ordered_classes: list[dict[str, Any]] = []

    # 1. Enums and data models
    for cu in ir.compilation_units:
        for t in cu.types:
            if t.name in models or t.kind in ("enum", "record") or (not t.methods and t.fields):
                ordered_classes.append({
                    "name": t.name,
                    "kind": t.kind,
                    "phase": "1_domain_models",
                    "file": cu.file,
                    "risk": "low",
                    "reason": "Foundational data structures with no business logic dependencies.",
                })

    # 2. Repositories and data access interfaces
    for cu in ir.compilation_units:
        for t in cu.types:
            if t.name in repos or t.kind == "interface":
                if not any(c["name"] == t.name for c in ordered_classes):
                    ordered_classes.append({
                        "name": t.name,
                        "kind": t.kind,
                        "phase": "2_data_access",
                        "file": cu.file,
                        "risk": "low" if t.kind == "interface" else "medium",
                        "reason": "Data access contracts and database operations.",
                    })

    # 3. Services and core business logic
    for cu in ir.compilation_units:
        for t in cu.types:
            if t.name in services:
                if not any(c["name"] == t.name for c in ordered_classes):
                    ordered_classes.append({
                        "name": t.name,
                        "kind": t.kind,
                        "phase": "3_business_services",
                        "file": cu.file,
                        "risk": "medium",
                        "reason": "Core business rules and operations orchestrating domain models.",
                    })

    # 4. Controllers, APIs, and Utilities
    for cu in ir.compilation_units:
        for t in cu.types:
            if not any(c["name"] == t.name for c in ordered_classes):
                phase = "4_api_controllers" if t.name in controllers else "5_utilities"
                ordered_classes.append({
                    "name": t.name,
                    "kind": t.kind,
                    "phase": phase,
                    "file": cu.file,
                    "risk": "medium" if phase == "4_api_controllers" else "low",
                    "reason": "External HTTP endpoints and utility helpers.",
                })

    steps: list[dict[str, Any]] = [
        {
            "step_number": 1,
            "name": "Dependency & Framework Translation",
            "description": "Map Maven/Gradle dependencies to target language package manifest.",
        },
        {
            "step_number": 2,
            "name": "Domain Models & Types Migration",
            "description": f"Convert {len([c for c in ordered_classes if c['phase'] == '1_domain_models'])} data structures and types.",
        },
        {
            "step_number": 3,
            "name": "Data Access & Services Migration",
            "description": f"Translate {len([c for c in ordered_classes if '2' in c['phase'] or '3' in c['phase']])} business logic components and services.",
        },
        {
            "step_number": 4,
            "name": "Controllers & Entrypoints Scaffolding",
            "description": f"Map {len([c for c in ordered_classes if '4' in c['phase']])} API endpoints to target framework routers.",
        },
        {
            "step_number": 5,
            "name": "Autonomous Build, Test & Repair Loop",
            "description": "Validate target compilation, run test suite, and autonomously repair syntax/type errors.",
        },
        {
            "step_number": 6,
            "name": "Validation & Report Generation",
            "description": "Perform full structural, type coverage, and behavioural validation; generate final report.",
        },
    ]

    total_classes = len(ordered_classes)
    complexity = "Low" if total_classes <= 5 else ("Medium" if total_classes <= 20 else "High")

    return {
        "complexity_estimate": complexity,
        "total_classes": total_classes,
        "steps": steps,
        "execution_order": ordered_classes,
    }
