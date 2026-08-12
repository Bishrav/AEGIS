from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
import time

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from aegis_auth.rbac import Permission, UserContext, authorize
from aegis_auth.app import COOKIE_NAME, authenticate_credentials, decode_token, issue_token

app = FastAPI(title="AEGIS API Gateway", version="0.1.0")
allowed_origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3001").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type"],
)


def current_user(request: Request) -> UserContext:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="authentication required")
    return decode_token(token, os.getenv("AEGIS_JWT_SECRET", "local-development-only-change-me"))


def require(request: Request, permission: Permission) -> UserContext:
    user = current_user(request)
    if not authorize(user, permission):
        raise HTTPException(status_code=403, detail="insufficient permissions")
    return user


def _request_json(base_url: str, path: str, method: str = "GET", params: dict[str, str] | None = None, body: dict | None = None) -> dict:
    query = ""
    if params:
        query = "?" + urllib.parse.urlencode(params)
    try:
        request = urllib.request.Request(f"{base_url.rstrip('/')}{path}{query}", method=method)
        if body is not None:
            request.data = json.dumps(body).encode()
            request.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        raise HTTPException(status_code=exc.code, detail="downstream service request failed") from exc
    except urllib.error.URLError as exc:
        raise HTTPException(status_code=503, detail="downstream service unavailable") from exc


def _get_json(base_url: str, path: str, params: dict[str, str] | None = None) -> dict:
    return _request_json(base_url, path, params=params)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "api-gateway"}


@app.get("/ready")
def ready() -> dict[str, str]:
    for service_url in (os.getenv("CORRELATION_URL", "http://correlation:8000"), os.getenv("EVIDENCE_URL", "http://evidence:8000")):
        try:
            _request_json(service_url, "/health")
        except HTTPException as exc:
            raise HTTPException(status_code=503, detail="application dependencies unavailable") from exc
    return {"status": "ready", "service": "api-gateway"}


@app.get("/api/v1/me")
def me(request: Request) -> dict[str, str]:
    user = current_user(request)
    return {"user_id": user.user_id, "role": user.role.value}


@app.post("/api/v1/auth/login")
def login(payload: dict, response: Response) -> dict[str, str]:
    user = authenticate_credentials(str(payload.get("username", "")), str(payload.get("password", "")))
    token = issue_token(user, os.getenv("AEGIS_JWT_SECRET", "local-development-only-change-me"))
    response.set_cookie(COOKIE_NAME, token, httponly=True, secure=os.getenv("ENVIRONMENT") == "production", samesite=os.getenv("COOKIE_SAMESITE", "lax").lower(), max_age=1800)
    return {"user_id": user.user_id, "role": user.role.value}


@app.post("/api/v1/auth/logout")
def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(COOKIE_NAME)
    return {"status": "logged_out"}


@app.get("/api/v1/incidents/{incident_id}")
def incident(incident_id: str, request: Request) -> dict:
    require(request, Permission.VIEW_INCIDENTS)
    return _get_json(os.getenv("CORRELATION_URL", "http://correlation:8000"), f"/incidents/{incident_id}")


@app.get("/api/v1/incidents")
def incidents(request: Request) -> dict:
    require(request, Permission.VIEW_INCIDENTS)
    return _get_json(os.getenv("CORRELATION_URL", "http://correlation:8000"), "/incidents")


@app.get("/api/v1/incidents/{incident_id}/evidence")
def incident_evidence(incident_id: str, request: Request, query: str, top_k: int = 5) -> dict:
    require(request, Permission.VIEW_EVIDENCE)
    return _get_json(os.getenv("EVIDENCE_URL", "http://evidence:8000"), f"/incidents/{incident_id}/evidence", {"query": query, "top_k": str(top_k)})


@app.post("/api/v1/evidence/documents")
def ingest_evidence_document(payload: dict, request: Request) -> dict:
    require(request, Permission.VIEW_EVIDENCE)
    return _request_json(os.getenv("EVIDENCE_URL", "http://evidence:8000"), "/documents", method="POST", body=payload)


@app.get("/api/v1/events/stream")
def event_stream(request: Request):
    require(request, Permission.VIEW_INCIDENTS)

    def events():
        import json
        import redis
        client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"), decode_responses=True)
        pubsub = client.pubsub()
        pubsub.subscribe("aegis:incidents")
        try:
            while True:
                message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message.get("data"):
                    yield f"event: incident\ndata: {message['data']}\n\n"
                else:
                    yield f"event: heartbeat\ndata: {json.dumps({'ts': time.time()})}\n\n"
                time.sleep(1)
        finally:
            pubsub.close()
            client.close()

    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "Connection": "keep-alive"})


@app.patch("/api/v1/incidents/{incident_id}/status")
def update_incident_status(incident_id: str, payload: dict, request: Request) -> dict:
    require(request, Permission.EDIT_INCIDENTS)
    return _request_json(os.getenv("CORRELATION_URL", "http://correlation:8000"), f"/incidents/{incident_id}/status", method="PATCH", body=payload)


@app.post("/api/v1/incidents/{incident_id}/notes")
def add_incident_note(incident_id: str, payload: dict, request: Request) -> dict:
    require(request, Permission.EDIT_INCIDENTS)
    return _request_json(os.getenv("CORRELATION_URL", "http://correlation:8000"), f"/incidents/{incident_id}/notes", method="POST", body=payload)
