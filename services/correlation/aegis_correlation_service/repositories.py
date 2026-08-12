from __future__ import annotations

from typing import Any, Protocol


class IncidentRepository(Protocol):
    def save(self, incident: Any, risk: Any, audit: dict[str, Any]) -> None: ...

    def get(self, incident_id: str) -> dict[str, Any] | None: ...


class InMemoryIncidentRepository:
    def __init__(self) -> None:
        self.records: dict[str, dict[str, Any]] = {}

    def save(self, incident: Any, risk: Any, audit: dict[str, Any]) -> None:
        self.records[incident.incident_id] = {
            "incident_id": incident.incident_id,
            "event_ids": incident.event_ids,
            "district": incident.district,
            "event_types": sorted(incident.event_types),
            "risk": {
                "risk": risk.risk,
                "level": risk.level,
                "components": risk.components,
                "policy_version": risk.policy_version,
            },
            "audit": audit,
        }

    def get(self, incident_id: str) -> dict[str, Any] | None:
        return self.records.get(incident_id)


class PostgresIncidentRepository:
    """Minimal durable repository; schema is created lazily for local MVP use."""

    def __init__(self, dsn: str) -> None:
        import psycopg

        self.connection = psycopg.connect(dsn, autocommit=True)
        with self.connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS aegis_incidents (
                    incident_id TEXT PRIMARY KEY,
                    payload JSONB NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)

    def save(self, incident: Any, risk: Any, audit: dict[str, Any]) -> None:
        import json

        payload = {
            "incident_id": incident.incident_id,
            "event_ids": incident.event_ids,
            "district": incident.district,
            "event_types": sorted(incident.event_types),
            "risk": {
                "risk": risk.risk,
                "level": risk.level,
                "components": risk.components,
                "policy_version": risk.policy_version,
            },
            "audit": audit,
        }
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO aegis_incidents (incident_id, payload) VALUES (%s, %s) "
                "ON CONFLICT (incident_id) DO UPDATE SET payload = EXCLUDED.payload, updated_at = now()",
                (incident.incident_id, json.dumps(payload)),
            )

    def get(self, incident_id: str) -> dict[str, Any] | None:
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT payload FROM aegis_incidents WHERE incident_id = %s", (incident_id,))
            row = cursor.fetchone()
        return row[0] if row else None
