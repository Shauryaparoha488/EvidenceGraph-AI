export interface User {
  id: string;
  email: string;
  full_name?: string;
  created_at: string;
}

export interface Project {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  document_count: number;
  claim_count: number;
  contradiction_count: number;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  project_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  page_count: number;
  chunk_count: number;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  error_message?: string;
  created_at: string;
}

export interface DocumentChunk {
  id: string;
  document_id: string;
  chunk_index: number;
  page_number?: number;
  section?: string;
  content: string;
  token_count: number;
}

export type EvidenceClassification = 'SUPPORTING' | 'CONTRADICTING' | 'NEUTRAL' | 'INSUFFICIENT';

export interface Claim {
  id: string;
  project_id: string;
  document_id: string;
  document_name?: string;
  chunk_id?: string;
  claim_text: string;
  page_number?: number;
  supporting_passage: string;
  classification: EvidenceClassification;
  confidence: number;
  keywords: string[];
  created_at: string;
}

export type ContradictionType = 'DIRECT' | 'CONTEXT_DEPENDENT' | 'EXPERIMENTAL_DIFFERENCE' | 'COMPATIBLE_NUANCE' | 'UNRESOLVED';

export interface Contradiction {
  id: string;
  project_id: string;
  claim_a_id: string;
  claim_b_id: string;
  claim_a?: Claim;
  claim_b?: Claim;
  contradiction_type: ContradictionType;
  explanation: string;
  confidence: number;
  created_at: string;
}

export interface Citation {
  citation_id: number;
  document_id: string;
  document_name: string;
  page_number?: number;
  chunk_id?: string;
  exact_passage: string;
}

export interface StructuredAnswer {
  direct_answer: string;
  key_findings: string[];
  supporting_evidence: Array<{
    claim: string;
    citation_id?: number;
    document_name?: string;
    page_number?: number;
  }>;
  contradictory_evidence: Array<{
    conflict: string;
    source_a_citation?: number;
    source_b_citation?: number;
  }>;
  limitations: string[];
  evidence_sufficiency: 'SUFFICIENT' | 'PARTIALLY_SUFFICIENT' | 'INSUFFICIENT';
  unanswered_aspects: string[];
}

export interface ChatMessage {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  structured_answer?: StructuredAnswer;
  citations?: Citation[];
  sufficiency_assessment?: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  project_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

export interface GraphNodeData {
  label: string;
  node_type: 'DOCUMENT' | 'CLAIM' | 'CONCEPT';
  classification?: string;
  document_id?: string;
  page_number?: number;
  passage?: string;
  details?: Record<string, any>;
  [key: string]: any;
}

export interface KnowledgeGraphData {
  nodes: Array<{
    id: string;
    type: string;
    position: { x: number; y: number };
    data: GraphNodeData;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    label?: string;
    type?: string;
    animated?: boolean;
    style?: Record<string, any>;
    data?: Record<string, any>;
  }>;
  stats: {
    total_nodes: number;
    documents_count: number;
    claims_count: number;
    concepts_count: number;
    total_edges: number;
  };
}

export interface ResearchReport {
  id: string;
  project_id: string;
  title: string;
  research_question: string;
  executive_summary: string;
  key_findings: string[];
  supporting_evidence: any[];
  contradictory_findings: any[];
  limitations?: string;
  references: any[];
  conclusion: string;
  markdown_content: string;
  pdf_download_url?: string;
  created_at: string;
}

export interface DashboardSummary {
  total_projects: number;
  total_documents: number;
  total_claims: number;
  total_contradictions: number;
  recent_projects: Array<{
    id: string;
    title: string;
    description?: string;
    document_count: number;
    claim_count: number;
    created_at: string;
  }>;
}
