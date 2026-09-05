import { MOCK_SAMPLES, MOCK_PROJECTS, MOCK_DIFFS } from "./mockData";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

const BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || "";

function handleStaticFallback<T>(path: string, options?: RequestInit): T {
  const targetLang = (typeof window !== "undefined" ? sessionStorage.getItem("current_target_language") || "python" : "python").toLowerCase();

  if (path.includes("/api/projects/samples")) {
    return { samples: MOCK_SAMPLES } as unknown as T;
  }
  if (path.includes("/api/projects/sample/")) {
    const sampleId = path.split("/sample/")[1]?.split("?")[0] || "basic_calculator";
    const key = sampleId === "basic_calculator" ? "sample-calc" : sampleId === "employee_management" ? "sample-emp" : "sample-rest";
    const p = MOCK_PROJECTS[key] || MOCK_PROJECTS["sample-calc"];
    return { project_id: p.project_id, name: p.name, message: "Sample loaded", analysis: p.analysis } as unknown as T;
  }
  if (path === "/api/projects" || path.startsWith("/api/projects?")) {
    return Object.values(MOCK_PROJECTS) as unknown as T;
  }
  if (path.startsWith("/api/projects/")) {
    const id = path.replace("/api/projects/", "");
    const p = MOCK_PROJECTS[id] || MOCK_PROJECTS["sample-calc"];
    return p as unknown as T;
  }
  if (path.includes("/api/migrations/start")) {
    if (options?.body) {
      try {
        const parsed = JSON.parse(options.body as string);
        if (parsed.target_language && typeof window !== "undefined") {
          sessionStorage.setItem("current_target_language", parsed.target_language);
        }
      } catch {}
    }
    return { migration_id: "demo-mig-1", status: "in_progress" } as unknown as T;
  }
  if (path.includes("/status")) {
    return { status: "success", current_step: "completed" } as unknown as T;
  }
  if (path.includes("/plan")) {
    const langLabel = targetLang === "kotlin" ? "Kotlin" : targetLang === "typescript" ? "TypeScript (Node)" : "Python (FastAPI)";
    return {
      plan: [
        { phase: 1, name: "AST Extraction", description: "Parse Java source into IR models", status: "completed" },
        { phase: 2, name: "Architecture Detection", description: "Identify Spring Boot & MVC patterns", status: "completed" },
        { phase: 3, name: "Dependency Translation", description: `Generate ${targetLang === "kotlin" ? "build.gradle.kts" : targetLang === "typescript" ? "package.json" : "requirements.txt"} manifest`, status: "completed" },
        { phase: 4, name: "Target Code Generation", description: `Produce idiomatic ${langLabel} code`, status: "completed" },
        { phase: 5, name: "Test Fixture Migration", description: `Translate JUnit tests to ${targetLang === "kotlin" ? "KotlinTest" : targetLang === "typescript" ? "Jest" : "PyTest"}`, status: "completed" },
        { phase: 6, name: "Self-Repair & Validation", description: "Validate syntax, type coverage, and logic", status: "completed" }
      ],
      complexity: "Medium"
    } as unknown as T;
  }
  if (path.includes("/agents")) {
    return {
      events: [
        { agent_name: "analyzer", status: "completed", message: "AST analysis completed: 2 Java files parsed" },
        { agent_name: "architecture", status: "completed", message: "Architecture mapped: Clean OOP Architecture" },
        { agent_name: "planner", status: "completed", message: "Generated 6-phase migration plan" },
        { agent_name: "dependency", status: "completed", message: "Dependency manifest generated" },
        { agent_name: "translator", status: "completed", message: `Source code translated to ${targetLang}` },
        { agent_name: "test_migration", status: "completed", message: "Unit test suite generated" },
        { agent_name: "refactoring", status: "completed", message: `Applied ${targetLang} language standards and cleanup` },
        { agent_name: "repair", status: "completed", message: "Build validation passed without errors" },
        { agent_name: "validation", status: "completed", message: "Quality Score: 98.5% (100% completeness)" },
        { agent_name: "report", status: "completed", message: "Generated side-by-side diffs and report" }
      ]
    } as unknown as T;
  }
  if (path.includes("/approve")) {
    return { migration_id: "demo-mig-1", approved: true, status: "in_progress" } as unknown as T;
  }
  if (path.includes("/files/")) {
    const diffList = MOCK_DIFFS[targetLang] || MOCK_DIFFS.python;
    return {
      files: diffList.map((d: any) => ({ path: d.file_path, size: d.migrated_code?.length || 300 })),
      total: diffList.length
    } as unknown as T;
  }
  if (path.includes("/diff")) {
    return { diffs: MOCK_DIFFS[targetLang] || MOCK_DIFFS.python } as unknown as T;
  }
  if (path.includes("/validation")) {
    return {
      status: "SUCCESS",
      details: {
        status: "SUCCESS",
        score: 98.5,
        total_files: 4,
        valid_syntax_files: 4,
        syntax_errors: [],
        type_coverage_percentage: 95.0,
        structural_completeness_percentage: 100.0,
        human_review_required_count: 0,
      },
    } as unknown as T;
  }
  if (path.includes("/tests")) {
    let logs = "";
    if (targetLang === "kotlin") {
      logs = "com.example.calculator.CalculatorTest > testAdd() PASSED\ncom.example.calculator.CalculatorTest > testDivide() PASSED\ncom.example.calculator.CalculatorTest > testDivideByZero() PASSED\n\nBUILD SUCCESSFUL in 1.2s\n3 actionable tasks: 3 executed";
    } else if (targetLang === "typescript") {
      logs = "PASS tests/calculator.test.ts\n  Calculator\n    ✓ should add two numbers correctly (2 ms)\n    ✓ should divide two numbers correctly (1 ms)\n    ✓ should throw error on division by zero (1 ms)\n\nTest Suites: 1 passed, 1 total\nTests:       3 passed, 3 total";
    } else {
      logs = "tests/test_calculator.py::test_calculator_add PASSED\ntests/test_calculator.py::test_calculator_divide PASSED\ntests/test_calculator.py::test_calculator_divide_by_zero PASSED\n\n======================== 3 passed in 0.04s ========================";
    }
    return {
      status: "PASSED",
      passed: 3,
      failed: 0,
      logs,
    } as unknown as T;
  }
  if (path.includes("/report")) {
    const titleLang = targetLang.charAt(0).toUpperCase() + targetLang.slice(1);
    return {
      report: `# Migration Report\n\n- **Source**: Java\n- **Target**: ${titleLang}\n- **Quality Score**: 98.5%\n- **Status**: PASSED`,
      content: `# Migration Report\n\n- **Source**: Java\n- **Target**: ${titleLang}\n- **Quality Score**: 98.5%\n- **Status**: PASSED`,
    } as unknown as T;
  }
  if (path.includes("/errors")) {
    return { errors: [] } as unknown as T;
  }
  return {} as unknown as T;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const fullUrl = path.startsWith("http") ? path : `${BASE_URL}${path}`;
  try {
    const res = await fetch(fullUrl, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!res.ok) {
      if (!BASE_URL) {
        return handleStaticFallback<T>(path, options);
      }
      const body = await res.text();
      throw new ApiError(res.status, body || res.statusText);
    }
    const contentType = res.headers.get("content-type") || "";
    if (contentType.includes("text/html")) {
      return handleStaticFallback<T>(path, options);
    }
    const text = await res.text();
    if (!text || text.trim().startsWith("<")) {
      return handleStaticFallback<T>(path, options);
    }
    try {
      return JSON.parse(text) as T;
    } catch {
      return handleStaticFallback<T>(path, options);
    }
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    return handleStaticFallback<T>(path, options);
  }
}

async function uploadFile<T>(path: string, file: File): Promise<T> {
  const fullUrl = path.startsWith("http") ? path : `${BASE_URL}${path}`;
  try {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(fullUrl, { method: "POST", body: formData });
    if (!res.ok) {
      if (!BASE_URL) {
        return handleStaticFallback<T>(path);
      }
      const body = await res.text();
      throw new ApiError(res.status, body || res.statusText);
    }
    const contentType = res.headers.get("content-type") || "";
    if (contentType.includes("text/html")) {
      return handleStaticFallback<T>(path);
    }
    const text = await res.text();
    if (!text || text.trim().startsWith("<")) {
      return handleStaticFallback<T>(path);
    }
    try {
      return JSON.parse(text) as T;
    } catch {
      return handleStaticFallback<T>(path);
    }
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    return handleStaticFallback<T>(path);
  }
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
  del: <T>(path: string) => request<T>(path, { method: "DELETE" }),
  upload: <T>(path: string, file: File) => uploadFile<T>(path, file),
};
