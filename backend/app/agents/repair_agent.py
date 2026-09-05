"""
Autonomous Repair Agent (spec section 20).

Synthesizes and applies targeted code patches to fix syntax errors, missing imports,
and type mismatches detected by the Error Analysis Agent.
"""
from pathlib import Path
from typing import Any
from app.agents.error_analysis_agent import DiagnosticError


def attempt_repair(output_dir: Path, error: DiagnosticError, target_language: str) -> dict[str, Any]:
    """
    Attempts to autonomously repair an error in a generated project file.
    Returns: {"succeeded": bool, "patch_summary": str, "file_path": str}
    """
    target_file = output_dir / error.file_path
    if not target_file.exists():
        # Try matching basename in output_dir
        matches = list(output_dir.rglob(Path(error.file_path).name))
        if matches:
            target_file = matches[0]
        else:
            return {"succeeded": False, "patch_summary": f"Target file not found: {error.file_path}", "file_path": error.file_path}

    content = target_file.read_text(encoding="utf-8")
    patched = False
    patch_summary = ""

    if error.category == "missing_import" or "NameError" in error.message:
        # Check if missing typical imports like List, Dict, Optional, etc.
        if "name 'List'" in error.message or "name 'Dict'" in error.message or "name 'Optional'" in error.message:
            if "from typing import" not in content:
                content = "from typing import List, Dict, Optional, Any, Set\n" + content
                patched = True
                patch_summary = "Added missing 'from typing import List, Dict, Optional, Any, Set'"

    elif error.category == "syntax_error":
        # Fix common syntax glitches like trailing commas in def or duplicate colons
        lines = content.splitlines()
        if error.line_number and 1 <= error.line_number <= len(lines):
            idx = error.line_number - 1
            bad_line = lines[idx]
            # If line has empty body or unindented pass
            if bad_line.strip().endswith(":") and (idx + 1 >= len(lines) or not lines[idx + 1].startswith(" ")):
                lines.insert(idx + 1, "    pass")
                patched = True
                patch_summary = f"Inserted 'pass' statement on line {error.line_number + 1}"
            content = "\n".join(lines) + "\n"

    if patched:
        target_file.write_text(content, encoding="utf-8")
        return {
            "succeeded": True,
            "patch_summary": patch_summary or f"Applied automated repair for {error.category}",
            "file_path": str(target_file.relative_to(output_dir)),
        }

    return {
        "succeeded": False,
        "patch_summary": f"Could not automatically resolve {error.category}: {error.message}",
        "file_path": str(target_file.relative_to(output_dir)),
    }
