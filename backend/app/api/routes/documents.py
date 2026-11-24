"""Document routes for upload, processing pipeline, listing, and deletion."""
import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db, SessionLocal
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.document import Document, ProcessingStatus
from app.models.chunk import DocumentChunk
from app.models.claim import ExtractedClaim
from app.models.contradiction import ContradictionItem
from app.schemas.document import DocumentResponse, DocumentDetailResponse
from app.services.document_processor import DocumentProcessor
from app.services.chunking import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.claim_extractor import ClaimExtractor
from app.services.contradiction_detector import ContradictionDetector

router = APIRouter(prefix="/documents", tags=["Documents"])

def process_document_background(document_id: str):
    """Asynchronous background task processing uploaded file end-to-end."""
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return

        doc.status = ProcessingStatus.PROCESSING
        db.commit()

        # 1. Extract content page-by-page
        pages = DocumentProcessor.process_file(doc.storage_path)
        doc.page_count = len(pages)

        if not pages:
            doc.status = ProcessingStatus.FAILED
            doc.error_message = "No readable text content extracted from document."
            db.commit()
            return

        # 2. Semantic Chunking
        chunker = ChunkingService(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
        raw_chunks = chunker.chunk_document_pages(pages)
        doc.chunk_count = len(raw_chunks)

        # 3. Store Chunks in DB
        db_chunks = []
        for rc in raw_chunks:
            chunk = DocumentChunk(
                document_id=doc.id,
                chunk_index=rc["chunk_index"],
                page_number=rc["page_number"],
                section=rc["section"],
                content=rc["content"],
                token_count=rc["token_count"]
            )
            db.add(chunk)
            db_chunks.append(chunk)
        db.commit()
        for c in db_chunks:
            db.refresh(c)

        # 4. Generate Embeddings & Index in Qdrant
        embedder = EmbeddingService.get_instance()
        texts = [c.content for c in db_chunks]
        embeddings = embedder.embed_texts(texts)

        vector_store = VectorStore.get_instance()
        point_payloads = [
            {
                "id": c.id,
                "document_id": doc.id,
                "document_name": doc.filename,
                "project_id": doc.project_id,
                "page_number": c.page_number,
                "section": c.section,
                "content": c.content,
                "chunk_index": c.chunk_index
            }
            for c in db_chunks
        ]
        point_ids = vector_store.upsert_chunks(point_payloads, embeddings)

        for c, pid in zip(db_chunks, point_ids):
            c.qdrant_point_id = pid
        db.commit()

        # 5. Extract Initial Claims & Detect Contradictions
        claim_extractor = ClaimExtractor()
        extracted_db_claims = []
        for c in db_chunks[:6]:  # Extract core claims from initial key passages
            claims = claim_extractor.extract_claims_from_passage(
                passage=c.content,
                document_name=doc.filename,
                page_number=c.page_number
            )
            for item in claims:
                db_claim = ExtractedClaim(
                    project_id=doc.project_id,
                    document_id=doc.id,
                    chunk_id=c.id,
                    claim_text=item["claim_text"],
                    page_number=item.get("page_number", c.page_number),
                    supporting_passage=item.get("supporting_passage", c.content),
                    classification=item.get("classification", "NEUTRAL"),
                    confidence=item.get("confidence", 0.9),
                    keywords=item.get("keywords", [])
                )
                db.add(db_claim)
                extracted_db_claims.append(db_claim)
        db.commit()

        # 6. Check for Contradictions with existing project claims
        existing_claims = (
            db.query(ExtractedClaim)
            .filter(ExtractedClaim.project_id == doc.project_id, ExtractedClaim.document_id != doc.id)
            .all()
        )
        if existing_claims and extracted_db_claims:
            detector = ContradictionDetector()
            for new_c in extracted_db_claims:
                for old_c in existing_claims[:15]:
                    conflict = detector.analyze_claim_pair(
                        {"id": new_c.id, "claim_text": new_c.claim_text, "supporting_passage": new_c.supporting_passage, "document_name": doc.filename, "page_number": new_c.page_number},
                        {"id": old_c.id, "claim_text": old_c.claim_text, "supporting_passage": old_c.supporting_passage, "document_name": old_c.document.filename if old_c.document else "Doc", "page_number": old_c.page_number}
                    )
                    if conflict:
                        contra_item = ContradictionItem(
                            project_id=doc.project_id,
                            claim_a_id=new_c.id,
                            claim_b_id=old_c.id,
                            contradiction_type=conflict.get("contradiction_type", "DIRECT"),
                            explanation=conflict.get("explanation", ""),
                            confidence=conflict.get("confidence", 0.85)
                        )
                        db.add(contra_item)
            db.commit()

        doc.status = ProcessingStatus.COMPLETED
        db.commit()

    except Exception as e:
        print(f"[DocumentProcessingError] {document_id}: {e}")
        db.rollback()
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.status = ProcessingStatus.FAILED
            doc.error_message = str(e)
            db.commit()
    finally:
        db.close()

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    project_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload research document and schedule async ingestion pipeline."""
    # Validate project ownership
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Save to disk
    project_upload_dir = Path(settings.UPLOAD_DIR) / project_id
    project_upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = project_upload_dir / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)
    if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"File exceeds maximum allowed {settings.MAX_FILE_SIZE_MB}MB.")

    # Create document record
    document = Document(
        project_id=project_id,
        filename=file.filename,
        file_type=file_ext.lstrip("."),
        file_size=file_size,
        storage_path=str(file_path),
        status=ProcessingStatus.PENDING
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # Queue background processing
    background_tasks.add_task(process_document_background, document.id)

    return DocumentResponse.model_validate(document)

@router.get("/project/{project_id}", response_model=List[DocumentResponse])
def list_project_documents(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all documents uploaded to a project."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    docs = db.query(Document).filter(Document.project_id == project_id).order_by(Document.created_at.desc()).all()
    return [DocumentResponse.model_validate(d) for d in docs]

@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get document details with its indexed chunks."""
    doc = db.query(Document).join(Project).filter(Document.id == document_id, Project.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    return DocumentDetailResponse.model_validate(doc)

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete document and remove its points from Qdrant vector store."""
    doc = db.query(Document).join(Project).filter(Document.id == document_id, Project.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Remove from Qdrant
    try:
        VectorStore.get_instance().delete_document_points(doc.id)
    except Exception as e:
        print(f"[QdrantDeleteWarning] {e}")

    # Remove file from disk
    if os.path.exists(doc.storage_path):
        try:
            os.remove(doc.storage_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()
    return None

@router.get("/{document_id}/download")
def download_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Serve original document file for in-browser citation reading."""
    doc = db.query(Document).join(Project).filter(Document.id == document_id, Project.user_id == current_user.id).first()
    if not doc or not os.path.exists(doc.storage_path):
        raise HTTPException(status_code=404, detail="Document file not found.")

    return FileResponse(doc.storage_path, filename=doc.filename)
