from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException

from aegis_ingestion.adapters import JsonReplayAdapter
from aegis_ingestion.external import KafkaEventPublisher, MinioRawPayloadStore, MinioSettings
from aegis_ingestion.normalize import EventNormalizer
from aegis_ingestion.ports import ingest_records

app = FastAPI(title="AEGIS Ingestion Service", version="0.1.0")
FIXTURES = Path(__file__).parent / "fixtures"


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
        KafkaEventPublisher(os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")),
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ingestion"}


@app.get("/ready")
def ready() -> dict[str, str]:
    try:
        raw_store, publisher = _dependencies()
        publisher.close()
        del raw_store
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"dependencies unavailable: {exc}") from exc
    return {"status": "ready", "service": "ingestion"}


@app.post("/replay/{source_type}")
def replay(source_type: str) -> dict[str, int | str]:
    fixture_name = "reports.json" if source_type == "report" else f"{source_type}.json"
    fixture = FIXTURES / fixture_name
    if not fixture.exists():
        raise HTTPException(status_code=404, detail=f"no fixture for source type: {source_type}")
    raw_store, publisher = _dependencies()
    try:
        records = JsonReplayAdapter(source_type, fixture).read()
        published = ingest_records(records, raw_store, publisher, EventNormalizer())
        return {"source_type": source_type, "published": published}
    finally:
        publisher.close()

