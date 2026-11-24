"""Research Report schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ReportGenerateRequest(BaseModel):
    project_id: str
    title: Optional[str] = None
    research_question: str = Field(..., min_length=5)

class ReportResponse(BaseModel):
    id: str
    project_id: str
    title: str
    research_question: str
    executive_summary: str
    key_findings: List[str]
    supporting_evidence: List[Dict[str, Any]]
    contradictory_findings: List[Dict[str, Any]]
    limitations: Optional[str] = None
    references: List[Dict[str, Any]]
    conclusion: str
    markdown_content: str
    pdf_download_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
