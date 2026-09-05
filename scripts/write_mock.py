# Python generator for mockData.ts
import json

content = """export const MOCK_SAMPLES = [
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
    description: "Full Spring Boot REST service with RestController, Service, and Repository annotations.",
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

const JAVA_CALC_SRC = `package com.example.calculator;

import java.util.ArrayList;
import java.util.List;

public class Calculator {
    private List<Double> history;

    public Calculator() {
        this.history = new ArrayList<>();
    }

    public double add(double a, double b) {
        double result = a + b;
        this.history.add(result);
        return result;
    }

    public double divide(double a, double b) {
        if (b == 0) {
            throw new IllegalArgumentException("Cannot divide by zero");
        }
        double result = a / b;
        this.history.add(result);
        return result;
    }

    public List<Double> getHistory() {
        return this.history;
    }
}`;

const JAVA_OP_SRC = `package com.example.calculator;

public enum Operation {
    ADD, SUBTRACT, MULTIPLY, DIVIDE
}`;

export const MOCK_DIFFS: Record<string, any[]> = {
  python: [
    {
      file_path: "basic_calculator/com/example/calculator/calculator.py",
      status: "modified",
      additions: 24,
      deletions: 26,
      original_code: JAVA_CALC_SRC,
      migrated_code: `from __future__ import annotations
from typing import List


class Calculator:
    history: list[float] = None

    def __init__(self) -> None:
        self.history = []

    def add(self, a: float, b: float) -> float:
        result = a + b
        self.history.append(result)
        return result

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.history.append(result)
        return result

    def get_history(self) -> list[float]:
        return self.history
`,
      diff_content: `--- Java Source: Calculator.java
+++ Python Target: calculator.py
@@ -1,26 +1,24 @@
-package com.example.calculator;
-import java.util.ArrayList;
-import java.util.List;
+from __future__ import annotations
+from typing import List

-public class Calculator {
-    private List<Double> history;

-    public Calculator() {
-        this.history = new ArrayList<>();
-    }

-    public double add(double a, double b) {
-        double result = a + b;
-        this.history.add(result);
-        return result;
-    }

-    public double divide(double a, double b) {
-        if (b == 0) {
-            throw new IllegalArgumentException("Cannot divide by zero");
-        }
-        double result = a / b;
-        this.history.add(result);
-        return result;
-    }

-    public List<Double> getHistory() {
-        return this.history;
-    }
+class Calculator:
+    history: list[float] = None

+    def __init__(self) -> None:
+        self.history = []

+    def add(self, a: float, b: float) -> float:
+        result = a + b
+        self.history.append(result)
+        return result

+    def divide(self, a: float, b: float) -> float:
+        if b == 0:
+            raise ValueError("Cannot divide by zero")
+        result = a / b
+        self.history.append(result)
+        return result

+    def get_history(self) -> list[float]:
+        return self.history
-}`,
    },
    {
      file_path: "basic_calculator/com/example/calculator/operation.py",
      status: "modified",
      additions: 10,
      deletions: 8,
      original_code: JAVA_OP_SRC,
      migrated_code: `from enum import Enum, auto


class Operation(Enum):
    ADD = auto()
    SUBTRACT = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
`,
      diff_content: `--- Java Source: Operation.java
+++ Python Target: operation.py
@@ -1,5 +1,8 @@
-package com.example.calculator;
+from enum import Enum, auto

-public enum Operation {
-    ADD, SUBTRACT, MULTIPLY, DIVIDE
-}
+class Operation(Enum):
+    ADD = auto()
+    SUBTRACT = auto()
+    MULTIPLY = auto()
+    DIVIDE = auto()`,
    },
    {
      file_path: "tests/test_calculator.py",
      status: "added",
      additions: 18,
      deletions: 0,
      original_code: "",
      migrated_code: `import pytest
from basic_calculator.com.example.calculator.calculator import Calculator


def test_calculator_add():
    calc = Calculator()
    assert calc.add(2.0, 3.0) == 5.0

def test_calculator_divide():
    calc = Calculator()
    assert calc.divide(10.0, 2.0) == 5.0

def test_calculator_divide_by_zero():
    calc = Calculator()
    with pytest.raises(ValueError):
        calc.divide(10.0, 0)
`,
      diff_content: `+++ tests/test_calculator.py (New File)
@@ -0,0 +1,18 @@
+import pytest
+from basic_calculator.com.example.calculator.calculator import Calculator
+
+def test_calculator_add():
+    calc = Calculator()
+    assert calc.add(2.0, 3.0) == 5.0
+
+def test_calculator_divide():
+    calc = Calculator()
+    assert calc.divide(10.0, 2.0) == 5.0
+
+def test_calculator_divide_by_zero():
+    calc = Calculator()
+    with pytest.raises(ValueError):
+        calc.divide(10.0, 0)`,
    },
    {
      file_path: "requirements.txt",
      status: "added",
      additions: 4,
      deletions: 0,
      original_code: "",
      migrated_code: `fastapi>=0.100.0
uvicorn>=0.22.0
pydantic>=2.0.0
pytest>=7.4.0
`,
      diff_content: `+++ requirements.txt (New File)
@@ -0,0 +1,4 @@
+fastapi>=0.100.0
+uvicorn>=0.22.0
+pydantic>=2.0.0
+pytest>=7.4.0`,
    },
  ],

  kotlin: [
    {
      file_path: "src/main/kotlin/com/example/calculator/Calculator.kt",
      status: "modified",
      additions: 23,
      deletions: 26,
      original_code: JAVA_CALC_SRC,
      migrated_code: `package com.example.calculator

class Calculator {
    private val history: MutableList<Double> = mutableListOf()

    fun add(a: Double, b: Double): Double {
        val result = a + b
        this.history.add(result)
        return result
    }

    fun divide(a: Double, b: Double): Double {
        if (b == 0.0) {
            throw IllegalArgumentException("Cannot divide by zero")
        }
        val result = a / b
        this.history.add(result)
        return result
    }

    fun getHistory(): List<Double> {
        return this.history.toList()
    }
}
`,
      diff_content: `--- Java Source: Calculator.java
+++ Kotlin Target: Calculator.kt
@@ -1,26 +1,23 @@
-package com.example.calculator;
-import java.util.ArrayList;
-import java.util.List;
+package com.example.calculator

-public class Calculator {
-    private List<Double> history;

-    public Calculator() {
-        this.history = new ArrayList<>();
-    }

-    public double add(double a, double b) {
-        double result = a + b;
-        this.history.add(result);
-        return result;
-    }

-    public double divide(double a, double b) {
-        if (b == 0) {
-            throw new IllegalArgumentException("Cannot divide by zero");
-        }
-        double result = a / b;
-        this.history.add(result);
-        return result;
-    }

-    public List<Double> getHistory() {
-        return this.history;
-    }
+class Calculator {
+    private val history: MutableList<Double> = mutableListOf()

+    fun add(a: Double, b: Double): Double {
+        val result = a + b
+        this.history.add(result)
+        return result
+    }

+    fun divide(a: Double, b: Double): Double {
+        if (b == 0.0) {
+            throw IllegalArgumentException("Cannot divide by zero")
+        }
+        val result = a / b
+        this.history.add(result)
+        return result
+    }

+    fun getHistory(): List<Double> {
+        return this.history.toList()
+    }
-}`,
    },
    {
      file_path: "src/main/kotlin/com/example/calculator/Operation.kt",
      status: "modified",
      additions: 5,
      deletions: 5,
      original_code: JAVA_OP_SRC,
      migrated_code: `package com.example.calculator

enum class Operation {
    ADD, SUBTRACT, MULTIPLY, DIVIDE
}
`,
      diff_content: `--- Java Source: Operation.java
+++ Kotlin Target: Operation.kt
@@ -1,5 +1,5 @@
-package com.example.calculator;
+package com.example.calculator

-public enum Operation {
+enum class Operation {
     ADD, SUBTRACT, MULTIPLY, DIVIDE
 }`,
    },
    {
      file_path: "src/test/kotlin/com/example/calculator/CalculatorTest.kt",
      status: "added",
      additions: 22,
      deletions: 0,
      original_code: "",
      migrated_code: `package com.example.calculator

import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.*

class CalculatorTest {
    @Test
    fun testAdd() {
        val calc = Calculator()
        assertEquals(5.0, calc.add(2.0, 3.0))
    }

    @Test
    fun testDivide() {
        val calc = Calculator()
        assertEquals(5.0, calc.divide(10.0, 2.0))
    }

    @Test
    fun testDivideByZero() {
        val calc = Calculator()
        assertThrows(IllegalArgumentException::class.java) {
            calc.divide(10.0, 0.0)
        }
    }
}
`,
      diff_content: `+++ src/test/kotlin/com/example/calculator/CalculatorTest.kt (New File)
@@ -0,0 +1,22 @@
+package com.example.calculator
+
+import org.junit.jupiter.api.Test
+import org.junit.jupiter.api.Assertions.*
+
+class CalculatorTest {
+    @Test
+    fun testAdd() {
+        val calc = Calculator()
+        assertEquals(5.0, calc.add(2.0, 3.0))
+    }
+
+    @Test
+    fun testDivide() {
+        val calc = Calculator()
+        assertEquals(5.0, calc.divide(10.0, 2.0))
+    }
+
+    @Test
+    fun testDivideByZero() {
+        val calc = Calculator()
+        assertThrows(IllegalArgumentException::class.java) { calc.divide(10.0, 0.0) }
+    }
+}`,
    },
    {
      file_path: "build.gradle.kts",
      status: "added",
      additions: 8,
      deletions: 0,
      original_code: "",
      migrated_code: `plugins {
    kotlin("jvm") version "1.9.22"
}

dependencies {
    testImplementation(kotlin("test"))
    testImplementation("org.junit.jupiter:junit-jupiter:5.9.2")
}
`,
      diff_content: `+++ build.gradle.kts (New File)
@@ -0,0 +1,8 @@
+plugins {
+    kotlin("jvm") version "1.9.22"
+}

+dependencies {
+    testImplementation(kotlin("test"))
+    testImplementation("org.junit.jupiter:junit-jupiter:5.9.2")
+}`,
    },
  ],

  typescript: [
    {
      file_path: "src/calculator.ts",
      status: "modified",
      additions: 25,
      deletions: 26,
      original_code: JAVA_CALC_SRC,
      migrated_code: `export class Calculator {
  private history: number[] = [];

  public add(a: number, b: number): number {
    const result = a + b;
    this.history.push(result);
    return result;
  }

  public divide(a: number, b: number): number {
    if (b === 0) {
      throw new Error("Cannot divide by zero");
    }
    const result = a / b;
    this.history.push(result);
    return result;
  }

  public getHistory(): number[] {
    return [...this.history];
  }
}
`,
      diff_content: `--- Java Source: Calculator.java
+++ TypeScript Target: calculator.ts
@@ -1,26 +1,25 @@
-package com.example.calculator;
-import java.util.ArrayList;
-import java.util.List;
+export class Calculator {
+  private history: number[] = [];

-public class Calculator {
-    private List<Double> history;

-    public Calculator() {
-        this.history = new ArrayList<>();
-    }

-    public double add(double a, double b) {
-        double result = a + b;
-        this.history.add(result);
-        return result;
-    }

-    public double divide(double a, double b) {
-        if (b == 0) {
-            throw new IllegalArgumentException("Cannot divide by zero");
-        }
-        double result = a / b;
-        this.history.add(result);
-        return result;
-    }

-    public List<Double> getHistory() {
-        return this.history;
-    }
+  public add(a: number, b: number): number {
+    const result = a + b;
+    this.history.push(result);
+    return result;
+  }

+  public divide(a: number, b: number): number {
+    if (b === 0) {
+      throw new Error("Cannot divide by zero");
+    }
+    const result = a / b;
+    this.history.push(result);
+    return result;
+  }

+  public getHistory(): number[] {
+    return [...this.history];
+  }
-}`,
    },
    {
      file_path: "src/operation.ts",
      status: "modified",
      additions: 6,
      deletions: 5,
      original_code: JAVA_OP_SRC,
      migrated_code: `export enum Operation {
  ADD = "ADD",
  SUBTRACT = "SUBTRACT",
  MULTIPLY = "MULTIPLY",
  DIVIDE = "DIVIDE",
}
`,
      diff_content: `--- Java Source: Operation.java
+++ TypeScript Target: operation.ts
@@ -1,5 +1,6 @@
-package com.example.calculator;
-public enum Operation {
+export enum Operation {
   ADD = "ADD",
   SUBTRACT = "SUBTRACT",
   MULTIPLY = "MULTIPLY",
   DIVIDE = "DIVIDE",
 }`,
    },
    {
      file_path: "tests/calculator.test.ts",
      status: "added",
      additions: 19,
      deletions: 0,
      original_code: "",
      migrated_code: `import { Calculator } from "../src/calculator";

describe("Calculator", () => {
  it("should add two numbers correctly", () => {
    const calc = new Calculator();
    expect(calc.add(2, 3)).toBe(5);
  });

  it("should divide two numbers correctly", () => {
    const calc = new Calculator();
    expect(calc.divide(10, 2)).toBe(5);
  });

  it("should throw error on division by zero", () => {
    const calc = new Calculator();
    expect(() => calc.divide(10, 0)).toThrow("Cannot divide by zero");
  });
});
`,
      diff_content: `+++ tests/calculator.test.ts (New File)
@@ -0,0 +1,19 @@
+import { Calculator } from "../src/calculator";
+
+describe("Calculator", () => {
+  it("should add two numbers correctly", () => {
+    const calc = new Calculator();
+    expect(calc.add(2, 3)).toBe(5);
+  });
+
+  it("should divide two numbers correctly", () => {
+    const calc = new Calculator();
+    expect(calc.divide(10, 2)).toBe(5);
+  });
+
+  it("should throw error on division by zero", () => {
+    const calc = new Calculator();
+    expect(() => calc.divide(10, 0)).toThrow("Cannot divide by zero");
+  });
+});`,
    },
    {
      file_path: "package.json",
      status: "added",
      additions: 12,
      deletions: 0,
      original_code: "",
      migrated_code: `{
  "name": "basic-calculator-ts",
  "version": "1.0.0",
  "scripts": {
    "build": "tsc",
    "test": "jest"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "jest": "^29.5.0",
    "@types/jest": "^29.5.0",
    "ts-jest": "^29.1.0"
  }
}
`,
      diff_content: `+++ package.json (New File)
@@ -0,0 +1,12 @@
+{
  "name": "basic-calculator-ts",
  "version": "1.0.0",
  "scripts": {
    "build": "tsc",
    "test": "jest"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "jest": "^29.5.0"
  }
}`,
    },
  ],
};
"""

with open("frontend/src/services/mockData.ts", "w", encoding="utf-8") as f:
    f.write(content)
print("Successfully generated frontend/src/services/mockData.ts")
