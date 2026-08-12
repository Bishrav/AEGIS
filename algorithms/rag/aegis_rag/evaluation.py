from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import EvidenceHit
from .retrieval import HybridRetriever


@dataclass(frozen=True)
class RetrievalEvaluation:
    recall_at_k: float
    queries: int


def recall_at_k(retriever: HybridRetriever, labelled_queries: Iterable[tuple[str, set[str]]], top_k: int = 5) -> RetrievalEvaluation:
    cases = list(labelled_queries)
    if not cases:
        return RetrievalEvaluation(0.0, 0)
    hits = sum(any(hit.document_id in relevant for hit in retriever.retrieve(query, top_k).hits) for query, relevant in cases)
    return RetrievalEvaluation(hits / len(cases), len(cases))


def rank_by_mode(retriever: HybridRetriever, query: str, mode: str, top_k: int = 5) -> tuple[EvidenceHit, ...]:
    if mode not in {"hybrid", "lexical", "semantic"}:
        raise ValueError("mode must be hybrid, lexical, or semantic")
    if mode == "hybrid":
        return retriever.retrieve(query, top_k).hits
    return retriever._retrieve_with_weights(query, top_k, lexical_weight=1.0 if mode == "lexical" else 0.0)
