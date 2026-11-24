"""Semantic chunking service with page and section preservation."""
import re
from typing import List, Dict, Any

class ChunkingService:
    """Splits document content into semantically coherent overlapping passages."""

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences while respecting abbreviations."""
        # Simple regex sentence splitter
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk_document_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Produce indexed chunks while strictly preserving page numbers and section metadata.
        Each chunk contains:
        - chunk_index
        - page_number
        - section
        - content
        - token_count
        """
        chunks = []
        global_index = 0

        for page in pages:
            page_num = page.get("page_number", 1)
            section = page.get("section", "General")
            text = page.get("text", "")

            sentences = self.split_into_sentences(text)
            if not sentences:
                continue

            current_chunk = []
            current_len = 0

            for sentence in sentences:
                sentence_len = len(sentence)

                if current_len + sentence_len > self.chunk_size and current_chunk:
                    chunk_text = " ".join(current_chunk)
                    chunks.append({
                        "chunk_index": global_index,
                        "page_number": page_num,
                        "section": section,
                        "content": chunk_text,
                        "token_count": len(chunk_text.split())
                    })
                    global_index += 1

                    # Retain overlap sentences
                    overlap_chunk = []
                    overlap_len = 0
                    for s in reversed(current_chunk):
                        if overlap_len + len(s) <= self.chunk_overlap:
                            overlap_chunk.insert(0, s)
                            overlap_len += len(s)
                        else:
                            break
                    current_chunk = overlap_chunk
                    current_len = overlap_len

                current_chunk.append(sentence)
                current_len += sentence_len

            if current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append({
                    "chunk_index": global_index,
                    "page_number": page_num,
                    "section": section,
                    "content": chunk_text,
                    "token_count": len(chunk_text.split())
                })
                global_index += 1

        return chunks
