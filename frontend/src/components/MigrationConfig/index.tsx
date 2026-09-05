import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { migrationApi } from '../../services/migrationApi';
import type { TargetLanguage, MigrationMode } from '../../types/migration';
import type { ProjectAnalysis } from '../../types/project';

interface MigrationConfigProps {
  projectId: string;
  projectName: string;
  analysis?: ProjectAnalysis | null;
}

export default function MigrationConfig({ projectId, projectName, analysis }: MigrationConfigProps) {
  const [targetLanguage, setTargetLanguage] = useState<TargetLanguage>('python');
  const [mode, setMode] = useState<MigrationMode>('suggest');
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleStart = async () => {
    setStarting(true);
    setError(null);
    try {
      const res = await migrationApi.start({
        project_id: projectId,
        target_language: targetLanguage,
        mode: mode,
      });
      navigate(`/migrations/${res.migration_id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to start migration');
      setStarting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
      <h2 className="text-2xl font-bold mb-6 text-gray-900">Configure Migration</h2>
      
      {error && <div className="bg-red-50 text-red-600 p-3 rounded mb-4">{error}</div>}
      
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-3">Target Language</h3>
          <div className="grid grid-cols-3 gap-4">
            {(['python', 'typescript', 'kotlin'] as TargetLanguage[]).map(lang => (
              <label
                key={lang}
                className={`border rounded-lg p-4 cursor-pointer flex flex-col items-center transition-colors ${
                  targetLanguage === lang ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500' : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <input
                  type="radio"
                  name="language"
                  value={lang}
                  checked={targetLanguage === lang}
                  onChange={(e) => setTargetLanguage(e.target.value as TargetLanguage)}
                  className="hidden"
                />
                <span className="capitalize font-medium">{lang}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-3">Migration Mode</h3>
          <div className="space-y-3">
            {[
              { id: 'analyze_only', label: 'Analyze Only', desc: 'Detailed analysis without code changes' },
              { id: 'suggest', label: 'Suggest', desc: 'Propose changes and wait for approval' },
              { id: 'autonomous', label: 'Autonomous', desc: 'Fully automated end-to-end migration' },
            ].map((m) => (
              <label
                key={m.id}
                className={`flex items-center p-4 border rounded-lg cursor-pointer transition-colors ${
                  mode === m.id ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500' : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <input
                  type="radio"
                  name="mode"
                  value={m.id}
                  checked={mode === m.id}
                  onChange={(e) => setMode(e.target.value as MigrationMode)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500"
                />
                <div className="ml-4">
                  <span className="block text-sm font-medium text-gray-900">{m.label}</span>
                  <span className="block text-sm text-gray-500">{m.desc}</span>
                </div>
              </label>
            ))}
          </div>
        </div>

        <div className="pt-4 border-t border-gray-200 flex justify-end">
          <button
            onClick={handleStart}
            disabled={starting}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition"
          >
            {starting ? 'Starting...' : 'Start Migration'}
          </button>
        </div>
      </div>
    </div>
  );
}
