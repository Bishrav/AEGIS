from __future__ import annotations

import math
import re
import hashlib
import json
import urllib.request
from collections import Counter
from typing import Iterable, Protocol

from .models import EvidenceHit, EvidencePackage

TOKEN_RE = re.compile(r"[a-z0-9]{2,}")


class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> list[float]: ...


class HashingEmbedder:
    """Small deterministic embedding substitute for local tests and offline demos."""

    def __init__(self, dimensions: int = 128) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in TOKEN_RE.findall(text.lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            vector[index] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class HttpEmbeddingProvider:
    """Provider-neutral JSON embedding adapter for production endpoints."""

    def __init__(self, endpoint: str, api_key: str, model: str, dimensions: int = 128, timeout: int = 30) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.dimensions = dimensions
        self.timeout = timeout

    def embed(self, text: str) -> list[float]:
        request = urllib.request.Request(
            f"{self.endpoint}/embeddings",
            data=json.dumps({"model": self.model, "input": text}).encode(),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            values = json.loads(response.read().decode())["data"][0]["embedding"]
        if len(values) != self.dimensions:
            raise ValueError(f"embedding dimension {len(values)} does not match configured {self.dimensions}")
        return [float(value) for value in values]


class HybridRetriever:
    def __init__(self, embedder: HashingEmbedder | None = None, lexical_weight: float = 0.55) -> None:
        self.embedder = embedder or HashingEmbedder()
        self.lexical_weight = lexical_weight
        self._chunks: list[dict[str, str]] = []
        self._vectors: list[list[float]] = []

    def add(self, chunks: Iterable[dict[str, str]]) -> None:
        for chunk in chunks:
            if any(existing["evidence_id"] == chunk["evidence_id"] for existing in self._chunks):
                continue
            self._chunks.append(dict(chunk))
            self._vectors.append(self.embedder.embed(chunk["text"]))

    def retrieve(self, query: str, top_k: int = 5) -> EvidencePackage:
        return EvidencePackage(query, self._retrieve_with_weights(query, top_k, self.lexical_weight))

    def _retrieve_with_weights(self, query: str, top_k: int, lexical_weight: float) -> tuple[EvidenceHit, ...]:
        if top_k <= 0:
            return ()
        query_tokens = Counter(TOKEN_RE.findall(query.lower()))
        query_vector = self.embedder.embed(query)
        scored: list[EvidenceHit] = []
        for chunk, vector in zip(self._chunks, self._vectors):
            chunk_tokens = Counter(TOKEN_RE.findall(chunk["text"].lower()))
            lexical = sum(min(query_tokens[token], chunk_tokens[token]) for token in query_tokens) / max(sum(query_tokens.values()), 1)
            semantic = sum(left * right for left, right in zip(query_vector, vector))
            score = lexical_weight * lexical + (1 - lexical_weight) * semantic
            scored.append(EvidenceHit(chunk["evidence_id"], chunk["document_id"], chunk["title"], chunk["text"], score, chunk["source_uri"]))
        scored.sort(key=lambda hit: (-hit.score, hit.evidence_id))
        return tuple(scored[:top_k])
