"""
Filesystem helpers shared by file_service and later phases.
"""
from pathlib import Path

WORKSPACE_ROOT = Path("workspace")
MAX_ZIP_SIZE_BYTES = 100 * 1024 * 1024  # 100MB -- generous for an academic sample project


def workspace_original_dir(project_id: str) -> Path:
    return WORKSPACE_ROOT / "original" / project_id


def workspace_working_dir(project_id: str) -> Path:
    return WORKSPACE_ROOT / "working" / project_id


def workspace_generated_dir(migration_id: str) -> Path:
    return WORKSPACE_ROOT / "generated" / migration_id
