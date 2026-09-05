"""
Unit tests for AST Parser, IR Builder, and Method Body preservation.
"""
import pytest
from pathlib import Path
from app.parsers.java_parser import parse_java_files
from app.ir.builder import build_project_ir
from app.ir.serializer import ir_to_json, ir_from_json
from app.generators.python_generator import PythonGenerator
from app.generators.typescript_generator import TypeScriptGenerator
from app.generators.kotlin_generator import KotlinGenerator

SAMPLE_CALCULATOR = Path(__file__).parents[3] / "sample_projects" / "basic_calculator" / "src" / "main" / "java" / "com" / "example" / "calculator" / "Calculator.java"
SAMPLE_EMPLOYEES_DIR = Path(__file__).parents[3] / "sample_projects" / "employee_management" / "src" / "main" / "java" / "com" / "example" / "employees"

def test_ast_parses_method_bodies():
    assert SAMPLE_CALCULATOR.exists(), f"Sample file not found at {SAMPLE_CALCULATOR}"
    res = parse_java_files([SAMPLE_CALCULATOR])
    assert len(res) == 1
    file_ast = res[0]
    assert file_ast["package"] == "com.example.calculator"
    assert len(file_ast["types"]) == 1
    
    calc_type = file_ast["types"][0]
    assert calc_type["name"] == "Calculator"
    assert len(calc_type["methods"]) == 3
    
    # Check add method
    add_m = next(m for m in calc_type["methods"] if m["name"] == "add")
    assert add_m["return_type"] == "double"
    assert len(add_m["parameters"]) == 2
    assert add_m["body"] is not None
    assert len(add_m["body"]["statements"]) == 3
    assert add_m["body"]["statements"][0]["kind"] == "variable_decl"
    assert add_m["body"]["statements"][1]["kind"] == "expression_statement"
    assert add_m["body"]["statements"][2]["kind"] == "return"

    # Check divide method (contains if-throw)
    div_m = next(m for m in calc_type["methods"] if m["name"] == "divide")
    assert div_m["body"] is not None
    if_stmt = div_m["body"]["statements"][0]
    assert if_stmt["kind"] == "if"
    assert if_stmt["condition"]["kind"] == "parenthesized"

def test_ir_builder_preserves_method_bodies():
    res = parse_java_files([SAMPLE_CALCULATOR])
    ir = build_project_ir(res, "basic_calculator")
    assert ir.name == "basic_calculator"
    assert len(ir.compilation_units) == 1
    
    cu = ir.compilation_units[0]
    assert len(cu.types) == 1
    cls_ir = cu.types[0]
    
    add_m = next(m for m in cls_ir.methods if m.name == "add")
    assert add_m.body is not None
    assert len(add_m.body.statements) == 3
    assert "double result = a + b" in add_m.body.source_code
    
    # Check statement structure
    stmt0 = add_m.body.statements[0]
    assert stmt0.kind == "variable_decl"
    assert stmt0.name == "result"
    assert stmt0.initializer is not None
    assert stmt0.initializer.kind == "binary_operation"
    assert stmt0.initializer.operator == "PLUS"

def test_ir_roundtrip_serialization():
    res = parse_java_files([SAMPLE_CALCULATOR])
    ir = build_project_ir(res, "basic_calculator")
    json_str = ir_to_json(ir)
    restored_ir = ir_from_json(json_str)
    
    assert restored_ir.name == ir.name
    assert len(restored_ir.compilation_units) == len(ir.compilation_units)
    restored_cls = restored_ir.compilation_units[0].types[0]
    assert len(restored_cls.methods) == len(ir.compilation_units[0].types[0].methods)
    
    add_m = next(m for m in restored_cls.methods if m.name == "add")
    assert add_m.body is not None
    assert len(add_m.body.statements) == 3

def test_employee_management_project_ir():
    emp_files = list(SAMPLE_EMPLOYEES_DIR.glob("*.java"))
    assert len(emp_files) >= 4
    res = parse_java_files(emp_files)
    assert len(res) == len(emp_files)
    
    ir = build_project_ir(res, "employee_management")
    assert len(ir.compilation_units) == len(emp_files)
    
    # Verify controller and service methods have bodies
    for cu in ir.compilation_units:
        for t in cu.types:
            if t.kind == "class":
                for m in t.methods:
                    assert m.body is not None, f"Method {m.name} in {t.name} should have a body"
                    assert m.body.source_code is not None

def test_generators_backward_compatibility(tmp_path):
    res = parse_java_files([SAMPLE_CALCULATOR])
    ir = build_project_ir(res, "basic_calculator")
    
    # Python generator
    py_gen = PythonGenerator()
    py_files = py_gen.generate_project(ir, tmp_path / "python")
    assert any(f.path.endswith("calculator.py") for f in py_files)
    
    # TypeScript generator
    ts_gen = TypeScriptGenerator()
    ts_files = ts_gen.generate_project(ir, tmp_path / "ts")
    assert any(f.path.endswith("calculator.ts") for f in ts_files)
    
    # Kotlin generator
    kt_gen = KotlinGenerator()
    kt_files = kt_gen.generate_project(ir, tmp_path / "kt")
    assert any(f.path.endswith("Calculator.kt") for f in kt_files)
