import React, { useEffect, useState } from 'react';
import { useProject } from '../contexts/ProjectContext';
import { reportsApi } from '../services/api';
import { ResearchReport } from '../types';
import {
  FileCheck,
  Download,
  Plus,
  FileCode,
  Sparkles,
  ExternalLink,
  ChevronRight
} from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const { activeProject } = useProject();
  const [reports, setReports] = useState<ResearchReport[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [researchQuestion, setResearchQuestion] = useState('');
  const [selectedReport, setSelectedReport] = useState<ResearchReport | null>(null);

  const loadReports = async () => {
    if (!activeProject) return;
    try {
      setLoading(true);
      const data = await reportsApi.listByProject(activeProject.id);
      setReports(data);
      if (data.length > 0 && !selectedReport) {
        setSelectedReport(data[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReports();
  }, [activeProject?.id]);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!researchQuestion.trim() || !activeProject || generating) return;

    try {
      setGenerating(true);
      const newReport = await reportsApi.generate(activeProject.id, researchQuestion.trim());
      setResearchQuestion('');
      await loadReports();
      setSelectedReport(newReport);
    } catch (err) {
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="pb-4 border-b border-slate-800">
        <h1 className="text-2xl font-bold text-white flex items-center space-x-2">
          <FileCheck className="h-6 w-6 text-blue-500" />
          <span>Research Intelligence Reports</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Synthesize investigation reports with traceable citations, contradiction audits, and instant PDF/Markdown exports.
        </p>
      </div>

      {/* Report Generator Prompt */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-lg">
        <h3 className="text-sm font-bold text-white mb-2">Generate New Investigation Report</h3>
        <form onSubmit={handleGenerate} className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            required
            placeholder="e.g. What are the key empirical trade-offs between batch size and learning rate?"
            value={researchQuestion}
            onChange={(e) => setResearchQuestion(e.target.value)}
            className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={generating || !researchQuestion.trim()}
            className="px-6 py-2.5 rounded-xl font-semibold bg-blue-600 hover:bg-blue-500 text-white text-xs shadow-lg shadow-blue-600/30 transition flex items-center justify-center space-x-2 disabled:opacity-50 shrink-0"
          >
            <Sparkles className="h-4 w-4" />
            <span>{generating ? 'Synthesizing...' : 'Generate Report'}</span>
          </button>
        </form>
      </div>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Reports Sidebar */}
        <div className="lg:col-span-4 bg-slate-900/70 border border-slate-800 rounded-2xl p-4 shadow-lg space-y-3">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
            Investigation Archive ({reports.length})
          </span>

          <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
            {reports.length === 0 ? (
              <div className="text-center py-8 text-xs text-slate-500">
                No reports generated yet. Enter a research question above.
              </div>
            ) : (
              reports.map((rep) => (
                <div
                  key={rep.id}
                  onClick={() => setSelectedReport(rep)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition ${
                    selectedReport?.id === rep.id
                      ? 'bg-blue-950/40 border-blue-500/60 ring-1 ring-blue-500/30'
                      : 'bg-slate-800/40 border-slate-700 hover:border-slate-600'
                  }`}
                >
                  <h4 className="text-xs font-semibold text-white truncate mb-1">{rep.title}</h4>
                  <p className="text-[11px] text-slate-400 line-clamp-1 mb-2 font-mono">
                    {rep.research_question}
                  </p>
                  <div className="text-[10px] text-slate-500 font-mono">
                    {new Date(rep.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Report Preview Panel */}
        <div className="lg:col-span-8 bg-slate-900/70 border border-slate-800 rounded-2xl p-6 shadow-lg">
          {selectedReport ? (
            <div className="space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
                <div>
                  <h2 className="text-lg font-bold text-white">{selectedReport.title}</h2>
                  <p className="text-xs text-slate-400 mt-0.5 font-mono">
                    Research Question: {selectedReport.research_question}
                  </p>
                </div>

                <div className="flex items-center space-x-2 shrink-0">
                  {selectedReport.pdf_download_url && (
                    <a
                      href={selectedReport.pdf_download_url}
                      target="_blank"
                      rel="noreferrer"
                      className="px-3 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md transition flex items-center space-x-1"
                    >
                      <Download className="h-3.5 w-3.5" />
                      <span>PDF Export</span>
                    </a>
                  )}
                  <a
                    href={`/api/reports/${selectedReport.id}/markdown`}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition flex items-center space-x-1"
                  >
                    <FileCode className="h-3.5 w-3.5" />
                    <span>Markdown</span>
                  </a>
                </div>
              </div>

              {/* Render Report Sections */}
              <div className="space-y-5 text-xs text-slate-300">
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400 mb-1">
                    1. Executive Summary
                  </h3>
                  <p className="leading-relaxed bg-slate-800/40 p-3.5 rounded-xl border border-slate-700/60">
                    {selectedReport.executive_summary}
                  </p>
                </div>

                {selectedReport.key_findings && selectedReport.key_findings.length > 0 && (
                  <div>
                    <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400 mb-1">
                      2. Key Findings
                    </h3>
                    <ul className="list-disc pl-5 space-y-1">
                      {selectedReport.key_findings.map((kf, i) => (
                        <li key={i}>{kf}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {selectedReport.supporting_evidence && selectedReport.supporting_evidence.length > 0 && (
                  <div>
                    <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400 mb-1">
                      3. Supporting Evidence
                    </h3>
                    <div className="space-y-1.5">
                      {selectedReport.supporting_evidence.map((ev: any, i: number) => (
                        <div key={i} className="p-2.5 rounded-lg bg-slate-800/50 border border-slate-700/60">
                          <strong>{ev.document_name}</strong> (Page {ev.page_number}): {ev.claim}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400 mb-1">
                    4. Conclusion
                  </h3>
                  <p className="leading-relaxed">{selectedReport.conclusion}</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-20 text-xs text-slate-500">
              Select or generate a report to inspect.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
