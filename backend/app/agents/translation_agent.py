"""
AI Translation Agent (spec section 7 & 14).

Translates language-neutral IR statements and expressions into target language
logic (Python, TypeScript, Kotlin), with rule-based AST synthesis and fallback.
"""
from typing import Any
from app.ir.models import IRMethod, IRStatement, IRExpression, IRType
from app.rules.rule_engine import get_rule_engine


class TranslationAgent:
    def __init__(self, target_language: str = "python", class_fields: set[str] | None = None):
        self.target_language = target_language
        self.rule_engine = get_rule_engine(target_language)
        self.class_fields = class_fields or set()
        self.local_vars: set[str] = set()

    def translate_method_body(self, method: IRMethod, indent: str = "        ") -> str:
        """
        Translates an IRMethod's body into target language statements.
        Returns indented source code lines.
        """
        self.local_vars = {p.name for p in method.parameters}
        if not method.body or not method.body.statements:
            if self.target_language == "python":
                return f"{indent}pass"
            elif self.target_language == "typescript":
                return f"{indent}// empty body"
            elif self.target_language == "kotlin":
                return f"{indent}// empty body"

        lines: list[str] = []
        for stmt in method.body.statements:
            translated = self._translate_statement(stmt, indent)
            if translated:
                lines.append(translated)

        if not lines:
            return f"{indent}pass" if self.target_language == "python" else f"{indent}// no statements"

        return "\n".join(lines)

    def _translate_statement(self, stmt: IRStatement, indent: str) -> str:
        kind = stmt.kind

        if kind == "return":
            if stmt.expression:
                expr = self._translate_expression(stmt.expression)
                return f"{indent}return {expr}"
            return f"{indent}return"

        elif kind == "variable_decl":
            name = stmt.name or "temp"
            self.local_vars.add(name)
            if self.target_language == "python":
                if stmt.initializer:
                    expr = self._translate_expression(stmt.initializer)
                    return f"{indent}{name} = {expr}"
                return f"{indent}{name} = None"
            elif self.target_language == "typescript":
                if stmt.initializer:
                    expr = self._translate_expression(stmt.initializer)
                    return f"{indent}let {name} = {expr};"
                return f"{indent}let {name};"
            elif self.target_language == "kotlin":
                if stmt.initializer:
                    expr = self._translate_expression(stmt.initializer)
                    return f"{indent}val {name} = {expr}"
                return f"{indent}var {name}: Any? = null"

        elif kind == "expression_statement":
            if stmt.expression:
                expr = self._translate_expression(stmt.expression)
                suffix = ";" if self.target_language == "typescript" else ""
                return f"{indent}{expr}{suffix}"
            return ""

        elif kind == "if":
            cond = self._translate_expression(stmt.condition) if stmt.condition else "True"
            then_code = self._translate_nested_statement(stmt.then_statement, indent + "    ")
            else_code = ""
            if stmt.else_statement:
                else_body = self._translate_nested_statement(stmt.else_statement, indent + "    ")
                if self.target_language == "python":
                    else_code = f"\n{indent}else:\n{else_body}"
                else:
                    else_code = f" else {{\n{else_body}\n{indent}}}"

            if self.target_language == "python":
                return f"{indent}if {cond}:\n{then_code}{else_code}"
            else:
                return f"{indent}if ({cond}) {{\n{then_code}\n{indent}}}{else_code}"

        elif kind == "throw":
            expr = self._translate_expression(stmt.expression) if stmt.expression else "Exception()"
            if self.target_language == "python":
                # Convert IllegalArgumentException to ValueError
                expr = expr.replace("IllegalArgumentException", "ValueError").replace("IllegalStateException", "RuntimeError")
                return f"{indent}raise {expr}"
            else:
                return f"{indent}throw {expr};"

        elif kind == "block":
            sub_lines = []
            for s in stmt.statements:
                st = self._translate_statement(s, indent)
                if st:
                    sub_lines.append(st)
            return "\n".join(sub_lines) if sub_lines else (f"{indent}pass" if self.target_language == "python" else "")

        # Fallback to source code if available
        if stmt.source:
            return f"{indent}# {stmt.source.strip()}" if self.target_language == "python" else f"{indent}// {stmt.source.strip()}"

        return f"{indent}# unhandled stmt: {kind}" if self.target_language == "python" else f"{indent}// unhandled stmt: {kind}"

    def _translate_nested_statement(self, stmt: IRStatement | None, indent: str) -> str:
        if not stmt:
            return f"{indent}pass" if self.target_language == "python" else ""
        if stmt.kind == "block":
            lines = [self._translate_statement(s, indent) for s in stmt.statements if s]
            return "\n".join([l for l in lines if l]) or (f"{indent}pass" if self.target_language == "python" else "")
        return self._translate_statement(stmt, indent) or (f"{indent}pass" if self.target_language == "python" else "")

    def _translate_expression(self, expr: IRExpression | None) -> str:
        if not expr:
            return "None" if self.target_language == "python" else "null"

        kind = expr.kind

        if kind == "identifier":
            name = expr.name or "id"
            if name == "this":
                return "self" if self.target_language == "python" else "this"
            if self.target_language == "python" and name in self.class_fields and name not in self.local_vars:
                return f"self.{name}"
            return name

        elif kind == "literal":
            val = expr.value
            if val is None:
                return "None" if self.target_language == "python" else "null"
            if expr.literal_kind == "boolean":
                if self.target_language == "python":
                    return "True" if str(val).lower() == "true" else "False"
                return str(val).lower()
            elif expr.literal_kind == "string" or (expr.source and (expr.source.startswith('"') or expr.source.startswith("'"))):
                val_str = str(val)
                if not (val_str.startswith('"') or val_str.startswith("'")):
                    return f'"{val_str}"'
                return val_str
            return str(val)

        elif kind == "binary_operation":
            left = self._translate_expression(expr.left)
            right = self._translate_expression(expr.right)
            op = expr.operator or "+"
            op_map = {
                "PLUS": "+", "MINUS": "-", "MULTIPLY": "*", "DIVIDE": "/", "REMAINDER": "%",
                "EQUAL_TO": "==", "NOT_EQUAL_TO": "!=", "LESS_THAN": "<", "LESS_THAN_EQUAL": "<=",
                "GREATER_THAN": ">", "GREATER_THAN_EQUAL": ">=", "CONDITIONAL_AND": "and" if self.target_language == "python" else "&&",
                "CONDITIONAL_OR": "or" if self.target_language == "python" else "||",
                "==": "==", "!=": "!=", "<": "<", ">": ">", "<=": "<=", ">=": ">=",
                "+": "+", "-": "-", "*": "*", "/": "/"
            }
            mapped_op = op_map.get(op, op)
            return f"{left} {mapped_op} {right}"

        elif kind == "parenthesized":
            inner = self._translate_expression(expr.expression)
            return f"({inner})"

        elif kind == "unary_operation":
            inner = self._translate_expression(expr.expression)
            op = expr.operator or "!"
            if op in ("NOT", "!"):
                return f"not {inner}" if self.target_language == "python" else f"!{inner}"
            elif op in ("MINUS", "-"):
                return f"-{inner}"
            return f"{op}{inner}"

        elif kind == "method_invocation":
            args = [self._translate_expression(a) for a in expr.arguments]
            args_str = ", ".join(args)

            if expr.method_select:
                select = self._translate_expression(expr.method_select)
                # Method mappings (e.g. .add() on list in Python -> .append())
                if self.target_language == "python":
                    if select.endswith(".add"):
                        return f"{select[:-4]}.append({args_str})"
                    elif select.endswith(".size"):
                        obj = select[:-5]
                        return f"len({obj})"
                    elif select.endswith(".get"):
                        return f"{select[:-4]}[{args_str}]"
                    elif select.endswith(".equals"):
                        return f"{select[:-7]} == {args_str}"
                return f"{select}({args_str})"
            elif expr.name:
                return f"{expr.name}({args_str})"
            return f"method_call({args_str})"

        elif kind == "member_select":
            target = self._translate_expression(expr.expression) if expr.expression else ""
            field = expr.identifier or expr.name or ""
            if not target and expr.qualifier:
                target = expr.qualifier
            if target == "this":
                target = "self" if self.target_language == "python" else "this"
            if target and field:
                return f"{target}.{field}"
            return field or target or ("self" if self.target_language == "python" else "this")

        elif kind == "assignment":
            left = self._translate_expression(expr.left)
            right = self._translate_expression(expr.right)
            if left == "None" or not left:
                if expr.source and "=" in expr.source:
                    parts = expr.source.split("=", 1)
                    left_s = parts[0].strip().replace("this.", "self." if self.target_language == "python" else "this.")
                    right_s = parts[1].strip().rstrip(";").strip()
                    if "new ArrayList" in right_s:
                        right_s = "[]"
                    return f"{left_s} = {right_s}"
            return f"{left} = {right}"

        elif kind == "object_creation":
            cls_name = expr.class_type or "Object"
            args = [self._translate_expression(a) for a in expr.arguments]
            args_str = ", ".join(args)
            if self.target_language == "python":
                if "ArrayList" in cls_name or "List" in cls_name:
                    return "[]"
                elif "HashMap" in cls_name or "Map" in cls_name:
                    return "{}"
                elif "HashSet" in cls_name or "Set" in cls_name:
                    return "set()"
                # Exception conversions
                cls_name = cls_name.replace("IllegalArgumentException", "ValueError").replace("IllegalStateException", "RuntimeError")
                return f"{cls_name}({args_str})"
            elif self.target_language == "typescript":
                if "ArrayList" in cls_name or "List" in cls_name:
                    return "[]"
                elif "HashMap" in cls_name or "Map" in cls_name:
                    return "new Map()"
                return f"new {cls_name}({args_str})"
            elif self.target_language == "kotlin":
                if "ArrayList" in cls_name or "List" in cls_name:
                    return "mutableListOf()"
                elif "HashMap" in cls_name or "Map" in cls_name:
                    return "mutableMapOf()"
                return f"{cls_name}({args_str})"

        # Fallback to source
        if expr.source:
            src = expr.source.strip().rstrip(";")
            if self.target_language == "python":
                src = src.replace("this.", "self.")
            return src

        return "None" if self.target_language == "python" else "null"
