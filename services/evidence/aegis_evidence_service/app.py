from __future__ import annotations

import os
import secrets

from fastapi import FastAPI, Header, HTTPException

from aegis_rag.chunking import chunk_document
from aegis_rag.models import Document
from aegis_rag.retrieval import HashingEmbedder, HttpEmbeddingProvider, HybridRetriever
from aegis_rag.store import InMemoryEvidenceStore, PostgresEvidenceStore

app = FastAPI(title="AEGIS Evidence Service", version="0.1.0")
embedding_provider = HttpEmbeddingProvider(
    os.environ["EMBEDDING_ENDPOINT"], os.environ["EMBEDDING_API_KEY"], os.environ["EMBEDDING_MODEL"],
) if all(os.getenv(name) for name in ("EMBEDDING_ENDPOINT", "EMBEDDING_API_KEY", "EMBEDDING_MODEL")) else HashingEmbedder()
store = PostgresEvidenceStore(os.environ["EVIDENCE_POSTGRES_DSN"]) if os.getenv("EVIDENCE_POSTGRES_DSN") else InMemoryEvidenceStore()
retriever = HybridRetriever(embedding_provider)


def require_service_token(service_token: str | None) -> None:
    expected = os.getenv("AEGIS_SERVICE_TOKEN")
    if expected and not secrets.compare_digest(service_token or "", expected):
        raise HTTPException(status_code=401, detail="service authentication required")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "evidence"}


@app.post("/documents")
def ingest_document(payload: dict, x_aegis_service_token: str | None = Header(default=None)) -> dict[str, object]:
    require_service_token(x_aegis_service_token)
    required = ("document_id", "title", "text", "source_uri")
    if any(not payload.get(field) for field in required):
        raise HTTPException(status_code=400, detail=f"required fields: {', '.join(required)}")
    document = Document(
        document_id=str(payload["document_id"]), title=str(payload["title"]), text=str(payload["text"]),
        source_uri=str(payload["source_uri"]), published_at=payload.get("published_at"), source_type=str(payload.get("source_type", "historical_report")),
    )
    chunks = chunk_document(document)
    store.upsert_document(document, chunks)
    retriever.add(chunks)
    return {"document_id": document.document_id, "evidence_ids": [chunk["evidence_id"] for chunk in chunks]}


@app.get("/search")
def search(query: str, top_k: int = 5, x_aegis_service_token: str | None = Header(default=None)) -> dict[str, object]:
    require_service_token(x_aegis_service_token)
    package = retriever.retrieve(query, top_k)
    return {"query": package.query, "evidence_ids": list(package.evidence_ids), "hits": [hit.__dict__ for hit in package.hits]}


@app.get("/incidents/{incident_id}/evidence")
def incident_evidence(incident_id: str, query: str, top_k: int = 5, x_aegis_service_token: str | None = Header(default=None)) -> dict[str, object]:
    require_service_token(x_aegis_service_token)
    if not query.strip():
        raise HTTPException(status_code=400, detail="query must not be empty")
    package = retriever.retrieve(query, top_k)
    return {"incident_id": incident_id, "query": query, "evidence_ids": list(package.evidence_ids), "hits": [hit.__dict__ for hit in package.hits]}
