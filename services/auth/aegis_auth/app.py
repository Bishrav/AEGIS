from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import FastAPI, HTTPException, Request, Response

from .rbac import Role, UserContext

app = FastAPI(title="AEGIS Auth Service", version="0.1.0")
COOKIE_NAME = "aegis_access_token"


def _users() -> dict[str, dict[str, str]]:
    configured = os.getenv("AEGIS_USERS_JSON")
    if configured:
        return json.loads(configured)
    return {
        "viewer": {"password": "viewer-dev", "user_id": "user-viewer", "role": Role.VIEWER.value},
        "analyst": {"password": "analyst-dev", "user_id": "user-analyst", "role": Role.ANALYST.value},
        "admin": {"password": "admin-dev", "user_id": "user-admin", "role": Role.ADMIN.value},
    }


def issue_token(user: UserContext, secret: str, ttl_minutes: int = 30) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": user.user_id, "role": user.role.value, "iat": now, "exp": now + timedelta(minutes=ttl_minutes)}, secret, algorithm="HS256")


def decode_token(token: str, secret: str) -> UserContext:
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return UserContext(str(payload["sub"]), Role(str(payload["role"])))
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="invalid or expired access token") from exc


def _secret() -> str:
    secret = os.getenv("AEGIS_JWT_SECRET", "local-development-only-change-me")
    if len(secret) < 32 and os.getenv("ENVIRONMENT") == "production":
        raise RuntimeError("AEGIS_JWT_SECRET must be at least 32 characters in production")
    return secret


def authenticate_credentials(username: str, password: str) -> UserContext:
    account = _users().get(username)
    if not account or not hmac.compare_digest(password, account["password"]):
        raise HTTPException(status_code=401, detail="invalid credentials")
    return UserContext(account["user_id"], Role(account["role"]))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "auth"}


@app.post("/auth/login")
def login(payload: dict, response: Response) -> dict[str, str]:
    username = str(payload.get("username", ""))
    password = str(payload.get("password", ""))
    user = authenticate_credentials(username, password)
    token = issue_token(user, _secret())
    response.set_cookie(COOKIE_NAME, token, httponly=True, secure=os.getenv("ENVIRONMENT") == "production", samesite="lax", max_age=1800)
    return {"user_id": user.user_id, "role": user.role.value}


@app.post("/auth/logout")
def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(COOKIE_NAME)
    return {"status": "logged_out"}


@app.get("/auth/me")
def me(request: Request) -> dict[str, str]:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="authentication required")
    user = decode_token(token, _secret())
    return {"user_id": user.user_id, "role": user.role.value}
