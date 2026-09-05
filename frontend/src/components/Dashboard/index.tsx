import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { projectApi } from '../../services/projectApi';
import type { Project, SampleProject } from '../../types/project';

export default function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [samples, setSamples] = useState<SampleProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  if (loading) return <div className="p-8 text-center text-gray-500">Loading dashboard...</div>;
  if (error) return <div className="p-8 text-center text-red-500">Error: {error}</div>;

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <h2 className="text-xl font-semibold mb-4">Overview</h2>
          <div className="flex items-center space-x-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <span className="block text-3xl font-bold text-blue-600">{projects.length}</span>
              <span className="text-sm text-gray-600">Total Projects</span>
            </div>
          </div>
          <div className="mt-6">
            <Link to="/upload" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition">
              Upload New Project
            </Link>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <h2 className="text-xl font-semibold mb-4">Sample Projects</h2>
          {samples.length === 0 ? (
            <p className="text-gray-500">No samples available.</p>
          ) : (
            <ul className="space-y-3">
              {samples.map(sample => (
                <li key={sample.id} className="flex justify-between items-center border-b pb-2">
                  <div>
                    <span className="block font-medium">{sample.name}</span>
                    <span className="text-xs text-gray-500">{sample.framework}</span>
                  </div>
                  <Link to={`/upload?sample=${sample.id}`} className="text-blue-500 hover:underline text-sm">
                    Load
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
