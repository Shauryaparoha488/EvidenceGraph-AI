"""Claim extraction service extracting discrete verifiable factual claims."""
import json
import re
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types

from app.core.config import settings
from app.models.claim import EvidenceClassification

class ClaimExtractor:
    """Extracts factual claims from document passages with classifications and concept tags."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self._client = None
        if self.api_key:
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[ClaimExtractor] GenAI client init: {e}")

    def extract_claims_from_passage(
        self,
        passage: str,
        document_name: str,
        page_number: Optional[int] = 1,
        context_topic: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract structured claims from a single passage.
        If Gemini is available, uses structured prompt. Otherwise uses deterministic factual parsing.
        """
        if self._client and self.api_key:
            try:
                return self._extract_with_gemini(passage, document_name, page_number, context_topic)
            except Exception as e:
                print(f"[ClaimExtractor] Gemini call failed, falling back to local extractor: {e}")

        return self._extract_locally(passage, document_name, page_number)

    def _extract_with_gemini(
        self,
        passage: str,
        document_name: str,
        page_number: Optional[int],
        context_topic: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Use Gemini to extract atomic claims with structured output."""
        prompt = f"""You are an expert scientific claim extraction system.
Analyze the following text extracted from document "{document_name}", Page {page_number}.

Extract each atomic, verifiable factual claim made in the text.
For each claim:
1. `claim_text`: A concise, standalone statement of the factual assertion.
2. `supporting_passage`: The exact snippet or sentence directly supporting this claim.
3. `classification`: One of "SUPPORTING", "CONTRADICTING", "NEUTRAL", "INSUFFICIENT" (relative to {context_topic or 'general scientific consensus'}).
4. `confidence`: A float between 0.5 and 1.0 representing assertion certainty.
5. `keywords`: List of 2-4 key concepts, variables, or entities mentioned.

Text:
\"\"\"{passage}\"\"\"

Return ONLY a valid JSON list of objects matching this schema:
[
  {{
    "claim_text": "...",
    "supporting_passage": "...",
    "classification": "SUPPORTING|CONTRADICTING|NEUTRAL|INSUFFICIENT",
    "confidence": 0.95,
    "keywords": ["concept1", "concept2"]
  }}
]
"""
        response = self._client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json"
            )
        )
        claims = json.loads(response.text)
        # Ensure page and doc info attached
        for c in claims:
            c["page_number"] = page_number
            c["document_name"] = document_name
        return claims

    def _extract_locally(
        self,
        passage: str,
        document_name: str,
        page_number: Optional[int]
    ) -> List[Dict[str, Any]]:
        """
        Robust rule-based factual claim extractor.
        Identifies declarative sentences with empirical/causal verbs.
        """
        sentences = re.split(r'(?<=[.!?])\s+', passage)
        claims = []

        # Indicators of factual assertions
        assertion_patterns = [
            r'\b(shows?|demonstrates?|reveals?|suggests?|finds?|found|proves?|proved|indicates?)\b',
            r'\b(increases?|decreases?|improves?|reduces?|causes?|leads to|results in)\b',
            r'\b(observed|measured|concluded|verified|confirmed|correlated|associated with)\b',
            r'\b(significantly|consistently|experimentally|statistically)\b'
        ]

        # Stop words for keyword extraction
        stop_words = {
            "the", "and", "or", "in", "on", "at", "to", "for", "with", "a", "an", "is", "was",
            "are", "were", "that", "this", "these", "those", "from", "by", "as", "it", "be"
        }

        for sentence in sentences:
            s_clean = sentence.strip()
            if len(s_clean) < 30 or len(s_clean) > 400:
                continue

            matches_assertion = any(re.search(pat, s_clean, re.IGNORECASE) for pat in assertion_patterns)
            if matches_assertion:
                # Classify sentiment / direction
                classification = EvidenceClassification.NEUTRAL.value
                if re.search(r'\b(improves?|increases?|supports?|effective|outperforms?|superior)\b', s_clean, re.IGNORECASE):
                    classification = EvidenceClassification.SUPPORTING.value
                elif re.search(r'\b(fails?|decreases?|worsens?|contradicts?|ineffective|inferior|not improve)\b', s_clean, re.IGNORECASE):
                    classification = EvidenceClassification.CONTRADICTING.value

                # Extract keywords (capitalized words or noun-like terms)
                words = re.findall(r'\b[A-Za-z]{3,}\b', s_clean)
                keywords = [w.capitalize() for w in words if w.lower() not in stop_words][:4]

                claims.append({
                    "claim_text": s_clean,
                    "supporting_passage": s_clean,
                    "classification": classification,
                    "confidence": 0.90,
                    "keywords": list(set(keywords)),
                    "page_number": page_number,
                    "document_name": document_name
                })

        return claims
