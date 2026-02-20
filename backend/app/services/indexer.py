from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Item
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store


def _build_text(item: Item) -> str:
    return "\n".join(
        [
            item.title or "",
            item.description or "",
            item.content or "",
            item.taxonomy_path or "",
        ]
    ).strip()


def _chunk_text(text: str, max_chars: int = 800, overlap_chars: int = 120) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return [""]
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(end - overlap_chars, start + 1)
    return chunks


def index_item(db: Session, item: Item) -> int:
    full_text = _build_text(item)
    chunks = _chunk_text(full_text)
    embeddings = embedding_service.embed_many(chunks)

    vector_store.delete_item(item.id)
    chunk_count = vector_store.upsert_item_chunks(
        item_id=item.id,
        chunks=chunks,
        embeddings=embeddings,
        metadata={
            "source": item.source,
            "source_ref": item.source_ref or "",
            "taxonomy_path": item.taxonomy_path or "",
            "title": item.title,
        },
    )

    item.chunk_count = chunk_count
    item.embedding_model_version = settings.embedding_model_version
    item.embedded_at = datetime.utcnow()
    item.status = "embedded"
    item.error_reason = None
    db.add(item)
    db.commit()
    return chunk_count
