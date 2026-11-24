"""Qdrant vector store integration for persistent semantic retrieval."""
import os
import uuid
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.core.config import settings

class VectorStore:
    """Qdrant client abstraction for indexed document chunk vector retrieval."""

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.collection_name = "evidencegraph_chunks"
        self.dimension = settings.EMBEDDING_DIMENSION
        self._init_client()
        self._ensure_collection()

    def _init_client(self):
        """Initialize Qdrant client based on configuration."""
        if settings.QDRANT_MODE == "server" and settings.QDRANT_URL:
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY or None,
                timeout=30.0
            )
        else:
            # Persistent local storage
            os.makedirs(settings.QDRANT_PATH, exist_ok=True)
            self.client = QdrantClient(path=settings.QDRANT_PATH)

    def _ensure_collection(self):
        """Create Qdrant collection if not already existing."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(
                    size=self.dimension,
                    distance=qmodels.Distance.COSINE
                )
            )

    def upsert_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> List[str]:
        """
        Store chunks and their dense embeddings in Qdrant.
        Returns list of point IDs.
        """
        points = []
        point_ids = []

        for chunk, embedding in zip(chunks, embeddings):
            point_id = str(uuid.uuid4())
            point_ids.append(point_id)
            
            payload = {
                "chunk_id": chunk.get("id"),
                "document_id": chunk.get("document_id"),
                "document_name": chunk.get("document_name", ""),
                "project_id": chunk.get("project_id"),
                "page_number": chunk.get("page_number"),
                "section": chunk.get("section"),
                "content": chunk.get("content"),
                "chunk_index": chunk.get("chunk_index")
            }

            points.append(qmodels.PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload
            ))

        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
        return point_ids

    def search(
        self,
        query_vector: List[float],
        project_id: str,
        document_ids: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search filtered by project and optional documents.
        """
        must_filters = [
            qmodels.FieldCondition(
                key="project_id",
                match=qmodels.MatchValue(value=project_id)
            )
        ]

        if document_ids:
            must_filters.append(
                qmodels.FieldCondition(
                    key="document_id",
                    match=qmodels.MatchAny(any=document_ids)
                )
            )

        query_filter = qmodels.Filter(must=must_filters)

        query_response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True
        )

        passages = []
        for res in query_response.points:
            passages.append({
                "chunk_id": res.payload.get("chunk_id"),
                "document_id": res.payload.get("document_id"),
                "document_name": res.payload.get("document_name"),
                "page_number": res.payload.get("page_number"),
                "section": res.payload.get("section"),
                "content": res.payload.get("content"),
                "score": float(res.score),
                "point_id": res.id
            })
        return passages

    def delete_document_points(self, document_id: str):
        """Delete all points associated with a specific document."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="document_id",
                        match=qmodels.MatchValue(value=document_id)
                    )
                ]
            )
        )
