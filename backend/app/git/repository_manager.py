"""
Repository Manager (spec section 21).

Manages project workspaces, branch isolation, and cleanup.
"""
import shutil
from pathlib import Path


class RepositoryManager:
    @staticmethod
    def prepare_workspace(base_path: Path, project_id: str) -> Path:
        target = base_path / project_id
        target.mkdir(parents=True, exist_ok=True)
        return target

    @staticmethod
    def cleanup_workspace(workspace: Path) -> None:
        if workspace.exists():
            shutil.rmtree(workspace, ignore_errors=True)
