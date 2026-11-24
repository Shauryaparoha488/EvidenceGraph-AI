"""Contradiction Item model storing detected conflicts between claims."""
import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base

class ContradictionType(str, enum.Enum):
    DIRECT = "DIRECT"
    CONTEXT_DEPENDENT = "CONTEXT_DEPENDENT"
    EXPERIMENTAL_DIFFERENCE = "EXPERIMENTAL_DIFFERENCE"
    COMPATIBLE_NUANCE = "COMPATIBLE_NUANCE"
    UNRESOLVED = "UNRESOLVED"

class ContradictionItem(Base):
    __tablename__ = "contradictions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_a_id = Column(String(36), ForeignKey("extracted_claims.id", ondelete="CASCADE"), nullable=False)
    claim_b_id = Column(String(36), ForeignKey("extracted_claims.id", ondelete="CASCADE"), nullable=False)
    
    contradiction_type = Column(Enum(ContradictionType), default=ContradictionType.DIRECT, index=True)
    explanation = Column(Text, nullable=False)
    confidence = Column(Float, default=0.85)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    project = relationship("Project", back_populates="contradictions")
    claim_a = relationship("ExtractedClaim", foreign_keys=[claim_a_id])
    claim_b = relationship("ExtractedClaim", foreign_keys=[claim_b_id])
