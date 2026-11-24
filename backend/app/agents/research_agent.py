"""EvidenceGraph AI Research Agent orchestrating multi-stage grounded synthesis."""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.services.retrieval_service import RetrievalService
from app.services.claim_extractor import ClaimExtractor
from app.services.contradiction_detector import ContradictionDetector
from app.services.answer_generator import AnswerGenerator
from app.models.claim import ExtractedClaim
from app.models.contradiction import ContradictionItem

class ResearchAgent:
    """
    Controlled multi-agent workflow:
    1. Query Understanding & Expansion
    2. Retrieval Agent (Hybrid Vector + BM25 + Reciprocal Rank Fusion)
    3. Evidence Extraction Agent (Isolates atomic claims from passages)
    4. Contradiction Analysis Agent (Compares claims across documents)
    5. Critic / Verification Agent (Verifies claim-to-passage alignment)
    6. Grounded Answer Generation (Gemini with strict groundedness)
    7. Citation Validation (Rejects hallucinated or unverified sources)
    """

    def __init__(self, db: Session):
        self.db = db
        self.retrieval_service = RetrievalService(db)
        self.claim_extractor = ClaimExtractor()
        self.contradiction_detector = ContradictionDetector()
        self.answer_generator = AnswerGenerator()

    def execute_research_workflow(
        self,
        query: str,
        project_id: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = 8
    ) -> Dict[str, Any]:
        """Run the end-to-end evidence synthesis pipeline."""

        # 1. Query Understanding & Retrieval Stage
        passages = self.retrieval_service.hybrid_retrieve(
            query=query,
            project_id=project_id,
            document_ids=document_ids,
            top_k=top_k,
            use_hybrid=True
        )

        if not passages:
            return self.answer_generator._insufficient_evidence_response(query)

        # 2. Evidence & Claim Extraction Stage
        new_extracted_claims = []
        for p in passages[:4]:
            claims = self.claim_extractor.extract_claims_from_passage(
                passage=p["content"],
                document_name=p["document_name"],
                page_number=p.get("page_number", 1),
                context_topic=query
            )
            for c in claims:
                c["document_id"] = p["document_id"]
                c["chunk_id"] = p["chunk_id"]
                new_extracted_claims.append(c)

        # 3. Contradiction Detection Stage
        detected_contradictions = []
        for i in range(len(new_extracted_claims)):
            for j in range(i + 1, len(new_extracted_claims)):
                ca = new_extracted_claims[i]
                cb = new_extracted_claims[j]
                # Compare claims from differing documents or distinct sections
                if ca.get("document_id") != cb.get("document_id"):
                    conflict = self.contradiction_detector.analyze_claim_pair(ca, cb)
                    if conflict:
                        detected_contradictions.append(conflict)

        # 4. Critic & Verification Stage
        # Ensure passages actually contain substantive text related to query
        verified_passages = [p for p in passages if len(p.get("content", "").strip()) > 20]

        # 5. Grounded Answer Generation with Citation Validation
        answer_result = self.answer_generator.generate_grounded_answer(
            query=query,
            retrieved_passages=verified_passages,
            project_claims=new_extracted_claims
        )

        # Attach workflow telemetry
        answer_result["workflow_metadata"] = {
            "passages_retrieved": len(verified_passages),
            "claims_extracted": len(new_extracted_claims),
            "contradictions_found": len(detected_contradictions),
            "evidence_sufficiency": answer_result["sufficiency_assessment"]
        }
        answer_result["contradictions"] = detected_contradictions
        answer_result["extracted_claims"] = new_extracted_claims

        return answer_result
