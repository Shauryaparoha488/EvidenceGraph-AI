"""Document processing and semantic chunking tests."""
import os
import tempfile
import pytest
from app.services.document_processor import DocumentProcessor
from app.services.chunking import ChunkingService

def test_clean_text_normalization():
    dirty = "This is  an  experi-\nmental result\n\n\n\nwith multiple lines\tand tabs."
    cleaned = DocumentProcessor.clean_text(dirty)
    assert "experimental result" in cleaned
    assert "\n\n\n" not in cleaned
    assert "\t" not in cleaned

def test_markdown_and_text_extraction():
    sample_md = """# Introduction
EvidenceGraph AI is designed to eliminate LLM hallucinations.
Factual statements are backed by real citations.

# Methodology
We combine dense vector search with sparse BM25 retrieval.
The reciprocal rank fusion algorithm merges results.
"""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(sample_md)
        temp_path = f.name

    try:
        sections = DocumentProcessor.extract_text_or_markdown(temp_path)
        assert len(sections) >= 2
        assert sections[0]["section"] == "Introduction"
        assert "hallucinations" in sections[0]["text"]
        assert sections[1]["section"] == "Methodology"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_semantic_chunking_with_overlap():
    pages = [
        {
            "page_number": 1,
            "section": "Experiments",
            "text": "Sentence one is about neural architecture. Sentence two discusses learning rate dynamics. Sentence three explores weight decay and regularization techniques. Sentence four evaluates model convergence."
        }
    ]
    chunker = ChunkingService(chunk_size=120, chunk_overlap=40)
    chunks = chunker.chunk_document_pages(pages)
    assert len(chunks) >= 1
    for c in chunks:
        assert c["page_number"] == 1
        assert c["section"] == "Experiments"
        assert len(c["content"]) > 0
        assert c["token_count"] > 0

def test_unsupported_file_format():
    with pytest.raises(ValueError, match="Unsupported file format"):
        DocumentProcessor.process_file("malformed_document.xyz")
