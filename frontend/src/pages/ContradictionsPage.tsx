import React, { useEffect, useState } from 'react';
import { useProject } from '../contexts/ProjectContext';
import { claimsApi } from '../services/api';
import { Contradiction } from '../types';
import {
  GitCompare,
  AlertTriangle,
  FileText,
  ExternalLink,
  ShieldAlert,
  Info
} from 'lucide-react';

export const ContradictionsPage: React.FC = () => {
  const { activeProject } = useProject();
  const [contradictions, setContradictions] = useState<Contradiction[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchContradictions = async () => {
      if (!activeProject) return;
      try {
        setLoading(true);
        const data = await claimsApi.listContradictions(activeProject.id);
        setContradictions(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchContradictions();
  }, [activeProject?.id]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="pb-4 border-b border-slate-800">
        <h1 className="text-2xl font-bold text-white flex items-center space-x-2">
          <GitCompare className="h-6 w-6 text-rose-500" />
          <span>Evidence Disagreement & Contradiction Engine</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Identifying direct contradictions, context-dependent variances, and experimental discrepancies across research documents.
        </p>
      </div>

      {loading ? (
        <div className="text-center py-12 text-xs text-blue-400">
          Analyzing claims across document library...
        </div>
      ) : contradictions.length === 0 ? (
        <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-12 text-center max-w-xl mx-auto space-y-3">
          <div className="h-12 w-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto">
            <ShieldAlert className="h-6 w-6" />
          </div>
          <h3 className="text-base font-bold text-white">No Direct Contradictions Detected</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            All extracted claims across the uploaded papers appear empirically consistent or non-conflicting. Upload additional comparative papers to discover conflicting findings.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {contradictions.map((contra) => (
            <div
              key={contra.id}
              className="bg-slate-900/80 border border-rose-500/30 rounded-2xl p-6 shadow-xl relative overflow-hidden"
            >
              <div className="flex items-center justify-between mb-4">
                <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
                  <AlertTriangle className="h-3.5 w-3.5" />
                  <span>{contra.contradiction_type} CONTRADICTION</span>
                </span>
                <span className="text-xs text-slate-500 font-mono">
                  Confidence: {(contra.confidence * 100).toFixed(0)}%
                </span>
              </div>

              {/* Side-by-side Claims */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                {/* Claim A */}
                <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700">
                  <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono mb-2">
                    <span className="flex items-center space-x-1 font-semibold text-blue-400">
                      <FileText className="h-3.5 w-3.5" />
                      <span>{contra.claim_a?.document_name || 'Document A'}</span>
                    </span>
                    <span>Page {contra.claim_a?.page_number || 1}</span>
                  </div>
                  <p className="text-xs text-white font-medium mb-3">
                    "{contra.claim_a?.claim_text}"
                  </p>
                  <div className="text-[11px] text-slate-400 italic bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
                    "{contra.claim_a?.supporting_passage}"
                  </div>
                </div>

                {/* Claim B */}
                <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700">
                  <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono mb-2">
                    <span className="flex items-center space-x-1 font-semibold text-rose-400">
                      <FileText className="h-3.5 w-3.5" />
                      <span>{contra.claim_b?.document_name || 'Document B'}</span>
                    </span>
                    <span>Page {contra.claim_b?.page_number || 1}</span>
                  </div>
                  <p className="text-xs text-white font-medium mb-3">
                    "{contra.claim_b?.claim_text}"
                  </p>
                  <div className="text-[11px] text-slate-400 italic bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
                    "{contra.claim_b?.supporting_passage}"
                  </div>
                </div>
              </div>

              {/* Contradiction Analysis Explanation */}
              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 flex items-start space-x-2">
                <Info className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="text-white block mb-0.5">Discrepancy Analysis:</strong>
                  {contra.explanation}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
