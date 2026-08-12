from __future__ import annotations

import os
import secrets
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException

from aegis_correlation.pipeline import IncidentPipeline
from aegis_risk.audit import RiskAuditRecord

from .repositories import InMemoryIncidentRepository, PostgresIncidentRepository

app = FastAPI(title="AEGIS Correlation Service", version="0.1.0")
pipeline = IncidentPipeline()
repository = PostgresIncidentRepository(os.environ["POSTGRES_DSN"]) if os.getenv("POSTGRES_DSN") else InMemoryIncidentRepository()


def require_service_token(service_token: str | None) -> None:
    expected = os.getenv("AEGIS_SERVICE_TOKEN")
    if expected and not secrets.compare_digest(service_token or "", expected):
        raise HTTPException(status_code=401, detail="service authentication required")


def _publish(event_type: str, incident_id: str, payload: dict) -> None:
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        return
    try:
        import json
        import redis
        redis.Redis.from_url(redis_url).publish("aegis:incidents", json.dumps({"type": event_type, "incident_id": incident_id, "payload": payload}))
    except Exception:
        pass


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "correlation"}


@app.get("/incidents")
def list_incidents(x_aegis_service_token: str | None = Header(default=None)) -> dict[str, object]:
    require_service_token(x_aegis_service_token)
    return {"incidents": repository.list()}


@app.post("/correlate")
def correlate(payload: dict, x_aegis_service_token: str | None = Header(default=None)) -> dict:
    require_service_token(x_aegis_service_token)
    events = payload.get("events", [])
    if not events:
        raise HTTPException(status_code=400, detail="events must not be empty")
    incident_id = payload.get("incident_id", f"incident-{uuid4()}" )
    result = pipeline.process(events, incident_id)
    audit = RiskAuditRecord.from_result(incident_id, result.risk).to_dict()
    repository.save(result.incident, result.risk, audit)
    _publish("incident.updated", incident_id, repository.get(incident_id) or {})
    return repository.get(incident_id) or {}


@app.get("/incidents/{incident_id}")
def get_incident(incident_id: str, x_aegis_service_token: str | None = Header(default=None)) -> dict:
    require_service_token(x_aegis_service_token)
    record = repository.get(incident_id)
    if record is None:
        raise HTTPException(status_code=404, detail="incident not found")
    return record


@app.patch("/incidents/{incident_id}/status")
def update_status(incident_id: str, payload: dict, x_aegis_service_token: str | None = Header(default=None)) -> dict:
    require_service_token(x_aegis_service_token)
    status = str(payload.get("status", "")).upper()
    if status not in {"OPEN", "ACKNOWLEDGED", "INVESTIGATING", "RESOLVED"}:
        raise HTTPException(status_code=400, detail="invalid incident status")
    record = repository.update_status(incident_id, status)
    if record is None:
        raise HTTPException(status_code=404, detail="incident not found")
    _publish("incident.status_changed", incident_id, {"status": status})
    return record


@app.post("/incidents/{incident_id}/notes")
def add_note(incident_id: str, payload: dict, x_aegis_service_token: str | None = Header(default=None)) -> dict:
    require_service_token(x_aegis_service_token)
    note = str(payload.get("note", "")).strip()
    author = str(payload.get("author", "analyst")).strip() or "analyst"
    if not note:
        raise HTTPException(status_code=400, detail="note must not be empty")
    record = repository.add_note(incident_id, note, author)
    if record is None:
        raise HTTPException(status_code=404, detail="incident not found")
    _publish("incident.note_added", incident_id, {"author": author, "note": note})
    return record
