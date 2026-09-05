export type TargetLanguage = "python" | "typescript" | "kotlin";
export type MigrationMode = "analyze_only" | "suggest" | "autonomous";
export type MigrationStatus = "pending" | "running" | "success" | "partial" | "failed" | "cancelled";

export interface MigrationStartRequest {
  project_id: string;
  target_language: TargetLanguage;
  mode: MigrationMode;
}

export interface MigrationStartResponse {
  migration_id: string;
  project_id: string;
  target_language: TargetLanguage;
  mode: MigrationMode;
  status: MigrationStatus;
}

export interface MigrationProgress {
  analyzer?: boolean;
  architecture?: boolean;
  planner?: boolean;
  dependency?: boolean;
  translator?: boolean;
  refactoring?: boolean;
  test_migration?: boolean;
  build?: boolean;
  repair?: boolean;
  testing?: boolean;
  validation?: boolean;
  report?: boolean;
  [key: string]: boolean | undefined;
}

export interface MigrationStatusResponse {
  migration_id: string;
  status: MigrationStatus;
  progress: MigrationProgress;
  repair_attempts: number;
  human_approval_required: boolean;
}

export interface AgentEventItem {
  agent: string;
  message: string;
  timestamp: string;
}

export interface FileChangeItem {
  file: string;
  status: "success" | "partial" | "failed" | "requires_human_review" | "unsupported";
  reason?: string;
}

export interface FileDiffItem {
  from_file: string;
  to_file: string;
  unified_diff: string;
  additions: number;
  deletions: number;
}

export interface MigrationPlanStep {
  step_number: number;
  name: string;
  description: string;
}

export interface MigrationReportData {
  project_name: string;
  target_language: string;
  mode: string;
  generated_at: string;
  score: number;
  status: string;
  summary: string;
  markdown: string;
  statistics: {
    total_files: number;
    success_files: number;
    partial_files: number;
    review_files: number;
    classes_count: number;
    methods_count: number;
    repair_attempts_count: number;
  };
  validation: {
    status: string;
    score: number;
    total_files: number;
    valid_syntax_files: number;
    syntax_errors: Array<{ file: string; line: number; message: string }>;
    type_coverage_percentage: number;
    structural_completeness_percentage: number;
  };
  file_changes: Array<{ file_path: string; status: string; reason?: string }>;
  repair_attempts: Array<{
    attempt_number: number;
    error: string;
    category: string;
    file_path: string;
    patch_summary?: string;
    succeeded?: boolean;
  }>;
  test_results: {
    passed: number;
    failed: number;
    output?: string;
  };
}
