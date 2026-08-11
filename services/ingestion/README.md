# Ingestion Service

The ingestion service owns source adapters, raw-record capture, canonical event normalization, idempotency, deduplication, retries, and dead-letter routing.

## Adapter contract

Every live or replay adapter implements:

```python
class SourceAdapter(Protocol):
    source_type: str

    def read(self) -> Iterable[RawRecord]: ...
```

The initial replay adapters use frozen JSON fixtures but follow the same contract expected from future weather, hydrology, road, and report providers.

The runnable service persists raw records to MinIO and publishes normalized events to `normalized.events`. Malformed records are published to `deadletter.ingestion`.

Open-Meteo weather can be pulled for the default Sindhupalchok coordinates with `POST /pull/weather`. The provider strategy and deferred live-source decisions are recorded in [`docs/architecture/adr/0002-live-source-provider-strategy.md`](../../docs/architecture/adr/0002-live-source-provider-strategy.md).

BIPAD-backed pulls are available through `POST /pull/hydrology`, `POST /pull/roads`, and `POST /pull/reports`. The hydrology adapter maps BIPAD river levels and danger thresholds; incident adapters classify road-related and flood-related reports without pretending that every incident is a road closure. Incomplete river observations are retained as explicit `NORMAL` events without fabricated measurements.

Replay a fixture after the Docker stack is running:

```powershell
Invoke-WebRequest -Method Post http://localhost:8002/replay/weather
Invoke-WebRequest -Method Post http://localhost:8002/replay/hydrology
Invoke-WebRequest -Method Post http://localhost:8002/replay/infrastructure
Invoke-WebRequest -Method Post http://localhost:8002/replay/report
```

## Run tests

```powershell
$env:PYTHONPATH = "services/ingestion"
python -m unittest discover -s services/ingestion/tests -v
```
