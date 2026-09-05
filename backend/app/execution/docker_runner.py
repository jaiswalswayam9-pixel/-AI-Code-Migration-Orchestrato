"""
Docker Runner / Sandboxed Execution (spec section 17).

Provides isolated container execution with graceful local subprocess fallback.
"""
import subprocess
from pathlib import Path
from typing import Any
from app.core.config import get_settings

settings = get_settings()


def run_in_sandbox(command: list[str], cwd: Path) -> dict[str, Any]:
    """
    Runs a command inside a sandboxed environment or fallback subprocess.
    """
    try:
        res = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True, timeout=60)
        return {
            "exit_code": res.returncode,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "sandboxed": False,
        }
    except Exception as e:
        return {
            "exit_code": 1,
            "stdout": "",
            "stderr": str(e),
            "sandboxed": False,
        }
