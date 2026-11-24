"""End-to-End integration test covering the complete user workflow."""
import os
import tempfile
import pytest
from app.core.database import SessionLocal, init_db
from app.core.security import hash_password, create_access_token
from app.models.user import User
from app.models.project import Project
from app.models.document import Document, ProcessingStatus
from app.models.chunk import DocumentChunk
from app.models.claim import ExtractedClaim
from app.models.contradiction import ContradictionItem
from app.services.chunking import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.agents.research_agent import ResearchAgent
from app.services.graph_builder import KnowledgeGraphService
from app.services.report_generator import ReportGenerator

def setup_module():
    init_db()

def test_complete_e2e_research_lifecycle():
    """
    Simulates:
    1. User Creation & Project Workspace Initialization
    2. Multi-document chunking and vector indexing
    3. Claim extraction and contradiction detection
    4. Grounded research assistant query with verified citations
    5. Interactive Knowledge Graph export
    6. PDF Research Report generation
    """
    db = SessionLocal()
    try:
        # Step 1: User & Project
        user = User(email="e2e_researcher@evidencegraph.ai", hashed_password=hash_password("SecurePass123!"), full_name="E2E Scientist")
        db.add(user)
        db.commit()
        db.refresh(user)

        project = Project(user_id=user.id, title="Neural Scaling Laws Study", description="Comprehensive evaluation of model scaling.")
        db.add(project)
        db.commit()
        db.refresh(project)

        # Step 2: Ingest Two Comparative Documents
        doc_a = Document(
            project_id=project.id,
            filename="Scaling_Hypothesis_2023.pdf",
            file_type="pdf",
            file_size=102400,
            storage_path="dummy_path_a.pdf",
            page_count=12,
            chunk_count=2,
            status=ProcessingStatus.COMPLETED
        )
        doc_b = Document(
            project_id=project.id,
            filename="Limits_Of_Scaling_2024.pdf",
            file_type="pdf",
            file_size=104800,
            storage_path="dummy_path_b.pdf",
            page_count=15,
            chunk_count=2,
            status=ProcessingStatus.COMPLETED
        )
        db.add_all([doc_a, doc_b])
        db.commit()
        db.refresh(doc_a)
        db.refresh(doc_b)

        # Step 3: Add Chunks & Embeddings in Qdrant
        chunk_a1 = DocumentChunk(
            document_id=doc_a.id,
            chunk_index=0,
            page_number=3,
            section="Findings",
            content="Experiments demonstrate that increasing parameter count consistently improves downstream reasoning performance on benchmarks.",
            token_count=16
        )
        chunk_b1 = DocumentChunk(
            document_id=doc_b.id,
            chunk_index=0,
            page_number=8,
            section="Limitations",
            content="Empirical audits reveal that parameter scaling fails to improve reasoning when synthetic data contamination is eliminated.",
            token_count=16
        )
        db.add_all([chunk_a1, chunk_b1])
        db.commit()
        db.refresh(chunk_a1)
        db.refresh(chunk_b1)

        embedder = EmbeddingService.get_instance()
        vstore = VectorStore.get_instance()

        embs = embedder.embed_texts([chunk_a1.content, chunk_b1.content])
        vstore.upsert_chunks(
            [
                {"id": chunk_a1.id, "document_id": doc_a.id, "document_name": doc_a.filename, "project_id": project.id, "page_number": 3, "section": "Findings", "content": chunk_a1.content, "chunk_index": 0},
                {"id": chunk_b1.id, "document_id": doc_b.id, "document_name": doc_b.filename, "project_id": project.id, "page_number": 8, "section": "Limitations", "content": chunk_b1.content, "chunk_index": 0}
            ],
            embs
        )

        # Step 4: Add Claims & Detect Disagreement
        claim_a = ExtractedClaim(
            project_id=project.id,
            document_id=doc_a.id,
            chunk_id=chunk_a1.id,
            claim_text="Parameter scaling consistently improves reasoning performance.",
            supporting_passage=chunk_a1.content,
            classification="SUPPORTING",
            confidence=0.95,
            keywords=["Scaling", "Reasoning", "Parameters"],
            page_number=3
        )
        claim_b = ExtractedClaim(
            project_id=project.id,
            document_id=doc_b.id,
            chunk_id=chunk_b1.id,
            claim_text="Parameter scaling fails to improve reasoning without contaminated data.",
            supporting_passage=chunk_b1.content,
            classification="CONTRADICTING",
            confidence=0.92,
            keywords=["Scaling", "Reasoning", "Contamination"],
            page_number=8
        )
        db.add_all([claim_a, claim_b])
        db.commit()
        db.refresh(claim_a)
        db.refresh(claim_b)

        contra = ContradictionItem(
            project_id=project.id,
            claim_a_id=claim_a.id,
            claim_b_id=claim_b.id,
            contradiction_type="DIRECT",
            explanation="Scaling_Hypothesis claims scaling improves reasoning, whereas Limits_Of_Scaling shows failure when benchmark contamination is removed.",
            confidence=0.90
        )
        db.add(contra)
        db.commit()

        # Step 5: Research Agent Execution
        agent = ResearchAgent(db)
        query = "Does parameter scaling guarantee better reasoning?"
        result = agent.execute_research_workflow(query=query, project_id=project.id, top_k=5)

        assert result is not None
        assert "content" in result
        assert len(result.get("citations", [])) >= 1
        # Validate citation references real document
        first_cite = result["citations"][0]
        assert first_cite["document_name"] in [doc_a.filename, doc_b.filename]
        assert first_cite["page_number"] in [3, 8]

        # Step 6: Interactive Knowledge Graph Construction
        graph_service = KnowledgeGraphService()
        kg = graph_service.build_project_graph(
            documents=[{"id": doc_a.id, "filename": doc_a.filename}, {"id": doc_b.id, "filename": doc_b.filename}],
            claims=[
                {"id": claim_a.id, "document_id": doc_a.id, "claim_text": claim_a.claim_text, "classification": "SUPPORTING", "keywords": ["Scaling", "Reasoning"]},
                {"id": claim_b.id, "document_id": doc_b.id, "claim_text": claim_b.claim_text, "classification": "CONTRADICTING", "keywords": ["Scaling", "Reasoning"]}
            ],
            contradictions=[{"id": contra.id, "claim_a_id": claim_a.id, "claim_b_id": claim_b.id, "contradiction_type": "DIRECT", "explanation": contra.explanation}]
        )
        assert kg["stats"]["documents_count"] == 2
        assert kg["stats"]["claims_count"] == 2
        # Contradiction edge exists
        contra_edge = next((e for e in kg["edges"] if e["label"] == "CONTRADICTS"), None)
        assert contra_edge is not None
        assert contra_edge["style"]["stroke"] == "#ef4444"

        # Step 7: Research Report Generation & PDF Output
        report_data = {
            "title": "Scaling Law Reasoning Synthesis",
            "research_question": query,
            "executive_summary": result["content"],
            "key_findings": ["Paper A finds reasoning gains.", "Paper B disputes gains due to data contamination."],
            "supporting_evidence": [{"document_name": doc_a.filename, "page_number": 3, "claim": claim_a.claim_text}],
            "contradictory_findings": [{"type": "DIRECT", "explanation": contra.explanation}],
            "limitations": "Limited to benchmark evaluations.",
            "references": result["citations"],
            "conclusion": "Scaling alone is insufficient for verifiable reasoning without data purity."
        }
        pdf_path = ReportGenerator.generate_pdf(report_data, "e2e_scaling_report.pdf")
        assert os.path.exists(pdf_path)

        # Cleanup test entities
        vstore.delete_document_points(doc_a.id)
        vstore.delete_document_points(doc_b.id)
        db.delete(contra)
        db.delete(claim_a)
        db.delete(claim_b)
        db.delete(chunk_a1)
        db.delete(chunk_b1)
        db.delete(doc_a)
        db.delete(doc_b)
        db.delete(project)
        db.delete(user)
        db.commit()

    finally:
        db.close()
