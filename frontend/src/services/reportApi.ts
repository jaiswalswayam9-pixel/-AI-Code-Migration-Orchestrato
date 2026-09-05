import { api } from "./api";
import type { MigrationReport } from "../types/report";

export const reportApi = {
  get: (migrationId: string) => api.get<MigrationReport>(`/api/reports/${migrationId}`),
};
