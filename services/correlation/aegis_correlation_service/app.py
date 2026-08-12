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
