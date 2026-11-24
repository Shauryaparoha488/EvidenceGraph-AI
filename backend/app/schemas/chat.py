"""Grounded Chat and Citation schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class Citation(BaseModel):
    citation_id: int  # [1], [2], etc.
    document_id: str
    document_name: str
    page_number: Optional[int] = None
    chunk_id: Optional[str] = None
    exact_passage: str

class StructuredAnswer(BaseModel):
    direct_answer: str
    key_findings: List[str]
    supporting_evidence: List[Dict[str, Any]]
    contradictory_evidence: List[Dict[str, Any]]
    limitations: List[str]
    evidence_sufficiency: str  # "SUFFICIENT", "PARTIALLY_SUFFICIENT", "INSUFFICIENT"
    unanswered_aspects: List[str]

class ChatRequest(BaseModel):
    project_id: str
    message: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    structured_answer: Optional[StructuredAnswer] = None
    citations: Optional[List[Citation]] = []
    sufficiency_assessment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: str
    project_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True
