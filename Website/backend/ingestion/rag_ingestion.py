from __future__ import annotations

import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from sqlalchemy import delete, select

from backend.database.models import RagChunk, RagDocument, SessionLocal


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PERSIST_DIR = Path(os.getenv("RAG_PERSIST_DIR", PROJECT_ROOT / "vector_db" / "chroma"))
COLLECTION_NAME = os.getenv("RAG_COLLECTION", "advisor_docs")
EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2")


def _iter_documents(input_dir: Path) -> Iterable[tuple[Path, str]]:
    for path in input_dir.rglob("*.txt"):
        yield path, path.read_text(encoding="utf-8")


def _extract_metadata(input_dir: Path, path: Path) -> tuple[str, str]:
    relative = path.relative_to(input_dir)
    parts = list(relative.parts)
    university = ""
    category = ""
    if len(parts) >= 3:
        university = parts[0]
        category = parts[1]
    elif len(parts) == 2:
        university = parts[0]
        category = "general"
    return university, category


def _checksum(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _chunk(text: str, chunk_size: int = 800) -> List[str]:
    words = text.split()
    chunks = []
    current = []
    for word in words:
        current.append(word)
        if len(current) >= chunk_size:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks


def ingest_rag(input_dir: str) -> None:
    directory = Path(input_dir)
    if not directory.exists():
        raise FileNotFoundError(f"RAG input directory not found: {directory}")

    client = chromadb.Client(Settings(persist_directory=str(PERSIST_DIR)))
    collection = client.get_or_create_collection(COLLECTION_NAME)
    embedder = SentenceTransformer(EMBEDDING_MODEL)

    ids = []
    documents = []
    metadatas = []
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    with SessionLocal() as session:
        for path, text in _iter_documents(directory):
            doc_id = path.stem
            checksum = _checksum(text)
            title = path.stem
            university, category = _extract_metadata(directory, path)

            existing = session.scalar(select(RagDocument).where(RagDocument.doc_id == doc_id))
            if existing:
                existing.title = title
                existing.category = category
                existing.full_text = text
                existing.checksum = checksum
                existing.updated_at = now
                document = existing
            else:
                document = RagDocument(
                    doc_id=doc_id,
                    university=university,
                    title=title,
                    source_url="",
                    category=category,
                    full_text=text,
                    checksum=checksum,
                    created_at=now,
                    updated_at=now,
                )
                session.add(document)
                session.flush()

            session.execute(delete(RagChunk).where(RagChunk.doc_id == document.id))

            for index, chunk in enumerate(_chunk(text)):
                chunk_id = f"{doc_id}-{index}"
                session.add(
                    RagChunk(
                        chunk_id=chunk_id,
                        doc_id=document.id,
                        chunk_text=chunk,
                        created_at=now,
                    )
                )
                ids.append(chunk_id)
                documents.append(chunk)
                metadatas.append(
                    {
                        "doc_id": doc_id,
                        "chunk_id": chunk_id,
                        "title": title,
                        "university": university.lower(),
                        "category": category.lower(),
                    }
                )

        session.commit()

    if not documents:
        print("No documents found for ingestion.")
        return

    embeddings = embedder.encode(documents).tolist()
    collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
    client.persist()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest RAG documents into Chroma")
    parser.add_argument("input_dir", help="Directory with .txt files to ingest")
    args = parser.parse_args()

    ingest_rag(args.input_dir)
    print("RAG ingestion complete.")
