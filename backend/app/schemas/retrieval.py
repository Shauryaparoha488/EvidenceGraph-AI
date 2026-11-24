"""Retrieval and Search schemas."""
from typing import Optional, List
from pydantic import BaseModel, Field

class SearchQuery(BaseModel):
    project_id: str
    query: str = Field(..., min_length=2)
    top_k: int = 10
    document_ids: Optional[List[str]] = None
    use_hybrid: bool = True
    use_rerank: bool = True

class RetrievedPassage(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    content: str
    score: float
    retrieval_method: str = "hybrid"  # "dense", "sparse", "hybrid", "reranked"

class SearchResponse(BaseModel):
    query: str
    passages: List[RetrievedPassage]
    total_found: int
