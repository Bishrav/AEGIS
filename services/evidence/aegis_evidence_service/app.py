from __future__ import annotations

from fastapi import FastAPI, HTTPException

from aegis_rag.chunking import chunk_document
from aegis_rag.models import Document
from aegis_rag.retrieval import HybridRetriever
from aegis_rag.store import InMemoryEvidenceStore

app = FastAPI(title="AEGIS Evidence Service", version="0.1.0")
store = InMemoryEvidenceStore()
retriever = HybridRetriever()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "evidence"}


@app.post("/documents")
def ingest_document(payload: dict) -> dict[str, object]:
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
def search(query: str, top_k: int = 5) -> dict[str, object]:
    package = retriever.retrieve(query, top_k)
    return {"query": package.query, "evidence_ids": list(package.evidence_ids), "hits": [hit.__dict__ for hit in package.hits]}


@app.get("/incidents/{incident_id}/evidence")
def incident_evidence(incident_id: str, query: str, top_k: int = 5) -> dict[str, object]:
    if not query.strip():
        raise HTTPException(status_code=400, detail="query must not be empty")
    package = retriever.retrieve(query, top_k)
    return {"incident_id": incident_id, "query": query, "evidence_ids": list(package.evidence_ids), "hits": [hit.__dict__ for hit in package.hits]}
