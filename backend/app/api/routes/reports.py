"""Research Report routes."""
import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.report import ResearchReport
from app.schemas.report import ReportGenerateRequest, ReportResponse
from app.agents.research_agent import ResearchAgent
from app.services.report_generator import ReportGenerator

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def generate_report(
    req: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate structured research report with Markdown and PDF exports."""
    project = db.query(Project).filter(Project.id == req.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    # Execute research workflow to gather synthesis, findings, and citations
    agent = ResearchAgent(db)
    result = agent.execute_research_workflow(
        query=req.research_question,
        project_id=req.project_id,
        top_k=10
    )

    structured = result.get("structured_answer", {})
    report_title = req.title or f"Investigation: {req.research_question[:40]}..."

    report_payload = {
        "title": report_title,
        "research_question": req.research_question,
        "executive_summary": structured.get("direct_answer", result.get("content", "")),
        "key_findings": structured.get("key_findings", []),
        "supporting_evidence": structured.get("supporting_evidence", []),
        "contradictory_findings": result.get("contradictions", []),
        "limitations": " ".join(structured.get("limitations", [])),
        "references": result.get("citations", []),
        "conclusion": "Evidence grounded investigation completed with traceable document citations."
    }

    # Generate Markdown & PDF
    markdown_content = ReportGenerator.generate_markdown(report_payload)
    pdf_filename = f"report_{uuid.uuid4().hex[:10]}.pdf"
    try:
        pdf_path = ReportGenerator.generate_pdf(report_payload, pdf_filename)
    except Exception as e:
        print(f"[PDFGenerationWarning] {e}")
        pdf_path = None

    db_report = ResearchReport(
        project_id=req.project_id,
        title=report_title,
        research_question=req.research_question,
        executive_summary=report_payload["executive_summary"],
        key_findings=report_payload["key_findings"],
        supporting_evidence=report_payload["supporting_evidence"],
        contradictory_findings=report_payload["contradictory_findings"],
        limitations=report_payload["limitations"],
        references=report_payload["references"],
        conclusion=report_payload["conclusion"],
        markdown_content=markdown_content,
        pdf_path=pdf_path
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    resp = ReportResponse.model_validate(db_report)
    if db_report.pdf_path:
        resp.pdf_download_url = f"/api/reports/{db_report.id}/pdf"
    return resp

@router.get("/project/{project_id}", response_model=List[ReportResponse])
def list_reports(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List reports generated for a project."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    reports = db.query(ResearchReport).filter(ResearchReport.project_id == project_id).order_by(ResearchReport.created_at.desc()).all()
    out = []
    for r in reports:
        item = ReportResponse.model_validate(r)
        if r.pdf_path and os.path.exists(r.pdf_path):
            item.pdf_download_url = f"/api/reports/{r.id}/pdf"
        out.append(item)
    return out

@router.get("/{report_id}/pdf")
def download_pdf_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download generated PDF report."""
    report = db.query(ResearchReport).join(Project).filter(ResearchReport.id == report_id, Project.user_id == current_user.id).first()
    if not report or not report.pdf_path or not os.path.exists(report.pdf_path):
        raise HTTPException(status_code=404, detail="PDF report not found.")

    return FileResponse(report.pdf_path, filename=f"{report.title.replace(' ', '_')}.pdf")

@router.get("/{report_id}/markdown")
def download_markdown_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download report as raw Markdown."""
    report = db.query(ResearchReport).join(Project).filter(ResearchReport.id == report_id, Project.user_id == current_user.id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    return PlainTextResponse(report.markdown_content, media_type="text/markdown")
