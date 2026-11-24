"""Project and Workspace schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    document_count: Optional[int] = 0
    claim_count: Optional[int] = 0
    contradiction_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
