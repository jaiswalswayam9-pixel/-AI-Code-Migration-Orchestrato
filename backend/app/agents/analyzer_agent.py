"""
Codebase Analyzer Agent (spec section 2).

As of Phase 6, structural counts (classes/interfaces/enums/methods/fields
and Spring component detection) come from the real JDK Compiler Tree API
AST (java_parser.py / AstDumper.java) instead of the Phase 5 regex
heuristics. Per-file AST parse failures don't abort the whole analysis --
a file that fails to parse is recorded and excluded from structural
counts, consistent with spec section 35's per-file status model.
"""
from pathlib import Path

from app.parsers.pom_parser import parse_pom
from app.parsers.gradle_parser import parse_gradle
from app.parsers.java_parser import parse_java_files, JavaAstBridgeError

_SPRING_ANNOTATIONS = {
    "RestController": "controller",
    "Controller": "controller",
    "Service": "service",
    "Repository": "repository",
    "Entity": "entity",
    "Configuration": "configuration",
}


def _detect_build_tool_and_metadata(workspace: Path) -> dict:
    pom = workspace / "pom.xml"
    if pom.exists():
        meta = parse_pom(pom)
        meta["build_tool"] = "maven"
        return meta

    for gradle_file in ("build.gradle.kts", "build.gradle"):
        path = workspace / gradle_file
        if path.exists():
            meta = parse_gradle(path)
            meta["build_tool"] = "gradle"
            return meta

    return {"build_tool": None, "java_version": None, "dependencies": [], "framework": None, "framework_version": None}


def analyze_project(workspace: Path) -> dict:
    """
    workspace: root directory of the extracted Java project
    (workspace/original/{project_id}/ -- see file_service.py).
    """
    metadata = _detect_build_tool_and_metadata(workspace)
    java_files = list(workspace.rglob("*.java"))

    source_dirs, test_dirs = set(), set()
    for f in java_files:
        parts = f.relative_to(workspace).parts
        if "test" in parts:
            test_dirs.add(str(Path(*parts[: parts.index("test") + 2])) if len(parts) > 1 else "test")
        elif "main" in parts:
            source_dirs.add(str(Path(*parts[: parts.index("main") + 2])) if len(parts) > 1 else "main")

    counts = {"class_count": 0, "interface_count": 0, "enum_count": 0, "method_count": 0}
    component_counts = {"controller": 0, "service": 0, "repository": 0, "entity": 0, "configuration": 0}
    parse_errors: list[dict] = []

    try:
        parsed_files = parse_java_files(java_files)
    except JavaAstBridgeError as e:
        # AST bridge unavailable (e.g. no JDK on this machine) -- degrade
        # to file-count-only rather than failing the whole analysis.
        parsed_files = []
        parse_errors.append({"file": "*", "message": f"AST bridge unavailable: {e}"})

    for pf in parsed_files:
        if pf.get("error"):
            parse_errors.append({"file": pf["file"], "message": pf["error"]})
            continue
        for t in pf.get("types", []):
            kind = t["kind"]
            if kind == "class":
                counts["class_count"] += 1
            elif kind == "interface":
                counts["interface_count"] += 1
            elif kind == "enum":
                counts["enum_count"] += 1
            counts["method_count"] += len(t.get("methods", []))

            all_annotations = set(t.get("annotations", []))
            for f in t.get("fields", []):
                all_annotations.update(f.get("annotations", []))
            for ann, component in _SPRING_ANNOTATIONS.items():
                if ann in t.get("annotations", []):
                    component_counts[component] += 1

    return {
        "java_version": metadata["java_version"],
        "build_tool": metadata["build_tool"],
        "framework": metadata["framework"],
        "framework_version": metadata.get("framework_version"),
        "dependencies": metadata["dependencies"],
        "file_count": len(java_files),
        "source_dirs": sorted(source_dirs),
        "test_dirs": sorted(test_dirs),
        "controller_count": component_counts["controller"],
        "service_count": component_counts["service"],
        "repository_count": component_counts["repository"],
        "entity_count": component_counts["entity"],
        "configuration_count": component_counts["configuration"],
        "parse_errors": parse_errors,
        **counts,
    }
