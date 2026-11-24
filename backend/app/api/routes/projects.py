"""Projects / Research Workspaces routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.document import Document
from app.models.claim import ExtractedClaim
from app.models.contradiction import ContradictionItem
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all projects owned by the current user."""
    projects = db.query(Project).filter(Project.user_id == current_user.id).order_by(Project.created_at.desc()).all()
    
    result = []
    for p in projects:
        doc_count = db.query(func.count(Document.id)).filter(Document.project_id == p.id).scalar() or 0
        claim_count = db.query(func.count(ExtractedClaim.id)).filter(ExtractedClaim.project_id == p.id).scalar() or 0
        contra_count = db.query(func.count(ContradictionItem.id)).filter(ContradictionItem.project_id == p.id).scalar() or 0

        p_resp = ProjectResponse.model_validate(p)
        p_resp.document_count = doc_count
        p_resp.claim_count = claim_count
        p_resp.contradiction_count = contra_count
        result.append(p_resp)
    return result

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new research workspace/project."""
    project = Project(
        user_id=current_user.id,
        title=project_in.title,
        description=project_in.description
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectResponse.model_validate(project)

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get project details."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    doc_count = db.query(func.count(Document.id)).filter(Document.project_id == project.id).scalar() or 0
    claim_count = db.query(func.count(ExtractedClaim.id)).filter(ExtractedClaim.project_id == project.id).scalar() or 0
    contra_count = db.query(func.count(ContradictionItem.id)).filter(ContradictionItem.project_id == project.id).scalar() or 0

    p_resp = ProjectResponse.model_validate(project)
    p_resp.document_count = doc_count
    p_resp.claim_count = claim_count
    p_resp.contradiction_count = contra_count
    return p_resp

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update project title or description."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    if project_in.title is not None:
        project.title = project_in.title
    if project_in.description is not None:
        project.description = project_in.description

    db.commit()
    db.refresh(project)
    return ProjectResponse.model_validate(project)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete project and all associated documents, vectors, claims, and graphs."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    db.delete(project)
    db.commit()
    return None
