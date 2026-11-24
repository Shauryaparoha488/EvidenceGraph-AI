"""Research Report database model."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class ResearchReport(Base):
    __tablename__ = "research_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    research_question = Column(Text, nullable=False)
    executive_summary = Column(Text, nullable=False)
    key_findings = Column(JSON, nullable=False)  # List of strings/objects
    supporting_evidence = Column(JSON, nullable=False)  # List of claims with citations
    contradictory_findings = Column(JSON, nullable=False)  # List of conflicts
    limitations = Column(Text, nullable=True)
    references = Column(JSON, nullable=False)  # Traceable sources
    conclusion = Column(Text, nullable=False)
    markdown_content = Column(Text, nullable=False)
    pdf_path = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    project = relationship("Project", back_populates="reports")
