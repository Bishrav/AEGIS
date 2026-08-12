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

- Add replay determinism and duplicate-delivery acceptance checks.
- Add failure-injection and service recovery checks.
- Add load benchmark reports for ingestion, incident queries, graph traversal, risk, and evidence retrieval.
- Add Prometheus/Grafana dashboard evidence and CI quality gates.
- Complete Railway deployment verification, screenshots, and recruiter demo documentation.
