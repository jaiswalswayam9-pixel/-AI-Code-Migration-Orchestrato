"""
Diff Manager (spec section 21 & 24).

Generates unified diffs and side-by-side comparison models for migrated files.
"""
import difflib
from pathlib import Path
from typing import Any


def generate_file_diff(original_content: str, new_content: str, from_file: str, to_file: str) -> dict[str, Any]:
    """
    Generates unified diff text and structured line changes between two file contents.
    """
    orig_lines = original_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)

    clean_from = from_file.replace("\\", "/")
    clean_to = to_file.replace("\\", "/")

    diff_lines = list(difflib.unified_diff(
        orig_lines,
        new_lines,
        fromfile=clean_from,
        tofile=clean_to,
        n=3
    ))

    unified_diff_text = "".join(diff_lines)

    # Calculate additions and deletions
    additions = sum(1 for line in diff_lines if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in diff_lines if line.startswith("-") and not line.startswith("---"))

    file_path = clean_to if clean_to != "/dev/null" else clean_from

    return {
        "from_file": clean_from,
        "to_file": clean_to,
        "file_path": file_path,
        "unified_diff": unified_diff_text,
        "diff_content": unified_diff_text,
        "original_code": original_content,
        "migrated_code": new_content,
        "additions": additions,
        "deletions": deletions,
    }


def compute_migration_diffs(source_workspace: Path, target_output_dir: Path) -> list[dict[str, Any]]:
    """
    Compares source Java files with corresponding generated target files.
    """
    diffs: list[dict[str, Any]] = []

    if not source_workspace.exists() or not target_output_dir.exists():
        return diffs

    java_files = list(source_workspace.rglob("*.java"))
    matched_target_files = set()

    for jf in java_files:
        stem = jf.stem.lower()
        orig_code = jf.read_text(encoding="utf-8", errors="ignore")

        # Find matching target file (first exact stem match, then substring)
        matched_target = None
        for tf in target_output_dir.rglob("*"):
            if tf.is_file() and not tf.name.endswith(".zip") and not tf.name.endswith(".pyc") and "__pycache__" not in str(tf):
                if tf.stem.lower() == stem:
                    matched_target = tf
                    matched_target_files.add(tf)
                    break

        if not matched_target:
            for tf in target_output_dir.rglob("*"):
                if tf.is_file() and not tf.name.endswith(".zip") and not tf.name.endswith(".pyc") and "__pycache__" not in str(tf):
                    if stem in tf.name.lower() and not tf.name.startswith("test_"):
                        matched_target = tf
                        matched_target_files.add(tf)
                        break

        if matched_target:
            target_code = matched_target.read_text(encoding="utf-8", errors="ignore")
            diff = generate_file_diff(
                orig_code,
                target_code,
                str(jf.relative_to(source_workspace)),
                str(matched_target.relative_to(target_output_dir)),
            )
            diffs.append(diff)
        else:
            diff = generate_file_diff(
                orig_code,
                "",
                str(jf.relative_to(source_workspace)),
                "/dev/null",
            )
            diffs.append(diff)

    # Now add remaining generated files (e.g. tests, configs, init, manifests)
    for tf in target_output_dir.rglob("*"):
        if tf.is_file() and not tf.name.endswith(".zip") and not tf.name.endswith(".pyc") and "__pycache__" not in str(tf) and tf not in matched_target_files:
            target_code = tf.read_text(encoding="utf-8", errors="ignore")
            diff = generate_file_diff(
                "",
                target_code,
                "/dev/null",
                str(tf.relative_to(target_output_dir)),
            )
            diffs.append(diff)

    return diffs
