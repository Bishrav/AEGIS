# AEGIS Benchmarks

Phase 7 benchmark artifacts are generated locally and intentionally excluded from source control when they contain machine-specific timings.

Run the HTTP benchmark against the Compose stack:

```powershell
python benchmarks/phase7_load.py --requests 60 --workers 6
```

The command writes `artifacts/phase7-load.json` with success rate, p50/p95 latency, and throughput for the API health endpoint, incident listing, and evidence search.
