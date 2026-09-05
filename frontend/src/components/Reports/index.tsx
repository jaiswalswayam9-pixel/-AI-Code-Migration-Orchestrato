import React, { useEffect, useState } from 'react';
import { migrationApi } from '../../services/migrationApi';

interface ReportsProps {
  migrationId: string;
}

export default function Reports({ migrationId }: ReportsProps) {
  const [markdown, setMarkdown] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    migrationApi.report(migrationId)
      .then(res => {
        if (!res) return;
        const text = res.report_markdown || 
                     (res.report && typeof res.report === 'object' ? (res.report.markdown || JSON.stringify(res.report, null, 2)) : res.report) ||
                     (res.report_json ? JSON.stringify(res.report_json, null, 2) : (typeof res === 'string' ? res : JSON.stringify(res, null, 2)));
        setMarkdown(text);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [migrationId]);

  if (loading) return <div className="p-4">Loading report...</div>;
  if (!markdown) return <div className="p-4 text-gray-500">Report not generated yet.</div>;

  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold text-gray-900">Final Report</h3>
        <a 
          href={migrationApi.downloadUrl(migrationId)}
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition font-medium flex items-center gap-2"
          download
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
          Download ZIP
        </a>
      </div>
      
      <div className="prose prose-sm sm:prose-base max-w-none bg-gray-50 p-6 rounded border">
        {/* Basic render for markdown since external parsers aren't guaranteed */}
        <pre className="whitespace-pre-wrap font-sans text-gray-800">{markdown}</pre>
      </div>
    </div>
  );
}
