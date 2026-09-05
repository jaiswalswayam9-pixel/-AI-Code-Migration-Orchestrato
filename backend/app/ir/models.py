"""
Language-neutral Intermediate Representation (spec section 4).

These models describe STRUCTURE (what a class/method/type IS), never
target-language syntax. A generator (Phase 9-11) reads an IRType and
decides for itself whether "list of X" becomes `list[X]` (Python),
`X[]` (TypeScript), or `MutableList<X>` (Kotlin) -- that decision does
not belong here.

IRType.kind values:
  primitive - int, double, boolean, char, ... (language keyword types)
  void      - method return type only
  class     - a named reference type (User, String, EmployeeService, ...)
  list      - List/ArrayList/Collection-family single-type-arg containers
  set       - Set/HashSet-family
  map       - Map/HashMap-family (two type args: key, value)
  array     - Java array syntax (T[]) -- distinct from `list` because
              arrays and collections generate differently in every
              target language
  generic   - a type parameter used unresolved (T, E, K, V) -- distinct
              from `class` because it has no concrete definition to map
"""
from __future__ import annotations
from typing import Literal, Optional, Any
from pydantic import BaseModel, Field


class IRType(BaseModel):
    kind: Literal["primitive", "void", "class", "list", "set", "map", "array", "generic"]
    name: str                          # "int", "String", "List", "T", ...
    type_args: list["IRType"] = []     # List<Employee> -> [IRType(class, "Employee")]
    array_dimensions: int = 0          # String[][] -> array_dimensions=2, kind of element type is base


IRType.model_rebuild()


class IRAnnotation(BaseModel):
    name: str                          # "RestController", "GetMapping", ...


class IRImport(BaseModel):
    path: str
    is_static: bool = False


class IRParameter(BaseModel):
    name: str
    type: IRType


class IRExpression(BaseModel):
    """Language-neutral AST expression node."""
    kind: str  # identifier, literal, binary_operation, unary_operation, method_invocation, member_select, assignment, compound_assignment, object_creation, array_creation, array_access, parenthesized, type_cast, instance_of, conditional_expression, lambda, member_reference, unsupported
    source: Optional[str] = None
    name: Optional[str] = None
    value: Optional[str] = None
    literal_kind: Optional[str] = None
    operator: Optional[str] = None
    left: Optional["IRExpression"] = None
    right: Optional["IRExpression"] = None
    expression: Optional["IRExpression"] = None
    method_select: Optional["IRExpression"] = None
    arguments: list["IRExpression"] = []
    type_arguments: list[str] = []
    identifier: Optional[str] = None
    class_type: Optional[str] = None
    element_type: Optional[str] = None
    dimensions: list["IRExpression"] = []
    initializers: list["IRExpression"] = []
    index: Optional["IRExpression"] = None
    target_type: Optional[str] = None
    check_type: Optional[str] = None
    condition: Optional["IRExpression"] = None
    true_expression: Optional["IRExpression"] = None
    false_expression: Optional["IRExpression"] = None
    node_type: Optional[str] = None
    parameters: list[Any] = []
    body_statement: Optional[Any] = None
    body_expression: Optional[Any] = None
    qualifier: Optional[str] = None


IRExpression.model_rebuild()


class IRCatch(BaseModel):
    parameter_name: str
    parameter_type: str
    block: Optional["IRStatement"] = None


class IRCase(BaseModel):
    source: Optional[str] = None
    is_default: bool = False
    statements: list["IRStatement"] = []


class IRStatement(BaseModel):
    """Language-neutral AST statement node."""
    kind: str  # variable_decl, expression_statement, return, if, for, enhanced_for, while, do_while, block, try, throw, break, continue, switch, assert, empty, unsupported
    source: Optional[str] = None
    name: Optional[str] = None
    type: Optional[IRType] = None
    type_str: Optional[str] = None
    modifiers: list[str] = []
    initializer: Optional[IRExpression] = None
    expression: Optional[IRExpression] = None
    condition: Optional[IRExpression] = None
    then_statement: Optional["IRStatement"] = None
    else_statement: Optional["IRStatement"] = None
    initializers: list["IRStatement"] = []
    updates: list["IRStatement"] = []
    variable: Optional[Any] = None
    statement: Optional["IRStatement"] = None
    statements: list["IRStatement"] = []
    resources: list[Any] = []
    block: Optional["IRStatement"] = None
    catches: list[IRCatch] = []
    finally_block: Optional["IRStatement"] = None
    label: Optional[str] = None
    cases: list[IRCase] = []
    detail: Optional[IRExpression] = None
    node_type: Optional[str] = None


IRStatement.model_rebuild()
IRCatch.model_rebuild()
IRCase.model_rebuild()


class IRMethodBody(BaseModel):
    """Preserves method logic as both structured AST statements and original source code."""
    statements: list[IRStatement] = []
    source_code: Optional[str] = None


class IRMethod(BaseModel):
    name: str
    return_type: IRType
    parameters: list[IRParameter] = []
    modifiers: list[str] = []
    annotations: list[IRAnnotation] = []
    throws: list[str] = []
    body: Optional[IRMethodBody] = None


class IRConstructor(BaseModel):
    parameters: list[IRParameter] = []
    modifiers: list[str] = []
    annotations: list[IRAnnotation] = []
    throws: list[str] = []
    body: Optional[IRMethodBody] = None


class IRField(BaseModel):
    name: str
    type: IRType
    modifiers: list[str] = []
    annotations: list[IRAnnotation] = []
    initializer: Optional[IRExpression] = None


class IRClass(BaseModel):
    """Covers class, interface, enum, record, and annotation-type decls --
    they share this shape closely enough that a separate model per kind
    would just duplicate fields. `kind` is what a generator switches on.
    """
    kind: Literal["class", "interface", "enum", "record", "annotation"]
    name: str
    modifiers: list[str] = []
    annotations: list[IRAnnotation] = []
    extends: list[str] = []            # multiple only possible for interfaces
    implements: list[str] = []
    fields: list[IRField] = []
    constructors: list[IRConstructor] = []
    methods: list[IRMethod] = []
    nested_types: list["IRClass"] = []


IRClass.model_rebuild()


class IRCompilationUnit(BaseModel):
    """One source file's worth of IR -- mirrors AstDumper\'s per-file output."""
    file: str
    package: Optional[str] = None
    imports: list[IRImport] = []
    types: list[IRClass] = []
    parse_error: Optional[str] = None


class IRProject(BaseModel):
    name: str
    compilation_units: list[IRCompilationUnit] = []

