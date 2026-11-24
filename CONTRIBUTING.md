# Contributing to EvidenceGraph AI

Thank you for contributing to EvidenceGraph AI! This platform is dedicated to grounded, traceable AI research intelligence.

---

## Development Setup

### Backend (Python 3.12+)
```powershell
cd backend
python -m pip install -r requirements.txt
python app/main.py
```

### Frontend (Node.js 20+)
```powershell
cd frontend
npm install
npm run dev
```

---

## Running the Automated Test Suite

Every pull request and commit must pass all automated unit and integration tests:

```powershell
python -m pytest backend/tests -v
```

### Areas Covered by Tests
- JWT and User isolation (`test_auth.py`)
- Document ingestion & semantic chunking (`test_processing.py`)
- FastEmbed and Qdrant vector retrieval (`test_embeddings_vector.py`)
- BM25 and Reciprocal Rank Fusion (`test_retrieval.py`)
- Factual claim extraction & contradiction detection (`test_claims_contradictions.py`)
- React Flow knowledge graph and PDF generation (`test_answer_graph_report.py`)
- Full End-to-End research lifecycle (`test_e2e_workflow.py`)

---

## Coding Standards
- Python: PEP 8, Pydantic v2 schemas, typed functions, SQLAlchemy ORM.
- TypeScript: Strict type definitions without unconstrained `any`, functional React components.
- Groundedness Principle: All factual claims returned by AI agents must strictly retain passage and document citations.
