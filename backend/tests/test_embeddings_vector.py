"""Embeddings and Vector storage tests."""
import pytest
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore

def test_embedding_generation():
    embedder = EmbeddingService.get_instance()
    texts = [
        "Increasing learning rate accelerates convergence in small neural networks.",
        "High learning rates cause gradient explosion in deep Transformers."
    ]
    embs = embedder.embed_texts(texts)
    assert len(embs) == 2
    assert len(embs[0]) == 384
    assert len(embs[1]) == 384

def test_vector_store_upsert_and_retrieval():
    vstore = VectorStore.get_instance()
    embedder = EmbeddingService.get_instance()

    test_chunk = {
        "id": "test_chunk_999",
        "document_id": "test_doc_999",
        "document_name": "TestPaper.pdf",
        "project_id": "test_proj_999",
        "page_number": 4,
        "section": "Results",
        "content": "Empirical testing reveals that batch normalization improves stability across all learning rates.",
        "chunk_index": 0
    }
    embedding = embedder.embed_texts([test_chunk["content"]])
    point_ids = vstore.upsert_chunks([test_chunk], embedding)
    assert len(point_ids) == 1

    # Search with matching query
    query_vec = embedder.embed_query("batch normalization stability")
    results = vstore.search(query_vec, project_id="test_proj_999", limit=5)
    assert len(results) >= 1
    top = results[0]
    assert top["document_name"] == "TestPaper.pdf"
    assert "batch normalization" in top["content"]
    assert top["score"] > 0.4

    # Search with wrong project ID ensures tenant isolation
    isolated_results = vstore.search(query_vec, project_id="wrong_proj_id", limit=5)
    assert len(isolated_results) == 0

    # Cleanup
    vstore.delete_document_points("test_doc_999")
