"""
LangGraph Multi-Agent Orchestrator Workflow (spec section 12-25).

Defines the state-machine graph connecting all 10 specialized agents:
Analyzer -> Architecture -> Planner -> Dependency -> Translator -> Refactoring -> Test -> Build/Repair -> Validation -> Report
"""
from pathlib import Path
from typing import Any, Callable

from app.orchestrator import nodes
from app.orchestrator.events import AgentEvent


def execute_migration_workflow(
    workspace_path: Path,
    output_dir: Path,
    project_name: str,
    target_language: str,
    mode: str,
    event_callback: Callable[[AgentEvent], None] | None = None,
) -> dict[str, Any]:
    """
    Executes the multi-agent migration state machine from start to finish.
    """
    state: dict[str, Any] = {
        "project_name": project_name,
        "target_language": target_language,
        "mode": mode,
    }

    def emit(agent_name: str, stage: str, message: str, status: str = "completed"):
        if event_callback:
            event_callback(AgentEvent(
                agent_name=agent_name,
                stage=stage,
                message=message,
                status=status
            ))

    # Stage 1: Codebase Analyzer
    emit("analyzer", "analyzer", "Parsing Java AST and extracting codebase metrics...")
    res = nodes.analyze_node(state, workspace_path)
    state.update(res)
    emit("analyzer", "analyzer", f"Analysis complete: {state['analysis']['file_count']} Java files parsed.")

    # Stage 2: Architecture Analyzer
    emit("architecture", "architecture", "Detecting architectural layers and framework patterns...")
    res = nodes.architecture_node(state)
    state.update(res)
    emit("architecture", "architecture", f"Architecture mapped: {state['architecture']['architecture_type']}.")

    # Stage 3: Migration Planner
    emit("planner", "planner", "Generating ordered dependency-aware migration plan...")
    res = nodes.planner_node(state)
    state.update(res)
    emit("planner", "planner", f"Migration plan generated: {len(state['plan']['steps'])} phases.")

    # Stage 4: Dependency Mapper
    emit("dependency", "dependency", f"Translating dependencies to {target_language} manifest...")
    res = nodes.dependency_node(state, target_language)
    state.update(res)
    emit("dependency", "dependency", f"Mapped {len(state['dependency_mapping'])} dependencies.")

    # Stage 5: AI Translation & Generators
    emit("translator", "translator", f"Generating {target_language.capitalize()} structures, types, and logic...")
    res = nodes.translation_node(state, output_dir, target_language)
    state.update(res)
    emit("translator", "translator", f"Generated {len(state['file_changes'])} project files.")

    # Stage 6: Test Migration Agent
    emit("test_migration", "test_migration", "Generating unit test suite...")
    res = nodes.test_migration_node(state, output_dir, target_language)
    state.update(res)
    emit("test_migration", "test_migration", "Unit tests created.")

    # Stage 7: Build, Error Analysis & Repair Loop
    emit("repair", "repair", "Validating build syntax and running autonomous repair loop...")
    res = nodes.build_and_repair_node(state, output_dir, target_language)
    state.update(res)
    repairs_count = len(state.get("repair_attempts", []))
    emit("repair", "repair", f"Build verified with {repairs_count} autonomous repair iteration(s).")

    # Stage 8: Validation & Report Agent
    emit("validation", "validation", "Running final quality and type completeness validation...")
    res = nodes.validation_and_report_node(state, output_dir, target_language, project_name, mode)
    state.update(res)
    emit("report", "report", f"Migration finished! Quality score: {state['validation']['score']}%")

    return state
