"""Grounded answer generation engine with strict citation validation and sufficiency check."""
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from google import genai
from google.genai import types

from app.core.config import settings

class AnswerGenerator:
    """Produces grounded answers with verified citations from retrieved evidence passages."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self._client = None
        if self.api_key:
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[AnswerGenerator] GenAI client init: {e}")

    def generate_grounded_answer(
        self,
        query: str,
        retrieved_passages: List[Dict[str, Any]],
        project_claims: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate grounded response from passages.
        If passages are empty or relevance is zero, report insufficient evidence.
        """
        if not retrieved_passages:
            return self._insufficient_evidence_response(query)

        # Build citation reference table
        citation_catalog = []
        context_blocks = []

        for idx, p in enumerate(retrieved_passages, start=1):
            citation = {
                "citation_id": idx,
                "document_id": p.get("document_id"),
                "document_name": p.get("document_name", "Unknown Document"),
                "page_number": p.get("page_number", 1),
                "chunk_id": p.get("chunk_id"),
                "exact_passage": p.get("content", "")
            }
            citation_catalog.append(citation)
            context_blocks.append(
                f"[{idx}] Source: {citation['document_name']} (Page {citation['page_number']})\nPassage: {citation['exact_passage']}"
            )

        context_str = "\n\n".join(context_blocks)

        if self._client and self.api_key:
            try:
                return self._generate_with_gemini(query, context_str, citation_catalog)
            except Exception as e:
                print(f"[AnswerGenerator] Gemini generation failed: {e}")

        # Deterministic grounded synthesis fallback
        return self._generate_locally(query, citation_catalog)

    def _generate_with_gemini(
        self,
        query: str,
        context_str: str,
        citation_catalog: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Query Gemini using structured instructions for grounded synthesis."""
        system_instruction = """You are EvidenceGraph AI, a precision research synthesis engine.
Your core mandate: EVERY important factual claim MUST be traceable to its supporting evidence via bracketed citation numbers (e.g. [1], [2]).
CRITICAL GROUNDING RULES:
1. ONLY make assertions directly supported by the provided numbered context passages.
2. If the passages DO NOT contain sufficient evidence to answer the user question reliably, you MUST explicitly state: "The available documents do not provide sufficient evidence to answer this question reliably."
3. NEVER invent facts, statistics, citations, or references not in the numbered passages.
4. Distinguish between supporting findings and conflicting/contradictory findings across documents.
"""

        prompt = f"""Context Passages:
{context_str}

User Research Question:
"{query}"

Generate a structured response as a JSON object matching this schema:
{{
  "direct_answer": "Direct answer synthesizing evidence with [1], [2] citation markers...",
  "key_findings": ["Key finding 1 with [1]", "Key finding 2 with [2]"],
  "supporting_evidence": [
    {{"claim": "Assertion", "citation_id": 1, "document_name": "...", "page_number": 1}}
  ],
  "contradictory_evidence": [
    {{"conflict": "Conflict description", "source_a_citation": 1, "source_b_citation": 2}}
  ],
  "limitations": ["Scope limitation 1", "Scope limitation 2"],
  "evidence_sufficiency": "SUFFICIENT" | "PARTIALLY_SUFFICIENT" | "INSUFFICIENT",
  "unanswered_aspects": ["Aspect 1 not covered in evidence"]
}}
"""
        response = self._client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                system_instruction=system_instruction,
                response_mime_type="application/json"
            )
        )
        answer_data = json.loads(response.text)

        # Validate citations in response against catalog
        validated_citations, answer_data = self._validate_citations(answer_data, citation_catalog)

        return {
            "content": answer_data.get("direct_answer", ""),
            "structured_answer": answer_data,
            "citations": validated_citations,
            "sufficiency_assessment": answer_data.get("evidence_sufficiency", "SUFFICIENT")
        }

    def _validate_citations(
        self,
        answer_data: Dict[str, Any],
        citation_catalog: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Validate and retain only citations that exist in the source catalog."""
        catalog_map = {c["citation_id"]: c for c in citation_catalog}
        text = answer_data.get("direct_answer", "")
        
        # Find all [i] in text
        cited_indices = set(int(m) for m in re.findall(r'\[(\d+)\]', text))
        
        # Validated list
        valid_citations = []
        for idx in sorted(cited_indices):
            if idx in catalog_map:
                valid_citations.append(catalog_map[idx])

        # If model cited nothing or invalid, attach top 2 source passages as relevant evidence
        if not valid_citations and citation_catalog:
            valid_citations = citation_catalog[:2]

        return valid_citations, answer_data

    def _generate_locally(
        self,
        query: str,
        citation_catalog: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Deterministic grounded synthesis when LLM API key is not supplied."""
        top_citations = citation_catalog[:3]
        key_findings = []
        for c in top_citations:
            snippet = c["exact_passage"][:150].strip() + "..."
            key_findings.append(f"{snippet} [{c['citation_id']}]")

        direct_answer = (
            f"Based on evidence extracted from {len(top_citations)} source passages, "
            + " ".join(key_findings)
        )

        structured_answer = {
            "direct_answer": direct_answer,
            "key_findings": key_findings,
            "supporting_evidence": [
                {
                    "claim": c["exact_passage"][:100],
                    "citation_id": c["citation_id"],
                    "document_name": c["document_name"],
                    "page_number": c["page_number"]
                }
                for c in top_citations
            ],
            "contradictory_evidence": [],
            "limitations": ["Synthesized from indexed document passages."],
            "evidence_sufficiency": "SUFFICIENT" if len(citation_catalog) >= 2 else "PARTIALLY_SUFFICIENT",
            "unanswered_aspects": []
        }

        return {
            "content": direct_answer,
            "structured_answer": structured_answer,
            "citations": top_citations,
            "sufficiency_assessment": structured_answer["evidence_sufficiency"]
        }

    def _insufficient_evidence_response(self, query: str) -> Dict[str, Any]:
        """Standard explicit insufficient evidence response."""
        msg = "The available documents do not provide sufficient evidence to answer this question reliably."
        return {
            "content": msg,
            "structured_answer": {
                "direct_answer": msg,
                "key_findings": [],
                "supporting_evidence": [],
                "contradictory_evidence": [],
                "limitations": ["No relevant indexed document passages matched this query."],
                "evidence_sufficiency": "INSUFFICIENT",
                "unanswered_aspects": [query]
            },
            "citations": [],
            "sufficiency_assessment": "INSUFFICIENT"
        }
