import { api } from "./api";
import type { MigrationStartRequest, MigrationStartResponse, MigrationStatusResponse, MigrationPlanStep } from "../types/migration";

export const migrationApi = {
  start: (data: MigrationStartRequest) => api.post<MigrationStartResponse>("/api/migrations/start", data),
  status: (migrationId: string) => api.get<MigrationStatusResponse>(`/api/migrations/${migrationId}/status`),
  plan: (migrationId: string) => api.get<{ plan: MigrationPlanStep[]; complexity?: string }>(`/api/migrations/${migrationId}/plan`),
  approve: (migrationId: string) => api.post<{ migration_id?: string; approved?: boolean; status?: string }>(`/api/migrations/${migrationId}/approve`),
  agents: (migrationId: string) => api.get<{ events: any[] }>(`/api/migrations/${migrationId}/agents`),
  files: (migrationId: string) => api.get<{ files: any[]; total?: number }>(`/api/files/${migrationId}`),
  diff: (migrationId: string) => api.get<{ diffs: any[] }>(`/api/migrations/${migrationId}/diff`),
  errors: (migrationId: string) => api.get<{ errors: any[]; repair_attempts: any[] }>(`/api/migrations/${migrationId}/errors`),
  tests: (migrationId: string) => api.get<{ passed: number; failed: number; log?: string; logs?: string }>(`/api/migrations/${migrationId}/tests`),
  validation: (migrationId: string) => api.get<any>(`/api/migrations/${migrationId}/validation`),
  report: (migrationId: string) => api.get<any>(`/api/migrations/${migrationId}/report`),
  downloadUrl: (migrationId: string) => `/api/migrations/${migrationId}/download`,
};
