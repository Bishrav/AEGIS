from __future__ import annotations

import os
import json
from collections import defaultdict

from aegis_correlation.pipeline import IncidentPipeline
from aegis_risk.audit import RiskAuditRecord

from .consumer import NormalizedEventConsumer
from .repositories import InMemoryIncidentRepository, PostgresIncidentRepository


class CorrelationWorker:
    def __init__(self) -> None:
        self.pipeline = IncidentPipeline()
        self.repository = PostgresIncidentRepository(os.environ["POSTGRES_DSN"]) if os.getenv("POSTGRES_DSN") else InMemoryIncidentRepository()
        self.buckets: dict[str, list[dict]] = defaultdict(list)

    def handle(self, event: dict) -> None:
        district = next((entity["value"] for entity in event.get("entities", []) if entity.get("type") == "DISTRICT"), "unknown")
        bucket = self.buckets[district]
        bucket.append(event)
        # The MVP worker processes a compact three-signal flood window.
        event_types = {item.get("event_type") for item in bucket}
        if {"HEAVY_RAIN", "FLOOD", "ROAD_CLOSURE"}.issubset(event_types):
            incident_id = f"incident-{district.lower().replace(' ', '-')}-live"
            result = self.pipeline.process(bucket, incident_id)
            audit = RiskAuditRecord.from_result(incident_id, result.risk).to_dict()
            self.repository.save(result.incident, result.risk, audit)
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                try:
                    import redis
                    redis.Redis.from_url(redis_url).publish("aegis:incidents", json.dumps({"type": "incident.updated", "incident_id": incident_id, "payload": self.repository.get(incident_id)}))
                except Exception:
                    pass
            self.buckets.pop(district, None)


def main() -> None:
    worker = CorrelationWorker()
    consumer = NormalizedEventConsumer(os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092"), worker.handle)
    try:
        while True:
            consumer.consume_once(timeout_ms=1000)
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
