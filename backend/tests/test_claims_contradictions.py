"""Claim extraction and contradiction analysis tests."""
import pytest
from app.services.claim_extractor import ClaimExtractor
from app.services.contradiction_detector import ContradictionDetector

def test_claim_extraction_from_passage():
    extractor = ClaimExtractor()
    passage = "Our experiments demonstrate that increasing the learning rate improves training speed by 35% on CIFAR-10."
    claims = extractor.extract_claims_from_passage(passage, document_name="PaperA.pdf", page_number=3)
    assert len(claims) >= 1
    top_claim = claims[0]
    assert top_claim["document_name"] == "PaperA.pdf"
    assert top_claim["page_number"] == 3
    assert top_claim["classification"] == "SUPPORTING"
    assert len(top_claim["keywords"]) > 0

def test_contradiction_detection_between_conflicting_claims():
    detector = ContradictionDetector()
    claim_a = {
        "id": "c_a",
        "document_name": "Author2023.pdf",
        "page_number": 5,
        "claim_text": "Increasing learning rate accelerates convergence in convolutional networks.",
        "supporting_passage": "Experiments confirm higher learning rates improve convergence speed."
    }
    claim_b = {
        "id": "c_b",
        "document_name": "Author2024.pdf",
        "page_number": 12,
        "claim_text": "Increasing learning rate degrades model convergence and induces numerical instability.",
        "supporting_passage": "Higher learning rates consistently degrade convergence under deep layers."
    }

    conflict = detector.analyze_claim_pair(claim_a, claim_b)
    assert conflict is not None
    assert conflict["claim_a_id"] == "c_a"
    assert conflict["claim_b_id"] == "c_b"
    assert conflict["contradiction_type"] in ["DIRECT", "CONTEXT_DEPENDENT"]
    assert "convergence" in conflict["explanation"].lower() or "learning" in conflict["explanation"].lower()
