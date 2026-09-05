"""
Deterministic Migration Rule Engine (spec section 6).

Loads migration_rules/java_to_<target>/type_mappings.json and turns an
IRType (Phase 7) into the equivalent target-language type string, with a
confidence/risk classification per spec section 18 -- not every mapping
is equally certain, and this engine says so rather than pretending
uniform confidence.

Confidence rules:
  high   - primitive/void/generic mappings, or a container with a known
           template (List/Map/Set-family with a documented target form)
  medium - an unrecognized class name, passed through unchanged on the
           assumption it is a user-defined type the Migrator/Translation
           Agent (Phase 14) will handle -- correct in the common case,
           but not verified
  low    - a container kind with no template for this target language;
           the engine cannot express it and flags it for human review
           rather than emitting something silently wrong
"""
import functools
import json
from pathlib import Path
from typing import Literal

from app.ir.models import IRType
from app.ir.type_parser import classify_name

_RULES_ROOT = Path(__file__).resolve().parents[3] / "migration_rules"

Confidence = Literal["high", "medium", "low"]
_CONFIDENCE_RANK = {"high": 0, "medium": 1, "low": 2}


class TypeMappingResult:
    __slots__ = ("target", "confidence", "notes")

    def __init__(self, target: str, confidence: Confidence, notes: list[str] | None = None):
        self.target = target
        self.confidence = confidence
        self.notes = notes or []

    def __repr__(self) -> str:
        return f"TypeMappingResult(target={self.target!r}, confidence={self.confidence!r}, notes={self.notes!r})"


def _worse(a: Confidence, b: Confidence) -> Confidence:
    return a if _CONFIDENCE_RANK[a] >= _CONFIDENCE_RANK[b] else b


class RuleEngine:
    def __init__(self, target_language: str):
        self.target_language = target_language
        rules_path = _RULES_ROOT / f"java_to_{target_language}" / "type_mappings.json"
        if not rules_path.exists():
            raise FileNotFoundError(f"No rule file for target language: {target_language}")
        data = json.loads(rules_path.read_text())
        self.type_mappings: dict[str, str] = data["type_mappings"]
        self.container_templates: dict[str, str] = data["container_templates"]
        self.void_type: str = data["void_type"]
        self.any_type: str = data["any_type"]

    def map_type(self, ir_type: IRType) -> TypeMappingResult:
        # Arrays: reclassify the element (name/type_args with dims stripped),
        # map it once, then wrap with the array template N times.
        if ir_type.array_dimensions > 0:
            element_kind = classify_name(ir_type.name, ir_type.type_args)
            element = IRType(kind=element_kind, name=ir_type.name, type_args=ir_type.type_args, array_dimensions=0)
            elem_result = self.map_type(element)
            template = self.container_templates.get("array")
            if template is None:
                return TypeMappingResult(
                    target=f"{elem_result.target}[]" * ir_type.array_dimensions,
                    confidence="low",
                    notes=[f"No array template for target '{self.target_language}'; used a raw fallback."] + elem_result.notes,
                )
            target = elem_result.target
            for _ in range(ir_type.array_dimensions):
                target = template.format(target)
            return TypeMappingResult(target=target, confidence=elem_result.confidence, notes=elem_result.notes)

        if ir_type.kind == "void":
            return TypeMappingResult(target=self.void_type, confidence="high")

        if ir_type.kind == "generic":
            return TypeMappingResult(target=ir_type.name, confidence="high")

        if ir_type.kind == "primitive":
            mapped = self.type_mappings.get(ir_type.name)
            if mapped is None:
                return TypeMappingResult(
                    target=ir_type.name, confidence="low",
                    notes=[f"Unrecognized primitive type '{ir_type.name}' -- no rule defined."],
                )
            return TypeMappingResult(target=mapped, confidence="high")

        if ir_type.kind == "class":
            mapped = self.type_mappings.get(ir_type.name)
            if mapped is not None:
                return TypeMappingResult(target=mapped, confidence="high")
            # Not a known JDK type -- assume it's a user-defined class
            # that keeps its name across the migration (the Migrator
            # Agent, Phase 14, is responsible for actually generating
            # that class in the target project).
            return TypeMappingResult(
                target=ir_type.name, confidence="medium",
                notes=[f"'{ir_type.name}' assumed to be a user-defined type; name preserved as-is."],
            )

        if ir_type.kind in ("list", "set", "map"):
            template = self.container_templates.get(ir_type.kind)
            arg_results = [self.map_type(a) for a in ir_type.type_args]

            if template is None:
                return TypeMappingResult(
                    target=ir_type.name, confidence="low",
                    notes=[f"No '{ir_type.kind}' container template for target '{self.target_language}'."],
                )

            expected_args = 2 if ir_type.kind == "map" else 1
            arg_targets = [r.target for r in arg_results]
            notes = [n for r in arg_results for n in r.notes]
            confidence: Confidence = "high"
            for r in arg_results:
                confidence = _worse(confidence, r.confidence)

            if len(arg_targets) < expected_args:
                # Raw type used without generics (e.g. a bare `List`, no <>)
                arg_targets += [self.any_type] * (expected_args - len(arg_targets))
                notes.append(f"Raw (non-generic) '{ir_type.name}' used -- generic argument(s) assumed.")
                confidence = _worse(confidence, "medium")

            return TypeMappingResult(target=template.format(*arg_targets), confidence=confidence, notes=notes)

        # Should be unreachable given IRType\'s Literal kind, but fail
        # loudly rather than silently mis-mapping if the model ever grows
        # a new kind this engine hasn\'t been taught about.
        return TypeMappingResult(
            target=ir_type.name, confidence="low",
            notes=[f"Unhandled IRType.kind '{ir_type.kind}'."],
        )


@functools.lru_cache(maxsize=None)
def get_rule_engine(target_language: str) -> RuleEngine:
    return RuleEngine(target_language)
