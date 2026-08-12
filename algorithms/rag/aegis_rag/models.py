from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Document:
    document_id: str
    title: str
    text: str
    source_uri: str
    published_at: str | None = None
    source_type: str = "historical_report"


@dataclass(frozen=True)
class EvidenceHit:
    evidence_id: str
    document_id: str
    title: str
    snippet: str
    score: float
    source_uri: str


@dataclass(frozen=True)
class EvidencePackage:
    query: str
    hits: tuple[EvidenceHit, ...] = field(default_factory=tuple)

    @property
    def evidence_ids(self) -> tuple[str, ...]:
        return tuple(hit.evidence_id for hit in self.hits)
