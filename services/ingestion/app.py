from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException

from aegis_ingestion.adapters import JsonReplayAdapter
from aegis_ingestion.external import KafkaEventPublisher, MinioRawPayloadStore, MinioSettings
from aegis_ingestion.idempotency import RedisIdempotencyStore
from aegis_ingestion.live_adapters import OpenMeteoWeatherAdapter
from aegis_ingestion.bipad_adapters import BipadIncidentAdapter, BipadRiverAdapter
from aegis_ingestion.normalize import EventNormalizer
from aegis_ingestion.ports import ingest_records
from aegis_ingestion.reliability import RetryingPublisher, RetryPolicy, SourceHealthRegistry

app = FastAPI(title="AEGIS Ingestion Service", version="0.1.0")
FIXTURES = Path(__file__).parent / "fixtures"
health_registry = SourceHealthRegistry()
retry_policy = RetryPolicy()


def _dependencies():
    return (
        MinioRawPayloadStore(
            MinioSettings(
                endpoint_url=os.getenv("S3_ENDPOINT_URL", "http://minio:9000"),
                access_key=os.getenv("S3_ACCESS_KEY", "aegis"),
                secret_key=os.getenv("S3_SECRET_KEY", "aegis_dev_password"),
                bucket=os.getenv("S3_BUCKET", "aegis-raw"),
            )
        ),
        RetryingPublisher(
            KafkaEventPublisher(os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")),
            retry_policy,
        ),
        RedisIdempotencyStore(os.getenv("REDIS_URL", "redis://redis:6379/0")),
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ingestion"}


@app.get("/ready")
def ready() -> dict[str, str]:
    try:
        raw_store, publisher, idempotency = _dependencies()
        idempotency.client.ping()
        publisher.close()
        del raw_store
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"dependencies unavailable: {exc}") from exc
    return {"status": "ready", "service": "ingestion"}


@app.get("/sources/health")
def source_health() -> dict[str, list[dict[str, object]]]:
    return {"sources": health_registry.snapshot()}


@app.post("/pull/weather")
def pull_weather() -> dict[str, int | str]:
    adapter = OpenMeteoWeatherAdapter(
        latitude=float(os.getenv("AEGIS_WEATHER_LATITUDE", "27.95")),
        longitude=float(os.getenv("AEGIS_WEATHER_LONGITUDE", "85.68")),
    )
    raw_store, publisher, idempotency = _dependencies()
    try:
        records = retry_policy.run(lambda: list(adapter.read()))
        published = ingest_records(
            records,
            raw_store,
            publisher,
            EventNormalizer(),
            idempotency_store=idempotency,
            health_registry=health_registry,
        )
        return {"source_type": "weather", "published": published}
    finally:
        publisher.close()


def _pull_adapter(adapter, source_type: str) -> dict[str, int | str]:
    raw_store, publisher, idempotency = _dependencies()
    try:
        records = retry_policy.run(lambda: list(adapter.read()))
        published = ingest_records(
            records,
            raw_store,
            publisher,
            EventNormalizer(),
            idempotency_store=idempotency,
            health_registry=health_registry,
        )
        return {"source_type": source_type, "published": published}
    finally:
        publisher.close()


@app.post("/pull/hydrology")
def pull_hydrology() -> dict[str, int | str]:
    return _pull_adapter(BipadRiverAdapter(), "hydrology")


@app.post("/pull/roads")
def pull_roads() -> dict[str, int | str]:
    return _pull_adapter(BipadIncidentAdapter("infrastructure", {"limit": "25", "search": "road"}), "infrastructure")


@app.post("/pull/reports")
def pull_reports() -> dict[str, int | str]:
    return _pull_adapter(BipadIncidentAdapter("report", {"limit": "25", "search": "flood"}), "report")


@app.post("/replay/{source_type}")
def replay(source_type: str) -> dict[str, int | str]:
    fixture_name = "reports.json" if source_type == "report" else f"{source_type}.json"
    fixture = FIXTURES / fixture_name
    if not fixture.exists():
        raise HTTPException(status_code=404, detail=f"no fixture for source type: {source_type}")
    raw_store, publisher, idempotency = _dependencies()
    try:
        adapter = JsonReplayAdapter(source_type, fixture)
        records = retry_policy.run(lambda: list(adapter.read()))
        published = ingest_records(
            records,
            raw_store,
            publisher,
            EventNormalizer(),
            idempotency_store=idempotency,
            health_registry=health_registry,
        )
        return {"source_type": source_type, "published": published}
    finally:
        publisher.close()
