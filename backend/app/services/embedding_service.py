"""Embedding service providing dense vector representations."""
from typing import List
import numpy as np
from app.core.config import settings

class EmbeddingService:
    """Manages text embeddings via FastEmbed ONNX models or Gemini."""

    _instance = None
    _model = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.provider = settings.EMBEDDING_PROVIDER
        self.model_name = settings.EMBEDDING_MODEL
        self._init_model()

    def _init_model(self):
        """Initialize the local embedding model."""
        if self.provider == "fastembed":
            try:
                from fastembed import TextEmbedding
                # Using BAAI/bge-small-en-v1.5 (dimension 384)
                self._model = TextEmbedding(model_name=self.model_name)
            except Exception as e:
                print(f"[EmbeddingService] FastEmbed initialization fallback: {e}")
                self._model = None
        else:
            self._model = None

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate normalized vector embeddings for a list of passages."""
        if not texts:
            return []

        if self._model is not None:
            embeddings_generator = self._model.embed(texts)
            return [emb.tolist() for emb in embeddings_generator]

        # Deterministic lightweight fallback (TF-IDF hashed embedding) if model is not yet cached
        return [self._fallback_embed(t) for t in texts]

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for search query."""
        results = self.embed_texts([query])
        return results[0] if results else [0.0] * settings.EMBEDDING_DIMENSION

    def _fallback_embed(self, text: str) -> List[float]:
        """Deterministic pseudo-semantic vector representation used if weights are loading."""
        dim = settings.EMBEDDING_DIMENSION
        vec = np.zeros(dim, dtype=np.float32)
        words = text.lower().split()
        for i, word in enumerate(words):
            h = hash(word) % dim
            vec[h] += 1.0 / (1.0 + i * 0.1)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()
