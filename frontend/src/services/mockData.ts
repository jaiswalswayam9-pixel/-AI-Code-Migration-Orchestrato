export const MOCK_SAMPLES = [
  {
    id: "basic_calculator",
    name: "Basic Calculator",
    description: "Simple calculator with arithmetic operations, exception handling, and history collection.",
    framework: "Plain Java (Maven)",
  },
  {
    id: "employee_management",
    name: "Employee Management",
    description: "Layered MVC service with Employee model, repository, service, and controller.",
    framework: "Plain Java (Maven)",
  },
  {
    id: "spring_boot_rest",
    name: "Product Catalog REST API",
    description: "Full Spring Boot REST service with @RestController, @Service, and @Repository annotations.",
    framework: "Spring Boot 3.x",
  },
];

export const MOCK_PROJECTS: Record<string, any> = {
  "sample-calc": {
    project_id: "sample-calc",
    name: "Basic Calculator",
    uploaded_at: new Date().toISOString(),
    file_count: 2,
    status: "analyzed",
    analysis: {
      java_version: "17",
      build_tool: "maven",
      framework: "Plain Java",
      file_count: 2,
      class_count: 1,
      interface_count: 0,
      enum_count: 1,
      method_count: 4,
      dependencies: [{ artifact_id: "junit-jupiter", version: "5.9.2" }],
    },
  },
  "sample-emp": {
    project_id: "sample-emp",
    name: "Employee Management",
    uploaded_at: new Date().toISOString(),
    file_count: 4,
    status: "analyzed",
    analysis: {
      java_version: "17",
      build_tool: "maven",
      framework: "Layered MVC",
      file_count: 4,
      class_count: 3,
      interface_count: 1,
      enum_count: 0,
      method_count: 8,
      controller_count: 1,
      service_count: 1,
      repository_count: 1,
      dependencies: [],
    },
  },
  "sample-rest": {
    project_id: "sample-rest",
    name: "Product Catalog REST API",
    uploaded_at: new Date().toISOString(),
    file_count: 4,
    status: "analyzed",
    analysis: {
      java_version: "17",
      build_tool: "maven",
      framework: "Spring Boot 3.x",
      file_count: 4,
      class_count: 3,
      interface_count: 1,
      enum_count: 0,
      method_count: 9,
      controller_count: 1,
      service_count: 1,
      repository_count: 1,
      dependencies: [{ artifact_id: "spring-boot-starter-web", version: "3.1.0" }],
    },
  },
};

export const MOCK_DIFFS: Record<string, any[]> = {
  python: [
    {
      file_path: "basic_calculator/com/example/calculator/calculator.py",
      status: "modified",
      additions: 24,
      deletions: 26,
      original_code: "package com.example.calculator;\n\nimport java.util.ArrayList;\nimport java.util.List;\n\npublic class Calculator {\n    private List<Double> history;\n\n    public Calculator() {\n        this.history = new ArrayList<>();\n    }\n\n    public double add(double a, double b) {\n        double result = a + b;\n        this.history.add(result);\n        return result;\n    }\n\n    public double divide(double a, double b) {\n        if (b == 0) {\n            throw new IllegalArgumentException(\"Cannot divide by zero\");\n        }\n        double result = a / b;\n        this.history.add(result);\n        return result;\n    }\n\n    public List<Double> getHistory() {\n        return this.history;\n    }\n}",
      migrated_code: "from __future__ import annotations\nfrom typing import List\n\n\nclass Calculator:\n    history: list[float] = None\n\n    def __init__(self) -> None:\n        self.history = []\n\n    def add(self, a: float, b: float) -> float:\n        result = a + b\n        self.history.append(result)\n        return result\n\n    def divide(self, a: float, b: float) -> float:\n        if b == 0:\n            raise ValueError(\"Cannot divide by zero\")\n        result = a / b\n        self.history.append(result)\n        return result\n\n    def get_history(self) -> list[float]:\n        return self.history\n",
      diff_content: "--- Java Source: Calculator.java\n+++ Python Target: calculator.py\n@@ -1,26 +1,24 @@\n-package com.example.calculator;\n-import java.util.ArrayList;\n-import java.util.List;\n+from __future__ import annotations\n+from typing import List\n\n-public class Calculator {\n-    private List<Double> history;\n+class Calculator:\n+    history: list[float] = None\n\n-    public Calculator() {\n-        this.history = new ArrayList<>();\n-    }\n+    def __init__(self) -> None:\n+        self.history = []\n\n-    public double add(double a, double b) {\n-        double result = a + b;\n-        this.history.add(result);\n-        return result;\n-    }\n+    def add(self, a: float, b: float) -> float:\n+        result = a + b\n+        self.history.append(result)\n+        return result\n\n-    public double divide(double a, double b) {\n-        if (b == 0) {\n-            throw new IllegalArgumentException(\"Cannot divide by zero\");\n-        }\n-        double result = a / b;\n-        this.history.add(result);\n-        return result;\n-    }\n+    def divide(self, a: float, b: float) -> float:\n+        if b == 0:\n+            raise ValueError(\"Cannot divide by zero\")\n+        result = a / b\n+        self.history.append(result)\n+        return result\n\n-    public List<Double> getHistory() {\n-        return this.history;\n-    }\n+    def get_history(self) -> list[float]:\n+        return self.history\n-}"
    },
    {
      file_path: "basic_calculator/com/example/calculator/operation.py",
      status: "modified",
      additions: 10,
      deletions: 8,
      original_code: "package com.example.calculator;\n\npublic enum Operation {\n    ADD, SUBTRACT, MULTIPLY, DIVIDE\n}",
      migrated_code: "from enum import Enum, auto\n\n\nclass Operation(Enum):\n    ADD = auto()\n    SUBTRACT = auto()\n    MULTIPLY = auto()\n    DIVIDE = auto()\n",
      diff_content: "--- Java Source: Operation.java\n+++ Python Target: operation.py\n@@ -1,5 +1,8 @@\n-package com.example.calculator;\n+from enum import Enum, auto\n\n-public enum Operation {\n-    ADD, SUBTRACT, MULTIPLY, DIVIDE\n-}\n+class Operation(Enum):\n+    ADD = auto()\n+    SUBTRACT = auto()\n+    MULTIPLY = auto()\n+    DIVIDE = auto()"
    },
    {
      file_path: "tests/test_calculator.py",
      status: "added",
      additions: 18,
      deletions: 0,
      original_code: "",
      migrated_code: "import pytest\nfrom basic_calculator.com.example.calculator.calculator import Calculator\n\n\ndef test_calculator_add():\n    calc = Calculator()\n    assert calc.add(2.0, 3.0) == 5.0\n\ndef test_calculator_divide():\n    calc = Calculator()\n    assert calc.divide(10.0, 2.0) == 5.0\n\ndef test_calculator_divide_by_zero():\n    calc = Calculator()\n    with pytest.raises(ValueError):\n        calc.divide(10.0, 0)\n",
      diff_content: "+++ tests/test_calculator.py (New File)\n@@ -0,0 +1,18 @@\n+import pytest\n+from basic_calculator.com.example.calculator.calculator import Calculator\n+\n+def test_calculator_add():\n+    calc = Calculator()\n+    assert calc.add(2.0, 3.0) == 5.0\n+\n+def test_calculator_divide():\n+    calc = Calculator()\n+    assert calc.divide(10.0, 2.0) == 5.0\n+\n+def test_calculator_divide_by_zero():\n+    calc = Calculator()\n+    with pytest.raises(ValueError):\n+        calc.divide(10.0, 0)"
    },
    {
      file_path: "requirements.txt",
      status: "added",
      additions: 4,
      deletions: 0,
      original_code: "",
      migrated_code: "fastapi>=0.100.0\nuvicorn>=0.22.0\npydantic>=2.0.0\npytest>=7.4.0\n",
      diff_content: "+++ requirements.txt (New File)\n@@ -0,0 +1,4 @@\n+fastapi>=0.100.0\n+uvicorn>=0.22.0\n+pydantic>=2.0.0\n+pytest>=7.4.0"
    }
  ]
};
