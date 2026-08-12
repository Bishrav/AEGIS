"""Small, dependency-free Phase 7 HTTP benchmark.

Example:
    python benchmarks/phase7_load.py --requests 60 --workers 6
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor


def request(url: str) -> tuple[float, int]:
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            response.read()
            return (time.perf_counter() - started) * 1000, response.status
    except Exception:
        return (time.perf_counter() - started) * 1000, 0


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, round((len(ordered) - 1) * fraction))
    return ordered[index]


def benchmark(name: str, url: str, count: int, workers: int) -> dict[str, object]:
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda _: request(url), range(count)))
    elapsed = time.perf_counter() - started
    latencies = [latency for latency, _ in results]
    statuses = [status for _, status in results]
    return {
        "name": name,
        "url": url,
        "requests": count,
        "workers": workers,
        "successes": sum(status == 200 for status in statuses),
        "errors": sum(status != 200 for status in statuses),
        "p50_ms": round(statistics.median(latencies), 2),
        "p95_ms": round(percentile(latencies, 0.95), 2),
        "throughput_rps": round(count / elapsed, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests", type=int, default=60)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--output", default="artifacts/phase7-load.json")
    args = parser.parse_args()
    results = [
        benchmark("api-health", "http://localhost:8000/health", args.requests, args.workers),
        benchmark("incident-list", "http://localhost:8003/incidents", args.requests, args.workers),
        benchmark("evidence-search", "http://localhost:8004/search?query=flood&top_k=5", args.requests, args.workers),
    ]
    payload = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "benchmarks": results}
    print(json.dumps(payload, indent=2))
    output_path = __import__("pathlib").Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
