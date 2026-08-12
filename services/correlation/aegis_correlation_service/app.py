from __future__ import annotations

import os
from uuid import uuid4

from fastapi import FastAPI, HTTPException

from aegis_correlation.pipeline import IncidentPipeline
from aegis_risk.audit import RiskAuditRecord

from .repositories import InMemoryIncidentRepository, PostgresIncidentRepository

app = FastAPI(title="AEGIS Correlation Service", version="0.1.0")
pipeline = IncidentPipeline()
repository = PostgresIncidentRepository(os.environ["POSTGRES_DSN"]) if os.getenv("POSTGRES_DSN") else InMemoryIncidentRepository()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "correlation"}


@app.get("/incidents")
def list_incidents() -> dict[str, object]:
    return {"incidents": repository.list()}


@app.post("/correlate")
def correlate(payload: dict) -> dict:
    events = payload.get("events", [])
    if not events:
        raise HTTPException(status_code=400, detail="events must not be empty")
    incident_id = payload.get("incident_id", f"incident-{uuid4()}" )
    result = pipeline.process(events, incident_id)
    audit = RiskAuditRecord.from_result(incident_id, result.risk).to_dict()
    repository.save(result.incident, result.risk, audit)
    return repository.get(incident_id) or {}


@app.get("/incidents/{incident_id}")
def get_incident(incident_id: str) -> dict:
    record = repository.get(incident_id)
    if record is None:
        raise HTTPException(status_code=404, detail="incident not found")
    return record


@app.patch("/incidents/{incident_id}/status")
def update_status(incident_id: str, payload: dict) -> dict:
    status = str(payload.get("status", "")).upper()
    if status not in {"OPEN", "ACKNOWLEDGED", "INVESTIGATING", "RESOLVED"}:
        raise HTTPException(status_code=400, detail="invalid incident status")
    record = repository.update_status(incident_id, status)
    if record is None:
        raise HTTPException(status_code=404, detail="incident not found")
    return record


@app.post("/incidents/{incident_id}/notes")
def add_note(incident_id: str, payload: dict) -> dict:
    note = str(payload.get("note", "")).strip()
    author = str(payload.get("author", "analyst")).strip() or "analyst"
    if not note:
        raise HTTPException(status_code=400, detail="note must not be empty")
    record = repository.add_note(incident_id, note, author)
    if record is None:
        raise HTTPException(status_code=404, detail="incident not found")
    return record
