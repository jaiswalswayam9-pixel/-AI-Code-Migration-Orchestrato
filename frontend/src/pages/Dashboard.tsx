import { Link } from "react-router-dom";
import { useProjects } from "../hooks/useProject";
import DashboardComponent from "../components/Dashboard";

export default function Dashboard() {
  const { projects, loading, error } = useProjects();

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <DashboardComponent />

      <div className="mt-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Your Projects</h2>
          <Link
            to="/upload"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition"
          >
            + Upload Project
          </Link>
        </div>

        {loading && <p className="text-gray-500">Loading projects...</p>}
        {error && <p className="text-red-600">Failed to load projects: {error}</p>}

        {!loading && !error && projects.length === 0 && (
          <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
            <p className="text-gray-500 text-lg">No projects yet.</p>
            <p className="text-gray-400 mt-2">Upload a Java project or load a sample to get started.</p>
          </div>
        )}

        {projects.length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200 divide-y">
            {projects.map((p) => (
              <Link
                key={p.project_id}
                to={`/projects/${p.project_id}`}
                className="flex items-center justify-between p-4 hover:bg-gray-50 transition"
              >
                <div>
                  <span className="font-medium text-gray-900">{p.name}</span>
                  <span className="block text-sm text-gray-500 mt-1">
                    {p.file_count} file(s) • Uploaded {new Date(p.uploaded_at).toLocaleDateString()}
                  </span>
                </div>
                <span className={`text-xs font-medium px-3 py-1 rounded-full ${
                  p.status === "analyzed" ? "bg-green-100 text-green-700" :
                  p.status === "error" ? "bg-red-100 text-red-700" :
                  "bg-yellow-100 text-yellow-700"
                }`}>
                  {p.status}
                </span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
