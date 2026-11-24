import React from 'react';
import {
  Network,
  ShieldCheck,
  FileCheck2,
  GitCompare,
  ArrowRight,
  Database,
  Sparkles,
  Search,
  CheckCircle,
  FileText
} from 'lucide-react';

interface LandingPageProps {
  onGetStarted: () => void;
  onLogin: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onGetStarted, onLogin }) => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Top Bar */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Network className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white">
              EvidenceGraph<span className="text-blue-500">.AI</span>
            </span>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={onLogin}
              className="text-sm font-medium text-slate-300 hover:text-white px-3 py-1.5 transition"
            >
              Sign In
            </button>
            <button
              onClick={onGetStarted}
              className="text-sm font-semibold bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-xl shadow-lg shadow-blue-600/30 transition flex items-center space-x-1.5"
            >
              <span>Explore Platform</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-20 pb-24 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(59,130,246,0.18),rgba(255,255,255,0))]"></div>
        <div className="max-w-5xl mx-auto px-6 text-center relative z-10">
          <div className="inline-flex items-center space-x-2 bg-blue-500/10 border border-blue-500/20 rounded-full px-4 py-1.5 mb-8">
            <Sparkles className="h-4 w-4 text-blue-400" />
            <span className="text-xs font-semibold text-blue-300">
              Zero Hallucinations • 100% Traceable Research Evidence
            </span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white mb-6 leading-tight">
            Evidence-Grounded AI Research & <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-cyan-400 bg-clip-text text-transparent">
              Knowledge Intelligence
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-300 max-w-3xl mx-auto mb-10 leading-relaxed font-light">
            Upload complex scientific papers and multi-document corpuses. EvidenceGraph extracts atomic verifiable claims, detects direct contradictions across authors, and visually maps relationships in an interactive knowledge graph.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center space-y-3 sm:space-y-0 sm:space-x-4">
            <button
              onClick={onGetStarted}
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl text-base font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-xl shadow-blue-600/25 transition transform hover:-translate-y-0.5 flex items-center justify-center space-x-2"
            >
              <span>Launch Research Workspace</span>
              <ArrowRight className="h-5 w-5" />
            </button>
            <button
              onClick={onLogin}
              className="w-full sm:w-auto px-6 py-3.5 rounded-xl text-base font-medium bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800/80 transition"
            >
              Try Demo Project
            </button>
          </div>

          {/* Principle Banner */}
          <div className="mt-14 p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur max-w-2xl mx-auto flex items-center justify-center space-x-3 text-xs text-slate-300">
            <ShieldCheck className="h-5 w-5 text-emerald-400 shrink-0" />
            <span>
              <strong>Guiding Principle:</strong> Every factual claim generated is traceable to an exact document and page passage.
            </span>
          </div>
        </div>
      </section>

      {/* Feature Cards Grid */}
      <section className="py-20 border-t border-slate-900 bg-slate-950/50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-3">Enterprise-Grade Evidence Pipeline</h2>
            <p className="text-sm text-slate-400 max-w-2xl mx-auto">
              Moving beyond naive RAG: multi-stage extraction, reciprocal rank fusion, and contradiction resolution.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-blue-500/40 transition">
              <div className="h-12 w-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mb-4 text-blue-400">
                <FileText className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Multi-Format Ingestion</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                PyMuPDF, python-docx, and markdown parser preserving page numbers, section hierarchies, and layout geometry.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-indigo-500/40 transition">
              <div className="h-12 w-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mb-4 text-indigo-400">
                <Search className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Hybrid BM25 + Qdrant</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Combines BAAI/bge-small dense embeddings with BM25 keyword matching via Reciprocal Rank Fusion (RRF).
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-emerald-500/40 transition">
              <div className="h-12 w-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-4 text-emerald-400">
                <FileCheck2 className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Claim & Citation Engine</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Extracts atomic claims and strictly enforces numbered citations mapped to exact document passages.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-rose-500/40 transition">
              <div className="h-12 w-12 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center mb-4 text-rose-400">
                <GitCompare className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Contradiction Analysis</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Cross-document comparative intelligence identifying direct contradictions vs context-dependent differences.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-cyan-500/40 transition">
              <div className="h-12 w-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center mb-4 text-cyan-400">
                <Network className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Interactive React Flow</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Explore connected documents, claims, concepts, and relationships (`SUPPORTS`, `CONTRADICTS`) on an interactive canvas.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-purple-500/40 transition">
              <div className="h-12 w-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mb-4 text-purple-400">
                <Database className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Automated PDF Reports</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Export publication-ready research reports with executive summaries, findings, contradiction audits, and citation indices.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-8 text-center text-xs text-slate-500">
        <p>© 2026 EvidenceGraph AI. Designed for rigorous evidence-grounded scientific intelligence.</p>
      </footer>
    </div>
  );
};
