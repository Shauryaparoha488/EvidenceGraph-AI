"""Hybrid retrieval and passage deduplication tests."""
import pytest
from app.services.retrieval_service import RetrievalService
from app.core.database import SessionLocal, init_db

def setup_module():
    init_db()

def test_reciprocal_rank_fusion_and_deduplication():
    db = SessionLocal()
    try:
        retrieval = RetrievalService(db)

        dense = [
            {"chunk_id": "c1", "content": "Evidence grounded AI is traceable.", "score": 0.95},
            {"chunk_id": "c2", "content": "Knowledge graphs connect concepts.", "score": 0.85}
        ]
        sparse = [
            {"chunk_id": "c2", "content": "Knowledge graphs connect concepts.", "score": 4.5},
            {"chunk_id": "c3", "content": "Citations map to exact pages.", "score": 3.2}
        ]

        fused = retrieval.reciprocal_rank_fusion(dense, sparse)
        assert len(fused) == 3
        # c2 appears in both, so it should rank highest
        assert fused[0]["chunk_id"] == "c2"

        # Deduplication test with near duplicate passages
        duplicates = [
            {"chunk_id": "d1", "content": "Evidence grounded AI is traceable and reliable for research."},
            {"chunk_id": "d2", "content": "Evidence grounded AI is traceable and reliable for research."}
        ]
        deduped = retrieval.deduplicate_passages(duplicates)
        assert len(deduped) == 1
    finally:
        db.close()
