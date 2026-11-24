import React, { useEffect, useState, useMemo } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  Node,
  Edge
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useProject } from '../contexts/ProjectContext';
import { graphApi } from '../services/api';
import { CustomNode } from '../components/graph/CustomNode';
import {
  Network,
  Search,
  Filter,
  RefreshCw,
  FileText,
  AlertTriangle,
  Info,
  CheckCircle2,
  X
} from 'lucide-react';

export const GraphPage: React.FC = () => {
  const { activeProject } = useProject();
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [rawNodes, setRawNodes] = useState<Node[]>([]);
  const [rawEdges, setRawEdges] = useState<Edge[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRelFilter, setSelectedRelFilter] = useState('ALL');
  const [selectedNodeData, setSelectedNodeData] = useState<any | null>(null);

  const nodeTypes = useMemo(() => ({ customNode: CustomNode }), []);

  const loadGraph = async () => {
    if (!activeProject) return;
    try {
      setLoading(true);
      const data = await graphApi.getProjectGraph(activeProject.id);
      
      const formattedNodes: Node[] = data.nodes.map((n) => ({
        id: n.id,
        type: 'customNode',
        position: n.position,
        data: n.data,
      }));

      const formattedEdges: Edge[] = data.edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        label: e.label,
        type: 'smoothstep',
        animated: e.animated,
        style: e.style,
        data: e.data,
      }));

      setRawNodes(formattedNodes);
      setRawEdges(formattedEdges);
      setNodes(formattedNodes);
      setEdges(formattedEdges);
    } catch (err) {
      console.error('Failed to load knowledge graph', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGraph();
  }, [activeProject?.id]);

  // Handle filtering
  useEffect(() => {
    let filteredNodes = rawNodes;
    let filteredEdges = rawEdges;

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      filteredNodes = filteredNodes.filter((n) =>
        (n.data?.label as string || '').toLowerCase().includes(q)
      );
      const visibleNodeIds = new Set(filteredNodes.map((n) => n.id));
      filteredEdges = filteredEdges.filter(
        (e) => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target)
      );
    }

    if (selectedRelFilter !== 'ALL') {
      filteredEdges = filteredEdges.filter((e) => e.label === selectedRelFilter);
    }

    setNodes(filteredNodes);
    setEdges(filteredEdges);
  }, [searchQuery, selectedRelFilter, rawNodes, rawEdges]);

  const onNodeClick = (_: any, node: Node) => {
    setSelectedNodeData(node.data);
  };

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col bg-slate-950 relative">
      {/* Top Filter Bar */}
      <div className="p-4 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md flex flex-wrap items-center justify-between gap-4 z-20">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400">
            <Network className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white">Interactive Evidence Graph</h1>
            <p className="text-[11px] text-slate-400">
              {nodes.length} entities • {edges.length} relationships
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Node Search */}
          <div className="relative">
            <Search className="h-3.5 w-3.5 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Filter nodes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded-xl pl-8 pr-3 py-1.5 text-xs text-white focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          {/* Relationship Filter */}
          <select
            value={selectedRelFilter}
            onChange={(e) => setSelectedRelFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-xs text-slate-200 rounded-xl px-3 py-1.5 focus:outline-none"
          >
            <option value="ALL">All Relationships</option>
            <option value="CONTRADICTS">Contradictions (Red)</option>
            <option value="SUPPORTS">Supports (Green)</option>
            <option value="EXTRACTED_FROM">Extracted From (Blue)</option>
            <option value="RELATED_TO">Related To</option>
          </select>

          <button
            onClick={loadGraph}
            disabled={loading}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
            title="Refresh Graph"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* React Flow Canvas */}
      <div className="flex-1 w-full h-full relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          onNodeClick={onNodeClick}
          fitView
          attributionPosition="bottom-right"
        >
          <Background color="#1e293b" gap={20} size={1} />
          <Controls />
          <MiniMap
            nodeColor={(node: any) => {
              if (node.data?.node_type === 'DOCUMENT') return '#3b82f6';
              if (node.data?.classification === 'SUPPORTING') return '#10b981';
              if (node.data?.classification === 'CONTRADICTING') return '#ef4444';
              return '#a855f7';
            }}
            maskColor="rgba(3, 7, 18, 0.7)"
          />
        </ReactFlow>

        {/* Evidence Inspection Drawer */}
        {selectedNodeData && (
          <div className="absolute top-4 right-4 z-30 w-80 sm:w-96 bg-slate-900/95 border border-slate-800 rounded-2xl p-5 shadow-2xl backdrop-blur-md">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-blue-400">
                {selectedNodeData.node_type} INSPECTOR
              </span>
              <button
                onClick={() => setSelectedNodeData(null)}
                className="text-slate-400 hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-[10px] font-semibold text-slate-500 uppercase block mb-1">
                  Assertion / Label
                </span>
                <p className="font-semibold text-white">{selectedNodeData.label}</p>
              </div>

              {selectedNodeData.classification && (
                <div>
                  <span className="text-[10px] font-semibold text-slate-500 uppercase block mb-1">
                    Classification
                  </span>
                  <span
                    className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${
                      selectedNodeData.classification === 'SUPPORTING'
                        ? 'bg-emerald-500/20 text-emerald-300'
                        : selectedNodeData.classification === 'CONTRADICTING'
                        ? 'bg-rose-500/20 text-rose-300'
                        : 'bg-slate-700 text-slate-300'
                    }`}
                  >
                    {selectedNodeData.classification}
                  </span>
                </div>
              )}

              {selectedNodeData.passage && (
                <div>
                  <span className="text-[10px] font-semibold text-slate-500 uppercase block mb-1">
                    Supporting Passage Context (Page {selectedNodeData.page_number || 1})
                  </span>
                  <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/80 text-slate-300 leading-relaxed max-h-48 overflow-y-auto font-sans">
                    "{selectedNodeData.passage}"
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
