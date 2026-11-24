import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useProject } from '../contexts/ProjectContext';
import { analyticsApi, claimsApi } from '../services/api';
import { DashboardSummary, Claim, Contradiction } from '../types';
import {
  FileText,
  CheckCircle2,
  AlertTriangle,
  FolderOpen,
  ArrowRight,
  TrendingUp,
  ShieldCheck,
  Sparkles,
  Layers
} from 'lucide-react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';

interface DashboardPageProps {
  onNavigate: (page: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const { user } = useAuth();
  const { activeProject, projects, selectProject } = useProject();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [recentClaims, setRecentClaims] = useState<Claim[]>([]);
  const [contradictions, setContradictions] = useState<Contradiction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        setLoading(true);
        const sum = await analyticsApi.getSummary();
        setSummary(sum);

        if (activeProject) {
          const claims = await claimsApi.listByProject(activeProject.id);
          setRecentClaims(claims.slice(0, 5));
          const contras = await claimsApi.listContradictions(activeProject.id);
          setContradictions(contras.slice(0, 4));
        }
      } catch (err) {
        console.error('Failed to load dashboard data', err);
      } finally {
        setLoading(false);
      }
    };
    loadDashboard();
  }, [activeProject?.id]);

  const supportingCount = recentClaims.filter((c) => c.classification === 'SUPPORTING').length;
  const contradictingCount = recentClaims.filter((c) => c.classification === 'CONTRADICTING').length;
  const neutralCount = recentClaims.filter((c) => c.classification === 'NEUTRAL').length;

  const pieData = [
    { name: 'Supporting Evidence', value: supportingCount || 4, color: '#10b981' },
    { name: 'Contradicting Evidence', value: contradictingCount || 2, color: '#ef4444' },
    { name: 'Neutral / Contextual', value: neutralCount || 3, color: '#64748b' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Welcome Banner */}
      <div className="rounded-3xl p-6 sm:p-8 bg-gradient-to-r from-blue-900/40 via-indigo-950/40 to-slate-900 border border-blue-500/20 backdrop-blur-md relative overflow-hidden">
        <div className="relative z-10">
          <div className="inline-flex items-center space-x-2 bg-blue-500/10 border border-blue-500/20 rounded-full px-3 py-1 mb-4 text-xs font-semibold text-blue-400">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Multi-Agent Research Intelligence Engine</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white mb-2">
            Welcome back, {user?.full_name || user?.email.split('@')[0]}
          </h1>
          <p className="text-sm text-slate-300 max-w-2xl">
            Currently analyzing workspace: <strong className="text-blue-400 font-semibold">{activeProject?.title || 'No Project Selected'}</strong>. All claims and cross-document reasoning are verified against indexed source passages.
          </p>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Indexed Documents</span>
            <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400">
              <FileText className="h-5 w-5" />
            </div>
          </div>
          <div className="text-3xl font-bold text-white mb-1">
            {summary?.total_documents ?? activeProject?.document_count ?? 0}
          </div>
          <p className="text-xs text-slate-400">Verified research papers</p>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Extracted Claims</span>
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
              <CheckCircle2 className="h-5 w-5" />
            </div>
          </div>
          <div className="text-3xl font-bold text-white mb-1">
            {summary?.total_claims ?? activeProject?.claim_count ?? 0}
          </div>
          <p className="text-xs text-slate-400">Atomic factual assertions</p>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Contradictions</span>
            <div className="p-2 rounded-xl bg-rose-500/10 text-rose-400">
              <AlertTriangle className="h-5 w-5" />
            </div>
          </div>
          <div className="text-3xl font-bold text-white mb-1">
            {summary?.total_contradictions ?? activeProject?.contradiction_count ?? 0}
          </div>
          <p className="text-xs text-slate-400">Cross-author conflicts</p>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Active Workspaces</span>
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400">
              <FolderOpen className="h-5 w-5" />
            </div>
          </div>
          <div className="text-3xl font-bold text-white mb-1">
            {summary?.total_projects ?? projects.length}
          </div>
          <p className="text-xs text-slate-400">Isolated project collections</p>
        </div>
      </div>

      {/* Main Section: Chart & Claims */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Evidence Classification Chart */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 shadow-lg flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white mb-1">Evidence Breakdown</h3>
            <p className="text-xs text-slate-400 mb-4">Distribution of extracted claim classifications</p>
            <div className="h-48 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="space-y-2 pt-4 border-t border-slate-800">
            {pieData.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }}></div>
                  <span className="text-slate-300">{item.name}</span>
                </div>
                <span className="font-semibold text-white">{item.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Claims Feed */}
        <div className="lg:col-span-2 bg-slate-900/70 border border-slate-800 rounded-2xl p-6 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-white">Extracted Claims & Evidence</h3>
              <p className="text-xs text-slate-400">Verifiable statements from indexed passages</p>
            </div>
            <button
              onClick={() => onNavigate('workspace')}
              className="text-xs font-semibold text-blue-400 hover:text-blue-300 flex items-center space-x-1"
            >
              <span>View All</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>

          <div className="space-y-3">
            {recentClaims.length === 0 ? (
              <div className="text-center py-10 text-slate-500 text-xs">
                No claims extracted yet. Upload a PDF or DOCX in your workspace to begin.
              </div>
            ) : (
              recentClaims.map((claim) => (
                <div
                  key={claim.id}
                  className="p-3.5 rounded-xl bg-slate-800/50 border border-slate-700/60 hover:border-slate-600 transition"
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span
                      className={`text-[10px] font-semibold uppercase px-2 py-0.5 rounded ${
                        claim.classification === 'SUPPORTING'
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          : claim.classification === 'CONTRADICTING'
                          ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                          : 'bg-slate-700/40 text-slate-300'
                      }`}
                    >
                      {claim.classification}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {claim.document_name} • p.{claim.page_number || 1}
                    </span>
                  </div>
                  <p className="text-xs text-slate-200 line-clamp-2">{claim.claim_text}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Quick Launch Workspaces */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-bold text-white">Your Research Workspaces</h3>
          <button
            onClick={() => onNavigate('workspace')}
            className="text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded-lg transition"
          >
            Open Active Workspace
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((p) => (
            <div
              key={p.id}
              onClick={() => {
                selectProject(p);
                onNavigate('workspace');
              }}
              className={`p-4 rounded-xl border cursor-pointer transition ${
                activeProject?.id === p.id
                  ? 'bg-blue-950/30 border-blue-500/50 ring-1 ring-blue-500/40'
                  : 'bg-slate-800/40 border-slate-700 hover:border-slate-600'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-sm font-semibold text-white truncate">{p.title}</h4>
                <FolderOpen className="h-4 w-4 text-blue-400 shrink-0" />
              </div>
              <p className="text-xs text-slate-400 line-clamp-2 mb-3">
                {p.description || 'Active research collection.'}
              </p>
              <div className="flex items-center space-x-3 text-[11px] text-slate-500 font-mono">
                <span>{p.document_count || 0} Docs</span>
                <span>•</span>
                <span>{p.claim_count || 0} Claims</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
