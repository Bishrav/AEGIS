from datetime import UTC, datetime

from fastapi import FastAPI

app = FastAPI(title="AEGIS Platform Health", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "platform-health"}


@app.get("/ready")
def readiness() -> dict[str, str]:
    return {
        "status": "ready",
        "service": "platform-health",
        "timestamp": datetime.now(UTC).isoformat(),
    }

