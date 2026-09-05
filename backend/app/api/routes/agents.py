"""
Agent registry and status metadata.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/agents", tags=["agents"])

AGENT_REGISTRY = [
    {
        "name": "analyzer",
        "label": "Codebase Analyzer",
        "stage": "1. Analysis",
        "description": "Inspects project structure, build definitions (Maven/Gradle), and parses Java AST via Compiler Tree API.",
        "implemented": True,
    },
    {
        "name": "architecture",
        "label": "Architecture Analyzer",
        "stage": "2. Architecture",
        "description": "Identifies architectural patterns (Layered, Spring Boot MVC) and recommends target framework mapping.",
        "implemented": True,
    },
    {
        "name": "planner",
        "label": "Migration Planner",
        "stage": "3. Planning",
        "description": "Computes class dependency topological ordering and phased migration roadmaps.",
        "implemented": True,
    },
    {
        "name": "dependency",
        "label": "Dependency Mapper",
        "stage": "4. Dependencies",
        "description": "Maps Maven / Gradle artifacts to target package manifests (requirements.txt, package.json, build.gradle.kts).",
        "implemented": True,
    },
    {
        "name": "translator",
        "label": "AI Translation Agent",
        "stage": "5. Code Generation",
        "description": "Translates Java classes, methods, syntax, and logic into target language files.",
        "implemented": True,
    },
    {
        "name": "refactoring",
        "label": "Refactoring Agent",
        "stage": "6. Refactoring",
        "description": "Post-processes code into idiomatic patterns (dataclasses, typing, naming conventions).",
        "implemented": True,
    },
    {
        "name": "test_migration",
        "label": "Test Migration Agent",
        "stage": "7. Testing",
        "description": "Generates unit test suites (PyTest, Vitest, KotlinTest) for generated modules.",
        "implemented": True,
    },
    {
        "name": "repair",
        "label": "Autonomous Repair Agent",
        "stage": "8. Build & Repair",
        "description": "Validates syntax, detects compilation/type errors, and applies autonomous patches.",
        "implemented": True,
    },
    {
        "name": "validation",
        "label": "Validation Agent",
        "stage": "9. Quality Check",
        "description": "Evaluates overall syntax, structural completeness, and quality score (0-100%).",
        "implemented": True,
    },
    {
        "name": "report",
        "label": "Report Agent",
        "stage": "10. Reporting",
        "description": "Synthesizes comprehensive migration reports, metrics, and actionable engineering next steps.",
        "implemented": True,
    },
]


@router.get("")
def list_agents():
    return {"agents": AGENT_REGISTRY}
