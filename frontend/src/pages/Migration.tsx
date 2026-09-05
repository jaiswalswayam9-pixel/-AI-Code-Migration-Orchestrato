import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { migrationApi } from "../services/migrationApi";
import type { MigrationStatusResponse } from "../types/migration";
import AgentActivity from "../components/AgentActivity";
import MigrationPlan from "../components/MigrationPlan";

const STEPS = [
  "analyzer", "architecture", "planner", "dependency",
  "translator", "refactoring", "test_migration", "build", "repair",
  "testing", "validation", "report",
];

export default function Migration() {
  const { migrationId } = useParams<{ migrationId: string }>();
  const [status, setStatus] = useState<MigrationStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!migrationId) return;
    const fetchStatus = () => {
      migrationApi.status(migrationId).then(setStatus).catch((e) => setError(e.message));
    };
    fetchStatus();
    // Poll every 2 seconds while running
    const interval = setInterval(() => {
      migrationApi.status(migrationId).then((s) => {
        setStatus(s);
        if (s.status !== "running" && s.status !== "pending") {
          clearInterval(interval);
        }
      }).catch(() => {});
    }, 2000);
    return () => clearInterval(interval);
  }, [migrationId]);

  if (error) return <div className="p-8 text-red-600">Error: {error}</div>;
  if (!status) return <div className="p-12 text-center text-gray-500 font-medium">Loading migration pipeline...</div>;

  const currentStatus = status.status || "running";
  const isFinished = currentStatus !== "running" && currentStatus !== "pending";
  const migIdStr = (status.migration_id || migrationId || "migration").toString();
  const progress = status.progress || {
    analyzer: true,
    architecture: true,
    planner: true,
    dependency: true,
    translator: true,
    refactoring: true,
    test_migration: true,
    build: true,
    repair: true,
    testing: true,
    validation: true,
    report: true,
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-2">
        <Link to="/" className="text-blue-600 hover:underline text-sm">← Back to Dashboard</Link>
      </div>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Migration {migIdStr.slice(0, 8)}…
          </h1>
          <div className="flex items-center gap-3 mt-2">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              currentStatus === "success" ? "bg-green-100 text-green-700" :
              currentStatus === "running" ? "bg-blue-100 text-blue-700" :
              currentStatus === "partial" ? "bg-yellow-100 text-yellow-700" :
              currentStatus === "failed" ? "bg-red-100 text-red-700" :
              "bg-gray-100 text-gray-700"
            }`}>
              {currentStatus.toUpperCase()}
            </span>
            {!isFinished && (
              <span className="text-sm text-gray-500 animate-pulse">Pipeline running…</span>
            )}
          </div>
        </div>
        {isFinished && (
          <div className="flex gap-3">
            <Link
              to={`/results/${migrationId || migIdStr}`}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition"
            >
              View Results
            </Link>
            <Link
              to={`/report/${migrationId || migIdStr}`}
              className="bg-gray-800 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-700 transition"
            >
              View Report
            </Link>
          </div>
        )}
      </div>

      {/* Progress Steps */}
      <div className="bg-white rounded-lg shadow border p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Pipeline Progress</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {STEPS.map((step) => {
            const done = Boolean(progress[step]);
            return (
              <div
                key={step}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${
                  done ? "bg-green-50 border-green-200" : "bg-gray-50 border-gray-200"
                }`}
              >
                <span className={`text-lg ${done ? "text-green-500" : "text-gray-300"}`}>
                  {done ? "✓" : "○"}
                </span>
                <span className={`text-sm capitalize ${done ? "text-green-700 font-medium" : "text-gray-500"}`}>
                  {step.replace(/_/g, " ")}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AgentActivity migrationId={migrationId || migIdStr} />
        <MigrationPlan migrationId={migrationId || migIdStr} />
      </div>
    </div>
  );
}
