export type ProjectStatus = "uploaded" | "analyzing" | "analyzed" | "error";

export interface ProjectAnalysis {
  java_version?: string | null;
  build_tool?: "maven" | "gradle" | null;
  framework?: string | null;
  framework_version?: string | null;
  dependencies?: Array<{ group_id?: string; artifact_id?: string; version?: string; name?: string }>;
  file_count: number;
  class_count: number;
  interface_count: number;
  enum_count: number;
  method_count: number;
  controller_count?: number;
  service_count?: number;
  repository_count?: number;
  entity_count?: number;
  configuration_count?: number;
  source_dirs?: string[];
  test_dirs?: string[];
  parse_errors?: Array<{ file: string; message: string }>;
}

export interface Project {
  project_id: string;
  name: string;
  uploaded_at: string;
  file_count: number;
  status: ProjectStatus;
  analysis?: ProjectAnalysis | null;
}

export interface ProjectUploadResponse {
  project_id: string;
  name: string;
  message: string;
  analysis?: ProjectAnalysis | null;
}

export interface SampleProject {
  id: string;
  name: string;
  description: string;
  framework: string;
}
