# EvidenceGraph AI

### An Evidence-Grounded AI Research and Knowledge Intelligence Platform

EvidenceGraph AI bridges the gap between raw document ingestion and verifiable AI reasoning. Every factual claim generated is traceable to its source passage, evaluated for contradiction, and visually interconnected via an interactive knowledge graph.

---

## High-Level Capabilities

1. **Multi-Format Document Ingestion**: Process PDF, DOCX, TXT, and Markdown with page number and section tracking.
2. **Hybrid Semantic & Keyword Retrieval**: Vector search powered by Qdrant combined with BM25 keyword matching and cross-passage reranking.
3. **Claim & Evidence Extraction**: Isolates individual claims with classifications:
   - *Supporting Evidence*
   - *Contradicting Evidence*
   - *Neutral / Contextual Evidence*
   - *Insufficient Evidence*
4. **Contradiction Detection**: Side-by-side comparative analysis evaluating definitions, experimental scopes, and temporal conditions.
5. **Grounded Answer Generation**: Structured responses powered by Google Gemini, requiring strict citation validation.
6. **Interactive Knowledge Graph**: React Flow powered visualization of documents, claims, concepts, and relationships (`SUPPORTS`, `CONTRADICTS`, `EXTRACTED_FROM`, `RELATED_TO`).
7. **Research Reports**: Export structured investigation reports to PDF and Markdown.

---

## Repository Structure

```
EvidenceGraph-AI/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── agents/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
├── .env.example
└── README.md
```
