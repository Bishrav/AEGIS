# API Overview

The API is introduced incrementally with each service milestone. All endpoints are versioned under `/api/v1` once the gateway is available.

## Planned read endpoints

- `GET /api/v1/health`
- `GET /api/v1/metrics`
- `GET /api/v1/incidents`
- `GET /api/v1/incidents/{id}`
- `GET /api/v1/incidents/{id}/events`
- `GET /api/v1/incidents/{id}/risk`
- `GET /api/v1/incidents/{id}/graph`
- `GET /api/v1/incidents/{id}/evidence`
- `GET /api/v1/events`
- `GET /api/v1/predictions`
- `GET /api/v1/anomalies`
- `GET /api/v1/sources`
- `GET /api/v1/models`

## Planned write endpoints

- `POST /api/v1/auth/login`
- `PATCH /api/v1/incidents/{id}/status`
- `POST /api/v1/incidents/{id}/notes`
- `POST /api/v1/sources/{id}/replay`
- `POST /api/v1/sources`
- `PATCH /api/v1/risk-policies/{id}`
- `POST /api/v1/models/{id}/activate`

The published API contract will be OpenAPI-generated and tested with contract tests before the endpoint is marked complete.

