"""Document and Chunk schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.document import ProcessingStatus

class DocumentChunkResponse(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    page_number: Optional[int] = None
    section: Optional[str] = None
    content: str
    token_count: int

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: str
    project_id: str
    filename: str
    file_type: str
    file_size: int
    page_count: int
    chunk_count: int
    status: ProcessingStatus
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentDetailResponse(DocumentResponse):
    chunks: Optional[List[DocumentChunkResponse]] = []
