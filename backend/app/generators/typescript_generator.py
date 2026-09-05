"""
TypeScript target-language generator (spec section 8, TypeScript Generator).

Structural only -- same boundary as python_generator.py: method bodies
are never fabricated, only signatures. See that file's docstring for the
full rationale (AI Translation Agent, Phase 14, owns logic translation).

One genuine simplification versus Python: TS `interface` is a pure
structural contract with no runtime representation, so a Java interface
maps directly to a TS interface with signature-only members -- no
ABC-style workaround needed, and nothing is left "TODO" on an interface
file (there's no body to translate in the first place). TS interfaces
also natively support multiple `extends`, which matches our IR's
reinterpreted multi-extends list for interfaces exactly.
"""
from pathlib import Path

from app.generators.base_generator import BaseLanguageGenerator, GeneratedFile, FileStatus
from app.generators.naming import TypeScriptProjectRegistry, to_kebab_case, package_to_path
from app.ir.models import IRProject, IRClass, IRCompilationUnit, IRType
from app.rules.rule_engine import get_rule_engine


def _modifier_prefix(modifiers: list[str]) -> str:
    parts = []
    if "private" in modifiers:
        parts.append("private")
    elif "protected" in modifiers:
        parts.append("protected")
    if "static" in modifiers:
        parts.append("static")
    if "final" in modifiers:
        parts.append("readonly")
    return (" ".join(parts) + " ") if parts else ""


class TypeScriptGenerator(BaseLanguageGenerator):
    language = "typescript"
    file_extension = ".ts"

    def __init__(self):
        self.rule_engine = get_rule_engine("typescript")

    def generate_project(self, ir: IRProject, output_dir: Path) -> list[GeneratedFile]:
        registry = TypeScriptProjectRegistry(ir)
        results: list[GeneratedFile] = []

        for cu in ir.compilation_units:
            pkg_path = package_to_path(cu.package)
            dir_path = Path(pkg_path) if pkg_path else Path(".")

            if cu.parse_error:
                results.append(GeneratedFile(
                    path=str(dir_path / "PARSE_ERROR.txt"),
                    content=f"Source file could not be parsed: {cu.file}\nError: {cu.parse_error}\n",
                    status="failed", notes=[cu.parse_error],
                ))
                continue

            for t in cu.types:
                results.append(self._generate_type_file(t, cu, registry, pkg_path))

        results.append(GeneratedFile(
            path="package.json",
            content=self._package_json(to_kebab_case(ir.name)),
            status="success",
        ))
        results.append(GeneratedFile(
            path="tsconfig.json",
            content=self._tsconfig_json(),
            status="success",
        ))

        for r in results:
            full_path = output_dir / r.path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(r.content)

        return results

    def _generate_type_file(self, t: IRClass, cu: IRCompilationUnit, registry: TypeScriptProjectRegistry, pkg_path: str) -> GeneratedFile:
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

        # ---- header: extends / implements ----
        extends_names: list[str] = []
        implements_names: list[str] = []
        if is_interface:
            for ext in t.extends:
                name = ext.split("<")[0].strip()
                extends_names.append(name)
                if registry.is_project_local(name):
                    referenced_classes.add(name)
                else:
                    notes.append(f"Extended interface '{ext}' is external/unresolved.")
        elif not is_enum:
            if t.extends:
                name = t.extends[0].split("<")[0].strip()
                extends_names.append(name)
                if registry.is_project_local(name):
                    referenced_classes.add(name)
                else:
                    notes.append(f"Base class '{name}' is external/unresolved in this project.")
            for impl in t.implements:
                name = impl.split("<")[0].strip()
                if registry.is_project_local(name):
                    referenced_classes.add(name)
                    implements_names.append(name)
                else:
                    notes.append(f"Implemented interface '{impl}' is external/unresolved -- not added as a TS 'implements'.")

        # ---- body ----
        body_lines: list[str] = []

        if is_enum:
            for f in t.fields:
                body_lines.append(f"    {f.name},")
            if not t.fields:
                body_lines.append("    // no enum constants found")
        elif is_interface:
            for f in t.fields:
                body_lines.append(f"    {f.name}: {map_type(f.type)};")
            for m in t.methods:
                params_sig = ", ".join(f"{p.name}: {map_type(p.type)}" for p in m.parameters)
                body_lines.append(f"    {m.name}({params_sig}): {map_type(m.return_type)};")
            if not body_lines:
                body_lines.append("    // marker interface -- no members")
        else:
            has_ctor = bool(t.constructors)
            for f in t.fields:
                ann = map_type(f.type)
                prefix = _modifier_prefix(f.modifiers)
                suffix = ":" if has_ctor else "!:"
                body_lines.append(f"    {prefix}{f.name}{suffix} {ann};")

            if has_ctor:
                if len(t.constructors) > 1:
                    notes.append(f"Java class has {len(t.constructors)} constructors; only the first was used -- others require manual merging.")
                ctor = t.constructors[0]
                params_sig = ", ".join(f"{p.name}: {map_type(p.type)}" for p in ctor.parameters)
                body_lines.append("")
                body_lines.append(f"    constructor({params_sig}) {{")
                field_names = {f.name for f in t.fields}
                if not ctor.parameters:
                    body_lines.append("        // no-arg constructor")
                for p in ctor.parameters:
                    comment = "" if p.name in field_names else "  // no matching field found on source class -- verify"
                    body_lines.append(f"        this.{p.name} = {p.name};{comment}")
                body_lines.append("    }")

            for m in t.methods:
                params_sig = ", ".join(f"{p.name}: {map_type(p.type)}" for p in m.parameters)
                ret = map_type(m.return_type)
                body_lines.append("")
                body_lines.append(f"    {m.name}({params_sig}): {ret} {{")
                if m.body and m.body.statements:
                    from app.agents.translation_agent import TranslationAgent
                    translator = TranslationAgent("typescript")
                    body_code = translator.translate_method_body(m, indent="        ")
                    body_lines.append(body_code)
                else:
                    body_lines.append("        // no implementation")
                body_lines.append("    }")

        if not body_lines:
            body_lines = ["    // empty"]

        # ---- imports ----
        import_lines = []
        for cls_name in sorted(referenced_classes):
            rel = registry.import_path_from(pkg_path, cls_name)
            import_lines.append(f"import {{ {cls_name} }} from '{rel}';")

        header_comment = (
            f"/**\n"
            f" * Auto-generated from {cu.file} (Java {t.kind}) -- structural migration only.\n"
            f" * Method bodies are NOT translated; see AI Translation Agent (Phase 14).\n"
            f" * Review before use.\n"
            f" */"
        )

        keyword = "enum" if is_enum else ("interface" if is_interface else "class")
        extends_clause = f" extends {', '.join(extends_names)}" if extends_names else ""
        implements_clause = f" implements {', '.join(implements_names)}" if implements_names else ""
        header = f"export {keyword} {t.name}{extends_clause}{implements_clause} {{"

        parts = [header_comment]
        if import_lines:
            parts.append("\n".join(import_lines))
        parts.append(header + "\n" + "\n".join(body_lines) + "\n}")
        source = "\n\n".join(parts) + "\n"

        status: FileStatus = "success"
        if "low" in confidences:
            status = "requires_human_review"
        elif t.methods and not is_interface:
            status = "partial"

        stem = to_kebab_case(t.name)
        dir_path = Path(pkg_path) if pkg_path else Path(".")
        return GeneratedFile(path=str(dir_path / f"{stem}.ts"), content=source, status=status, notes=notes)

    def _package_json(self, name: str) -> str:
        return (
            "{\n"
            f'  "name": "{name}",\n'
            '  "version": "0.1.0",\n'
            '  "private": true,\n'
            '  "dependencies": {}\n'
            "}\n"
        )

    def _tsconfig_json(self) -> str:
        return (
            "{\n"
            '  "compilerOptions": {\n'
            '    "target": "ES2020",\n'
            '    "module": "commonjs",\n'
            '    "strict": true,\n'
            '    "declaration": true,\n'
            '    "outDir": "dist"\n'
            "  }\n"
            "}\n"
        )
