import React, { useEffect, useState } from 'react';
import { migrationApi } from '../../services/migrationApi';

interface CodeDiffProps {
  migrationId: string;
}

export default function CodeDiff({ migrationId }: CodeDiffProps) {
  const [diffs, setDiffs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [viewMode, setViewMode] = useState<'sideBySide' | 'migratedOnly' | 'unifiedDiff'>('sideBySide');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    migrationApi.diff(migrationId)
      .then(res => {
        setDiffs(res.diffs || []);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [migrationId]);

  if (loading) return <div className="p-8 text-center text-gray-500">Loading code diffs and migrated files...</div>;
  if (diffs.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 border border-gray-200 text-center text-gray-500">
        No code diffs available yet.
      </div>
    );
  }

  const activeDiff = diffs[selectedIdx] || diffs[0];
  const activeFileName = activeDiff.file_path || activeDiff.to_file || activeDiff.from_file || 'Unknown File';
  const originalCode = activeDiff.original_code || '';
  const migratedCode = activeDiff.migrated_code || '';
  const unifiedDiff = activeDiff.diff_content || activeDiff.unified_diff || '';

  const handleCopy = () => {
    const textToCopy = viewMode === 'unifiedDiff' ? unifiedDiff : migratedCode;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
      {/* Header & Controls */}
      <div className="p-4 border-b border-gray-200 bg-gray-50 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold text-gray-900">Migrated Code & Comparison</h3>
          <p className="text-xs text-gray-500 mt-0.5">
            {diffs.length} migrated file(s) available • Select a file and view mode below
          </p>
        </div>

        {/* View Mode Toggle Buttons */}
        <div className="flex items-center gap-2">
          <div className="inline-flex rounded-md shadow-sm bg-white p-1 border border-gray-300">
            <button
              onClick={() => setViewMode('sideBySide')}
              className={`px-3 py-1.5 text-xs font-medium rounded ${
                viewMode === 'sideBySide'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              Side-by-Side View
            </button>
            <button
              onClick={() => setViewMode('migratedOnly')}
              className={`px-3 py-1.5 text-xs font-medium rounded ${
                viewMode === 'migratedOnly'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              Migrated Code
            </button>
            <button
              onClick={() => setViewMode('unifiedDiff')}
              className={`px-3 py-1.5 text-xs font-medium rounded ${
                viewMode === 'unifiedDiff'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              Unified Diff
            </button>
          </div>

          <button
            onClick={handleCopy}
            className="px-3 py-1.5 text-xs font-medium rounded border border-gray-300 bg-white hover:bg-gray-50 text-gray-700 flex items-center gap-1 shadow-sm"
          >
            {copied ? (
              <>
                <span className="text-green-600">✓</span> Copied!
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy Code
              </>
            )}
          </button>
        </div>
      </div>

      {/* File Selector Tabs */}
      <div className="flex overflow-x-auto border-b border-gray-200 bg-gray-100 px-2 py-2 gap-1.5">
        {diffs.map((d, idx) => {
          const name = d.file_path || d.to_file || d.from_file || `File ${idx + 1}`;
          const isSelected = idx === selectedIdx;
          return (
            <button
              key={idx}
              onClick={() => setSelectedIdx(idx)}
              className={`px-3 py-1.5 text-xs font-mono rounded-md border whitespace-nowrap transition flex items-center gap-2 ${
                isSelected
                  ? 'bg-white border-blue-500 text-blue-700 font-semibold shadow-sm ring-1 ring-blue-500'
                  : 'bg-gray-200/70 border-transparent text-gray-600 hover:bg-white hover:text-gray-900'
              }`}
            >
              <span>{name}</span>
              {d.additions > 0 && <span className="text-green-600 font-sans font-bold text-[10px]">+{d.additions}</span>}
              {d.deletions > 0 && <span className="text-red-600 font-sans font-bold text-[10px]">-{d.deletions}</span>}
            </button>
          );
        })}
      </div>

      {/* Active File Header */}
      <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 text-xs font-mono text-gray-600 flex justify-between items-center">
        <div>
          <span className="font-semibold text-gray-800">Target File:</span> {activeFileName}
          {activeDiff.from_file && activeDiff.from_file !== '/dev/null' && (
            <span className="ml-3 text-gray-500">
              (Source: <span className="text-gray-700">{activeDiff.from_file}</span>)
            </span>
          )}
        </div>
        <div className="flex gap-2">
          {activeDiff.additions > 0 && (
            <span className="bg-green-100 text-green-800 px-2 py-0.5 rounded text-[11px] font-sans">
              +{activeDiff.additions} lines
            </span>
          )}
          {activeDiff.deletions > 0 && (
            <span className="bg-red-100 text-red-800 px-2 py-0.5 rounded text-[11px] font-sans">
              -{activeDiff.deletions} lines
            </span>
          )}
        </div>
      </div>

      {/* View Mode 1: Side-by-Side */}
      {viewMode === 'sideBySide' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-gray-200 text-xs font-mono">
          {/* Left: Original Java Code */}
          <div className="flex flex-col">
            <div className="bg-amber-50/80 px-4 py-2 border-b border-gray-200 text-amber-900 font-semibold flex items-center justify-between">
              <span>☕ Original Java Source</span>
              <span className="text-[11px] font-normal text-amber-700">
                {activeDiff.from_file && activeDiff.from_file !== '/dev/null' ? activeDiff.from_file : 'Newly Created File'}
              </span>
            </div>
            <div className="p-4 bg-gray-50 overflow-x-auto max-h-[600px] overflow-y-auto">
              {originalCode ? (
                <table className="w-full border-collapse">
                  <tbody>
                    {originalCode.split('\n').map((line: string, i: number) => (
                      <tr key={i} className="hover:bg-amber-100/40">
                        <td className="w-8 pr-3 text-right text-gray-400 select-none text-[11px] align-top">{i + 1}</td>
                        <td className="whitespace-pre text-gray-800">{line || ' '}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="text-gray-400 italic p-4 text-center">No original source file (Newly generated file)</div>
              )}
            </div>
          </div>

          {/* Right: Migrated Target Code */}
          <div className="flex flex-col">
            <div className="bg-blue-50/80 px-4 py-2 border-b border-gray-200 text-blue-900 font-semibold flex items-center justify-between">
              <span>🚀 Migrated Target Code</span>
              <span className="text-[11px] font-normal text-blue-700">{activeFileName}</span>
            </div>
            <div className="p-4 bg-white overflow-x-auto max-h-[600px] overflow-y-auto">
              {migratedCode ? (
                <table className="w-full border-collapse">
                  <tbody>
                    {migratedCode.split('\n').map((line: string, i: number) => (
                      <tr key={i} className="hover:bg-blue-50/60">
                        <td className="w-8 pr-3 text-right text-gray-400 select-none text-[11px] align-top">{i + 1}</td>
                        <td className="whitespace-pre text-gray-900">{line || ' '}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="text-gray-400 italic p-4 text-center">No migrated code generated</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* View Mode 2: Migrated Only */}
      {viewMode === 'migratedOnly' && (
        <div className="bg-gray-950 text-gray-100 p-4 overflow-x-auto max-h-[600px] overflow-y-auto font-mono text-xs">
          {migratedCode ? (
            <table className="w-full border-collapse">
              <tbody>
                {migratedCode.split('\n').map((line: string, i: number) => (
                  <tr key={i} className="hover:bg-gray-900">
                    <td className="w-10 pr-4 text-right text-gray-600 select-none text-[11px] align-top">{i + 1}</td>
                    <td className="whitespace-pre text-emerald-300">{line || ' '}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="text-gray-500 italic p-4 text-center">No code available</div>
          )}
        </div>
      )}

      {/* View Mode 3: Unified Diff */}
      {viewMode === 'unifiedDiff' && (
        <div className="bg-gray-50 p-4 overflow-x-auto max-h-[600px] overflow-y-auto font-mono text-xs">
          {unifiedDiff ? (
            unifiedDiff.split('\n').map((line: string, i: number) => {
              let bg = '';
              let textColor = 'text-gray-800';
              if (line.startsWith('+') && !line.startsWith('+++')) {
                bg = 'bg-green-100 text-green-900';
                textColor = 'text-green-900 font-semibold';
              } else if (line.startsWith('-') && !line.startsWith('---')) {
                bg = 'bg-red-100 text-red-900';
                textColor = 'text-red-900 line-through';
              } else if (line.startsWith('@@')) {
                bg = 'bg-blue-50 text-blue-600 font-semibold';
                textColor = 'text-blue-600';
              } else if (line.startsWith('---') || line.startsWith('+++')) {
                textColor = 'text-gray-500 font-bold';
              }

              return (
                <div key={i} className={`px-2 py-0.5 whitespace-pre ${bg} ${textColor}`}>
                  {line || ' '}
                </div>
              );
            })
          ) : (
            <div className="text-gray-400 italic p-4 text-center">No diff changes detected</div>
          )}
        </div>
      )}
    </div>
  );
}
