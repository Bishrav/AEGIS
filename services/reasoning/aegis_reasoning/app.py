from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException

from aegis_rag.models import EvidenceHit, EvidencePackage

from .explainer import EvidenceGroundedExplainer, MockLLMProvider
from .providers import OpenAICompatibleProvider

app = FastAPI(title="AEGIS Reasoning Service", version="0.1.0")


def _explainer() -> EvidenceGroundedExplainer:
    if os.getenv("LLM_ENDPOINT") and os.getenv("LLM_API_KEY") and os.getenv("LLM_MODEL"):
        provider = OpenAICompatibleProvider(os.environ["LLM_ENDPOINT"], os.environ["LLM_API_KEY"], os.environ["LLM_MODEL"])
        return EvidenceGroundedExplainer(provider)
    return EvidenceGroundedExplainer(MockLLMProvider())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "reasoning"}


@app.post("/explain")
def explain(payload: dict) -> dict[str, object]:
    summary = str(payload.get("incident_summary", "")).strip()
    raw_hits = payload.get("evidence", [])
    if not summary or not raw_hits:
        raise HTTPException(status_code=400, detail="incident_summary and evidence are required")
    package = EvidencePackage(
        query=str(payload.get("query", summary)),
        hits=tuple(EvidenceHit(**hit) for hit in raw_hits),
    )
    try:
        result = _explainer().explain(summary, package)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"explanation": result.text, "evidence_ids": list(result.evidence_ids), "provider": result.provider}
