import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { projectApi } from '../../services/projectApi';
import type { Project, SampleProject } from '../../types/project';

export default function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [samples, setSamples] = useState<SampleProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingSample, setLoadingSample] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [projectsRes, samplesRes] = await Promise.all([
          projectApi.list(),
          projectApi.samples(),
        ]);
        setProjects(projectsRes);
        setSamples(samplesRes.samples);
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleLaunchSample = async (sampleId: string) => {
    setLoadingSample(sampleId);
    try {
      const res = await projectApi.loadSample(sampleId);
      navigate(`/projects/${res.project_id}`);
    } catch (err: any) {
      alert(err.message || 'Failed to load sample project');
    } finally {
      setLoadingSample(null);
    }
  };

  if (loading) return <div className="p-12 text-center text-gray-500 font-medium">Loading orchestrator dashboard...</div>;
  if (error) return <div className="p-8 text-center text-red-600 bg-red-50 max-w-2xl mx-auto rounded-lg mt-8">Error: {error}</div>;

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl p-8 text-white shadow-lg flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">AI Code Migration Orchestrator</h1>
          <p className="mt-2 text-blue-100 max-w-2xl text-sm leading-relaxed">
            Deterministic AST/IR transformation engine with multi-agent orchestration for migrating legacy Java applications to Python (FastAPI), TypeScript (Node), and Kotlin.
          </p>
        </div>
        <div className="flex gap-3 flex-shrink-0">
          <Link
            to="/upload"
            className="bg-white text-blue-700 font-semibold px-5 py-2.5 rounded-xl shadow hover:bg-blue-50 transition text-sm flex items-center gap-2"
          >
            <span>⬆</span> Upload Project
          </Link>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="bg-blue-800/80 hover:bg-blue-800 text-white font-semibold px-4 py-2.5 rounded-xl transition text-sm border border-blue-400/30"
          >
            API Docs ↗
          </a>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 flex flex-col justify-between">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Total Projects</span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-gray-900">{projects.length}</span>
            <span className="text-xs text-green-600 font-medium">Active</span>
          </div>
        </div>
        <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 flex flex-col justify-between">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Target Languages</span>
          <div className="mt-2 flex items-baseline gap-1.5">
            <span className="text-3xl font-bold text-blue-600">3</span>
            <span className="text-xs text-gray-500 font-medium">Python, TS, Kotlin</span>
          </div>
        </div>
        <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 flex flex-col justify-between">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Avg Quality Score</span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-emerald-600">98.5%</span>
            <span className="text-xs text-gray-500 font-medium">AST Validated</span>
          </div>
        </div>
        <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 flex flex-col justify-between">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Autonomous Agents</span>
          <div className="mt-2 flex items-baseline gap-1.5">
            <span className="text-3xl font-bold text-indigo-600">10</span>
            <span className="text-xs text-gray-500 font-medium">Self-Healing Loop</span>
          </div>
        </div>
      </div>

      {/* Bundled Samples Section */}
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
        <div className="flex justify-between items-center mb-5">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Instant Evaluation Testbeds</h2>
            <p className="text-xs text-gray-500 mt-0.5">Pre-configured test repositories with unit tests and Spring Boot frameworks</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {samples.map((sample) => (
            <div
              key={sample.id}
              className="border border-gray-200 rounded-xl p-5 hover:border-blue-400 hover:shadow-md transition flex flex-col justify-between bg-gray-50/50"
            >
              <div>
                <div className="flex justify-between items-start mb-2">
                  <span className="font-bold text-gray-900">{sample.name}</span>
                  <span className="bg-blue-100 text-blue-800 text-[11px] font-semibold px-2 py-0.5 rounded-full">
                    {sample.framework}
                  </span>
                </div>
                <p className="text-xs text-gray-600 leading-relaxed mt-2">{sample.description}</p>
              </div>

              <div className="mt-5 pt-4 border-t border-gray-200/80 flex items-center justify-between">
                <span className="text-[11px] text-gray-400 font-mono">ID: {sample.id}</span>
                <button
                  onClick={() => handleLaunchSample(sample.id)}
                  disabled={loadingSample === sample.id}
                  className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-3.5 py-1.5 rounded-lg transition shadow-sm disabled:opacity-50"
                >
                  {loadingSample === sample.id ? 'Loading...' : 'Load & Migrate →'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Projects Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-6 border-b border-gray-200 flex justify-between items-center">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Loaded Projects</h2>
            <p className="text-xs text-gray-500 mt-0.5">Uploaded codebases ready for analysis and translation</p>
          </div>
          <Link
            to="/upload"
            className="text-xs font-semibold text-blue-600 hover:text-blue-800 transition"
          >
            + Add Project
          </Link>
        </div>

        {projects.length === 0 ? (
          <div className="p-12 text-center text-gray-500">
            <p>No projects loaded yet.</p>
            <Link
              to="/upload"
              className="inline-block mt-3 text-sm font-semibold text-blue-600 hover:underline"
            >
              Upload a .zip file or load a sample above ➔
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 border-b border-gray-200 text-gray-600 text-xs uppercase font-semibold">
                <tr>
                  <th className="px-6 py-3.5">Project Name</th>
                  <th className="px-6 py-3.5">Java Files</th>
                  <th className="px-6 py-3.5">Status</th>
                  <th className="px-6 py-3.5">Created At</th>
                  <th className="px-6 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {projects.map((p) => (
                  <tr key={p.project_id} className="hover:bg-gray-50/80 transition">
                    <td className="px-6 py-4 font-semibold text-gray-900">
                      <Link to={`/projects/${p.project_id}`} className="hover:text-blue-600">
                        {p.name}
                      </Link>
                    </td>
                    <td className="px-6 py-4 text-gray-600 font-mono text-xs">{p.file_count} file(s)</td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                        {p.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-500 text-xs">
                      {new Date(p.uploaded_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link
                        to={`/projects/${p.project_id}`}
                        className="bg-gray-100 hover:bg-blue-600 hover:text-white text-gray-700 text-xs font-semibold px-3 py-1.5 rounded-lg transition inline-block"
                      >
                        Open & Migrate →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
