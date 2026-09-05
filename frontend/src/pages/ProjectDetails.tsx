import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { projectApi } from "../services/projectApi";
import type { Project } from "../types/project";
import MigrationConfig from "../components/MigrationConfig";

export default function ProjectDetails() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (projectId) {
      projectApi.get(projectId).then(setProject).catch((e) => setError(e.message));
    }
  }, [projectId]);

  if (error) return <div className="p-8 text-red-600">Error: {error}</div>;
  if (!project) return <div className="p-8 text-gray-500">Loading project...</div>;

  const analysis = project.analysis;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-2">
        <Link to="/" className="text-blue-600 hover:underline text-sm">← Back to Dashboard</Link>
      </div>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
          <p className="text-gray-500 text-sm mt-1">
            Status: <span className={`font-medium ${project.status === "analyzed" ? "text-green-600" : "text-yellow-600"}`}>{project.status}</span>
            {" • "}{project.file_count} Java file(s)
            {" • "}Uploaded {new Date(project.uploaded_at).toLocaleString()}
          </p>
        </div>
      </div>

      {analysis && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow border p-6">
            <h2 className="text-lg font-semibold mb-4 text-gray-900">Project Analysis</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 p-3 rounded">
                <span className="block text-2xl font-bold text-blue-600">{analysis.class_count}</span>
                <span className="text-sm text-gray-600">Classes</span>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <span className="block text-2xl font-bold text-purple-600">{analysis.interface_count}</span>
                <span className="text-sm text-gray-600">Interfaces</span>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <span className="block text-2xl font-bold text-green-600">{analysis.method_count}</span>
                <span className="text-sm text-gray-600">Methods</span>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <span className="block text-2xl font-bold text-orange-600">{analysis.enum_count}</span>
                <span className="text-sm text-gray-600">Enums</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow border p-6">
            <h2 className="text-lg font-semibold mb-4 text-gray-900">Build Info</h2>
            <dl className="space-y-3">
              <div className="flex justify-between">
                <dt className="text-gray-500">Build Tool</dt>
                <dd className="font-medium capitalize">{analysis.build_tool || "Unknown"}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Java Version</dt>
                <dd className="font-medium">{analysis.java_version || "Unknown"}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Framework</dt>
                <dd className="font-medium">{analysis.framework || "Standard Java"}</dd>
              </div>
              {analysis.framework_version && (
                <div className="flex justify-between">
                  <dt className="text-gray-500">Framework Version</dt>
                  <dd className="font-medium">{analysis.framework_version}</dd>
                </div>
              )}
              {analysis.dependencies && analysis.dependencies.length > 0 && (
                <div>
                  <dt className="text-gray-500 mb-2">Dependencies ({analysis.dependencies.length})</dt>
                  <dd>
                    <ul className="space-y-1">
                      {analysis.dependencies.map((dep, i) => (
                        <li key={i} className="text-sm bg-gray-50 px-2 py-1 rounded font-mono">
                          {dep.name || `${dep.group_id}:${dep.artifact_id}`}
                          {dep.version && <span className="text-gray-400 ml-1">:{dep.version}</span>}
                        </li>
                      ))}
                    </ul>
                  </dd>
                </div>
              )}
            </dl>

            {(analysis.controller_count || analysis.service_count || analysis.repository_count || analysis.entity_count) && (
              <div className="mt-4 pt-4 border-t">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Spring Boot Components</h3>
                <div className="flex gap-3 flex-wrap">
                  {analysis.controller_count ? <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded">{analysis.controller_count} Controllers</span> : null}
                  {analysis.service_count ? <span className="text-xs bg-teal-100 text-teal-700 px-2 py-1 rounded">{analysis.service_count} Services</span> : null}
                  {analysis.repository_count ? <span className="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded">{analysis.repository_count} Repositories</span> : null}
                  {analysis.entity_count ? <span className="text-xs bg-pink-100 text-pink-700 px-2 py-1 rounded">{analysis.entity_count} Entities</span> : null}
                </div>
              </div>
            )}
          </div>

          {analysis.parse_errors && analysis.parse_errors.length > 0 && (
            <div className="md:col-span-2 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h3 className="text-sm font-medium text-yellow-800 mb-2">Parse Warnings ({analysis.parse_errors.length})</h3>
              <ul className="text-sm text-yellow-700 space-y-1">
                {analysis.parse_errors.map((e, i) => (
                  <li key={i} className="font-mono">{e.file}: {e.message}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <MigrationConfig
        projectId={projectId!}
        projectName={project.name}
        analysis={analysis}
      />
    </div>
  );
}
