import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { FileText, CheckCircle2, AlertTriangle, HelpCircle, Tag } from 'lucide-react';
import { GraphNodeData } from '../../types';

export const CustomNode = memo(({ data }: { data: GraphNodeData }) => {
  const isDocument = data.node_type === 'DOCUMENT';
  const isClaim = data.node_type === 'CLAIM';
  const isConcept = data.node_type === 'CONCEPT';

  // Classification coloring
  let borderClass = 'border-slate-700 bg-slate-900/90';
  let badgeColor = 'bg-slate-800 text-slate-300';
  let Icon = FileText;

  if (isDocument) {
    borderClass = 'border-blue-500/60 bg-blue-950/40 shadow-lg shadow-blue-500/10';
    badgeColor = 'bg-blue-500/20 text-blue-300 border border-blue-500/30';
    Icon = FileText;
  } else if (isClaim) {
    if (data.classification === 'SUPPORTING') {
      borderClass = 'border-emerald-500/60 bg-emerald-950/30 shadow-lg shadow-emerald-500/10';
      badgeColor = 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';
      Icon = CheckCircle2;
    } else if (data.classification === 'CONTRADICTING') {
      borderClass = 'border-rose-500/70 bg-rose-950/30 shadow-lg shadow-rose-500/20 ring-1 ring-rose-500/30';
      badgeColor = 'bg-rose-500/20 text-rose-300 border border-rose-500/30';
      Icon = AlertTriangle;
    } else {
      borderClass = 'border-slate-600/60 bg-slate-900/80';
      badgeColor = 'bg-slate-700/50 text-slate-300';
      Icon = HelpCircle;
    }
  } else if (isConcept) {
    borderClass = 'border-purple-500/50 bg-purple-950/30 shadow-md shadow-purple-500/10 rounded-full px-4 py-2';
    badgeColor = 'bg-purple-500/20 text-purple-300';
    Icon = Tag;
  }

  return (
    <div className={`p-3 rounded-xl border backdrop-blur-md max-w-[260px] text-xs transition-all hover:scale-105 ${borderClass}`}>
      <Handle type="target" position={Position.Top} className="!bg-slate-400 !w-2 !h-2" />
      
      <div className="flex items-center space-x-2 mb-1.5">
        <Icon className="h-3.5 w-3.5 shrink-0 opacity-80" />
        <span className={`text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded ${badgeColor}`}>
          {isDocument ? 'Document' : isClaim ? (data.classification || 'Claim') : 'Concept'}
        </span>
        {data.page_number && (
          <span className="text-[10px] text-slate-400 ml-auto font-mono">
            p.{data.page_number}
          </span>
        )}
      </div>

      <div className="font-medium text-slate-100 leading-snug line-clamp-3">
        {data.label}
      </div>

      <Handle type="source" position={Position.Bottom} className="!bg-slate-400 !w-2 !h-2" />
    </div>
  );
});
