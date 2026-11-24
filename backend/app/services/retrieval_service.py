"""Hybrid retrieval engine combining Qdrant dense vector search with BM25 keyword matching."""
import re
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from sqlalchemy.orm import Session

from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore

class RetrievalService:
    """Orchestrates dense semantic search, sparse BM25, Reciprocal Rank Fusion, and deduplication."""

    def __init__(self, db: Session):
        self.db = db
        self.vector_store = VectorStore.get_instance()
        self.embedding_service = EmbeddingService.get_instance()

    def tokenize_text(self, text: str) -> List[str]:
        """Simple lowercase word tokenizer for BM25."""
        return re.findall(r'\b\w+\b', text.lower())

    def dense_search(
        self,
        query: str,
        project_id: str,
        document_ids: Optional[List[str]] = None,
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        """Vector semantic search via Qdrant."""
        query_vector = self.embedding_service.embed_query(query)
        results = self.vector_store.search(
            query_vector=query_vector,
            project_id=project_id,
            document_ids=document_ids,
            limit=limit
        )
        for r in results:
            r["method"] = "dense"
        return results

    def sparse_search(
        self,
        query: str,
        project_id: str,
        document_ids: Optional[List[str]] = None,
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        """BM25 keyword search across project chunks in SQL."""
        query_terms = self.tokenize_text(query)
        if not query_terms:
            return []

        # Fetch candidate chunks for the project
        query_builder = (
            self.db.query(DocumentChunk, Document.filename)
            .join(Document, Document.id == DocumentChunk.document_id)
            .filter(Document.project_id == project_id)
        )

        if document_ids:
            query_builder = query_builder.filter(Document.id.in_(document_ids))

        chunks_with_doc = query_builder.all()
        if not chunks_with_doc:
            return []

        corpus = [self.tokenize_text(chunk.content) for chunk, _ in chunks_with_doc]
        bm25 = BM25Okapi(corpus)
        scores = bm25.get_scores(query_terms)

        scored_chunks = []
        for (chunk, filename), score in zip(chunks_with_doc, scores):
            if score > 0.05:  # Relevance threshold
                scored_chunks.append({
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "document_name": filename,
                    "page_number": chunk.page_number,
                    "section": chunk.section,
                    "content": chunk.content,
                    "score": float(score),
                    "method": "sparse"
                })

        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:limit]

    def reciprocal_rank_fusion(
        self,
        dense_results: List[Dict[str, Any]],
        sparse_results: List[Dict[str, Any]],
        k: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Merge ranked lists using Reciprocal Rank Fusion (RRF):
        RRF_score(d) = sum(1 / (k + rank_i(d)))
        """
        rrf_scores = {}
        passages_by_id = {}

        # Process dense rankings
        for rank, item in enumerate(dense_results):
            cid = item.get("chunk_id") or item.get("content")[:50]
            passages_by_id[cid] = item
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k + rank + 1))

        # Process sparse rankings
        for rank, item in enumerate(sparse_results):
            cid = item.get("chunk_id") or item.get("content")[:50]
            if cid not in passages_by_id:
                passages_by_id[cid] = item
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k + rank + 1))

        # Sort by combined RRF score
        sorted_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)

        merged = []
        for cid in sorted_cids:
            passage = passages_by_id[cid].copy()
            passage["score"] = round(rrf_scores[cid], 5)
            passage["retrieval_method"] = "hybrid_rrf"
            merged.append(passage)

        return merged

    def deduplicate_passages(
        self,
        passages: List[Dict[str, Any]],
        jaccard_threshold: float = 0.75
    ) -> List[Dict[str, Any]]:
        """Filter out redundant or near-duplicate passages."""
        unique_passages = []
        seen_token_sets = []

        for p in passages:
            tokens = set(self.tokenize_text(p["content"]))
            if not tokens:
                continue

            is_duplicate = False
            for seen_set in seen_token_sets:
                intersection = len(tokens.intersection(seen_set))
                union = len(tokens.union(seen_set))
                similarity = intersection / union if union > 0 else 0
                if similarity >= jaccard_threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_passages.append(p)
                seen_token_sets.append(tokens)

        return unique_passages

    def hybrid_retrieve(
        self,
        query: str,
        project_id: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = 10,
        use_hybrid: bool = True
    ) -> List[Dict[str, Any]]:
        """Full hybrid retrieval pipeline with deduplication and metadata retention."""
        dense_hits = self.dense_search(
            query=query,
            project_id=project_id,
            document_ids=document_ids,
            limit=top_k * 2
        )

        if not use_hybrid:
            return self.deduplicate_passages(dense_hits)[:top_k]

        sparse_hits = self.sparse_search(
            query=query,
            project_id=project_id,
            document_ids=document_ids,
            limit=top_k * 2
        )

        fused = self.reciprocal_rank_fusion(dense_hits, sparse_hits)
        deduped = self.deduplicate_passages(fused)
        return deduped[:top_k]
