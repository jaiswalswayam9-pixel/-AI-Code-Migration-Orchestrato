import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { projectApi } from '../../services/projectApi';
import type { SampleProject } from '../../types/project';

export default function ProjectUpload() {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [samples, setSamples] = useState<SampleProject[]>([]);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    projectApi.samples()
      .then(res => setSamples(res.samples))
      .catch(err => console.error('Failed to load samples:', err));
  }, []);

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(true);
  };

  const onDragLeave = () => setDragging(false);

  const handleFileUpload = async (file: File) => {
    if (!file.name.endsWith('.zip')) {
      setError('Please upload a .zip file.');
      return;
    }
    setUploading(true);
    setError(null);
    try {
      const res = await projectApi.upload(file);
      navigate(`/projects/${res.project_id}`);
    } catch (err: any) {
      setError(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleSampleLoad = async (sampleId: string) => {
    setUploading(true);
    setError(null);
    try {
      const res = await projectApi.loadSample(sampleId);
      navigate(`/projects/${res.project_id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to load sample');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Upload Project</h1>
      
      {error && <div className="bg-red-50 text-red-600 p-4 rounded mb-6">{error}</div>}

      <div
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        className={`border-4 border-dashed rounded-xl p-12 text-center transition-colors ${
          dragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'
        }`}
      >
        <div className="text-gray-500 mb-4">
          <svg className="mx-auto h-12 w-12 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p className="text-lg font-medium">Drag & Drop your project .zip file here</p>
          <p className="text-sm mt-2">or</p>
        </div>
        <input
          type="file"
          accept=".zip"
          onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
          className="hidden"
          id="file-upload"
          disabled={uploading}
        />
        <label
          htmlFor="file-upload"
          className="cursor-pointer bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition inline-block"
        >
          {uploading ? 'Uploading...' : 'Browse Files'}
        </label>
      </div>

      <div className="mt-12">
        <h2 className="text-2xl font-bold mb-4">Or load a sample project</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {samples.map((sample) => (
            <div key={sample.id} className="border p-4 rounded-lg hover:shadow-md transition bg-white">
              <h3 className="text-lg font-semibold">{sample.name}</h3>
              <p className="text-gray-600 text-sm mt-1">{sample.description}</p>
              <div className="mt-4 flex justify-between items-center">
                <span className="text-xs font-mono bg-gray-100 px-2 py-1 rounded text-gray-700">
                  {sample.framework}
                </span>
                <button
                  onClick={() => handleSampleLoad(sample.id)}
                  disabled={uploading}
                  className="text-blue-600 hover:text-blue-800 font-medium text-sm"
                >
                  Load Sample
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
