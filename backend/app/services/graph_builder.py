"""Knowledge Graph builder using NetworkX with React Flow layout export and Neo4j abstraction."""
import math
from typing import List, Dict, Any, Optional
import networkx as nx

class KnowledgeGraphService:
    """Builds and serializes research evidence graphs from real extracted document data."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def build_project_graph(
        self,
        documents: List[Dict[str, Any]],
        claims: List[Dict[str, Any]],
        contradictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build NetworkX DiGraph and convert to React Flow graph format.
        Nodes:
        - Documents (DOCUMENT)
        - Extracted Claims (CLAIM)
        - Concepts / Entities (CONCEPT)
        Edges:
        - EXTRACTED_FROM (Claim -> Document)
        - SUPPORTS (Claim -> Claim / Concept)
        - CONTRADICTS (Claim -> Claim)
        - RELATED_TO (Claim -> Concept)
        - REFERENCES (Document -> Concept)
        """
        self.graph.clear()

        # 1. Add Document Nodes
        for doc in documents:
            doc_id = f"doc_{doc['id']}"
            self.graph.add_node(
                doc_id,
                label=doc.get("filename", "Document"),
                node_type="DOCUMENT",
                details={
                    "file_type": doc.get("file_type"),
                    "page_count": doc.get("page_count", 0),
                    "chunk_count": doc.get("chunk_count", 0),
                    "raw_id": doc["id"]
                }
            )

        # 2. Add Claim Nodes & Concepts
        concepts_seen = set()
        for claim in claims:
            claim_id = f"claim_{claim['id']}"
            classification = claim.get("classification", "NEUTRAL")
            label_text = claim.get("claim_text", "")
            if len(label_text) > 65:
                label_text = label_text[:62] + "..."

            self.graph.add_node(
                claim_id,
                label=label_text,
                node_type="CLAIM",
                classification=classification,
                document_id=claim.get("document_id"),
                page_number=claim.get("page_number"),
                passage=claim.get("supporting_passage"),
                details={
                    "confidence": claim.get("confidence", 1.0),
                    "raw_id": claim["id"],
                    "full_text": claim.get("claim_text", "")
                }
            )

            # Edge: Claim -> Document (EXTRACTED_FROM)
            if claim.get("document_id"):
                doc_node_id = f"doc_{claim['document_id']}"
                if self.graph.has_node(doc_node_id):
                    self.graph.add_edge(
                        claim_id,
                        doc_node_id,
                        label="EXTRACTED_FROM",
                        relationship="EXTRACTED_FROM"
                    )

            # Add Concepts and Edges
            keywords = claim.get("keywords") or []
            for kw in keywords[:3]:
                concept_id = f"concept_{kw.lower().strip()}"
                if concept_id not in concepts_seen:
                    concepts_seen.add(concept_id)
                    self.graph.add_node(
                        concept_id,
                        label=kw,
                        node_type="CONCEPT",
                        details={"concept_name": kw}
                    )
                # Edge: Claim -> Concept (RELATED_TO)
                self.graph.add_edge(
                    claim_id,
                    concept_id,
                    label="RELATED_TO",
                    relationship="RELATED_TO"
                )

        # 3. Add Contradiction Edges
        for contra in contradictions:
            c_a_id = f"claim_{contra['claim_a_id']}"
            c_b_id = f"claim_{contra['claim_b_id']}"
            if self.graph.has_node(c_a_id) and self.graph.has_node(c_b_id):
                self.graph.add_edge(
                    c_a_id,
                    c_b_id,
                    label="CONTRADICTS",
                    relationship="CONTRADICTS",
                    contradiction_type=contra.get("contradiction_type", "DIRECT"),
                    explanation=contra.get("explanation", "")
                )

        return self.to_react_flow_format()

    def to_react_flow_format(self) -> Dict[str, Any]:
        """Convert NetworkX graph into React Flow compatible nodes and edges with layered layout."""
        rf_nodes = []
        rf_edges = []

        # Group nodes by type for visual hierarchy
        doc_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("node_type") == "DOCUMENT"]
        claim_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("node_type") == "CLAIM"]
        concept_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("node_type") == "CONCEPT"]

        # Calculate coordinates
        # Row 0: Documents (Top)
        doc_spacing = 320
        start_x_doc = 100
        for i, node_id in enumerate(doc_nodes):
            data = self.graph.nodes[node_id]
            rf_nodes.append({
                "id": node_id,
                "type": "customNode",
                "position": {"x": start_x_doc + (i * doc_spacing), "y": 80},
                "data": {
                    "label": data.get("label", ""),
                    "node_type": data.get("node_type", "DOCUMENT"),
                    "details": data.get("details", {})
                }
            })

        # Row 1: Claims (Middle)
        claim_spacing_x = 280
        claim_cols = 4
        for i, node_id in enumerate(claim_nodes):
            data = self.graph.nodes[node_id]
            col = i % claim_cols
            row = i // claim_cols
            rf_nodes.append({
                "id": node_id,
                "type": "customNode",
                "position": {"x": 80 + (col * claim_spacing_x), "y": 280 + (row * 160)},
                "data": {
                    "label": data.get("label", ""),
                    "node_type": data.get("node_type", "CLAIM"),
                    "classification": data.get("classification", "NEUTRAL"),
                    "document_id": data.get("document_id"),
                    "page_number": data.get("page_number"),
                    "passage": data.get("passage"),
                    "details": data.get("details", {})
                }
            })

        # Row 2: Concepts (Bottom)
        concept_spacing = 220
        concept_y = 350 + (math.ceil(len(claim_nodes) / max(claim_cols, 1)) * 160)
        for i, node_id in enumerate(concept_nodes):
            data = self.graph.nodes[node_id]
            rf_nodes.append({
                "id": node_id,
                "type": "customNode",
                "position": {"x": 120 + (i * concept_spacing), "y": concept_y},
                "data": {
                    "label": data.get("label", ""),
                    "node_type": data.get("node_type", "CONCEPT"),
                    "details": data.get("details", {})
                }
            })

        # Edges
        edge_id_counter = 0
        for u, v, edge_data in self.graph.edges(data=True):
            edge_id_counter += 1
            rel = edge_data.get("relationship", "RELATED_TO")
            is_contradiction = rel == "CONTRADICTS"
            
            rf_edges.append({
                "id": f"e_{edge_id_counter}_{u}_{v}",
                "source": u,
                "target": v,
                "label": rel,
                "type": "smoothstep",
                "animated": is_contradiction,
                "style": {
                    "stroke": "#ef4444" if is_contradiction else ("#3b82f6" if rel == "EXTRACTED_FROM" else "#10b981"),
                    "strokeWidth": 2.5 if is_contradiction else 1.8
                },
                "data": edge_data
            })

        stats = {
            "total_nodes": len(rf_nodes),
            "documents_count": len(doc_nodes),
            "claims_count": len(claim_nodes),
            "concepts_count": len(concept_nodes),
            "total_edges": len(rf_edges)
        }

        return {
            "nodes": rf_nodes,
            "edges": rf_edges,
            "stats": stats
        }
