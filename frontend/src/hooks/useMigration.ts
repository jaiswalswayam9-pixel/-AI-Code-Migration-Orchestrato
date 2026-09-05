import { useEffect, useState } from "react";
import { migrationApi } from "../services/migrationApi";
import type { MigrationStatusResponse } from "../types/migration";

// Phase 3: simple one-shot fetch. Phase 23 (Live Agent Activity) upgrades
// this to poll or use a websocket/SSE connection to the orchestrator.
export function useMigrationStatus(migrationId: string | null) {
  const [status, setStatus] = useState<MigrationStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!migrationId) return;
    migrationApi.status(migrationId).then(setStatus).catch((e) => setError(e.message));
  }, [migrationId]);

  return { status, error };
}
