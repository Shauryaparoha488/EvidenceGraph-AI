"""Claim and Contradiction schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.claim import EvidenceClassification
from app.models.contradiction import ContradictionType

class ClaimResponse(BaseModel):
    id: str
    project_id: str
    document_id: str
    document_name: Optional[str] = None
    chunk_id: Optional[str] = None
    claim_text: str
    page_number: Optional[int] = None
    supporting_passage: str
    classification: EvidenceClassification
    confidence: float
    keywords: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True

class ContradictionResponse(BaseModel):
    id: str
    project_id: str
    claim_a_id: str
    claim_b_id: str
    claim_a: Optional[ClaimResponse] = None
    claim_b: Optional[ClaimResponse] = None
    contradiction_type: ContradictionType
    explanation: str
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True
