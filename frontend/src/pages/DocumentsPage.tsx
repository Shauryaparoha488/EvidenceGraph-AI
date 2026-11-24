import React, { useState } from 'react';
import { useProject } from '../contexts/ProjectContext';
import { documentsApi } from '../services/api';
import { Document } from '../types';
import {
  FileText,
  Upload,
  Trash2,
  Download,
  Eye,
  CheckCircle2,
  Clock,
  AlertCircle
} from 'lucide-react';

export const DocumentsPage: React.FC = () => {
  const { activeProject, documents, refreshDocuments } = useProject();
  const [uploading, setUploading] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0 || !activeProject) return;
    const file = e.target.files[0];
    try {
      setUploading(true);
      await documentsApi.upload(activeProject.id, file);
      await refreshDocuments();
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleDelete = async (docId: string) => {
    if (!confirm('Are you sure you want to delete this document and its vector embeddings?')) return;
    try {
      await documentsApi.delete(docId);
      await refreshDocuments();
      if (selectedDoc?.id === docId) setSelectedDoc(null);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Document Intelligence Library</h1>
          <p className="text-xs text-slate-400 mt-1">
            Uploaded corpus for workspace: <strong className="text-blue-400">{activeProject?.title}</strong>
          </p>
        </div>

        <label className="cursor-pointer inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/30 transition">
          <Upload className="h-4 w-4" />
          <span>{uploading ? 'Processing File...' : 'Upload Document'}</span>
          <input
            type="file"
            disabled={uploading}
            accept=".pdf,.docx,.doc,.txt,.md"
            onChange={handleUpload}
            className="hidden"
          />
        </label>
      </div>

      {/* Documents Table */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-800/60 border-b border-slate-700/60 text-slate-400 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="px-6 py-3.5">Document Name</th>
                <th className="px-6 py-3.5">Format</th>
                <th className="px-6 py-3.5">Size</th>
                <th className="px-6 py-3.5">Pages</th>
                <th className="px-6 py-3.5">Chunks</th>
                <th className="px-6 py-3.5">Status</th>
                <th className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 text-slate-300">
              {documents.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-500">
                    No documents found in this workspace. Upload your first research paper above.
                  </td>
                </tr>
              ) : (
                documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-800/40 transition">
                    <td className="px-6 py-4 font-medium text-white flex items-center space-x-2.5">
                      <FileText className="h-4 w-4 text-blue-400 shrink-0" />
                      <span className="truncate max-w-[220px]">{doc.filename}</span>
                    </td>
                    <td className="px-6 py-4 uppercase font-mono text-[11px] text-slate-400">
                      {doc.file_type}
                    </td>
                    <td className="px-6 py-4 font-mono text-[11px] text-slate-400">
                      {(doc.file_size / (1024 * 1024)).toFixed(2)} MB
                    </td>
                    <td className="px-6 py-4 font-mono">{doc.page_count}</td>
                    <td className="px-6 py-4 font-mono">{doc.chunk_count}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center space-x-1 text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                          doc.status === 'COMPLETED'
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            : doc.status === 'PROCESSING'
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                        }`}
                      >
                        {doc.status === 'COMPLETED' ? (
                          <CheckCircle2 className="h-3 w-3" />
                        ) : doc.status === 'PROCESSING' ? (
                          <Clock className="h-3 w-3 animate-spin" />
                        ) : (
                          <AlertCircle className="h-3 w-3" />
                        )}
                        <span>{doc.status}</span>
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      <a
                        href={documentsApi.getDownloadUrl(doc.id)}
                        target="_blank"
                        rel="noreferrer"
                        className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition inline-block"
                        title="View / Download Source"
                      >
                        <Download className="h-4 w-4" />
                      </a>
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition"
                        title="Delete Document"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
