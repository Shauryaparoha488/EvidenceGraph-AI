"""Document Chunk model storing passage metadata."""
import uuid
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=True)  # 1-indexed page
    section = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    qdrant_point_id = Column(String(64), nullable=True, index=True)

    # Relationships
    document = relationship("Document", back_populates="chunks")
    claims = relationship("ExtractedClaim", back_populates="chunk", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_doc_chunk_order", "document_id", "chunk_index"),
    )
