from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Role(StrEnum):
    VIEWER = "VIEWER"
    ANALYST = "ANALYST"
    ADMIN = "ADMIN"


class Permission(StrEnum):
    VIEW_INCIDENTS = "view:incidents"
    VIEW_EVIDENCE = "view:evidence"
    ACKNOWLEDGE_ALERTS = "acknowledge:alerts"
    EDIT_INCIDENTS = "edit:incidents"
    MANAGE_USERS = "manage:users"
    MANAGE_SOURCES = "manage:sources"
    MANAGE_POLICIES = "manage:policies"


ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.VIEWER: frozenset({Permission.VIEW_INCIDENTS, Permission.VIEW_EVIDENCE}),
    Role.ANALYST: frozenset({Permission.VIEW_INCIDENTS, Permission.VIEW_EVIDENCE, Permission.ACKNOWLEDGE_ALERTS, Permission.EDIT_INCIDENTS}),
    Role.ADMIN: frozenset(Permission),
}


@dataclass(frozen=True)
class UserContext:
    user_id: str
    role: Role


def authorize(user: UserContext, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS[user.role]
