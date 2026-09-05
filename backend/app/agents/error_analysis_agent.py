"""
Error Analysis Agent (spec section 19).

Parses compilation/build/test outputs, identifies error categories,
and diagnoses root causes for the Repair Agent.
"""
import re
from typing import Any
from pydantic import BaseModel


class DiagnosticError(BaseModel):
    file_path: str
    line_number: int | None = None
    category: str  # syntax_error, type_error, missing_import, name_error, test_failure
    message: str
    raw_trace: str | None = None
    suggested_fix: str | None = None


def analyze_errors(raw_output: str, target_language: str) -> list[DiagnosticError]:
    """
    Parses compiler / test output and produces structured diagnostic errors.
    """
    diagnostics: list[DiagnosticError] = []

    if target_language == "python":
        # Check for SyntaxError / IndentationError / NameError
        # Example: File "calc.py", line 12, in add
        pattern = r'File "([^"]+)", line (\d+)(?:, in .*)?\n\s+(?:[^\n]+\n\s+)?([A-Za-z]+Error:[^\n]+)'
        for match in re.finditer(pattern, raw_output):
            file_path, line_num, msg = match.groups()
            category = "syntax_error" if "SyntaxError" in msg or "IndentationError" in msg else "type_error"
            if "NameError" in msg or "ImportError" in msg:
                category = "missing_import"
            diagnostics.append(DiagnosticError(
                file_path=file_path,
                line_number=int(line_num),
                category=category,
                message=msg.strip(),
                raw_trace=match.group(0),
                suggested_fix="Fix syntax or add missing import",
            ))

        # Check for pytest failure summaries
        if not diagnostics and "FAILED" in raw_output:
            for line in raw_output.splitlines():
                if "FAILED" in line:
                    diagnostics.append(DiagnosticError(
                        file_path="tests",
                        category="test_failure",
                        message=line.strip(),
                        suggested_fix="Review assertion or implementation",
                    ))

    elif target_language == "typescript":
        # TS1234: error message in file.ts(12,5)
        pattern = r'([^\s(]+)\((\d+),\d+\):\s+error\s+(TS\d+):\s+([^\n]+)'
        for match in re.finditer(pattern, raw_output):
            file_path, line_num, code, msg = match.groups()
            diagnostics.append(DiagnosticError(
                file_path=file_path,
                line_number=int(line_num),
                category="type_error" if "type" in msg.lower() else "syntax_error",
                message=f"{code}: {msg}",
                suggested_fix="Fix TypeScript type or syntax declaration",
            ))

    return diagnostics
