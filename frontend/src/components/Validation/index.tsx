import React, { useEffect, useState } from 'react';
import { migrationApi } from '../../services/migrationApi';

interface ValidationProps {
  migrationId: string;
}

export default function Validation({ migrationId }: ValidationProps) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    migrationApi.validation(migrationId)
      .then(res => setData(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [migrationId]);

  if (loading) return <div className="p-4">Loading validation...</div>;
  if (!data) return <div className="p-4 text-gray-500">No validation data available.</div>;

  const rawScore = data?.details?.score ?? data?.score ?? 0;
  const score = Math.round(Number(rawScore) || 0);

  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const safeScore = Math.min(100, Math.max(0, isNaN(score) ? 0 : score));
  const offset = circumference - (safeScore / 100) * circumference;

  const details = data?.details || data?.metrics || {};
  const displayMetrics: Array<{ label: string; value: number }> = [];

  if (details.type_coverage_percentage !== undefined) {
    displayMetrics.push({ label: 'Type Coverage', value: Number(details.type_coverage_percentage) });
  }
  if (details.structural_completeness_percentage !== undefined) {
    displayMetrics.push({ label: 'Structural Completeness', value: Number(details.structural_completeness_percentage) });
  }
  if (details.valid_syntax_files !== undefined && details.total_files) {
    const syntaxRate = Math.round((Number(details.valid_syntax_files) / Number(details.total_files)) * 100);
    displayMetrics.push({ label: 'Syntax Validity Rate', value: syntaxRate });
  }

  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold text-gray-900">Quality Validation</h3>
        <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
          (data.status || '').toUpperCase() === 'SUCCESS' ? 'bg-green-100 text-green-800' :
          (data.status || '').toUpperCase() === 'PARTIAL' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
        }`}>
          {data.status || 'PENDING'}
        </span>
      </div>
      
      <div className="flex items-center gap-8">
        <div className="relative w-32 h-32 flex items-center justify-center flex-shrink-0">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r={radius} stroke="currentColor" strokeWidth="8" fill="transparent" className="text-gray-200" />
            <circle cx="50" cy="50" r={radius} stroke="currentColor" strokeWidth="8" fill="transparent" 
              strokeDasharray={circumference} strokeDashoffset={isNaN(offset) ? 0 : offset}
              className={`${score >= 80 ? 'text-green-500' : score >= 50 ? 'text-yellow-500' : 'text-red-500'} transition-all duration-1000 ease-out`}
            />
          </svg>
          <div className="absolute text-2xl font-bold text-gray-800">{score}%</div>
        </div>

        <div className="flex-1 space-y-4">
          {displayMetrics.length > 0 ? (
            displayMetrics.map((item, idx) => (
              <div key={idx}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-medium text-gray-700">{item.label}</span>
                  <span className="text-gray-600 font-semibold">{item.value}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full transition-all duration-500" style={{ width: `${Math.min(100, Math.max(0, item.value))}%` }}></div>
                </div>
              </div>
            ))
          ) : (
            <p className="text-sm text-gray-500">Validation metrics computed successfully.</p>
          )}
        </div>
      </div>
    </div>
  );
}
