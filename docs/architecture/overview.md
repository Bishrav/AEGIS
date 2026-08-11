# AEGIS Architecture Overview

AEGIS is a flood-risk intelligence pipeline for Nepal. Source adapters capture public signals, Kafka decouples processing, typed services produce evidence, and deterministic components own correlation and risk decisions.

```mermaid
flowchart LR
  sources[Public Sources] --> adapters[Source Adapters]
  adapters --> raw[(MinIO Raw Objects)]
  adapters --> bus[(Kafka / Redpanda)]
  bus --> norm[Normalization]
  norm --> nlp[NLP Extraction]
  norm --> ts[Anomaly + Forecasting]
  nlp --> corr[Correlation]
  ts --> corr
  corr --> graph[(Neo4j)]
  corr --> risk[Risk Policy Engine]
  risk --> evidence[pgvector Evidence Retrieval]
  evidence --> reasoning[LLM Reasoning Adapter]
  reasoning --> api[API Gateway]
  api --> console[Operations Console]
```

## Core invariants

- Canonical events are versioned and schema validated.
- Duplicate source deliveries are idempotent.
- Low-confidence extraction remains explicitly low-confidence.
- Risk scores are deterministic for identical inputs and policy versions.
- Every explanation references stored evidence IDs.
- Critical calculations do not depend on an LLM response.

## Initial storage responsibilities

| Store | Responsibility |
| --- | --- |
| PostgreSQL/PostGIS | Incidents, events, users, policies, audit metadata, spatial metadata |
| Redpanda | Decoupled event processing and replayable topics |
| Redis | Cache, locks, rate limits, ephemeral state |
| Neo4j | Incident and infrastructure dependency graph |
| MinIO | Raw source payloads and document/model artifacts |
| pgvector | Historical document embeddings and semantic retrieval |

