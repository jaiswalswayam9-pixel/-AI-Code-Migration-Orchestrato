import React, { useEffect, useState } from 'react';
import { migrationApi } from '../../services/migrationApi';

interface TestResultsProps {
  migrationId: string;
}

export default function TestResults({ migrationId }: TestResultsProps) {
  const [data, setData] = useState<{ passed: number; failed: number; log?: string; logs?: string } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    migrationApi.tests(migrationId)
      .then(res => setData(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [migrationId]);

  if (loading) return <div className="p-4">Loading tests...</div>;
  if (!data) return <div className="p-4 text-gray-500">No test data available.</div>;

  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
      <h3 className="text-xl font-bold mb-4 text-gray-900">Test Results</h3>
      <div className="flex gap-4 mb-6">
        <div className="bg-green-50 text-green-700 px-4 py-2 rounded-lg border border-green-200">
          <span className="font-bold text-2xl">{data.passed}</span> Passed
        </div>
        <div className="bg-red-50 text-red-700 px-4 py-2 rounded-lg border border-red-200">
          <span className="font-bold text-2xl">{data.failed}</span> Failed
        </div>
      </div>
      
      {(data.log || (data as any).logs) && (
        <div className="mt-4">
          <h4 className="font-semibold text-sm mb-2 text-gray-700">Test Output Logs</h4>
          <pre className="bg-gray-900 text-gray-100 p-4 rounded text-xs overflow-x-auto max-h-96">
            {data.log || (data as any).logs}
          </pre>
        </div>
      )}
    </div>
  );
}
