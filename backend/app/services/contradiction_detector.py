"""Contradiction detection service analyzing conflicting evidence across research documents."""
import json
import re
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types

from app.core.config import settings
from app.models.contradiction import ContradictionType

class ContradictionDetector:
    """Detects and explains contradictions and nuanced disagreements between pairs of claims."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self._client = None
        if self.api_key:
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[ContradictionDetector] GenAI client init: {e}")

    def analyze_claim_pair(
        self,
        claim_a: Dict[str, Any],
        claim_b: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Compare two claims from different documents or sections.
        Returns contradiction details if conflict detected, else None.
        """
        # If Gemini is configured, use LLM comparative reasoning
        if self._client and self.api_key:
            try:
                return self._analyze_with_gemini(claim_a, claim_b)
            except Exception as e:
                print(f"[ContradictionDetector] Gemini comparison failed: {e}")

        # Deterministic semantic comparison
        return self._analyze_locally(claim_a, claim_b)

    def _analyze_with_gemini(
        self,
        claim_a: Dict[str, Any],
        claim_b: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Use Gemini to evaluate nuance, conditions, populations, and contradictions."""
        prompt = f"""You are a rigorous scientific literature reviewer specializing in evidence conflict analysis.
Compare these two claims from research documents:

CLAIM A:
Document: {claim_a.get('document_name', 'Doc A')} (Page {claim_a.get('page_number', '?')})
Text: "{claim_a.get('claim_text')}"
Supporting Context: "{claim_a.get('supporting_passage')}"

CLAIM B:
Document: {claim_b.get('document_name', 'Doc B')} (Page {claim_b.get('page_number', '?')})
Text: "{claim_b.get('claim_text')}"
Supporting Context: "{claim_b.get('supporting_passage')}"

Determine if there is a contradiction or disagreement between these two claims.
Do not classify as contradiction if wording merely differs but meanings align.
Consider scope, populations, conditions, and definitions.

If there IS a disagreement, classify as:
- DIRECT (Direct mutually exclusive contradiction)
- CONTEXT_DEPENDENT (Conflict depends on specific scope, parameter, or environment)
- EXPERIMENTAL_DIFFERENCE (Difference arising from differing methodology or dataset)
- UNRESOLVED (Inconclusive or conflicting metrics)

Return a JSON object:
{{
  "is_contradiction": true/false,
  "contradiction_type": "DIRECT|CONTEXT_DEPENDENT|EXPERIMENTAL_DIFFERENCE|UNRESOLVED",
  "explanation": "Detailed explanation of why and how they disagree",
  "confidence": 0.85
}}
"""
        response = self._client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json"
            )
        )
        res = json.loads(response.text)
        if res.get("is_contradiction"):
            return {
                "claim_a_id": claim_a.get("id"),
                "claim_b_id": claim_b.get("id"),
                "contradiction_type": res.get("contradiction_type", ContradictionType.DIRECT.value),
                "explanation": res.get("explanation", ""),
                "confidence": float(res.get("confidence", 0.85))
            }
        return None

    def _analyze_locally(
        self,
        claim_a: Dict[str, Any],
        claim_b: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Rule-based contradiction analysis comparing shared entities and opposing predicates.
        """
        text_a = claim_a.get("claim_text", "").lower()
        text_b = claim_b.get("claim_text", "").lower()

        # Check for overlapping concepts/keywords
        words_a = set(re.findall(r'\b\w{4,}\b', text_a))
        words_b = set(re.findall(r'\b\w{4,}\b', text_b))
        common = words_a.intersection(words_b)

        # If they share at least 2 substantive words
        if len(common) >= 2:
            # Positive vs negative predicates
            positive_cues = ["increase", "improve", "accelerate", "superior", "enhance", "higher", "positive", "beneficial"]
            negative_cues = ["decrease", "degrade", "slow", "inferior", "reduce", "lower", "negative", "detrimental", "not improve", "fails"]

            a_pos = any(c in text_a for c in positive_cues)
            a_neg = any(c in text_a for c in negative_cues)
            b_pos = any(c in text_b for c in positive_cues)
            b_neg = any(c in text_b for c in negative_cues)

            if (a_pos and b_neg) or (a_neg and b_pos):
                c_type = ContradictionType.DIRECT.value
                if "under" in text_a or "when" in text_a or "under" in text_b or "when" in text_b:
                    c_type = ContradictionType.CONTEXT_DEPENDENT.value

                return {
                    "claim_a_id": claim_a.get("id"),
                    "claim_b_id": claim_b.get("id"),
                    "contradiction_type": c_type,
                    "explanation": f"Claim from {claim_a.get('document_name', 'Doc A')} indicates positive impact while Claim from {claim_b.get('document_name', 'Doc B')} indicates reduction or failure regarding shared concept '{list(common)[0]}'.",
                    "confidence": 0.82
                }

        return None
