"""Extracted Claim model representing discrete verifiable facts."""
import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Float, Enum, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class EvidenceClassification(str, enum.Enum):
    SUPPORTING = "SUPPORTING"
    CONTRADICTING = "CONTRADICTING"
    NEUTRAL = "NEUTRAL"
    INSUFFICIENT = "INSUFFICIENT"

class ExtractedClaim(Base):
    __tablename__ = "extracted_claims"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id = Column(String(36), ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True, index=True)
    
    claim_text = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    supporting_passage = Column(Text, nullable=False)
    classification = Column(Enum(EvidenceClassification), default=EvidenceClassification.NEUTRAL, index=True)
    confidence = Column(Float, default=1.0)
    keywords = Column(JSON, default=list)  # Associated concepts / entities
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    project = relationship("Project", back_populates="claims")
    document = relationship("Document", back_populates="claims")
    chunk = relationship("DocumentChunk", back_populates="claims")
