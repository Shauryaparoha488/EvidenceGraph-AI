import React from 'react';
import { Settings as SettingsIcon, Database, Cpu, Shield, Key } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="pb-4 border-b border-slate-800">
        <h1 className="text-2xl font-bold text-white flex items-center space-x-2">
          <SettingsIcon className="h-6 w-6 text-blue-500" />
          <span>System & Intelligence Settings</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Configure Gemini AI integration, local vector database parameters, and embedding providers.
        </p>
      </div>

      {/* Model & AI Settings */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 shadow-lg space-y-4">
        <div className="flex items-center space-x-2 text-sm font-bold text-white">
          <Cpu className="h-4 w-4 text-blue-400" />
          <h3>Generative AI Engine</h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block text-slate-400 mb-1">Primary LLM Provider</label>
            <input
              type="text"
              disabled
              value="Google Gemini 2.5 Flash"
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white font-mono"
            />
          </div>

          <div>
            <label className="block text-slate-400 mb-1">API Key Configuration</label>
            <input
              type="text"
              disabled
              value="GEMINI_API_KEY (Environment configured)"
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-emerald-400 font-mono"
            />
          </div>
        </div>
      </div>

      {/* Vector Store Settings */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 shadow-lg space-y-4">
        <div className="flex items-center space-x-2 text-sm font-bold text-white">
          <Database className="h-4 w-4 text-indigo-400" />
          <h3>Vector Database & Embeddings</h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block text-slate-400 mb-1">Vector Store Engine</label>
            <input
              type="text"
              disabled
              value="Qdrant Local Persistent Disk Storage"
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white font-mono"
            />
          </div>

          <div>
            <label className="block text-slate-400 mb-1">Embedding Model</label>
            <input
              type="text"
              disabled
              value="BAAI/bge-small-en-v1.5 (FastEmbed ONNX 384d)"
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-blue-400 font-mono"
            />
          </div>
        </div>
      </div>

      {/* Security & Isolation */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 shadow-lg space-y-4">
        <div className="flex items-center space-x-2 text-sm font-bold text-white">
          <Shield className="h-4 w-4 text-emerald-400" />
          <h3>Security & Tenant Isolation</h3>
        </div>

        <ul className="text-xs text-slate-300 space-y-2 list-disc pl-5">
          <li>User documents are strictly isolated per authenticated user ID.</li>
          <li>Passage chunking preserves original page numbers and section headers.</li>
          <li>Prompt injection defenses sanitize uploaded file text before LLM reasoning.</li>
          <li>All citations are validated strictly against real retrieved passages.</li>
        </ul>
      </div>
    </div>
  );
};
