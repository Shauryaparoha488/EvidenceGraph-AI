"""Claims and Contradiction endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.document import Document
from app.models.claim import ExtractedClaim, EvidenceClassification
from app.models.contradiction import ContradictionItem
from app.schemas.claim import ClaimResponse, ContradictionResponse

router = APIRouter(prefix="/claims", tags=["Claims & Evidence"])

@router.get("/project/{project_id}", response_model=List[ClaimResponse])
def list_project_claims(
    project_id: str,
    classification: Optional[EvidenceClassification] = None,
    document_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List extracted claims for a project with optional filters."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    query = db.query(ExtractedClaim).filter(ExtractedClaim.project_id == project_id)
    if classification:
        query = query.filter(ExtractedClaim.classification == classification)
    if document_id:
        query = query.filter(ExtractedClaim.document_id == document_id)

    claims = query.order_by(ExtractedClaim.created_at.desc()).all()
    
    result = []
    for c in claims:
        cr = ClaimResponse.model_validate(c)
        cr.document_name = c.document.filename if c.document else "Unknown"
        result.append(cr)
    return result

@router.get("/contradictions/{project_id}", response_model=List[ContradictionResponse])
def list_project_contradictions(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List detected contradictions and conflicting evidence pairs."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    contras = db.query(ContradictionItem).filter(ContradictionItem.project_id == project_id).all()
    
    result = []
    for ct in contras:
        cr_item = ContradictionResponse.model_validate(ct)
        if ct.claim_a:
            cr_item.claim_a = ClaimResponse.model_validate(ct.claim_a)
            cr_item.claim_a.document_name = ct.claim_a.document.filename if ct.claim_a.document else "Doc A"
        if ct.claim_b:
            cr_item.claim_b = ClaimResponse.model_validate(ct.claim_b)
            cr_item.claim_b.document_name = ct.claim_b.document.filename if ct.claim_b.document else "Doc B"
        result.append(cr_item)
    return result
