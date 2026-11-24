"""Knowledge Graph visualization API endpoint."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.document import Document
from app.models.claim import ExtractedClaim
from app.models.contradiction import ContradictionItem
from app.schemas.graph import KnowledgeGraphResponse
from app.services.graph_builder import KnowledgeGraphService

router = APIRouter(prefix="/graph", tags=["Knowledge Graph"])

@router.get("/project/{project_id}", response_model=KnowledgeGraphResponse)
def get_project_knowledge_graph(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate interactive React Flow graph representing documents, claims, concepts, and relationships.
    """
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    docs = db.query(Document).filter(Document.project_id == project_id).all()
    claims = db.query(ExtractedClaim).filter(ExtractedClaim.project_id == project_id).all()
    contras = db.query(ContradictionItem).filter(ContradictionItem.project_id == project_id).all()

    doc_data = [
        {"id": d.id, "filename": d.filename, "file_type": d.file_type, "page_count": d.page_count, "chunk_count": d.chunk_count}
        for d in docs
    ]
    claim_data = [
        {
            "id": c.id,
            "document_id": c.document_id,
            "claim_text": c.claim_text,
            "classification": c.classification.value if hasattr(c.classification, 'value') else str(c.classification),
            "confidence": c.confidence,
            "keywords": c.keywords or [],
            "page_number": c.page_number,
            "supporting_passage": c.supporting_passage
        }
        for c in claims
    ]
    contra_data = [
        {
            "id": ct.id,
            "claim_a_id": ct.claim_a_id,
            "claim_b_id": ct.claim_b_id,
            "contradiction_type": ct.contradiction_type.value if hasattr(ct.contradiction_type, 'value') else str(ct.contradiction_type),
            "explanation": ct.explanation
        }
        for ct in contras
    ]

    graph_service = KnowledgeGraphService()
    rf_graph = graph_service.build_project_graph(doc_data, claim_data, contra_data)
    return KnowledgeGraphResponse(**rf_graph)
