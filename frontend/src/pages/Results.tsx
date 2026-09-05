import { useParams, Link } from "react-router-dom";
import CodeDiff from "../components/CodeDiff";
import TestResults from "../components/TestResults";
import ErrorPanel from "../components/ErrorPanel";
import Validation from "../components/Validation";

export default function Results() {
  const { migrationId } = useParams<{ migrationId: string }>();

  if (!migrationId) return <div className="p-8 text-red-600">Missing migration ID</div>;

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-2 flex items-center gap-4">
        <Link to={`/migrations/${migrationId}`} className="text-blue-600 hover:underline text-sm">← Back to Migration</Link>
        <Link to={`/report/${migrationId}`} className="text-blue-600 hover:underline text-sm">View Full Report →</Link>
      </div>

      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        Migration Results
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Validation migrationId={migrationId} />
        <TestResults migrationId={migrationId} />
      </div>

      <div className="mb-6">
        <ErrorPanel migrationId={migrationId} />
      </div>

      <div>
        <CodeDiff migrationId={migrationId} />
      </div>
    </div>
  );
}
