# AEGIS Delivery Roadmap

Every phase ends with working evidence, not only source code. A phase is complete when its acceptance criteria pass locally and in CI where applicable.

## Phase 0 — Portfolio foundation

- README, architecture map, roadmap, API index, and local runbook.
- Issue and pull-request templates.
- Conventional commit guidance and branch protection recommendation.

## Phase 1 — Platform foundation

- Docker Compose infrastructure.
- Health/readiness endpoints and service scaffolding.
- Versioned event schemas and Kafka topic catalog.

## Phase 2 — Ingestion and normalization — Complete

- At least three real source adapters.
- Raw payload persistence, retries, idempotency, deduplication, and dead-letter handling.
- Historical replay fixtures.
- Live Open-Meteo and BIPAD adapters, retries, Redis idempotency, source health, and CI integration contract.

## Phase 3 — Flood intelligence — Complete

- NLP extraction and entity normalization.
- Rainfall/river anomaly detection.
- Forecasting baselines and evaluation reports.
- Typed inference schemas, hybrid NER, anomaly ensemble, and CI verification.

## Phase 4 — Correlation, graph, and risk

- Correlated flood incidents.
- Neo4j graph projection and traversal.
- Versioned, deterministic, explainable risk scores.

## Phase 5 — Evidence and reasoning

- pgvector hybrid retrieval.
- Evidence packs and citation IDs.
- Provider-neutral LLM explanation adapters.

## Phase 6 — Product surface

- JWT/RBAC, REST APIs, analyst workflows, dashboard, and live updates.

## Phase 7 — Production evidence

- Integration, replay, E2E, load, and failure-injection tests.
- Observability dashboards, CI gates, deployment, screenshots, benchmarks, and recruiter demo.
