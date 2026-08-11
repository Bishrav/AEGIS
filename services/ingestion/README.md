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

## Run tests

```powershell
$env:PYTHONPATH = "services/ingestion"
python -m unittest discover -s services/ingestion/tests -v
```

