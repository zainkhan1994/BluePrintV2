from __future__ import annotations

import os
from typing import Any

import chromadb

from app.config import settings


class VectorStore:
    def __init__(self, persist_dir: str, collection_name: str):
        os.makedirs(persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def upsert_item_chunks(
        self,
        item_id: str,
        chunks: list[str],
        embeddings: list[list[float]],
        metadata: dict[str, Any],
    ) -> int:
        ids = [self._chunk_id(item_id, i) for i in range(len(chunks))]
        metadatas = []
        for i, _ in enumerate(chunks):
            row = dict(metadata)
            row["item_id"] = item_id
            row["chunk_index"] = i
            metadatas.append(row)

        self.collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        return len(ids)

    def delete_item(self, item_id: str) -> None:
        results = self.collection.get(where={"item_id": item_id})
        ids = results.get("ids", [])
        if ids:
            self.collection.delete(ids=ids)

    def health(self) -> dict[str, Any]:
        count = self.collection.count()
        return {"collection": settings.chroma_collection, "vector_count": count}

    def query(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["distances", "metadatas", "documents"],
        )

        ids = (result.get("ids") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        documents = (result.get("documents") or [[]])[0]

        rows: list[dict[str, Any]] = []
        for idx, chunk_id in enumerate(ids):
            distance = float(distances[idx]) if idx < len(distances) else 1.0
            metadata = metadatas[idx] if idx < len(metadatas) else {}
            snippet = documents[idx] if idx < len(documents) else ""
            # Convert distance to bounded score for API consumers.
            score = 1.0 / (1.0 + max(0.0, distance))
            rows.append(
                {
                    "chunk_id": chunk_id,
                    "distance": distance,
                    "score": score,
                    "metadata": metadata or {},
                    "snippet": snippet or "",
                }
            )
        return rows

    @staticmethod
    def _chunk_id(item_id: str, chunk_index: int) -> str:
        return f"{item_id}::chunk::{chunk_index}"


vector_store = VectorStore(settings.chroma_path, settings.chroma_collection)
