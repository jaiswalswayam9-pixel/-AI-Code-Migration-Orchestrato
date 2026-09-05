// Stub -- real implementation arrives in Phase 23 (Live Agent Activity),
// once backend/app/orchestrator/events.py emits real events to poll/stream.
export function useAgentEvents(_migrationId: string | null) {
  return { events: [] as { timestamp: string; agent: string; message: string }[] };
}
