from __future__ import annotations

import re

from .models import EvidencePackage

EVIDENCE_REF = re.compile(r"\[(ev-[a-f0-9]{16})\]")


def validate_citations(evidence: EvidencePackage, cited_ids: tuple[str, ...]) -> None:
    available = set(evidence.evidence_ids)
    unknown = set(cited_ids) - available
    if unknown:
        raise ValueError(f"explanation cites unknown evidence IDs: {sorted(unknown)}")
    if not cited_ids:
        raise ValueError("explanation must contain at least one evidence ID")


def extract_citations(text: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(EVIDENCE_REF.findall(text)))
