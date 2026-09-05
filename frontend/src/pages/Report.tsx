import { useParams, Link } from "react-router-dom";
import Reports from "../components/Reports";

export default function Report() {
  const { migrationId } = useParams<{ migrationId: string }>();

  if (!migrationId) return <div className="p-8 text-red-600">Missing migration ID</div>;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-2 flex items-center gap-4">
        <Link to={`/migrations/${migrationId}`} className="text-blue-600 hover:underline text-sm">← Back to Migration</Link>
        <Link to={`/results/${migrationId}`} className="text-blue-600 hover:underline text-sm">← View Results</Link>
      </div>
      <Reports migrationId={migrationId} />
    </div>
  );
}
