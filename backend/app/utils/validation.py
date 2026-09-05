"""
Validation utilities for files, projects, and migrations.
"""
from pathlib import Path


def is_valid_java_project(directory: Path) -> bool:
    """Check if the directory contains Java sources or build files."""
    if not directory.exists() or not directory.is_dir():
        return False
    has_java = any(directory.rglob("*.java"))
    has_build = (directory / "pom.xml").exists() or (directory / "build.gradle").exists() or (directory / "build.gradle.kts").exists()
    return has_java or has_build


def get_supported_target_languages() -> list[str]:
    return ["python", "typescript", "kotlin"]
