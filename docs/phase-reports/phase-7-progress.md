# Phase 7 Progress

## Scope

Phase 7 turns AEGIS from a working local MVP into a production-evidence portfolio project. It covers repeatable integration and end-to-end verification, replay and failure testing, load measurements, observability evidence, deployment, screenshots, benchmarks, and a recruiter-ready demonstration.

## First milestone — E2E acceptance harness

- Added a standard-library-only acceptance test at [`tests/e2e/test_phase7_acceptance.py`](../../tests/e2e/test_phase7_acceptance.py).
- The test authenticates as an analyst, ingests evidence, creates a correlated flood incident, reads the live gateway detail, updates status, adds a note, retrieves evidence, and verifies the authenticated SSE heartbeat.
- Run it against the local Compose stack with:

```powershell
docker compose up -d
$env:AEGIS_E2E = "1"
python -m unittest tests/e2e/test_phase7_acceptance.py -v
```

## Second milestone — deterministic replay evidence

- Added [`tests/phase7/test_replay_acceptance.py`](../../tests/phase7/test_replay_acceptance.py).
- Weather, hydrology, infrastructure, and report fixtures are normalized twice and compared as canonical JSON.
- Duplicate delivery across separate ingestion batches is verified to publish exactly once.
- Event ID uniqueness is verified for every MVP fixture source.
- The replay acceptance suite is now a required CI job.

Run locally with:

```powershell
$env:PYTHONPATH = "services/ingestion"
python -m unittest tests.phase7.test_replay_acceptance -v
```

## Remaining milestones

- Add load benchmark reports for ingestion, incident queries, graph traversal, risk, and evidence retrieval.
- Add Prometheus/Grafana dashboard evidence and CI quality gates.
- Complete Railway deployment verification, screenshots, and recruiter demo documentation.

## Third milestone — failure recovery evidence

- Added [`tests/phase7/test_failure_recovery.py`](../../tests/phase7/test_failure_recovery.py).
- A transient broker failure is injected and verified to recover on the third retry without dead-lettering.
- A permanent upstream timeout is verified to produce a degraded source-health record with an actionable error.
- These checks are required by the Phase 7 CI job.

## Fourth milestone — dashboard route UI verification

- Replaced the overview page's hash-only navigation with real Next.js links.
- Added the missing page-level visual system for incident tables, evidence cards, graph canvas and nodes, model registry rows, risk timelines, filters, analyst actions, and responsive layouts.
- Rebuilt the production frontend container and verified all four routes return rendered HTML:
  - `/incidents` — incident queue and workflow status.
  - `/evidence` — hybrid retrieval search and evidence cards.
  - `/graph` — infrastructure dependency graph and traversal paths.
  - `/models` — model metrics, registry, reproducibility, and risk governance.
- Frontend production build and Docker startup both pass after the UI changes.

## Seventh milestone — working dashboard actions

- Added an authenticated gateway route for evidence document ingestion.
- Evidence search now displays live results, the ingest modal indexes a document through the backend, and source citations open a real URL or search fallback.
- Overview incident navigation now opens the full incident queue.
- Knowledge graph traversal now filters impact paths and supports Reset view.
- Model Evaluation now exports JSON metrics and downloads a Markdown evaluation report.
- Smoke verification passed: analyst login `200`, document ingestion `200`, and `/incidents`, `/evidence`, `/graph`, and `/models` each returned `200` with rendered HTML.

## Eighth milestone — interaction audit and graph visualization

- Audited every dashboard button and replaced static incident controls with working filters, search, CSV export, and detail navigation.
- Overview incident arrows now open the corresponding incident detail pages.
- Replaced the graph placeholder geometry with an SVG topology: directional edges, relationship labels, selectable nodes, node metadata, highlighted connections, traversal filtering, and Reset view.
- Full route smoke test passed for `/`, `/incidents`, `/evidence`, `/graph`, `/models`, `/sources`, and `/observability`.

## Ninth milestone — deployment and recruiter evidence package

- Added [`tests/e2e/test_deployment_smoke.py`](../../tests/e2e/test_deployment_smoke.py), an environment-driven smoke contract for `/health`, `/ready`, and `/sources/health` on Railway or any deployed ingestion URL.
- Added [`docs/portfolio/recruiter-demo.md`](../portfolio/recruiter-demo.md) with a two-minute walkthrough, engineering talking points, screenshot checklist, and explicit deployment limitations.
- The deployment test intentionally skips when `AEGIS_DEPLOYMENT_URL` is unset and avoids live provider pulls during routine verification.

## Fifth milestone — reproducible load evidence

- Added [`benchmarks/phase7_load.py`](../../benchmarks/phase7_load.py), a standard-library benchmark for API health, incident listing, and evidence search.
- It reports success/error counts, p50 latency, p95 latency, and throughput, and writes a machine-specific JSON artifact under `artifacts/`.
- The benchmark is intentionally parameterized by request count and worker count so results can be compared across local hardware or deployment targets.

## Sixth milestone — reproducible observability dashboard

- Added repository-managed Grafana provisioning for the Prometheus datasource.
- Added an AEGIS Platform Overview dashboard with Prometheus health, scrape duration, and scrape sample panels.
- Docker Compose now mounts the datasource, dashboard provider, and dashboard JSON automatically, so a fresh local stack opens with the same observability configuration.
