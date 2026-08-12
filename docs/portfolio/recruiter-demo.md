# AEGIS Recruiter Demo

## Two-minute walkthrough

1. Start the platform with `docker compose up -d` and open `http://localhost:3001`.
2. Explain the Nepal flood-risk MVP boundary and point to the live operations overview.
3. Open Incidents, filter to Critical, export the visible queue, and open `INC-042`.
4. Change the incident status and add an analyst note to demonstrate RBAC-protected workflow actions.
5. Open Evidence, run a search, ingest a short document, and open its source citation.
6. Open Knowledge Graph, select the incident node, run a traversal query, and explain the directional impact paths.
7. Open Model Evaluation and download the JSON metrics plus Markdown evaluation report.
8. Open Observability and Grafana at `http://localhost:3000` to show the provisioned Prometheus dashboard.

## Engineering points to mention

- Four-source ingestion produces one canonical event contract with deterministic IDs and Redis-backed idempotency.
- Classical ML baselines are evaluated before advanced models.
- Correlation and risk are deterministic and explainable; the LLM boundary only explains retrieved evidence.
- JWT/RBAC, Postgres persistence, Redis SSE, Neo4j graph intelligence, pgvector-compatible evidence, and Docker Compose are all demonstrated in one vertical slice.
- Phase 7 adds replay, failure recovery, load, observability, and deployment smoke evidence.

## Screenshot checklist

- Overview: map, risk posture, active incident queue.
- Incident detail: transparent risk components, timeline, analyst workspace.
- Evidence: search results, ingestion modal, citations.
- Knowledge graph: selected node and labeled directional edges.
- Model Evaluation: registry, metrics, downloaded report.
- Grafana: AEGIS Platform Overview dashboard.

## Limitations to state clearly

AEGIS is a portfolio MVP for Nepal flood intelligence. Railway deployment requires project-specific infrastructure bindings for Kafka, Redis, and S3-compatible storage; no public deployment is claimed until those bindings are configured and the deployment smoke test passes.
