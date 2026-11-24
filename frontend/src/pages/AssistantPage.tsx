import React, { useState } from 'react';
import { useProject } from '../contexts/ProjectContext';
import { chatApi } from '../services/api';
import { ChatMessage, Citation } from '../types';
import {
  Sparkles,
  Send,
  ShieldCheck,
  ExternalLink,
  BookOpen,
  AlertTriangle,
  CheckCircle,
  HelpCircle
} from 'lucide-react';

export const AssistantPage: React.FC = () => {
  const { activeProject } = useProject();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputQuery.trim() || !activeProject || loading) return;

    const query = inputQuery.trim();
    setInputQuery('');

    const tempUserMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      conversation_id: 'conv',
      role: 'user',
      content: query,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setLoading(true);

    try {
      const response = await chatApi.sendMessage(activeProject.id, query);
      setMessages((prev) => [...prev, response]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 h-[calc(100vh-80px)] flex flex-col">
      {/* Header */}
      <div className="pb-4 border-b border-slate-800 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2">
            <Sparkles className="h-5 w-5 text-blue-400" />
            <span>AI Research Assistant</span>
          </h1>
          <p className="text-xs text-slate-400">
            Precision synthesis with automatic claim-to-passage citation validation
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs text-slate-400 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-full">
          <BookOpen className="h-3.5 w-3.5 text-blue-400" />
          <span>Active: {activeProject?.title}</span>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto py-6 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-8">
            <div className="h-14 w-14 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 mb-4">
              <Sparkles className="h-7 w-7" />
            </div>
            <h2 className="text-lg font-bold text-white mb-2">Evidence-Grounded Querying</h2>
            <p className="text-xs text-slate-400 max-w-md mb-6 leading-relaxed">
              Every answer is synthesized directly from your uploaded research papers. If evidence is insufficient or contradictory, the assistant will explicitly communicate it.
            </p>
            <div className="flex flex-wrap gap-2 justify-center max-w-lg">
              <button
                onClick={() => setInputQuery('Does increasing learning rate always improve convergence?')}
                className="px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 hover:border-blue-500/50 transition"
              >
                "Does increasing learning rate always improve convergence?"
              </button>
              <button
                onClick={() => setInputQuery('Compare experimental methodologies and sample sizes across the papers.')}
                className="px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 hover:border-blue-500/50 transition"
              >
                "Compare experimental methodologies across papers."
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
                className={`max-w-[90%] rounded-2xl p-5 text-xs leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white rounded-br-none shadow-md'
                    : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-none shadow-xl'
                }`}
              >
                {/* Sufficiency Badge */}
                {msg.sufficiency_assessment && (
                  <div className="mb-3 flex items-center space-x-1.5">
                    <span
                      className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                        msg.sufficiency_assessment === 'SUFFICIENT'
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          : msg.sufficiency_assessment === 'PARTIALLY_SUFFICIENT'
                          ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                          : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                      }`}
                    >
                      Evidence {msg.sufficiency_assessment}
                    </span>
                  </div>
                )}

                <div className="whitespace-pre-wrap text-[13px]">{msg.content}</div>

                {/* Structured Breakdown Card */}
                {msg.structured_answer && (
                  <div className="mt-4 pt-4 border-t border-slate-800 space-y-3">
                    {msg.structured_answer.key_findings.length > 0 && (
                      <div>
                        <span className="text-[11px] font-bold uppercase tracking-wider text-blue-400 block mb-1">
                          Key Research Findings
                        </span>
                        <ul className="list-disc pl-4 space-y-1 text-slate-300">
                          {msg.structured_answer.key_findings.map((kf, i) => (
                            <li key={i}>{kf}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {msg.structured_answer.contradictory_evidence.length > 0 && (
                      <div className="p-3 rounded-xl bg-rose-950/20 border border-rose-500/30 text-rose-300">
                        <span className="text-[11px] font-bold uppercase tracking-wider block mb-1">
                          Contradictory / Conflicting Evidence
                        </span>
                        {msg.structured_answer.contradictory_evidence.map((ce, i) => (
                          <div key={i}>• {ce.conflict}</div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Citations Footer */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-800 flex flex-wrap gap-2 items-center">
                    <span className="text-[10px] font-bold text-slate-400">CITATIONS:</span>
                    {msg.citations.map((c) => (
                      <button
                        key={c.citation_id}
                        onClick={() => setSelectedCitation(c)}
                        className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20 text-[11px] hover:bg-blue-500/20 transition"
                      >
                        <span className="font-bold">[{c.citation_id}]</span>
                        <span className="max-w-[140px] truncate">{c.document_name}</span>
                        <span className="text-[9px] text-slate-500 font-mono">p.{c.page_number}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {loading && (
          <div className="flex items-center space-x-2 text-xs text-blue-400 py-3">
            <Sparkles className="h-4 w-4 animate-spin" />
            <span>Analyzing evidence across multi-document corpus...</span>
          </div>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="pt-3 border-t border-slate-800 flex items-center space-x-3">
        <input
          type="text"
          placeholder="Ask a question supported by traceable evidence..."
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          className="flex-1 bg-slate-900 border border-slate-800 rounded-2xl px-5 py-3 text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-inner"
        />
        <button
          type="submit"
          disabled={loading || !inputQuery.trim()}
          className="p-3 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/30 transition disabled:opacity-50"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>

      {/* Citation Modal */}
      {selectedCitation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold px-2.5 py-1 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                Citation [{selectedCitation.citation_id}]
              </span>
              <button onClick={() => setSelectedCitation(null)} className="text-xs text-slate-400 hover:text-white">
                Close
              </button>
            </div>
            <h3 className="text-base font-bold text-white mb-1">{selectedCitation.document_name}</h3>
            <p className="text-xs text-slate-400 mb-4 font-mono">Page {selectedCitation.page_number || 1}</p>
            <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700 text-xs text-slate-200 leading-relaxed max-h-60 overflow-y-auto">
              "{selectedCitation.exact_passage}"
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
