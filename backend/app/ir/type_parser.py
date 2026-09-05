"""
Parses a Java type\'s source-text form (as emitted by AstDumper.java\'s
`.toString()` on type trees -- e.g. "List<Employee>", "Map<String, Long>",
"double", "T", "String[]") into a structured IRType.

This is intentionally a small hand-written recursive-descent parser, not
a full Java grammar -- it only needs to understand type syntax (names,
generics, arrays), not expressions or statements.
"""
import re
from app.ir.models import IRType

_PRIMITIVES = {"int", "long", "double", "float", "boolean", "char", "byte", "short"}
_LIST_TYPES = {"List", "ArrayList", "LinkedList", "Collection", "Iterable", "Queue", "Deque", "Stack", "Vector"}
_SET_TYPES = {"Set", "HashSet", "TreeSet", "LinkedHashSet", "SortedSet"}
_MAP_TYPES = {"Map", "HashMap", "TreeMap", "LinkedHashMap", "SortedMap", "ConcurrentHashMap"}
_GENERIC_PARAM_RE = re.compile(r"^[A-Z][0-9]?$")  # heuristic: T, E, K, V, R, T1, ...


def _split_top_level(s: str) -> list[str]:
    """Split "A, Map<B, C>, D" into ["A", "Map<B, C>", "D"] -- commas
    inside nested <...> must not split."""
    parts, depth, current = [], 0, ""
    for ch in s:
        if ch == "<":
            depth += 1
            current += ch
        elif ch == ">":
            depth -= 1
            current += ch
        elif ch == "," and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += ch
    if current.strip():
        parts.append(current.strip())
    return parts


def classify_name(name: str, type_args: list[IRType]) -> str:
    if name == "void":
        return "void"
    if name in _PRIMITIVES:
        return "primitive"
    if name in _LIST_TYPES:
        return "list"
    if name in _SET_TYPES:
        return "set"
    if name in _MAP_TYPES:
        return "map"
    if name.startswith("?") or _GENERIC_PARAM_RE.match(name):
        return "generic"
    return "class"


def parse_type(type_str: str) -> IRType:
    s = type_str.strip()

    array_dims = 0
    while s.endswith("[]"):
        s = s[:-2].strip()
        array_dims += 1

    name = s
    type_args: list[IRType] = []
    if "<" in s and s.endswith(">"):
        idx = s.index("<")
        name = s[:idx].strip()
        inner = s[idx + 1: -1]
        type_args = [parse_type(a) for a in _split_top_level(inner)]

    elem_kind = classify_name(name, type_args)
    kind = "array" if array_dims > 0 else elem_kind

    return IRType(kind=kind, name=name, type_args=type_args, array_dimensions=array_dims)
