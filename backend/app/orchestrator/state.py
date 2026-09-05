"""
WorkflowState: the single source of truth threaded through every
LangGraph node / agent. Agents do not talk to each other directly --
they read and write this shared state object. See docs/agent_design.md.
"""
from typing import Literal, Optional
from pydantic import BaseModel


class ProjectAnalysis(BaseModel):
    java_version: Optional[str] = None
    build_tool: Optional[Literal["maven", "gradle"]] = None
    framework: Optional[str] = None
    file_count: int = 0
    class_count: int = 0
    interface_count: int = 0


class MigrationError(BaseModel):
    file: str
    message: str
    category: Optional[str] = None  # syntax_error, type_error, missing_dependency, ...


class FileStatus(BaseModel):
    status: Literal["success", "partial", "failed", "unsupported", "requires_human_review"]
    reason: Optional[str] = None


class WorkflowState(BaseModel):
    project_id: str
    migration_id: str
    source_language: Literal["java"] = "java"
    target_language: Literal["python", "typescript", "kotlin"]
    mode: Literal["analyze_only", "suggest", "autonomous"] = "suggest"

    project_analysis: Optional[ProjectAnalysis] = None
    ir: Optional[dict] = None  # replaced with IRProject once ir/models.py is implemented
    migration_plan: Optional[dict] = None
    dependency_mapping: list[dict] = []

    generated_files: dict[str, str] = {}
    file_status: dict[str, FileStatus] = {}

    build_success: Optional[bool] = None
    test_pass_count: int = 0
    test_fail_count: int = 0
    errors: list[MigrationError] = []
    repair_attempts: int = 0
    max_repair_attempts: int = 3

    status: Literal["pending", "running", "success", "partial", "failed"] = "pending"
    human_approval_required: bool = False
