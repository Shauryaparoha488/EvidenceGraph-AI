import React, { useState } from 'react';
import { useProject } from '../contexts/ProjectContext';
import { documentsApi, chatApi } from '../services/api';
import { ChatMessage, Citation } from '../types';
import {
  Upload,
  FileText,
  MessageSquare,
  Sparkles,
  Send,
  CheckCircle2,
  AlertTriangle,
  ExternalLink,
  Layers,
  ChevronRight,
  ShieldCheck
} from 'lucide-react';

interface WorkspacePageProps {
  onNavigate: (page: string) => void;
}

export const WorkspacePage: React.FC<WorkspacePageProps> = ({ onNavigate }) => {
  const { activeProject, documents, refreshDocuments } = useProject();
  const [uploading, setUploading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuery, setInputQuery] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0 || !activeProject) return;
    const file = e.target.files[0];
    try {
      setUploading(true);
      await documentsApi.upload(activeProject.id, file);
      await refreshDocuments();
    } catch (err) {
      console.error('File upload error', err);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleSendChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputQuery.trim() || !activeProject || chatLoading) return;

    const query = inputQuery.trim();
    setInputQuery('');

    // Optimistic user message
    const tempUserMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      conversation_id: 'active',
      role: 'user',
      content: query,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setChatLoading(true);

    try {
      const response = await chatApi.sendMessage(activeProject.id, query);
      setMessages((prev) => [...prev, response]);
    } catch (err) {
      console.error('Chat error', err);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Workspace Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center space-x-2">
            <span>{activeProject?.title || 'Research Workspace'}</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Grounded multi-document analysis • {documents.length} indexed research papers
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => onNavigate('graph')}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition flex items-center space-x-1.5"
          >
            <Layers className="h-4 w-4 text-blue-400" />
            <span>Interactive Graph</span>
          </button>
          <button
            onClick={() => onNavigate('reports')}
            className="px-3.5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white shadow-lg shadow-blue-600/30 transition flex items-center space-x-1.5"
          >
            <span>Generate Report</span>
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Main Workspace Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Document Upload & Library */}
        <div className="lg:col-span-4 space-y-6">
          {/* Upload Dropzone */}
          <div className="bg-slate-900/80 border-2 border-dashed border-slate-700/80 hover:border-blue-500/60 rounded-2xl p-6 text-center transition">
            <Upload className="h-8 w-8 text-blue-400 mx-auto mb-2" />
            <h3 className="text-sm font-semibold text-white mb-1">Upload Research Documents</h3>
            <p className="text-xs text-slate-400 mb-4">PDF, DOCX, TXT, or Markdown (Max 25MB)</p>
            <label className="cursor-pointer inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition">
              <span>{uploading ? 'Processing File...' : 'Choose File'}</span>
              <input
                type="file"
                disabled={uploading}
                accept=".pdf,.docx,.doc,.txt,.md"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>
          </div>

          {/* Document List */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-lg">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Indexed Papers</h3>
              <span className="text-xs font-mono text-slate-500">{documents.length} Total</span>
            </div>

            <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
              {documents.length === 0 ? (
                <div className="text-center py-8 text-xs text-slate-500">
                  No documents in this workspace yet.
                </div>
              ) : (
                documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/50 flex items-center justify-between hover:border-slate-600 transition"
                  >
                    <div className="flex items-center space-x-2.5 truncate">
                      <FileText className="h-4 w-4 text-blue-400 shrink-0" />
                      <div className="truncate">
                        <div className="text-xs font-medium text-slate-200 truncate">{doc.filename}</div>
                        <div className="text-[10px] text-slate-400 font-mono">
                          {doc.page_count} pages • {doc.chunk_count} chunks
                        </div>
                      </div>
                    </div>
                    <span
                      className={`text-[9px] font-bold uppercase px-1.5 py-0.5 rounded shrink-0 ${
                        doc.status === 'COMPLETED'
                          ? 'bg-emerald-500/20 text-emerald-300'
                          : doc.status === 'PROCESSING'
                          ? 'bg-amber-500/20 text-amber-300'
                          : 'bg-rose-500/20 text-rose-300'
                      }`}
                    >
                      {doc.status}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Research AI Grounded Chat */}
        <div className="lg:col-span-8 bg-slate-900/70 border border-slate-800 rounded-2xl flex flex-col h-[650px] shadow-lg">
          {/* Chat Header */}
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <MessageSquare className="h-5 w-5 text-blue-400" />
              <h2 className="text-sm font-bold text-white">Grounded AI Research Assistant</h2>
            </div>
            <div className="flex items-center space-x-1.5 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-full">
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>Strict Citation Validation Active</span>
            </div>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-400">
                <Sparkles className="h-10 w-10 text-blue-500/50 mb-3" />
                <h3 className="text-base font-semibold text-slate-200 mb-1">
                  Ask Complex Research Questions
                </h3>
                <p className="text-xs max-w-md text-slate-400 mb-6">
                  EvidenceGraph retrieves relevant multi-document passages, extracts claims, checks for contradictions, and outputs verifiable citations.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left max-w-lg w-full">
                  <button
                    onClick={() => setInputQuery('Does increasing the learning rate always improve model convergence?')}
                    className="p-2.5 rounded-xl bg-slate-800/60 border border-slate-700/60 text-xs text-slate-300 hover:border-blue-500/50 transition"
                  >
                    "Does increasing the learning rate always improve model convergence?"
                  </button>
                  <button
                    onClick={() => setInputQuery('What experimental contradictions exist across the uploaded papers?')}
                    className="p-2.5 rounded-xl bg-slate-800/60 border border-slate-700/60 text-xs text-slate-300 hover:border-blue-500/50 transition"
                  >
                    "What experimental contradictions exist across the uploaded papers?"
                  </button>
                </div>
              </div>
            ) : (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl p-4 text-xs leading-relaxed ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white rounded-br-none shadow-md'
                        : 'bg-slate-800/80 border border-slate-700/70 text-slate-200 rounded-bl-none shadow-lg'
                    }`}
                  >
                    <div className="font-sans whitespace-pre-wrap">{msg.content}</div>

                    {/* Key Findings List */}
                    {msg.structured_answer?.key_findings && msg.structured_answer.key_findings.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-slate-700/60 space-y-1">
                        <strong className="text-[11px] uppercase tracking-wider text-blue-400 block">
                          Key Evidence Findings:
                        </strong>
                        <ul className="list-disc pl-4 space-y-1 text-slate-300">
                          {msg.structured_answer.key_findings.map((f, i) => (
                            <li key={i}>{f}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Citations Pills */}
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="mt-3 pt-2.5 border-t border-slate-700/60 flex flex-wrap gap-1.5 items-center">
                        <span className="text-[10px] font-semibold text-slate-400">Sources:</span>
                        {msg.citations.map((c) => (
                          <button
                            key={c.citation_id}
                            onClick={() => setSelectedCitation(c)}
                            className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-blue-500/20 text-blue-300 border border-blue-500/30 text-[10px] hover:bg-blue-500/30 transition"
                          >
                            <span>[{c.citation_id}]</span>
                            <span className="max-w-[120px] truncate">{c.document_name}</span>
                            <ExternalLink className="h-2.5 w-2.5 opacity-70" />
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}

            {chatLoading && (
              <div className="flex items-center space-x-2 text-xs text-blue-400 py-2">
                <Sparkles className="h-4 w-4 animate-spin" />
                <span>Retrieving evidence and checking contradictions...</span>
              </div>
            )}
          </div>

          {/* Chat Input */}
          <form onSubmit={handleSendChat} className="p-3 border-t border-slate-800 flex items-center space-x-2">
            <input
              type="text"
              placeholder="Ask a question grounded in your document library..."
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              className="flex-1 bg-slate-800/80 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={chatLoading || !inputQuery.trim()}
              className="p-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/30 transition disabled:opacity-50"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      </div>

      {/* Citation Inspector Modal */}
      {selectedCitation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                Citation [{selectedCitation.citation_id}]
              </span>
              <button
                onClick={() => setSelectedCitation(null)}
                className="text-xs text-slate-400 hover:text-white"
              >
                Close
              </button>
            </div>
            <h3 className="text-base font-bold text-white mb-1">{selectedCitation.document_name}</h3>
            <p className="text-xs text-slate-400 mb-4 font-mono">Page {selectedCitation.page_number || 1}</p>
            <div className="p-4 rounded-xl bg-slate-800/70 border border-slate-700 text-xs text-slate-200 leading-relaxed max-h-60 overflow-y-auto">
              "{selectedCitation.exact_passage}"
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
