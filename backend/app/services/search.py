from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from app.schemas import RetrievalResult, SearchRequest, SearchResult
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store


_TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


def _token_set(value: str) -> set[str]:
    return set(_TOKEN_RE.findall((value or "").lower()))


def _build_where_filter(payload: SearchRequest) -> dict[str, Any] | None:
    clauses: list[dict[str, Any]] = []
    if payload.source:
        clauses.append({"source": payload.source})
    if payload.taxonomy_path_prefix:
        clauses.append({"taxonomy_path": {"$contains": payload.taxonomy_path_prefix}})

    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


def run_semantic_search(payload: SearchRequest) -> list[SearchResult]:
    query = payload.query.strip()
    query_embedding = embedding_service.embed(query)
    rows = vector_store.query(
        query_embedding=query_embedding,
        top_k=max(payload.top_k * 3, payload.top_k),
        where=_build_where_filter(payload),
    )

    results: list[SearchResult] = []
    for row in rows:
        if row["score"] < payload.min_score:
            continue
        metadata = row["metadata"]
        results.append(
            SearchResult(
                item_id=str(metadata.get("item_id", "")),
                chunk_id=row["chunk_id"],
                chunk_index=int(metadata.get("chunk_index", 0)),
                score=float(row["score"]),
                source=str(metadata.get("source", "")),
                source_ref=metadata.get("source_ref") or None,
                taxonomy_path=metadata.get("taxonomy_path") or None,
                title=str(metadata.get("title", "")),
                snippet=row["snippet"],
            )
        )
        if len(results) >= payload.top_k:
            break
    return results


def run_retrieval(payload: SearchRequest) -> list[RetrievalResult]:
    query_tokens = _token_set(payload.query)
    query_embedding = embedding_service.embed(payload.query.strip())
    rows = vector_store.query(
        query_embedding=query_embedding,
        top_k=max(payload.top_k * 8, payload.top_k),
        where=_build_where_filter(payload),
    )

    grouped: dict[str, dict[str, Any]] = defaultdict(lambda: {"snippets": [], "best": None, "hits": 0})
    for row in rows:
        metadata = row["metadata"]
        item_id = str(metadata.get("item_id", ""))
        if not item_id:
            continue

        snippet = row["snippet"]
        snippet_tokens = _token_set(snippet)
        title_tokens = _token_set(str(metadata.get("title", "")))
        overlap = len(query_tokens & (snippet_tokens | title_tokens))
        lexical_score = min(1.0, overlap / max(1, len(query_tokens)))

        # Lightweight hybrid score: mostly semantic with small lexical boost.
        hybrid_score = (0.8 * float(row["score"])) + (0.2 * lexical_score)
        if hybrid_score < payload.min_score:
            continue

        bucket = grouped[item_id]
        bucket["hits"] += 1
        if snippet and snippet not in bucket["snippets"]:
            bucket["snippets"].append(snippet)

        current_best = bucket["best"]
        candidate = {
            "score": hybrid_score,
            "source": str(metadata.get("source", "")),
            "source_ref": metadata.get("source_ref") or None,
            "taxonomy_path": metadata.get("taxonomy_path") or None,
            "title": str(metadata.get("title", "")),
        }
        if current_best is None or candidate["score"] > current_best["score"]:
            bucket["best"] = candidate

    ranked = sorted(
        (
            RetrievalResult(
                item_id=item_id,
                score=float(data["best"]["score"]),
                source=data["best"]["source"],
                source_ref=data["best"]["source_ref"],
                taxonomy_path=data["best"]["taxonomy_path"],
                title=data["best"]["title"],
                snippets=data["snippets"][:3],
                chunk_hits=int(data["hits"]),
            )
            for item_id, data in grouped.items()
            if data["best"] is not None
        ),
        key=lambda x: x.score,
        reverse=True,
    )

    return ranked[: payload.top_k]
