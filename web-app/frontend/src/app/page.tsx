'use client';
import { useState } from 'react';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsProcessing(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/redact`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to redact document');
      }

      // Download the returned file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `redacted_${file.name}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-950 text-slate-200">
      <div className="max-w-xl w-full bg-slate-900 p-8 rounded-2xl shadow-xl border border-slate-800">
        <h1 className="text-3xl font-bold mb-2 text-center text-white">PII Redactor</h1>
        <p className="text-slate-400 mb-8 text-center">Upload a DOCX file to automatically detect and redact Personally Identifiable Information.</p>

        <div className="flex flex-col items-center space-y-6">
          <label className="flex flex-col items-center justify-center w-full h-48 border-2 border-slate-700 border-dashed rounded-xl cursor-pointer bg-slate-800/50 hover:bg-slate-800 transition-colors">
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              <svg className="w-10 h-10 mb-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
              <p className="mb-2 text-sm text-slate-300">
                <span className="font-semibold">Click to upload</span> or drag and drop
              </p>
              <p className="text-xs text-slate-500">.docx files only</p>
            </div>
            <input 
              type="file" 
              className="hidden" 
              accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document" 
              onChange={handleFileChange}
            />
          </label>

          {file && (
            <div className="text-sm font-medium text-emerald-400 bg-emerald-400/10 px-4 py-2 rounded-lg w-full text-center">
              Selected: {file.name}
            </div>
          )}

          {error && (
            <div className="text-sm font-medium text-red-400 bg-red-400/10 px-4 py-2 rounded-lg w-full text-center">
              {error}
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!file || isProcessing}
            className={`w-full py-3 px-4 rounded-xl font-semibold text-white transition-all ${
              !file || isProcessing 
                ? 'bg-slate-700 cursor-not-allowed opacity-50' 
                : 'bg-blue-600 hover:bg-blue-500 active:scale-[0.98] shadow-lg shadow-blue-500/30'
            }`}
          >
            {isProcessing ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing Document...
              </span>
            ) : (
              'Redact Document'
            )}
          </button>
        </div>
      </div>
    </main>
  );
}
