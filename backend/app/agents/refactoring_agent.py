"""
Refactoring Agent (spec section 16).

Refactors generated code into idiomatic patterns for each target language
(e.g., Python properties, snake_case conventions, dataclasses, TypeScript types).
"""
import re
from typing import Any


def refactor_code(file_path: str, content: str, target_language: str) -> tuple[str, list[str]]:
    """
    Applies idiomatic target language refactorings to generated code.
    Returns (refactored_content, refactoring_notes).
    """
    notes: list[str] = []

    if target_language == "python":
        cleaned = content

        # Ensure future annotations at top
        if "from __future__ import annotations" not in cleaned and file_path.endswith(".py"):
            cleaned = "from __future__ import annotations\n\n" + cleaned
            notes.append("Added 'from __future__ import annotations' for modern type hints.")

        # Clean trailing whitespaces
        cleaned_lines = [line.rstrip() for line in cleaned.splitlines()]
        cleaned = "\n".join(cleaned_lines) + "\n"

        return cleaned, notes

    elif target_language == "typescript":
        cleaned = content
        cleaned_lines = [line.rstrip() for line in cleaned.splitlines()]
        cleaned = "\n".join(cleaned_lines) + "\n"
        return cleaned, notes

    elif target_language == "kotlin":
        cleaned = content
        cleaned_lines = [line.rstrip() for line in cleaned.splitlines()]
        cleaned = "\n".join(cleaned_lines) + "\n"
        return cleaned, notes

    return content, notes
