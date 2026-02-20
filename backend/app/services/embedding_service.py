from __future__ import annotations

import hashlib
import json
import math
import re
from urllib import error, request

from app.config import settings


_TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


class EmbeddingService:
    """
    Pluggable embedding service.
    - local_hash: deterministic local embedding for offline/dev.
    - api: provider-backed embedding endpoint (OpenAI-style JSON contract).
    """

    def __init__(self, dimension: int, provider: str):
        self.dimension = dimension
        self.provider = provider.strip().lower()

    def embed(self, text: str) -> list[float]:
        if self.provider == "api":
            return self._embed_via_api(text)
        return self._embed_local_hash(text)

    def _embed_local_hash(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        tokens = _TOKEN_RE.findall(text.lower())
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            bucket = int.from_bytes(digest[:4], byteorder="big") % self.dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[bucket] += sign

        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector

    def _embed_via_api(self, text: str) -> list[float]:
        if not settings.embedding_api_url:
            return self._embed_local_hash(text)

        payload = {
            "input": text,
            "model": settings.embedding_api_model,
        }
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if settings.embedding_api_key:
            headers["Authorization"] = f"Bearer {settings.embedding_api_key}"

        req = request.Request(settings.embedding_api_url, data=body, headers=headers, method="POST")
        try:
            with request.urlopen(req, timeout=20) as resp:  # noqa: S310
                response_payload = json.loads(resp.read().decode("utf-8"))
        except (error.URLError, TimeoutError, json.JSONDecodeError):
            # Fall back to local embedding so indexing continues.
            return self._embed_local_hash(text)

        vectors = response_payload.get("data", [])
        if not vectors:
            return self._embed_local_hash(text)
        emb = vectors[0].get("embedding")
        if not isinstance(emb, list) or not emb:
            return self._embed_local_hash(text)

        # Fit/pad to configured dimension for vector-store consistency.
        if len(emb) >= self.dimension:
            return [float(x) for x in emb[: self.dimension]]
        padded = [float(x) for x in emb] + ([0.0] * (self.dimension - len(emb)))
        return padded

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]


embedding_service = EmbeddingService(dimension=settings.embedding_dim, provider=settings.embedding_provider)
