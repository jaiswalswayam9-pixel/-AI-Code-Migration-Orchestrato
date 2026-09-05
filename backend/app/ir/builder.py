"""
Converts AstDumper.java's per-file JSON into the IR models
(app/ir/models.py). This is the ONLY place that should know
about both the raw AST JSON shape and the IR shape -- generators
only ever see IRProject, never raw AST JSON.
"""
from app.ir.models import (
    IRProject, IRCompilationUnit, IRClass, IRField, IRMethod,
    IRConstructor, IRParameter, IRAnnotation, IRImport, IRType,
    IRMethodBody, IRStatement, IRExpression, IRCatch, IRCase,
)
from app.ir.type_parser import parse_type

_VOID = IRType(kind="void", name="void")


def _annotations(names: list[str]) -> list[IRAnnotation]:
    return [IRAnnotation(name=n) for n in names]


def _build_expression(e: dict | None) -> IRExpression | None:
    if not e or not isinstance(e, dict):
        return None
    left = _build_expression(e.get("left"))
    right = _build_expression(e.get("right"))
    expression = _build_expression(e.get("expression"))
    method_select = _build_expression(e.get("method_select"))
    arguments = [_build_expression(a) for a in e.get("arguments", []) if a]
    dimensions = [_build_expression(d) for d in e.get("dimensions", []) if d]
    initializers = [_build_expression(i) for i in e.get("initializers", []) if i]
    index = _build_expression(e.get("index"))
    condition = _build_expression(e.get("condition"))
    true_expr = _build_expression(e.get("true_expression"))
    false_expr = _build_expression(e.get("false_expression"))

    return IRExpression(
        kind=e.get("kind", "unsupported"),
        source=e.get("source"),
        name=e.get("name"),
        value=e.get("value"),
        literal_kind=e.get("literal_kind"),
        operator=e.get("operator"),
        left=left,
        right=right,
        expression=expression,
        method_select=method_select,
        arguments=[a for a in arguments if a is not None],
        type_arguments=e.get("type_arguments", []),
        identifier=e.get("identifier"),
        class_type=e.get("class_type"),
        element_type=e.get("element_type"),
        dimensions=[d for d in dimensions if d is not None],
        initializers=[i for i in initializers if i is not None],
        index=index,
        target_type=e.get("target_type"),
        check_type=e.get("check_type"),
        condition=condition,
        true_expression=true_expr,
        false_expression=false_expr,
        node_type=e.get("node_type"),
        qualifier=e.get("qualifier"),
    )


def _build_statement(s: dict | None) -> IRStatement | None:
    if not s or not isinstance(s, dict):
        return None
    type_obj = parse_type(s["type"]) if s.get("type") else None
    initializer = _build_expression(s.get("initializer"))
    expression = _build_expression(s.get("expression"))
    condition = _build_expression(s.get("condition"))
    then_stmt = _build_statement(s.get("then_statement"))
    else_stmt = _build_statement(s.get("else_statement"))
    inits = [_build_statement(i) for i in s.get("initializers", []) if i]
    updates = [_build_statement(u) for u in s.get("updates", []) if u]
    variable = _build_statement(s.get("variable")) if isinstance(s.get("variable"), dict) else None
    stmt = _build_statement(s.get("statement"))
    statements = [_build_statement(st) for st in s.get("statements", []) if st]
    block = _build_statement(s.get("block"))
    finally_blk = _build_statement(s.get("finally_block"))
    detail = _build_expression(s.get("detail"))

    catches = []
    for c in s.get("catches", []):
        catches.append(IRCatch(
            parameter_name=c.get("parameter_name", "e"),
            parameter_type=c.get("parameter_type", "Exception"),
            block=_build_statement(c.get("block")),
        ))

    cases = []
    for c in s.get("cases", []):
        cases.append(IRCase(
            source=c.get("source"),
            is_default=c.get("is_default", False),
            statements=[st for st in [_build_statement(st) for st in c.get("statements", []) if st] if st is not None],
        ))

    return IRStatement(
        kind=s.get("kind", "unsupported"),
        source=s.get("source"),
        name=s.get("name"),
        type=type_obj,
        type_str=s.get("type"),
        modifiers=s.get("modifiers", []),
        initializer=initializer,
        expression=expression,
        condition=condition,
        then_statement=then_stmt,
        else_statement=else_stmt,
        initializers=[i for i in inits if i is not None],
        updates=[u for u in updates if u is not None],
        variable=variable,
        statement=stmt,
        statements=[st for st in statements if st is not None],
        block=block,
        catches=catches,
        finally_block=finally_blk,
        label=s.get("label"),
        cases=cases,
        detail=detail,
        node_type=s.get("node_type"),
    )


def _build_body(body_json: dict | None) -> IRMethodBody | None:
    if not body_json or not isinstance(body_json, dict):
        return None
    statements = [_build_statement(st) for st in body_json.get("statements", []) if st]
    return IRMethodBody(
        statements=[st for st in statements if st is not None],
        source_code=body_json.get("source_code"),
    )


def _build_field(f: dict) -> IRField:
    init_expr = _build_expression(f.get("initializer"))
    return IRField(
        name=f["name"], type=parse_type(f["type"]),
        modifiers=f.get("modifiers", []), annotations=_annotations(f.get("annotations", [])),
        initializer=init_expr,
    )


def _build_parameters(params: list[dict]) -> list[IRParameter]:
    return [IRParameter(name=p["name"], type=parse_type(p["type"])) for p in params]


def _build_method(m: dict) -> IRMethod:
    return IRMethod(
        name=m["name"],
        return_type=parse_type(m["return_type"]) if m.get("return_type") else _VOID,
        parameters=_build_parameters(m.get("parameters", [])),
        modifiers=m.get("modifiers", []),
        annotations=_annotations(m.get("annotations", [])),
        throws=m.get("throws", []),
        body=_build_body(m.get("body")),
    )


def _build_constructor(c: dict) -> IRConstructor:
    return IRConstructor(
        parameters=_build_parameters(c.get("parameters", [])),
        modifiers=c.get("modifiers", []),
        annotations=_annotations(c.get("annotations", [])),
        throws=c.get("throws", []),
        body=_build_body(c.get("body")),
    )


def build_ir_class(type_json: dict) -> IRClass:
    kind = type_json["kind"]

    if kind == "interface":
        extends_list = list(type_json.get("implements", []))
        implements_list = []
    else:
        ext = type_json.get("extends")
        extends_list = [ext] if ext else []
        implements_list = list(type_json.get("implements", []))

    return IRClass(
        kind=kind,
        name=type_json["name"],
        modifiers=type_json.get("modifiers", []),
        annotations=_annotations(type_json.get("annotations", [])),
        extends=extends_list,
        implements=implements_list,
        fields=[_build_field(f) for f in type_json.get("fields", [])],
        constructors=[_build_constructor(c) for c in type_json.get("constructors", [])],
        methods=[_build_method(m) for m in type_json.get("methods", [])],
        nested_types=[build_ir_class(n) for n in type_json.get("nested_types", [])],
    )


def build_compilation_unit(ast_json: dict) -> IRCompilationUnit:
    if ast_json.get("error"):
        return IRCompilationUnit(file=ast_json["file"], parse_error=ast_json["error"])

    imports = [
        IRImport(path=i["path"], is_static=i.get("is_static", False))
        for i in ast_json.get("imports", [])
    ]
    types = [build_ir_class(t) for t in ast_json.get("types", [])]
    return IRCompilationUnit(
        file=ast_json["file"], package=ast_json.get("package"),
        imports=imports, types=types,
    )


def build_project_ir(ast_jsons: list[dict], project_name: str) -> IRProject:
    return IRProject(
        name=project_name,
        compilation_units=[build_compilation_unit(a) for a in ast_jsons],
    )

