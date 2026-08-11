# ADR 0002: Live Source Provider Strategy

## Status

Accepted for Phase 2 implementation.

## Decision

- Weather begins with Open-Meteo behind `OpenMeteoWeatherAdapter`.
- Hydrology remains behind an adapter until DHM/BIPAD access is verified for the required station-level fields.
- Road disruption and public reports remain adapter contracts with replay fixtures until a stable public feed is selected.
- All providers emit the same `RawRecord` contract and use the shared retry, raw-storage, idempotency, and health pipeline.

## Rationale

Open-Meteo provides a no-key weather API suitable for an initial portfolio integration. Nepal government hydrology sources are authoritative, but their public data access and field contracts need to be verified before hard-coding a live connector. Replays preserve deterministic development while the remaining provider contracts are validated.

