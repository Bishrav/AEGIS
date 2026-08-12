from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

from fastapi import FastAPI, HTTPException, Request

from aegis_auth.rbac import Permission, UserContext, authorize
from aegis_auth.app import COOKIE_NAME, decode_token

app = FastAPI(title="AEGIS API Gateway", version="0.1.0")


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


def _get_json(base_url: str, path: str, params: dict[str, str] | None = None) -> dict:
    query = ""
    if params:
        query = "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(f"{base_url.rstrip('/')}{path}{query}", timeout=10) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        raise HTTPException(status_code=exc.code, detail="downstream service request failed") from exc
    except urllib.error.URLError as exc:
        raise HTTPException(status_code=503, detail="downstream service unavailable") from exc


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "api-gateway"}


@app.get("/api/v1/me")
def me(request: Request) -> dict[str, str]:
    user = current_user(request)
    return {"user_id": user.user_id, "role": user.role.value}


@app.get("/api/v1/incidents/{incident_id}")
def incident(incident_id: str, request: Request) -> dict:
    require(request, Permission.VIEW_INCIDENTS)
    return _get_json(os.getenv("CORRELATION_URL", "http://correlation:8000"), f"/incidents/{incident_id}")


@app.get("/api/v1/incidents/{incident_id}/evidence")
def incident_evidence(incident_id: str, request: Request, query: str, top_k: int = 5) -> dict:
    require(request, Permission.VIEW_EVIDENCE)
    return _get_json(os.getenv("EVIDENCE_URL", "http://evidence:8000"), f"/incidents/{incident_id}/evidence", {"query": query, "top_k": str(top_k)})
