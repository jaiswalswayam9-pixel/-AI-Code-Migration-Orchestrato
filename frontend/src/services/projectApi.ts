import { api } from "./api";
import type { Project, ProjectUploadResponse, SampleProject } from "../types/project";

export const projectApi = {
  list: () => api.get<Project[]>("/api/projects"),
  get: (projectId: string) => api.get<Project>(`/api/projects/${projectId}`),
  upload: (file: File) => api.upload<ProjectUploadResponse>("/api/projects/upload", file),
  del: (projectId: string) => api.del<{ status: string }>(`/api/projects/${projectId}`),
  samples: () => api.get<{ samples: SampleProject[] }>("/api/projects/samples"),
  loadSample: (sampleId: string) => api.post<ProjectUploadResponse>(`/api/projects/sample/${sampleId}`),
};
