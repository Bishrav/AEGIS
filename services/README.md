# Services

Service implementations are introduced by delivery phase. Each service must provide:

- `/health` for process health.
- `/ready` for dependency readiness.
- `/metrics` for Prometheus metrics once the service has runtime behavior.
- Structured JSON logs.
- Typed input/output contracts from `schemas/`.
- Unit and integration tests appropriate to its dependencies.

The `platform-health` service is the initial executable scaffold used to validate the service conventions and Docker networking.

