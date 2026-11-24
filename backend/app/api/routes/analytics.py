"""Analytics and Dashboard summary metrics."""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.document import Document
from app.models.claim import ExtractedClaim
from app.models.contradiction import ContradictionItem

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary")
def get_user_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Provide high-level dashboard metrics for the authenticated user."""
    # User's projects
    user_projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    project_ids = [p.id for p in user_projects]

    if not project_ids:
        return {
            "total_projects": 0,
            "total_documents": 0,
            "total_chunks": 0,
            "total_claims": 0,
            "total_contradictions": 0,
            "recent_projects": []
        }

    total_docs = db.query(func.count(Document.id)).filter(Document.project_id.in_(project_ids)).scalar() or 0
    total_claims = db.query(func.count(ExtractedClaim.id)).filter(ExtractedClaim.project_id.in_(project_ids)).scalar() or 0
    total_contradictions = db.query(func.count(ContradictionItem.id)).filter(ContradictionItem.project_id.in_(project_ids)).scalar() or 0

    recent_projects_data = []
    for p in user_projects[:5]:
        d_cnt = db.query(func.count(Document.id)).filter(Document.project_id == p.id).scalar() or 0
        c_cnt = db.query(func.count(ExtractedClaim.id)).filter(ExtractedClaim.project_id == p.id).scalar() or 0
        recent_projects_data.append({
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "document_count": d_cnt,
            "claim_count": c_cnt,
            "created_at": p.created_at
        })

    return {
        "total_projects": len(user_projects),
        "total_documents": total_docs,
        "total_claims": total_claims,
        "total_contradictions": total_contradictions,
        "recent_projects": recent_projects_data
    }
