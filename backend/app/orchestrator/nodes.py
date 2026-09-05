"""
LangGraph Workflow Nodes (spec section 12-25).

Each node represents a distinct agent in the migration pipeline,
receiving and transforming the shared WorkflowState.
"""
from pathlib import Path
from typing import Any

from app.orchestrator.state import WorkflowState, FileStatus, MigrationError
from app.agents.analyzer_agent import analyze_project
from app.agents.architecture_agent import analyze_architecture
from app.agents.planner_agent import create_migration_plan
from app.agents.dependency_agent import map_dependencies, generate_manifest_content
from app.agents.translation_agent import TranslationAgent
from app.agents.refactoring_agent import refactor_code
from app.agents.test_migration_agent import generate_tests_for_project
from app.agents.error_analysis_agent import analyze_errors
from app.agents.repair_agent import attempt_repair
from app.agents.validation_agent import validate_project
from app.agents.report_agent import generate_migration_report
from app.parsers.java_parser import parse_java_files
from app.ir.builder import build_project_ir
from app.generators.python_generator import PythonGenerator
from app.generators.typescript_generator import TypeScriptGenerator
from app.generators.kotlin_generator import KotlinGenerator
from app.execution.build_runner import run_build
from app.execution.test_runner import run_tests

GENERATORS = {
    "python": PythonGenerator,
    "typescript": TypeScriptGenerator,
    "kotlin": KotlinGenerator,
}


def analyze_node(state: dict[str, Any], workspace_path: Path) -> dict[str, Any]:
    import re
    analysis = analyze_project(workspace_path)
    java_files = list(workspace_path.rglob("*.java"))
    ast_jsons = parse_java_files(java_files)
    proj_name = state.get("project_name") or workspace_path.name
    clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', proj_name.lower().strip())
    clean_name = re.sub(r'_+', '_', clean_name).strip('_')
    if not clean_name or clean_name[0].isdigit():
        clean_name = "app_" + (clean_name or "project")
    ir = build_project_ir(ast_jsons, project_name=clean_name)
    return {
        "analysis": analysis,
        "ir": ir,
        "stage": "analyzer",
    }


def architecture_node(state: dict[str, Any]) -> dict[str, Any]:
    ir = state["ir"]
    analysis = state.get("analysis", {})
    arch = analyze_architecture(ir, analysis)
    return {
        "architecture": arch,
        "stage": "architecture",
    }


def planner_node(state: dict[str, Any]) -> dict[str, Any]:
    ir = state["ir"]
    arch = state.get("architecture", {})
    plan = create_migration_plan(ir, arch)
    return {
        "plan": plan,
        "stage": "planner",
    }


def dependency_node(state: dict[str, Any], target_language: str) -> dict[str, Any]:
    analysis = state.get("analysis", {})
    source_deps = analysis.get("dependencies", [])
    mapped = map_dependencies(source_deps, target_language)
    return {
        "dependency_mapping": mapped,
        "stage": "dependency",
    }


def translation_node(state: dict[str, Any], output_dir: Path, target_language: str) -> dict[str, Any]:
    ir = state["ir"]
    gen_cls = GENERATORS.get(target_language, PythonGenerator)
    gen = gen_cls()
    generated_files = gen.generate_project(ir, output_dir)

    # Method logic translation injection
    translator = TranslationAgent(target_language)
    file_changes: list[dict[str, Any]] = []

    for gf in generated_files:
        full_p = output_dir / gf.path
        if full_p.exists() and full_p.suffix in (".py", ".ts", ".kt"):
            content = full_p.read_text(encoding="utf-8")
            # Replace placeholder method bodies if possible
            # Refactor code
            content, _ = refactor_code(gf.path, content, target_language)
            full_p.write_text(content, encoding="utf-8")

        file_changes.append({
            "file_path": gf.path,
            "status": gf.status,
            "reason": ", ".join(gf.notes) if gf.notes else "Migrated cleanly",
        })

    # Write manifest file
    mapped_deps = state.get("dependency_mapping", [])
    manifest_name, manifest_content = generate_manifest_content(mapped_deps, target_language, ir.name)
    manifest_path = output_dir / manifest_name
    manifest_path.write_text(manifest_content, encoding="utf-8")
    file_changes.append({
        "file_path": manifest_name,
        "status": "success",
        "reason": "Target dependency manifest generated",
    })

    return {
        "file_changes": file_changes,
        "stage": "translator",
    }


def test_migration_node(state: dict[str, Any], output_dir: Path, target_language: str) -> dict[str, Any]:
    ir = state["ir"]
    test_files = generate_tests_for_project(ir, target_language)
    for tf in test_files:
        p = output_dir / tf["path"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(tf["content"], encoding="utf-8")

    return {
        "stage": "test_migration",
    }


def build_and_repair_node(state: dict[str, Any], output_dir: Path, target_language: str) -> dict[str, Any]:
    repair_attempts: list[dict[str, Any]] = []
    max_attempts = 3

    for attempt_idx in range(1, max_attempts + 1):
        build_res = run_build(output_dir, target_language)
        if build_res["success"]:
            break

        diagnostics = analyze_errors(build_res["output"], target_language)
        if not diagnostics:
            break

        for diag in diagnostics:
            repair_res = attempt_repair(output_dir, diag, target_language)
            repair_attempts.append({
                "attempt_number": attempt_idx,
                "error": diag.message,
                "category": diag.category,
                "file_path": diag.file_path,
                "patch_summary": repair_res.get("patch_summary"),
                "succeeded": repair_res.get("succeeded"),
            })

    test_res = run_tests(output_dir, target_language)

    return {
        "repair_attempts": repair_attempts,
        "test_results": test_res,
        "stage": "repair",
    }


def validation_and_report_node(state: dict[str, Any], output_dir: Path, target_language: str, project_name: str, mode: str) -> dict[str, Any]:
    ir = state["ir"]
    analysis = state.get("analysis", {})
    arch = state.get("architecture", {})
    plan = state.get("plan", {})
    file_changes = state.get("file_changes", [])
    repair_attempts = state.get("repair_attempts", [])
    test_results = state.get("test_results", {})

    validation = validate_project(output_dir, ir, target_language)

    report = generate_migration_report(
        project_name=project_name,
        target_language=target_language,
        mode=mode,
        analysis=analysis,
        architecture=arch,
        plan=plan,
        file_changes=file_changes,
        validation=validation,
        repair_attempts=repair_attempts,
        test_results=test_results,
    )

    return {
        "validation": validation,
        "report": report,
        "stage": "report",
    }
