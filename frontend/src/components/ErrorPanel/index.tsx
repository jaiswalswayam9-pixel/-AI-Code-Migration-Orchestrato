import React, { useEffect, useState } from 'react';
import { migrationApi } from '../../services/migrationApi';

interface ErrorPanelProps {
  migrationId: string;
}

export default function ErrorPanel({ migrationId }: ErrorPanelProps) {
  const [errors, setErrors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    migrationApi.errors(migrationId)
      .then(res => setErrors(res.errors || []))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [migrationId]);

  if (loading) return <div className="p-4">Loading errors...</div>;
  if (errors.length === 0) return null;

  return (
    <div className="bg-red-50 rounded-lg shadow p-6 border border-red-200">
      <h3 className="text-xl font-bold mb-4 text-red-800 flex items-center">
        <svg className="w-6 h-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        Errors & Warnings
      </h3>
      <div className="space-y-3">
        {errors.map((err, idx) => (
          <div key={idx} className="bg-white p-3 rounded shadow-sm border-l-4 border-red-500">
            <div className="font-semibold text-sm text-gray-800">{err.type || 'Error'}</div>
            <div className="text-sm text-gray-600 mt-1">{err.message}</div>
            {err.file && <div className="text-xs text-gray-400 mt-2">File: {err.file}</div>}
          </div>
        ))}
      </div>
    </div>
  );
}
