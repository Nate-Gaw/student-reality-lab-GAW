from __future__ import annotations

import os
from pathlib import Path
from typing import List


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PERSIST_DIR = Path(os.getenv("RAG_PERSIST_DIR", PROJECT_ROOT / "vector_db" / "chroma"))
COLLECTION_NAME = os.getenv("RAG_COLLECTION", "advisor_docs")
EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2")


class RagService:
    def __init__(self) -> None:
        self._client = None
        self._collection = None
        self._embedder = None

    def _ensure(self) -> None:
        from chromadb.config import Settings
        import chromadb
        from sentence_transformers import SentenceTransformer

        if self._client is None:
            self._client = chromadb.Client(Settings(persist_directory=str(PERSIST_DIR)))
        if self._collection is None:
            self._collection = self._client.get_or_create_collection(COLLECTION_NAME)
        if self._embedder is None:
            self._embedder = SentenceTransformer(EMBEDDING_MODEL)

    def query(self, text: str, limit: int = 3, universities: List[str] | None = None, category: str | None = None) -> List[dict]:
        if not text:
            return []

        if not PERSIST_DIR.exists() or not any(PERSIST_DIR.iterdir()):
            return []

        try:
            self._ensure()
        except Exception:
            return []

        embeddings = self._embedder.encode([text]).tolist()
        where = {}
        if universities:
            where["university"] = {"$in": [name.lower() for name in universities]}
        if category:
            where["category"] = category.lower()
        from backend.cache.redis_cache import cache
        cache_key = None
        if universities:
            key_universities = ":".join(sorted([name.lower() for name in universities]))
            key_category = (category or "all").lower()
            cache_key = f"rag:{key_universities}:{key_category}"
            cached = cache.get(cache_key)
            if cached:
                return cached

        results = self._collection.query(query_embeddings=embeddings, n_results=limit, where=where or None)
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        snippets = []
        for doc, meta in zip(documents, metadatas):
            if not doc:
                continue
            snippets.append({
                "text": doc,
                "university": (meta or {}).get("university", ""),
                "category": (meta or {}).get("category", ""),
            })
        if cache_key:
            cache.set(cache_key, snippets, ttl_seconds=1800)
        return snippets


rag_service = RagService()


def get_rag_snippets(query: str, limit: int = 3, universities: List[str] | None = None, category: str | None = None) -> List[dict]:
    return rag_service.query(query, limit=limit, universities=universities, category=category)
