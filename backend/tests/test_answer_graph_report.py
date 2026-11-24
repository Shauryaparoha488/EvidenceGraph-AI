"""Grounded answer generation, citation validation, knowledge graph, and report export tests."""
import os
import pytest
from app.services.answer_generator import AnswerGenerator
from app.services.graph_builder import KnowledgeGraphService
from app.services.report_generator import ReportGenerator

def test_insufficient_evidence_response():
    generator = AnswerGenerator()
    resp = generator.generate_grounded_answer("What is the quantum spin of hypothetical particle X?", [])
    assert resp["sufficiency_assessment"] == "INSUFFICIENT"
    assert "The available documents do not provide sufficient evidence to answer this question reliably." in resp["content"]
    assert len(resp["citations"]) == 0

def test_grounded_answer_with_citations():
    generator = AnswerGenerator()
    passages = [
        {
            "chunk_id": "ch_1",
            "document_id": "doc_1",
            "document_name": "TransformerConvergence.pdf",
            "page_number": 7,
            "content": "Warmup schedules stabilize learning rates and ensure steady loss convergence."
        }
    ]
    resp = generator.generate_grounded_answer("How does warmup affect convergence?", passages)
    assert len(resp["citations"]) >= 1
    assert resp["citations"][0]["document_name"] == "TransformerConvergence.pdf"
    assert resp["citations"][0]["page_number"] == 7
    assert resp["sufficiency_assessment"] in ["SUFFICIENT", "PARTIALLY_SUFFICIENT"]

def test_knowledge_graph_react_flow_serialization():
    graph_service = KnowledgeGraphService()
    docs = [{"id": "d1", "filename": "Study1.pdf", "file_type": "pdf", "page_count": 5, "chunk_count": 12}]
    claims = [{
        "id": "c1",
        "document_id": "d1",
        "claim_text": "Data augmentation prevents overfitting.",
        "classification": "SUPPORTING",
        "confidence": 0.95,
        "keywords": ["Augmentation", "Overfitting"],
        "page_number": 2,
        "supporting_passage": "Data augmentation prevents overfitting."
    }]
    contras = []

    rf_graph = graph_service.build_project_graph(docs, claims, contras)
    assert "nodes" in rf_graph
    assert "edges" in rf_graph
    assert "stats" in rf_graph
    assert rf_graph["stats"]["documents_count"] == 1
    assert rf_graph["stats"]["claims_count"] == 1
    assert rf_graph["stats"]["concepts_count"] >= 1
    # Check node position and type
    assert "position" in rf_graph["nodes"][0]
    assert rf_graph["nodes"][0]["type"] == "customNode"

def test_report_generator_markdown_and_pdf():
    report_data = {
        "title": "Learning Dynamics Investigation",
        "research_question": "Does learning rate warmup improve stability?",
        "executive_summary": "Synthesized evidence indicates warmup prevents gradient explosion.",
        "key_findings": ["Warmup stabilizes early iterations.", "Decay schedules improve final accuracy."],
        "supporting_evidence": [
            {"document_name": "Dynamics.pdf", "page_number": 3, "claim": "Warmup prevents divergence."}
        ],
        "contradictory_findings": [],
        "limitations": "Tested only on vision and text benchmarks.",
        "references": [
            {"citation_id": 1, "document_name": "Dynamics.pdf", "page_number": 3, "exact_passage": "Warmup prevents divergence."}
        ],
        "conclusion": "Warmup is recommended across deep architectures."
    }

    # Markdown export test
    md = ReportGenerator.generate_markdown(report_data)
    assert "# EvidenceGraph AI Research Report" in md
    assert "1. Executive Summary" in md
    assert "Does learning rate warmup improve stability?" in md

    # PDF export test
    pdf_path = ReportGenerator.generate_pdf(report_data, "test_output_report.pdf")
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000  # Non-empty valid PDF
