from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from .engine import RiskResult


@dataclass(frozen=True)
class RiskAuditRecord:
    incident_id: str
    created_at: str
    risk: float
    level: str
    components: dict[str, float]
    policy_version: str

    @classmethod
    def from_result(cls, incident_id: str, result: RiskResult) -> "RiskAuditRecord":
        return cls(incident_id, datetime.now(timezone.utc).isoformat(), result.risk, result.level, dict(result.components), result.policy_version)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
