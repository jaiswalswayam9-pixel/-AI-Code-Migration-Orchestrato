"""
Python-side bridge to the JDK Compiler Tree API AST dumper
(java_ast_bridge/src/AstDumper.java -- see that file\'s docstring for why
this uses the JDK\'s own compiler frontend instead of JavaParser).

parse_java_files() shells out to a compiled AstDumper and parses its
newline-delimited JSON output. One `java` invocation handles an entire
batch of files (JVM startup cost is real -- a few hundred ms -- so we
never invoke it once per file).
"""
import json
import subprocess
from pathlib import Path

_BRIDGE_DIR = Path(__file__).parent / "java_ast_bridge"
_BIN_DIR = _BRIDGE_DIR / "bin"


class JavaAstBridgeError(RuntimeError):
    pass


def ensure_compiled() -> None:
    """Compile AstDumper.java if bin/ is missing or empty. Idempotent."""
    if _BIN_DIR.exists() and any(_BIN_DIR.glob("*.class")):
        return
    _BIN_DIR.mkdir(parents=True, exist_ok=True)
    src = _BRIDGE_DIR / "src" / "AstDumper.java"
    proc = subprocess.run(
        ["javac", "-d", str(_BIN_DIR), str(src)],
        capture_output=True, text=True, timeout=60,
    )
    if proc.returncode != 0:
        raise JavaAstBridgeError(f"Failed to compile AstDumper: {proc.stderr}")


def parse_java_files(paths: list[Path]) -> list[dict]:
    """
    Returns one dict per input file, each shaped like:
    {"file": ..., "package": ..., "imports": [...], "types": [...],
     "diagnostics": [...], "error": str | None}

    A per-file "error" does not raise -- callers decide whether a
    syntax-broken file should block the whole batch or just get flagged
    UNSUPPORTED/REQUIRES_HUMAN_REVIEW (spec section 35) downstream.
    """
    if not paths:
        return []
    ensure_compiled()

    proc = subprocess.run(
        ["java", "-cp", str(_BIN_DIR), "AstDumper", *[str(p) for p in paths]],
        capture_output=True, text=True, timeout=120,
    )
    if proc.returncode != 0 and not proc.stdout.strip():
        raise JavaAstBridgeError(f"AstDumper failed: {proc.stderr}")

    results = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        results.append(json.loads(line))
    return results


def parse_java_file(path: Path) -> dict:
    results = parse_java_files([path])
    return results[0] if results else {"file": str(path), "error": "No output from AstDumper"}
