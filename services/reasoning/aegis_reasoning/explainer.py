from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from aegis_rag.models import EvidencePackage
from aegis_rag.citations import validate_citations


class LLMProvider(Protocol):
    def generate(self, prompt: str) -> str: ...


class MockLLMProvider:
    def generate(self, prompt: str) -> str:
        return "The incident is supported by the retrieved historical evidence."


@dataclass(frozen=True)
class Explanation:
    text: str
    evidence_ids: tuple[str, ...]
    provider: str


class EvidenceGroundedExplainer:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider or MockLLMProvider()

    def explain(self, incident_summary: str, evidence: EvidencePackage) -> Explanation:
        if not evidence.hits:
            raise ValueError("cannot generate an explanation without evidence")
        evidence_lines = "\n".join(f"[{hit.evidence_id}] {hit.snippet}" for hit in evidence.hits)
        prompt = f"Incident: {incident_summary}\nEvidence:\n{evidence_lines}"
        text = self.provider.generate(prompt).strip()
        if not text:
            raise ValueError("provider returned an empty explanation")
        citation_ids = evidence.evidence_ids
        validate_citations(evidence, citation_ids)
        return Explanation(text, citation_ids, type(self.provider).__name__)
