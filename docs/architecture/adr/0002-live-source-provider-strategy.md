# ADR 0002: Live Source Provider Strategy

## Status

Accepted for Phase 2 implementation.

## Decision

- Weather begins with Open-Meteo behind `OpenMeteoWeatherAdapter`.
- Hydrology uses BIPAD's public `/api/v1/river/` resource, which exposes station coordinates, water level, danger level, status, and observation time.
- Road disruption and public reports use BIPAD's public `/api/v1/incident/` resource with explicit text classification and conservative source typing.
- All providers emit the same `RawRecord` contract and use the shared retry, raw-storage, idempotency, and health pipeline.

## Rationale

Open-Meteo provides a no-key weather API suitable for an initial portfolio integration. BIPAD exposes a public OpenAPI contract and current river/incident resources suitable for a bounded MVP pull. Replays remain the deterministic test path even when live adapters exist.
