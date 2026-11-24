"""Interactive Knowledge Graph schemas (React Flow compatible)."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class GraphNodeData(BaseModel):
    label: str
    node_type: str  # "DOCUMENT", "CLAIM", "CONCEPT"
    details: Optional[Dict[str, Any]] = None
    classification: Optional[str] = None
    document_id: Optional[str] = None
    page_number: Optional[int] = None
    passage: Optional[str] = None

class GraphNode(BaseModel):
    id: str
    type: str = "customNode"
    data: GraphNodeData
    position: Dict[str, float]  # {"x": float, "y": float}

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None  # "SUPPORTS", "CONTRADICTS", "EXTRACTED_FROM", "RELATED_TO"
    type: str = "smoothstep"
    animated: bool = False
    data: Optional[Dict[str, Any]] = None

class KnowledgeGraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    stats: Dict[str, int]
