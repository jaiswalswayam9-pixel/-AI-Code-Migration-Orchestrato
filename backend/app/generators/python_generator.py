"""
Python target-language generator (spec section 8, Python Generator).

Structural only: fields, method/constructor SIGNATURES, class hierarchy,
enums-as-Enum, interfaces-as-ABC. Method BODIES are never translated here
-- that is the AI Translation Agent's job (spec section 7 / Phase 14),
which works file-by-file on real logic, not on the IR. Every generated
method gets a clearly marked `raise NotImplementedError(...)` body, and
every file containing at least one method is marked "partial" (spec
section 35), never "success" -- "success" is reserved for files where
nothing was left for a human/agent to still do.
"""
from pathlib import Path

from app.generators.base_generator import BaseLanguageGenerator, GeneratedFile, FileStatus
from app.generators.naming import ProjectRegistry, to_snake_case, package_to_path
from app.ir.models import IRProject, IRClass, IRCompilationUnit, IRType
from app.rules.rule_engine import get_rule_engine


class PythonGenerator(BaseLanguageGenerator):
    language = "python"
    file_extension = ".py"

    def __init__(self):
        self.rule_engine = get_rule_engine("python")

    # ---------- public entry point ----------

    def generate_project(self, ir: IRProject, output_dir: Path) -> list[GeneratedFile]:
        root_package = to_snake_case(ir.name)
        registry = ProjectRegistry(ir, root_package)

        results: list[GeneratedFile] = []
        package_dirs: set[Path] = {Path(root_package)}

        for cu in ir.compilation_units:
            pkg_path = package_to_path(cu.package)
            dir_path = Path(root_package) / pkg_path if pkg_path else Path(root_package)
            package_dirs.add(dir_path)
            for parent in list(dir_path.parents):
                if parent != Path("."):
                    package_dirs.add(parent)

            if cu.parse_error:
                results.append(GeneratedFile(
                    path=str(dir_path / "PARSE_ERROR.txt"),
                    content=f"Source file could not be parsed: {cu.file}\nError: {cu.parse_error}\n",
                    status="failed",
                    notes=[cu.parse_error],
                ))
                continue

            for t in cu.types:
                results.append(self._generate_type_file(t, cu, registry, dir_path))

        # __init__.py for every package directory (including the root),
        # so the generated tree is a real importable Python package.
        for d in package_dirs:
            results.append(GeneratedFile(path=str(d / "__init__.py"), content="", status="success"))

        results.append(GeneratedFile(
            path="requirements.txt",
            content="# Dependencies are mapped by the Dependency Mapping Agent (spec section 9) -- not yet implemented.\n",
            status="success",
        ))

        for r in results:
            full_path = output_dir / r.path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(r.content)

        return results

    # ---------- per-type generation ----------

    def _generate_type_file(self, t: IRClass, cu: IRCompilationUnit, registry: ProjectRegistry, dir_path: Path) -> GeneratedFile:
        notes: list[str] = []
        confidences: list[str] = []
        referenced_classes: set[str] = set()

        def collect_classes(ir_type: IRType) -> None:
            if ir_type.kind == "class" and registry.is_project_local(ir_type.name) and ir_type.name != t.name:
                referenced_classes.add(ir_type.name)
            for arg in ir_type.type_args:
                collect_classes(arg)

        def map_type(ir_type: IRType) -> str:
            result = self.rule_engine.map_type(ir_type)
            notes.extend(result.notes)
            confidences.append(result.confidence)
            collect_classes(ir_type)
            return result.target

        is_interface = t.kind == "interface"
        is_enum = t.kind == "enum"
        use_dataclass = (not is_interface and not is_enum and not t.constructors and bool(t.fields))

        # ---- base classes ----
        base_classes: list[str] = []
        if is_interface:
            base_classes.append("ABC")
        elif is_enum:
            base_classes.append("Enum")
        else:
            if t.extends:
                base_name = t.extends[0].split("<")[0].strip()
                base_classes.append(base_name)
                if registry.is_project_local(base_name):
                    referenced_classes.add(base_name)
                else:
                    notes.append(f"Base class '{base_name}' is external/unresolved in this project.")
            for impl in t.implements:
                base_name = impl.split("<")[0].strip()
                if registry.is_project_local(base_name):
                    referenced_classes.add(base_name)
                    base_classes.append(base_name)
                else:
                    notes.append(f"Implemented interface '{impl}' is external/unresolved -- not added as a Python base class.")

        # ---- body: fields ----
        field_names = {f.name for f in t.fields}
        field_lines: list[str] = []
        if is_enum:
            if not t.fields:
                field_lines.append("    pass")
            for f in t.fields:
                field_lines.append(f"    {f.name} = auto()")
        else:
            for f in t.fields:
                ann = map_type(f.type)
                if use_dataclass:
                    field_lines.append(f"    {f.name}: {ann}")
                else:
                    field_lines.append(f"    {f.name}: {ann} = None  # type-hint only; see __init__ for assignment" if t.constructors else f"    {f.name}: {ann}")

        # ---- body: constructor(s) ----
        ctor_lines: list[str] = []
        if t.constructors and not is_enum:
            if len(t.constructors) > 1:
                notes.append(f"Java class has {len(t.constructors)} constructors; Python supports one __init__ -- only the first was used.")
            ctor = t.constructors[0]
            params_sig = "".join(f", {p.name}: {map_type(p.type)}" for p in ctor.parameters)
            ctor_lines.append("")
            ctor_lines.append(f"    def __init__(self{params_sig}) -> None:")
            if ctor.body and ctor.body.statements:
                from app.agents.translation_agent import TranslationAgent
                translator = TranslationAgent("python", class_fields=field_names)
                body_code = translator.translate_method_body(ctor, indent="        ")
                ctor_lines.append(body_code)
            else:
                if not ctor.parameters:
                    ctor_lines.append("        pass")
                for p in ctor.parameters:
                    if p.name in field_names:
                        ctor_lines.append(f"        self.{p.name} = {p.name}")
                    else:
                        ctor_lines.append(f"        self.{p.name} = {p.name}  # no matching field found on source class -- verify")

        # ---- body: methods ----
        method_lines: list[str] = []
        for m in t.methods:
            params_sig = "".join(f", {p.name}: {map_type(p.type)}" for p in m.parameters)
            ret = map_type(m.return_type)
            method_lines.append("")
            if is_interface:
                method_lines.append("    @abstractmethod")
                method_lines.append(f"    def {m.name}(self{params_sig}) -> {ret}:")
                method_lines.append("        pass")
            else:
                method_lines.append(f"    def {m.name}(self{params_sig}) -> {ret}:")
                if m.body and m.body.statements:
                    from app.agents.translation_agent import TranslationAgent
                    translator = TranslationAgent("python", class_fields=field_names)
                    body_code = translator.translate_method_body(m, indent="        ")
                    method_lines.append(body_code)
                else:
                    method_lines.append("        pass")

        # ---- assemble class body ----
        body_lines = field_lines + ctor_lines + method_lines
        if not body_lines:
            body_lines = ["    pass"]

        # ---- imports ----
        import_lines = ["from __future__ import annotations", ""]
        if is_interface:
            import_lines.append("from abc import ABC, abstractmethod")
        if is_enum:
            import_lines.append("from enum import Enum, auto")
        if use_dataclass:
            import_lines.append("from dataclasses import dataclass")
        for cls_name in sorted(referenced_classes):
            module = registry.module_for(cls_name)
            if module:
                import_lines.append(f"from {module} import {cls_name}")

        decorator = "@dataclass\n" if use_dataclass else ""
        base_str = f"({', '.join(base_classes)})" if base_classes else ""
        class_header = f"{decorator}class {t.name}{base_str}:"

        docstring = (
            f'"""Auto-generated from {cu.file} (Java {t.kind}) -- structural migration only.\n'
            f"Method bodies are NOT translated; see AI Translation Agent (Phase 14).\n"
            f'Review before use."""'
        )

        source = docstring + "\n\n" + "\n".join(import_lines) + "\n\n\n" + class_header + "\n" + "\n".join(body_lines) + "\n"

        # ---- status per spec section 35 ----
        status: FileStatus = "success"
        if "low" in confidences:
            status = "requires_human_review"
        elif t.methods:
            status = "partial"  # structure done, logic not translated

        module_name = to_snake_case(t.name)
        return GeneratedFile(path=str(dir_path / f"{module_name}.py"), content=source, status=status, notes=notes)
