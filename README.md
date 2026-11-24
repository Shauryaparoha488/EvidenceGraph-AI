# EvidenceGraph AI
### An Evidence-Grounded AI Research and Knowledge Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue.svg)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC.svg)](https://tailwindcss.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-red.svg)](https://qdrant.tech)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## 1. Project Overview & Vision

Conventional Large Language Model applications often generate fluent, persuasive answers without verifiable backing. In scientific, legal, and biomedical research, ungrounded assertions lead to dangerous hallucinations and unvalidated claims.

**EvidenceGraph AI** enforces a fundamental principle:

> **Every important factual claim must be traceable to its supporting evidence.**

EvidenceGraph AI is a full-stack research intelligence platform where users upload multi-document corpuses (PDFs, DOCX, TXT, Markdown), extract discrete factual claims, detect cross-document contradictions, generate grounded answers with numbered source citations, and visualize conceptual relationships through an interactive knowledge graph.

---

## 2. Core Architecture

```mermaid
flowchart TD
    subgraph Client ["Frontend (React 18 + TypeScript + Vite + Tailwind)"]
        UI["Modern Research UI"]
        RF["Interactive Knowledge Graph (React Flow)"]
        Chat["Grounded Assistant & Citation Drawer"]
        Reports["PDF / Markdown Report Viewer"]
    end

    subgraph Backend ["Backend API (FastAPI + Pydantic v2)"]
        Router["REST Routers (Auth, Docs, Claims, Chat, Graph, Reports)"]
        Agent["Multi-Stage Research Agent"]
        Critic["Critic & Citation Validator"]
    end

    subgraph Processing ["Document Intelligence & Ingestion"]
        PyMuPDF["PyMuPDF / python-docx Extractors"]
        Chunker["Semantic Overlap Chunker"]
        Embedder["FastEmbed (BAAI/bge-small-en-v1.5)"]
    end

    subgraph Storage ["Persistent Data Layer"]
        SQL[("Relational DB (PostgreSQL / SQLite)")]
        Qdrant[("Qdrant Vector DB (Dense Embeddings)")]
        FS["File Storage (PDFs, Reports)"]
    end

    UI --> Router
    Router --> Agent
    Agent --> Critic
    PyMuPDF --> Chunker --> Embedder
    Embedder --> Qdrant
    Chunker --> SQL
    Agent --> Qdrant
    Agent --> SQL
    Router --> FS
```

---

## 3. Controlled AI Agent Workflow

```mermaid
sequenceDiagram
    autonumber
    actor User as Researcher
    participant UI as EvidenceGraph UI
    participant Agent as Research Agent
    participant Hybrid as Hybrid Retrieval (Qdrant + BM25)
    participant Extractor as Claim Extractor
    participant Contra as Contradiction Engine
    participant LLM as Google Gemini / Grounding
    participant Critic as Citation Validator

    User->>UI: Submits Research Question
    UI->>Agent: execute_research_workflow(query, project_id)
    Agent->>Hybrid: Dense + Sparse Retrieval with Reciprocal Rank Fusion
    Hybrid-->>Agent: Top Ranked Relevant Passages
    Agent->>Extractor: Extract atomic factual assertions from passages
    Extractor-->>Agent: Categorized Claims (Supporting, Contradicting, Neutral)
    Agent->>Contra: Compare cross-document claim pairs
    Contra-->>Agent: Detected Disagreements & Explanations
    Agent->>LLM: Grounded Synthesis with strict passage constraints
    LLM-->>Critic: Answer draft with bracketed citations [1], [2]
    Critic-->>Critic: Validate every [i] against actual retrieved catalog
    Critic-->>UI: Verified Grounded Answer + Citations + Sufficiency Assessment
    UI->>User: Renders Answer, Clickable Citations, and Conflicting Claims
```

---

## 4. Database Schema Design

```mermaid
erDiagram
    USERS ||--o{ PROJECTS : owns
    PROJECTS ||--o{ DOCUMENTS : contains
    PROJECTS ||--o{ CONVERSATIONS : tracks
    PROJECTS ||--o{ RESEARCH_REPORTS : generates
    DOCUMENTS ||--o{ DOCUMENT_CHUNKS : splits_into
    DOCUMENTS ||--o{ EXTRACTED_CLAIMS : yields
    DOCUMENT_CHUNKS ||--o{ EXTRACTED_CLAIMS : references
    CONVERSATIONS ||--o{ MESSAGES : contains
    EXTRACTED_CLAIMS ||--o{ CONTRADICTIONS : conflicts_with

    USERS {
        string id PK
        string email
        string hashed_password
        string full_name
        datetime created_at
    }

    PROJECTS {
        string id PK
        string user_id FK
        string title
        string description
        datetime created_at
    }

    DOCUMENTS {
        string id PK
        string project_id FK
        string filename
        string file_type
        int page_count
        int chunk_count
        string status
    }

    DOCUMENT_CHUNKS {
        string id PK
        string document_id FK
        int page_number
        string section
        text content
        string qdrant_point_id
    }

    EXTRACTED_CLAIMS {
        string id PK
        string project_id FK
        string document_id FK
        string chunk_id FK
        text claim_text
        string classification
        float confidence
        json keywords
    }

    CONTRADICTIONS {
        string id PK
        string project_id FK
        string claim_a_id FK
        string claim_b_id FK
        string contradiction_type
        text explanation
        float confidence
    }
```

---

## 5. Key Modules Implemented

### Module A: Authentication and Workspace
- User registration and login with bcrypt hashing and signed JWT authentication.
- Workspace-level data isolation: documents, vectors, claims, and chat sessions are strictly private to the user.

### Module B: Document Intelligence Pipeline
- Handles PDF (PyMuPDF with page geometry and text normalization), DOCX (python-docx), TXT, and Markdown.
- Semantic overlapping chunker preserving page numbers, section headers, and token counts.
- Background asynchronous processing for large document libraries.

### Module C: Advanced Retrieval Engine
- Hybrid retrieval: Qdrant dense vector search (Cosine distance) + BM25 keyword matching (`rank-bm25`).
- Reciprocal Rank Fusion (RRF): $RRF(d) = \sum \frac{1}{60 + rank_i(d)}$.
- Jaccard token deduplication removing redundant passages.

### Module D: Evidence & Claim Extraction Engine
- Isolates atomic, verifiable statements from retrieved passages.
- Classifies claims into `SUPPORTING`, `CONTRADICTING`, `NEUTRAL`, and `INSUFFICIENT`.
- Tagging of key scientific concepts for graph indexing.

### Module E: Grounded Answer Generation & Citation Validation
- Strict grounding with Google Gemini 2.5 Flash and deterministic synthesis fallback.
- Explicit insufficient evidence communication: *"The available documents do not provide sufficient evidence to answer this question reliably."*
- Verification layer: rejects any citation number not present in the indexed source catalog.

### Module F: Contradiction Detection Engine
- Cross-document comparative analysis identifying direct contradictions, context-dependent variances, and experimental differences.
- Side-by-side claim comparison with detailed explanations and original passages.

### Module G: Interactive Knowledge Graph
- React Flow interactive canvas displaying Documents, Claims, and Concepts.
- Edges: `EXTRACTED_FROM`, `SUPPORTS`, `CONTRADICTS`, `RELATED_TO`.
- Full zoom, pan, node search, relationship filtering, and slide-out evidence inspection drawer.

### Module H & I: Research Reports & Export
- Formatted investigation reports containing executive summaries, key findings, supporting citations, and limitation audits.
- Export options: publication-quality PDF via ReportLab and raw scientific Markdown.

---

## 6. API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register new researcher account |
| `POST` | `/api/auth/login-json` | Authenticate and obtain JWT access token |
| `GET` | `/api/auth/me` | Fetch authenticated researcher profile |
| `GET` | `/api/projects/` | List user's isolated research workspaces |
| `POST` | `/api/projects/` | Create a new research workspace |
| `POST` | `/api/documents/upload` | Upload PDF/DOCX/TXT and trigger ingestion |
| `GET` | `/api/documents/project/{id}` | List indexed documents for a project |
| `GET` | `/api/documents/{id}/download` | View or download original document file |
| `POST` | `/api/retrieval/search` | Execute hybrid vector + BM25 retrieval |
| `GET` | `/api/claims/project/{id}` | List extracted claims with classification filters |
| `GET` | `/api/claims/contradictions/{id}`| List detected cross-document contradictions |
| `POST` | `/api/chat/message` | Submit grounded query to the Research Agent |
| `GET` | `/api/graph/project/{id}` | Obtain React Flow formatted Knowledge Graph |
| `POST` | `/api/reports/generate` | Synthesize and generate research report |
| `GET` | `/api/reports/{id}/pdf` | Download formatted publication PDF report |
| `GET` | `/api/reports/{id}/markdown` | Download report as raw Markdown |
| `GET` | `/api/analytics/summary` | Aggregate dashboard statistics |

---

## 7. Local Execution Guide

### Prerequisites
- Python 3.12+
- Node.js 20+

### 1. Backend Setup
```powershell
cd backend
python -m pip install -r requirements.txt
python app/main.py
```
The backend API server will start on `http://localhost:8000`. Swagger documentation is available at `http://localhost:8000/docs`.

### 2. Frontend Setup
```powershell
cd frontend
npm install
npm run dev
```
The React frontend will start on `http://localhost:5173`.

---

## 8. Docker Compose Deployment

Run the complete stack (FastAPI, React, Qdrant, PostgreSQL) with one command:

```bash
docker-compose up --build
```

- Frontend: `http://localhost:80`
- Backend API: `http://localhost:8000`
- Qdrant UI: `http://localhost:6333/dashboard`

---

## 9. Automated Testing

Run the full pytest suite covering authentication, chunking, embeddings, hybrid retrieval, claim extraction, contradiction detection, graph serialization, and end-to-end research workflows:

```powershell
python -m pytest backend/tests -v
```

**Results:**
```
backend/tests/test_answer_graph_report.py::test_insufficient_evidence_response PASSED
backend/tests/test_answer_graph_report.py::test_grounded_answer_with_citations PASSED
backend/tests/test_answer_graph_report.py::test_knowledge_graph_react_flow_serialization PASSED
backend/tests/test_answer_graph_report.py::test_report_generator_markdown_and_pdf PASSED
backend/tests/test_auth.py::test_password_hashing_and_verification PASSED
backend/tests/test_auth.py::test_jwt_token_creation_and_decoding PASSED
backend/tests/test_auth.py::test_user_creation_and_isolation PASSED
backend/tests/test_claims_contradictions.py::test_claim_extraction_from_passage PASSED
backend/tests/test_claims_contradictions.py::test_contradiction_detection_between_conflicting_claims PASSED
backend/tests/test_e2e_workflow.py::test_complete_e2e_research_lifecycle PASSED
backend/tests/test_embeddings_vector.py::test_embedding_generation PASSED
backend/tests/test_embeddings_vector.py::test_vector_store_upsert_and_retrieval PASSED
backend/tests/test_processing.py::test_clean_text_normalization PASSED
backend/tests/test_processing.py::test_markdown_and_text_extraction PASSED
backend/tests/test_processing.py::test_semantic_chunking_with_overlap PASSED
backend/tests/test_processing.py::test_unsupported_file_format PASSED
backend/tests/test_retrieval.py::test_reciprocal_rank_fusion_and_deduplication PASSED

======================== 17 passed in 10.80s (100%) ========================
```

---

## 10. Repository Information

- **GitHub Repository**: [https://github.com/Shauryaparoha488/EvidenceGraph-AI](https://github.com/Shauryaparoha488/EvidenceGraph-AI)
- **Branch**: `main`

---

## 11. Known Limitations & Future Enhancements
- **OCR Extension**: Scanned image-only PDFs currently require optional Tesseract integration.
- **Neo4j Production Adapter**: The current NetworkX knowledge graph abstraction layer can be connected to a live Neo4j cluster for billion-edge queries.
