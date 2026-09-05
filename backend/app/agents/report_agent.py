"""
Report Agent (spec section 25 & 36).

Synthesizes executive summary, structural metrics, conversion confidence,
test results, and next steps into a comprehensive migration report.
"""
from typing import Any
from datetime import datetime, timezone


def generate_migration_report(
    project_name: str,
    target_language: str,
    mode: str,
    analysis: dict[str, Any],
    architecture: dict[str, Any],
    plan: dict[str, Any],
    file_changes: list[dict[str, Any]],
    validation: dict[str, Any],
    repair_attempts: list[dict[str, Any]],
    test_results: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Builds the final structured report payload.
    """
    total_files = len(file_changes)
    success_files = len([f for f in file_changes if f.get("status") == "success"])
    partial_files = len([f for f in file_changes if f.get("status") == "partial"])
    review_files = len([f for f in file_changes if f.get("status") in ("requires_human_review", "failed")])

    score = validation.get("score", 90.0)

    summary = (
        f"Autonomous migration of Java project '{project_name}' to {target_language.capitalize()} "
        f"completed with an overall quality score of {score}/100. "
        f"{success_files} file(s) converted with full confidence, {partial_files} file(s) converted structurally, "
        f"and {review_files} file(s) flagged for human review."
    )

    markdown_report = f"""# Code Migration Report: {project_name} -> {target_language.capitalize()}

**Generated at:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}  
**Migration Mode:** {mode.capitalize()}  
**Overall Quality Score:** {score}% ({validation.get('status', 'SUCCESS')})

---

## 1. Executive Summary
{summary}

## 2. Architecture Transition
- **Source Framework:** {architecture.get('source_framework', 'Standard Java')}
- **Target Stack:** {architecture.get('recommendations', {}).get(target_language, 'Target Package')}
- **Architecture Pattern:** {architecture.get('architecture_type', 'Layered')}

## 3. Migration Statistics
- **Total Source Files:** {analysis.get('file_count', total_files)}
- **Classes Converted:** {analysis.get('class_count', 0)}
- **Interfaces Converted:** {analysis.get('interface_count', 0)}
- **Methods Migrated:** {analysis.get('method_count', 0)}
- **Generated Target Files:** {total_files}
- **Autonomous Repair Loops:** {len(repair_attempts)}

## 4. File-by-File Breakdown
| File | Status | Notes / Reason |
| --- | --- | --- |
"""
    for f in file_changes:
        markdown_report += f"| `{f.get('file_path')}` | **{f.get('status', 'success').upper()}** | {f.get('reason') or 'Cleanly migrated'} |\n"

    markdown_report += f"""
## 5. Next Steps for Development Team
1. Review generated dependencies in manifest.
2. Inspect methods flagged with `requires_human_review` if any.
3. Run the automated test suite using the target build tool.
"""

    return {
        "project_name": project_name,
        "target_language": target_language,
        "mode": mode,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "score": score,
        "status": validation.get("status", "SUCCESS"),
        "summary": summary,
        "markdown": markdown_report,
        "statistics": {
            "total_files": total_files,
            "success_files": success_files,
            "partial_files": partial_files,
            "review_files": review_files,
            "classes_count": analysis.get("class_count", 0),
            "methods_count": analysis.get("method_count", 0),
            "repair_attempts_count": len(repair_attempts),
        },
        "validation": validation,
        "file_changes": file_changes,
        "repair_attempts": repair_attempts,
        "test_results": test_results or {"passed": 0, "failed": 0},
    }
