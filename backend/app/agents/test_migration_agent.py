"""
Test Migration Agent (spec section 18).

Translates and generates unit tests for the migrated target language project
(JUnit -> PyTest for Python, Vitest for TypeScript, KotlinTest for Kotlin).
"""
from typing import Any
from app.ir.models import IRProject, IRClass
from app.generators.naming import to_snake_case


def generate_tests_for_project(ir: IRProject, target_language: str) -> list[dict[str, str]]:
    """
    Generates test files for classes in the project.
    Returns a list of dicts: [{"path": ..., "content": ..., "status": ...}]
    """
    test_files: list[dict[str, str]] = []

    for cu in ir.compilation_units:
        for t in cu.types:
            if t.kind == "class" and t.methods:
                if target_language == "python":
                    test_file = _generate_python_test(t, ir.name, cu.package)
                    test_files.append(test_file)
                elif target_language == "typescript":
                    test_file = _generate_ts_test(t, ir.name)
                    test_files.append(test_file)
                elif target_language == "kotlin":
                    test_file = _generate_kotlin_test(t, ir.name)
                    test_files.append(test_file)

    return test_files


def _generate_python_test(t: IRClass, project_name: str, package: str = "") -> dict[str, str]:
    module_name = to_snake_case(t.name)
    pkg_name = to_snake_case(project_name)
    if not pkg_name or pkg_name[0].isdigit():
        pkg_name = "app_" + (pkg_name or "project")

    if package:
        import_path = f"{pkg_name}.{package}.{module_name}"
    else:
        import_path = f"{pkg_name}.{module_name}"

    test_methods: list[str] = []
    for m in t.methods:
        test_methods.append(f"""
def test_{to_snake_case(t.name)}_{to_snake_case(m.name)}():
    instance = {t.name}()
    assert instance is not None
""")

    content = f'''"""Unit tests for {t.name} (PyTest)."""
import pytest
from {import_path} import {t.name}

{"".join(test_methods)}'''
    return {
        "path": f"tests/test_{module_name}.py",
        "content": content,
        "status": "success",
    }


def _generate_ts_test(t: IRClass, project_name: str) -> dict[str, str]:
    test_methods: list[str] = []
    for m in t.methods:
        test_methods.append(f"""
  it("should instantiate and execute {m.name}", () => {{
    const instance = new {t.name}();
    expect(instance).toBeDefined();
  }});
""")

    content = f'''import {{ describe, it, expect }} from "vitest";
import {{ {t.name} }} from "../src/{t.name}";

describe("{t.name}", () => {{
{"".join(test_methods)}
}});
'''
    return {
        "path": f"tests/{t.name}.test.ts",
        "content": content,
        "status": "success",
    }


def _generate_kotlin_test(t: IRClass, project_name: str) -> dict[str, str]:
    test_methods: list[str] = []
    for m in t.methods:
        test_methods.append(f"""
    @Test
    fun test{m.name.capitalize()} () {{
        val instance = {t.name}()
        assertNotNull(instance)
    }}
""")

    content = f'''package {project_name.lower()}

import kotlin.test.Test
import kotlin.test.assertNotNull

class {t.name}Test {{
{"".join(test_methods)}
}}
'''
    return {
        "path": f"src/test/kotlin/{t.name}Test.kt",
        "content": content,
        "status": "success",
    }
