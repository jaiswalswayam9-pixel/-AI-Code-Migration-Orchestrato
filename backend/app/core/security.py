"""
Security helpers for path traversal prevention and input sanitization.
"""
from pathlib import Path


def is_safe_path(base_dir: Path, target_path: Path) -> bool:
    """Ensure target_path does not escape outside base_dir."""
    try:
        base = base_dir.resolve()
        target = target_path.resolve()
        return base in target.parents or base == target
    except Exception:
        return False


def sanitize_filename(filename: str) -> str:
    """Remove dangerous characters from a filename."""
    import re
    cleaned = re.sub(r'[^\w\-_\. ]', '_', filename)
    return cleaned.strip(' .') or "unnamed"
