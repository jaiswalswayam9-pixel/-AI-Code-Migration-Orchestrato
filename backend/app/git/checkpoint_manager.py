"""
Git Checkpoint Manager (spec section 21).

Creates commits and snapshots at each stage of the migration workflow,
allowing rollbacks and historical revision inspections.
"""
import subprocess
from pathlib import Path
from typing import Any


class CheckpointManager:
    def __init__(self, workspace_path: Path):
        self.workspace = workspace_path
        self._ensure_git_init()

    def _ensure_git_init(self) -> None:
        if not (self.workspace / ".git").exists():
            try:
                subprocess.run(["git", "init"], cwd=str(self.workspace), capture_output=True, text=True)
                subprocess.run(["git", "config", "user.name", "AI Migration Orchestrator"], cwd=str(self.workspace), capture_output=True)
                subprocess.run(["git", "config", "user.email", "orchestrator@migration.ai"], cwd=str(self.workspace), capture_output=True)
            except Exception:
                pass

    def create_checkpoint(self, stage_name: str, message: str) -> str | None:
        """
        Commits current directory state as a milestone checkpoint.
        Returns commit hash or None.
        """
        try:
            subprocess.run(["git", "add", "."], cwd=str(self.workspace), capture_output=True, text=True)
            res = subprocess.run(
                ["git", "commit", "-m", f"checkpoint({stage_name}): {message}"],
                cwd=str(self.workspace),
                capture_output=True,
                text=True,
            )
            # Retrieve HEAD hash
            hash_res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(self.workspace), capture_output=True, text=True)
            return hash_res.stdout.strip() if hash_res.returncode == 0 else stage_name
        except Exception:
            return stage_name

    def list_checkpoints(self) -> list[dict[str, str]]:
        """Returns list of commits."""
        try:
            res = subprocess.run(["git", "log", "--oneline", "-n", "10"], cwd=str(self.workspace), capture_output=True, text=True)
            commits = []
            for line in res.stdout.splitlines():
                if " " in line:
                    h, msg = line.split(" ", 1)
                    commits.append({"hash": h, "message": msg})
            return commits
        except Exception:
            return []
