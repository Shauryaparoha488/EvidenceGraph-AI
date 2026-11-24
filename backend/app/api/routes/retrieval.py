"""Retrieval endpoints for hybrid search."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.schemas.retrieval import SearchQuery, SearchResponse, RetrievedPassage
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/retrieval", tags=["Retrieval"])

@router.post("/search", response_model=SearchResponse)
def search_passages(
    query_in: SearchQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute hybrid dense + sparse retrieval across project documents."""
    project = db.query(Project).filter(Project.id == query_in.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    retrieval_service = RetrievalService(db)
    passages = retrieval_service.hybrid_retrieve(
        query=query_in.query,
        project_id=query_in.project_id,
        document_ids=query_in.document_ids,
        top_k=query_in.top_k,
        use_hybrid=query_in.use_hybrid
    )

    formatted_passages = [
        RetrievedPassage(
            chunk_id=p.get("chunk_id", ""),
            document_id=p.get("document_id", ""),
            document_name=p.get("document_name", "Document"),
            page_number=p.get("page_number"),
            section=p.get("section"),
            content=p.get("content", ""),
            score=p.get("score", 0.0),
            retrieval_method=p.get("retrieval_method", "hybrid")
        )
        for p in passages
    ]

    return SearchResponse(
        query=query_in.query,
        passages=formatted_passages,
        total_found=len(formatted_passages)
    )
