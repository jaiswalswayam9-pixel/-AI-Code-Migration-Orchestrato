"""
Pydantic request/response schemas for the API layer.
"""
from datetime import datetime
from typing import Literal, Optional, Any
from pydantic import BaseModel


class ProjectResponse(BaseModel):
    project_id: str
    name: str
    uploaded_at: datetime
    file_count: int
    status: Literal["uploaded", "analyzing", "analyzed", "error"]
    analysis: Optional[dict[str, Any]] = None


class ProjectUploadResponse(BaseModel):
    project_id: str
    name: str
    message: str
    analysis: Optional[dict[str, Any]] = None


class MigrationStartRequest(BaseModel):
    project_id: str
    target_language: Literal["python", "typescript", "kotlin"]
    mode: Literal["analyze_only", "suggest", "autonomous"] = "suggest"


class MigrationStartResponse(BaseModel):
    migration_id: str
    project_id: str
    target_language: str
    mode: str
    status: str


class MigrationStatusResponse(BaseModel):
    migration_id: str
    status: Literal["pending", "running", "success", "partial", "failed"]
    progress: dict[str, bool]
    repair_attempts: int
    human_approval_required: bool


class AgentActivityEvent(BaseModel):
    timestamp: datetime
    agent: str
    message: str


class MigrationErrorItem(BaseModel):
    file: str
    message: str
    category: Optional[str] = None


class FileChangeItem(BaseModel):
    file: str
    status: Literal["success", "partial", "failed", "unsupported", "requires_human_review"]
    reason: Optional[str] = None
