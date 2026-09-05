"""
Kotlin target-language generator (spec section 8, Kotlin Generator).

Structural only -- same boundary as the Python/TypeScript generators.
Kotlin idioms used deliberately:
  - primary constructor with val/var parameters (Kotlin's standard way
    of declaring a class with constructor-assigned fields), instead of a
    separate constructor body + field declarations
  - `val` for fields whose Java modifiers include "final", `var` otherwise
  - `TODO("...")` for unmigrated method bodies -- Kotlin's own stdlib
    function for exactly this purpose, which throws NotImplementedError
  - a real `package` declaration per file, so same-package references
    need no import at all (unlike TypeScript's always-relative imports)
"""
from pathlib import Path

from app.generators.base_generator import BaseLanguageGenerator, GeneratedFile, FileStatus
from app.generators.naming import KotlinProjectRegistry, package_to_path
from app.ir.models import IRProject, IRClass, IRCompilationUnit, IRType
from app.rules.rule_engine import get_rule_engine


class KotlinGenerator(BaseLanguageGenerator):
    language = "kotlin"
    file_extension = ".kt"

    def __init__(self):
        self.rule_engine = get_rule_engine("kotlin")

    def generate_project(self, ir: IRProject, output_dir: Path) -> list[GeneratedFile]:
        registry = KotlinProjectRegistry(ir)
        results: list[GeneratedFile] = []

        for cu in ir.compilation_units:
            src_dir = Path("src/main/kotlin") / package_to_path(cu.package)

            if cu.parse_error:
                results.append(GeneratedFile(
                    path=str(src_dir / "PARSE_ERROR.txt"),
                    content=f"Source file could not be parsed: {cu.file}\nError: {cu.parse_error}\n",
                    status="failed", notes=[cu.parse_error],
                ))
                continue

            for t in cu.types:
                results.append(self._generate_type_file(t, cu, registry, src_dir))

        results.append(GeneratedFile(path="build.gradle.kts", content=self._build_gradle(), status="success"))

        for r in results:
            full_path = output_dir / r.path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(r.content)

        return results

    def _generate_type_file(self, t: IRClass, cu: IRCompilationUnit, registry: KotlinProjectRegistry, src_dir: Path) -> GeneratedFile:
        notes: list[str] = []
        confidences: list[str] = []
        referenced_classes: set[str] = set()
        pkg = cu.package or ""

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

        # ---- supertypes ----
        supertypes: list[str] = []
        if is_interface:
            for ext in t.extends:
                name = ext.split("<")[0].strip()
                supertypes.append(name)
                if registry.is_project_local(name):
                    referenced_classes.add(name)
                else:
                    notes.append(f"Extended interface '{ext}' is external/unresolved.")
        elif not is_enum:
            if t.extends:
                name = t.extends[0].split("<")[0].strip()
                supertypes.append(f"{name}()")
                if registry.is_project_local(name):
                    referenced_classes.add(name)
                else:
                    notes.append(f"Base class '{name}' is external/unresolved in this project.")
            for impl in t.implements:
                name = impl.split("<")[0].strip()
                if registry.is_project_local(name):
                    referenced_classes.add(name)
                    supertypes.append(name)
                else:
                    notes.append(f"Implemented interface '{impl}' is external/unresolved -- not added as a Kotlin supertype.")

        # ---- primary constructor (classes only) ----
        primary_ctor = ""
        field_names_in_ctor: set[str] = set()
        if not is_interface and not is_enum and t.constructors:
            if len(t.constructors) > 1:
                notes.append(f"Java class has {len(t.constructors)} constructors; only the first was used -- others require manual merging.")
            ctor = t.constructors[0]
            field_map = {f.name: f for f in t.fields}
            params = []
            for p in ctor.parameters:
                ann = map_type(p.type)
                if p.name in field_map:
                    mutability = "val" if "final" in field_map[p.name].modifiers else "var"
                    visibility = "private " if "private" in field_map[p.name].modifiers else ""
                    params.append(f"{visibility}{mutability} {p.name}: {ann}")
                    field_names_in_ctor.add(p.name)
                else:
                    params.append(f"{p.name}: {ann}")
                    notes.append(f"Constructor param '{p.name}' has no matching field -- included but not stored as a property.")
            primary_ctor = f"({', '.join(params)})"

        # ---- body ----
        body_lines: list[str] = []
        property_names = {f.name for f in t.fields}

        def is_redundant_accessor(method_name: str, param_count: int) -> str | None:
            """Returns the field name this method would redundantly
            duplicate, or None. Kotlin auto-generates get/set accessors
            for every var/val property -- an explicit Java-style
            getX()/setX() with the same target causes a real JVM
            signature clash (confirmed via kotlinc, not a hypothetical)."""
            if param_count == 0 and method_name.startswith("get") and len(method_name) > 3:
                candidate = method_name[3].lower() + method_name[4:]
            elif param_count == 0 and method_name.startswith("is") and len(method_name) > 2:
                candidate = method_name[2].lower() + method_name[3:]
            elif param_count == 1 and method_name.startswith("set") and len(method_name) > 3:
                candidate = method_name[3].lower() + method_name[4:]
            else:
                return None
            return candidate if candidate in property_names else None

        if is_enum:
            const_line = "    " + ", ".join(f.name for f in t.fields) if t.fields else "    // no enum constants found"
            body_lines.append(const_line + (";" if t.methods else ""))
        else:
            # fields not covered by the primary constructor
            for f in t.fields:
                if f.name in field_names_in_ctor:
                    continue
                ann = map_type(f.type)
                mutability = "val" if "final" in f.modifiers else "var"
                if is_interface:
                    body_lines.append(f"    val {f.name}: {ann}")
                else:
                    body_lines.append(f"    {mutability} {f.name}: {ann}? = null")
                    notes.append(f"Field '{f.name}' has no constructor -- declared nullable with a null default; verify.")

        for m in t.methods:
            redundant_for = is_redundant_accessor(m.name, len(m.parameters))
            if redundant_for and not is_interface:
                notes.append(
                    f"Method '{m.name}' is a JavaBean-style accessor for property '{redundant_for}' -- "
                    f"omitted because Kotlin properties auto-generate this (avoids a JVM signature clash)."
                )
                continue
            params_sig = ", ".join(f"{p.name}: {map_type(p.type)}" for p in m.parameters)
            ret = map_type(m.return_type)
            ret_clause = "" if ret == "Unit" else f": {ret}"
            if is_interface:
                body_lines.append(f"    fun {m.name}({params_sig}){ret_clause}")
            else:
                body_lines.append(f'    fun {m.name}({params_sig}){ret_clause} {{')
                if m.body and m.body.statements:
                    from app.agents.translation_agent import TranslationAgent
                    translator = TranslationAgent("kotlin")
                    body_code = translator.translate_method_body(m, indent="        ")
                    body_lines.append(body_code)
                else:
                    body_lines.append("        // no implementation")
                body_lines.append("    }")

        # ---- imports ----
        import_lines = []
        for cls_name in sorted(referenced_classes):
            full = registry.import_for(pkg, cls_name)
            if full:
                import_lines.append(f"import {full}")

        header_comment = (
            f"// Auto-generated from {cu.file} (Java {t.kind}) -- structural migration only.\n"
            f"// Method bodies are NOT translated; see AI Translation Agent (Phase 14).\n"
            f"// Review before use."
        )

        keyword = "enum class" if is_enum else ("interface" if is_interface else "class")
        supertype_clause = f" : {', '.join(supertypes)}" if supertypes else ""
        header = f"{keyword} {t.name}{primary_ctor}{supertype_clause} {{"

        parts = [header_comment, f"package {pkg}" if pkg else None]
        if import_lines:
            parts.append("\n".join(import_lines))
        parts.append(header + "\n" + "\n".join(body_lines) + "\n}")
        source = "\n\n".join(p for p in parts if p) + "\n"

        status: FileStatus = "success"
        if "low" in confidences:
            status = "requires_human_review"
        elif t.methods and not is_interface:
            status = "partial"

        return GeneratedFile(path=str(src_dir / f"{t.name}.kt"), content=source, status=status, notes=notes)

    def _build_gradle(self) -> str:
        return (
            'plugins {\n    kotlin("jvm") version "1.9.24"\n}\n\n'
            "repositories {\n    mavenCentral()\n}\n\n"
            "dependencies {\n    // Dependencies mapped by the Dependency Mapping Agent (spec section 9) -- not yet implemented.\n}\n"
        )
