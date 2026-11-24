"""Chat and conversational research routes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.conversation import Conversation, Message
from app.schemas.chat import ChatRequest, MessageResponse, ConversationResponse
from app.agents.research_agent import ResearchAgent

router = APIRouter(prefix="/chat", tags=["Research Chat"])

@router.post("/message", response_model=MessageResponse)
def send_chat_message(
    chat_in: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit research query and obtain citation-grounded response."""
    project = db.query(Project).filter(Project.id == chat_in.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    # Get or create conversation
    conv = None
    if chat_in.conversation_id:
        conv = db.query(Conversation).filter(
            Conversation.id == chat_in.conversation_id,
            Conversation.project_id == project.id
        ).first()

    if not conv:
        conv = Conversation(
            project_id=project.id,
            title=chat_in.message[:50] + "..." if len(chat_in.message) > 50 else chat_in.message
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # 1. Save user message
    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=chat_in.message
    )
    db.add(user_msg)
    db.commit()

    # 2. Execute Research Agent Workflow
    agent = ResearchAgent(db)
    agent_output = agent.execute_research_workflow(
        query=chat_in.message,
        project_id=project.id
    )

    # 3. Save assistant message with citations & structured findings
    assistant_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=agent_output["content"],
        structured_answer=agent_output.get("structured_answer"),
        citations=agent_output.get("citations", []),
        sufficiency_assessment=agent_output.get("sufficiency_assessment")
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return MessageResponse.model_validate(assistant_msg)

@router.get("/conversations/project/{project_id}", response_model=List[ConversationResponse])
def list_conversations(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all research chat sessions in a project."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    convs = db.query(Conversation).filter(Conversation.project_id == project_id).order_by(Conversation.updated_at.desc()).all()
    return [ConversationResponse.model_validate(c) for c in convs]

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation history with all messages and citations."""
    conv = db.query(Conversation).join(Project).filter(Conversation.id == conversation_id, Project.user_id == current_user.id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    return ConversationResponse.model_validate(conv)
