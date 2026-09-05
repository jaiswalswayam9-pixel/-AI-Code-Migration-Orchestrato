import { MOCK_SAMPLES, MOCK_PROJECTS, MOCK_DIFFS } from "./mockData";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

const BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || "";

function handleStaticFallback<T>(path: string, _options?: RequestInit): T {
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
    return { migration_id: "demo-mig-1", status: "success" } as unknown as T;
  }
  if (path.includes("/status")) {
    return { status: "success", current_step: "completed" } as unknown as T;
  }
  if (path.includes("/diff")) {
    return { diffs: MOCK_DIFFS.python } as unknown as T;
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
    return {
      status: "PASSED",
      passed: 3,
      failed: 0,
      logs: "tests/test_calculator.py::test_calculator_add PASSED\ntests/test_calculator.py::test_calculator_divide PASSED\ntests/test_calculator.py::test_calculator_divide_by_zero PASSED\n\n======================== 3 passed in 0.04s ========================",
    } as unknown as T;
  }
  if (path.includes("/report")) {
    return {
      report: "# Migration Report\n\n- **Source**: Java\n- **Target**: Python\n- **Quality Score**: 98.5%\n- **Status**: PASSED",
      content: "# Migration Report\n\n- **Source**: Java\n- **Target**: Python\n- **Quality Score**: 98.5%\n- **Status**: PASSED",
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
      if (res.status === 404 && !BASE_URL) {
        return handleStaticFallback<T>(path, options);
      }
      const body = await res.text();
      throw new ApiError(res.status, body || res.statusText);
    }
    return res.json() as Promise<T>;
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
      if (res.status === 404 && !BASE_URL) {
        return handleStaticFallback<T>(path);
      }
      const body = await res.text();
      throw new ApiError(res.status, body || res.statusText);
    }
    return res.json() as Promise<T>;
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
