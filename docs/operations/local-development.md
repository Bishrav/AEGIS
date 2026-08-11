# Local Development Runbook

## Prerequisites

- Docker Desktop with Compose v2.
- Git.
- Python 3.12 for Python services.
- Java 21 for Spring Boot services.
- Node.js 20+ for the dashboard.

## Start infrastructure

```powershell
Copy-Item .env.example .env
docker compose up -d
docker compose ps
```

The one-shot `redpanda-init` container provisions the topics declared in `schemas/topics.yaml` and exits successfully after creation. It is safe to rerun because existing topics are left unchanged.

## Local service URLs

| Service | URL |
| --- | --- |
| Redpanda Console | http://localhost:8080 |
| MinIO Console | http://localhost:9001 |
| Neo4j Browser | http://localhost:7474 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| Platform health | http://localhost:8001/health |
| Ingestion API | http://localhost:8002/health |

Credentials are development-only values from `.env.example`; never reuse them outside local development.

## Stop infrastructure

```powershell
docker compose down
```

Use `docker compose down -v` only when intentionally discarding local service data.
